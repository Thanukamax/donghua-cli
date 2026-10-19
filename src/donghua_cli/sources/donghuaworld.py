"""DonghuaWorld source plugin.

Fast, large catalog with multi-subtitle 4K episode uploads and active
Dailymotion/Ok.ru embeds. Standard AnimeStream WordPress theme, so the
templated search/episode scaffolding in ``Source`` covers it cleanly.
"""

from donghua_cli.sources.base import Source


class DonghuaWorld(Source):
    key = "dw"
    name = "DonghuaWorld"
    base_url = "https://donghuaworld.com"

    search_timeout = 10
