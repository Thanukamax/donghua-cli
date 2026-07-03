"""DonghuaStream source plugin.

The largest catalog in the niche. Sits behind Cloudflare, which 403s naked
HTTP clients — it's reachable only because ``utils.get_client`` now impersonates
a real browser's TLS fingerprint (curl_cffi). Standard AnimeStream WordPress
theme, so the templated search/episode scaffolding in ``Source`` covers it with
the default selectors; we only widen the search budget for Cloudflare's
first-hit latency.
"""

from donghua_cli.sources.base import Source


class DonghuaStream(Source):
    key = "ds"
    name = "DonghuaStream"
    base_url = "https://donghuastream.org"

    # Cloudflare adds a beat on the first request; give search room.
    search_timeout = 12
