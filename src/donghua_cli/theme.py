"""Wuxia-themed Rich styling for Donghua CLI.

Premium visual design with gradient-inspired color palette, layered panels,
and cinematic martial arts aesthetic.
"""

import random

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# ── Premium color palette ──────────────────────────────────────────────────

WUXIA_THEME = Theme(
    {
        # Core palette -- deep purples and electric blues
        "jade": "#5eead4",            # teal / primary accent
        "dark.jade": "#2dd4bf",       # darker teal
        "gold": "#fbbf24",            # warm amber gold
        "light.gold": "#fde68a",      # soft yellow
        "hot.gold": "#f59e0b",        # intense amber
        "martial.red": "#f43f5e",     # rose red -- errors / intense
        "hot.pink": "#ec4899",        # pink accent
        "purple": "#a78bfa",          # soft violet
        "deep.purple": "#7c3aed",     # deep violet accent
        "cyan": "#22d3ee",            # electric cyan
        "silver": "#e2e8f0",          # bright text
        "steel": "#94a3b8",           # secondary text
        "dim": "#64748b",             # muted text
        "ghost": "#475569",           # very muted
        "void": "#1e293b",            # dark background tint
        # Semantic
        "border": "#5eead4",
        "title": "bold #fbbf24",
        "subtitle": "#e2e8f0",
        "accent": "#fbbf24",
        "success": "#5eead4",
        "error": "#f43f5e",
        "warning": "#fbbf24",
        "info": "#e2e8f0",
    }
)

console = Console(theme=WUXIA_THEME)

# ── Wuxia flavour text ────────────────────────────────────────────────────

TECHNIQUES = [
    "Dragon Tail Sweep",
    "Phoenix Wing Strike",
    "Tiger Claw Attack",
    "Cloud Step Ascension",
    "Mountain Breaker Fist",
    "River Flow Counter",
    "Moonlight Cut",
    "Star Fall Descent",
    "Lotus Palm Strike",
    "Void Piercer",
    "Heavenly Sword Flash",
    "Iron Body Tempering",
    "Azure Dragon Roar",
    "Crimson Phoenix Dance",
    "Shadow Step Technique",
]

CULTIVATION_LEVELS = [
    "Qi Refining",
    "Foundation Establishment",
    "Golden Core",
    "Nascent Soul",
    "Divine Transformation",
    "Void Refinement",
    "Body Integration",
    "Tribulation",
    "Mahayana",
]


def random_technique() -> str:
    return random.choice(TECHNIQUES)


def random_level() -> str:
    return random.choice(CULTIVATION_LEVELS)


# ── Reusable display components ───────────────────────────────────────────


def banner() -> Panel:
    """The main application banner -- cinematic header."""
    import platform as _plat

    technique = random_technique()
    os_name = _plat.system()

    body = Text.assemble(
        ("\n", ""),
        ("         ", ""),
        ("\u6b66 \u4fa0 \u52a8 \u753b \u7ec8 \u7aef", "bold #fbbf24"),
        ("\n", ""),
        ("         ", ""),
        ("D O N G H U A   C L I", "bold #5eead4"),
        ("  ", ""),
        ("v3.1", "#94a3b8"),
        ("\n", ""),
        ("         ", ""),
        ("\u2500" * 36, "#334155"),
        ("\n\n", ""),
        ("         ", ""),
        ("\u2726 ", "#7c3aed"),
        (f"{technique}", "#a78bfa italic"),
        (" \u2726", "#7c3aed"),
        ("\n\n", ""),
        ("         ", ""),
        ("[", "#475569"),
        (" v3.1 ", "#f43f5e bold"),
        ("]", "#475569"),
        ("  ", ""),
        ("[", "#475569"),
        (f" {os_name} ", "#22d3ee"),
        ("]", "#475569"),
        ("  ", ""),
        ("[", "#475569"),
        (" Python 3.9+ ", "#a78bfa"),
        ("]", "#475569"),
        ("  ", ""),
        ("[", "#475569"),
        (" MIT ", "#5eead4"),
        ("]", "#475569"),
        ("\n\n", ""),
        ("         ", ""),
        ("\U0001f409", ""),
        ("  Enter the realm of immortal cultivation  ", "#64748b italic"),
        ("\U0001f409", ""),
    )

    return Panel(
        body,
        border_style="#334155",
        padding=(0, 0),
        width=72,
        title="[bold #5eead4]\u2726 DONGHUA CLI \u2726[/]",
        subtitle="[#475569]\u2500\u2500 Stream \u00b7 Download \u00b7 Cultivate \u2500\u2500[/]",
    )


def section_header(label: str, title: str, subtitle: str = "") -> None:
    """Print a section header with gradient-style treatment."""
    console.print()
    bar = "\u2500" * 3
    console.print(f"  [#475569]{bar}[/] [bold #a78bfa]{label.upper()}[/] [#475569]{bar}[/]")
    console.print(f"  [bold #fbbf24]{title}[/]")
    if subtitle:
        console.print(f"  [#64748b]{subtitle}[/]")
    console.print()


def divider() -> None:
    """Ornamental section divider."""
    left = "\u2500" * 22
    right = "\u2500" * 22
    console.print(f"\n  [#334155]{left}[/] [#7c3aed]\u2726[/] [#334155]{right}[/]\n")


def status(style: str, message: str) -> None:
    """Print a status line with colored icons."""
    icons = {
        "success": "[#5eead4]\u2713[/]",
        "error": "[#f43f5e]\u2717[/]",
        "warning": "[#fbbf24]\u26a0[/]",
        "info": "[#94a3b8]\u25cb[/]",
        "loading": "[#a78bfa]\u27f3[/]",
    }
    icon = icons.get(style, icons["info"])
    console.print(f"  {icon} {message}")


def prompt_text(label: str = "Enter command") -> str:
    """Return a styled prompt string for input()."""
    return f"\n  [#7c3aed]\u25b8[/] [bold #fbbf24]{label}[/] [#475569]\u00bb[/] "


def tip_box(title: str, content: str, style: str = "jade") -> Panel:
    """An info/tip panel."""
    border = "#5eead4" if style == "jade" else "#fbbf24"
    icon = "\u25cb" if style == "jade" else "\u26a0\ufe0f"
    return Panel(
        f"  {icon} [silver]{content}[/]",
        title=f"[bold {border}]{title}[/]",
        border_style="#334155",
        width=68,
        padding=(0, 1),
    )


def now_playing_panel(title: str, episode: int, total: int) -> Panel:
    """The now-playing display -- cinematic style."""
    level = random_level()
    body = Text.assemble(
        ("\n", ""),
        ("  ", ""),
        ("\u25b6 ", "#f43f5e"),
        ("NOW PLAYING", "#f43f5e bold"),
        ("\n", ""),
        ("  ", ""),
        ("\u2500" * 40, "#334155"),
        ("\n\n", ""),
        ("  ", ""),
        ("\u2726 ", "#7c3aed"),
        (f"{level}", "#a78bfa"),
        (" \u2726", "#7c3aed"),
        ("\n\n", ""),
        ("  ", ""),
        (f"{title[:56]}", "bold #fbbf24"),
        ("\n", ""),
        ("  Episode ", "#94a3b8"),
        (f"{episode:03d}", "#5eead4 bold"),
        (" / ", "#475569"),
        (f"{total:03d}", "#94a3b8"),
        ("  ", ""),
        ("\u2500" * 5, "#334155"),
        ("  ", ""),
        (_progress_bar_small(episode, total), ""),
        ("\n", ""),
    )
    return Panel(
        body,
        border_style="#5eead4",
        width=64,
        padding=(0, 1),
        title="[bold #5eead4]\u2726[/]",
        subtitle="[#475569]\u2500 cultivation in progress \u2500[/]",
    )


def _progress_bar_small(current: int, total: int) -> str:
    """Mini progress bar for now-playing."""
    width = 12
    filled = int(width * current / max(total, 1))
    return f"[#5eead4]{'━' * filled}[/][#334155]{'━' * (width - filled)}[/]"


def episode_table(
    episodes: list,
    start: int,
    end: int,
    page: int,
    total_pages: int,
    extract_num,
) -> Table:
    """Build a Rich table of episodes for a given page slice."""
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        expand=False,
        min_width=62,
    )
    table.add_column("#", style="#94a3b8", width=5, justify="right")
    table.add_column("", width=2)
    table.add_column("Episode", style="white", min_width=50)

    for i in range(start, end):
        ep_title, ep_url = episodes[i]
        ep_num = extract_num(ep_title, ep_url)
        label = f"Episode {ep_num}" if ep_num < 999999 else f"Episode {i + 1}"
        table.add_row(
            f"[#64748b]{i + 1}[/]",
            "[#475569]\u25b8[/]",
            f"[#e2e8f0]{label}[/]",
        )

    return table


def search_results_table(results: list) -> Table:
    """Build a Rich table of search results."""
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        expand=False,
        min_width=62,
    )
    table.add_column("#", style="#fbbf24", width=5, justify="right")
    table.add_column("", width=2)
    table.add_column("Title", style="white", min_width=50, max_width=55)

    for i, (title, _) in enumerate(results, 1):
        display = title[:55] + "\u2026" if len(title) > 55 else title
        table.add_row(str(i), "[#475569]\u25b8[/]", display)

    return table


def playback_controls(current: int, total: int) -> Panel:
    """Playback controls panel -- compact and clean."""
    def _key(key: str, desc: str, enabled: bool = True) -> str:
        if enabled:
            return f"  [bold #fbbf24]\\[{key}][/] [#e2e8f0]{desc}[/]"
        return f"  [#334155]\\[{key}][/] [#475569]{desc}[/]"

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
        title="[#5eead4]Controls[/]",
        border_style="#334155",
        width=50,
        padding=(0, 1),
    )


def source_table() -> Table:
    """Source selection table."""
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        expand=False,
    )
    table.add_column("Key", style="#fbbf24 bold", width=8)
    table.add_column("", width=2)
    table.add_column("Name", style="#e2e8f0", width=24)
    table.add_column("Desc", style="#64748b", width=24)

    table.add_row("[LD]", "[#475569]\u25b8[/]", "LuciferDonghua", "Primary source")
    table.add_row("[AX]", "[#475569]\u25b8[/]", "AnimeXin", "Alternative source")
    table.add_row("[BOTH]", "[#475569]\u25b8[/]", "Both Realms", "Maximum coverage")

    return table


def selection_help_table(total_episodes: int, has_pages: bool) -> Panel:
    """Episode selection help panel."""
    rows = [
        "  [bold #fbbf24]\\[1-5,8,10-12][/]  [#94a3b8]Select specific episodes[/]",
        "  [bold #fbbf24]\\[all][/]          [#94a3b8]Select all episodes[/]",
        "  [bold #fbbf24]\\[number][/]       [#94a3b8]Select single episode[/]",
    ]
    if has_pages:
        rows.append("  [bold #fbbf24]\\[n/p][/]          [#94a3b8]Navigate pages[/]")

    return Panel(
        "\n".join(rows),
        title="[#5eead4]Selection[/]",
        border_style="#334155",
        width=56,
        padding=(0, 1),
    )


def method_choice_panel() -> Panel:
    """Stream or download choice panel."""
    body = (
        "\n"
        "  [bold #fbbf24]\\[P][/]  [#5eead4]\u25b6[/]  [bold #e2e8f0]Stream episodes[/]\n"
        "       [#64748b]Watch instantly with MPV[/]\n\n"
        "  [bold #fbbf24]\\[D][/]  [#a78bfa]\u2b07[/]  [bold #e2e8f0]Download episodes[/]\n"
        "       [#64748b]Save for offline viewing[/]\n"
    )
    return Panel(
        body,
        title="[bold #fbbf24]Choose Your Path[/]",
        border_style="#334155",
        width=56,
        padding=(0, 1),
    )


def feature_cards() -> None:
    """Display feature showcase with styled rows."""
    features = [
        ("[#f43f5e]\u25cf[/]", "Multi-Source", "5 servers searched simultaneously"),
        ("[#fbbf24]\u25cf[/]", "Lightning Fast", "Preloading + stream cache"),
        ("[#5eead4]\u25cf[/]", "Smart Downloads", "Parallel via yt-dlp + ffmpeg"),
        ("[#a78bfa]\u25cf[/]", "Cross-Platform", "Linux / Windows / macOS / Android"),
        ("[#22d3ee]\u25cf[/]", "Smart Search", "Fuzzy match across all sources"),
        ("[#ec4899]\u25cf[/]", "Auto Fallback", "Seamless server switching"),
    ]

    for dot, title, desc in features:
        console.print(f"  {dot}  [bold #e2e8f0]{title:<20}[/] [#64748b]{desc}[/]")


def progress_text(current: int, total: int, width: int = 20) -> str:
    """Text-based progress indicator."""
    filled = int(width * current / max(total, 1))
    bar = f"[#5eead4]{'━' * filled}[/][#334155]{'━' * (width - filled)}[/]"
    return f"{bar} [#fbbf24]{current}[/][#475569]/[/][#94a3b8]{total}[/]"


def farewell() -> None:
    """Exit message."""
    divider()
    console.print("  [#7c3aed]\u2726[/] [bold #fbbf24]Farewell, Young Master[/] [#7c3aed]\u2726[/]")
    status("success", "May your cultivation reach new heights")
    console.print()
