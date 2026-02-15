# Donghua CLI

A fast terminal interface for streaming Chinese animation.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quick Start

```bash
pip install requests beautifulsoup4 yt-dlp
python dhua.py "Battle Through the Heavens"
```

**[View Full Documentation →](README.html)**

## Installation

**Linux:**
```bash
sudo apt install python3 mpv ffmpeg
pip3 install requests beautifulsoup4 yt-dlp
```

**Windows:**
```powershell
winget install mpv
pip install requests beautifulsoup4 yt-dlp
```

## Features

- Multi-source aggregation (LuciferDonghua, AnimeXin)
- Intelligent episode preloading
- MPV integration
- Download mode
- Cross-platform

## Usage

```bash
python dhua.py                    # interactive mode
python dhua.py "Soul Land"        # direct search
python dhua.py "BTTH" -q 1080    # set quality
python dhua.py "Martial Peak" -d  # download
```

## License

MIT - See [LICENSE](LICENSE)
