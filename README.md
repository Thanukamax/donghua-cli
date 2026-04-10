# Donghua CLI

A fast, Wuxia-themed terminal client for streaming and downloading Chinese animation (Donghua). Searches multiple sources simultaneously, auto-selects the best server, and plays via MPV/VLC.

[![PyPI](https://img.shields.io/pypi/v/donghua-cli)](https://pypi.org/project/donghua-cli/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Install

```bash
pip install donghua-cli
```

That's it. Works on **Linux**, **macOS**, **Windows**, and **Android (Termux)**.

You also need a video player:

| OS | Install player |
|----|---------------|
| Ubuntu/Debian | `sudo apt install mpv` |
| Fedora | `sudo dnf install mpv` |
| Arch | `sudo pacman -S mpv` |
| macOS | `brew install mpv` |
| Windows | `winget install mpv` |
| Termux | `pkg install mpv` |

> VLC works too, but MPV is recommended.

---

## Usage

```bash
# Launch the full-screen TUI (default)
dhua

# Classic terminal mode
dhua --classic

# Direct search
dhua "Battle Through the Heavens"

# Set quality
dhua "Soul Land" -q 1080

# Download instead of stream
dhua "Perfect World" -d

# Show version
dhua -V
```

### Aliases

The install scripts set up shortcuts:

| Command | What it does |
|---------|-------------|
| `dhua` | Interactive mode |
| `donghua` | Same thing |
| `dhua720` | Stream at 720p |
| `dhua1080` | Stream at 1080p |
| `dhuadl` | Download mode |

---

## Playback Controls

| Key | Action |
|-----|--------|
| `N` / `Enter` | Next episode |
| `P` | Previous episode |
| `S` | Skip to episode # |
| `R` | Replay current |
| `D` | Download current |
| `Q` | Quit |

---

## Platform Setup

<details>
<summary><b>Linux</b></summary>

```bash
# Install
pip install donghua-cli

# Dependencies
sudo apt install mpv ffmpeg    # Debian/Ubuntu
sudo dnf install mpv ffmpeg    # Fedora
sudo pacman -S mpv ffmpeg      # Arch

# Optional: add shell aliases
bash <(curl -s https://raw.githubusercontent.com/Thanukamax/donghua-cli/main/scripts/install.sh)

# Optional: add to app menu
bash packaging/desktop/install-desktop.sh
```

</details>

<details>
<summary><b>Windows</b></summary>

```powershell
# Install Python (if needed)
winget install Python.Python.3.12

# Install donghua-cli
pip install donghua-cli

# Install mpv
winget install mpv

# Optional: run installer for PowerShell aliases
irm https://raw.githubusercontent.com/Thanukamax/donghua-cli/main/scripts/install.ps1 | iex
```

Or download `donghua.exe` from [Releases](https://github.com/Thanukamax/donghua-cli/releases) -- no Python needed.

</details>

<details>
<summary><b>macOS</b></summary>

```bash
# Install
pip3 install donghua-cli

# Dependencies
brew install mpv

# Optional: aliases
bash <(curl -s https://raw.githubusercontent.com/Thanukamax/donghua-cli/main/scripts/install.sh)
```

</details>

<details>
<summary><b>Android (Termux)</b></summary>

```bash
pkg install python mpv ffmpeg
pip install donghua-cli

# Run
dhua
```

Platform is auto-detected. Quality defaults to 360p, playback uses Android intents (MPV, VLC, MX Player).

</details>

<details>
<summary><b>From source</b></summary>

```bash
git clone https://github.com/Thanukamax/donghua-cli.git
cd donghua-cli
pip install -e ".[dev]"

# Run tests
pytest

# Run
dhua
```

</details>

---

## How It Works

1. **Search** -- queries LuciferDonghua + AnimeXin concurrently, merges results by fuzzy title match
2. **Episodes** -- fetches episode lists from all available servers, merges by episode number
3. **Extraction** -- fast regex on partial HTML, falls back to full parse, then yt-dlp
4. **Playback** -- launches MPV/VLC with the resolved stream URL
5. **Preloading** -- background thread resolves the next 2-3 episodes while you watch
6. **Cache** -- LRU cache makes repeat plays instant
7. **Fallback** -- if one server fails, silently tries the next

Movies and series are detected automatically. Movie parts (PT-01, Part 01) are handled correctly.

---

## All CLI Options

```
donghua [query] [-q QUALITY] [-d] [--classic] [--logs] [--verbose]
                [--clear-cache] [--features] [-V]

positional:
  query              Series to search for

options:
  -q, --quality      Video quality (360, 480, 720, 1080)
  -d, --download     Download instead of stream
  --classic          Classic Rich terminal output (no TUI)
  --logs             Write debug log to file
  --verbose          Print debug output to stderr
  --clear-cache      Clear the stream cache
  --features         Show features and capabilities
  -V, --version      Show version
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `command not found: dhua` | Restart your shell, or run `pip install donghua-cli` again |
| No video plays | Install mpv: see platform table above |
| Search returns nothing | Try a simpler query, or check your internet |
| Slow search | Normal -- source sites take 3-4s to respond |
| Download fails | Install yt-dlp: `pip install yt-dlp` |
| TUI looks broken | Your terminal needs 256-color support. Try `--classic` mode |
| Windows colors broken | Use Windows Terminal (not cmd.exe) |

---

## Contributing

PRs welcome. Run `pytest` and `ruff check src/` before submitting.

## License

MIT -- see [LICENSE](LICENSE).

## Disclaimer

Educational purposes only. Support official releases when available. Not affiliated with any streaming sites.

---

Made by [Thanukamax](https://github.com/Thanukamax)
