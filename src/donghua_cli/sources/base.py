"""Abstract base for source plugins."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Episode:
    """A single episode, potentially available from multiple sources."""

    number: int  # parsed episode number (999999 = unknown)
    title: str  # display title
    urls: dict[str, str] = field(default_factory=dict)  # source_key -> episode_page_url

    def add_url(self, source_key: str, url: str) -> None:
        self.urls[source_key] = url

    @property
    def primary_url(self) -> str:
        """First available URL."""
        return next(iter(self.urls.values()))

    @property
    def sources(self) -> list[str]:
        return list(self.urls.keys())


@dataclass
class Series:
    """A series found across one or more sources."""

    title: str  # canonical display title
    urls: dict[str, str] = field(default_factory=dict)  # source_key -> series_page_url

    def add_url(self, source_key: str, url: str) -> None:
        self.urls[source_key] = url

    @property
    def sources(self) -> list[str]:
        return list(self.urls.keys())


class Source:
    """Base class for all source plugins.

    Subclasses must implement:
      - search(query) -> list of (title, url) tuples
      - get_episodes(series_url) -> list of (title, url) tuples
    """

    key: str = ""  # short identifier, e.g. "ld"
    name: str = ""  # display name, e.g. "LuciferDonghua"
    base_url: str = ""

    def search(self, query: str) -> List[tuple[str, str]]:
        """Search for series. Returns [(title, url), ...]."""
        raise NotImplementedError

    def get_episodes(self, series_url: str) -> List[tuple[str, str]]:
        """Get episode list for a series. Returns [(title, url), ...]."""
        raise NotImplementedError
