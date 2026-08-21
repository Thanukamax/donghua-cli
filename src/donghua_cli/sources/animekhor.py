"""AnimeKhor source plugin.

Same AnimeStream WordPress theme as AnimeXin and LMAnime, so the selectors
carry over unchanged. Series URLs live under `/anime/`.

Added 2026-08-19 to replace MisterDonghua and H-Donghua, whose domains stopped
answering entirely (verified over Tor, so it was not a local network block).
Its episode pages carry ~9 base64-encoded dub servers, which is exactly the
shape `extractor.extract_servers` decodes — so a pulled upload on one dub still
leaves the others playable.
"""

from donghua_cli.sources.base import Source


class AnimeKhor(Source):
    key = "ak"
    name = "AnimeKhor"
    base_url = "https://animekhor.org"

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
