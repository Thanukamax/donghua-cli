<div align="center">

# 🗡️ Donghua CLI 🐉

### 武侠动画终端 | Imperial Terminal for Chinese Animation

[![Python](https://img.shields.io/badge/Python-3.8+-gold?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-jade?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20Android%20%7C%20iOS-blue?style=for-the-badge)](https://github.com/Thanukamax/donghua-cli)

**Stream and download Chinese animation (Donghua) from your terminal with a Wuxia-forged engine.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots)

---

</div>

## 🌟 Enter the Realm of Immortal Cultivation

Donghua CLI is a powerful, blazing-fast terminal application for streaming and downloading Chinese animation. Inspired by the aesthetic of Wuxia and Xianxia cultivation novels, it brings the elegance of imperial jade and gold to your command line.

## ✨ Features

### ⚡ Lightning Fast Performance
- **Instant Playback**: Preloads next episodes while you watch
- **Smart Caching**: LRU cache makes repeat plays instant
- **Parallel Downloads**: Multi-threaded downloads via yt-dlp

### 🌐 Multi-Source Support
- **LuciferDonghua Realm**: Primary cultivation source
- **AnimeXin Sect**: Alternative cultivation path
- **Unified Search**: Search across multiple realms simultaneously

### 🎬 Premium Experience
- **MPV Integration**: Hardware-accelerated playback
- **Quality Control**: Choose your preferred resolution (360p - 1080p)
- **Episode Management**: Navigate, skip, replay with ease
- **Download Mode**: Archive episodes for offline viewing

### 🎨 Beautiful UI
- **Imperial Theme**: Jade and gold color scheme
- **Wuxia Aesthetics**: Martial arts inspired interface
- **Status Indicators**: Clear visual feedback for all actions
- **Smart Truncation**: Clean episode lists even with long titles

### 📱 Cross-Platform
- Linux (Debian, Ubuntu, Fedora, Arch)
- Windows 10/11
- Android (Termux)
- iOS (iSH)

## 📋 Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **MPV** or **VLC** (video player)
- **ffmpeg** (for downloads)

## 🚀 Installation

### Linux

#### Debian / Ubuntu / Mint
```bash
# Install system dependencies
sudo apt update && sudo apt install python3 python3-pip mpv ffmpeg -y

# Install Python packages
pip3 install requests beautifulsoup4 yt-dlp

# Download Donghua CLI
git clone https://github.com/Thanukamax/donghua-cli.git
cd donghua-cli

# Make executable
chmod +x dhua.py

# Run
./dhua.py
```

#### Fedora / Nobara
```bash
# Install system dependencies
sudo dnf install python3 python3-pip mpv ffmpeg -y

# Install Python packages
pip3 install requests beautifulsoup4 yt-dlp

# Download and run
git clone https://github.com/Thanukamax/donghua-cli.git
cd donghua-cli
chmod +x dhua.py
./dhua.py
```

#### Arch Linux
```bash
# Install system dependencies
sudo pacman -S python python-pip mpv ffmpeg

# Install Python packages
pip3 install requests beautifulsoup4 yt-dlp

# Download and run
git clone https://github.com/Thanukamax/donghua-cli.git
cd donghua-cli
chmod +x dhua.py
./dhua.py
```

### Windows

1. Install [Python 3.8+](https://www.python.org/downloads/)
2. Install [MPV](https://mpv.io/installation/) or use: `winget install mpv`
3. Install dependencies:
```powershell
pip install requests beautifulsoup4 yt-dlp
```
4. Download and run:
```powershell
git clone https://github.com/Thanukamax/donghua-cli.git
cd donghua-cli
python dhua.py
```

### Android (Termux)

```bash
# Install dependencies
pkg install python python-pip mpv ffmpeg -y

# Install Python packages
pip install requests beautifulsoup4 yt-dlp

# Download and run
git clone https://github.com/Thanukamax/donghua-cli.git
cd donghua-cli
chmod +x dhua.py
./dhua.py
```

## 🎮 Usage

### Interactive Mode
```bash
./dhua.py
```

### Direct Search & Stream
```bash
# Search and stream
./dhua.py "Battle Through the Heavens"

# Specify source
./dhua.py "Soul Land" -s ld

# Specify quality
./dhua.py "Perfect World" -q 1080
```

### Download Mode
```bash
# Download episodes
./dhua.py "Martial Peak" -d

# Download at specific quality
./dhua.py "Tales of Demons and Gods" -d -q 720
```

### Other Options
```bash
# Show all features
./dhua.py --features

# Clear cache
./dhua.py --clear-cache

# View help
./dhua.py --help
```

## 🎯 Playback Controls

During playback, you can use these commands:

| Key | Action |
|-----|--------|
| `N` / `Enter` | Next episode |
| `P` | Previous episode |
| `S` | Skip to specific episode |
| `R` | Replay current episode |
| `D` | Download current episode |
| `Q` | Quit to main menu |

## 📸 Screenshots

<div align="center">

### 🎨 Enhanced Banner with Badges
![Banner](https://via.placeholder.com/800x200/0a1512/d4af37?text=Donghua+CLI+Banner)

### 📋 Episode Selection
![Episodes](https://via.placeholder.com/800x400/0a1512/00A86B?text=Episode+List)

### ⚡ Playback Controls
![Playback](https://via.placeholder.com/800x300/0a1512/d4af37?text=Now+Playing)

</div>

## 🛠️ Technical Details

### Architecture
- **Stream Extraction**: Fast pattern-based extraction with BeautifulSoup fallback
- **Caching System**: LRU cache with disk persistence
- **Preloader**: Background thread preloads next episodes during playback
- **Cross-Platform**: Works on Linux, Windows, Android, and iOS

### Performance Optimizations
- Partial HTML loading (only 8KB) for faster extraction
- In-memory episode caching
- Concurrent fragment downloads
- Hardware-accelerated video playback

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Please respect copyright laws and support official releases when available.

## 🙏 Acknowledgments

- **LuciferDonghua** - Primary source provider
- **AnimeXin** - Alternative source provider
- **MPV** - Excellent media player
- **yt-dlp** - Powerful download engine

---

<div align="center">

### 🗡️ Forged by Thanukamax 🐉

**May your cultivation reach new heights**

⭐ Star this repository if you find it useful!

[Report Bug](https://github.com/Thanukamax/donghua-cli/issues) • [Request Feature](https://github.com/Thanukamax/donghua-cli/issues)

</div>
