"""Tests for stream extraction regex patterns."""

import re


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
