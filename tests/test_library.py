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
