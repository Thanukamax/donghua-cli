"""AnimeXin source plugin.

Series URLs are bare paths under base_url (no `/anime/` prefix).
"""

from donghua_cli.sources.base import Source


class AnimeXin(Source):
    key = "ax"
    name = "AnimeXin"
    base_url = "https://animexin.dev"

    search_selectors = ("article",)
    episode_selectors = (
        ".eplister a",
        ".episodelist a",
        "#chapterlist a",
        ".lstep a",
        "ul li a",
    )

    _skip_url_fragments = (
        "/genre",
        "/release-date",
        "/bookmark",
        "/dmca",
        "/privacy",
        "/help",
        "/how-to",
        "wp-content",
        "/page/",
        "/?s=",
    )
    _min_title_len = 4

    def _is_series_link(self, href: str) -> bool:
        # AX uses bare slug paths, not /anime/ — so override the default rule.
        if not href.startswith(self.base_url):
            return False
        return not any(skip in href for skip in self._skip_url_fragments)
