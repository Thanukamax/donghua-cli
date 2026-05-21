"""Textual-based TUI for Donghua CLI.

Restrained design: single accent per screen, fixed 5-glyph budget, no random
flavor in render paths. All colors come from palette.py.

Screens:
- SearchScreen   — query input + live per-source progress + results list
- EpisodeScreen  — episodes for a chosen series, optional cover art
- PlaybackScreen — now-playing + controls; auto-advances when configured
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Input,
    OptionList,
    ProgressBar,
    Rule,
    Static,
)
from textual.widgets.option_list import Option

from donghua_cli import __version__
from donghua_cli.palette import GLYPH, PALETTE
from donghua_cli.theme import TECHNIQUES, level_for_episode

if TYPE_CHECKING:
    from donghua_cli.sources.base import Episode, Series

# Banner technique is pinned for the lifetime of the app — never reshuffles
# on every render, so the eye can anchor.
_SESSION_TECHNIQUE = random.choice(TECHNIQUES)


# ── Static banner (replaces the old animated ParticleBanner) ─────────────


class StaticBanner(Static):
    """Quiet 4-row title block. Renders once, never redraws.

    Replaces the old 12-row 4fps animated particle banner. The old banner
    earned its space the first time a user saw it; not the hundredth.
    """

    DEFAULT_CSS = ""

    def on_mount(self) -> None:
        accent = PALETTE["accent"]
        accent_alt = PALETTE["accent_alt"]
        muted = PALETTE["text_muted"]
        faint = PALETTE["text_faint"]
        ghost = PALETTE["text_ghost"]

        body = (
            f"[bold {accent}]武 侠 动 画 终 端[/]\n"
            f"[bold {accent_alt}]D O N G H U A   C L I[/]   "
            f"[{muted}]v{__version__}[/]\n"
            f"[{ghost}]{'─' * 36}[/]\n"
            f"[italic {faint}]{_SESSION_TECHNIQUE}[/]"
        )
        self.update(body)


# ── CSS (token-driven, built from palette at module load) ────────────────

_CSS_TEMPLATE = """
Screen {{
    background: {surface};
}}

/* ── Static banner ── */
StaticBanner {{
    width: 100%;
    height: 4;
    content-align: center middle;
    text-align: center;
    background: {surface};
    margin: 1 0 0 0;
}}

/* ── Rule ── */
Rule {{
    color: {border};
    margin: 0 3;
}}

/* ── Search input ── */
#search-box {{
    height: auto;
    padding: 0 3;
    margin: 0 0 1 0;
}}

#search-input {{
    border: tall {border};
    padding: 0 1;
    background: {surface_alt};
    color: {text};
}}

#search-input:focus {{
    border: tall {accent_alt};
    background: {surface};
}}

/* ── Status bar (inline, above results) ── */
#status-bar {{
    height: 1;
    padding: 0 3;
    color: {text_muted};
}}

#continue-strip {{
    height: auto;
    padding: 0 3;
    color: {text_muted};
}}

/* ── Results / Episodes container ── */
#results-container {{
    height: 1fr;
    padding: 0 2;
    margin: 0;
}}

/* ── OptionList ── */
OptionList {{
    height: 1fr;
    border: round {border};
    background: {surface};
    scrollbar-background: {surface};
    scrollbar-color: {border};
    scrollbar-color-hover: {accent_alt};
    scrollbar-color-active: {accent};
    scrollbar-size-vertical: 1;
}}

OptionList > .option-list--option {{
    padding: 0 2;
    color: {text};
}}

OptionList > .option-list--option-highlighted {{
    background: {accent_alt} 12%;
    color: {accent};
    text-style: bold;
}}

OptionList > .option-list--option-hover {{
    background: {accent_alt} 6%;
}}

OptionList:focus {{
    border: round {accent_alt} 40%;
}}

/* ── Empty-state hint inside the list area ── */
#empty-hint {{
    width: 100%;
    height: auto;
    padding: 1 3;
    text-align: center;
    color: {text_faint};
}}

/* ── Episode header ── */
#episode-header {{
    padding: 1 3;
    height: auto;
    background: {surface_alt};
    border-bottom: heavy {border};
}}

#series-cover {{
    height: auto;
    width: auto;
    margin: 0 3;
}}

/* ── Help bar (docked at bottom) ── */
#help-text {{
    text-align: center;
    color: {text_faint};
    padding: 0 1;
    height: 1;
    background: {surface_alt};
    dock: bottom;
}}

/* ── Now Playing ── */
#np-outer {{
    width: 100%;
    height: auto;
    padding: 1 3;
}}

#np-title {{
    width: 100%;
    text-align: center;
    color: {text};
    text-style: bold;
    padding: 1 0 0 0;
}}

#np-meta {{
    width: 100%;
    text-align: center;
    color: {text_muted};
    padding: 0 0 1 0;
}}

#np-progress-box {{
    width: 100%;
    height: auto;
    padding: 0 4;
}}

ProgressBar {{
    padding: 0;
    margin: 0;
}}

ProgressBar > .bar--bar {{
    color: {accent_alt};
    background: {border};
}}

ProgressBar > .bar--complete {{
    color: {accent_alt};
}}

/* ── Controls strip ── */
#controls-panel {{
    width: 100%;
    text-align: center;
    padding: 1 0;
    color: {text};
}}

/* ── Footer ── */
Footer {{
    background: {surface_alt};
    color: {text_faint};
}}

Footer > .footer--key {{
    background: {border};
    color: {accent};
    text-style: bold;
}}

Footer > .footer--description {{
    color: {text_muted};
}}

LoadingIndicator {{
    color: {accent_alt};
}}
"""

WUXIA_CSS = _CSS_TEMPLATE.format(**PALETTE)


# ── Tiny helpers ─────────────────────────────────────────────────────────


def _source_pills(sources: list[str]) -> str:
    """Render server keys as a single faint line: 'LD · AX · LM'.

    Replaces the old `[bg-on-fg] LD [/]` colored badge blocks. Same info,
    tenth the visual weight.
    """
    accent_alt = PALETTE["accent_alt"]
    ghost = PALETTE["text_ghost"]
    parts = [f"[{accent_alt}]{s.upper()}[/]" for s in sources]
    return f" [{ghost}]·[/] ".join(parts)


# ── Screens ──────────────────────────────────────────────────────────────


class SearchScreen(Screen):
    """Search screen with static banner + live per-source progress."""

    BINDINGS = [
        Binding("escape", "quit", "Quit", show=True),
        Binding("c", "resume_recent", "Continue", show=True),
        Binding("b", "show_bookmarks", "Bookmarks", show=True),
    ]

    EMPTY_HINT = (
        f"[{PALETTE['text_faint']}]Type a title and press Enter "
        f"— try 'Battle Through the Heavens'.  "
        f"Press [bold {PALETTE['accent']}]C[/] to resume, "
        f"[bold {PALETTE['accent']}]B[/] for bookmarks.[/]"
    )

    HELP_BAR = (
        f"[bold {PALETTE['accent']}]Enter[/] [{PALETTE['text_faint']}]search[/]  "
        f"[{PALETTE['border']}]│[/]  "
        f"[bold {PALETTE['accent']}]C[/] [{PALETTE['text_faint']}]continue[/]  "
        f"[{PALETTE['border']}]│[/]  "
        f"[bold {PALETTE['accent']}]B[/] [{PALETTE['text_faint']}]bookmarks[/]  "
        f"[{PALETTE['border']}]│[/]  "
        f"[bold {PALETTE['accent']}]Q[/] [{PALETTE['text_faint']}]quit[/]"
    )

    def __init__(self, app_core) -> None:
        super().__init__()
        self._core = app_core
        self._results: list[Series] = []

    def compose(self) -> ComposeResult:
        yield StaticBanner(id="static-banner")
        yield Rule(line_style="heavy")
        with Container(id="search-box"):
            yield Input(placeholder="  Search for donghua…", id="search-input")
        yield Static("", id="continue-strip")
        yield Static("", id="status-bar")
        with Container(id="results-container"):
            yield OptionList(id="results-list")
            yield Static(self.EMPTY_HINT, id="empty-hint")
        yield Static(self.HELP_BAR, id="help-text")

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()
        self._refresh_continue_strip()

    def _refresh_continue_strip(self) -> None:
        from donghua_cli import library

        recent = library.recent_history(limit=3)
        bookmarks = library.list_bookmarks()
        if not recent and not bookmarks:
            return

        accent_alt = PALETTE["accent_alt"]
        accent = PALETTE["accent"]
        muted = PALETTE["text_muted"]
        text = PALETTE["text"]
        faint = PALETTE["text_faint"]
        border = PALETTE["border"]

        parts: list[str] = []
        if recent:
            top = recent[0]
            parts.append(
                f"[{accent_alt}]{GLYPH['pending']}[/] [{muted}]Resume[/] "
                f"[bold {text}]{top.title[:32]}[/] "
                f"[{faint}]ep {top.last_episode}[/]"
            )
        if bookmarks:
            parts.append(
                f"[{accent}]{GLYPH['star']}[/] [{muted}]Bookmarks[/] "
                f"[bold {text}]{len(bookmarks)}[/]"
            )
        try:
            self.query_one("#continue-strip", Static).update(
                "  " + f"   [{border}]│[/]   ".join(parts)
            )
        except NoMatches:
            pass

    def _show_library(self, title: str, entries) -> None:
        if not entries:
            self.app.notify(f"No {title.lower()} yet", title=title, timeout=2)
            return

        accent = PALETTE["accent"]
        text = PALETTE["text"]
        faint = PALETTE["text_faint"]

        self._results = [e.to_series() for e in entries]
        options = []
        for i, entry in enumerate(entries):
            label = f"[bold {accent}]{i + 1:2d}[/]  [{text}]{entry.title[:60]}[/]"
            extra = getattr(entry, "last_episode", None)
            if extra:
                label += f"  [{faint}]ep {extra}[/]"
            options.append(Option(label, id=str(i)))
        try:
            status = self.query_one("#status-bar", Static)
            status.update(
                f"  [{PALETTE['accent_alt']}]{GLYPH['ok']}[/] "
                f"[bold]{title}[/]  "
                f"[{PALETTE['text_muted']}]{len(entries)} entries[/]"
            )
        except NoMatches:
            pass
        self._populate_results(options)

    def action_resume_recent(self) -> None:
        from donghua_cli import library

        self._show_library("Continue watching", library.recent_history(limit=20))

    def action_show_bookmarks(self) -> None:
        from donghua_cli import library

        self._show_library("Bookmarks", library.list_bookmarks())

    @on(Input.Submitted, "#search-input")
    def on_search(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return
        self._do_search(query)

    @work(thread=True, exclusive=True)
    def _do_search(self, query: str) -> None:
        status = self.query_one("#status-bar", Static)
        results_list = self.query_one("#results-list", OptionList)
        try:
            hint = self.query_one("#empty-hint", Static)
        except NoMatches:
            hint = None

        accent_alt = PALETTE["accent_alt"]
        accent = PALETTE["accent"]
        danger = PALETTE["danger"]
        muted = PALETTE["text_muted"]
        text = PALETTE["text"]
        faint = PALETTE["text_faint"]
        border = PALETTE["border"]

        self.app.call_from_thread(
            status.update,
            f"  [{accent_alt}]{GLYPH['pending']}[/] [{muted}]Searching[/] "
            f"[bold {text}]'{query}'[/]",
        )
        self.app.call_from_thread(results_list.clear_options)
        if hint is not None:
            self.app.call_from_thread(hint.update, "")

        from donghua_cli.scraper import get_search_sources, search_all

        # Per-source progress pills, single-glyph budget.
        progress: dict[str, tuple[str, int, float]] = {
            s.key: ("pending", 0, 0.0) for s in get_search_sources()
        }

        def render_progress() -> str:
            parts = []
            for key, (state, hits, _) in progress.items():
                if state == "pending":
                    icon = f"[{muted}]{GLYPH['pending']}[/]"
                    detail = "…"
                elif state == "alive":
                    icon = f"[{accent_alt}]{GLYPH['ok']}[/]"
                    detail = f"{hits}"
                elif state == "dead":
                    icon = f"[{danger}]{GLYPH['fail']}[/]"
                    detail = "fail"
                else:  # timeout
                    icon = f"[{accent}]{GLYPH['fail']}[/]"
                    detail = "slow"
                parts.append(f"{icon} [{muted}]{key.upper()}[/]·{detail}")
            return "   ".join(parts)

        def on_progress(key: str, state: str, hits: int, elapsed: float) -> None:
            progress[key] = (state, hits, elapsed)
            self.app.call_from_thread(
                status.update,
                f"  [{accent_alt}]{GLYPH['pending']}[/] [{muted}]Searching[/] "
                f"[bold {text}]'{query}'[/]   {render_progress()}",
            )

        results = search_all(query, on_progress=on_progress)
        self._results = results

        if not results:
            self.app.call_from_thread(
                status.update,
                f"  [{danger}]{GLYPH['fail']}[/] [{muted}]No results[/]",
            )
            if hint is not None:
                self.app.call_from_thread(
                    hint.update,
                    f"[{faint}]Nothing matched '[/{faint}]"
                    f"[bold {text}]{query}[/][{faint}]'. "
                    f"Try a different spelling or a partial title.[/]",
                )
            self.app.call_from_thread(
                self.app.notify,
                "No results found",
                title="Search",
                severity="warning",
            )
            return

        multi = sum(1 for s in results if len(s.sources) > 1)
        self.app.call_from_thread(
            status.update,
            f"  [{accent_alt}]{GLYPH['ok']}[/] [bold]{len(results)}[/] "
            f"[{muted}]results[/]  [{border}]│[/]  "
            f"[{accent_alt}]{multi}[/] [{faint}]multi-server[/]",
        )

        from donghua_cli.scraper import _is_movie
        options = []
        for i, s in enumerate(results):
            # Demoted MOVIE/SERIES tag: a quiet faint suffix instead of a
            # high-contrast colored background.
            kind = "movie" if _is_movie(s.title) else None
            kind_suffix = f"  [{faint} italic]· {kind}[/]" if kind else ""

            srv_count = len(s.sources)
            count_dot = f"[{accent_alt}]●[/]" * srv_count + f"[{border}]●[/]" * max(0, 5 - srv_count)

            label = (
                f"[bold {accent}]{i + 1:2d}[/]  "
                f"[{text}]{s.title[:48]}[/]"
                f"{kind_suffix}  "
                f"{count_dot}"
            )
            options.append(Option(label, id=str(i)))

        self.app.call_from_thread(self._populate_results, options)
        self.app.call_from_thread(
            self.app.notify,
            f"{len(results)} result(s) found",
            title="Search complete",
            timeout=3,
        )

    def _populate_results(self, options: list[Option]) -> None:
        rl = self.query_one("#results-list", OptionList)
        rl.clear_options()
        for opt in options:
            rl.add_option(opt)
        try:
            self.query_one("#empty-hint", Static).update("")
        except NoMatches:
            pass
        rl.focus()

    @on(OptionList.OptionSelected, "#results-list")
    def on_select(self, event: OptionList.OptionSelected) -> None:
        if event.option_id is None:
            return
        idx = int(event.option_id)
        if 0 <= idx < len(self._results):
            self.app.push_screen(EpisodeScreen(self._core, self._results[idx]))

    def action_quit(self) -> None:
        self.app.exit()


class EpisodeScreen(Screen):
    """Episode selection. Single accent (gold = your next pick)."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("a", "select_all", "Play All", show=True),
        Binding("enter", "confirm", "Play", show=True),
        Binding("b", "toggle_bookmark", "Bookmark", show=True),
    ]

    HELP_BAR = (
        f"[bold {PALETTE['accent']}]Enter[/] [{PALETTE['text_faint']}]play[/]  "
        f"[{PALETTE['border']}]│[/]  "
        f"[bold {PALETTE['accent']}]A[/] [{PALETTE['text_faint']}]play all[/]  "
        f"[{PALETTE['border']}]│[/]  "
        f"[bold {PALETTE['accent']}]B[/] [{PALETTE['text_faint']}]bookmark[/]  "
        f"[{PALETTE['border']}]│[/]  "
        f"[bold {PALETTE['accent']}]Esc[/] [{PALETTE['text_faint']}]back[/]"
    )

    def __init__(self, app_core, series: Series) -> None:
        super().__init__()
        self._core = app_core
        self._series = series
        self._episodes: list[Episode] = []

    def compose(self) -> ComposeResult:
        accent = PALETTE["accent"]
        header = (
            f"[bold {accent}]{self._series.title}[/]\n"
            f"{_source_pills(list(self._series.sources))}"
        )
        yield Static(header, id="episode-header")
        yield Static("", id="series-cover")
        yield Static("", id="status-bar")
        with Container(id="results-container"):
            yield OptionList(id="episode-list")
            yield Static(
                f"[{PALETTE['text_faint']}]Loading episodes — Esc to go back.[/]",
                id="empty-hint",
            )
        yield Static(self.HELP_BAR, id="help-text")

    def on_mount(self) -> None:
        self._fetch_worker = self._load_episodes()
        if self._series.cover_url:
            self._load_cover(self._series.cover_url)

    @work(thread=True)
    def _load_cover(self, url: str) -> None:
        """Render the series cover into #series-cover when rich-pixels is
        available. Quietly does nothing if the optional `covers` extra
        isn't installed or the fetch fails.
        """
        try:
            from io import BytesIO

            import httpx
            from PIL import Image as PILImage
            from rich_pixels import Pixels
        except ImportError:
            return

        try:
            resp = httpx.get(url, timeout=5, follow_redirects=True)
            if resp.status_code != 200 or not resp.content:
                return
            img = PILImage.open(BytesIO(resp.content))
            img.thumbnail((28, 14))
            pixels = Pixels.from_image(img)
        except Exception:
            return

        self.app.call_from_thread(self._safe_update_cover, pixels)

    def _safe_update_cover(self, pixels) -> None:
        try:
            self.query_one("#series-cover", Static).update(pixels)
        except NoMatches:
            pass

    def action_go_back(self) -> None:
        # Cancel an in-flight fetch before leaving the screen so the worker
        # thread doesn't keep talking to dead UI widgets.
        worker = getattr(self, "_fetch_worker", None)
        if worker is not None and worker.is_running:
            worker.cancel()
        self.app.pop_screen()

    @work(thread=True, exclusive=True)
    def _load_episodes(self) -> None:
        status = self.query_one("#status-bar", Static)
        try:
            hint = self.query_one("#empty-hint", Static)
        except NoMatches:
            hint = None

        accent_alt = PALETTE["accent_alt"]
        accent = PALETTE["accent"]
        danger = PALETTE["danger"]
        muted = PALETTE["text_muted"]
        faint = PALETTE["text_faint"]
        border = PALETTE["border"]

        self.app.call_from_thread(
            status.update,
            f"  [{accent_alt}]{GLYPH['pending']}[/] [{muted}]Loading episodes…[/]",
        )

        from donghua_cli.scraper import get_episodes
        episodes = get_episodes(self._series)
        self._episodes = episodes

        if not episodes:
            self.app.call_from_thread(
                status.update,
                f"  [{danger}]{GLYPH['fail']}[/] [{muted}]No episodes[/]",
            )
            if hint is not None:
                self.app.call_from_thread(
                    hint.update,
                    f"[{faint}]Source returned no episodes. "
                    f"Press [bold {accent}]Esc[/] to go back and try another result.[/]",
                )
            self.app.call_from_thread(
                self.app.notify,
                "No episodes found",
                title="Episodes",
                severity="warning",
            )
            return

        if hint is not None:
            self.app.call_from_thread(hint.update, "")

        multi = sum(1 for e in episodes if len(e.sources) > 1)
        self.app.call_from_thread(
            status.update,
            f"  [{accent_alt}]{GLYPH['ok']}[/] [bold]{len(episodes)}[/] "
            f"[{muted}]episodes[/]  [{border}]│[/]  "
            f"[{accent_alt}]{multi}[/] [{faint}]multi-server[/]",
        )

        options = []
        for i, ep in enumerate(episodes):
            num = ep.number if ep.number < 999999 else i + 1
            srv_count = len(ep.sources)
            count_dot = f"[{accent_alt}]●[/]" * srv_count + f"[{border}]●[/]" * max(0, 5 - srv_count)
            # Single number per row — drop the redundant list index that
            # mirrored the episode number on most plugins.
            label = (
                f"[bold {accent}]EP {num:<4}[/]  "
                f"{count_dot}"
            )
            options.append(Option(label, id=str(i)))

        self.app.call_from_thread(self._populate, options)
        self.app.call_from_thread(
            self.app.notify,
            f"{len(episodes)} episodes loaded",
            title="Ready",
            timeout=2,
        )

    def _populate(self, options: list[Option]) -> None:
        el = self.query_one("#episode-list", OptionList)
        el.clear_options()
        for opt in options:
            el.add_option(opt)
        el.focus()

    @on(OptionList.OptionSelected, "#episode-list")
    def on_select(self, event: OptionList.OptionSelected) -> None:
        if event.option_id is None:
            return
        idx = int(event.option_id)
        if 0 <= idx < len(self._episodes):
            self.app.push_screen(
                PlaybackScreen(self._core, self._episodes[idx:], self._series)
            )

    def action_select_all(self) -> None:
        if self._episodes:
            self.app.push_screen(
                PlaybackScreen(self._core, self._episodes, self._series)
            )

    def action_confirm(self) -> None:
        el = self.query_one("#episode-list", OptionList)
        if el.highlighted is not None and self._episodes:
            self.app.push_screen(
                PlaybackScreen(self._core, self._episodes[el.highlighted:], self._series)
            )

    def action_toggle_bookmark(self) -> None:
        from donghua_cli import library

        bookmarked = library.toggle_bookmark(self._series)
        if bookmarked:
            self.app.notify(
                f"Bookmarked: {self._series.title}",
                title=f"{GLYPH['star']} Saved",
                timeout=3,
            )
        else:
            self.app.notify(
                f"Removed: {self._series.title}",
                title="Bookmark",
                timeout=3,
            )


class PlaybackScreen(Screen):
    """Now-playing screen. Three blocks: title, progress, controls."""

    BINDINGS = [
        Binding("n", "next_ep", "Next", show=True),
        Binding("p", "prev_ep", "Prev", show=True),
        Binding("r", "replay", "Replay", show=True),
        Binding("d", "download", "Download", show=True),
        Binding("q", "quit_playback", "Quit", show=True),
    ]

    current_idx = reactive(0)

    def __init__(
        self,
        app_core,
        episodes: list[Episode],
        series: "Series | str",
    ) -> None:
        super().__init__()
        self._core = app_core
        self._episodes = episodes
        if isinstance(series, str):
            self._series_title = series
            self._series_urls: dict[str, str] = {}
        else:
            self._series_title = series.title
            self._series_urls = dict(series.urls)
        self._stream_url = ""
        self._server_name = ""

    def compose(self) -> ComposeResult:
        with Container(id="np-outer"):
            yield Static("", id="np-title")
            yield Static("", id="np-meta")
            with Container(id="np-progress-box"):
                yield ProgressBar(
                    total=max(len(self._episodes), 1),
                    show_eta=False,
                    show_percentage=False,
                )
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
        # Deterministic level per episode — never reshuffles on refresh.
        level = level_for_episode(num)
        cur = self.current_idx + 1
        total = len(self._episodes)

        accent = PALETTE["accent"]
        accent_alt = PALETTE["accent_alt"]
        text = PALETTE["text"]
        muted = PALETTE["text_muted"]
        faint = PALETTE["text_faint"]
        border = PALETTE["border"]

        self._safe_update(
            "#np-title",
            f"[{accent}]{GLYPH['play']}[/]  [bold {text}]{self._series_title}[/]   "
            f"[{muted}]EP[/] [bold {accent_alt}]{num}[/]",
        )
        self._safe_update(
            "#np-meta",
            f"[italic {faint}]{level}[/]   [{border}]·[/]   "
            f"[{muted}]{cur} of {total}[/]   [{border}]·[/]   "
            f"{_source_pills(list(ep.sources))}",
        )

        try:
            self.query_one(ProgressBar).update(total=total, progress=cur)
        except NoMatches:
            pass

        can_n = self.current_idx < len(self._episodes) - 1
        can_p = self.current_idx > 0

        def _k(key: str, label: str, on: bool = True) -> str:
            if on:
                return f"[bold {accent}]{key}[/] [{text}]{label}[/]"
            return f"[{border}]{key}[/] [{faint}]{label}[/]"

        self._safe_update(
            "#controls-panel",
            f"{_k('N', 'Next', can_n)}    {_k('P', 'Prev', can_p)}    "
            f"{_k('R', 'Replay')}    {_k('D', 'Download')}    {_k('Q', 'Quit')}",
        )

    def _safe_update(self, selector: str, content: str) -> None:
        try:
            self.query_one(selector, Static).update(content)
        except NoMatches:
            pass

    @work(thread=True)
    def _play_current(self) -> None:
        accent_alt = PALETTE["accent_alt"]
        danger = PALETTE["danger"]
        muted = PALETTE["text_muted"]

        if self.current_idx >= len(self._episodes):
            self.app.call_from_thread(
                self._safe_update,
                "#status-bar",
                f"  [{accent_alt}]{GLYPH['ok']}[/] [bold]All episodes complete[/]",
            )
            self.app.call_from_thread(
                self.app.notify, "All episodes played", title="Complete",
            )
            return

        ep = self._episodes[self.current_idx]
        self.app.call_from_thread(
            self._safe_update,
            "#status-bar",
            f"  [{accent_alt}]{GLYPH['pending']}[/] [{muted}]Resolving stream…[/]",
        )

        from donghua_cli.extractor import extract_with_fallback
        from donghua_cli.sources import get_source

        stream_url, source_key = extract_with_fallback(ep)
        self._stream_url = stream_url
        source = get_source(source_key)
        self._server_name = source.name if source else source_key.upper()

        self.app.call_from_thread(self._update_display)

        from donghua_cli import config as _config, library
        from donghua_cli.player import Player
        from donghua_cli.sources.base import Series

        player = Player(self._core._quality)
        title = f"{self._series_title} - Episode {ep.number}"

        if player.play(stream_url, title=title):
            self.app.call_from_thread(
                self._safe_update,
                "#status-bar",
                f"  [{accent_alt}]{GLYPH['ok']}[/] Playing via [bold]{self._server_name}[/]",
            )
            self.app.call_from_thread(
                self.app.notify,
                f"Playing via {self._server_name}",
                title=f"{GLYPH['play']} Episode {ep.number}",
                timeout=3,
            )

            ep_num = ep.number if ep.number < 999999 else self.current_idx + 1
            library.record_watch(
                Series(
                    title=self._series_title,
                    urls=getattr(self, "_series_urls", {}) or {},
                ),
                ep_num,
            )

            # Auto-advance when the current player finishes, if enabled and
            # there's a next episode queued. Guard against an immediate exit
            # (extraction returned a bad URL → mpv dies in <1s) — without
            # this check the TUI cascades through every episode in seconds.
            if _config.get_auto_next() and self.current_idx < len(self._episodes) - 1:
                import time as _time
                started_playback = _time.time()
                player.wait_for_end()
                elapsed = _time.time() - started_playback
                if elapsed < 30:
                    self.app.call_from_thread(
                        self._safe_update,
                        "#status-bar",
                        f"  [{danger}]{GLYPH['fail']}[/] Playback failed in "
                        f"{elapsed:.1f}s — auto-next disabled",
                    )
                    self.app.call_from_thread(
                        self.app.notify,
                        f"mpv exited after {elapsed:.1f}s. Check the URL "
                        f"or try Replay (R).",
                        title="Playback failed",
                        severity="error",
                        timeout=6,
                    )
                else:
                    self.app.call_from_thread(self._advance_after_playback)
        else:
            self.app.call_from_thread(
                self._safe_update,
                "#status-bar",
                f"  [{danger}]{GLYPH['fail']}[/] No player found",
            )
            self.app.call_from_thread(
                self.app.notify,
                f"Install mpv or vlc.\nURL: {stream_url[:50]}",
                title="No Player",
                severity="error",
            )

    def _advance_after_playback(self) -> None:
        if self.current_idx < len(self._episodes) - 1:
            self.current_idx += 1
            self._play_current()

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
        self._safe_update(
            "#status-bar",
            f"  [{PALETTE['accent_alt']}]{GLYPH['pending']}[/] Downloading…",
        )
        self.app.notify("Download started…", title="Download", timeout=2)
        self._download_in_background()

    @work(thread=True)
    def _download_in_background(self) -> None:
        accent_alt = PALETTE["accent_alt"]
        danger = PALETTE["danger"]

        ep = self._episodes[self.current_idx]
        stream_url = self._stream_url or ""

        from donghua_cli.player import Downloader

        ok = Downloader.download(
            stream_url, self._series_title, ep.title, self._core._quality
        )
        if ok:
            self.app.call_from_thread(
                self._safe_update,
                "#status-bar",
                f"  [{accent_alt}]{GLYPH['ok']}[/] Download complete",
            )
            self.app.call_from_thread(
                self.app.notify, "Saved", title=f"{GLYPH['ok']} Downloaded"
            )
        else:
            self.app.call_from_thread(
                self._safe_update,
                "#status-bar",
                f"  [{danger}]{GLYPH['fail']}[/] Download failed",
            )
            self.app.call_from_thread(
                self.app.notify, "Failed", title="Error", severity="error"
            )

    def action_quit_playback(self) -> None:
        self.app.pop_screen()


# ── Main App ─────────────────────────────────────────────────────────────


class DonghuaTUI(App):
    TITLE = "Donghua CLI"
    SUB_TITLE = "武侠动画终端"
    CSS = WUXIA_CSS

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        # `q` is NOT priority=True any more — that would swallow a `q` typed
        # into the search input. Each screen handles its own Q semantics.
    ]

    def __init__(self, app_core) -> None:
        super().__init__()
        self._core = app_core

    def on_mount(self) -> None:
        self.push_screen(SearchScreen(self._core))
