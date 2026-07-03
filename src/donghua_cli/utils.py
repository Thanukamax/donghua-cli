"""Shared utility functions."""

import json
import os
import re
import subprocess
import tempfile

from curl_cffi import requests as cffi
from curl_cffi.requests.exceptions import RequestException
from selectolax.parser import HTMLParser

from donghua_cli import config

# Thread-local clients for safe concurrent access
import threading

_local = threading.local()


def atomic_write_json(path: str, data, *, indent: int | None = None) -> None:
    """Write JSON to `path` atomically.

    Writes to a temp file in the same directory, fsyncs, then `os.replace`s
    the target. Power loss mid-write can no longer leave a half-written file
    behind — the user either sees the old contents or the new ones.

    Raises OSError on directory creation / write failure; callers decide
    whether to swallow it.
    """
    parent = os.path.dirname(path) or "."
    os.makedirs(parent, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        prefix=".tmp_", suffix=".json", dir=parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=indent, ensure_ascii=False)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except OSError:
                # fsync is best-effort; some filesystems (procfs, virtio)
                # don't support it. The os.replace below is still atomic.
                pass
        os.replace(tmp_path, path)
    except Exception:
        # Don't leave a stray temp file if the replace failed.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def get_client() -> cffi.Session:
    """Return a thread-local curl_cffi session with browser TLS impersonation.

    curl_cffi mimics a real Chrome's TLS/JA3 + HTTP2 fingerprint, which is the
    single biggest lever against the anti-bot walls these aggregators sit behind
    — a plain requests/httpx handshake gets a 403 or a loading-shell page where a
    browser gets served. ``impersonate`` owns the fingerprint-sensitive headers
    (User-Agent, Accept, sec-ch-ua, …); we only layer on the app-specific
    Referer trick so the two never contradict each other.

    IMPORTANT: every fetch AND every liveness probe must share this client, or a
    naked probe gets blocked while the real fetch would have been served — a
    false "dead" verdict. See ``probe_alive``.
    """
    client = getattr(_local, "client", None)
    if client is None or getattr(client, "_closed", False):
        client = cffi.Session(
            impersonate=config.IMPERSONATE,
            headers={"Referer": config.get_headers().get("Referer", "")},
            timeout=8,
            allow_redirects=True,
        )
        _local.client = client
    return client


def is_valid_episode_url(href: str) -> bool:
    """Check if a URL looks like a real episode page, not a comment/anchor/noise link."""
    if not href or not href.startswith("http"):
        return False
    if "#comment" in href or "#respond" in href:
        return False
    if any(skip in href for skip in ("/tag/", "/category/", "/author/", "wp-content", "javascript:")):
        return False
    return True


def sanitize_filename(name: str) -> str:
    """Make a string safe for use as a filename on any OS."""
    sanitized = re.sub(r'[\\/:*?"<>|]', "_", name).strip(" .")
    sanitized = re.sub(r"_+", "_", sanitized)
    return sanitized or "untitled"


def extract_episode_number(title: str, url: str) -> int:
    """Pull an episode number from title text or URL. Returns 999999 on failure."""
    patterns = [
        r"episode\s*[-]?\s*(\d+)",
        r"ep\s*[-]?\s*(\d+)",
        r"\bpt\s*[-.]?\s*(\d+)",           # Movie parts: PT-01, PT 01, PT.01
        r"\bpart\s*[-.]?\s*(\d+)",          # part-01, part 01
        r"\u7b2c\s*(\d+)\s*[\u96c6\u8bdd]",
        r"(\d{2,})\s*$",
        r"\b(\d{2,})\b",
    ]
    for source in (title, url):
        for pat in patterns:
            m = re.search(pat, source, re.IGNORECASE)
            if m:
                return int(m.group(1))
    return 999999


def fetch_html(url: str, timeout: int = 8, fast: bool = False) -> HTMLParser:
    """Fetch a page and return a selectolax HTMLParser tree.

    When fast=True, uses streaming with early cutoff (for search -- we only
    need the first ~50KB containing results, not the full 200KB+ page).
    When fast=False (default), fetches full page with curl fallback.
    """
    try:
        resp = get_client().get(url, timeout=timeout)
        if resp.status_code == 200:
            return HTMLParser(resp.text)
    except RequestException:
        pass

    if fast:
        return HTMLParser("")

    # curl fallback (only for non-speed-critical paths like episode pages)
    try:
        headers = config.get_headers()
        cmd = ["curl", "-s", "-L", "-m", str(timeout)]
        if config.PLATFORM == "windows":
            cmd += ["-A", headers["User-Agent"], url]
        else:
            cmd += [
                "-H", f"User-Agent: {headers['User-Agent']}",
                "-H", "Accept: text/html",
                url,
            ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
        if result.returncode == 0:
            return HTMLParser(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return HTMLParser("")


def fetch_partial(url: str, max_bytes: int = 8192, timeout: int = 5) -> str:
    """Fetch only the first `max_bytes` of a page for fast regex scanning."""
    try:
        with get_client().stream("GET", url, timeout=timeout) as resp:
            chunks: list[bytes] = []
            total = 0
            for chunk in resp.iter_content():
                chunks.append(chunk)
                total += len(chunk)
                if total >= max_bytes:
                    break
            return b"".join(chunks)[:max_bytes].decode("utf-8", "replace")
    except RequestException:
        return ""


def probe_alive(url: str, timeout: int = 4) -> bool:
    """Confirm a candidate URL actually serves media bytes, not a shell page.

    Uses a ranged ``GET`` (``Range: bytes=0-1``) rather than ``HEAD``: many dead
    embeds answer ``200`` to HEAD and even to a full GET while the body is just a
    loading SVG / "video unavailable" shell. Asking for the first bytes and
    checking the response is the only way to tell live media from a polite 200.

    Runs on the shared impersonated client (``get_client``) so the probe sees
    exactly what the real fetch would — probing naked would get us blocked where
    a browser is served, producing false negatives.

    Returns True when the server answers 2xx/206 for the range and doesn't
    hand back an obvious HTML/SVG shell.
    """
    if not url or not url.startswith("http"):
        return False
    try:
        with get_client().stream(
            "GET", url, timeout=timeout, headers={"Range": "bytes=0-1"}
        ) as resp:
            if resp.status_code not in (200, 206):
                return False
            ctype = (resp.headers.get("content-type") or "").lower()
            # A real media/playlist endpoint won't advertise html/svg. Embed
            # pages that we still want to accept (they carry the player) report
            # text/html — those are handled upstream by extraction, not here, so
            # this probe is only ever pointed at resolved stream/candidate URLs.
            if "text/html" in ctype or "image/svg" in ctype:
                return False
            return True
    except RequestException:
        return False


def clear_screen() -> None:
    os.system("cls" if config.PLATFORM == "windows" else "clear")
