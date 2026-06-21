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
