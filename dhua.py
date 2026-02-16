#!/usr/bin/env python3
"""
Donghua CLI - Wuxia-inspired terminal player for Chinese animation
Jade borders, gold text, martial arts theme - OPTIMIZED FOR SPEED
"""

import argparse
import os
import re
import sys
import time
import subprocess
import threading
import json
from collections import OrderedDict
from typing import List, Tuple, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

# ============================================================================
# WUXIA THEME CONFIGURATION
# ============================================================================
class WuxiaTheme:
    """Wuxia-inspired color theme - jade, gold, martial colors"""
    
    # Color codes
    JADE = "\033[38;5;79m"       # Imperial jade
    DARK_JADE = "\033[38;5;29m"  # Dark jade
    GOLD = "\033[38;5;220m"      # Imperial gold
    LIGHT_GOLD = "\033[38;5;229m"# Light gold
    RED = "\033[38;5;196m"       # Martial red
    BROWN = "\033[38;5;130m"     # Earth brown
    SILVER = "\033[38;5;252m"    # Silver steel
    WHITE = "\033[38;5;255m"     # Pure white
    GRAY = "\033[38;5;245m"      # Light gray
    RESET = "\033[0m"
    
    # Wuxia-inspired borders (more angular, martial)
    BORDER_HORIZ = "─"
    BORDER_VERT = "│"
    BORDER_CORNER_TL = "┌"
    BORDER_CORNER_TR = "┐"
    BORDER_CORNER_BL = "└"
    BORDER_CORNER_BR = "┘"
    BORDER_T = "┬"
    BORDER_B = "┴"
    BORDER_L = "├"
    BORDER_R = "┤"
    BORDER_CROSS = "┼"
    
    # Wuxia symbols
    SYMBOL_SWORD = "🗡️"
    SYMBOL_DRAGON = "🐉"
    SYMBOL_SCROLL = "📜"
    SYMBOL_LOTUS = "🪷"
    SYMBOL_MOON = "🌙"
    SYMBOL_STAR = "⭐"
    SYMBOL_MOUNTAIN = "⛰️"
    SYMBOL_WAVE = "🌊"
    SYMBOL_CLOUD = "☁️"
    SYMBOL_TIGER = "🐅"
    SYMBOL_PHOENIX = "🦚"
    SYMBOL_ORNAMENT = "◆"
    SYMBOL_GLOW = "◈"
    SYMBOL_CHECK = "✓"
    SYMBOL_CROSS = "✗"
    SYMBOL_WARNING = "⚠"
    SYMBOL_INFO = "ⓘ"
    SYMBOL_LOADING = "⟳"
    
    # Martial arts techniques
    TECHNIQUES = [
        "Dragon Tail Sweep", "Phoenix Wing Strike", "Tiger Claw Attack",
        "Cloud Step", "Mountain Breaker", "River Flow",
        "Moonlight Cut", "Star Fall", "Lotus Palm"
    ]
    
    @classmethod
    def random_technique(cls):
        """Get a random martial arts technique name"""
        import random
        return random.choice(cls.TECHNIQUES)
    
    @classmethod
    def banner(cls) -> str:
        """Generate wuxia banner"""
        technique = cls.random_technique()
        lines = [
            f"{cls.JADE}{cls.BORDER_CORNER_TL}{cls.BORDER_HORIZ*58}{cls.BORDER_CORNER_TR}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET}  {cls.SYMBOL_SWORD}  {cls.GOLD}武 侠 动 画 终 端{cls.RESET}  {cls.SYMBOL_SWORD}  {cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET}   {cls.SILVER} Donghua CLI{cls.RESET}   {cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET} {cls.SYMBOL_CLOUD}{cls.GRAY} {technique:^48} {cls.SYMBOL_CLOUD}{cls.RESET} {cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET}{' '*58}{cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET} {cls.SYMBOL_DRAGON}{cls.DARK_JADE}  Enter the realm of immortal cultivation  {cls.SYMBOL_DRAGON}{cls.RESET} {cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_CORNER_BL}{cls.BORDER_HORIZ*58}{cls.BORDER_CORNER_BR}{cls.RESET}",
        ]
        return "\n".join(lines)
    
    @classmethod
    def header(cls, text: str) -> str:
        """Create a martial arts section header"""
        symbols = [cls.SYMBOL_MOUNTAIN, cls.SYMBOL_WAVE, cls.SYMBOL_STAR]
        import random
        left_sym = random.choice(symbols)
        right_sym = random.choice(symbols)
        
        padded_text = f" {text} "
        total_width = 56
        text_width = len(padded_text) + 4  # +4 for symbols and spaces
        
        if text_width < total_width:
            padding = (total_width - text_width) // 2
            left_pad = " " * padding
            right_pad = " " * (total_width - text_width - padding)
        else:
            left_pad = ""
            right_pad = ""
        
        return f"{cls.JADE}{cls.BORDER_L}{cls.BORDER_HORIZ*2}{cls.DARK_JADE}{left_pad}{left_sym} {cls.GOLD}{padded_text}{cls.DARK_JADE} {right_sym}{right_pad}{cls.JADE}{cls.BORDER_HORIZ*2}{cls.BORDER_R}{cls.RESET}"
    
    @classmethod
    def menu_item(cls, key: str, desc: str, active: bool = True) -> str:
        """Create a martial arts menu item"""
        color = cls.GOLD if active else cls.GRAY
        symbol = f"{cls.SYMBOL_STAR} " if active else "  "
        return f"  {cls.JADE}{cls.BORDER_VERT}{cls.RESET}  {cls.LIGHT_GOLD}[{key}]{cls.RESET} {symbol}{desc}"
    
    @classmethod
    def episode_item(cls, num: int, title: str, selected: bool = False) -> str:
        """Create an episode listing with wuxia flair"""
        episode_sym = cls.SYMBOL_SCROLL if "集" in title or "Episode" in title else cls.SYMBOL_STAR

        # Strict truncation to prevent overflow
        max_title_len = 50
        if len(title) > max_title_len:
            truncated_title = title[:max_title_len-3] + "..."
        else:
            truncated_title = title

        if selected:
            return f"  {cls.JADE}{cls.BORDER_VERT}{cls.RESET} {cls.GOLD}{num:3d}.{cls.RESET} {episode_sym} {cls.LIGHT_GOLD}{truncated_title:<50}{cls.RESET} {cls.JADE}{cls.BORDER_VERT}{cls.RESET}"
        return f"  {cls.JADE}{cls.BORDER_VERT}{cls.RESET} {cls.SILVER}{num:3d}.{cls.RESET} {episode_sym} {cls.WHITE}{truncated_title:<50}{cls.RESET} {cls.JADE}{cls.BORDER_VERT}{cls.RESET}"
    
    @classmethod
    def now_playing(cls, title: str, episode: int, total: int) -> str:
        """Create now playing display with martial arts theme"""
        cultivation_levels = ["Qi Refining", "Foundation", "Golden Core", "Nascent Soul", "Divine Realm"]
        import random
        level = random.choice(cultivation_levels)
        
        lines = [
            f"{cls.JADE}{cls.BORDER_CORNER_TL}{cls.BORDER_HORIZ*58}{cls.BORDER_CORNER_TR}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET} {cls.SYMBOL_PHOENIX} {cls.RED}⚔️ CULTIVATION IN PROGRESS ⚔️{cls.RESET} {cls.SYMBOL_TIGER} {cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET} {cls.GOLD}{level:^58}{cls.RESET} {cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET} {cls.LIGHT_GOLD}{title[:56]:^56}{cls.RESET} {cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET} {cls.GRAY}Episode {cls.GOLD}{episode:03d}{cls.GRAY}/{cls.GOLD}{total:03d}{cls.GRAY} {cls.SYMBOL_MOON}{' ' * 35}{cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_CORNER_BL}{cls.BORDER_HORIZ*58}{cls.BORDER_CORNER_BR}{cls.RESET}",
        ]
        return "\n".join(lines)
    
    @classmethod
    def prompt(cls, text: str = "Enter command") -> str:
        """Create a wuxia-style prompt"""
        return f"\n{cls.DARK_JADE}╭─{cls.SYMBOL_SWORD}{cls.RESET} {cls.GOLD}{text}{cls.RESET} {cls.DARK_JADE}─╮{cls.RESET}\n{cls.DARK_JADE}╰─»{cls.RESET} "
    
    @classmethod
    def progress_bar(cls, current: int, total: int, width: int = 30) -> str:
        """Create a martial arts progress bar"""
        filled = int(width * current / total)
        bar = f"{cls.JADE}[{cls.GOLD}{'■' * filled}{cls.GRAY}{'□' * (width - filled)}{cls.JADE}]{cls.RESET}"
        return f"{bar} {cls.GOLD}{current:02d}{cls.GRAY}/{cls.GOLD}{total:02d}{cls.RESET}"

    @classmethod
    def imperial_divider(cls) -> str:
        """Create an ornamental section divider"""
        line_len = 25
        line = cls.BORDER_HORIZ * line_len
        return f"\n  {cls.JADE}{line}{cls.GOLD} {cls.SYMBOL_ORNAMENT} {cls.JADE}{line}{cls.RESET}\n"

    @classmethod
    def badge(cls, text: str, style: str = "gold") -> str:
        """Create a colored badge"""
        colors = {
            "gold": (cls.GOLD, cls.WHITE),
            "jade": (cls.JADE, cls.WHITE),
            "red": (cls.RED, cls.WHITE),
            "silver": (cls.SILVER, cls.WHITE),
            "gray": (cls.GRAY, cls.WHITE)
        }
        color, text_color = colors.get(style, colors["gold"])
        return f"{color}[{text_color} {text} {color}]{cls.RESET}"

    @classmethod
    def tip_box(cls, title: str, content: str, style: str = "jade") -> str:
        """Create a tip/alert box with text wrapping"""
        color = cls.JADE if style == "jade" else cls.GOLD
        icon = "💡" if style == "jade" else "⚠️"
        width = 64
        content_width = 60

        # Wrap content text if too long
        import textwrap
        wrapped_lines = textwrap.wrap(content, width=content_width)

        lines = [
            f"{color}{cls.BORDER_CORNER_TL}{cls.BORDER_HORIZ*width}{cls.BORDER_CORNER_TR}{cls.RESET}",
            f"{color}{cls.BORDER_VERT}{cls.RESET} {icon} {cls.LIGHT_GOLD}{title:<60}{color}{cls.BORDER_VERT}{cls.RESET}",
            f"{color}{cls.BORDER_L}{cls.BORDER_HORIZ*width}{cls.BORDER_R}{cls.RESET}",
        ]

        for line in wrapped_lines:
            lines.append(f"{color}{cls.BORDER_VERT}{cls.RESET}  {cls.WHITE}{line:<60}{color}{cls.BORDER_VERT}{cls.RESET}")

        lines.append(f"{color}{cls.BORDER_CORNER_BL}{cls.BORDER_HORIZ*width}{cls.BORDER_CORNER_BR}{cls.RESET}")
        return "\n".join(lines)

    @classmethod
    def section_header(cls, label: str, title: str, subtitle: str = "") -> str:
        """Create a section header with label and subtitle"""
        lines = [
            "",
            f"  {cls.GRAY}┌─ {label.upper()} ─┐{cls.RESET}",
            f"  {cls.GOLD}{title}{cls.RESET}",
        ]
        if subtitle:
            lines.append(f"  {cls.DARK_JADE}{subtitle}{cls.RESET}")
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def glow_text(cls, text: str, color: str = "gold") -> str:
        """Create glowing text effect"""
        if color == "gold":
            return f"{cls.GOLD}{cls.SYMBOL_GLOW} {cls.LIGHT_GOLD}{text}{cls.GOLD} {cls.SYMBOL_GLOW}{cls.RESET}"
        else:
            return f"{cls.JADE}{cls.SYMBOL_GLOW} {cls.WHITE}{text}{cls.JADE} {cls.SYMBOL_GLOW}{cls.RESET}"

    @classmethod
    def status_indicator(cls, status: str, label: str) -> str:
        """Display a status with colored indicator"""
        indicators = {
            "success": (cls.JADE, cls.SYMBOL_CHECK),
            "error": (cls.RED, cls.SYMBOL_CROSS),
            "warning": (cls.GOLD, cls.SYMBOL_WARNING),
            "info": (cls.SILVER, cls.SYMBOL_INFO),
            "loading": (cls.GOLD, cls.SYMBOL_LOADING)
        }
        color, symbol = indicators.get(status, indicators["info"])
        return f"  {color}{symbol}{cls.RESET} {cls.WHITE}{label}{cls.RESET}"

    @classmethod
    def feature_card(cls, icon: str, title: str, desc: str) -> str:
        """Display a feature card"""
        width = 38
        lines = [
            f"  {cls.JADE}{cls.BORDER_CORNER_TL}{cls.BORDER_HORIZ*width}{cls.BORDER_CORNER_TR}{cls.RESET}",
            f"  {cls.JADE}{cls.BORDER_VERT}{cls.RESET} {icon}  {cls.GOLD}{title:<34}{cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"  {cls.JADE}{cls.BORDER_VERT}{cls.RESET}    {cls.GRAY}{desc[:34]:<34}{cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"  {cls.JADE}{cls.BORDER_CORNER_BL}{cls.BORDER_HORIZ*width}{cls.BORDER_CORNER_BR}{cls.RESET}"
        ]
        return "\n".join(lines)

    @classmethod
    def enhanced_banner(cls) -> str:
        """Generate enhanced wuxia banner with badges"""
        technique = cls.random_technique()
        import platform
        os_name = platform.system()

        lines = [
            f"{cls.JADE}{cls.BORDER_CORNER_TL}{cls.BORDER_HORIZ*68}{cls.BORDER_CORNER_TR}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET}  {cls.SYMBOL_SWORD}  {cls.GOLD}武 侠 动 画 终 端{cls.RESET} {cls.SYMBOL_DRAGON}  {cls.LIGHT_GOLD}Donghua CLI{cls.RESET}  {cls.SYMBOL_SWORD}  {' '*15}{cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET}   {cls.GRAY}Imperial Terminal for Chinese Animation{' '*26}{cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_L}{cls.BORDER_HORIZ*68}{cls.BORDER_R}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET} {cls.SYMBOL_CLOUD}{cls.GRAY} {technique:^62} {cls.SYMBOL_CLOUD}{cls.RESET} {cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_L}{cls.BORDER_HORIZ*68}{cls.BORDER_R}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET}  {cls.badge('v2.0 OPTIMIZED', 'red')} {cls.badge('Python 3.8+', 'gold')} {cls.badge(os_name, 'jade')} {cls.badge('MIT License', 'silver')}  {cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET}{' '*68}{cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_VERT}{cls.RESET} {cls.SYMBOL_DRAGON}{cls.DARK_JADE}  Enter the realm of immortal cultivation{' '*25}{cls.RESET} {cls.JADE}{cls.BORDER_VERT}{cls.RESET}",
            f"{cls.JADE}{cls.BORDER_CORNER_BL}{cls.BORDER_HORIZ*68}{cls.BORDER_CORNER_BR}{cls.RESET}",
        ]
        return "\n".join(lines)

# ============================================================================
# CONFIGURATION
# ============================================================================
class Config:
    """Global configuration"""
    
    # Sources
    SOURCES = {
        "ld": {
            "name": "LuciferDonghua",
            "base_url": "https://luciferdonghua.in",
            "search_selector": "article.bs",
            "episode_selectors": [".eplister a", ".episodelist a", "#chapterlist a", "li a"]
        },
        "ax": {
            "name": "AnimeXin",
            "base_url": "https://animexin.dev",
            "search_selector": "article",
            "episode_selectors": [".eplister a", ".episodelist a", "#chapterlist a", ".lstep a", "ul li a"]
        }
    }
    
    # Defaults
    DEFAULT_QUALITY = "720"
    DOWNLOAD_DIR = os.path.normpath(os.path.expanduser("~/Videos/Donghua"))
    
    # Cache files
    if os.name == 'nt':  # Windows
        CACHE_DIR = os.path.expanduser("~/.donghua")
    else:  # Linux/Mac
        CACHE_DIR = os.path.expanduser("~/.cache/donghua")
    
    STREAM_CACHE_FILE = os.path.join(CACHE_DIR, "stream_cache.json")
    EPISODE_CACHE_FILE = os.path.join(CACHE_DIR, "episode_cache.json")
    
    # Network
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://google.com",
        "Upgrade-Insecure-Requests": "1",
    }

# ============================================================================
# FAST CACHE SYSTEM
# ============================================================================
class FastStreamCache:
    """LRU cache for stream URLs - makes repeat plays INSTANT"""
    
    def __init__(self, max_size=100):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.load()
    
    def get(self, episode_url: str) -> Optional[str]:
        """Get cached stream URL (O(1) time)"""
        if episode_url in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(episode_url)
            return self.cache[episode_url]
        return None
    
    def put(self, episode_url: str, stream_url: str):
        """Cache stream URL"""
        if episode_url in self.cache:
            self.cache.move_to_end(episode_url)
        else:
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                self.cache.popitem(last=False)
            self.cache[episode_url] = stream_url
        self.save()
    
    def save(self):
        """Save cache to disk"""
        try:
            os.makedirs(Config.CACHE_DIR, exist_ok=True)
            with open(Config.STREAM_CACHE_FILE, 'w') as f:
                json.dump(list(self.cache.items()), f)
        except:
            pass
    
    def load(self):
        """Load cache from disk"""
        try:
            if os.path.exists(Config.STREAM_CACHE_FILE):
                with open(Config.STREAM_CACHE_FILE, 'r') as f:
                    items = json.load(f)
                    self.cache = OrderedDict(items[-self.max_size:])
        except:
            self.cache = OrderedDict()

# ============================================================================
# INSTANT PRELOADER
# ============================================================================
class InstantPreloader:
    """Preloads next episodes WHILE you're watching - makes navigation INSTANT"""
    
    def __init__(self):
        self.cache = FastStreamCache()
        self.preload_thread = None
        self.stop_flag = threading.Event()
        self.current_preloads = []
    
    def preload_episodes(self, episodes: List[Tuple[str, str]], start_idx: int):
        """Preload next 2 episodes in background"""
        if self.preload_thread and self.preload_thread.is_alive():
            self.stop_flag.set()
            self.preload_thread.join(timeout=1)
        
        self.stop_flag.clear()
        self.current_preloads = []
        
        # Get next 2 episode URLs
        next_urls = []
        for i in range(start_idx + 1, min(start_idx + 3, len(episodes))):
            next_urls.append(episodes[i][1])
        
        if not next_urls:
            return
        
        def preload_worker(urls):
            for url in urls:
                if self.stop_flag.is_set():
                    break
                try:
                    # Skip if already cached
                    if self.cache.get(url):
                        continue
                    
                    stream_url = StreamExtractor.extract_stream_url_fast(url)
                    if stream_url and stream_url != url:
                        self.cache.put(url, stream_url)
                        self.current_preloads.append(stream_url)
                except:
                    pass
        
        self.preload_thread = threading.Thread(
            target=preload_worker, 
            args=(next_urls,),
            daemon=True
        )
        self.preload_thread.start()
    
    def get_stream(self, episode_url: str) -> str:
        """Get stream URL - uses cache if available, otherwise extracts fresh"""
        # Check cache first (INSTANT if cached)
        cached = self.cache.get(episode_url)
        if cached:
            return cached
        
        # Extract fresh
        stream_url = StreamExtractor.extract_stream_url_fast(episode_url)
        self.cache.put(episode_url, stream_url)
        return stream_url
    
    def stop(self):
        """Stop preloading"""
        self.stop_flag.set()
        if self.preload_thread and self.preload_thread.is_alive():
            self.preload_thread.join(timeout=1)

# ============================================================================
# CORE UTILITIES (OPTIMIZED)
# ============================================================================
class Utils:
    """Utility functions"""
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen (Windows/Linux compatible)"""
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitize filename for cross-platform compatibility"""
        invalid_chars = r'[\\/:*?"<>|]'
        sanitized = re.sub(invalid_chars, '_', name)
        sanitized = sanitized.strip(' .')
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized if sanitized else "untitled"
    
    @staticmethod
    def extract_episode_number(title: str, url: str) -> int:
        """Extract episode number from title or URL"""
        patterns = [
            r'episode\s*[-]?\s*(\d+)',
            r'ep\s*[-]?\s*(\d+)',
            r'第\s*(\d+)\s*[集话]',
            r'(\d{2,})\s*$',
            r'\b(\d{2,})\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Try URL as fallback
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 999999
    
    @staticmethod
    def get_soup_fast(url: str, timeout: int = 8) -> BeautifulSoup:
        """Fast HTTP fetch with fallback"""
        try:
            resp = requests.get(url, headers=Config.HEADERS, timeout=timeout)
            if resp.status_code == 200:
                return BeautifulSoup(resp.text, "html.parser")
        except requests.exceptions.Timeout:
            print(f"{WuxiaTheme.GRAY}  ⏱️ Request timeout, trying curl...{WuxiaTheme.RESET}")
        except:
            pass
        
        # Fallback to curl (works on Windows with Git Bash/Cygwin/WSL)
        try:
            if os.name == 'nt':
                # Windows - try curl if available
                curl_cmd = ["curl", "-s", "-L", "-m", str(timeout),
                          "-A", Config.HEADERS["User-Agent"], url]
            else:
                # Linux/Mac
                curl_cmd = ["curl", "-s", "-L", "-m", str(timeout),
                          "-H", f"User-Agent: {Config.HEADERS['User-Agent']}",
                          "-H", "Accept: text/html", url]
            
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=timeout+2)
            if result.returncode == 0:
                return BeautifulSoup(result.stdout, "html.parser")
        except:
            pass
        
        return BeautifulSoup("", "html.parser")

# ============================================================================
# OPTIMIZED STREAM EXTRACTOR
# ============================================================================
class StreamExtractor:
    """Ultra-fast stream extractor with intelligent caching"""
    
    preloader = InstantPreloader()
    
    @staticmethod
    def extract_stream_url_fast(episode_url: str) -> str:
        """Ultra-fast extraction - tries fastest methods first"""
        
        # 1. Already direct URL? (Fastest - 0ms)
        if episode_url.endswith((".m3u8", ".mp4", ".mkv")):
            return episode_url
        
        # 2. Try common patterns without full page load (Fast - ~200ms)
        try:
            # Quick partial fetch - only first 8KB of HTML
            resp = requests.get(episode_url, headers=Config.HEADERS, 
                              timeout=5, stream=True)
            html_chunk = ""
            for chunk in resp.iter_content(chunk_size=4096, decode_unicode=True):
                html_chunk += chunk if isinstance(chunk, str) else chunk.decode('utf-8', 'ignore')
                if len(html_chunk) > 8192:  # 8KB is enough
                    break
            
            # Fast regex search for common patterns
            import re
            
            # Dailymotion video ID
            dm_match = re.search(r'data-video\s*=\s*["\']([^"\']+)["\']', html_chunk)
            if dm_match:
                return f"https://www.dailymotion.com/video/{dm_match.group(1)}"
            
            # Iframe src
            iframe_match = re.search(r'src\s*=\s*["\'](https?://[^"\']*dailymotion[^"\']*)["\']', html_chunk)
            if iframe_match:
                return iframe_match.group(1)
            
            # OK.ru iframe
            ok_match = re.search(r'src\s*=\s*["\'](https?://ok\.[^"\']+)["\']', html_chunk)
            if ok_match:
                return ok_match.group(1)
            
        except:
            pass
        
        # 3. Full BeautifulSoup parsing (Medium - ~500ms)
        soup = Utils.get_soup_fast(episode_url, timeout=8)
        
        # Check for Dailymotion in scripts
        for script in soup.select("script[data-video]"):
            src = script.get("src", "")
            if "dailymotion" in src:
                video_id = script.get("data-video")
                if video_id:
                    return f"https://www.dailymotion.com/video/{video_id}"
        
        # Check meta tags
        for meta in soup.select('meta[content*="dailymotion"], meta[content*="ok.ru"]'):
            if content := meta.get("content", ""):
                return content
        
        # Check iframes
        for iframe in soup.select("iframe"):
            src = iframe.get("src") or iframe.get("data-src")
            if src and any(x in src for x in ["dailymotion", "ok.ru", "youtube"]):
                return src
        
        # 4. Fallback to yt-dlp (Slowest - ~1000ms+)
        try:
            cmd = ["yt-dlp", "--get-url", "--quiet",
                  "--no-check-certificates",
                  "--referer", episode_url,
                  "--user-agent", Config.HEADERS["User-Agent"],
                  episode_url]
            
            # Windows-specific adjustments
            if os.name == 'nt':
                # Hide console window on Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      timeout=15, startupinfo=startupinfo)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line.startswith("http") and not line.endswith(".svg"):
                        return line
        except:
            pass
        
        return episode_url

# ============================================================================
# OPTIMIZED SCRAPER
# ============================================================================
class Scraper:
    """Fast scraper with intelligent caching"""
    
    def __init__(self, source: str):
        self.source = Config.SOURCES[source]
        self.base_url = self.source["base_url"]
        self.episode_cache = {}
    
    def search(self, query: str) -> List[Tuple[str, str]]:
        """Fast search with timeout"""
        url = f"{self.base_url}/?s={query.replace(' ', '+')}"
        soup = Utils.get_soup_fast(url, timeout=10)
        
        results = []
        seen = set()
        
        articles = soup.select(self.source["search_selector"])
        if not articles:
            articles = soup.select("a")
        
        for article in articles[:15]:  # Limit to 15 results for speed
            a = article if article.name == "a" else article.select_one("a")
            if a and (href := a.get("href")):
                if href not in seen and "/anime/" in href:
                    seen.add(href)
                    title = a.get("title") or a.get_text(strip=True)
                    results.append((title, href))
        
        return results
    
    def get_episodes(self, series_url: str) -> List[Tuple[str, str]]:
        """Get ALL episodes with caching"""
        # Check memory cache first
        if series_url in self.episode_cache:
            return self.episode_cache[series_url]
        
        soup = Utils.get_soup_fast(series_url, timeout=12)
        episodes = []
        seen_urls = set()

        # Try all selectors
        for selector in self.source["episode_selectors"]:
            for a in soup.select(selector):
                href = a.get("href")
                if not href:
                    continue
                # Normalize URL: strip trailing slash and query params
                normalized = href.rstrip("/").split("?")[0].split("#")[0]
                if normalized in seen_urls:
                    continue
                seen_urls.add(normalized)
                title = a.get_text(strip=True)

                # Fast episode detection
                title_lower = title.lower()
                href_lower = href.lower()
                if any(indicator in title_lower or indicator in href_lower
                      for indicator in ["episode", "ep-", "第", "集", "ep"]):
                    episodes.append((title, href))

        # Sort by episode number
        episodes.sort(key=lambda x: Utils.extract_episode_number(x[0], x[1]))

        # Remove duplicates with the same episode number (keep first occurrence)
        seen_nums = set()
        unique_episodes = []
        for ep in episodes:
            ep_num = Utils.extract_episode_number(ep[0], ep[1])
            if ep_num not in seen_nums:
                seen_nums.add(ep_num)
                unique_episodes.append(ep)
        episodes = unique_episodes
        
        # Cache in memory
        self.episode_cache[series_url] = episodes
        
        return episodes

# ============================================================================
# LIGHTNING-FAST PLAYER
# ============================================================================
class Player:
    """Ultra-fast MPV playback with instant starts"""
    
    def __init__(self, quality: str = Config.DEFAULT_QUALITY):
        self.quality = quality
        self.current_process = None
        self.preloader = InstantPreloader()
    
    def play(self, url: str, episodes: List[Tuple[str, str]] = None, 
             current_idx: int = 0, log_file: Optional[str] = None) -> bool:
        """Start MPV INSTANTLY with preloaded streams"""
        
        # Get stream URL from preloader cache (INSTANT if cached)
        stream_url = self.preloader.get_stream(url)
        
        # Preload next episodes in background
        if episodes and current_idx < len(episodes) - 1:
            self.preloader.preload_episodes(episodes, current_idx)
        
        # Build MPV command
        cmd = ["mpv", stream_url]
        cmd.append(f"--ytdl-format=bestvideo[height<={self.quality}]+bestaudio/best[height<={self.quality}]/best")
        cmd.append("--cache=yes")
        cmd.append("--cache-secs=60")  # Larger cache for smoother playback
        cmd.append("--no-terminal")
        
        # Windows-specific MPV flags
        if os.name == 'nt':
            cmd.append("--no-border")
            cmd.append("--volume=50")
        
        if log_file:
            cmd.append(f"--log-file={log_file}")
        
        try:
            # Start MPV
            if os.name == 'nt':
                # Windows: hide console window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                    startupinfo=startupinfo
                )
            else:
                # Linux/Mac
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            print(WuxiaTheme.status_indicator("success", "Player launched instantly!"))
            return True
        except FileNotFoundError:
            print(WuxiaTheme.status_indicator("error", "MPV not found on your system"))
            print()
            if os.name == 'nt':
                print(WuxiaTheme.tip_box(
                    "Installation Required",
                    "Install MPV from: https://mpv.io/ or use: winget install mpv",
                    "gold"
                ))
            else:
                print(WuxiaTheme.tip_box(
                    "Installation Required",
                    "Ubuntu/Debian: sudo apt install mpv | Fedora: sudo dnf install mpv",
                    "gold"
                ))
            return False
    
    def stop(self):
        """Stop playback and preloading"""
        self.preloader.stop()
        if self.current_process and self.current_process.poll() is None:
            try:
                if os.name == 'nt':
                    self.current_process.terminate()
                    time.sleep(0.3)
                    if self.current_process.poll() is None:
                        self.current_process.kill()
                else:
                    self.current_process.terminate()
                    time.sleep(0.3)
                    if self.current_process.poll() is None:
                        self.current_process.kill()
                self.current_process.wait(timeout=2)
            except:
                pass
    
    def is_playing(self) -> bool:
        """Check if MPV is still running"""
        return self.current_process and self.current_process.poll() is None

# ============================================================================
# DOWNLOADER (OPTIMIZED)
# ============================================================================
class Downloader:
    """Handles episode downloads"""
    
    @staticmethod
    def download_episode(url: str, series_title: str, ep_title: str, quality: str) -> bool:
        """Download an episode using yt-dlp"""
        # Get pre-extracted stream for faster download
        stream_url = StreamExtractor.preloader.get_stream(url)
        
        # Create directory
        series_dir = os.path.join(Config.DOWNLOAD_DIR, Utils.sanitize_filename(series_title))
        os.makedirs(series_dir, exist_ok=True)
        
        # Build filename
        filename = f"{Utils.sanitize_filename(ep_title)}.%(ext)s"
        output_path = os.path.join(series_dir, filename)
        
        # Download with yt-dlp (optimized flags)
        cmd = [
            "yt-dlp",
            "-f", f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best",
            "-o", output_path,
            "--no-check-certificates",
            "--no-part",
            "--concurrent-fragments", "4",  # Parallel downloads
            stream_url
        ]
        
        try:
            print(WuxiaTheme.status_indicator("loading", "Starting fast download..."))

            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                result = subprocess.run(cmd, check=True, capture_output=True,
                                      text=True, startupinfo=startupinfo)
            else:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            print(WuxiaTheme.status_indicator("success", "Download complete!"))
            return True
        except subprocess.CalledProcessError as e:
            print(WuxiaTheme.status_indicator("error", "Download failed"))
            return False

# ============================================================================
# USER INTERFACE (UNCHANGED - KEEPING YOUR GREAT DESIGN)
# ============================================================================
class UserInterface:
    """Handles all user interactions with wuxia theme"""
    
    @staticmethod
    def show_banner():
        """Display wuxia banner"""
        Utils.clear_screen()
        print(WuxiaTheme.enhanced_banner())
        print()
    
    @staticmethod
    def select_source() -> str:
        """Let user select source"""
        print(WuxiaTheme.section_header(
            "Cultivation Realm Selection",
            "Choose Your Realm",
            "Select which realm to search for cultivation manuals"
        ))

        sources = [
            ("ld", "LuciferDonghua Realm", "Primary cultivation source", True),
            ("ax", "AnimeXin Sect", "Alternative cultivation path", True),
            ("both", "Search Both Realms", "Maximum coverage", True)
        ]

        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_CORNER_TL}{WuxiaTheme.BORDER_HORIZ*56}{WuxiaTheme.BORDER_CORNER_TR}{WuxiaTheme.RESET}")
        for key, name, desc, active in sources:
            symbol = f"{WuxiaTheme.SYMBOL_STAR} " if active else "  "
            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {WuxiaTheme.LIGHT_GOLD}[{key.upper()}]{WuxiaTheme.RESET} {symbol}{WuxiaTheme.WHITE}{name:<25}{WuxiaTheme.GRAY}{desc:<18}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")
        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_CORNER_BL}{WuxiaTheme.BORDER_HORIZ*56}{WuxiaTheme.BORDER_CORNER_BR}{WuxiaTheme.RESET}")

        while True:
            try:
                choice = input(WuxiaTheme.prompt("Choose cultivation realm")).strip().lower()
                if choice in ["", "both", "b"]:
                    print(WuxiaTheme.status_indicator("success", "Searching both realms for maximum results"))
                    return "both"
                elif choice in ["ld", "l"]:
                    print(WuxiaTheme.status_indicator("success", "Entering LuciferDonghua Realm"))
                    return "ld"
                elif choice in ["ax", "a"]:
                    print(WuxiaTheme.status_indicator("success", "Entering AnimeXin Sect"))
                    return "ax"
                else:
                    print(WuxiaTheme.status_indicator("error", "Invalid choice, young master"))
            except KeyboardInterrupt:
                raise
    
    @staticmethod
    def select_from_list(items: List[Tuple[str, str]], title: str) -> int:
        """Display list and let user select"""
        print(WuxiaTheme.section_header(
            "Cultivation Manuals Found",
            title,
            f"{len(items)} sacred scrolls discovered"
        ))

        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_CORNER_TL}{WuxiaTheme.BORDER_HORIZ*64}{WuxiaTheme.BORDER_CORNER_TR}{WuxiaTheme.RESET}")
        for i, (item_title, _) in enumerate(items, 1):
            # Add visual separators every 5 items for readability
            if i > 1 and (i - 1) % 5 == 0:
                print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_L}{WuxiaTheme.BORDER_HORIZ*64}{WuxiaTheme.BORDER_R}{WuxiaTheme.RESET}")

            # Strict truncation to prevent overflow
            max_title_len = 52
            if len(item_title) > max_title_len:
                truncated_title = item_title[:max_title_len-3] + "..."
            else:
                truncated_title = item_title

            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET} {WuxiaTheme.SYMBOL_SCROLL} {WuxiaTheme.GOLD}{i:3d}.{WuxiaTheme.RESET} {WuxiaTheme.WHITE}{truncated_title:<52}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")

        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_CORNER_BL}{WuxiaTheme.BORDER_HORIZ*64}{WuxiaTheme.BORDER_CORNER_BR}{WuxiaTheme.RESET}")

        while True:
            try:
                choice = input(WuxiaTheme.prompt(f"Select manual [1-{len(items)}]")).strip()
                if not choice:
                    print(WuxiaTheme.status_indicator("warning", "Please enter a number"))
                    continue

                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    print(WuxiaTheme.status_indicator("success", f"Selected: {items[idx][0][:50]}"))
                    return idx
                else:
                    print(WuxiaTheme.status_indicator("error", f"Selection out of range (1-{len(items)})"))
            except ValueError:
                print(WuxiaTheme.status_indicator("error", "Please enter a valid number"))
            except KeyboardInterrupt:
                raise
    
    @staticmethod
    def display_all_episodes(episodes: List[Tuple[str, str]], page: int = 1, per_page: int = 20) -> Tuple[int, int]:
        """Display ALL episodes with pagination"""
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, len(episodes))
        total_pages = (len(episodes) + per_page - 1) // per_page

        print(WuxiaTheme.section_header(
            "Episode Manual",
            "Cultivation Techniques",
            f"Viewing {start_idx + 1}-{end_idx} of {len(episodes)} techniques"
        ))

        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_CORNER_TL}{WuxiaTheme.BORDER_HORIZ*64}{WuxiaTheme.BORDER_CORNER_TR}{WuxiaTheme.RESET}")

        # Show episodes for current page
        for i in range(start_idx, end_idx):
            # Add visual separator every 5 episodes
            if i > start_idx and (i - start_idx) % 5 == 0:
                print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_L}{WuxiaTheme.BORDER_HORIZ*64}{WuxiaTheme.BORDER_R}{WuxiaTheme.RESET}")

            episode_sym = WuxiaTheme.SYMBOL_SCROLL
            ep_num = Utils.extract_episode_number(episodes[i][0], episodes[i][1])
            ep_label = f"Episode {ep_num}" if ep_num < 999999 else f"Episode {i + 1}"

            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET} {WuxiaTheme.SILVER}{i + 1:3d}.{WuxiaTheme.RESET} {episode_sym} {WuxiaTheme.WHITE}{ep_label:<50}{WuxiaTheme.RESET} {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")

        # Show pagination info
        if total_pages > 1:
            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_L}{WuxiaTheme.BORDER_HORIZ*64}{WuxiaTheme.BORDER_R}{WuxiaTheme.RESET}")
            progress = WuxiaTheme.progress_bar(page, total_pages, 20)
            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET} {WuxiaTheme.GRAY}Page {page}/{total_pages}{WuxiaTheme.RESET}  {progress}  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")
            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET} {WuxiaTheme.GRAY}Navigation: {WuxiaTheme.LIGHT_GOLD}[N]ext {WuxiaTheme.GRAY}| {WuxiaTheme.LIGHT_GOLD}[P]revious{' '*28}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")

        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_CORNER_BL}{WuxiaTheme.BORDER_HORIZ*64}{WuxiaTheme.BORDER_CORNER_BR}{WuxiaTheme.RESET}")

        return total_pages, per_page
    
    @staticmethod
    def select_episodes_interactive(episodes: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Interactive episode selection with ALL episodes visible via pagination"""
        page = 1
        per_page = 20
        
        while True:
            Utils.clear_screen()
            UserInterface.show_banner()
            total_pages, per_page = UserInterface.display_all_episodes(episodes, page, per_page)
            
            print()
            print(WuxiaTheme.glow_text("Cultivation Selection Options", "gold"))
            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_CORNER_TL}{WuxiaTheme.BORDER_HORIZ*54}{WuxiaTheme.BORDER_CORNER_TR}{WuxiaTheme.RESET}")
            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {WuxiaTheme.LIGHT_GOLD}[1-5,8,10-12]{WuxiaTheme.RESET}  {WuxiaTheme.GRAY}→{WuxiaTheme.RESET}  {WuxiaTheme.WHITE}Select specific techniques{' '*18}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")
            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {WuxiaTheme.LIGHT_GOLD}[all]{WuxiaTheme.RESET}         {WuxiaTheme.GRAY}→{WuxiaTheme.RESET}  {WuxiaTheme.WHITE}Select all techniques{' '*23}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")
            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {WuxiaTheme.LIGHT_GOLD}[1]{WuxiaTheme.RESET}           {WuxiaTheme.GRAY}→{WuxiaTheme.RESET}  {WuxiaTheme.WHITE}Select single technique{' '*21}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")

            if total_pages > 1:
                print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_L}{WuxiaTheme.BORDER_HORIZ*54}{WuxiaTheme.BORDER_R}{WuxiaTheme.RESET}")
                print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {WuxiaTheme.LIGHT_GOLD}[n/p]{WuxiaTheme.RESET}         {WuxiaTheme.GRAY}→{WuxiaTheme.RESET}  {WuxiaTheme.WHITE}Navigate pages{' '*30}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")

            print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_CORNER_BL}{WuxiaTheme.BORDER_HORIZ*54}{WuxiaTheme.BORDER_CORNER_BR}{WuxiaTheme.RESET}")
            
            try:
                choice = input(WuxiaTheme.prompt("Select techniques")).strip().lower()
                
                if choice == "n" and page < total_pages:
                    page += 1
                    continue
                elif choice == "p" and page > 1:
                    page -= 1
                    continue
                elif choice in ["", "all", "a"]:
                    return episodes
                else:
                    # Parse episode selection
                    selected = []
                    try:
                        for part in choice.split(","):
                            part = part.strip()
                            if "-" in part:
                                start, end = map(int, part.split("-"))
                                if start < 1 or end > len(episodes) or start > end:
                                    raise IndexError
                                selected.extend(episodes[start-1:end])
                            else:
                                num = int(part)
                                if num < 1 or num > len(episodes):
                                    raise IndexError
                                selected.append(episodes[num-1])

                        if selected:
                            print(WuxiaTheme.status_indicator("success", f"Selected {len(selected)} technique(s)"))
                            return selected
                        print(WuxiaTheme.status_indicator("error", "No techniques selected"))
                        time.sleep(1)
                    except ValueError:
                        print(WuxiaTheme.status_indicator("error", "Please enter a valid number or range"))
                        time.sleep(1)
                    except IndexError:
                        print(WuxiaTheme.status_indicator("error", f"Out of range. Pick between 1 and {len(episodes)}"))
                        time.sleep(1)
            except KeyboardInterrupt:
                raise
    
    @staticmethod
    def show_playback_controls(title: str, current: int, total: int):
        """Show playback controls with martial arts theme"""
        print(WuxiaTheme.now_playing(title, current, total))
        print()
        print(WuxiaTheme.glow_text("Playback Controls", "jade"))
        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_CORNER_TL}{WuxiaTheme.BORDER_HORIZ*54}{WuxiaTheme.BORDER_CORNER_TR}{WuxiaTheme.RESET}")
        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {WuxiaTheme.LIGHT_GOLD}[D]{WuxiaTheme.RESET} Download this technique{' '*28}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")

        prev_color = WuxiaTheme.LIGHT_GOLD if current > 1 else WuxiaTheme.GRAY
        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {prev_color}[P]{WuxiaTheme.RESET} Previous technique{' '*32}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")

        next_color = WuxiaTheme.LIGHT_GOLD if current < total else WuxiaTheme.GRAY
        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {next_color}[N]{WuxiaTheme.RESET} Next technique{' '*36}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")

        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {WuxiaTheme.LIGHT_GOLD}[S]{WuxiaTheme.RESET} Skip to specific technique{' '*25}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")
        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {WuxiaTheme.LIGHT_GOLD}[R]{WuxiaTheme.RESET} Restart cultivation{' '*31}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")
        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}  {WuxiaTheme.LIGHT_GOLD}[Q]{WuxiaTheme.RESET} Return to sect{' '*36}{WuxiaTheme.JADE}{WuxiaTheme.BORDER_VERT}{WuxiaTheme.RESET}")
        print(f"  {WuxiaTheme.JADE}{WuxiaTheme.BORDER_CORNER_BL}{WuxiaTheme.BORDER_HORIZ*54}{WuxiaTheme.BORDER_CORNER_BR}{WuxiaTheme.RESET}")
        print(f"\n  {WuxiaTheme.GRAY}⚡ Close MPV window or enter command to continue...{WuxiaTheme.RESET}")

# ============================================================================
# MAIN APPLICATION (OPTIMIZED)
# ============================================================================
class DonghuaCLI:
    """Main application class - OPTIMIZED VERSION"""
    
    def __init__(self):
        self.theme = WuxiaTheme
        self.ui = UserInterface
        self.player = None
        self.preloader = InstantPreloader()

        # Create cache directory
        os.makedirs(Config.CACHE_DIR, exist_ok=True)
        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

    def show_features(self):
        """Display feature showcase"""
        self.ui.show_banner()

        print(self.theme.section_header(
            "Core Abilities",
            "Features & Capabilities",
            "Everything you need to stream and download Donghua"
        ))

        features = [
            ("🌐", "Multi-Source Support", "LuciferDonghua + AnimeXin realms"),
            ("⚡", "Lightning Fast", "Instant playback with preloading"),
            ("⬇️", "Smart Downloads", "Parallel downloads via yt-dlp"),
            ("📱", "Cross-Platform", "Linux • Windows • Android • iOS"),
            ("🔍", "Smart Search", "Find any Donghua instantly"),
            ("🎬", "MPV Integration", "Premium playback experience"),
        ]

        # Display features in 2 columns
        print(f"  {self.theme.JADE}{'─' * 70}{self.theme.RESET}")
        for i in range(0, len(features), 2):
            left = features[i]
            right = features[i+1] if i+1 < len(features) else None

            left_text = f"{left[0]} {self.theme.GOLD}{left[1]:<22}{self.theme.GRAY}{left[2]:<20}{self.theme.RESET}"

            if right:
                right_text = f"{right[0]} {self.theme.GOLD}{right[1]:<22}{self.theme.GRAY}{right[2]:<20}{self.theme.RESET}"
                print(f"  {left_text}")
                print(f"  {right_text}")
            else:
                print(f"  {left_text}")

            if i < len(features) - 2:
                print(f"  {self.theme.JADE}{'─' * 70}{self.theme.RESET}")

        print(f"  {self.theme.JADE}{'─' * 70}{self.theme.RESET}")

        print(self.theme.imperial_divider())

        print(self.theme.tip_box(
            "Quick Start",
            "Run 'dhua' for interactive mode or 'dhua --help' for all options",
            "jade"
        ))
        print()
    
    def run(self):
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="Donghua Cultivation Terminal - OPTIMIZED",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  dhua "soul land"                Search and cultivate
  dhua "perfect world" -s ld      Search LuciferDonghua Realm
  dhua "btth" -q 1080             Cultivate at 1080p resolution
  dhua "martial peak" -d          Archive techniques (download)
            """
        )
        
        parser.add_argument("query", nargs="?", help="Cultivation manual to search")
        parser.add_argument("-s", "--source", choices=["ld", "ax"], help="Cultivation realm to use")
        parser.add_argument("-q", "--quality", default=Config.DEFAULT_QUALITY, 
                          help=f"Resolution quality (default: {Config.DEFAULT_QUALITY})")
        parser.add_argument("-d", "--download", action="store_true", help="Archive mode (download)")
        parser.add_argument("--log", help="Cultivation log file")
        parser.add_argument("--clear-cache", action="store_true", help="Clear stream cache")
        parser.add_argument("--features", action="store_true", help="Show features and capabilities")
        
        args = parser.parse_args()
        
        # Show features if requested
        if args.features:
            self.show_features()
            return

        # Clear cache if requested
        if args.clear_cache:
            self.clear_cache()

        try:
            if args.query:
                # Direct mode with arguments
                self.direct_mode(args)
            else:
                # Interactive mode
                self.interactive_mode()
        except KeyboardInterrupt:
            self.cleanup()
            print(f"\n{self.theme.imperial_divider()}")
            print(self.theme.glow_text("Cultivation Session Interrupted", "jade"))
            print(self.theme.status_indicator("info", "May your journey be eternal"))
        except Exception as e:
            self.cleanup()
            print(f"\n{self.theme.imperial_divider()}")
            print(self.theme.status_indicator("error", f"Cultivation Error: {e}"))
            sys.exit(1)
    
    def clear_cache(self):
        """Clear all cached data"""
        self.ui.show_banner()
        print(self.theme.status_indicator("loading", "Clearing stream cache..."))
        try:
            if os.path.exists(Config.STREAM_CACHE_FILE):
                os.remove(Config.STREAM_CACHE_FILE)
                print(self.theme.status_indicator("success", "Stream cache cleared successfully"))
            else:
                print(self.theme.status_indicator("info", "No cache found to clear"))
        except Exception as e:
            print(self.theme.status_indicator("error", f"Failed to clear cache: {e}"))
    
    def direct_mode(self, args):
        """Run with command line arguments"""
        self.ui.show_banner()
        
        # Select source if not specified
        if not args.source:
            args.source = self.ui.select_source()
        
        # Search
        results = self.search_all(args.query, args.source)
        if not results:
            print(self.theme.tip_box(
                "No Results Found",
                "Try a different search term or realm",
                "gold"
            ))
            return

        # Select series
        idx = self.ui.select_from_list(results, "CULTIVATION MANUALS")
        series_title, series_url = results[idx]

        # Get ALL episodes
        episodes = self.get_episodes(series_url, args.source)
        if not episodes:
            print(self.theme.tip_box(
                "No Episodes Found",
                "This manual contains no techniques",
                "gold"
            ))
            return
        
        # Select episodes (shows ALL episodes)
        selected = self.ui.select_episodes_interactive(episodes)
        
        # Download or cultivate
        if args.download:
            self.download_episodes(selected, series_title, args.quality)
        else:
            self.play_episodes(selected, series_title, args.quality)
    
    def interactive_mode(self):
        """Fully interactive cultivation mode"""
        while True:
            self.ui.show_banner()
            
            # Get query
            print(self.theme.section_header(
                "Begin Your Journey",
                "Search for Cultivation Manuals",
                "Enter the name of the Donghua you seek"
            ))
            query = input(self.theme.prompt("Search cultivation manual")).strip()
            if not query:
                print(self.theme.status_indicator("warning", "Please enter a search term"))
                time.sleep(1)
                continue
            
            # Select source
            source = self.ui.select_source()
            
            # Search
            results = self.search_all(query, source)
            if not results:
                print()
                print(self.theme.tip_box(
                    "No Results Found",
                    "Try a different search term or realm",
                    "gold"
                ))
                time.sleep(3)
                continue

            # Select series
            idx = self.ui.select_from_list(results, "CULTIVATION MANUALS")
            series_title, series_url = results[idx]

            # Get ALL episodes
            episodes = self.get_episodes(series_url, source)
            if not episodes:
                print()
                print(self.theme.tip_box(
                    "No Episodes Found",
                    "This manual contains no techniques",
                    "gold"
                ))
                time.sleep(3)
                continue
            
            # Select episodes (shows ALL episodes)
            selected = self.ui.select_episodes_interactive(episodes)
            
            # Play or download choice
            print(self.theme.imperial_divider())
            print(self.theme.section_header(
                "Cultivation Method",
                "Choose Your Path",
                "Stream or download selected techniques"
            ))

            print(f"  {self.theme.JADE}{self.theme.BORDER_CORNER_TL}{self.theme.BORDER_HORIZ*54}{self.theme.BORDER_CORNER_TR}{self.theme.RESET}")
            print(f"  {self.theme.JADE}{self.theme.BORDER_VERT}{self.theme.RESET}  {self.theme.LIGHT_GOLD}[P]{self.theme.RESET} {self.theme.SYMBOL_PHOENIX} Practice techniques (stream){' '*21}{self.theme.JADE}{self.theme.BORDER_VERT}{self.theme.RESET}")
            print(f"  {self.theme.JADE}{self.theme.BORDER_VERT}{self.theme.RESET}      {self.theme.GRAY}Watch episodes instantly with MPV{' '*19}{self.theme.JADE}{self.theme.BORDER_VERT}{self.theme.RESET}")
            print(f"  {self.theme.JADE}{self.theme.BORDER_L}{self.theme.BORDER_HORIZ*54}{self.theme.BORDER_R}{self.theme.RESET}")
            print(f"  {self.theme.JADE}{self.theme.BORDER_VERT}{self.theme.RESET}  {self.theme.LIGHT_GOLD}[D]{self.theme.RESET} {self.theme.SYMBOL_SCROLL} Archive techniques (download){' '*18}{self.theme.JADE}{self.theme.BORDER_VERT}{self.theme.RESET}")
            print(f"  {self.theme.JADE}{self.theme.BORDER_VERT}{self.theme.RESET}      {self.theme.GRAY}Save episodes for offline viewing{' '*18}{self.theme.JADE}{self.theme.BORDER_VERT}{self.theme.RESET}")
            print(f"  {self.theme.JADE}{self.theme.BORDER_CORNER_BL}{self.theme.BORDER_HORIZ*54}{self.theme.BORDER_CORNER_BR}{self.theme.RESET}")

            choice = input(self.theme.prompt("Choose method [P]")).strip().lower()
            
            if choice == "d":
                self.download_episodes(selected, series_title, Config.DEFAULT_QUALITY)
            else:
                self.play_episodes(selected, series_title, Config.DEFAULT_QUALITY)
            
            # Ask to continue
            print(self.theme.imperial_divider())
            cont = input(self.theme.prompt("Continue cultivation? [Y/n]")).strip().lower()
            if cont in ["n", "no"]:
                print(f"\n{self.theme.glow_text('Farewell, Young Master', 'gold')}")
                print(self.theme.status_indicator("success", "May your cultivation reach new heights"))
                break
    
    def search_all(self, query: str, source: str) -> List[Tuple[str, str]]:
        """Search across cultivation realms"""
        print(self.theme.imperial_divider())
        print(self.theme.status_indicator("loading", f"Searching for '{query}'..."))

        if source == "both":
            print(self.theme.status_indicator("info", "Scanning both LuciferDonghua and AnimeXin realms"))
            scraper_ld = Scraper("ld")
            scraper_ax = Scraper("ax")
            results = scraper_ld.search(query) + scraper_ax.search(query)
        else:
            realm_name = "LuciferDonghua" if source == "ld" else "AnimeXin"
            print(self.theme.status_indicator("info", f"Scanning {realm_name} realm"))
            scraper = Scraper(source)
            results = scraper.search(query)

        # Remove duplicates
        seen = set()
        unique_results = []
        for title, url in results:
            if url not in seen:
                seen.add(url)
                unique_results.append((title, url))

        result_count = len(unique_results[:20])
        if result_count > 0:
            print(self.theme.status_indicator("success", f"Found {result_count} cultivation manual(s)"))
        else:
            print(self.theme.status_indicator("error", "No manuals found in this realm"))

        return unique_results[:20]  # Limit to 20 results for speed
    
    def get_episodes(self, url: str, source: str) -> List[Tuple[str, str]]:
        """Get ALL episodes from manual"""
        print(self.theme.imperial_divider())
        print(self.theme.status_indicator("loading", "Reading cultivation manual..."))

        if source == "both":
            # Determine source from URL
            if "luciferdonghua" in url:
                scraper = Scraper("ld")
                print(self.theme.status_indicator("info", "Source: LuciferDonghua Realm"))
            else:
                scraper = Scraper("ax")
                print(self.theme.status_indicator("info", "Source: AnimeXin Sect"))
        else:
            scraper = Scraper(source)

        episodes = scraper.get_episodes(url)

        if episodes:
            print(self.theme.status_indicator("success", f"Found {len(episodes)} cultivation technique(s)"))
        else:
            print(self.theme.status_indicator("warning", "No episodes found in this manual"))

        return episodes
    
    def play_episodes(self, episodes: List[Tuple[str, str]], series_title: str, quality: str):
        """Cultivate (play) episodes sequentially - OPTIMIZED FOR SPEED"""
        self.player = Player(quality)

        print(self.theme.imperial_divider())
        print(self.theme.glow_text("Cultivation Session Starting", "jade"))
        print(self.theme.status_indicator("loading", "Preparing first technique..."))

        current_idx = 0
        while current_idx < len(episodes):
            title, url = episodes[current_idx]

            Utils.clear_screen()
            self.ui.show_banner()
            self.ui.show_playback_controls(title, current_idx + 1, len(episodes))

            # Start playback with preloaded stream (INSTANT)
            if not self.player.play(url, episodes, current_idx, log_file=None):
                return

            # Monitor player in background so we can notify when it finishes
            player_finished = threading.Event()
            def _monitor_player():
                while self.player.is_playing():
                    time.sleep(0.5)
                player_finished.set()
                print(f"\n{self.theme.status_indicator('success', 'Technique complete! Press Enter or type a command.')}")

            monitor_thread = threading.Thread(target=_monitor_player, daemon=True)
            monitor_thread.start()

            # Accept user commands while player runs in the background
            action = None
            while action is None:
                try:
                    choice = input(self.theme.prompt("Command [N/P/S/R/D/Q]")).strip().lower()
                except KeyboardInterrupt:
                    self.player.stop()
                    print(f"\n{self.theme.glow_text('Cultivation Session Complete', 'jade')}")
                    print(self.theme.status_indicator("success", "All techniques mastered!"))
                    return

                if choice in ['n', '']:
                    if current_idx < len(episodes) - 1:
                        action = 'next'
                        print(self.theme.status_indicator("info", "Moving to next technique"))
                    elif player_finished.is_set():
                        action = 'done'
                    else:
                        print(self.theme.status_indicator("warning", "Already at last technique"))
                elif choice == 'p':
                    if current_idx > 0:
                        action = 'prev'
                        print(self.theme.status_indicator("info", "Moving to previous technique"))
                    else:
                        print(self.theme.status_indicator("warning", "Already at first technique"))
                elif choice == 'r':
                    action = 'replay'
                    print(self.theme.status_indicator("info", "Restarting current technique"))
                elif choice == 's':
                    try:
                        skip_to = int(input(self.theme.prompt(f"Skip to technique [1-{len(episodes)}]")).strip())
                        if 1 <= skip_to <= len(episodes):
                            action = ('skip', skip_to - 1)
                            print(self.theme.status_indicator("success", f"Skipping to technique {skip_to}"))
                        else:
                            print(self.theme.status_indicator("error", f"Out of range (1-{len(episodes)})"))
                    except ValueError:
                        print(self.theme.status_indicator("error", "Please enter a valid number"))
                    except KeyboardInterrupt:
                        pass
                elif choice == 'd':
                    print(self.theme.status_indicator("loading", "Downloading current technique..."))
                    Downloader.download_episode(url, series_title, title, quality)
                elif choice == 'q':
                    action = 'quit'
                    print(self.theme.status_indicator("info", "Returning to sect"))
                else:
                    print(f"{self.theme.GRAY}  Commands: {self.theme.LIGHT_GOLD}[N]ext [P]rev [S]kip [R]eplay [D]ownload [Q]uit{self.theme.RESET}")

            # Stop current playback
            self.player.stop()

            # Process the action
            if action == 'next':
                current_idx += 1
            elif action == 'prev':
                current_idx -= 1
            elif action == 'replay':
                pass  # same index, will replay
            elif action == 'quit':
                break
            elif action == 'done':
                current_idx += 1  # last episode finished, exit loop naturally
            elif isinstance(action, tuple) and action[0] == 'skip':
                current_idx = action[1]

        print(f"\n{self.theme.glow_text('Cultivation Session Complete', 'jade')}")
        print(self.theme.status_indicator("success", "All techniques mastered! Your cultivation has improved."))
    
    def download_episodes(self, episodes: List[Tuple[str, str]], series_title: str, quality: str):
        """Archive (download) cultivation techniques"""
        print(self.theme.imperial_divider())
        print(self.theme.section_header(
            "Archive Mode",
            "Downloading Techniques",
            f"Archiving {len(episodes)} technique(s) to {Config.DOWNLOAD_DIR}"
        ))

        successful = 0
        failed = 0

        for i, (title, url) in enumerate(episodes, 1):
            episode_num = Utils.extract_episode_number(title, url)

            # Strict truncation for download display
            max_title_len = 60
            if len(title) > max_title_len:
                display_title = title[:max_title_len-3] + "..."
            else:
                display_title = title

            print(f"\n{self.theme.GOLD}╭{'─' * 68}╮{self.theme.RESET}")
            print(f"{self.theme.GOLD}│{self.theme.RESET} {self.theme.SYMBOL_SCROLL} {self.theme.LIGHT_GOLD}[{i:03d}/{len(episodes):03d}]{self.theme.RESET} Technique {episode_num if episode_num < 999999 else i:03d}{' ' * 42}{self.theme.GOLD}│{self.theme.RESET}")
            print(f"{self.theme.GOLD}│{self.theme.RESET}   {self.theme.WHITE}{display_title:<60}{self.theme.GOLD}│{self.theme.RESET}")
            print(f"{self.theme.GOLD}╰{'─' * 68}╯{self.theme.RESET}")

            if Downloader.download_episode(url, series_title, title, quality):
                successful += 1
            else:
                failed += 1

        print(self.theme.imperial_divider())
        print(self.theme.glow_text("Archive Complete", "gold"))
        print()
        print(self.theme.status_indicator("success", f"{successful}/{len(episodes)} techniques successfully archived"))
        if failed > 0:
            print(self.theme.status_indicator("error", f"{failed} technique(s) failed to download"))
        print(self.theme.status_indicator("info", f"Archive location: {Config.DOWNLOAD_DIR}"))
    
    def cleanup(self):
        """Cleanup cultivation resources"""
        if self.player:
            self.player.stop()
        self.preloader.stop()

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    # Enable colors on Windows
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass
    
    # Create necessary directories
    os.makedirs(Config.CACHE_DIR, exist_ok=True)
    os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)
    
    # Run the OPTIMIZED cultivation terminal
    app = DonghuaCLI()
    app.run() 