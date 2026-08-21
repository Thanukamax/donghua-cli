"""Unified search and episode resolution across all sources.

Searches all sources concurrently via thread pool, merges results by
fuzzy title matching, filters irrelevant results, and resolves episodes
with automatic server fallback.
"""

import logging
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from difflib import SequenceMatcher
from typing import Callable, List, Optional

from donghua_cli import health
from donghua_cli.sources import ALL_SOURCES, Source, Series, Episode
from donghua_cli.utils import extract_episode_number

log = logging.getLogger("donghua")

# Callback signature: (source_key, status, hit_count, elapsed_seconds)
# status ∈ {"pending", "alive", "dead", "timeout"}
ProgressCallback = Callable[[str, str, int, float], None]


def _is_movie(title: str) -> bool:
    """Check if a title refers to a movie/film/special."""
    return bool(re.search(r"\b(Movie|Film|OVA|Special|Gekijouban)\b", title, re.IGNORECASE))


_SEASON_RE = re.compile(r"\bseason\s*(\d+)\b", re.IGNORECASE)


def _normalize_title(title: str) -> str:
    """Normalize a title for fuzzy comparison.

    Strips noise but PRESERVES season info (so S1 and S5 stay distinct) and
    the movie/series distinction (handled in _titles_match).
    """
    t = title.strip()
    # Strip noise suffixes
    t = re.sub(r"\s*(English\s+Sub(bed)?|Subbed|Dubbed|Sub|Dub)\s*$", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*[\[\(]\d{4}[\]\)]\s*$", "", t)       # [2024] or (2024)
    t = re.sub(r"\s*\|.*$", "", t)                         # | Chinese title
    t = re.sub(r"\s*(THAI\s+DUB|DUB)\s*(VER\.?)?\s*$", "", t, flags=re.IGNORECASE)
    # Strip annotation suffixes that don't change identity ([ Temporary ], [ New ])
    t = re.sub(r"\s*[\[\(]\s*(Temporary|New)\s*[\]\)]\s*", " ", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*\(Temporary\)\s*$", "", t, flags=re.IGNORECASE)
    # Strip movie subtitle variations (so "Movie: Battle of Gods" merges with "Movie")
    t = re.sub(r"\s*[:–\-]\s*(Battle\s+of\s+(the\s+)?Gods|Remake|Director'?s?\s+Cut).*$", "", t, flags=re.IGNORECASE)
    # Strip bracket tags like [Xian Ni]
    t = re.sub(r"\s*[\[\(](Xian\s+Ni|[^)]{1,20})[\]\)]\s*$", "", t)
    # NORMALIZE season notation (do NOT strip): "Season 04" / "S 5" / "S5" → "season N"
    t = re.sub(r"\bS\s*(\d+)\b", lambda m: f"season {int(m.group(1))}", t, flags=re.IGNORECASE)
    t = re.sub(r"\bseason\s*0*(\d+)\b", lambda m: f"season {int(m.group(1))}", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def _season_of(normalized: str) -> Optional[int]:
    """Extract the season number from an already-normalized title, or None."""
    m = _SEASON_RE.search(normalized)
    return int(m.group(1)) if m else None


def _titles_match(a: str, b: str, threshold: float = 0.82) -> bool:
    """Check if two titles refer to the same season of the same series.

    Movies only merge with movies, series with series. Different seasons of
    the same series NEVER merge (a 0.97 string ratio between "season 4" and
    "season 5" otherwise leaks them together — that's how the BTTH bug hid
    Seasons 1–4).
    """
    if _is_movie(a) != _is_movie(b):
        return False

    na = _normalize_title(a)
    nb = _normalize_title(b)
    if na == nb:
        return True

    sa = _season_of(na)
    sb = _season_of(nb)

    if sa is not None and sb is not None:
        # Both have season markers — only merge same-season titles, then
        # require ratio match for the rest of the title.
        if sa != sb:
            return False
        return SequenceMatcher(None, na, nb).ratio() >= threshold

    if (sa is None) != (sb is None):
        # One side has a season marker, the other doesn't. Treat them as
        # distinct so a bare-title landing page doesn't swallow a numbered
        # season (or vice versa).
        return False

    # Neither has a season marker — substring/ratio is fine here.
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


def get_search_sources() -> list[Source]:
    """Return the sources eligible for search right now (enabled + healthy)."""
    return [s for s in ALL_SOURCES if s.enabled and health.is_healthy(s.key)]


def search_all(
    query: str,
    on_progress: Optional[ProgressCallback] = None,
) -> List[Series]:
    """Search every enabled, healthy source concurrently and merge results.

    Each source gets its own `search_timeout` budget (set on the Source class).
    The global deadline is the slowest source's budget plus a small buffer, so
    no participant is silently dropped just for being slow.

    If `on_progress` is provided it is invoked from worker threads with
    ``(source_key, status, hit_count, elapsed_seconds)`` each time a source
    transitions: once with ``"pending"`` at startup, then ``"alive"``,
    ``"dead"``, or ``"timeout"`` when it settles. Use it to drive live UI
    indicators.
    """
    import time

    from donghua_cli import cache

    # Serve repeat searches from cache — but only when nobody's driving the live
    # per-source progress UI (the TUI passes on_progress). A cache hit resolves
    # instantly and would leave those indicators unfired, so the live path always
    # re-scrapes; classic/direct mode gets the speed-up.
    if on_progress is None:
        cached = cache.get_search(query)
        if cached is not None:
            log.debug("Search cache hit for '%s' (%d results)", query, len(cached))
            return cached

    raw: list[tuple[str, str, str, str | None]] = []
    search_sources = get_search_sources()
    if not search_sources:
        log.warning("No healthy sources available for search")
        return []

    deadline = max(s.search_timeout for s in search_sources) + 2
    started = time.time()

    if on_progress is not None:
        for s in search_sources:
            on_progress(s.key, "pending", 0, 0.0)

    with ThreadPoolExecutor(max_workers=len(search_sources)) as pool:
        futures = {
            pool.submit(_search_one, source, query, on_progress, started): source
            for source in search_sources
        }
        try:
            for future in as_completed(futures, timeout=deadline):
                try:
                    raw.extend(future.result(timeout=0.1))
                except Exception:
                    pass
        except TimeoutError:
            slow = [futures[f].key for f in futures if not f.done()]
            if slow:
                log.info("Search deadline hit; dropping slow sources: %s", slow)
            for future in futures:
                if future.done():
                    try:
                        raw.extend(future.result(timeout=0))
                    except Exception:
                        pass
                else:
                    if on_progress is not None:
                        on_progress(
                            futures[future].key,
                            "timeout",
                            0,
                            time.time() - started,
                        )
                    future.cancel()

    # Filter irrelevant results before merging
    filtered = [(sk, t, u, c) for sk, t, u, c in raw if _is_relevant(t, query)]
    log.debug("Search raw=%d filtered=%d for query='%s'", len(raw), len(filtered), query)

    merged = _merge_results(filtered)
    if merged:
        cache.put_search(query, merged)
    return merged


def _search_one(
    source: Source,
    query: str,
    on_progress: Optional[ProgressCallback] = None,
    started: float = 0.0,
) -> list[tuple[str, str, str, str | None]]:
    """Search a single source. Returns (source_key, title, url, cover) tuples."""
    import time

    try:
        log.debug("Searching %s for '%s'", source.name, query)
        results = source.search_with_covers(query)
        log.debug("%s returned %d results", source.name, len(results))
        health.mark_alive(source.key)
        if on_progress is not None:
            on_progress(source.key, "alive", len(results), time.time() - started)
        return [(source.key, title, url, cover) for title, url, cover in results]
    except Exception as e:
        log.warning("Search failed on %s: %s", source.name, e)
        health.mark_dead(source.key, reason=str(e)[:120])
        if on_progress is not None:
            on_progress(source.key, "dead", 0, time.time() - started)
        return []


def _merge_results(raw: list[tuple[str, str, str, str | None]]) -> List[Series]:
    """Merge raw results from multiple sources into deduplicated Series list."""
    merged: list[Series] = []

    for source_key, title, url, cover in raw:
        matched = False
        for series in merged:
            if _titles_match(series.title, title):
                series.add_url(source_key, url)
                if cover and not series.cover_url:
                    series.cover_url = cover
                matched = True
                log.debug("Merged '%s' into '%s'", title, series.title)
                break

        if not matched:
            s = Series(title=title, cover_url=cover)
            s.add_url(source_key, url)
            merged.append(s)

    return merged[:20]


# ── Episode resolution with multi-source merging (concurrent) ────────────


def get_episodes(series: Series) -> List[Episode]:
    """Get episodes from all sources concurrently, merge by episode number."""
    from donghua_cli import cache
    from donghua_cli.sources import get_source

    cached = cache.get_episode_list(series)
    if cached is not None:
        log.debug("Episode-list cache hit for '%s' (%d eps)", series.title, len(cached))
        return cached

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
            source = get_source(source_key)
            timeout = source.episode_timeout if source else 15
            try:
                eps = future.result(timeout=timeout)
                log.debug("%s returned %d episodes", source_key, len(eps))
                for title, url in eps:
                    all_raw.append((source_key, title, url))
                if eps:
                    health.mark_alive(source_key)
            except Exception as e:
                log.warning("Episode fetch failed on %s: %s", source_key, e)
                health.mark_dead(source_key, reason=str(e)[:120])

    merged = _merge_episodes(all_raw)
    if merged:
        cache.put_episode_list(series, merged)
    return merged


def _merge_episodes(raw: list[tuple[str, str, str]]) -> List[Episode]:
    """Merge episode lists from multiple sources by episode number.

    Unknown-numbered episodes (sentinel 999999) are kept as distinct entries
    instead of being bucketed together — otherwise every page that didn't
    parse cleanly gets collapsed into one phantom "Episode 999999".
    """
    by_number: dict[int, Episode] = {}
    unknowns: list[Episode] = []

    for source_key, title, url in raw:
        num = extract_episode_number(title, url)

        if num >= 999999:
            ep = Episode(number=num, title=title)
            ep.add_url(source_key, url)
            unknowns.append(ep)
            continue

        if num in by_number:
            by_number[num].add_url(source_key, url)
        else:
            ep = Episode(number=num, title=title)
            ep.add_url(source_key, url)
            by_number[num] = ep

    known = sorted(by_number.values(), key=lambda e: e.number)
    return known + unknowns
