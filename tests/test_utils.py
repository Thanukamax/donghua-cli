"""Tests for utility functions."""


from donghua_cli.utils import extract_episode_number, sanitize_filename


class TestSanitizeFilename:
    def test_removes_special_chars(self):
        assert sanitize_filename('Test: Episode 1') == "Test_ Episode 1"

    def test_removes_slashes(self):
        assert sanitize_filename("path/to\\file") == "path_to_file"

    def test_collapses_underscores(self):
        assert sanitize_filename("a::b") == "a_b"

    def test_strips_dots_and_spaces(self):
        assert sanitize_filename("  test. ") == "test"

    def test_empty_returns_untitled(self):
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("...") == "untitled"

    def test_preserves_normal_chars(self):
        assert sanitize_filename("Soul Land Episode 42") == "Soul Land Episode 42"

    def test_unicode_preserved(self):
        assert sanitize_filename("斗罗大陆 Episode 1") == "斗罗大陆 Episode 1"


class TestExtractEpisodeNumber:
    def test_standard_episode(self):
        assert extract_episode_number("Episode 42", "") == 42

    def test_episode_with_dash(self):
        assert extract_episode_number("Episode-12", "") == 12

    def test_ep_abbreviation(self):
        assert extract_episode_number("EP 7", "") == 7

    def test_chinese_format(self):
        assert extract_episode_number("第5集", "") == 5
        assert extract_episode_number("第12话", "") == 12

    def test_from_url(self):
        assert extract_episode_number("", "https://example.com/episode-15/") == 15

    def test_trailing_number(self):
        assert extract_episode_number("Soul Land 42", "") == 42

    def test_no_number_returns_sentinel(self):
        assert extract_episode_number("Soul Land", "https://example.com/") == 999999

    def test_title_takes_priority_over_url(self):
        assert extract_episode_number("Episode 5", "https://example.com/episode-10/") == 5

    def test_case_insensitive(self):
        assert extract_episode_number("EPISODE 99", "") == 99
        assert extract_episode_number("ep 3", "") == 3


class TestProbeAlive:
    def test_dailymotion_published_video_returns_true(self, monkeypatch):
        from donghua_cli import utils

        class DummyResponse:
            status_code = 200

            def json(self):
                return {"id": "x123", "status": "published"}

        monkeypatch.setattr(
            utils, "get_client", lambda: type("C", (), {"get": lambda s, u, **k: DummyResponse()})()
        )
        assert utils.probe_alive("https://www.dailymotion.com/video/k3jQk") is True

    def test_dailymotion_deleted_video_returns_false(self, monkeypatch):
        from donghua_cli import utils

        class DummyResponse:
            status_code = 404

            def json(self):
                return {"error": {"code": 404, "message": "deleted"}}

        monkeypatch.setattr(
            utils, "get_client", lambda: type("C", (), {"get": lambda s, u, **k: DummyResponse()})()
        )
        assert utils.probe_alive("https://www.dailymotion.com/video/k5zvC") is False

    def test_okru_live_video_returns_true(self, monkeypatch):
        from donghua_cli import utils

        class DummyResponse:
            status_code = 200
            text = '<html><div data-module="OKVideo"></div></html>'

        monkeypatch.setattr(
            utils, "get_client", lambda: type("C", (), {"get": lambda s, u, **k: DummyResponse()})()
        )
        assert utils.probe_alive("https://ok.ru/video/14560929319603") is True

    def test_okru_deleted_video_returns_false(self, monkeypatch):
        from donghua_cli import utils

        class DummyResponse:
            status_code = 200
            text = '<html><title>OK</title><body>Video not found</body></html>'

        monkeypatch.setattr(
            utils, "get_client", lambda: type("C", (), {"get": lambda s, u, **k: DummyResponse()})()
        )
        assert utils.probe_alive("https://ok.ru/video/16051238603360") is False

