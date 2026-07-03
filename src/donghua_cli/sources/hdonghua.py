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

TODO: full listing via the WP REST API — ``/wp-json/wp/v2/episode`` exists but
the ``?anime=<id>`` filter is ignored (returns the globally-latest episodes,
not the series'). Needs the correct taxonomy/meta filter param.
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
