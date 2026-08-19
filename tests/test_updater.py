"""Update-check behaviour: version ordering, install detection, and the
notify-don't-mutate policy."""

import json
import os
import time

import pytest

from donghua_cli import updater


class TestVersionOrdering:
    def test_semver(self):
        assert updater.is_newer("3.2.2", "3.2.1")
        assert not updater.is_newer("3.2.1", "3.2.2")

    def test_equal_is_not_newer(self):
        assert not updater.is_newer("3.2.1", "3.2.1")

    def test_ytdlp_date_versions(self):
        # yt-dlp ships date versions; these must order correctly too.
        assert updater.is_newer("2026.07.04", "2026.02.04")
        assert not updater.is_newer("2026.02.04", "2026.07.04")

    def test_zero_padded_components_compare_numerically(self):
        # "2026.10.01" must beat "2026.09.30" — string compare would too, but
        # "2026.2.4" vs "2026.10.1" is where lexical ordering breaks.
        assert updater.is_newer("2026.10.01", "2026.2.4")

    def test_missing_versions_never_claim_an_update(self):
        assert not updater.is_newer("", "3.2.1")
        assert not updater.is_newer("3.2.2", "")
        assert not updater.is_newer(None, None)  # type: ignore[arg-type]

    def test_prerelease_suffix_does_not_fabricate_an_update(self):
        # Dropping the suffix can only suppress a prompt, never invent one.
        assert not updater.is_newer("3.2.1rc1", "3.2.1")


class TestInstallDetection:
    def test_pipx_prefix_uses_pipx_upgrade(self, monkeypatch):
        monkeypatch.setattr(updater.sys, "prefix", "/home/u/.local/share/pipx/venvs/donghua-cli")
        got = updater._detect_self_install()
        assert got.method == "pipx"
        assert got.command == ("pipx", "upgrade", "donghua-cli")

    def test_uv_tool_prefix_uses_uv_upgrade(self, monkeypatch):
        monkeypatch.setattr(updater.sys, "prefix", "/home/u/.local/share/uv/tools/donghua-cli")
        assert updater._detect_self_install().method == "uv"

    def test_source_checkout_refuses_to_self_update(self, monkeypatch):
        # Running from a working tree: pip would fight git. Report, don't act.
        monkeypatch.setattr(updater.sys, "prefix", "/home/u/proj/.venv")
        got = updater._detect_self_install()
        assert got.method == "source"
        assert not got.updatable
        assert got.note

    def test_distro_ytdlp_is_left_to_the_package_manager(self, monkeypatch):
        monkeypatch.setattr(updater.shutil if hasattr(updater, "shutil") else os, "sep", os.sep)
        import shutil as _sh
        monkeypatch.setattr(_sh, "which", lambda c: "/usr/bin/yt-dlp")
        got = updater._detect_ytdlp_install()
        assert got.method == "system"
        assert not got.updatable

    def test_missing_ytdlp_points_at_doctor(self, monkeypatch):
        import shutil as _sh
        monkeypatch.setattr(_sh, "which", lambda c: None)
        got = updater._detect_ytdlp_install()
        assert got.method == "missing"
        assert not got.updatable


class TestCheckCaching:
    @pytest.fixture(autouse=True)
    def _isolate_state(self, tmp_path, monkeypatch):
        monkeypatch.setattr(updater, "STATE_FILE", str(tmp_path / "update-check.json"))
        monkeypatch.setattr(updater.config, "CACHE_DIR", str(tmp_path))

    def test_network_is_skipped_while_the_verdict_is_fresh(self, monkeypatch):
        calls = []
        monkeypatch.setattr(updater, "latest_pypi_version",
                            lambda pkg: calls.append(pkg) or "99.0.0")
        monkeypatch.setattr(updater, "_installed_ytdlp_version", lambda: "2026.02.04")
        updater.check(force=True)
        assert calls, "first check must hit the network"
        calls.clear()
        updater.check()
        assert calls == [], "a fresh verdict must not re-query PyPI"

    def test_force_bypasses_the_cache(self, monkeypatch):
        monkeypatch.setattr(updater, "_installed_ytdlp_version", lambda: "2026.02.04")
        calls = []
        monkeypatch.setattr(updater, "latest_pypi_version",
                            lambda pkg: calls.append(pkg) or "99.0.0")
        updater.check(force=True)
        calls.clear()
        updater.check(force=True)
        assert calls, "--update must re-query even with a fresh cache"

    def test_cached_verdict_clears_once_the_update_is_applied(self, monkeypatch):
        # Only the *remote* version is cached. Installed versions are re-read, so
        # the notice must vanish immediately after upgrading rather than linger.
        with open(updater.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"at": time.time(), "latest": {"yt-dlp": "2026.07.04"}}, f)
        monkeypatch.setattr(updater, "_installed_ytdlp_version", lambda: "2026.02.04")
        assert any(u.package == "yt-dlp" for u in updater.check())
        monkeypatch.setattr(updater, "_installed_ytdlp_version", lambda: "2026.07.04")
        assert not any(u.package == "yt-dlp" for u in updater.check())

    def test_a_failed_lookup_reports_no_updates(self, monkeypatch):
        monkeypatch.setattr(updater, "latest_pypi_version", lambda pkg: None)
        monkeypatch.setattr(updater, "_installed_ytdlp_version", lambda: "2026.02.04")
        assert updater.check(force=True) == []


class TestApply:
    def test_dry_run_executes_nothing(self, monkeypatch):
        ran = []
        monkeypatch.setattr(updater.subprocess, "run", lambda *a, **k: ran.append(a))
        up = updater.Update("yt-dlp", "1", "2", updater.Install("pip", ("echo", "hi")))
        assert updater.apply([up], dry_run=True) == 0
        assert ran == [], "--dry-run must not run the upgrade command"

    def test_non_updatable_package_is_reported_not_attempted(self, monkeypatch):
        ran = []
        monkeypatch.setattr(updater.subprocess, "run", lambda *a, **k: ran.append(a))
        up = updater.Update("yt-dlp", "1", "2",
                            updater.Install("system", (), note="use your package manager"))
        assert updater.apply([up]) == 1
        assert ran == []
