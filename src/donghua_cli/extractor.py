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


# Hosts whose iframe / regex matches we trust enough to hand to mpv. Donghua
# aggregators rotate through these as alternative servers; if we don't pick
# them up they fall through to yt-dlp and usually fail.
VIDEO_HOSTS: tuple[str, ...] = (
    "dailymotion",
    "ok.ru",
    "youtube",
    "youtu.be",
    "streamtape",
    "mixdrop",
    "doodstream",
    "dood.",
    "ds2play",
    "d0000d",
    "mp4upload",
    "vidmoly",
    "fembed",
    "feurl",
    "supervideo",
)


def _normalise_scheme(url: str) -> str:
    """Promote protocol-relative URLs and trim leading whitespace."""
    url = url.strip()
    if url.startswith("//"):
        url = "https:" + url
    return url


def _canonicalize(url: str) -> str:
    """Rewrite embed-style player URLs into forms mpv's ytdl_hook can handle.

    mpv only invokes yt-dlp for URLs its built-in matcher recognises (the
    extractor's ``_VALID_URL`` regex). Several hosts use distinct ``/embed/``
    paths whose embed page returns HTML (sometimes just a loading SVG); mpv
    tries to demux that as media and exits in <1s. Canonicalisation rewrites
    each known host's embed form to the form yt-dlp's extractor expects.
    """
    if not url:
        return url

    url = _normalise_scheme(url)

    # Dailymotion: collapse EVERY embed/geo/player form to the canonical
    # https://www.dailymotion.com/video/<id> that yt-dlp's extractor pins. The
    # legacy /embed/video/<id> path is easy, but modern aggregators hand over the
    # geo player form geo.dailymotion.com/player/<pid>.html?video=<id> — there's
    # no /video/ in the path, so the old substring check missed it and mpv tried
    # to demux the player HTML and died in <1s.
    if "dailymotion." in url:
        vid = None
        m = re.search(r"[?&]video=([A-Za-z0-9]+)", url)  # player.html?video=<id>
        if m:
            vid = m.group(1)
        else:
            m = re.search(r"dailymotion\.com/(?:embed/)?video/([A-Za-z0-9]+)", url)
            if m:
                vid = m.group(1)
        if vid:
            url = f"https://www.dailymotion.com/video/{vid}"

    # ok.ru: /videoembed/<id> → /video/<id>
    if "ok.ru/videoembed/" in url:
        url = url.replace("/videoembed/", "/video/")

    # YouTube: /embed/<id> → /watch?v=<id>
    m = re.match(r"(https?://(?:www\.)?youtube\.com)/embed/([A-Za-z0-9_-]{6,})(?:[/?&#].*)?$", url)
    if m:
        url = f"{m.group(1)}/watch?v={m.group(2)}"

    # Streamtape: /e/<id>/... → /v/<id>/... (yt-dlp's Streamtape extractor
    # accepts both, but the /v/ "watch" URL is the canonical form most
    # extractor releases pin.)
    url = re.sub(
        r"(streamtape\.[A-Za-z]{2,6})/e/",
        r"\1/v/",
        url,
    )

    # Mixdrop: /e/<id> → /f/<id>
    url = re.sub(
        r"(mixdrop\.[A-Za-z]{2,6})/e/",
        r"\1/f/",
        url,
    )

    # mp4upload: /embed-<id>.html → /<id> (yt-dlp's mp4upload extractor wants
    # the bare ID path)
    m = re.match(r"(https?://(?:www\.)?mp4upload\.com)/embed-([A-Za-z0-9_-]+)(?:\.html)?$", url)
    if m:
        url = f"{m.group(1)}/{m.group(2)}"

    # Doodstream / dood family: /e/<id> → /d/<id> across the rotating mirror
    # set (dood.so, dood.cx, ds2play.com, d0000d.com, …)
    url = re.sub(
        r"((?:dood|ds2play|d0000d)\.[A-Za-z]{2,8})/e/",
        r"\1/d/",
        url,
    )

    return url


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
            stream = _canonicalize(stream)
            log.info("Extracted via %s: %s", source_key, stream[:80])
            return stream, source_key
        log.debug("Failed on %s, trying next server", source_key)

    log.warning("All servers failed for ep %d, returning raw URL", episode.number)
    return _canonicalize(episode.primary_url), episode.sources[0]


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

        # Generic iframe/src match for any known host (covers the previous
        # dailymotion + ok.ru cases plus streamtape, doodstream, mixdrop,
        # mp4upload, youtube, vidmoly, fembed, supervideo).
        host_alt = "|".join(re.escape(h) for h in VIDEO_HOSTS)
        m = re.search(
            rf'src\s*=\s*["\']((?:https?:)?//[^"\']*(?:{host_alt})[^"\']*)["\']',
            chunk,
        )
        if m:
            return m.group(1)

    # 3. Full selectolax parse
    tree = fetch_html(episode_url, timeout=8)

    for script in tree.css("script[data-video]"):
        src = script.attributes.get("src") or ""
        if "dailymotion" in src:
            vid = script.attributes.get("data-video")
            if vid:
                return f"https://www.dailymotion.com/video/{vid}"

    for meta in tree.css("meta"):
        content = meta.attributes.get("content") or ""
        if any(host in content for host in VIDEO_HOSTS):
            return content

    for iframe in tree.css("iframe"):
        src = iframe.attributes.get("src") or iframe.attributes.get("data-src") or ""
        if src and any(host in src for host in VIDEO_HOSTS):
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
            si = subprocess.STARTUPINFO()  # type: ignore[attr-defined]
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore[attr-defined]
            kwargs["startupinfo"] = si

        result = subprocess.run(cmd, **kwargs)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.startswith("http") and not line.endswith(".svg"):
                    return line
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return url
