"""LRU stream cache and adaptive background preloader.

The cache persists stream URLs to disk so repeat plays are instant.
The preloader tracks navigation patterns and adapts:
  - Sequential watching: preload 3-5 episodes ahead
  - Random jumping: reduce to 1-2 or stop entirely
"""

from __future__ import annotations

import json
import os
import threading
from collections import OrderedDict
from typing import TYPE_CHECKING, List, Optional

from donghua_cli import config

if TYPE_CHECKING:
    from donghua_cli.sources.base import Episode


class StreamCache:
    """Persistent LRU cache for resolved stream URLs."""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: OrderedDict[str, tuple[str, str]] = OrderedDict()  # ep_key -> (stream_url, source_key)
        self._load()

    def _key(self, episode: Episode) -> str:
        """Cache key from episode's primary URL."""
        return episode.primary_url

    def get(self, key: str) -> Optional[tuple[str, str]]:
        """Get cached (stream_url, source_key) or None."""
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, stream_url: str, source_key: str) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
        self._cache[key] = (stream_url, source_key)
        self._save()

    def clear(self) -> bool:
        self._cache.clear()
        try:
            if os.path.exists(config.STREAM_CACHE_FILE):
                os.remove(config.STREAM_CACHE_FILE)
                return True
        except OSError:
            pass
        return False

    def _save(self) -> None:
        try:
            os.makedirs(config.CACHE_DIR, exist_ok=True)
            # Serialize as list of [key, [stream_url, source_key]]
            data = [[k, list(v)] for k, v in self._cache.items()]
            with open(config.STREAM_CACHE_FILE, "w") as f:
                json.dump(data, f)
        except OSError:
            pass

    def _load(self) -> None:
        try:
            if os.path.exists(config.STREAM_CACHE_FILE):
                with open(config.STREAM_CACHE_FILE, "r") as f:
                    items = json.load(f)
                    self._cache = OrderedDict()
                    for item in items[-self.max_size:]:
                        key = item[0]
                        val = item[1]
                        # Handle old format (string) and new format ([url, source])
                        if isinstance(val, str):
                            self._cache[key] = (val, "unknown")
                        elif isinstance(val, list) and len(val) == 2:
                            self._cache[key] = (val[0], val[1])
        except (OSError, json.JSONDecodeError, (IndexError, KeyError)):
            self._cache = OrderedDict()


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
