"""Global configuration for Donghua CLI.

Loads user preferences from ~/.config/donghua-cli/config.toml if it exists,
falling back to sensible defaults. Platform is auto-detected.
"""

import os
import platform

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]


def _detect_platform() -> str:
    uname = platform.uname()
    info = f"{uname.system} {uname.release}".lower()
    if "android" in info or os.path.exists("/data/data/com.termux"):
        return "android"
    if "ish" in info or os.path.exists("/proc/ish"):
        return "ish"
    if uname.system == "Windows":
        return "windows"
    return "linux"


PLATFORM = _detect_platform()

# ── config file paths ────────────────────────────────────────────────────

if PLATFORM == "android":
    _CONFIG_DIR = os.path.expanduser("~/DonghuaCultivation")
    CACHE_DIR = os.path.join(_CONFIG_DIR, "cache")
elif PLATFORM == "windows":
    _CONFIG_DIR = os.path.expanduser("~/.donghua")
    CACHE_DIR = _CONFIG_DIR
else:
    _CONFIG_DIR = os.path.expanduser("~/.config/donghua-cli")
    CACHE_DIR = os.path.expanduser("~/.cache/donghua")

CONFIG_FILE = os.path.join(_CONFIG_DIR, "config.toml")
STREAM_CACHE_FILE = os.path.join(CACHE_DIR, "stream_cache.json")

# ── defaults ─────────────────────────────────────────────────────────────

DEFAULT_QUALITY = "720"
DEFAULT_QUALITY_MOBILE = "360"


def _default_download_dir() -> str:
    """Platform-native default download directory.

    Linux/Termux → ``~/Videos/Donghua``
    Windows → ``%USERPROFILE%\\Videos\\Donghua``
    macOS → ``~/Movies/Donghua``
    Android → ``~/storage/movies/Donghua`` when Termux storage is set up,
              else ``~/DonghuaCultivation/downloads``.
    """
    if PLATFORM == "windows":
        base = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        return os.path.normpath(os.path.join(base, "Videos", "Donghua"))
    if PLATFORM == "android":
        termux_storage = os.path.expanduser("~/storage/movies")
        if os.path.isdir(termux_storage):
            return os.path.join(termux_storage, "Donghua")
        return os.path.join(_CONFIG_DIR, "downloads")
    system = platform.uname().system
    if system == "Darwin":
        return os.path.normpath(os.path.expanduser("~/Movies/Donghua"))
    return os.path.normpath(os.path.expanduser("~/Videos/Donghua"))


DOWNLOAD_DIR = _default_download_dir()

# curl_cffi TLS-fingerprint impersonation target. "chrome" tracks the latest
# stable Chrome profile curl_cffi ships; override in config.toml if a site
# starts fingerprinting a specific build.
IMPERSONATE = "chrome"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://google.com",
    "Upgrade-Insecure-Requests": "1",
}

HEADERS_MOBILE = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ── user config loading ──────────────────────────────────────────────────

_user_config: dict = {}


def _load_user_config() -> dict:
    """Load config.toml if it exists. Returns empty dict on failure."""
    global _user_config
    if _user_config:
        return _user_config
    if tomllib is None or not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "rb") as f:
            _user_config = tomllib.load(f)
    except Exception:
        _user_config = {}
    return _user_config


def get_headers() -> dict:
    return HEADERS_MOBILE if PLATFORM == "android" else HEADERS


def get_quality() -> str:
    cfg = _load_user_config()
    custom = cfg.get("quality")
    if custom:
        return str(custom)
    return DEFAULT_QUALITY_MOBILE if PLATFORM == "android" else DEFAULT_QUALITY


def get_download_dir() -> str:
    cfg = _load_user_config()
    custom = cfg.get("download_dir")
    if custom:
        return os.path.normpath(os.path.expanduser(custom))
    return DOWNLOAD_DIR


def get_disabled_sources() -> set[str]:
    """Source keys the user has disabled via config.toml."""
    cfg = _load_user_config()
    raw = cfg.get("disabled_sources", [])
    if isinstance(raw, str):
        return {raw}
    return {str(k) for k in raw}


def get_auto_next() -> bool:
    """Whether to auto-advance to the next episode after MPV finishes one."""
    cfg = _load_user_config()
    return bool(cfg.get("auto_next", True))


def ensure_dirs():
    os.makedirs(CACHE_DIR, exist_ok=True)
    if PLATFORM != "android":
        os.makedirs(get_download_dir(), exist_ok=True)


def create_default_config() -> str:
    """Create a default config.toml if it doesn't exist. Returns the path."""
    if os.path.exists(CONFIG_FILE):
        return CONFIG_FILE
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write("""\
# Donghua CLI configuration
# Uncomment and modify values to override defaults.

# Default video quality (e.g. 360, 480, 720, 1080)
# quality = 720

# Download directory
# download_dir = "~/Videos/Donghua"
""")
    return CONFIG_FILE
