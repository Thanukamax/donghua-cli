"""H-Donghua source plugin.

Re-pointed from the dead ``h-donghua.xyz`` (its TLS handshake now fails
outright) to ``h-donghua.com``, which is live. The new site is a *custom*
WordPress theme, not the shared AnimeStream one — search + series pages parse
fine, but the episode list is populated client-side (only the latest episode
is in the static HTML under ``.hd-episodes-grid``; the rest load via an
admin-ajax/wp-json call we haven't reverse-engineered yet).

That partial episode coverage is harmless in practice: episodes are merged
across every source, so the other providers supply the full run and hd just
contributes an extra live mirror for whatever it can see. Restoring hd here is
still strictly better than the previous TLS crash, which contributed nothing.

Full listing — investigated 2026-07-05, NO clean endpoint exists (don't re-chase):
  * The ``episode`` post type has **no taxonomy and no meta** linking an episode
    to its ``anime`` — ``/wp-json/wp/v2/types/episode`` reports ``taxonomies:
    []`` and an episode's ``meta`` is just ``{footnotes: ""}``. That's why the
    old ``?anime=<id>`` guess was ignored: there is nothing to filter on.
  * ``/wp-json/wp/v2/episode?search=<series>`` matches title/content tokens and
    returns only a handful (3 for a 160-ep series), not the run.
  * The theme ships a custom ``hdonghua/v1`` REST namespace, but it exposes only
    an anime *count* (``discord/anime/<id>`` → ``episodes: "182"``, a string
    count) and a **global** ``discord/latest-episodes`` feed (carries
    ``anime_id`` per item but accepts no per-anime filter and no real paging).
    No "episodes for anime X" route exists.
  * The anime page embeds only the latest ~3 episodes statically (grid is
    hydrated client-side); ``single.js`` issues no episode-list fetch.
URL reconstruction from the count is unreliable — the slug suffix is
inconsistent within a single series (…-episode-160-``subtitles`` vs
…-episode-158-``subtitle``) — so we deliberately don't guess.
"""

from donghua_cli.sources.base import Source


class HDonghua(Source):
    key = "hd"
    name = "H-Donghua"
    base_url = "https://h-donghua.com"

    # Still a slow upstream; keep generous budgets.
    search_timeout = 14
    episode_timeout = 16

    search_selectors = ("div.bsx", "article.bs", "div.bs")
    episode_selectors = (
        ".hd-episodes-grid a",  # new custom theme (best-effort: latest ep only)
        ".eplister a",
        ".episodelist a",
        ".epwrapper a",
        "#chapterlist a",
    )
