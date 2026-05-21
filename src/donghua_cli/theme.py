"""Rich-based theming for Donghua CLI's classic mode.

Public API (consumed by ui.py / app.py / cli.py) is preserved:
console, banner(), section_header(), divider(), status(), prompt_text(),
tip_box(), now_playing_panel(), episode_table(), search_results_table(),
playback_controls(), source_table(), selection_help_table(),
method_choice_panel(), feature_cards(), progress_text(), farewell().

All colors come from palette.py. No inline hex.
"""

from __future__ import annotations

import random
from typing import Callable

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from donghua_cli import __version__
from donghua_cli.palette import GLYPH, PALETTE

# ── Color shorthands ──────────────────────────────────────────────────────

C_TEXT = PALETTE["text"]
C_MUTED = PALETTE["text_muted"]
C_FAINT = PALETTE["text_faint"]
C_GHOST = PALETTE["text_ghost"]
C_BORDER = PALETTE["border"]
C_SURFACE_ALT = PALETTE["surface_alt"]
C_ACCENT = PALETTE["accent"]
C_ACCENT_ALT = PALETTE["accent_alt"]
C_DANGER = PALETTE["danger"]

# Register tokens as named styles so callers can write [accent] / [muted] / etc.
WUXIA_THEME = Theme(
    {
        "text":         C_TEXT,
        "muted":        C_MUTED,
        "faint":        C_FAINT,
        "ghost":        C_GHOST,
        "accent":       C_ACCENT,
        "accent.bold":  f"bold {C_ACCENT}",
        "accent.alt":   C_ACCENT_ALT,
        "danger":       C_DANGER,
        # Legacy aliases — old callers used these names directly.
        "gold":         C_ACCENT,
        "light.gold":   C_ACCENT,
        "hot.gold":     C_ACCENT,
        "jade":         C_ACCENT_ALT,
        "dark.jade":    C_ACCENT_ALT,
        "silver":       C_TEXT,
        "steel":        C_MUTED,
        "dim":          C_FAINT,
        # Semantic
        "success":      C_ACCENT_ALT,
        "error":        C_DANGER,
        "warning":      C_ACCENT,
        "info":         C_TEXT,
        "title":        f"bold {C_ACCENT}",
        "subtitle":     C_TEXT,
        "border":       C_ACCENT_ALT,
    }
)

console = Console(theme=WUXIA_THEME)


# ── Wuxia flavour (curated, restrained) ───────────────────────────────────
# Used sparingly. Random per process, never per-render — so the eye anchors.

TECHNIQUES = (
    "Dragon Tail Sweep",
    "Phoenix Wing Strike",
    "Cloud Step Ascension",
    "Mountain Breaker Fist",
    "Moonlight Cut",
    "Lotus Palm Strike",
    "Heavenly Sword Flash",
    "Shadow Step Technique",
)

CULTIVATION_LEVELS = (
    "Qi Refining",
    "Foundation Establishment",
    "Golden Core",
    "Nascent Soul",
    "Divine Transformation",
    "Void Refinement",
    "Body Integration",
    "Tribulation",
    "Mahayana",
)

# Pin once per process. Banner technique never shuffles after import.
_SESSION_TECHNIQUE = random.choice(TECHNIQUES)


def random_technique() -> str:
    return _SESSION_TECHNIQUE


def random_level() -> str:
    """Deprecated — prefer level_for_episode(n). Kept for API stability."""
    return _SESSION_TECHNIQUE  # stable; just so callers don't churn


def level_for_episode(episode: int) -> str:
    """Deterministic level from episode number — progresses with watch."""
    return CULTIVATION_LEVELS[max(0, episode - 1) % len(CULTIVATION_LEVELS)]


# ── Reusable display components ───────────────────────────────────────────


def banner() -> Panel:
    """Application banner — quiet, single accent, real version."""
    import platform as _plat

    os_name = _plat.system()
    technique = _SESSION_TECHNIQUE

    body = Text.assemble(
        ("\n  ", ""),
        ("武 侠 动 画 终 端", f"bold {C_ACCENT}"),
        ("\n  ", ""),
        ("D O N G H U A   C L I", f"bold {C_ACCENT_ALT}"),
        ("   ", ""),
        (f"v{__version__}", C_MUTED),
        ("\n  ", ""),
        ("─" * 32, C_BORDER),
        ("\n  ", ""),
        (technique, f"italic {C_MUTED}"),
        ("\n  ", ""),
        (f"{os_name} · Python 3.9+ · MIT", C_FAINT),
        ("\n", ""),
    )

    return Panel(
        body,
        border_style=C_BORDER,
        padding=(0, 2),
        width=60,
        title=f"[bold {C_ACCENT_ALT}]Donghua CLI[/]",
        subtitle=f"[{C_GHOST}]Stream · Download · Cultivate[/]",
    )


def section_header(label: str, title: str, subtitle: str = "") -> None:
    console.print()
    bar = "─" * 3
    console.print(f"  [ghost]{bar}[/] [accent.alt]{label.upper()}[/] [ghost]{bar}[/]")
    console.print(f"  [accent.bold]{title}[/]")
    if subtitle:
        console.print(f"  [faint]{subtitle}[/]")
    console.print()


def divider() -> None:
    """Quiet horizontal rule. No ornament."""
    console.print(f"\n  [ghost]{'─' * 56}[/]\n")


def status(style: str, message: str) -> None:
    """Print a status line. Glyphs from the 5-glyph budget only."""
    icons = {
        "success": f"[accent.alt]{GLYPH['ok']}[/]",
        "error":   f"[danger]{GLYPH['fail']}[/]",
        "warning": f"[accent]{GLYPH['fail']}[/]",
        "info":    f"[muted]{GLYPH['pending']}[/]",
        "loading": f"[muted]{GLYPH['pending']}[/]",
    }
    icon = icons.get(style, icons["info"])
    console.print(f"  {icon} [text]{message}[/]")


def prompt_text(label: str = "Enter command") -> str:
    return f"\n  [accent.alt]›[/] [accent.bold]{label}[/] [ghost]»[/] "


def tip_box(title: str, content: str, style: str = "jade") -> Panel:
    border = C_ACCENT_ALT if style == "jade" else C_ACCENT
    return Panel(
        f"  [text]{content}[/]",
        title=f"[bold {border}]{title}[/]",
        border_style=C_BORDER,
        width=64,
        padding=(0, 1),
    )


def now_playing_panel(title: str, episode: int, total: int) -> Panel:
    """Compact Now Playing — one block, no theatre."""
    level = level_for_episode(episode)
    body = Text.assemble(
        ("\n  ", ""),
        (GLYPH["play"], C_ACCENT),
        ("  NOW PLAYING", f"bold {C_ACCENT}"),
        ("\n\n  ", ""),
        (title[:56], f"bold {C_TEXT}"),
        ("\n  ", ""),
        ("Episode ", C_MUTED),
        (f"{episode:03d}", f"bold {C_ACCENT_ALT}"),
        (" / ", C_GHOST),
        (f"{total:03d}", C_MUTED),
        ("   ", ""),
        (_progress_bar_small(episode, total), ""),
        ("\n  ", ""),
        (level, f"italic {C_FAINT}"),
        ("\n", ""),
    )
    return Panel(
        body,
        border_style=C_ACCENT_ALT,
        width=60,
        padding=(0, 1),
    )


def _progress_bar_small(current: int, total: int) -> str:
    width = 14
    filled = int(width * current / max(total, 1))
    return f"[accent.alt]{'━' * filled}[/][ghost]{'━' * (width - filled)}[/]"


def episode_table(
    episodes: list,
    start: int,
    end: int,
    page: int,
    total_pages: int,
    extract_num: Callable[..., int],
) -> Table:
    """Episode list for classic mode. Quiet, readable."""
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        expand=False,
        min_width=62,
    )
    table.add_column("#", style=C_MUTED, width=5, justify="right")
    table.add_column("", width=2)
    table.add_column("Episode", style="white", min_width=50)

    for i in range(start, end):
        ep_title, ep_url = episodes[i]
        ep_num = extract_num(ep_title, ep_url)
        label = f"Episode {ep_num}" if ep_num < 999999 else f"Episode {i + 1}"
        table.add_row(
            f"[faint]{i + 1}[/]",
            "[ghost]·[/]",
            f"[text]{label}[/]",
        )

    return table


def search_results_table(results: list) -> Table:
    """Search results for classic mode."""
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        expand=False,
        min_width=62,
    )
    table.add_column("#", style=C_ACCENT, width=5, justify="right")
    table.add_column("", width=2)
    table.add_column("Title", style="white", min_width=50, max_width=55)

    for i, (title, _) in enumerate(results, 1):
        display = title[:55] + "…" if len(title) > 55 else title
        table.add_row(str(i), "[ghost]·[/]", display)

    return table


def playback_controls(current: int, total: int) -> Panel:
    """Playback controls — compact, single accent for keys."""
    def _key(key: str, desc: str, enabled: bool = True) -> str:
        if enabled:
            return f"  [accent.bold]\\[{key}][/] [text]{desc}[/]"
        return f"  [border]\\[{key}][/] [ghost]{desc}[/]"

    rows = [
        _key("N", "Next", current < total),
        _key("P", "Prev", current > 1),
        _key("S", "Skip to #"),
        _key("R", "Replay"),
        _key("D", "Download"),
        _key("Q", "Quit"),
    ]

    return Panel(
        "\n".join(rows),
        title=f"[{C_ACCENT_ALT}]Controls[/]",
        border_style=C_BORDER,
        width=50,
        padding=(0, 1),
    )


def source_table() -> Table:
    """Live source listing. Reflects the actual ALL_SOURCES registry —
    no fake placeholders."""
    from donghua_cli.sources import ALL_SOURCES

    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        expand=False,
    )
    table.add_column("Key", style=f"bold {C_ACCENT}", width=8)
    table.add_column("", width=2)
    table.add_column("Name", style=C_TEXT, width=24)
    table.add_column("Status", style=C_FAINT, width=18)

    for src in ALL_SOURCES:
        status_label = "enabled" if getattr(src, "enabled", True) else "disabled"
        table.add_row(
            f"[{src.key.upper()}]",
            "[ghost]·[/]",
            src.name,
            status_label,
        )

    return table


def selection_help_table(total_episodes: int, has_pages: bool) -> Panel:
    rows = [
        "  [accent.bold]\\[1-5,8,10-12][/]  [muted]Select specific episodes[/]",
        "  [accent.bold]\\[all][/]          [muted]Select all episodes[/]",
        "  [accent.bold]\\[number][/]       [muted]Select single episode[/]",
    ]
    if has_pages:
        rows.append("  [accent.bold]\\[n/p][/]          [muted]Navigate pages[/]")

    return Panel(
        "\n".join(rows),
        title=f"[{C_ACCENT_ALT}]Selection[/]",
        border_style=C_BORDER,
        width=56,
        padding=(0, 1),
    )


def method_choice_panel() -> Panel:
    body = (
        "\n"
        f"  [accent.bold]\\[P][/]  [accent.alt]{GLYPH['play']}[/]  [bold text]Stream episodes[/]\n"
        "       [faint]Watch instantly with MPV[/]\n\n"
        f"  [accent.bold]\\[D][/]  [muted]↓[/]  [bold text]Download episodes[/]\n"
        "       [faint]Save for offline viewing[/]\n"
    )
    return Panel(
        body,
        title="[accent.bold]Choose Your Path[/]",
        border_style=C_BORDER,
        width=56,
        padding=(0, 1),
    )


def feature_cards() -> None:
    """Feature showcase. Claims match what the app actually does."""
    from donghua_cli.sources import ALL_SOURCES

    source_count = len(ALL_SOURCES)
    features = [
        ("Multi-Source",   f"{source_count} servers searched in parallel"),
        ("Lightning Fast", "Preloading + stream cache (<15s to play)"),
        ("Smart Downloads", "Parallel via yt-dlp + ffmpeg"),
        ("Cross-Platform", "Linux · Windows · macOS · Android"),
        ("Smart Search",   "Fuzzy match across all sources"),
        ("Auto Fallback",  "Seamless server switching"),
    ]

    for title, desc in features:
        console.print(f"  [accent.alt]·[/]  [bold text]{title:<20}[/] [faint]{desc}[/]")


def progress_text(current: int, total: int, width: int = 20) -> str:
    filled = int(width * current / max(total, 1))
    bar = f"[accent.alt]{'━' * filled}[/][ghost]{'━' * (width - filled)}[/]"
    return f"{bar} [accent]{current}[/][ghost]/[/][muted]{total}[/]"


def farewell() -> None:
    divider()
    console.print("  [accent.bold]Farewell, traveller.[/]")
    status("success", "May your cultivation reach new heights")
    console.print()
