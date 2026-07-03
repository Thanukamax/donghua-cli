"""Tests for source plugin data structures."""


from donghua_cli.sources import ALL_SOURCES
from donghua_cli.sources.base import Episode, Series


class TestRegistry:
    def test_keys_are_unique(self):
        keys = [s.key for s in ALL_SOURCES]
        assert len(keys) == len(set(keys)), f"duplicate source keys: {keys}"

    def test_donghuastream_registered(self):
        ds = next((s for s in ALL_SOURCES if s.key == "ds"), None)
        assert ds is not None
        assert ds.base_url == "https://donghuastream.org"

    def test_hdonghua_repointed_off_dead_xyz(self):
        hd = next((s for s in ALL_SOURCES if s.key == "hd"), None)
        assert hd is not None
        # .xyz TLS-handshake-fails; .com is the live replacement.
        assert "h-donghua.xyz" not in hd.base_url
        assert hd.base_url == "https://h-donghua.com"

    def test_every_source_declares_identity(self):
        for s in ALL_SOURCES:
            assert s.key and s.name and s.base_url.startswith("https://")


class TestEpisode:
    def test_add_url(self):
        ep = Episode(number=1, title="Ep 1")
        ep.add_url("ld", "http://ld/ep1")
        ep.add_url("ax", "http://ax/ep1")
        assert len(ep.urls) == 2
        assert ep.sources == ["ld", "ax"]

    def test_primary_url_is_first(self):
        ep = Episode(number=1, title="Ep 1")
        ep.add_url("ld", "http://ld/ep1")
        ep.add_url("ax", "http://ax/ep1")
        assert ep.primary_url == "http://ld/ep1"

    def test_single_source(self):
        ep = Episode(number=5, title="Ep 5")
        ep.add_url("ax", "http://ax/ep5")
        assert ep.primary_url == "http://ax/ep5"
        assert ep.sources == ["ax"]


class TestSeries:
    def test_multi_source(self):
        s = Series(title="Soul Land")
        s.add_url("ld", "http://ld/soul-land")
        s.add_url("ax", "http://ax/soul-land")
        assert s.sources == ["ld", "ax"]

    def test_single_source(self):
        s = Series(title="Martial Peak")
        s.add_url("ld", "http://ld/martial-peak")
        assert s.sources == ["ld"]
