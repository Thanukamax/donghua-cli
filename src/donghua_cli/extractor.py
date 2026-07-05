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
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING

from donghua_cli import cache, config, health
from donghua_cli.utils import fetch_html, fetch_partial, probe_alive

if TYPE_CHECKING:
    from donghua_cli.sources.base import Episode

log = logging.getLogger("donghua")

# Cap on concurrent mirror races. Aggregators rarely list more than a handful
# of servers per episode; a small pool keeps us from opening a dozen sockets at
# once while still resolving every candidate in parallel.
MAX_RACE_WORKERS = 6


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


def _resolve_candidate(source_key: str, ep_url: str) -> tuple[str, str] | None:
    """Cheaply resolve one mirror to a canonical stream URL (no yt-dlp).

    Returns ``(source_key, stream_url)`` when the fast path (partial-fetch regex
    + selectolax parse) yields a real stream, else ``None``. yt-dlp is left out
    on purpose so the concurrent race stays sub-second and cancelling losers
    never orphans a 15s subprocess.
    """
    stream = extract(ep_url, allow_ytdlp=False)
    if stream and stream != ep_url:
        return source_key, _canonicalize(stream)
    return None


def extract_with_fallback(episode: Episode, probe: bool = True) -> tuple[str, str]:
    """Resolve the fastest LIVE mirror for an episode. Returns (stream_url, key).

    Races every candidate source concurrently through the cheap resolver, then
    hands each resolved URL to a ranged-GET liveness probe. The first mirror that
    both resolves AND serves real media bytes wins — this is simultaneously the
    correctness fix (a plain 200 loading-shell no longer counts as "extracted")
    and a speed win (we stop waiting on the slowest mirror the moment a live one
    answers, attacking the <15s-to-play target).

    Fallbacks, in order: a mirror that resolved but failed/​skipped the probe
    (probes can false-negative on odd hosts), then a sequential yt-dlp pass over
    every candidate, then the raw primary URL.
    """
    candidates = list(episode.urls.items())
    if not candidates:
        return _canonicalize(episode.primary_url), (episode.sources[0] if episode.sources else "")

    # ── Phase 1: race the cheap resolver across all mirrors ──────────────
    resolved: list[tuple[str, str]] = []  # resolved-but-not-yet-live pool
    probed: set[str] = set()  # canonical targets we've already probed this race
    with ThreadPoolExecutor(max_workers=min(len(candidates), MAX_RACE_WORKERS)) as pool:
        futures = {
            pool.submit(_resolve_candidate, key, url): key for key, url in candidates
        }
        for fut in as_completed(futures):
            try:
                res = fut.result()
            except Exception as e:  # a mirror blew up; treat as a miss
                log.debug("Resolver error on %s: %s", futures[fut], e)
                res = None
            if res is None:
                continue
            source_key, stream = res
            resolved.append(res)

            # Mirror-group dedup: these aggregators share a small set of
            # backends (one Dailymotion id often sits behind several "mirrors"),
            # so two candidates routinely resolve to the *same* canonical
            # target. Probing it twice wastes an RTT and hammers one host — skip
            # a target we've already probed this race, or one the negative cache
            # says just failed a probe elsewhere.
            if stream in probed or cache.is_target_dead(stream):
                continue
            probed.add(stream)

            if not probe or probe_alive(stream):
                for f in futures:
                    f.cancel()
                health.mark_alive(source_key)
                log.info("Live via %s: %s", source_key, stream[:80])
                return stream, source_key
            cache.mark_target_dead(stream)

    # ── Phase 2: something resolved but nothing probed live ──────────────
    if resolved:
        source_key, stream = resolved[0]
        log.info("No live probe hit; using resolved %s: %s", source_key, stream[:80])
        return stream, source_key

    # ── Phase 3: cheap path found nothing — sequential yt-dlp fallback ───
    for source_key, ep_url in candidates:
        log.debug("yt-dlp fallback on %s: %s", source_key, ep_url[:80])
        stream = extract(ep_url, allow_ytdlp=True)
        if stream and stream != ep_url:
            stream = _canonicalize(stream)
            health.mark_alive(source_key)
            log.info("Extracted via yt-dlp %s: %s", source_key, stream[:80])
            return stream, source_key
        health.mark_dead(source_key, "extract failed")

    log.warning("All servers failed for ep %d, returning raw URL", episode.number)
    return _canonicalize(episode.primary_url), episode.sources[0]


def extract(episode_url: str, allow_ytdlp: bool = True) -> str:
    """Extract the playable stream URL from a single episode page URL.

    Returns the best stream URL found, or the original URL if nothing worked.
    Set ``allow_ytdlp=False`` to skip the slow yt-dlp last resort — used by the
    concurrent mirror race, which wants every candidate to stay sub-second.
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

    # 4. yt-dlp fallback (skipped in the concurrent race — too slow to block on)
    if not allow_ytdlp:
        return episode_url
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
