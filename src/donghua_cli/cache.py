"""Tiered on-disk cache (diskcache) and adaptive background preloader.

The cache persists three tiers of scrape output so the app doesn't re-hit the
network for work it just did:

  * ``search:``   — merged search results (hours). Search used to re-scrape
                    every source on every keystroke-completed query.
  * ``episodes:`` — per-series episode lists (hours). The "mirror pages".
  * ``stream:``   — resolved stream/embed URLs (seconds-minutes). These are
                    frequently *signed* (Dailymotion et al.) and expire; the
                    old hand-rolled LRU had **no TTL**, so a stale signed URL
                    sat cached until it was LRU-evicted and then failed on
                    replay. A short ``expire=`` is the fix.
  * ``dead:``     — negative cache for resolved targets that just failed a
                    liveness probe (short), so the mirror race stops re-probing
                    a known-dead target across invocations.

Everything is backed by a single :class:`diskcache.Cache` (SQLite-backed:
atomic, process- and thread-safe, size-bound, native per-key TTL), rooted under
``config.CACHE_DB_DIR``. The preloader below is unchanged — it still tracks
navigation patterns and adapts lookahead depth.
"""

from __future__ import annotations

import logging
import os
import threading
from typing import TYPE_CHECKING, List, Optional, cast

import diskcache

from donghua_cli import config

if TYPE_CHECKING:
    from donghua_cli.sources.base import Episode, Series

log = logging.getLogger("donghua")

# ── TTL tiers (seconds) ───────────────────────────────────────────────────
TTL_SEARCH = 6 * 3600      # search results — hours; catalogs move slowly
TTL_EPISODES = 3 * 3600    # episode lists — hours
TTL_STREAM = 90            # resolved stream URLs — seconds-minutes (signed!)
TTL_DEAD = 300             # negative cache for dead resolved targets — short

# Key namespaces within the flat diskcache keyspace.
_NS_STREAM = "stream:"
_NS_SEARCH = "search:"
_NS_EPISODES = "episodes:"
_NS_DEAD = "dead:"

# 128 MB is comfortably huge for what are essentially short strings; diskcache
# evicts least-recently-stored past this. URLs never approach it in practice.
_SIZE_LIMIT = 128 * 1024 * 1024

_store: Optional[diskcache.Cache] = None
_store_lock = threading.Lock()


def store() -> diskcache.Cache:
    """Return the process-wide diskcache handle, opening it on first use."""
    global _store
    if _store is None:
        with _store_lock:
            if _store is None:
                os.makedirs(config.CACHE_DB_DIR, exist_ok=True)
                _store = diskcache.Cache(
                    directory=config.CACHE_DB_DIR,
                    size_limit=_SIZE_LIMIT,
                )
    return _store


# ── search-tier helpers ───────────────────────────────────────────────────


def _search_key(query: str) -> str:
    return _NS_SEARCH + query.strip().lower()


def get_search(query: str) -> Optional[List["Series"]]:
    """Return cached search results for ``query`` or ``None`` on miss."""
    from donghua_cli.sources.base import Series

    raw = store().get(_search_key(query))
    if not raw:
        return None
    try:
        rows = cast("list[tuple[str, dict, str | None]]", raw)
        return [Series(title=t, urls=dict(urls), cover_url=cover) for (t, urls, cover) in rows]
    except Exception as e:  # corrupt/old shape → treat as a miss
        log.debug("get_search deserialise failed: %s", e)
        return None


def put_search(query: str, results: List["Series"]) -> None:
    """Cache merged search results as plain primitives (pickle-shape-safe)."""
    payload = [(s.title, dict(s.urls), s.cover_url) for s in results]
    try:
        store().set(_search_key(query), payload, expire=TTL_SEARCH)
    except Exception as e:
        log.debug("put_search failed: %s", e)


# ── episode-list-tier helpers ─────────────────────────────────────────────


def _episodes_key(series: "Series") -> str:
    # Identity = the set of (source, series-page URL) pairs backing the series.
    sig = ";".join(f"{k}={v}" for k, v in sorted(series.urls.items()))
    return _NS_EPISODES + sig


def get_episode_list(series: "Series") -> Optional[List["Episode"]]:
    """Return the cached merged episode list for ``series`` or ``None``."""
    from donghua_cli.sources.base import Episode

    raw = store().get(_episodes_key(series))
    if not raw:
        return None
    try:
        rows = cast("list[tuple[int, str, dict]]", raw)
        return [Episode(number=num, title=title, urls=dict(urls)) for (num, title, urls) in rows]
    except Exception as e:
        log.debug("get_episode_list deserialise failed: %s", e)
        return None


def put_episode_list(series: "Series", episodes: List["Episode"]) -> None:
    payload = [(e.number, e.title, dict(e.urls)) for e in episodes]
    try:
        store().set(_episodes_key(series), payload, expire=TTL_EPISODES)
    except Exception as e:
        log.debug("put_episode_list failed: %s", e)


# ── negative cache (dead resolved targets) ────────────────────────────────


def mark_target_dead(url: str) -> None:
    """Remember that a resolved target just failed its liveness probe."""
    if not url:
        return
    try:
        store().set(_NS_DEAD + url, True, expire=TTL_DEAD)
    except Exception as e:
        log.debug("mark_target_dead failed: %s", e)


def is_target_dead(url: str) -> bool:
    """True if ``url`` failed a probe within the last ``TTL_DEAD`` seconds."""
    if not url:
        return False
    try:
        return bool(store().get(_NS_DEAD + url))
    except Exception:
        return False


class StreamCache:
    """Persistent, TTL'd cache for resolved stream URLs.

    Public surface (``get``/``put``/``clear``/``_key``) is unchanged so the
    Preloader and app layers don't move. What changed underneath: entries now
    carry a short ``expire=`` (``TTL_STREAM``), so a signed URL that goes stale
    disappears on its own instead of being served dead until LRU-eviction.
    Thread/process safety comes from diskcache itself.
    """

    def __init__(self, max_size: int = 100):
        # max_size kept for API compatibility; diskcache bounds by bytes, and
        # TTL does the real eviction work for this tier.
        self.max_size = max_size

    def _key(self, episode: Episode) -> str:
        """Cache key from episode's primary URL."""
        return episode.primary_url

    def get(self, key: str) -> Optional[tuple[str, str]]:
        """Get cached (stream_url, source_key) or None.

        Canonicalises the URL on the way out, so entries written by older
        versions (with /embed/ URLs mpv can't handle) still play.
        """
        from donghua_cli.extractor import _canonicalize

        val = store().get(_NS_STREAM + key)
        if not val:
            return None
        stream_url, source_key = cast("tuple[str, str]", val)
        return _canonicalize(stream_url), source_key

    def put(self, key: str, stream_url: str, source_key: str) -> None:
        from donghua_cli.extractor import _canonicalize

        stream_url = _canonicalize(stream_url)
        try:
            store().set(
                _NS_STREAM + key, (stream_url, source_key), expire=TTL_STREAM
            )
        except Exception as e:
            log.debug("StreamCache.put failed: %s", e)

    def clear(self) -> bool:
        """Drop every tier. Returns True if anything (incl. the legacy JSON
        file) was removed."""
        removed = False
        try:
            if store().clear() > 0:
                removed = True
        except Exception as e:
            log.debug("StreamCache.clear failed: %s", e)
        # Reap the pre-diskcache stream_cache.json if it's still lying around.
        try:
            if os.path.exists(config.STREAM_CACHE_FILE):
                os.remove(config.STREAM_CACHE_FILE)
                removed = True
        except OSError:
            pass
        return removed


class Preloader:
    """Adaptive background preloader that adjusts lookahead based on watch pattern."""

    MIN_LOOKAHEAD = 1
    MAX_LOOKAHEAD = 5
    HISTORY_SIZE = 6

    def __init__(self, cache: StreamCache):
        self.cache = cache
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._nav_history: list[int] = []
        self._lookahead = 2

    def record_navigation(self, prev_idx: int, new_idx: int) -> None:
        """Record a navigation action to adapt preloading depth."""
        delta = new_idx - prev_idx
        self._nav_history.append(delta)
        if len(self._nav_history) > self.HISTORY_SIZE:
            self._nav_history = self._nav_history[-self.HISTORY_SIZE:]

        if len(self._nav_history) >= 3:
            sequential = sum(1 for d in self._nav_history if d == 1)
            ratio = sequential / len(self._nav_history)

            if ratio >= 0.8:
                self._lookahead = min(self._lookahead + 1, self.MAX_LOOKAHEAD)
            elif ratio >= 0.5:
                self._lookahead = max(2, self._lookahead)
            else:
                self._lookahead = max(self.MIN_LOOKAHEAD, self._lookahead - 1)

    @property
    def lookahead(self) -> int:
        return self._lookahead

    def preload(self, episodes: List[Episode], current_idx: int, extract_fn) -> None:
        """Start preloading upcoming episodes in a daemon thread."""
        self.stop()
        self._stop.clear()

        end = min(current_idx + 1 + self._lookahead, len(episodes))
        upcoming = episodes[current_idx + 1 : end]
        if not upcoming:
            return

        def _worker():
            for ep in upcoming:
                if self._stop.is_set():
                    break
                key = ep.primary_url
                if self.cache.get(key):
                    continue
                try:
                    stream_url, source_key = extract_fn(ep)
                    if stream_url and stream_url != ep.primary_url:
                        self.cache.put(key, stream_url, source_key)
                except Exception:
                    pass

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()

    def get_stream(self, episode: Episode, extract_fn) -> tuple[str, str]:
        """Return (stream_url, source_key) -- cached or freshly extracted."""
        key = episode.primary_url
        cached = self.cache.get(key)
        if cached:
            return cached
        stream_url, source_key = extract_fn(episode)
        if stream_url:
            self.cache.put(key, stream_url, source_key)
        return stream_url, source_key

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        self._thread = None
