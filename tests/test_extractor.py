"""Tests for stream extraction regex patterns + URL canonicalisation."""

import re

from donghua_cli.extractor import _canonicalize


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
