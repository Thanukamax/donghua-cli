# Future Ideas -- Donghua CLI v3

Captured during the v3 revamp. Review and implement as priorities allow.

---

## UI / UX

- [ ] **Textual full-screen TUI** -- upgrade from Rich console output to a proper Textual app with mouse support, real-time search-as-you-type, scrollable episode lists, and keyboard arrow navigation. Rich is the foundation; Textual is the next level.
- [ ] **Fuzzy search** -- use `thefuzz` or `rapidfuzz` to match partial/typo'd series names locally against recent results.
- [ ] **Watch history** -- track what you've watched (episode + timestamp) in a local SQLite/JSON file, show "Continue watching" on launch.
- [ ] **Bookmarks / favorites** -- save series to a local favorites list for quick access without re-searching.
- [ ] **Terminal image preview** -- use `chafa.py` or `kitty` protocol to show series cover art in the terminal (H-CLI already does this).

## Performance

- [x] **Async HTTP** -- replaced `requests` with `httpx`. Concurrent search across both sources via `asyncio.gather`. Connection pooling via shared client.
- [x] **Smarter preloading** -- adaptive preloader tracks navigation deltas. Sequential watchers get 3-5 episodes ahead; jumpy users get reduced to 1.
- [x] **HTML partial parse** -- replaced BeautifulSoup with `selectolax` (lexbor-based, 5-10x faster). `fetch_partial()` streams first 8KB for regex pre-scan.

## Sources

- [x] **Source plugin system** -- each source is its own module in `src/donghua_cli/sources/`. Adding a new site = one file + register in `__init__.py`.
- [x] **More sources** -- added MisterDonghua, H-Donghua, LMAnime (5 total). All share AnimeStream WordPress theme selectors.
- [ ] **Even more sources** -- candidates researched:
  - LuciferDonghua.org (mirror, no `/anime/` prefix -- easy, same theme)
  - ChineseAnime.in (AnimeStream theme, simpler episode HTML)
  - MyDonghua.com (AJAX search + non-standard `/watch/slug.html/N` -- medium effort)
  - Blogger-based: DonghuaZone, 4KDonghua (different platform entirely -- low priority)
  - Cloudflare-blocked: DonghuaStream.org, DonghuaWorld, AnimeCube (need cloudscraper -- low priority)
  - Bilibili (geo handling needed), MyAnimeList (metadata only)
- [ ] **Source health checking** -- on startup, quick ping each source and mark dead ones so users aren't waiting for timeouts.

## Packaging / Distribution

- [x] **PyPI publish** -- GitHub Actions workflow publishes to PyPI on `v*` tag. `pipx install donghua-cli` will work once first release is tagged.
- [x] **Homebrew formula** -- formula at `packaging/homebrew/donghua-cli.rb`. Needs sha256 update per release.
- [x] **AUR package** -- PKGBUILD at `packaging/aur/PKGBUILD`. Needs sha256 update per release.
- [ ] **Flatpak / AppImage** -- bundle MPV + Python for zero-dep install on Linux. (Deprioritized: CLI + mpv makes this awkward.)
- [x] **Single binary** -- PyInstaller spec at `packaging/pyinstaller/donghua.spec`. CI builds Windows `.exe` on release.

## Developer Experience

- [x] **Tests** -- 43 unit tests covering utils, scraper logic (normalization, matching, merging), extraction patterns, and source data structures.
- [x] **CI pipeline** -- GitHub Actions: lint (ruff) + typecheck (pyright) + tests on push/PR across Python 3.9-3.13.
- [x] **CHANGELOG.md** -- tracking changes from v2.0 -> v3.0.
- [x] **Config file** -- `~/.config/donghua-cli/config.toml` for persistent preferences (quality, download dir). Loaded via tomllib/tomli.

## Platform

- [ ] **Termux-specific enhancements** -- notification on episode download complete, background playback support.
- [ ] **Windows Terminal integration** -- detect WT and use its richer capabilities (e.g., proper Unicode, wider color palette).
- [ ] **MPV IPC** -- control MPV via JSON IPC socket instead of just launching it. This enables: pause/resume from CLI, progress tracking, auto-next when episode ends.
