"""Tests for donghua_cli.library — history + bookmarks JSON store."""

from __future__ import annotations

import importlib

import pytest

from donghua_cli.sources.base import Series


@pytest.fixture
def lib(tmp_path, monkeypatch):
    """Reload the library module with state redirected into a tmp path."""
    fake_config_file = tmp_path / "config.toml"
    import donghua_cli.config as cfg

    monkeypatch.setattr(cfg, "CONFIG_FILE", str(fake_config_file), raising=True)

    import donghua_cli.library as library

    importlib.reload(library)
    library.reset()
    return library


def _series(title: str) -> Series:
    return Series(title=title, urls={"ld": f"https://luciferdonghua.in/anime/{title}/"})


def test_record_watch_inserts_at_front(lib):
    lib.record_watch(_series("A"), 1)
    lib.record_watch(_series("B"), 2)
    lib.record_watch(_series("C"), 3)

    titles = [h.title for h in lib.recent_history()]
    assert titles == ["C", "B", "A"]


def test_record_watch_dedupes_by_title(lib):
    lib.record_watch(_series("A"), 1)
    lib.record_watch(_series("B"), 1)
    lib.record_watch(_series("A"), 7)

    history = lib.recent_history()
    assert [h.title for h in history] == ["A", "B"]
    assert history[0].last_episode == 7


def test_toggle_bookmark_round_trip(lib):
    s = _series("Battle Through The Heavens")

    assert lib.toggle_bookmark(s) is True
    assert lib.is_bookmarked(s.title) is True
    assert len(lib.list_bookmarks()) == 1

    assert lib.toggle_bookmark(s) is False
    assert lib.is_bookmarked(s.title) is False
    assert lib.list_bookmarks() == []


def test_state_persists_to_disk(lib):
    lib.record_watch(_series("Soul Land"), 12)
    lib.toggle_bookmark(_series("Renegade Immortal"))

    importlib.reload(lib)

    history = lib.recent_history()
    bookmarks = lib.list_bookmarks()
    assert len(history) == 1
    assert history[0].title == "Soul Land"
    assert history[0].last_episode == 12
    assert len(bookmarks) == 1
    assert bookmarks[0].title == "Renegade Immortal"


def test_malformed_library_json_falls_back_to_empty(lib, tmp_path):
    """A corrupted library.json must not crash on load — just start fresh."""
    import os

    # Write garbage into the on-disk path (lib._PATH points into tmp via fixture).
    with open(lib._PATH, "w", encoding="utf-8") as fh:
        fh.write("{not valid json")
    assert os.path.exists(lib._PATH)

    importlib.reload(lib)
    assert lib.recent_history() == []
    assert lib.list_bookmarks() == []


def test_wrong_shape_library_json_falls_back_to_empty(lib):
    """`history` being a string instead of a list shouldn't crash."""
    import json

    with open(lib._PATH, "w", encoding="utf-8") as fh:
        json.dump({"history": "not-a-list", "bookmarks": []}, fh)

    importlib.reload(lib)
    assert lib.recent_history() == []
    assert lib.list_bookmarks() == []


def test_atomic_save_leaves_no_temp_file(lib):
    """After a save, no .tmp_*.json siblings should remain in the dir."""
    import os

    lib.record_watch(_series("Soul Land"), 5)

    dirpath = os.path.dirname(lib._PATH)
    leftovers = [f for f in os.listdir(dirpath) if f.startswith(".tmp_")]
    assert leftovers == []
