"""Tests for the tiered diskcache layer (donghua_cli.cache)."""

import time

from donghua_cli import cache
from donghua_cli.sources.base import Episode, Series


class TestStreamCache:
    def test_put_get_roundtrip_canonicalises(self):
        c = cache.StreamCache()
        # Store an embed-form URL; get() must hand back the canonical /video/ form.
        c.put("ep-key", "https://geo.dailymotion.com/player.html?video=xabc", "ds")
        stream, source = c.get("ep-key")
        assert stream == "https://www.dailymotion.com/video/xabc"
        assert source == "ds"

    def test_miss_returns_none(self):
        assert cache.StreamCache().get("nope") is None

    def test_ttl_expiry(self, monkeypatch):
        # A tiny TTL must actually evict — this is the stale-signed-URL fix.
        monkeypatch.setattr(cache, "TTL_STREAM", 1)
        c = cache.StreamCache()
        c.put("ep", "https://cdn.example/v.m3u8", "ax")
        assert c.get("ep") is not None
        time.sleep(1.1)
        assert c.get("ep") is None

    def test_clear_reports_removal(self):
        c = cache.StreamCache()
        c.put("ep", "https://cdn.example/v.m3u8", "ax")
        assert c.clear() is True
        assert c.get("ep") is None


class TestSearchCache:
    def test_roundtrip_reconstructs_series(self):
        s = Series(title="Battle Through the Heavens", cover_url="http://img/x.jpg")
        s.add_url("ds", "http://ds/series")
        s.add_url("ax", "http://ax/series")
        cache.put_search("btth", [s])

        got = cache.get_search("btth")
        assert got is not None
        assert len(got) == 1
        assert got[0].title == "Battle Through the Heavens"
        assert got[0].urls == {"ds": "http://ds/series"} | {"ax": "http://ax/series"}
        assert got[0].cover_url == "http://img/x.jpg"

    def test_key_is_case_and_space_insensitive(self):
        s = Series(title="X")
        s.add_url("ds", "http://ds/x")
        cache.put_search("  Soul Land  ", [s])
        assert cache.get_search("soul land") is not None

    def test_miss_returns_none(self):
        assert cache.get_search("never-searched") is None


class TestEpisodeListCache:
    def _series(self):
        s = Series(title="Perfect World")
        s.add_url("ds", "http://ds/pw")
        return s

    def test_roundtrip_reconstructs_episodes(self):
        series = self._series()
        ep = Episode(number=3, title="Episode 3")
        ep.add_url("ds", "http://ds/pw/ep-3")
        cache.put_episode_list(series, [ep])

        got = cache.get_episode_list(series)
        assert got is not None
        assert got[0].number == 3
        assert got[0].urls == {"ds": "http://ds/pw/ep-3"}

    def test_key_depends_on_series_urls(self):
        series = self._series()
        cache.put_episode_list(series, [Episode(number=1, title="E1", urls={"ds": "u"})])
        # A different backing URL set is a different series → cache miss.
        other = Series(title="Perfect World", urls={"ds": "http://ds/OTHER"})
        assert cache.get_episode_list(other) is None


class TestNegativeCache:
    def test_mark_and_check(self):
        assert cache.is_target_dead("http://dead/x") is False
        cache.mark_target_dead("http://dead/x")
        assert cache.is_target_dead("http://dead/x") is True

    def test_empty_url_is_never_dead(self):
        cache.mark_target_dead("")
        assert cache.is_target_dead("") is False
