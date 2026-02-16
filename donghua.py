#!/usr/bin/env python3
"""
武侠动画 - TERMUX CULTIVATION REALM
Android/Termux Donghua Streaming Client
Default Quality: 360p (optimized for mobile data)
"""
import os, re, sys, time, subprocess, requests, json
from bs4 import BeautifulSoup

# ============================================================================
# CONFIGURATION
# ============================================================================
DEFAULT_QUALITY = "360"  # 360p for mobile data saving

class WuxiaTheme:
    JADE = "\033[38;5;79m"; GOLD = "\033[38;5;220m"
    SILVER = "\033[38;5;252m"; WHITE = "\033[38;5;255m"
    RED = "\033[38;5;196m"; RESET = "\033[0m"
    
    @classmethod
    def banner(cls):
        os.system('clear')
        return f"""{cls.JADE}┌────────────────────────────────────────────────────────┐
│  ⚔️  {cls.GOLD}武 侠 动 画 : TERMUX CULTIVATION REALM {cls.JADE} ⚔️  │
│  {cls.SILVER}Quality: {DEFAULT_QUALITY}p{cls.JADE}                                          │
└────────────────────────────────────────────────────────┘{cls.RESET}"""

class Config:
    BASE_DIR = '/sdcard/Documents/DonghuaCultivation'
    CACHE_DIR = os.path.join(BASE_DIR, 'cache')
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    @staticmethod
    def setup():
        if not os.path.exists(Config.CACHE_DIR):
            try:
                os.makedirs(Config.CACHE_DIR, exist_ok=True)
            except PermissionError:
                print(f"{WuxiaTheme.RED}⚠ Cannot create cache dir. Using Termux home{WuxiaTheme.RESET}")
                Config.BASE_DIR = os.path.expanduser("~/DonghuaCultivation")
                Config.CACHE_DIR = os.path.join(Config.BASE_DIR, 'cache')
                os.makedirs(Config.CACHE_DIR, exist_ok=True)

# ============================================================================
# CORE ENGINE
# ============================================================================
class CultivationEngine:
    @staticmethod
    def get_direct_link(url):
        """Extracts actual video stream from iframe-embedded players"""
        print(f"{WuxiaTheme.JADE}  🔍 Deep scanning for {DEFAULT_QUALITY}p stream...{WuxiaTheme.RESET}")
        
        try:
            # Step 1: Fetch the episode page
            r = requests.get(url, headers=Config.HEADERS, timeout=15)
            html = r.text
            print(f"{WuxiaTheme.JADE}  📄 Fetched episode page ({len(html)} bytes){WuxiaTheme.RESET}")
            
            # Step 2: Look for Dailymotion embeds first
            dm_patterns = [
                r'geo\.dailymotion\.com/player/([^.]+)\.js["\'][^>]*data-video=["\']([^"\']+)["\']',
                r'geo\.dailymotion\.com/player/([^.]+)\.html\?video=([^"\'&\s]+)',
                r'dailymotion\.com/(?:video|embed)/([a-zA-Z0-9]+)'
            ]
            
            for pattern in dm_patterns:
                match = re.search(pattern, html)
                if match:
                    video_id = match.groups()[-1]  # Get video ID
                    print(f"{WuxiaTheme.JADE}  📺 Found Dailymotion video: {video_id}{WuxiaTheme.RESET}")
                    return CultivationEngine.extract_dailymotion_stream(video_id, url)
            
            # Step 3: Look for iframe embeds
            iframe_pattern = r'<iframe[^>]+src=["\']([^"\']+)["\'][^>]*>'
            iframe_match = re.search(iframe_pattern, html)
            if iframe_match:
                iframe_src = iframe_match.group(1)
                # Skip decoy iframes
                if any(skip in iframe_src.lower() for skip in ['bitcoin', 'crypto', 'ads', 'blogspot']):
                    print(f"{WuxiaTheme.RED}  ⚠ Skipping decoy iframe{WuxiaTheme.RESET}")
                else:
                    print(f"{WuxiaTheme.JADE}  🎬 Found iframe: {iframe_src[:50]}...{WuxiaTheme.RESET}")
                    return CultivationEngine.extract_from_iframe(iframe_src, url)
            
            # Step 4: Fallback to yt-dlp
            print(f"{WuxiaTheme.RED}  ⚠ No embeds found, trying yt-dlp fallback...{WuxiaTheme.RESET}")
            return CultivationEngine.fallback_ytdlp(url)
            
        except Exception as e:
            print(f"{WuxiaTheme.RED}  ⚠ Error: {e}{WuxiaTheme.RESET}")
            return url

    @staticmethod
    def extract_dailymotion_stream(video_id, referer):
        """Extract Dailymotion stream URL with 360p preference"""
        try:
            metadata_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"
            headers = {"Referer": referer, **Config.HEADERS}
            meta = requests.get(metadata_url, headers=headers, timeout=15).json()
            
            qualities = meta.get("qualities", {})
            # Try 360p first, then fall back to other qualities
            preferred_order = ["380", "360", "480", "240", "auto"]
            
            for q in preferred_order:
                if q in qualities:
                    for item in qualities[q]:
                        if item.get("type") == "application/x-mpegURL":
                            print(f"{WuxiaTheme.JADE}  ✓ Found {q}p Dailymotion stream{WuxiaTheme.RESET}")
                            return item.get("url")
            
            # Ultimate fallback to auto
            if "auto" in qualities:
                for item in qualities["auto"]:
                    if item.get("type") == "application/x-mpegURL":
                        print(f"{WuxiaTheme.JADE}  ✓ Found auto Dailymotion stream{WuxiaTheme.RESET}")
                        return item.get("url")
            
            print(f"{WuxiaTheme.RED}  ⚠ No Dailymotion stream found{WuxiaTheme.RESET}")
            return referer
            
        except Exception as e:
            print(f"{WuxiaTheme.RED}  ⚠ Dailymotion extraction failed: {e}{WuxiaTheme.RESET}")
            return referer

    @staticmethod
    def extract_from_iframe(iframe_src, referer_url):
        """Extract stream URL from iframe page"""
        try:
            # Make absolute URL if needed
            if not iframe_src.startswith("http"):
                from urllib.parse import urljoin
                iframe_src = urljoin(referer_url, iframe_src)
            
            # Fetch iframe content
            headers = {"Referer": referer_url, **Config.HEADERS}
            r = requests.get(iframe_src, headers=headers, timeout=10)
            iframe_html = r.text
            
            # Look for stream URLs in JavaScript
            stream_patterns = [
                r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'file\s*:\s*["\']([^"\']+\.mp4[^"\']*)["\']',
                r'["\']([^"\']+\.mp4[^"\']*)["\']',
            ]
            
            for pattern in stream_patterns:
                matches = re.findall(pattern, iframe_html, re.IGNORECASE)
                for match in matches:
                    if match.startswith("http") and len(match) > 20:
                        print(f"{WuxiaTheme.JADE}  ✓ Found stream in iframe{WuxiaTheme.RESET}")
                        return match
            
            # Check for Dailymotion in iframe
            dm_patterns = [
                r'geo\.dailymotion\.com/player/([^.]+)\.js["\'][^>]*data-video=["\']([^"\']+)["\']',
                r'geo\.dailymotion\.com/player/([^.]+)\.html\?video=([^"\'&\s]+)',
                r'dailymotion\.com/(?:video|embed)/([a-zA-Z0-9]+)'
            ]
            
            for pattern in dm_patterns:
                match = re.search(pattern, iframe_html)
                if match:
                    video_id = match.groups()[-1]
                    print(f"{WuxiaTheme.JADE}  📺 Found Dailymotion in iframe: {video_id}{WuxiaTheme.RESET}")
                    return CultivationEngine.extract_dailymotion_stream(video_id, iframe_src)
            
            print(f"{WuxiaTheme.RED}  ⚠ No stream found in iframe{WuxiaTheme.RESET}")
            return referer_url
            
        except Exception as e:
            print(f"{WuxiaTheme.RED}  ⚠ Iframe extraction failed: {e}{WuxiaTheme.RESET}")
            return referer_url

    @staticmethod
    def fallback_ytdlp(url):
        """Fallback to yt-dlp extraction"""
        try:
            cmd = [
                "yt-dlp", "-g", 
                "-f", f"best[height<={DEFAULT_QUALITY}]/worst",
                "--no-check-certificate", 
                "--socket-timeout", "15", 
                "--user-agent", Config.HEADERS["User-Agent"], 
                url
            ]
            result = subprocess.run(
                cmd,
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                streams = result.stdout.strip().split('\n')
                for stream in streams:
                    if stream and ('m3u8' in stream or 'mp4' in stream):
                        print(f"{WuxiaTheme.JADE}  ✓ yt-dlp found stream{WuxiaTheme.RESET}")
                        return stream
                if streams:
                    print(f"{WuxiaTheme.JADE}  ✓ yt-dlp fallback{WuxiaTheme.RESET}")
                    return streams[0]
            
            print(f"{WuxiaTheme.RED}  ⚠ yt-dlp failed completely{WuxiaTheme.RESET}")
            return url
            
        except Exception as e:
            print(f"{WuxiaTheme.RED}  ⚠ yt-dlp fallback failed: {e}{WuxiaTheme.RESET}")
            return url

    @staticmethod
    def fallback_extract(url):
        """Fallback extraction for Dailymotion embeds with 360p preference"""
        try:
            r = requests.get(url, headers=Config.HEADERS, timeout=15)
            html = r.text
            
            dm_match = re.search(r'data-video=["\']([^"\']+)["\']', html)
            if dm_match:
                video_id = dm_match.group(1)
                print(f"{WuxiaTheme.JADE}  📺 Found Dailymotion: {video_id}{WuxiaTheme.RESET}")
                
                meta_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"
                meta = requests.get(meta_url, headers=Config.HEADERS, timeout=15).json()
                
                qualities = meta.get("qualities", {})
                
                # Try 360p first, then fall back to other qualities
                preferred_order = ["380", "360", "480", "240", "auto"]
                for q in preferred_order:
                    if q in qualities:
                        for item in qualities[q]:
                            if item.get("type") == "application/x-mpegURL":
                                print(f"{WuxiaTheme.JADE}  ✓ Using {q}p stream{WuxiaTheme.RESET}")
                                return item.get("url", url)
                
                # Ultimate fallback
                if "auto" in qualities:
                    for item in qualities["auto"]:
                        if item.get("type") == "application/x-mpegURL":
                            return item.get("url", url)
            return url
        except:
            return url

    @staticmethod
    def detect_os():
        """Detect operating system (ani-cli style)"""
        import platform
        uname = platform.uname()
        system_info = f"{uname.system} {uname.release}".lower()
        
        if "android" in system_info or os.path.exists("/data/data/com.termux"):
            return "android"
        elif "ish" in system_info or os.path.exists("/proc/ish"):
            return "ish"  # iOS iSH
        else:
            return "linux"

    @staticmethod
    def cast_intent(video_url, title="Donghua", referer=None):
        """Launch video in player (ani-cli style)"""
        os_type = CultivationEngine.detect_os()
        sanitized_url = video_url.replace(" ", "%20")
        
        if os_type == "android":
            print(f"{WuxiaTheme.GOLD}  ⚡ Launching Android Player...{WuxiaTheme.RESET}")
            
            # ani-cli style: Try MPV first, then VLC, then MX Player, then generic
            players = [
                # MPV for Android (ani-cli default)
                f"am start --user 0 -a android.intent.action.VIEW -d '{sanitized_url}' -n is.xyz.mpv/.MPVActivity",
                # VLC for Android (with title extra)
                f"am start --user 0 -a android.intent.action.VIEW -d '{sanitized_url}' -n org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity -e 'title' '{title}'",
                # MX Player
                f"am start --user 0 -a android.intent.action.VIEW -d '{sanitized_url}' -n com.mxtech.videoplayer.ad/com.mxtech.videoplayer.ActivityScreen -e 'title' '{title}'",
                # MX Player Pro
                f"am start --user 0 -a android.intent.action.VIEW -d '{sanitized_url}' -n com.mxtech.videoplayer.pro/com.mxtech.videoplayer.ActivityScreen -e 'title' '{title}'",
                # Generic intent (fallback)
                f"am start --user 0 -a android.intent.action.VIEW -d '{sanitized_url}' -t 'video/*'",
            ]
            
            for cmd in players:
                result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if result.returncode == 0:
                    print(f"{WuxiaTheme.JADE}  ✓ Player launched!{WuxiaTheme.RESET}")
                    return True
            
            # Ultimate fallback: termux-open-url
            print(f"{WuxiaTheme.SILVER}  🔄 Trying termux-open-url...{WuxiaTheme.RESET}")
            subprocess.run(f"termux-open-url '{sanitized_url}'", shell=True)
            return True
            
        elif os_type == "ish":
            # iOS iSH: Print clickable VLC link (ani-cli style)
            print(f"{WuxiaTheme.GOLD}  📱 iOS Detected - Tap the link below:{WuxiaTheme.RESET}")
            print(f"\033]8;;vlc://{sanitized_url}\a")
            print(f"{WuxiaTheme.JADE}~~~~~~~~~~~~~~~~~~~~{WuxiaTheme.RESET}")
            print(f"{WuxiaTheme.GOLD}~ Tap to open VLC ~{WuxiaTheme.RESET}")
            print(f"{WuxiaTheme.JADE}~~~~~~~~~~~~~~~~~~~~{WuxiaTheme.RESET}")
            print(f"\033]8;;\a")
            time.sleep(3)
            return True
            
        else:
            # Linux: Use mpv or vlc
            print(f"{WuxiaTheme.GOLD}  ⚡ Launching Desktop Player...{WuxiaTheme.RESET}")
            
            # Try mpv first
            try:
                subprocess.Popen(
                    ["mpv", f"--force-media-title={title}", video_url],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                print(f"{WuxiaTheme.JADE}  ✓ MPV launched!{WuxiaTheme.RESET}")
                return True
            except FileNotFoundError:
                pass
            
            # Try VLC
            try:
                refr_arg = f"--http-referrer={referer}" if referer else ""
                subprocess.Popen(
                    ["vlc", video_url, refr_arg, "--play-and-exit", f"--meta-title={title}"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                print(f"{WuxiaTheme.JADE}  ✓ VLC launched!{WuxiaTheme.RESET}")
                return True
            except FileNotFoundError:
                print(f"{WuxiaTheme.RED}  ✗ No player found! Install mpv or vlc{WuxiaTheme.RESET}")
                print(f"{WuxiaTheme.SILVER}  Stream URL: {video_url}{WuxiaTheme.RESET}")
                return False

class Scraper:
    @staticmethod
    def search(query):
        search_url = f"https://luciferdonghua.in/?s={query.replace(' ', '+')}"
        try:
            r = requests.get(search_url, headers=Config.HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            results = []
            
            seen = set()
            for article in soup.select("article.bs, div.bsx, div.bs"):
                a = article.find("a")
                if a and a.get('href') and a.get('href') not in seen:
                    seen.add(a.get('href'))
                    title = a.get('title') or a.text.strip()
                    results.append((title, a.get('href')))
            
            return results[:15]
        except Exception as e:
            print(f"{WuxiaTheme.RED}✗ Search failed: {e}{WuxiaTheme.RESET}")
            return []

    @staticmethod
    def get_all_episodes(series_url):
        try:
            r = requests.get(series_url, headers=Config.HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            episodes = []
            
            for li in soup.select(".eplister ul li, .episodelist ul li"):
                a = li.find("a")
                if not a:
                    continue
                    
                num_el = li.find(class_="epl-num") or li.find("span", class_="num")
                title_el = li.find(class_="epl-title") or li.find("span", class_="title")
                
                num = num_el.text.strip() if num_el else ""
                title = title_el.text.strip() if title_el else ""
                
                display_name = f"Episode {num}" if num else "Episode"
                if title:
                    display_name += f" - {title}"
                
                episodes.append((display_name, a.get('href')))
            
            if episodes:
                episodes.reverse()
            
            return episodes
        except Exception as e:
            print(f"{WuxiaTheme.RED}✗ Failed to fetch episodes: {e}{WuxiaTheme.RESET}")
            return []

# ============================================================================
# MAIN INTERFACE
# ============================================================================
def main():
    Config.setup()
    print(WuxiaTheme.banner())
    
    query = input(f"{WuxiaTheme.GOLD}📜 Enter Series Name: {WuxiaTheme.RESET}").strip()
    if not query:
        print(f"{WuxiaTheme.RED}✗ No query entered.{WuxiaTheme.RESET}")
        return

    print(f"{WuxiaTheme.JADE}  🔍 Searching...{WuxiaTheme.RESET}")
    results = Scraper.search(query)

    if not results:
        print(f"{WuxiaTheme.RED}✗ No results found.{WuxiaTheme.RESET}")
        return

    print(f"\n{WuxiaTheme.GOLD}━━━ SEARCH RESULTS ━━━{WuxiaTheme.RESET}")
    for i, (title, _) in enumerate(results, 1):
        print(f"  {WuxiaTheme.JADE}{i:2}.{WuxiaTheme.WHITE} {title[:55]}{'...' if len(title) > 55 else ''}")

    try:
        choice = input(f"\n{WuxiaTheme.GOLD}Select [1-{len(results)}]: {WuxiaTheme.RESET}").strip()
        if not choice:
            return
        choice = int(choice) - 1
        
        if not (0 <= choice < len(results)):
            print(f"{WuxiaTheme.RED}✗ Invalid selection.{WuxiaTheme.RESET}")
            return
            
        series_name, series_url = results[choice]
        
        print(f"\n{WuxiaTheme.JADE}  📜 Loading episodes...{WuxiaTheme.RESET}")
        episodes = Scraper.get_all_episodes(series_url)

        if not episodes:
            print(f"{WuxiaTheme.RED}✗ No episodes found.{WuxiaTheme.RESET}")
            return

        print(f"\n{WuxiaTheme.GOLD}━━━ {series_name[:40]} ━━━{WuxiaTheme.RESET}")
        print(f"{WuxiaTheme.SILVER}  Total: {len(episodes)} episodes | Quality: {DEFAULT_QUALITY}p{WuxiaTheme.RESET}\n")
        
        page_size = 20
        total_pages = (len(episodes) + page_size - 1) // page_size
        current_page = 0
        
        while True:
            start = current_page * page_size
            end = min(start + page_size, len(episodes))
            
            for i in range(start, end):
                name = episodes[i][0].split(" - ")[0]
                print(f"  {WuxiaTheme.SILVER}{i+1:03d}.{WuxiaTheme.RESET} {name}")
            
            if total_pages > 1:
                print(f"\n{WuxiaTheme.JADE}  Page {current_page + 1}/{total_pages} [n=next, p=prev]{WuxiaTheme.RESET}")
            
            ep_input = input(f"\n{WuxiaTheme.GOLD}Episode # (q=quit): {WuxiaTheme.RESET}").strip().lower()
            
            if ep_input == 'q':
                return
            elif ep_input == 'n' and current_page < total_pages - 1:
                current_page += 1
                continue
            elif ep_input == 'p' and current_page > 0:
                current_page -= 1
                continue
            
            try:
                ep_choice = int(ep_input) - 1
                if 0 <= ep_choice < len(episodes):
                    break
                print(f"{WuxiaTheme.RED}✗ Invalid number.{WuxiaTheme.RESET}")
            except ValueError:
                print(f"{WuxiaTheme.RED}✗ Enter a number.{WuxiaTheme.RESET}")
        
        ep_title = f"{series_name} - {episodes[ep_choice][0]}"
        print(f"\n{WuxiaTheme.JADE}  ⚔️ Loading {DEFAULT_QUALITY}p stream...{WuxiaTheme.RESET}")
        direct_link = CultivationEngine.get_direct_link(episodes[ep_choice][1])
        CultivationEngine.cast_intent(direct_link, title=ep_title)
        
        while True:
            next_input = input(f"\n{WuxiaTheme.GOLD}[n]ext, [r]eplay, [q]uit: {WuxiaTheme.RESET}").strip().lower()
            if next_input == 'n' and ep_choice < len(episodes) - 1:
                ep_choice += 1
                ep_title = f"{series_name} - {episodes[ep_choice][0]}"
                print(f"\n{WuxiaTheme.JADE}  ⚔️ Next: {episodes[ep_choice][0]}{WuxiaTheme.RESET}")
                direct_link = CultivationEngine.get_direct_link(episodes[ep_choice][1])
                CultivationEngine.cast_intent(direct_link, title=ep_title)
            elif next_input == 'r':
                CultivationEngine.cast_intent(direct_link, title=ep_title)
            elif next_input == 'q':
                break

    except (ValueError, IndexError) as e:
        print(f"{WuxiaTheme.RED}✗ Error: {e}{WuxiaTheme.RESET}")
    except KeyboardInterrupt:
        print(f"\n{WuxiaTheme.JADE}  👋 Farewell, cultivator!{WuxiaTheme.RESET}")

if __name__ == "__main__":
    main()
