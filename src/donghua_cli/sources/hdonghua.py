"""H-Donghua source plugin.

AnimeStream WordPress theme. Slowest of the upstream sources — search alone
can take ~12s before the first byte.
"""

from donghua_cli.sources.base import Source


class HDonghua(Source):
    key = "hd"
    name = "H-Donghua"
    base_url = "https://h-donghua.xyz"

    # hd consistently needs ~12s to return search results.
    search_timeout = 14
    episode_timeout = 16

    search_selectors = ("div.bsx", "article.bs", "div.bs")
    episode_selectors = (
        ".eplister a",
        ".episodelist a",
        ".epwrapper a",
        "#chapterlist a",
    )
