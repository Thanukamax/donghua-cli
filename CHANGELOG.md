# Changelog

All notable changes to Donghua CLI will be documented in this file.

## [3.2.1] - 2026-06-22

### Fixed
- **mpv process leak on auto-next.** The TUI kept no handle on the running player, so Next / Replay / auto-next launched a fresh mpv without stopping the previous one — leaking processes, audio, and IPC sockets, and stranding `wait_for_end` threads. The playback screen now holds the active player, stops it before each new playback, tears it down on screen exit, and uses a per-playback generation tag so a superseded worker never fires auto-next. `wait_for_end` binds the process locally so a concurrent `stop()` can't crash its poll loop.
- **`geo.dailymotion.com` embeds played as HTML and died in <1s.** Canonicalization only handled the legacy `/embed/video/<id>` path; modern aggregators hand over `geo.dailymotion.com/player/<pid>.html?video=<id>` (id in a query param, no `/video/` in the path). Every embed/geo/player form now collapses to the canonical `https://www.dailymotion.com/video/<id>`.

## [3.2.0] - 2026-05-21

### Added
- **Watch history + Continue watching** — every play is recorded to `~/.config/donghua-cli/library.json`. Press `C` on the search screen to jump back into the most-recent series; the inline "continue strip" shows the last title and resume episode at a glance.
- **Bookmarks** — press `B` on a series to star it; press `B` on the search screen to browse the bookmark list. Stored next to history in the same JSON file.
- **MPV auto-next-episode** — MPV is now launched with `--input-ipc-server`; when an episode finishes the TUI auto-advances. Disable with `auto_next = false` in `config.toml`.
- **Per-source progress pills** during search — the status bar updates as each source returns (⟳ pending → ✓ N hits / ✗ fail / ⌛ slow) so users can see md/hd/lm land late instead of staring at an opaque spinner.
- **Source-health benching** — repeated failures bench a source for an hour, persisted at `~/.cache/donghua/source_health.json`. Skipped sources don't waste search time.
- **Series cover thumbnails** (opt-in) — install `donghua-cli[covers]` for rich-pixels + Pillow and the EpisodeScreen renders the series poster.
- **Cross-platform download directory** — Windows `%USERPROFILE%\Videos\Donghua`, macOS `~/Movies/Donghua`, Termux uses `~/storage/movies` when shared storage is set up.
- **`disabled_sources` config knob** so users can silence a plugin without uninstalling.
- **library tests** — 4 new test cases covering history + bookmark round-trips.

### Fixed
- **MisterDonghua, H-Donghua, LMAnime now actually return results.** Previous releases hard-skipped them from search because the global deadline was 5s and these sites need 5–13s to respond. Each source now declares its own `search_timeout` and the global deadline scales accordingly.
- **`cache.py` exception clause** — a malformed nested tuple silently swallowed every error path; corrected to catch the right types so stream-cache loading no longer turns errors into "no cache".
- **TUI download no longer freezes the event loop** — `Downloader.download` now runs in a worker thread.
- **`EpisodeScreen.action_go_back` cancels the in-flight fetch worker** before popping the screen, instead of letting the thread keep writing to dead widgets.
- All 36 pyright errors and 5 ruff F401 errors cleaned up; both are now green.

### Changed
- **Source plugins collapsed from ~80 lines each to ~10.** The base `Source` class now templates `search()`, `get_episodes()`, and `dedup_episodes()`; plugins only declare selectors and an optional `_is_series_link` override. Backwards-compatible: third-party plugins overriding the old methods still work.
- **`scraper.search_all` gains an optional `on_progress` callback** for streaming UI updates without breaking the synchronous return contract.
- **Q now quits the app from any screen** (Ctrl+C still works, hidden from the footer).
- `PlaybackScreen` constructor accepts a `Series` (not just a title string) so history entries carry source URLs for resume.
- Banner badge bumped to v3.2.

## [3.1.0] - 2026-04-10

### Added
- **Movie support** -- movies now show up in search results and episode lists. Fixed keyword filter that rejected movie parts (PT-01, Part 01) across all 5 source plugins.
- **Movie/Series type tags** -- search results display `[MOVIE]` or `[SERIES]` badges so movies and series are visually distinct.
- **Desktop shortcuts** -- Linux `.desktop` file, Windows `.bat` launcher, and macOS app shortcut for quick access.
- **Updated installers** -- `install.sh` and `install.ps1` rewritten for v3 modular `pip install` workflow with quality aliases.

### Fixed
- Episode number extraction now handles `PT-XX` and `Part XX` formats used by movie pages.
- All 5 source plugins (LuciferDonghua, AnimeXin, MisterDonghua, H-Donghua, LMAnime) now accept movie part keywords.

### Changed
- Homebrew formula and AUR PKGBUILD updated to 3.1.0.
- PyInstaller spec updated with all current modules.
- CI publish workflow updated for cleaner release flow.

## [3.0.0] - 2026-04-10

### Added
- **Source plugin system** -- each source is its own module. Adding a new site = one file.
- **Unified global search** -- searches all sources concurrently, merges results by fuzzy title match. No more picking a source upfront.
- **Automatic server fallback** -- when stream extraction fails on one source, silently tries the next. Episodes show which servers they're available on.
- **Rich terminal UI** -- replaced ~300 lines of raw ANSI codes with Rich panels, tables, and styled output. Wuxia theme preserved.
- **httpx + selectolax** -- replaced requests + BeautifulSoup for ~5-10x faster HTTP and HTML parsing. Connection pooling via shared client.
- **Adaptive preloader** -- tracks navigation patterns. Sequential watchers get 3-5 episodes preloaded ahead; jumpy users get reduced lookahead.
- **Concurrent async search** -- `asyncio.gather` searches all sources in parallel.
- **Episode multi-source merging** -- episodes matched by number across sources, each storing URLs from every available server.
- **pyproject.toml** -- proper Python packaging with hatchling. Installable via `pipx install donghua-cli`.
- **Dual entry points** -- both `donghua` and `dhua` commands registered.
- **Unit tests** -- 43 tests covering utils, scraper logic, extraction patterns, and data structures.
- **CI/CD** -- GitHub Actions for lint/test on push, PyPI publish on tag, Windows exe on release.
- **Packaging** -- Homebrew formula, AUR PKGBUILD, PyInstaller spec for Windows binary.
- **Config file support** -- `~/.config/donghua-cli/config.toml` for persistent preferences.
- **CHANGELOG.md** -- you're reading it.

### Changed
- **Modular architecture** -- 2 monolithic scripts (1550 + 500 lines) replaced by 12 focused modules in `src/donghua_cli/`.
- **No more source selection** -- sources are now "servers" that work automatically behind the scenes.
- **Merged Termux support** -- Android/Termux is auto-detected (no separate script needed).
- **Dependencies** -- `requests` -> `httpx`, `beautifulsoup4` -> `selectolax`, added `rich`.
- **Cache format** -- now stores (stream_url, source_key) pairs. Backward-compatible with old format.

### Removed
- `dhua.py` and `donghua.py` monolithic scripts (preserved in git history).
- `--source` / `-s` CLI flag (sources are automatic now).
- Manual ANSI escape code theme system.

## [2.0.0] - 2025

- Initial public release with dual-script architecture.
- LuciferDonghua + AnimeXin sources.
- Wuxia-themed terminal UI with ANSI codes.
- LRU cache, background preloading, yt-dlp fallback.
