"""MisterDonghua source plugin.

Same AnimeStream WordPress theme as LuciferDonghua, but markedly slower
upstream — needs a higher search timeout.
"""

from donghua_cli.sources.base import Source


class MisterDonghua(Source):
    key = "md"
    name = "MisterDonghua"
    base_url = "https://misterdonghua.com"

    # md takes ~5s to respond to search; give it room.
    search_timeout = 10
    search_selectors = ("article.bs", "div.bsx", "div.bs")
