"""Shared test fixtures.

The tiered cache (``donghua_cli.cache``) writes to a real on-disk diskcache
under ``config.CACHE_DB_DIR``. Left unchecked, tests would pollute the user's
actual cache dir and — worse — see cross-test cache hits. This autouse fixture
points every test at a throwaway directory and reopens the store against it.
"""

import pytest

from donghua_cli import cache, config


@pytest.fixture(autouse=True)
def _isolate_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CACHE_DB_DIR", str(tmp_path / "dc"))
    previous = cache._store
    cache._store = None  # force store() to reopen against the tmp dir
    try:
        yield
    finally:
        if cache._store is not None:
            try:
                cache._store.close()
            except Exception:
                pass
        cache._store = previous
