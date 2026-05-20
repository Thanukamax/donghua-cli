"""LMAnime source plugin.

AnimeStream WordPress theme. English subs, multiple qualities.
Series URLs are bare paths (no `/anime/` prefix).
"""

from donghua_cli.sources.base import Source


class LMAnime(Source):
    key = "lm"
    name = "LMAnime"
    base_url = "https://lmanime.com"

    search_timeout = 10
    search_selectors = (".bs .bsx", "div.bsx", "article.bs", "div.bs")
    episode_selectors = (".eplister a", ".episodelist a", "#chapterlist a")

    _skip_url_fragments = (
        "/genre",
        "/release",
        "/bookmark",
        "/dmca",
        "/privacy",
        "/help",
        "wp-content",
        "/page/",
        "/?s=",
    )
    _min_title_len = 4

    def _is_series_link(self, href: str) -> bool:
        if not href.startswith(self.base_url):
            return False
        return not any(skip in href for skip in self._skip_url_fragments)
