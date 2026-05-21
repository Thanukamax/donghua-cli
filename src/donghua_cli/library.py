"""Local library: watch history + bookmarks.

A tiny JSON store at ``~/.config/donghua-cli/library.json`` so a single user's
state is portable, hand-editable, and easy to rsync between machines.

Two collections live in the same file:

* ``history`` — chronological list of series the user has played. Each entry
  records the last episode watched and a timestamp, sorted most-recent first.
* ``bookmarks`` — series the user starred. Order is insertion order.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import asdict, dataclass, field
from typing import List

from donghua_cli import config
from donghua_cli.sources.base import Series
from donghua_cli.utils import atomic_write_json

log = logging.getLogger("donghua")

_PATH = os.path.join(os.path.dirname(config.CONFIG_FILE), "library.json")
_lock = threading.RLock()


@dataclass
class HistoryEntry:
    title: str
    urls: dict[str, str] = field(default_factory=dict)
    last_episode: int = 0
    last_watched_at: float = 0.0

    def to_series(self) -> Series:
        return Series(title=self.title, urls=dict(self.urls))


@dataclass
class BookmarkEntry:
    title: str
    urls: dict[str, str] = field(default_factory=dict)
    added_at: float = 0.0

    def to_series(self) -> Series:
        return Series(title=self.title, urls=dict(self.urls))


@dataclass
class LibraryState:
    history: list[HistoryEntry] = field(default_factory=list)
    bookmarks: list[BookmarkEntry] = field(default_factory=list)


_state: LibraryState | None = None


def _load() -> LibraryState:
    global _state
    if _state is not None:
        return _state
    try:
        with open(_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise TypeError("library.json root is not an object")
        raw_history = data.get("history", [])
        raw_bookmarks = data.get("bookmarks", [])
        if not isinstance(raw_history, list):
            raise TypeError("library.json 'history' is not a list")
        if not isinstance(raw_bookmarks, list):
            raise TypeError("library.json 'bookmarks' is not a list")
        history = [HistoryEntry(**h) for h in raw_history if isinstance(h, dict)]
        bookmarks = [BookmarkEntry(**b) for b in raw_bookmarks if isinstance(b, dict)]
        _state = LibraryState(history=history, bookmarks=bookmarks)
    except FileNotFoundError:
        _state = LibraryState()
    except (ValueError, TypeError) as e:
        log.warning("library.json unreadable, starting fresh: %s", e)
        _state = LibraryState()
    return _state


def _save() -> None:
    state = _load()
    try:
        atomic_write_json(
            _PATH,
            {
                "history": [asdict(h) for h in state.history],
                "bookmarks": [asdict(b) for b in state.bookmarks],
            },
            indent=2,
        )
    except OSError as e:
        log.debug("Could not persist library: %s", e)


# ── History ──────────────────────────────────────────────────────────────


def record_watch(series: Series, episode_number: int) -> None:
    """Note that the user just watched an episode of `series`.

    Most-recent series moves to the front; older entries beyond MAX_HISTORY
    fall off the tail.
    """
    MAX_HISTORY = 50
    with _lock:
        state = _load()
        # Drop any existing entry with the same title; we re-add at the front.
        state.history = [h for h in state.history if h.title != series.title]
        state.history.insert(
            0,
            HistoryEntry(
                title=series.title,
                urls=dict(series.urls),
                last_episode=episode_number,
                last_watched_at=time.time(),
            ),
        )
        state.history = state.history[:MAX_HISTORY]
        _save()


def recent_history(limit: int = 10) -> List[HistoryEntry]:
    with _lock:
        return list(_load().history[:limit])


# ── Bookmarks ────────────────────────────────────────────────────────────


def is_bookmarked(title: str) -> bool:
    with _lock:
        return any(b.title == title for b in _load().bookmarks)


def toggle_bookmark(series: Series) -> bool:
    """Add or remove a bookmark. Returns True if now bookmarked."""
    with _lock:
        state = _load()
        existing = next(
            (b for b in state.bookmarks if b.title == series.title), None
        )
        if existing is not None:
            state.bookmarks.remove(existing)
            _save()
            return False
        state.bookmarks.append(
            BookmarkEntry(
                title=series.title,
                urls=dict(series.urls),
                added_at=time.time(),
            )
        )
        _save()
        return True


def list_bookmarks() -> List[BookmarkEntry]:
    with _lock:
        return list(_load().bookmarks)


def reset() -> None:
    """Wipe the whole library. Used by tests."""
    global _state
    with _lock:
        _state = LibraryState()
        _save()
