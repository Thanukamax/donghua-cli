"""Abstract base for source plugins.

The base implements the shared search/episode-fetch scaffolding so that each
concrete source plugin only declares its selectors and a tiny link filter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

EP_KEYWORDS = ("episode", "ep-", "ep", "part-", "part", "pt-", "pt")


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
    cover_url: str | None = None  # poster image, populated when available

    def add_url(self, source_key: str, url: str) -> None:
        self.urls[source_key] = url

    @property
    def sources(self) -> list[str]:
        return list(self.urls.keys())


class Source:
    """Base class for all source plugins.

    Subclasses customize the scraping behavior by overriding:
      - key / name / base_url (required)
      - search_timeout / episode_timeout (per-source HTTP budgets)
      - search_selectors (CSS selectors for the search result list)
      - episode_selectors (CSS selectors for episode anchors on a series page)
      - _is_series_link(href) (decide which anchors are real series pages)

    Override `search()` or `get_episodes()` directly only if the templated
    behavior is genuinely not enough.
    """

    key: str = ""
    name: str = ""
    base_url: str = ""

    # Per-source HTTP budgets (seconds). Slow upstreams override these.
    search_timeout: int = 8
    episode_timeout: int = 12

    # Default participation; user config can override per source.
    enabled: bool = True

    # CSS selectors tried in order until one returns nodes.
    search_selectors: tuple[str, ...] = ("article.bs", "div.bsx", "div.bs")
    episode_selectors: tuple[str, ...] = (
        ".eplister a",
        ".episodelist a",
        "#chapterlist a",
        "li a",
    )

    # Skip these anchor types entirely during search-result parsing.
    _skip_url_fragments: tuple[str, ...] = ()
    # Minimum title length to accept a search result.
    _min_title_len: int = 1

    def search_url(self, query: str) -> str:
        """Build the search URL. Default = WordPress `?s=` query."""
        return f"{self.base_url}/?s={query.replace(' ', '+')}"

    def _is_series_link(self, href: str) -> bool:
        """Decide whether a href looks like a real series page.

        Default rule: anchor is on `base_url` and contains `/anime/`.
        Override for sites that use bare paths.
        """
        if not href.startswith(self.base_url):
            return False
        if any(skip in href for skip in self._skip_url_fragments):
            return False
        return "/anime/" in href

    def search(self, query: str) -> List[tuple[str, str]]:
        """Search for series. Returns [(title, url), ...]."""
        return [(title, url) for title, url, _cover in self.search_with_covers(query)]

    def search_with_covers(self, query: str) -> List[tuple[str, str, str | None]]:
        """Search and also extract poster URLs when present.

        Returns ``[(title, url, cover_url), ...]``. ``cover_url`` is ``None``
        when no ``<img>`` was found inside the result card.
        """
        from donghua_cli.utils import fetch_html

        tree = fetch_html(self.search_url(query), timeout=self.search_timeout, fast=True)

        nodes: list = []
        for sel in self.search_selectors:
            nodes = tree.css(sel)
            if nodes:
                break
        if not nodes:
            nodes = tree.css("a")

        results: list[tuple[str, str, str | None]] = []
        seen: set[str] = set()
        for node in nodes[:15]:
            a = node if node.tag == "a" else node.css_first("a")
            if not a:
                continue
            href = a.attributes.get("href", "") or ""
            if not href or href in seen:
                continue
            if not self._is_series_link(href):
                continue
            seen.add(href)
            title = a.attributes.get("title") or a.text(strip=True)
            if not title or len(title) < self._min_title_len:
                continue

            cover = None
            if node.tag != "a":
                img = node.css_first("img")
                if img is not None:
                    cover = (
                        img.attributes.get("data-src")
                        or img.attributes.get("data-lazy-src")
                        or img.attributes.get("src")
                    )
            results.append((title, href, cover))

        return results

    def get_episodes(self, series_url: str) -> List[tuple[str, str]]:
        """Get episode list for a series. Returns [(title, url), ...]."""
        from donghua_cli.utils import (
            extract_episode_number,
            fetch_html,
            is_valid_episode_url,
        )

        tree = fetch_html(series_url, timeout=self.episode_timeout)
        episodes: list[tuple[str, str]] = []
        seen_urls: set[str] = set()

        for sel in self.episode_selectors:
            for a in tree.css(sel):
                if a.tag != "a":
                    continue
                href = a.attributes.get("href", "") or ""
                if not is_valid_episode_url(href):
                    continue
                normalized = href.rstrip("/").split("?")[0].split("#")[0]
                if normalized in seen_urls:
                    continue
                seen_urls.add(normalized)

                title = a.text(strip=True)
                tl = title.lower()
                hl = href.lower()
                if any(kw in tl or kw in hl for kw in EP_KEYWORDS):
                    episodes.append((title, href))

        episodes.sort(key=lambda x: extract_episode_number(x[0], x[1]))
        return self.dedup_episodes(episodes)

    @staticmethod
    def dedup_episodes(episodes: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """Drop episodes that share an extracted number with an earlier entry."""
        from donghua_cli.utils import extract_episode_number

        seen: set[int] = set()
        out: list[tuple[str, str]] = []
        for title, url in episodes:
            n = extract_episode_number(title, url)
            if n not in seen:
                seen.add(n)
                out.append((title, url))
        return out
