"""Source plugin system.

Each source is a subclass of Source that knows how to search a specific site
and extract episode lists. Adding a new source = adding one file here and
registering it in ALL_SOURCES.
"""

from donghua_cli import config
from donghua_cli.sources.base import Source, Episode, Series
from donghua_cli.sources.luciferdonghua import LuciferDonghua
from donghua_cli.sources.animexin import AnimeXin
from donghua_cli.sources.misterdonghua import MisterDonghua
from donghua_cli.sources.hdonghua import HDonghua
from donghua_cli.sources.lmanime import LMAnime


def _build_registry() -> list[Source]:
    sources: list[Source] = [
        LuciferDonghua(),
        AnimeXin(),
        MisterDonghua(),
        HDonghua(),
        LMAnime(),
    ]
    disabled = config.get_disabled_sources()
    for s in sources:
        if s.key in disabled:
            s.enabled = False
    return sources


# Registry: all available sources, ordered by priority (first = preferred).
ALL_SOURCES: list[Source] = _build_registry()


def get_source(key: str) -> Source | None:
    """Look up a source by its key."""
    for s in ALL_SOURCES:
        if s.key == key:
            return s
    return None


__all__ = ["Source", "Episode", "Series", "ALL_SOURCES", "get_source"]
