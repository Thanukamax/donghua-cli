"""LuciferDonghua source plugin."""

from donghua_cli.sources.base import Source


class LuciferDonghua(Source):
    key = "ld"
    name = "LuciferDonghua"
    base_url = "https://luciferdonghua.in"

    # ld responds quickly; default 8s search budget is plenty.
    search_selectors = ("article.bs",)
