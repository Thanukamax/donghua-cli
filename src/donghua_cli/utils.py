"""Shared utility functions."""

import os
import re
import subprocess

import httpx
from selectolax.parser import HTMLParser

from donghua_cli import config

# Thread-local clients for safe concurrent access
import threading

_local = threading.local()


def get_client() -> httpx.Client:
    """Return a thread-local httpx client with connection pooling."""
    client = getattr(_local, "client", None)
    if client is None or client.is_closed:
        client = httpx.Client(
            headers=config.get_headers(),
            follow_redirects=True,
            timeout=httpx.Timeout(8, connect=3),
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
    except httpx.TimeoutException:
        pass
    except httpx.HTTPError:
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
            chunks: list[str] = []
            total = 0
            for chunk in resp.iter_text():
                chunks.append(chunk)
                total += len(chunk)
                if total >= max_bytes:
                    break
            return "".join(chunks)[:max_bytes]
    except (httpx.HTTPError, httpx.TimeoutException):
        return ""


def clear_screen() -> None:
    os.system("cls" if config.PLATFORM == "windows" else "clear")
