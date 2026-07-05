"""Main application logic.

Wires together sources, extractor (with server fallback), player, cache, and UI.
The user never picks a source -- search is global, sources become servers.
"""

import threading
import time
from typing import List

from donghua_cli import config, theme, ui
from donghua_cli.cache import Preloader, StreamCache
from donghua_cli.extractor import extract_with_fallback
from donghua_cli.player import Downloader, Player
from donghua_cli.scraper import get_episodes, search_all, _is_movie
from donghua_cli.sources import ALL_SOURCES, get_source
from donghua_cli.sources.base import Episode, Series

console = theme.console


class DonghuaCLI:
    def __init__(self, quality: str | None = None):
        config.ensure_dirs()
        self._cache = StreamCache()
        self._preloader = Preloader(self._cache)
        self._player: Player | None = None
        self._quality = quality or config.get_quality()

    # ── public entry points ──────────────────────────────────────────────

    def run_interactive(self) -> None:
        """Fully interactive loop: search -> select -> play/download -> repeat."""
        try:
            while True:
                ui.show_banner()

                query = ui.get_search_query()
                if not query:
                    theme.status("warning", "Please enter a search term")
                    time.sleep(1)
                    continue

                series_list = self._search(query)
                if not series_list:
                    console.print(theme.tip_box("No Results", "Try a different search term", "gold"))
                    time.sleep(3)
                    continue

                series = self._pick_series(series_list)
                episodes = self._get_episodes(series)
                if not episodes:
                    console.print(theme.tip_box("No Episodes", "This series has no episodes yet", "gold"))
                    time.sleep(3)
                    continue

                selected = ui.select_episodes_from_list(episodes)
                method = ui.choose_method()

                if method == "download":
                    self._download_episodes(selected, series.title)
                else:
                    self._play_episodes(selected, series.title)

                if not ui.ask_continue():
                    theme.farewell()
                    break

        except KeyboardInterrupt:
            self._cleanup()
            theme.divider()
            theme.status("info", "Cultivation session interrupted")
            theme.status("success", "May your journey be eternal")

    def run_direct(self, query: str, download: bool = False) -> None:
        """CLI mode with arguments."""
        ui.show_banner()

        series_list = self._search(query)
        if not series_list:
            console.print(theme.tip_box("No Results", "Try a different search term", "gold"))
            return

        series = self._pick_series(series_list)
        episodes = self._get_episodes(series)
        if not episodes:
            console.print(theme.tip_box("No Episodes", "This series has no episodes yet", "gold"))
            return

        selected = ui.select_episodes_from_list(episodes)

        if download:
            self._download_episodes(selected, series.title)
        else:
            self._play_episodes(selected, series.title)

    def clear_cache(self) -> None:
        ui.show_banner()
        theme.status("loading", "Clearing stream cache...")
        if self._cache.clear():
            theme.status("success", "Cache cleared")
        else:
            theme.status("info", "No cache to clear")

    def show_features(self) -> None:
        ui.show_banner()
        theme.section_header("Core Abilities", "Features & Capabilities", "Everything you need to stream Donghua")
        theme.feature_cards()
        console.print()
        source_names = ", ".join(s.name for s in ALL_SOURCES)
        console.print(f"  [steel]Active servers:[/] [gold]{source_names}[/]")
        console.print()
        console.print(theme.tip_box("Quick Start", "Run 'dhua' for interactive mode or 'dhua --help' for all options"))
        console.print()

    # ── internal ─────────────────────────────────────────────────────────

    def _search(self, query: str) -> List[Series]:
        theme.divider()
        from donghua_cli import health
        search_sources = [
            s for s in ALL_SOURCES if s.enabled and health.is_healthy(s.key)
        ]
        source_names = " + ".join(s.name for s in search_sources)

        from rich.live import Live
        from rich.spinner import Spinner

        with Live(
            Spinner("dots", text=f"[gold]Searching '{query}' across {source_names}...[/]"),
            console=console,
            transient=True,
        ):
            results = search_all(query)

        if results:
            theme.status("success", f"Found {len(results)} result(s)")
            # Show how many sources each result is on
            multi = sum(1 for s in results if len(s.sources) > 1)
            if multi:
                theme.status("info", f"{multi} available on multiple servers")
        else:
            theme.status("error", "No results found")
        return results

    def _pick_series(self, series_list: List[Series]) -> Series:
        """Let user pick a series from unified results."""
        # Build display list with server badges and movie/series type tags
        display_items: list[tuple[str, str]] = []
        for s in series_list:
            type_tag = "[MOVIE]" if _is_movie(s.title) else "[SERIES]"
            badges = " ".join(f"[{k.upper()}]" for k in s.sources)
            display_items.append((s.title, f"{type_tag} {badges}"))

        idx = ui.select_from_list_with_badges(display_items, "CULTIVATION MANUALS")
        return series_list[idx]

    def _get_episodes(self, series: Series) -> List[Episode]:
        theme.divider()

        from rich.live import Live
        from rich.spinner import Spinner

        with Live(
            Spinner("dots", text="[gold]Fetching episodes from all servers...[/]"),
            console=console,
            transient=True,
        ):
            episodes = get_episodes(series)

        if episodes:
            multi = sum(1 for e in episodes if len(e.sources) > 1)
            theme.status("success", f"Found {len(episodes)} episode(s)")
            if multi:
                theme.status("info", f"{multi} episodes have multiple servers (auto-fallback enabled)")
        else:
            theme.status("warning", "No episodes found")
        return episodes

    def _play_episodes(self, episodes: List[Episode], series_title: str) -> None:
        self._player = Player(self._quality)
        theme.divider()
        theme.status("loading", "Preparing playback...")

        idx = 0
        while idx < len(episodes):
            ep = episodes[idx]

            ui.clear_screen()
            ui.show_banner()

            # Resolve stream with automatic server fallback
            from rich.live import Live
            from rich.spinner import Spinner

            with Live(
                Spinner("dots", text="[gold]Resolving stream...[/]"),
                console=console,
                transient=True,
            ):
                stream_url, source_key = self._preloader.get_stream(ep, extract_with_fallback)
            source = get_source(source_key)
            server_name = source.name if source else source_key.upper()

            # Start preloading next episodes
            self._preloader.preload(episodes, idx, extract_with_fallback)

            ui.show_playback(ep.title, idx + 1, len(episodes), server_name, ep.sources)

            if not self._player.play(stream_url, title=f"{series_title} - {ep.title}"):
                theme.status("error", "No player found -- run 'donghua doctor' to fix (installs mpv)")
                console.print(f"  [steel]Stream URL:[/] {stream_url}")
                return

            theme.status("success", f"Player launched! Server: {server_name}")

            # Monitor player in background
            finished = threading.Event()

            def _monitor():
                while self._player and self._player.is_playing():
                    time.sleep(0.5)
                finished.set()
                theme.status("success", "Episode finished! Press Enter or type a command.")

            threading.Thread(target=_monitor, daemon=True).start()

            # Command loop
            action = None
            while action is None:
                try:
                    cmd = console.input(theme.prompt_text("Command [N/P/S/R/D/Q]")).strip().lower()
                except KeyboardInterrupt:
                    self._player.stop()
                    theme.divider()
                    theme.status("info", "Session ended")
                    return

                if cmd in ("n", ""):
                    if idx < len(episodes) - 1:
                        action = "next"
                    elif finished.is_set():
                        action = "done"
                    else:
                        theme.status("warning", "Already at last episode")
                elif cmd == "p":
                    if idx > 0:
                        action = "prev"
                    else:
                        theme.status("warning", "Already at first episode")
                elif cmd == "r":
                    action = "replay"
                elif cmd == "s":
                    try:
                        n = int(console.input(theme.prompt_text(f"Skip to [1-{len(episodes)}]")).strip())
                        if 1 <= n <= len(episodes):
                            action = ("skip", n - 1)
                        else:
                            theme.status("error", f"Out of range (1-{len(episodes)})")
                    except (ValueError, KeyboardInterrupt):
                        pass
                elif cmd == "d":
                    theme.status("loading", "Downloading...")
                    Downloader.download(stream_url, series_title, ep.title, self._quality)
                elif cmd == "q":
                    action = "quit"
                else:
                    console.print("  [steel]Commands:[/] [light.gold]\\[N]ext \\[P]rev \\[S]kip \\[R]eplay \\[D]ownload \\[Q]uit[/]")

            self._player.stop()

            old_idx = idx
            if action == "next":
                idx += 1
            elif action == "prev":
                idx -= 1
            elif action == "replay":
                pass
            elif action == "quit":
                break
            elif action == "done":
                idx += 1
            elif isinstance(action, tuple) and action[0] == "skip":
                idx = action[1]

            if action != "quit":
                self._preloader.record_navigation(old_idx, idx)

        theme.divider()
        theme.status("success", "All techniques mastered!")

    def _download_episodes(self, episodes: List[Episode], series_title: str) -> None:
        theme.divider()
        theme.section_header(
            "Archive Mode",
            "Downloading Episodes",
            f"Saving {len(episodes)} episode(s) to {config.get_download_dir()}",
        )

        ok = 0
        fail = 0

        for i, ep in enumerate(episodes, 1):
            display_num = ep.number if ep.number < 999999 else i
            console.print(f"\n  [gold]\\[{i:03d}/{len(episodes):03d}][/] Episode {display_num:03d} -- [white]{ep.title[:55]}[/]")

            stream_url, source_key = self._preloader.get_stream(ep, extract_with_fallback)
            source = get_source(source_key)
            theme.status("loading", f"Downloading from {source.name if source else source_key}...")

            if Downloader.download(stream_url, series_title, ep.title, self._quality):
                theme.status("success", "Done")
                ok += 1
            else:
                theme.status("error", "Failed")
                fail += 1

        theme.divider()
        theme.status("success", f"{ok}/{len(episodes)} episodes downloaded")
        if fail:
            theme.status("error", f"{fail} failed")
        theme.status("info", f"Saved to: {config.get_download_dir()}")

    def _cleanup(self) -> None:
        self._preloader.stop()
        if self._player:
            self._player.stop()
