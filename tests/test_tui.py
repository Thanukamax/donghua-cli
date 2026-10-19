

class TestClip:
    """Titles must show a cut, not look like corrupt data."""

    def test_short_text_is_untouched(self):
        from donghua_cli.tui import _clip
        assert _clip("Perfect World", 32) == "Perfect World"

    def test_long_text_gets_an_ellipsis(self):
        from donghua_cli.tui import _clip
        got = _clip("Battle Through The Heavens Season 5 Special", 32)
        assert got.endswith("…")

    def test_result_never_exceeds_the_budget(self):
        # The ellipsis lives inside `width`, so a fixed-width column cannot be
        # blown out by one cell.
        from donghua_cli.tui import _clip
        for w in (1, 5, 12, 32, 60):
            assert len(_clip("x" * 200, w)) <= w


class TestTheme:
    """The Textual theme and the Rich palette must not drift apart."""

    def test_theme_is_built_from_the_palette(self):
        from donghua_cli.palette import PALETTE, build_theme
        t = build_theme()
        assert t.primary == PALETTE["accent"]
        assert t.secondary == PALETTE["accent_alt"]
        assert t.background == PALETTE["surface"]
        assert t.error == PALETTE["danger"]

    def test_css_carries_no_format_placeholders(self):
        # The CSS used to be a .format() template, which meant every literal
        # brace had to be doubled. Guard against that pattern coming back.
        import re
        from donghua_cli.tui import WUXIA_CSS
        assert "{{" not in WUXIA_CSS
        assert not re.search(r"\{[a-z_]+\}", WUXIA_CSS)


class TestConfigAutoNext:
    def test_default_auto_next_is_false(self, monkeypatch):
        from donghua_cli import config

        monkeypatch.setattr(config, "_user_config", {})
        monkeypatch.setattr(config, "tomllib", None)
        assert config.get_auto_next() is False

    def test_custom_auto_next_setting(self, monkeypatch):
        from donghua_cli import config

        monkeypatch.setattr(config, "_user_config", {"auto_next": True})
        assert config.get_auto_next() is True


class TestEpisodeSelectionAndPlayback:
    def test_clicking_episode_plays_immediately(self):
        from unittest.mock import MagicMock
        from donghua_cli.sources.base import Episode, Series
        from donghua_cli.tui import EpisodeScreen, PlaybackScreen
        from textual._context import active_app

        series = Series(title="BTTH", urls={"dw": "https://donghuaworld.com/btth"})
        ep1 = Episode(number=204, title="Episode 204", urls={"dw": "https://donghuaworld.com/btth/204"})
        ep2 = Episode(number=205, title="Episode 205", urls={"dw": "https://donghuaworld.com/btth/205"})
        es = EpisodeScreen(app_core=None, series=series)
        es._episodes = [ep1, ep2]
        fake_app = MagicMock()
        token = active_app.set(fake_app)
        try:
            # Clicking / selecting episode index 0 plays immediately
            es._play_episode(0)
            assert fake_app.push_screen.called
            pushed = fake_app.push_screen.call_args[0][0]
            assert isinstance(pushed, PlaybackScreen)
            assert pushed._episodes == [ep1, ep2]
        finally:
            active_app.reset(token)

    def test_playback_screen_next_ep_advances(self):
        from unittest.mock import MagicMock
        from donghua_cli.sources.base import Episode
        from donghua_cli.tui import PlaybackScreen

        ep1 = Episode(number=1, title="Episode 1", urls={"dw": "https://donghuaworld.com/ep1"})
        ep2 = Episode(number=2, title="Episode 2", urls={"dw": "https://donghuaworld.com/ep2"})
        ps = PlaybackScreen(
            app_core=None,
            episodes=[ep1, ep2],
            series="Test Series",
        )
        ps._play_current = MagicMock()
        assert ps.current_idx == 0

        # Pressing 'N' advances to the next episode and calls _play_current
        ps.action_next_ep()
        assert ps.current_idx == 1
        assert ps._play_current.called


class TestSearchScreenFiltersAndSections:
    """Test movie vs series sectioning and filter toggling in SearchScreen."""

    def test_search_results_partitioning_into_sections(self):
        import asyncio
        from textual.app import App
        from textual.widgets import OptionList, Static
        from donghua_cli.sources.base import Series
        from donghua_cli.tui import SearchScreen

        class DummyApp(App):
            pass

        async def run():
            app = DummyApp()
            async with app.run_test():
                screen = SearchScreen(app_core=None)
                await app.push_screen(screen)
                s1 = Series(title="Soul Land Season 1")
                m1 = Series(title="Battle Through The Heavens Movie: Origin")
                s2 = Series(title="Perfect World")
                screen._results = [s1, m1, s2]
                screen._populate_results()

                ol = screen.query_one("#results-list", OptionList)
                assert len(ol.options) == 5
                # Header 1: Series
                assert ol.options[0].disabled is True
                assert "SERIES" in str(ol.options[0].prompt)
                # Item 1: Series 1 (id="0")
                assert ol.options[1].disabled is False
                assert ol.options[1].id == "0"
                assert "Soul Land" in str(ol.options[1].prompt)
                # Item 2: Series 2 (id="2")
                assert ol.options[2].disabled is False
                assert ol.options[2].id == "2"
                assert "Perfect World" in str(ol.options[2].prompt)
                # Header 2: Movies
                assert ol.options[3].disabled is True
                assert "MOVIES" in str(ol.options[3].prompt)
                # Item 3: Movie 1 (id="1")
                assert ol.options[4].disabled is False
                assert ol.options[4].id == "1"
                assert "Movie: Origin" in str(ol.options[4].prompt)

                # Filter strip check
                fs = screen.query_one("#filter-strip", Static)
                rendered = str(fs.content)
                assert "All (3)" in rendered
                assert "Series (2)" in rendered
                assert "Movies (1)" in rendered

        asyncio.run(run())

    def test_filter_cycling_series_and_movies(self):
        import asyncio
        from textual.app import App
        from textual.widgets import OptionList
        from donghua_cli.sources.base import Series
        from donghua_cli.tui import SearchScreen

        class DummyApp(App):
            pass

        async def run():
            app = DummyApp()
            async with app.run_test() as pilot:
                screen = SearchScreen(app_core=None)
                await app.push_screen(screen)
                s1 = Series(title="Soul Land Season 1")
                m1 = Series(title="Battle Through The Heavens Movie: Origin")
                screen._results = [s1, m1]
                screen._populate_results()
                await pilot.pause()

                ol = screen.query_one("#results-list", OptionList)

                # Cycle from "all" to "series"
                screen.action_cycle_filter()
                assert screen.filter_mode == "series"
                # In series mode: 1 header + 1 series item
                assert len(ol.options) == 2
                assert ol.options[0].disabled is True
                assert ol.options[1].id == "0"

                # Cycle from "series" to "movies"
                screen.action_cycle_filter()
                assert screen.filter_mode == "movies"
                # In movies mode: 1 header + 1 movie item
                assert len(ol.options) == 2
                assert ol.options[0].disabled is True
                assert ol.options[1].id == "1"

                # Cycle from "movies" back to "all"
                screen.action_cycle_filter()
                assert screen.filter_mode == "all"
                assert len(ol.options) == 4

        asyncio.run(run())

    def test_empty_category_fallback_option(self):
        import asyncio
        from textual.app import App
        from textual.widgets import OptionList
        from donghua_cli.sources.base import Series
        from donghua_cli.tui import SearchScreen

        class DummyApp(App):
            pass

        async def run():
            app = DummyApp()
            async with app.run_test():
                screen = SearchScreen(app_core=None)
                await app.push_screen(screen)
                # Only series, no movies
                screen._results = [Series(title="A Will Eternal Season 2")]
                screen._populate_results()

                ol = screen.query_one("#results-list", OptionList)

                # Switch to movies mode
                screen.filter_mode = "movies"
                screen._populate_results()
                assert len(ol.options) == 2
                assert ol.options[0].disabled is True
                # Second option is fallback prompt
                assert ol.options[1].disabled is True
                assert "No movies found" in str(ol.options[1].prompt)

        asyncio.run(run())

    def test_selection_maps_to_correct_series_in_any_filter(self):
        import asyncio
        from unittest.mock import MagicMock
        from textual.app import App
        from donghua_cli.sources.base import Series
        from donghua_cli.tui import EpisodeScreen, SearchScreen

        class DummyApp(App):
            pass

        async def run():
            app = DummyApp()
            async with app.run_test():
                screen = SearchScreen(app_core=None)
                await app.push_screen(screen)
                s1 = Series(title="Soul Land Season 1")
                m1 = Series(title="Battle Through The Heavens Movie: Origin")
                screen._results = [s1, m1]

                # In movies mode, movie is selected
                screen.filter_mode = "movies"
                screen._populate_results()

                fake_push = MagicMock()
                app.push_screen = fake_push

                event = MagicMock()
                event.option_id = "1"
                screen.on_select(event)

                assert fake_push.called
                pushed = fake_push.call_args[0][0]
                assert isinstance(pushed, EpisodeScreen)
                assert pushed._series == m1

        asyncio.run(run())

    def test_ui_select_from_list_with_badges_sections(self, monkeypatch):
        from donghua_cli import ui

        items = [
            ("Soul Land Season 1", "[SERIES] [LD]"),
            ("BTTH Movie", "[MOVIE] [LD]"),
        ]
        monkeypatch.setattr(ui.console, "input", lambda *args: "2")
        chosen = ui.select_from_list_with_badges(items, "Results")
        assert chosen == 1



