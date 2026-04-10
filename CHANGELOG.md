# Changelog

All notable changes to Donghua CLI will be documented in this file.

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
