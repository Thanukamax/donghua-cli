"""Source health tracking.

Sources get marked alive on a successful response and dead on repeated failures.
Dead sources are skipped from search for the cooldown window so users don't
wait for a known-bad upstream every time.

State lives at ``~/.cache/donghua/source_health.json`` and is opportunistically
written; loss of the file just means the next search re-probes.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import asdict, dataclass

from donghua_cli import config
from donghua_cli.utils import atomic_write_json

log = logging.getLogger("donghua")

# Window during which a source marked dead is skipped from search.
COOLDOWN_SECONDS = 60 * 60  # 1 hour
# Allow this many failures before a source is benched.
FAILURE_THRESHOLD = 2

_STATE_PATH = os.path.join(config.CACHE_DIR, "source_health.json")
_lock = threading.RLock()


@dataclass
class SourceState:
    fails: int = 0
    last_dead_at: float = 0.0
    last_alive_at: float = 0.0
    reason: str = ""


_state: dict[str, SourceState] = {}
_loaded = False


def _load() -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    try:
        with open(_STATE_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        for key, raw in data.items():
            _state[key] = SourceState(**raw)
    except FileNotFoundError:
        pass
    except (OSError, ValueError, TypeError) as e:
        log.debug("Source health cache unreadable, ignoring: %s", e)


def _save() -> None:
    try:
        atomic_write_json(
            _STATE_PATH,
            {k: asdict(v) for k, v in _state.items()},
            indent=2,
        )
    except OSError as e:
        log.debug("Could not persist source health: %s", e)


def is_healthy(key: str) -> bool:
    """Return True unless the source has been benched within the cooldown window."""
    with _lock:
        _load()
        st = _state.get(key)
        if not st or st.fails < FAILURE_THRESHOLD:
            return True
        return (time.time() - st.last_dead_at) > COOLDOWN_SECONDS


def mark_alive(key: str) -> None:
    with _lock:
        _load()
        st = _state.get(key) or SourceState()
        st.fails = 0
        st.reason = ""
        st.last_alive_at = time.time()
        _state[key] = st
        _save()


def mark_dead(key: str, reason: str = "") -> None:
    with _lock:
        _load()
        st = _state.get(key) or SourceState()
        st.fails += 1
        st.last_dead_at = time.time()
        if reason:
            st.reason = reason
        _state[key] = st
        _save()


def snapshot() -> dict[str, SourceState]:
    """Return a copy of the current state for debugging / TUI display."""
    with _lock:
        _load()
        return {k: SourceState(**asdict(v)) for k, v in _state.items()}


def reset(key: str | None = None) -> None:
    """Clear health state. Useful for tests and for a `--reset-health` flag."""
    with _lock:
        if key is None:
            _state.clear()
        else:
            _state.pop(key, None)
        _save()
