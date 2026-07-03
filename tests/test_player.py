"""Tests for the Player lifecycle — process + IPC socket teardown.

These cover the v3.2.1 auto-next leak fix: a superseded player must release its
mpv process and IPC socket, and wait_for_end must survive a concurrent stop()
that nulls the process reference (which is what Next / Replay / auto-next do).
"""

import os
import tempfile
import threading
import time

from donghua_cli.player import Player


class _FakeProc:
    """Stand-in for subprocess.Popen: stays alive for `alive_polls` poll() calls,
    then reports the exit code set by terminate()/kill() (or 0)."""

    def __init__(self, alive_polls: int = 0):
        self._remaining = alive_polls
        self._code: int | None = None
        self.terminated = False
        self.killed = False

    def poll(self):
        if self._remaining > 0:
            self._remaining -= 1
            return None
        return self._code if self._code is not None else 0

    def terminate(self):
        self.terminated = True
        self._code = -15

    def kill(self):
        self.killed = True
        self._code = -9

    def wait(self, timeout=None):
        return self._code or 0


def _make_socket_file() -> str:
    fd, path = tempfile.mkstemp(prefix="dhua-test-", suffix=".sock")
    os.close(fd)
    return path


class TestPlayerTeardown:
    def test_wait_for_end_no_process_returns_false(self):
        assert Player(quality="720").wait_for_end() is False

    def test_stop_unlinks_ipc_socket_and_clears_state(self):
        p = Player(quality="720")
        sock = _make_socket_file()
        p._ipc_path = sock
        p._process = _FakeProc(alive_polls=1)
        assert os.path.exists(sock)
        p.stop()
        assert not os.path.exists(sock)
        assert p._process is None
        assert p._ipc_path is None

    def test_stop_is_idempotent_with_no_process(self):
        p = Player(quality="720")
        p.stop()  # must not raise
        p.stop()

    def test_wait_for_end_cleans_socket_on_natural_exit(self):
        p = Player(quality="720")
        sock = _make_socket_file()
        p._ipc_path = sock
        p._process = _FakeProc(alive_polls=0)  # already exited
        assert p.wait_for_end(poll_interval=0.01) is True
        assert not os.path.exists(sock)

    def test_wait_for_end_survives_concurrent_stop(self):
        # The core auto-next race: a newer playback stops this player (nulling
        # self._process) while wait_for_end is mid-poll. Binding the process
        # locally must keep this from NoneType-crashing the poll loop.
        p = Player(quality="720")
        p._ipc_path = _make_socket_file()
        proc = _FakeProc(alive_polls=50)
        p._process = proc

        def supersede():
            time.sleep(0.02)
            p._process = None      # what stop() does to the shared reference
            proc._code = -15       # ...after terminating the underlying process
            proc._remaining = 0

        t = threading.Thread(target=supersede)
        t.start()
        assert p.wait_for_end(poll_interval=0.01) is True
        t.join()


class _Proc:
    """Minimal CompletedProcess stand-in for Downloader._run stubs."""

    def __init__(self, returncode=0, stdout=""):
        self.returncode = returncode
        self.stdout = stdout


class TestDownloadRouting:
    """Downloader prefers N_m3u8DL-RE for HLS and falls back to yt-dlp for
    everything else. These stub subprocess + tool detection so nothing hits the
    network or the real filesystem beyond a tmp download dir."""

    def _setup(self, monkeypatch, tmp_path, *, has_binary):
        from donghua_cli import config, player

        monkeypatch.setattr(config, "get_download_dir", lambda: str(tmp_path))
        monkeypatch.setattr(
            player.shutil, "which", lambda name: "/usr/bin/x" if has_binary else None
        )

    def test_no_binary_uses_ytdlp(self, monkeypatch, tmp_path):
        from donghua_cli.player import Downloader

        self._setup(monkeypatch, tmp_path, has_binary=False)
        calls = []
        monkeypatch.setattr(Downloader, "_download_nm3u8dlre", lambda *a: calls.append("re") or True)
        monkeypatch.setattr(Downloader, "_download_ytdlp", lambda *a: calls.append("yt") or True)

        assert Downloader.download("http://x/watch", "S", "E01", "720") is True
        assert calls == ["yt"]

    def test_hls_resolves_uses_nm3u8dlre(self, monkeypatch, tmp_path):
        from donghua_cli.player import Downloader

        self._setup(monkeypatch, tmp_path, has_binary=True)
        calls = []
        monkeypatch.setattr(Downloader, "_resolve_hls", lambda url, q: "http://cdn/v.m3u8")
        monkeypatch.setattr(Downloader, "_download_nm3u8dlre", lambda *a: calls.append("re") or True)
        monkeypatch.setattr(Downloader, "_download_ytdlp", lambda *a: calls.append("yt") or True)

        assert Downloader.download("http://x/watch", "S", "E01", "720") is True
        assert calls == ["re"]

    def test_nm3u8dlre_failure_falls_back_to_ytdlp(self, monkeypatch, tmp_path):
        from donghua_cli.player import Downloader

        self._setup(monkeypatch, tmp_path, has_binary=True)
        calls = []
        monkeypatch.setattr(Downloader, "_resolve_hls", lambda url, q: "http://cdn/v.m3u8")
        monkeypatch.setattr(Downloader, "_download_nm3u8dlre", lambda *a: calls.append("re") or False)
        monkeypatch.setattr(Downloader, "_download_ytdlp", lambda *a: calls.append("yt") or True)

        assert Downloader.download("http://x/watch", "S", "E01", "720") is True
        assert calls == ["re", "yt"]

    def test_non_hls_source_uses_ytdlp(self, monkeypatch, tmp_path):
        from donghua_cli.player import Downloader

        self._setup(monkeypatch, tmp_path, has_binary=True)
        calls = []
        monkeypatch.setattr(Downloader, "_resolve_hls", lambda url, q: "")  # progressive/miss
        monkeypatch.setattr(Downloader, "_download_nm3u8dlre", lambda *a: calls.append("re") or True)
        monkeypatch.setattr(Downloader, "_download_ytdlp", lambda *a: calls.append("yt") or True)

        assert Downloader.download("http://x/file.mp4", "S", "E01", "720") is True
        assert calls == ["yt"]


class TestResolveHls:
    def test_direct_m3u8_passthrough(self):
        from donghua_cli.player import Downloader

        assert Downloader._resolve_hls("http://cdn/v.m3u8?token=1", "720") == "http://cdn/v.m3u8?token=1"

    def test_single_hls_url_accepted(self, monkeypatch):
        from donghua_cli.player import Downloader

        monkeypatch.setattr(Downloader, "_run", lambda cmd, check: _Proc(0, "http://cdn/v.m3u8\n"))
        assert Downloader._resolve_hls("http://x/watch", "720") == "http://cdn/v.m3u8"

    def test_split_tracks_rejected(self, monkeypatch):
        from donghua_cli.player import Downloader

        # Two URLs (video + audio) -> yt-dlp should mux instead; return "".
        monkeypatch.setattr(
            Downloader, "_run", lambda cmd, check: _Proc(0, "http://cdn/v.m3u8\nhttp://cdn/a.m3u8\n")
        )
        assert Downloader._resolve_hls("http://x/watch", "720") == ""

    def test_progressive_mp4_rejected(self, monkeypatch):
        from donghua_cli.player import Downloader

        monkeypatch.setattr(Downloader, "_run", lambda cmd, check: _Proc(0, "http://cdn/video.mp4\n"))
        assert Downloader._resolve_hls("http://x/watch", "720") == ""

    def test_resolve_failure_returns_empty(self, monkeypatch):
        from donghua_cli.player import Downloader

        monkeypatch.setattr(Downloader, "_run", lambda cmd, check: None)
        assert Downloader._resolve_hls("http://x/watch", "720") == ""
