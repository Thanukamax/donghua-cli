"""Textual-based TUI for Donghua CLI.

Full-screen terminal app with animated particles, live-updating progress,
toast notifications, and premium Wuxia-themed design.
"""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING, List, Sequence

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Footer,
    Input,
    Label,
    OptionList,
    ProgressBar,
    Rule,
    Static,
)
from textual.widgets.option_list import Option

if TYPE_CHECKING:
    from donghua_cli.sources.base import Episode, Series

# ── Wuxia flavour ────────────────────────────────────────────────────────

TECHNIQUES = [
    "Dragon Tail Sweep", "Phoenix Wing Strike", "Cloud Step Ascension",
    "Mountain Breaker Fist", "Moonlight Cut", "Star Fall Descent",
    "Lotus Palm Strike", "Void Piercer", "Heavenly Sword Flash",
    "Iron Body Tempering", "Azure Dragon Roar", "Shadow Step",
    "Crimson Phoenix Dance", "Jade Emperor's Decree", "Thunder God Fist",
]

LEVELS = [
    "Qi Refining", "Foundation", "Golden Core",
    "Nascent Soul", "Divine Transformation", "Void Refinement",
    "Body Integration", "Tribulation", "Mahayana",
]

# ── Custom Widgets ───────────────────────────────────────────────────────



class ParticleBanner(Static):
    """Plays a BTTH heavenly flame fight clip as half-block pixel art.

    All frames are pre-parsed into Rich Text objects at load time.
    During playback, render() just returns the next pre-parsed object --
    no markup parsing, no string processing, just a pointer swap.
    25 frames at 5fps = 5s loop (seconds 6-11 of the clip).
    """

    from rich.text import Text as _Text

    # Class-level frame cache: pre-parsed Text objects
    _parsed_frames: list[_Text] = []
    _loaded: bool = False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._frame_idx = 0
        self._current: ParticleBanner._Text | str = " \n" * 11

    def render(self) -> str | _Text:
        return self._current

    def on_mount(self) -> None:
        if ParticleBanner._loaded and ParticleBanner._parsed_frames:
            self._current = ParticleBanner._parsed_frames[0]
            self._timer = self.set_interval(1.0 / 4, self._step)
        else:
            # Load + parse in background thread so UI appears instantly
            self._load_in_background()

    @work(thread=True)
    def _load_in_background(self) -> None:
        if not ParticleBanner._loaded:
            self._load_frames()
        if ParticleBanner._parsed_frames:
            self._current = ParticleBanner._parsed_frames[0]
            self.app.call_from_thread(self.refresh)
            # Start the animation timer on the main thread
            self.app.call_from_thread(self._start_timer)

    def _start_timer(self) -> None:
        self._timer = self.set_interval(1.0 / 4, self._step)

    def _load_frames(self) -> None:
        import gzip, json
        from pathlib import Path
        from rich.text import Text

        data_path = Path(__file__).parent / "banner_frames.json.gz"
        if not data_path.exists():
            ParticleBanner._loaded = True
            return

        try:
            with gzip.open(data_path, "rb") as f:
                raw_frames = json.loads(f.read().decode())

            # Pre-parse all markup into Text objects -- this is the key optimization.
            # Parsing happens once at startup, then playback is instant.
            parsed = []
            for markup_str in raw_frames:
                parsed.append(Text.from_markup(markup_str))

            ParticleBanner._parsed_frames = parsed
            ParticleBanner._loaded = True
        except Exception:
            ParticleBanner._parsed_frames = []
            ParticleBanner._loaded = True

    def _step(self) -> None:
        if not ParticleBanner._parsed_frames:
            return
        self._frame_idx = (self._frame_idx + 1) % len(ParticleBanner._parsed_frames)
        self._current = ParticleBanner._parsed_frames[self._frame_idx]
        self.refresh(layout=True)


# ── CSS ──────────────────────────────────────────────────────────────────

WUXIA_CSS = """\

Screen {
    background: #0c0e1a;
}

/* ─── Particle Banner ─── */

ParticleBanner {
    width: 100%;
    height: 12;
    background: #0c0e1a;
    overflow: hidden;
}

/* ─── Banner title ─── */

#banner-title {
    width: 100%;
    height: 1;
    text-align: center;
    background: #0c0e1a;
    color: #fbbf24;
    margin: 0;
}

/* ─── Banner sub-info ─── */

#banner-badges {
    width: 100%;
    height: 1;
    text-align: center;
    background: #0c0e1a;
    color: #475569;
    margin-bottom: 0;
}


/* ─── Rule ─── */

Rule {
    color: #1e293b;
    margin: 0 3;
}

/* ─── Search ─── */

#search-box {
    height: auto;
    padding: 0 3;
    margin: 0 0 1 0;
}

#search-label {
    color: #475569;
    padding: 0 1;
    height: 1;
}

#search-input {
    border: tall #1e293b;
    padding: 0 1;
    background: #111827;
    color: #e2e8f0;
}

#search-input:focus {
    border: tall #5eead4;
    background: #0f172a;
}

/* ─── Status bar ─── */

#status-bar {
    dock: bottom;
    height: 1;
    padding: 0 3;
    background: #111827;
    color: #94a3b8;
}

/* ─── Results / Episodes ─── */

#results-container {
    height: 1fr;
    padding: 0 2;
    margin: 0;
}

/* ─── OptionList ─── */

OptionList {
    height: 1fr;
    border: round #1e293b;
    background: #0c0e1a;
    scrollbar-background: #0c0e1a;
    scrollbar-color: #1e293b;
    scrollbar-color-hover: #5eead4;
    scrollbar-color-active: #fbbf24;
    scrollbar-size-vertical: 1;
}

OptionList > .option-list--option {
    padding: 0 2;
    color: #cbd5e1;
}

OptionList > .option-list--option-highlighted {
    background: #5eead4 12%;
    color: #fbbf24;
    text-style: bold;
}

OptionList > .option-list--option-hover {
    background: #5eead4 6%;
}

OptionList:focus {
    border: round #5eead4 40%;
}

/* ─── Episode header ─── */

#episode-header {
    padding: 1 3;
    height: auto;
    background: #111827;
    border-bottom: heavy #1e293b;
}

/* ─── Help bar ─── */

#help-text {
    text-align: center;
    color: #475569;
    padding: 0 1;
    height: 1;
    background: #111827;
    dock: bottom;
}

/* ─── Now Playing ─── */

#np-outer {
    width: 100%;
    height: auto;
    padding: 1 4;
}

#np-header {
    width: 100%;
    text-align: center;
    padding: 1 0;
    background: #111827;
    border: heavy #5eead4 30%;
}

#np-body {
    width: 100%;
    padding: 1 4;
    background: #0c0e1a;
    height: auto;
    border: round #1e293b;
    margin: 1 0 0 0;
}

#np-progress-box {
    width: 100%;
    height: auto;
    padding: 0 4;
    margin: 1 0 0 0;
}

#np-progress-label {
    text-align: center;
    color: #94a3b8;
    height: 1;
}

ProgressBar {
    padding: 0;
    margin: 0;
}

ProgressBar > .bar--bar {
    color: #5eead4;
    background: #1e293b;
}

ProgressBar > .bar--complete {
    color: #5eead4;
}

#np-server {
    text-align: center;
    color: #64748b;
    height: 1;
    margin: 1 0 0 0;
}

/* ─── Controls ─── */

#controls-panel {
    padding: 1 4;
    margin: 1 4;
    border: round #1e293b;
    background: #111827;
    height: auto;
}

/* ─── Footer ─── */

Footer {
    background: #111827;
    color: #64748b;
}

Footer > .footer--key {
    background: #1e293b;
    color: #fbbf24;
    text-style: bold;
}

Footer > .footer--description {
    color: #94a3b8;
}

LoadingIndicator {
    color: #a78bfa;
}
"""

# ── Screens ──────────────────────────────────────────────────────────────


class SearchScreen(Screen):
    """Search screen with animated particle banner."""

    BINDINGS = [
        Binding("escape", "quit", "Quit", show=True),
    ]

    def __init__(self, app_core) -> None:
        super().__init__()
        self._core = app_core
        self._results: list[Series] = []

    def compose(self) -> ComposeResult:
        yield ParticleBanner(id="particle-banner")
        yield Static(
            "[bold #fbbf24]\u6b66\u4fa0\u52a8\u753b\u7ec8\u7aef[/]  "
            "[#334155]\u2502[/]  "
            "[bold #5eead4]DONGHUA CLI[/] [#475569]v3.1[/]",
            id="banner-title",
        )
        yield Static(
            "[#334155][[/][#f43f5e] v3.1 [/][#334155]][/]  "
            "[#334155][[/][#5eead4] Stream [/][#334155]][/]  "
            "[#334155][[/][#a78bfa] Download [/][#334155]][/]  "
            "[#334155][[/][#fbbf24] Cultivate [/][#334155]][/]",
            id="banner-badges",
        )
        yield Rule(line_style="heavy")

        with Container(id="search-box"):
            yield Input(placeholder="  Search for donghua...", id="search-input")

        yield Static("", id="status-bar")
        with Container(id="results-container"):
            yield OptionList(id="results-list")

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()

    @on(Input.Submitted, "#search-input")
    def on_search(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return
        self._do_search(query)

    @work(thread=True)
    def _do_search(self, query: str) -> None:
        status = self.query_one("#status-bar", Static)
        results_list = self.query_one("#results-list", OptionList)

        self.app.call_from_thread(
            status.update,
            f"  [#a78bfa]\u27f3[/] [#94a3b8]Searching[/] [bold #e2e8f0]'{query}'[/]",
        )
        self.app.call_from_thread(results_list.clear_options)

        from donghua_cli.scraper import search_all
        results = search_all(query)
        self._results = results

        if not results:
            self.app.call_from_thread(
                status.update,
                "  [#f43f5e]\u2717[/] [#94a3b8]No results[/]",
            )
            self.app.call_from_thread(
                self.app.notify, "No results found", title="Search", severity="warning",
            )
            return

        multi = sum(1 for s in results if len(s.sources) > 1)
        self.app.call_from_thread(
            status.update,
            f"  [#5eead4]\u2713[/] [bold]{len(results)}[/] [#94a3b8]results[/]"
            f"  [#334155]\u2502[/]  "
            f"[#5eead4]{multi}[/] [#64748b]multi-server[/]",
        )

        from donghua_cli.scraper import _is_movie
        options = []
        for i, s in enumerate(results):
            if _is_movie(s.title):
                tag = "[#0c0e1a on #f43f5e] MOVIE [/]"
            else:
                tag = "[#0c0e1a on #22d3ee] SERIES [/]"

            sc = len(s.sources)
            bars = "[#5eead4]\u2503[/]" * sc + "[#1e293b]\u2503[/]" * max(0, 5 - sc)

            label = (
                f"[bold #fbbf24]{i+1:2d}[/]  "
                f"{tag}  "
                f"[#e2e8f0]{s.title[:42]}[/]  "
                f"{bars}"
            )
            options.append(Option(label, id=str(i)))

        self.app.call_from_thread(self._populate_results, options)
        self.app.call_from_thread(
            self.app.notify,
            f"{len(results)} result(s) found",
            title="\u2713 Search Complete",
            timeout=3,
        )

    def _populate_results(self, options: list[Option]) -> None:
        rl = self.query_one("#results-list", OptionList)
        rl.clear_options()
        for opt in options:
            rl.add_option(opt)
        rl.focus()

    @on(OptionList.OptionSelected, "#results-list")
    def on_select(self, event: OptionList.OptionSelected) -> None:
        idx = int(event.option_id)
        if 0 <= idx < len(self._results):
            self.app.push_screen(EpisodeScreen(self._core, self._results[idx]))

    def action_quit(self) -> None:
        self.app.exit()


class EpisodeScreen(Screen):
    """Episode selection with server health bars."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("a", "select_all", "Play All", show=True),
        Binding("enter", "confirm", "Play", show=True),
    ]

    def __init__(self, app_core, series: Series) -> None:
        super().__init__()
        self._core = app_core
        self._series = series
        self._episodes: list[Episode] = []

    def compose(self) -> ComposeResult:
        srv_pills = "  ".join(
            f"[#0c0e1a on #5eead4] {s.upper()} [/]" for s in self._series.sources
        )
        yield Static(
            f"[bold #fbbf24]{self._series.title}[/]\n{srv_pills}",
            id="episode-header",
        )
        yield Static("", id="status-bar")
        with Container(id="results-container"):
            yield OptionList(id="episode-list")
        yield Static(
            "[bold #fbbf24]Enter[/] [#475569]play[/]  "
            "[#1e293b]\u2502[/]  "
            "[bold #fbbf24]A[/] [#475569]play all[/]  "
            "[#1e293b]\u2502[/]  "
            "[bold #fbbf24]Esc[/] [#475569]back[/]",
            id="help-text",
        )

    def on_mount(self) -> None:
        self._load_episodes()

    @work(thread=True)
    def _load_episodes(self) -> None:
        status = self.query_one("#status-bar", Static)
        self.app.call_from_thread(
            status.update, "  [#a78bfa]\u27f3[/] [#94a3b8]Loading episodes...[/]",
        )

        from donghua_cli.scraper import get_episodes
        episodes = get_episodes(self._series)
        self._episodes = episodes

        if not episodes:
            self.app.call_from_thread(
                status.update, "  [#f43f5e]\u2717[/] [#94a3b8]No episodes[/]",
            )
            self.app.call_from_thread(
                self.app.notify, "No episodes found", title="Episodes", severity="warning",
            )
            return

        multi = sum(1 for e in episodes if len(e.sources) > 1)
        self.app.call_from_thread(
            status.update,
            f"  [#5eead4]\u2713[/] [bold]{len(episodes)}[/] [#94a3b8]episodes[/]"
            f"  [#334155]\u2502[/]  "
            f"[#5eead4]{multi}[/] [#64748b]multi-server[/]",
        )

        options = []
        for i, ep in enumerate(episodes):
            num = ep.number if ep.number < 999999 else i + 1
            sc = len(ep.sources)
            bars = "[#5eead4]\u2503[/]" * sc + "[#1e293b]\u2503[/]" * max(0, 5 - sc)
            label = (
                f"[bold #fbbf24]{i+1:3d}[/]  "
                f"[#94a3b8]EP[/] [bold #e2e8f0]{num:<4}[/]  "
                f"{bars}"
            )
            options.append(Option(label, id=str(i)))

        self.app.call_from_thread(self._populate, options)
        self.app.call_from_thread(
            self.app.notify, f"{len(episodes)} episodes loaded", title="\u2713 Ready", timeout=2,
        )

    def _populate(self, options: list[Option]) -> None:
        el = self.query_one("#episode-list", OptionList)
        el.clear_options()
        for opt in options:
            el.add_option(opt)
        el.focus()

    @on(OptionList.OptionSelected, "#episode-list")
    def on_select(self, event: OptionList.OptionSelected) -> None:
        idx = int(event.option_id)
        if 0 <= idx < len(self._episodes):
            self.app.push_screen(
                PlaybackScreen(self._core, self._episodes[idx:], self._series.title)
            )

    def action_select_all(self) -> None:
        if self._episodes:
            self.app.push_screen(
                PlaybackScreen(self._core, self._episodes, self._series.title)
            )

    def action_confirm(self) -> None:
        el = self.query_one("#episode-list", OptionList)
        if el.highlighted is not None and self._episodes:
            self.app.push_screen(
                PlaybackScreen(self._core, self._episodes[el.highlighted:], self._series.title)
            )

    def action_go_back(self) -> None:
        self.app.pop_screen()


class PlaybackScreen(Screen):
    """Playback screen with progress bar and toasts."""

    BINDINGS = [
        Binding("n", "next_ep", "Next", show=True),
        Binding("p", "prev_ep", "Prev", show=True),
        Binding("r", "replay", "Replay", show=True),
        Binding("d", "download", "Download", show=True),
        Binding("q", "quit_playback", "Quit", show=True),
    ]

    current_idx = reactive(0)

    def __init__(self, app_core, episodes: list[Episode], series_title: str) -> None:
        super().__init__()
        self._core = app_core
        self._episodes = episodes
        self._series_title = series_title
        self._stream_url = ""
        self._server_name = ""

    def compose(self) -> ComposeResult:
        with Container(id="np-outer"):
            yield Static("", id="np-header")
            with Container(id="np-body"):
                yield Static("", id="np-body-text")
            with Container(id="np-progress-box"):
                yield Static("", id="np-progress-label")
                yield ProgressBar(total=max(len(self._episodes), 1), show_eta=False, show_percentage=False)
            yield Static("", id="np-server")

        yield Static("", id="controls-panel")
        yield Static("", id="status-bar")

    def on_mount(self) -> None:
        self._play_current()

    def watch_current_idx(self, value: int) -> None:
        self._update_display()

    def _update_display(self) -> None:
        if not self._episodes or self.current_idx >= len(self._episodes):
            return
        ep = self._episodes[self.current_idx]
        num = ep.number if ep.number < 999999 else self.current_idx + 1
        level = random.choice(LEVELS)
        servers = " [#334155]\u00b7[/] ".join(f"[#5eead4]{s.upper()}[/]" for s in ep.sources)
        cur = self.current_idx + 1
        total = len(self._episodes)

        self._safe_update("#np-header",
            f"[bold #f43f5e]\u25b6[/]  [bold #fbbf24]NOW PLAYING[/]  [bold #f43f5e]\u25b6[/]"
        )
        self._safe_update("#np-body-text",
            f"[#7c3aed]\u2726[/] [italic #a78bfa]{level}[/] [#7c3aed]\u2726[/]\n\n"
            f"[bold #fbbf24]{self._series_title}[/]\n"
            f"[#94a3b8]Episode[/] [bold #5eead4]{num}[/]"
        )
        self._safe_update("#np-progress-label",
            f"[bold #e2e8f0]{cur}[/] [#475569]/[/] [#94a3b8]{total}[/]"
        )
        self._safe_update("#np-server",
            f"[#5eead4]\u25b8[/] [bold #e2e8f0]{self._server_name}[/]  "
            f"[#1e293b]\u2502[/]  {servers}"
        )

        try:
            self.query_one(ProgressBar).update(total=total, progress=cur)
        except NoMatches:
            pass

        can_n = self.current_idx < len(self._episodes) - 1
        can_p = self.current_idx > 0
        def _k(k: str, l: str, on: bool = True) -> str:
            return f"[bold #fbbf24]{k}[/] [#e2e8f0]{l}[/]" if on else f"[#1e293b]{k}[/] [#334155]{l}[/]"

        self._safe_update("#controls-panel",
            f"  {_k('N','Next',can_n)}    {_k('P','Prev',can_p)}    "
            f"{_k('R','Replay')}    {_k('D','Download')}    {_k('Q','Quit')}"
        )

    def _safe_update(self, selector: str, content: str) -> None:
        try:
            self.query_one(selector, Static).update(content)
        except NoMatches:
            pass

    @work(thread=True)
    def _play_current(self) -> None:
        if self.current_idx >= len(self._episodes):
            self.app.call_from_thread(self._safe_update, "#status-bar",
                "  [#5eead4]\u2713[/] [bold]All episodes complete![/]")
            self.app.call_from_thread(self.app.notify,
                "All episodes played!", title="\u2726 Complete")
            return

        ep = self._episodes[self.current_idx]
        self.app.call_from_thread(self._safe_update, "#status-bar",
            "  [#a78bfa]\u27f3[/] [#94a3b8]Resolving stream...[/]")

        from donghua_cli.extractor import extract_with_fallback
        from donghua_cli.sources import get_source

        stream_url, source_key = extract_with_fallback(ep)
        self._stream_url = stream_url
        source = get_source(source_key)
        self._server_name = source.name if source else source_key.upper()

        self.app.call_from_thread(self._update_display)

        from donghua_cli.player import Player
        player = Player(self._core._quality)
        title = f"{self._series_title} - Episode {ep.number}"

        if player.play(stream_url, title=title):
            self.app.call_from_thread(self._safe_update, "#status-bar",
                f"  [#5eead4]\u2713[/] Playing via [bold]{self._server_name}[/]")
            self.app.call_from_thread(self.app.notify,
                f"Playing via {self._server_name}", title=f"\u25b6 Episode {ep.number}", timeout=3)
        else:
            self.app.call_from_thread(self._safe_update, "#status-bar",
                f"  [#f43f5e]\u2717[/] No player found")
            self.app.call_from_thread(self.app.notify,
                f"Install mpv or vlc.\nURL: {stream_url[:50]}", title="No Player", severity="error")

    def action_next_ep(self) -> None:
        if self.current_idx < len(self._episodes) - 1:
            self.current_idx += 1
            self._play_current()

    def action_prev_ep(self) -> None:
        if self.current_idx > 0:
            self.current_idx -= 1
            self._play_current()

    def action_replay(self) -> None:
        self._play_current()

    def action_download(self) -> None:
        if not self._stream_url:
            return
        ep = self._episodes[self.current_idx]
        self._safe_update("#status-bar", "  [#a78bfa]\u27f3[/] Downloading...")
        self.app.notify("Download started...", title="\u2b07 Download", timeout=2)

        from donghua_cli.player import Downloader
        if Downloader.download(self._stream_url, self._series_title, ep.title, self._core._quality):
            self._safe_update("#status-bar", "  [#5eead4]\u2713[/] Download complete")
            self.app.call_from_thread(self.app.notify, "Saved!", title="\u2713 Downloaded")
        else:
            self._safe_update("#status-bar", "  [#f43f5e]\u2717[/] Download failed")
            self.app.call_from_thread(self.app.notify, "Failed", title="Error", severity="error")

    def action_quit_playback(self) -> None:
        self.app.pop_screen()


# ── Main App ─────────────────────────────────────────────────────────────


class DonghuaTUI(App):
    TITLE = "Donghua CLI"
    SUB_TITLE = "\u6b66\u4fa0\u52a8\u753b\u7ec8\u7aef"
    CSS = WUXIA_CSS

    BINDINGS = [Binding("ctrl+c", "quit", "Quit")]

    def __init__(self, app_core) -> None:
        super().__init__()
        self._core = app_core

    def on_mount(self) -> None:
        self.push_screen(SearchScreen(self._core))
