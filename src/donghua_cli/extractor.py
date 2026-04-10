"""Stream URL extraction with automatic server fallback.

For a single URL, tries methods fastest-first:
  1. Direct URL detection (0ms)
  2. Partial-fetch regex on first 8KB (~100ms)
  3. Full selectolax parse (~200ms)
  4. yt-dlp fallback (~1000ms+)

For an Episode with multiple source URLs, tries each source in order.
If extraction fails on one server, silently moves to the next.
"""

from __future__ import annotations

import logging
import re
import subprocess
from typing import TYPE_CHECKING

from donghua_cli import config
from donghua_cli.utils import fetch_html, fetch_partial

if TYPE_CHECKING:
    from donghua_cli.sources.base import Episode

log = logging.getLogger("donghua")


def extract_with_fallback(episode: Episode) -> tuple[str, str]:
    """Try all servers for an episode. Returns (stream_url, source_key).

    Iterates over all source URLs stored on the Episode. For each one,
    runs the full extraction pipeline. Returns the first successful result.
    If all fail, returns the primary URL as-is.
    """
    for source_key, ep_url in episode.urls.items():
        log.debug("Trying %s: %s", source_key, ep_url[:80])
        stream = extract(ep_url)
        if stream and stream != ep_url:
            log.info("Extracted via %s: %s", source_key, stream[:80])
            return stream, source_key
        log.debug("Failed on %s, trying next server", source_key)

    log.warning("All servers failed for ep %d, returning raw URL", episode.number)
    return episode.primary_url, episode.sources[0]


def extract(episode_url: str) -> str:
    """Extract the playable stream URL from a single episode page URL.

    Returns the best stream URL found, or the original URL if nothing worked.
    """
    # 1. Already a direct media URL
    if episode_url.endswith((".m3u8", ".mp4", ".mkv")):
        return episode_url

    # 2. Quick partial fetch -- regex on first 8KB
    chunk = fetch_partial(episode_url, max_bytes=8192, timeout=5)
    if chunk:
        m = re.search(r'data-video\s*=\s*["\']([^"\']+)["\']', chunk)
        if m:
            return f"https://www.dailymotion.com/video/{m.group(1)}"

        m = re.search(r'src\s*=\s*["\'](https?://[^"\']*dailymotion[^"\']*)["\']', chunk)
        if m:
            return m.group(1)

        m = re.search(r'src\s*=\s*["\'](https?://ok\.[^"\']+)["\']', chunk)
        if m:
            return m.group(1)

    # 3. Full selectolax parse
    tree = fetch_html(episode_url, timeout=8)

    for script in tree.css("script[data-video]"):
        src = script.attributes.get("src", "")
        if "dailymotion" in src:
            vid = script.attributes.get("data-video")
            if vid:
                return f"https://www.dailymotion.com/video/{vid}"

    for meta in tree.css("meta"):
        content = meta.attributes.get("content", "")
        if "dailymotion" in content or "ok.ru" in content:
            return content

    for iframe in tree.css("iframe"):
        src = iframe.attributes.get("src") or iframe.attributes.get("data-src") or ""
        if src and any(x in src for x in ("dailymotion", "ok.ru", "youtube")):
            return src

    # 4. yt-dlp fallback
    return _ytdlp_extract(episode_url)


def _ytdlp_extract(url: str) -> str:
    """Use yt-dlp --get-url as a last resort."""
    headers = config.get_headers()
    cmd = [
        "yt-dlp",
        "--get-url",
        "--quiet",
        "--no-check-certificates",
        "--referer", url,
        "--user-agent", headers["User-Agent"],
        url,
    ]

    try:
        kwargs: dict = {"capture_output": True, "text": True, "timeout": 15}
        if config.PLATFORM == "windows":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = si

        result = subprocess.run(cmd, **kwargs)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.startswith("http") and not line.endswith(".svg"):
                    return line
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return url
