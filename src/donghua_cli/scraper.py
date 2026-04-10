"""Unified search and episode resolution across all sources.

Searches all sources concurrently via thread pool, merges results by
fuzzy title matching, filters irrelevant results, and resolves episodes
with automatic server fallback.
"""

import logging
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from difflib import SequenceMatcher
from typing import List

from donghua_cli.sources import ALL_SOURCES, Source, Series, Episode
from donghua_cli.utils import extract_episode_number

log = logging.getLogger("donghua")

# Sources to skip during search (too slow or redundant).
# They're still used for episode fallback when a series URL exists.
# LD + AX cover ~95% of titles; MD/LM/HD add latency for marginal gain.
_SEARCH_SKIP = {"hd", "md", "lm"}


def _is_movie(title: str) -> bool:
    """Check if a title refers to a movie/film/special."""
    return bool(re.search(r"\b(Movie|Film|OVA|Special|Gekijouban)\b", title, re.IGNORECASE))


def _normalize_title(title: str) -> str:
    """Normalize a title for fuzzy comparison.

    Strips noise but PRESERVES the movie/series distinction -- that's handled
    separately in _titles_match so movies don't merge with series.
    """
    t = title.strip()
    # Strip noise suffixes
    t = re.sub(r"\s*(English\s+Sub(bed)?|Subbed|Dubbed|Sub|Dub)\s*$", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*[\[\(]\d{4}[\]\)]\s*$", "", t)       # [2024] or (2024)
    t = re.sub(r"\s*\|.*$", "", t)                         # | Chinese title
    t = re.sub(r"\s*\(?(Season|S)\s*\d+\)?", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*(THAI\s+DUB|DUB)\s*(VER\.?)?\s*$", "", t, flags=re.IGNORECASE)
    # Strip movie subtitle variations (so "Movie: Battle of Gods" merges with "Movie")
    t = re.sub(r"\s*[:–\-]\s*(Battle\s+of\s+(the\s+)?Gods|Remake|Director'?s?\s+Cut).*$", "", t, flags=re.IGNORECASE)
    # Strip bracket tags like [Xian Ni], (Temporary)
    t = re.sub(r"\s*[\[\(](Xian\s+Ni|[^)]{1,20})[\]\)]\s*$", "", t)
    t = re.sub(r"\s*\(Temporary\)\s*$", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def _titles_match(a: str, b: str, threshold: float = 0.82) -> bool:
    """Check if two titles are the same thing.

    Movies only merge with movies, series only merge with series.
    """
    # Don't merge a movie with a series
    a_movie = _is_movie(a)
    b_movie = _is_movie(b)
    if a_movie != b_movie:
        return False

    na = _normalize_title(a)
    nb = _normalize_title(b)
    if na == nb:
        return True
    if na in nb or nb in na:
        return True
    return SequenceMatcher(None, na, nb).ratio() >= threshold


def _is_relevant(title: str, query: str) -> bool:
    """Check if a search result is actually relevant to the query.

    Filters out garbage results that sources return for unrelated series.
    """
    q_words = set(query.lower().split())
    t_lower = title.lower()

    # At least half the query words must appear in the title
    matches = sum(1 for w in q_words if w in t_lower)
    if matches >= max(1, len(q_words) // 2):
        return True

    # Or the normalized titles are similar enough
    nq = _normalize_title(query)
    nt = _normalize_title(title)
    return SequenceMatcher(None, nq, nt).ratio() >= 0.5


# ── Unified search (truly concurrent via threads) ────────────────────────


def search_all(query: str) -> List[Series]:
    """Search all sources concurrently and merge results into unified Series list.

    Only searches the 2 fastest sources (LD + AX) for speed. The other sources
    are still used for episode fallback when a series URL exists.
    Hard deadline: 5s -- anything slower is dropped.
    """
    raw: list[tuple[str, str, str]] = []
    search_sources = [s for s in ALL_SOURCES if s.key not in _SEARCH_SKIP]

    with ThreadPoolExecutor(max_workers=len(search_sources)) as pool:
        futures = {
            pool.submit(_search_one, source, query): source
            for source in search_sources
        }
        try:
            for future in as_completed(futures, timeout=5):
                try:
                    raw.extend(future.result(timeout=0.1))
                except Exception:
                    pass
        except TimeoutError:
            for future in futures:
                if future.done():
                    try:
                        raw.extend(future.result(timeout=0))
                    except Exception:
                        pass
                else:
                    future.cancel()

    # Filter irrelevant results before merging
    filtered = [(sk, t, u) for sk, t, u in raw if _is_relevant(t, query)]
    log.debug("Search raw=%d filtered=%d for query='%s'", len(raw), len(filtered), query)

    return _merge_results(filtered)


def _search_one(source: Source, query: str) -> list[tuple[str, str, str]]:
    """Search a single source. Returns (source_key, title, url) tuples."""
    try:
        log.debug("Searching %s for '%s'", source.name, query)
        results = source.search(query)
        log.debug("%s returned %d results", source.name, len(results))
        return [(source.key, title, url) for title, url in results]
    except Exception as e:
        log.warning("Search failed on %s: %s", source.name, e)
        return []


def _merge_results(raw: list[tuple[str, str, str]]) -> List[Series]:
    """Merge raw results from multiple sources into deduplicated Series list."""
    merged: list[Series] = []

    for source_key, title, url in raw:
        matched = False
        for series in merged:
            if _titles_match(series.title, title):
                series.add_url(source_key, url)
                matched = True
                log.debug("Merged '%s' into '%s'", title, series.title)
                break

        if not matched:
            s = Series(title=title)
            s.add_url(source_key, url)
            merged.append(s)

    return merged[:20]


# ── Episode resolution with multi-source merging (concurrent) ────────────


def get_episodes(series: Series) -> List[Episode]:
    """Get episodes from all sources concurrently, merge by episode number."""
    from donghua_cli.sources import get_source

    all_raw: list[tuple[str, str, str]] = []

    with ThreadPoolExecutor(max_workers=max(len(series.urls), 1)) as pool:
        futures = {}
        for source_key, series_url in series.urls.items():
            source = get_source(source_key)
            if source:
                futures[pool.submit(source.get_episodes, series_url)] = source_key
                log.debug("Fetching episodes from %s: %s", source_key, series_url)

        for future in as_completed(futures):
            source_key = futures[future]
            try:
                eps = future.result(timeout=15)
                log.debug("%s returned %d episodes", source_key, len(eps))
                for title, url in eps:
                    all_raw.append((source_key, title, url))
            except Exception as e:
                log.warning("Episode fetch failed on %s: %s", source_key, e)

    return _merge_episodes(all_raw)


def _merge_episodes(raw: list[tuple[str, str, str]]) -> List[Episode]:
    """Merge episode lists from multiple sources by episode number."""
    by_number: dict[int, Episode] = {}

    for source_key, title, url in raw:
        num = extract_episode_number(title, url)

        if num in by_number:
            by_number[num].add_url(source_key, url)
        else:
            ep = Episode(number=num, title=title)
            ep.add_url(source_key, url)
            by_number[num] = ep

    return sorted(by_number.values(), key=lambda e: e.number)
