"""LMAnime source plugin.

Uses the AnimeStream WordPress theme. English subs, multiple qualities.
Note: series URLs don't use /anime/ prefix.
"""

from typing import List

from donghua_cli.sources.base import Source
from donghua_cli.utils import extract_episode_number, fetch_html, is_valid_episode_url


class LMAnime(Source):
    key = "lm"
    name = "LMAnime"
    base_url = "https://lmanime.com"

    _SEARCH_SELS = [".bs .bsx", "div.bsx", "article.bs", "div.bs"]
    _EP_SELECTORS = [".eplister a", ".episodelist a", "#chapterlist a"]

    def search(self, query: str) -> List[tuple[str, str]]:
        url = f"{self.base_url}/?s={query.replace(' ', '+')}"
        tree = fetch_html(url, timeout=4, fast=True)

        results: list[tuple[str, str]] = []
        seen: set[str] = set()

        nodes: list = []
        for sel in self._SEARCH_SELS:
            nodes = tree.css(sel)
            if nodes:
                break
        if not nodes:
            nodes = tree.css("a")

        for node in nodes[:15]:
            a = node if node.tag == "a" else node.css_first("a")
            if not a:
                continue
            href = a.attributes.get("href", "")
            if not href or href in seen:
                continue
            # LMAnime doesn't always use /anime/ -- filter out non-series pages
            if any(skip in href for skip in (
                "/genre", "/release", "/bookmark", "/dmca",
                "/privacy", "/help", "wp-content", "/page/", "/?s=",
            )):
                continue
            if not href.startswith(self.base_url):
                continue
            seen.add(href)
            title = a.attributes.get("title") or a.text(strip=True)
            if title and len(title) > 3:
                results.append((title, href))

        return results

    def get_episodes(self, series_url: str) -> List[tuple[str, str]]:
        tree = fetch_html(series_url, timeout=12)
        episodes: list[tuple[str, str]] = []
        seen_urls: set[str] = set()

        for sel in self._EP_SELECTORS:
            for a in tree.css(sel):
                if a.tag != "a":
                    continue
                href = a.attributes.get("href", "")
                if not is_valid_episode_url(href):
                    continue
                normalized = href.rstrip("/").split("?")[0].split("#")[0]
                if normalized in seen_urls:
                    continue
                seen_urls.add(normalized)

                title = a.text(strip=True)
                tl = title.lower()
                hl = href.lower()
                if any(kw in tl or kw in hl for kw in (
                    "episode", "ep-", "ep", "part-", "part", "pt-", "pt"
                )):
                    episodes.append((title, href))

        episodes.sort(key=lambda x: extract_episode_number(x[0], x[1]))
        return _dedup(episodes)


def _dedup(episodes: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[int] = set()
    out: list[tuple[str, str]] = []
    for title, url in episodes:
        n = extract_episode_number(title, url)
        if n not in seen:
            seen.add(n)
            out.append((title, url))
    return out
