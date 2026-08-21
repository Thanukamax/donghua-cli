"""Tests for the doctor's pure logic: detection, arch/OS mapping, delegate
hints, GitHub asset matching, and archive extraction. Network fetch itself is
not exercised (no live download in CI) but everything feeding it is."""

import io
import os
import tarfile
import zipfile

import pytest

from donghua_cli import config, doctor


class TestArchOsMapping:
    @pytest.mark.parametrize("machine,expected", [
        ("x86_64", "x64"), ("AMD64", "x64"), ("aarch64", "arm64"),
        ("arm64", "arm64"), ("armv7l", "armhf"), ("i686", "x86"),
    ])
    def test_arch_tag(self, machine, expected, monkeypatch):
        monkeypatch.setattr(doctor.platform, "machine", lambda: machine)
        assert doctor._arch_tag() == expected

    def test_os_tag_windows(self, monkeypatch):
        monkeypatch.setattr(doctor.config, "PLATFORM", "windows")
        assert doctor._os_tag() == "win"

    def test_exe_suffix_on_windows(self, monkeypatch):
        monkeypatch.setattr(doctor.config, "PLATFORM", "windows")
        assert doctor._exe("mpv") == "mpv.exe"
        monkeypatch.setattr(doctor.config, "PLATFORM", "linux")
        assert doctor._exe("mpv") == "mpv"


class TestDetection:
    def test_prefers_managed_over_path(self, tmp_path, monkeypatch):
        # A binary in BIN_DIR must win over one on the system PATH.
        bindir = tmp_path / "bin"
        bindir.mkdir()
        managed = bindir / "mpv"
        managed.write_text("#!/bin/sh\n")
        managed.chmod(0o755)
        monkeypatch.setattr(config, "BIN_DIR", str(bindir))
        monkeypatch.setattr(doctor.shutil, "which", lambda c: "/usr/bin/mpv")

        path, source = doctor._which("mpv")
        assert source == "managed"
        assert path == str(managed)

    def test_falls_back_to_path(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "BIN_DIR", str(tmp_path / "empty"))
        monkeypatch.setattr(doctor.shutil, "which", lambda c: "/usr/bin/mpv")
        path, source = doctor._which("mpv")
        assert (path, source) == ("/usr/bin/mpv", "path")

    def test_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "BIN_DIR", str(tmp_path / "empty"))
        monkeypatch.setattr(doctor.shutil, "which", lambda c: None)
        assert doctor._which("nope") == (None, "missing")

    def test_detect_all_covers_every_tool(self, monkeypatch):
        monkeypatch.setattr(doctor, "_which", lambda cmd: (None, "missing"))
        statuses = doctor.detect_all()
        assert {s.tool.key for s in statuses} == {t.key for t in doctor.TOOLS}
        assert all(not s.ok for s in statuses)


class TestDelegateHint:
    def test_uses_present_manager(self, monkeypatch):
        monkeypatch.setattr(doctor.config, "PLATFORM", "linux")
        monkeypatch.setattr(doctor, "_present_managers", lambda: ["pacman"])
        assert doctor.delegate_hint(doctor.get_tool("mpv")) == "sudo pacman -S mpv"

    def test_ytdlp_always_has_pip_fallback(self, monkeypatch):
        monkeypatch.setattr(doctor, "_present_managers", lambda: [])
        hint = doctor.delegate_hint(doctor.get_tool("ytdlp"))
        assert "pip install" in hint

    def test_no_hint_when_manager_cannot_install(self, monkeypatch):
        # N_m3u8DL-RE isn't in apt; with only apt present there's no delegate.
        monkeypatch.setattr(doctor, "_present_managers", lambda: ["apt"])
        assert doctor.delegate_hint(doctor.get_tool("nm3u8dlre")) is None


class TestAssetMatching:
    def _assets(self, *names):
        return [{"name": n, "browser_download_url": f"https://x/{n}"} for n in names]

    def test_matches_os_and_arch(self):
        assets = self._assets(
            "N_m3u8DL-RE_v0.3.0_linux-x64_20241203.tar.gz",
            "N_m3u8DL-RE_v0.3.0_win-x64_20241203.zip",
            "N_m3u8DL-RE_v0.3.0_osx-arm64_20241203.tar.gz",
        )
        got = doctor._match_asset(assets, "linux", "x64")
        assert got["name"].endswith("linux-x64_20241203.tar.gz")

    def test_skips_checksum_sidecars(self):
        assets = self._assets(
            "tool_linux-x64.tar.gz.sha256",
            "tool_linux-x64.tar.gz",
        )
        got = doctor._match_asset(assets, "linux", "x64")
        assert got["name"] == "tool_linux-x64.tar.gz"

    def test_no_match_returns_none(self):
        assets = self._assets("tool_win-x64.zip")
        assert doctor._match_asset(assets, "linux", "arm64") is None


class TestExtractBinary:
    def test_extracts_from_targz(self, tmp_path):
        # Build a tar.gz containing a nested "ffmpeg" binary.
        archive = tmp_path / "ff.tar.gz"
        with tarfile.open(archive, "w:gz") as tf:
            data = b"#!/bin/sh\necho ffmpeg\n"
            info = tarfile.TarInfo("ffmpeg-6.0-static/ffmpeg")
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))

        dest = tmp_path / "bin"
        dest.mkdir()
        placed = doctor._extract_binary(str(archive), "ffmpeg", str(dest))
        assert placed == str(dest / "ffmpeg")
        assert os.path.isfile(placed)
        assert os.access(placed, os.X_OK)

    def test_extracts_from_zip(self, tmp_path):
        archive = tmp_path / "re.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("N_m3u8DL-RE", b"binary-bytes")

        dest = tmp_path / "bin"
        dest.mkdir()
        placed = doctor._extract_binary(str(archive), "N_m3u8DL-RE", str(dest))
        assert placed == str(dest / "N_m3u8DL-RE")

    def test_missing_member_returns_none(self, tmp_path):
        archive = tmp_path / "x.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("readme.txt", b"nope")
        dest = tmp_path / "bin"
        dest.mkdir()
        assert doctor._extract_binary(str(archive), "ffmpeg", str(dest)) is None


class TestFetchable:
    def test_ffmpeg_osx_delegates(self, monkeypatch):
        monkeypatch.setattr(doctor, "_os_tag", lambda: "osx")
        assert doctor.fetchable(doctor.get_tool("ffmpeg")) is False

    def test_ffmpeg_linux_fetchable(self, monkeypatch):
        monkeypatch.setattr(doctor, "_os_tag", lambda: "linux")
        assert doctor.fetchable(doctor.get_tool("ffmpeg")) is True

    def test_mpv_never_fetchable(self):
        assert doctor.fetchable(doctor.get_tool("mpv")) is False


class TestSmokeTest:
    def test_reports_player_and_source(self, monkeypatch):
        monkeypatch.setattr(
            doctor, "detect",
            lambda t: doctor.ToolStatus(t, path="/usr/bin/mpv", version="mpv 0.38", source="path"),
        )
        monkeypatch.setattr("donghua_cli.scraper.search_all", lambda q: ["hit"])
        res = doctor.smoke_test("x")
        names = {n for n, _, _ in res.checks}
        assert names == {"player", "source reachable"}
        assert res.ok

    def test_source_failure_is_not_ok(self, monkeypatch):
        monkeypatch.setattr(
            doctor, "detect",
            lambda t: doctor.ToolStatus(t, path="/usr/bin/mpv", version="mpv", source="path"),
        )
        monkeypatch.setattr("donghua_cli.scraper.search_all", lambda q: [])
        res = doctor.smoke_test("x")
        assert res.ok is False
