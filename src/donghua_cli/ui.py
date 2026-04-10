"""User-facing interaction flows built on Rich.

Each method handles one interaction step: display + input + validation.
All visual output goes through theme.py components.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, List, Optional

from donghua_cli import theme
from donghua_cli.utils import clear_screen

if TYPE_CHECKING:
    from donghua_cli.sources.base import Episode

console = theme.console


def show_banner() -> None:
    clear_screen()
    console.print(theme.banner())
    console.print()


def select_from_list_with_badges(items: list[tuple[str, str]], title: str) -> int:
    """Display a numbered list with server badges and return the chosen index.

    items: list of (title, badges_string) -- e.g. ("Soul Land", "[MOVIE] [LD] [AX]")
    """
    theme.section_header(
        "Results",
        title,
        f"{len(items)} found across all servers",
    )

    from rich.table import Table
    from rich.panel import Panel

    table = Table(show_header=False, box=None, padding=(0, 1), expand=False, min_width=68)
    table.add_column("#", width=5, justify="right")
    table.add_column("", width=2)
    table.add_column("Title", min_width=42, max_width=46)
    table.add_column("Servers", width=16, justify="right")

    for i, (item_title, badges) in enumerate(items, 1):
        display = item_title[:46] + "\u2026" if len(item_title) > 46 else item_title
        table.add_row(
            f"[bold #fbbf24]{i}[/]",
            "[#475569]\u25b8[/]",
            f"[#e2e8f0]{display}[/]",
            f"[#64748b]{badges}[/]",
        )

    console.print(Panel(
        table,
        border_style="#334155",
        width=76,
        padding=(0, 1),
        title="[#5eead4]\u2726 Results \u2726[/]",
    ))

    while True:
        try:
            raw = console.input(theme.prompt_text(f"Select [1-{len(items)}]")).strip()
            if not raw:
                theme.status("warning", "Please enter a number")
                continue
            idx = int(raw) - 1
            if 0 <= idx < len(items):
                theme.status("success", f"Selected: {items[idx][0][:50]}")
                return idx
            theme.status("error", f"Out of range (1-{len(items)})")
        except ValueError:
            theme.status("error", "Enter a valid number")
        except KeyboardInterrupt:
            raise


def select_episodes_from_list(episodes: List[Episode]) -> List[Episode]:
    """Paginated episode browser with range/multi-select for Episode objects."""
    page = 1
    per_page = 20

    while True:
        clear_screen()
        show_banner()

        total_pages = (len(episodes) + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = min(start + per_page, len(episodes))

        theme.section_header(
            "Episodes",
            "Select Cultivation Techniques",
            f"Viewing {start + 1}-{end} of {len(episodes)} episodes",
        )

        from rich.table import Table
        from rich.panel import Panel

        table = Table(show_header=False, box=None, padding=(0, 1), expand=False, min_width=68)
        table.add_column("#", width=5, justify="right")
        table.add_column("", width=2)
        table.add_column("Episode", min_width=40, max_width=44)
        table.add_column("Servers", width=16, justify="right")

        for i in range(start, end):
            ep = episodes[i]
            label = f"Episode {ep.number}" if ep.number < 999999 else f"Episode {i + 1}"
            servers = " ".join(f"[{k.upper()}]" for k in ep.sources)
            table.add_row(
                f"[#94a3b8]{i + 1}[/]",
                "[#475569]\u25b8[/]",
                f"[#e2e8f0]{label}[/]",
                f"[#5eead4]{servers}[/]",
            )

        subtitle = f"[#64748b]Page {page}/{total_pages}[/]" if total_pages > 1 else None
        console.print(Panel(
            table,
            border_style="#334155",
            width=76,
            padding=(0, 1),
            subtitle=subtitle,
            title="[#5eead4]\u2726 Episodes \u2726[/]",
        ))

        if total_pages > 1:
            console.print(f"  [#94a3b8]Page[/] [bold #fbbf24]{page}[/][#475569]/[/][#94a3b8]{total_pages}[/]  {theme.progress_text(page, total_pages)}")
            console.print("  [#475569]\u25b8[/] [bold #fbbf24]\\[N][/][#94a3b8]ext[/] [#475569]|[/] [bold #fbbf24]\\[P][/][#94a3b8]rev[/]")

        console.print()
        console.print(theme.selection_help_table(len(episodes), total_pages > 1))

        try:
            raw = console.input(theme.prompt_text("Select episodes")).strip().lower()

            if raw == "n" and page < total_pages:
                page += 1
                continue
            if raw == "p" and page > 1:
                page -= 1
                continue
            if raw in ("", "all", "a"):
                return episodes

            selected: list[Episode] = []
            for part in raw.split(","):
                part = part.strip()
                if "-" in part:
                    lo, hi = map(int, part.split("-"))
                    if lo < 1 or hi > len(episodes) or lo > hi:
                        raise IndexError
                    selected.extend(episodes[lo - 1 : hi])
                else:
                    n = int(part)
                    if n < 1 or n > len(episodes):
                        raise IndexError
                    selected.append(episodes[n - 1])

            if selected:
                theme.status("success", f"Selected {len(selected)} episode(s)")
                return selected
            theme.status("error", "No episodes selected")
            time.sleep(1)

        except ValueError:
            theme.status("error", "Enter a number or range (e.g. 1-5,8)")
            time.sleep(1)
        except IndexError:
            theme.status("error", f"Out of range -- pick between 1 and {len(episodes)}")
            time.sleep(1)
        except KeyboardInterrupt:
            raise


def show_playback(title: str, current: int, total: int, server_name: str = "", sources: list[str] | None = None) -> None:
    """Display the now-playing panel with server info."""
    console.print(theme.now_playing_panel(title, current, total))
    if server_name:
        all_servers = ", ".join(s.upper() for s in (sources or []))
        console.print(f"  [#5eead4]\u25b8[/] [bold #e2e8f0]{server_name}[/]  [#475569]\u2502[/]  [#64748b]Available: {all_servers}[/]")
    console.print()
    console.print(theme.playback_controls(current, total))
    console.print()
    console.print("  [#64748b]Close MPV window or enter command to continue...[/]")


def choose_method() -> str:
    """Ask user to stream or download. Returns 'play' or 'download'."""
    theme.divider()
    theme.section_header(
        "Method",
        "Choose Your Path",
        "Stream or download selected episodes",
    )
    console.print(theme.method_choice_panel())

    raw = console.input(theme.prompt_text("Choose method [P]")).strip().lower()
    return "download" if raw == "d" else "play"


def ask_continue() -> bool:
    """Ask whether to start another session."""
    theme.divider()
    raw = console.input(theme.prompt_text("Continue cultivation? [Y/n]")).strip().lower()
    return raw not in ("n", "no")


def get_search_query() -> Optional[str]:
    """Prompt for a search query. Returns None if empty."""
    theme.section_header(
        "Search",
        "Find Your Next Donghua",
        "Searches across all servers simultaneously",
    )
    raw = console.input(theme.prompt_text("Search")).strip()
    return raw or None
