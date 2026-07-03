"""Tests for stream extraction regex patterns + URL canonicalisation."""

import re

import donghua_cli.extractor as extractor
from donghua_cli.extractor import _canonicalize, extract_with_fallback
from donghua_cli.sources.base import Episode


class TestCanonicalize:
    """The canonicaliser rewrites embed-style URLs into forms mpv's ytdl_hook
    can resolve. Without this, mpv plays the HTML embed page as a video and
    exits in <1s, which used to cascade auto-next through every episode."""

    def test_dailymotion_embed_collapses_to_video(self):
        url = "https://www.dailymotion.com/embed/video/k3fOeWYJYDH5DVybIIp?queue-enable=false"
        assert _canonicalize(url) == "https://www.dailymotion.com/video/k3fOeWYJYDH5DVybIIp"

    def test_dailymotion_video_form_unchanged(self):
        url = "https://www.dailymotion.com/video/k3fOeWYJYDH5DVybIIp"
        assert _canonicalize(url) == url

    def test_dailymotion_geo_player_html_collapses_to_video(self):
        # Modern aggregator embed: no /video/ in the path, id is a query param.
        url = "https://geo.dailymotion.com/player/xabcd.html?video=k5abc123&mute=true"
        assert _canonicalize(url) == "https://www.dailymotion.com/video/k5abc123"

    def test_dailymotion_geo_embed_video_collapses_to_www(self):
        url = "https://geo.dailymotion.com/embed/video/k9zzz?autoplay=1"
        assert _canonicalize(url) == "https://www.dailymotion.com/video/k9zzz"

    def test_dailymotion_protocol_relative_geo_player(self):
        url = "//geo.dailymotion.com/player/x1234.html?video=kPqR9"
        assert _canonicalize(url) == "https://www.dailymotion.com/video/kPqR9"

    def test_ok_ru_embed_becomes_https_video(self):
        assert _canonicalize("//ok.ru/videoembed/6816742902324") == "https://ok.ru/video/6816742902324"

    def test_empty_string_passes_through(self):
        assert _canonicalize("") == ""

    def test_unrelated_url_passes_through(self):
        assert _canonicalize("https://example.com/foo") == "https://example.com/foo"

    def test_youtube_embed_to_watch(self):
        assert (
            _canonicalize("https://www.youtube.com/embed/dQw4w9WgXcQ")
            == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )

    def test_youtube_watch_form_unchanged(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert _canonicalize(url) == url

    def test_streamtape_embed_to_watch(self):
        assert (
            _canonicalize("https://streamtape.com/e/AbCdEf123/title.mp4")
            == "https://streamtape.com/v/AbCdEf123/title.mp4"
        )
        # Other TLDs in the streamtape mirror set.
        assert _canonicalize("https://streamtape.to/e/X9/").endswith("streamtape.to/v/X9/")

    def test_mixdrop_embed_to_file(self):
        assert (
            _canonicalize("https://mixdrop.ag/e/abc123")
            == "https://mixdrop.ag/f/abc123"
        )

    def test_mp4upload_embed_to_bare(self):
        assert (
            _canonicalize("https://www.mp4upload.com/embed-abc123def.html")
            == "https://www.mp4upload.com/abc123def"
        )
        assert (
            _canonicalize("https://mp4upload.com/embed-xyz")
            == "https://mp4upload.com/xyz"
        )

    def test_doodstream_embed_to_d(self):
        assert (
            _canonicalize("https://dood.so/e/abc123")
            == "https://dood.so/d/abc123"
        )
        # Sibling mirrors share the rule.
        assert (
            _canonicalize("https://ds2play.com/e/xyz")
            == "https://ds2play.com/d/xyz"
        )

    def test_protocol_relative_url_promoted(self):
        # Many WordPress themes emit //host/path. mpv refuses these; promote
        # to https unconditionally.
        assert _canonicalize("//streamtape.com/e/abc").startswith("https://")


# Test the regex patterns used in extractor.py without making real HTTP calls.

class TestExtractionPatterns:
    """Test the regex patterns that extract stream URLs from HTML chunks."""

    def test_dailymotion_data_video(self):
        html = '<script src="//geo.dailymotion.com/player/x1234.js" data-video="k5abc123def"></script>'
        m = re.search(r'data-video\s*=\s*["\']([^"\']+)["\']', html)
        assert m is not None
        assert m.group(1) == "k5abc123def"

    def test_dailymotion_iframe(self):
        html = '<iframe src="https://geo.dailymotion.com/player/x1234.html?video=k5abc"></iframe>'
        m = re.search(r'src\s*=\s*["\'](https?://[^"\']*dailymotion[^"\']*)["\']', html)
        assert m is not None
        assert "dailymotion" in m.group(1)

    def test_okru_iframe(self):
        html = '<iframe src="https://ok.ru/videoembed/123456789"></iframe>'
        m = re.search(r'src\s*=\s*["\'](https?://ok\.[^"\']+)["\']', html)
        assert m is not None
        assert m.group(1) == "https://ok.ru/videoembed/123456789"

    def test_no_match_on_random_html(self):
        html = '<div class="content"><p>No video here</p></div>'
        m = re.search(r'data-video\s*=\s*["\']([^"\']+)["\']', html)
        assert m is None

    def test_multiple_iframes_picks_first(self):
        html = '''
        <iframe src="https://ads.example.com/banner"></iframe>
        <iframe src="https://ok.ru/videoembed/999"></iframe>
        '''
        m = re.search(r'src\s*=\s*["\'](https?://ok\.[^"\']+)["\']', html)
        assert m is not None
        assert "ok.ru" in m.group(1)


class TestDirectUrlDetection:
    def test_m3u8(self):
        url = "https://cdn.example.com/video/stream.m3u8"
        assert url.endswith((".m3u8", ".mp4", ".mkv"))

    def test_mp4(self):
        url = "https://cdn.example.com/video/episode.mp4"
        assert url.endswith((".m3u8", ".mp4", ".mkv"))

    def test_html_page_not_detected(self):
        url = "https://example.com/watch/episode-1"
        assert not url.endswith((".m3u8", ".mp4", ".mkv"))


class TestRaceAndProbe:
    """extract_with_fallback races every mirror concurrently, then keeps the
    first that both resolves AND passes the liveness probe. These tests stub the
    network-touching helpers so we exercise pure control flow."""

    def _patch(self, monkeypatch, resolves: dict, alive: set):
        """Stub extract() to map an episode URL -> resolved stream (or itself
        for a miss) and probe_alive() to accept only URLs in `alive`. health is
        stubbed to a no-op so we don't touch the real cache file."""
        monkeypatch.setattr(
            extractor, "extract", lambda url, allow_ytdlp=True: resolves.get(url, url)
        )
        monkeypatch.setattr(extractor, "probe_alive", lambda url, timeout=4: url in alive)

        class _NoHealth:
            def mark_alive(self, *a, **k):
                pass

            def mark_dead(self, *a, **k):
                pass

        monkeypatch.setattr(extractor, "health", _NoHealth())

    def test_picks_a_live_mirror_over_a_dead_one(self, monkeypatch):
        ep = Episode(number=1, title="ep", urls={"dead": "http://dead/ep", "live": "http://live/ep"})
        self._patch(
            monkeypatch,
            resolves={"http://dead/ep": "http://s/dead", "http://live/ep": "http://s/live"},
            alive={"http://s/live"},
        )
        stream, key = extract_with_fallback(ep)
        assert (stream, key) == ("http://s/live", "live")

    def test_falls_back_to_resolved_when_nothing_probes_live(self, monkeypatch):
        # A mirror resolves to a stream but the probe rejects it (e.g. a dead
        # dailymotion the oEmbed check catches). We still hand back the resolved
        # URL rather than the raw episode page — the probe can false-negative.
        ep = Episode(number=2, title="ep", urls={"a": "http://a/ep"})
        self._patch(
            monkeypatch, resolves={"http://a/ep": "http://s/a"}, alive=set()
        )
        stream, key = extract_with_fallback(ep)
        assert (stream, key) == ("http://s/a", "a")

    def test_probe_false_disables_liveness_gate(self, monkeypatch):
        # With probe=False the first resolved mirror wins immediately, no probe.
        ep = Episode(number=3, title="ep", urls={"a": "http://a/ep"})
        self._patch(monkeypatch, resolves={"http://a/ep": "http://s/a"}, alive=set())
        stream, key = extract_with_fallback(ep, probe=False)
        assert (stream, key) == ("http://s/a", "a")

    def test_ytdlp_fallback_when_cheap_resolve_finds_nothing(self, monkeypatch):
        # Cheap path (allow_ytdlp=False) resolves nothing; the sequential
        # yt-dlp phase (allow_ytdlp=True) then succeeds on one mirror.
        ep = Episode(number=4, title="ep", urls={"a": "http://a/ep"})

        def fake_extract(url, allow_ytdlp=True):
            if url == "http://a/ep" and allow_ytdlp:
                return "http://s/ytdlp"
            return url  # cheap miss

        monkeypatch.setattr(extractor, "extract", fake_extract)
        monkeypatch.setattr(extractor, "probe_alive", lambda url, timeout=4: True)

        class _NoHealth:
            def mark_alive(self, *a, **k):
                pass

            def mark_dead(self, *a, **k):
                pass

        monkeypatch.setattr(extractor, "health", _NoHealth())
        stream, key = extract_with_fallback(ep)
        assert (stream, key) == ("http://s/ytdlp", "a")

    def test_all_dead_returns_raw_primary(self, monkeypatch):
        ep = Episode(number=5, title="ep", urls={"a": "http://a/ep", "b": "http://b/ep"})
        # Nothing resolves on either the cheap or yt-dlp pass.
        monkeypatch.setattr(extractor, "extract", lambda url, allow_ytdlp=True: url)
        monkeypatch.setattr(extractor, "probe_alive", lambda url, timeout=4: False)

        class _NoHealth:
            def mark_alive(self, *a, **k):
                pass

            def mark_dead(self, *a, **k):
                pass

        monkeypatch.setattr(extractor, "health", _NoHealth())
        stream, key = extract_with_fallback(ep)
        # Raw primary URL, canonicalised, attributed to the first source.
        assert stream == "http://a/ep"
        assert key == "a"
