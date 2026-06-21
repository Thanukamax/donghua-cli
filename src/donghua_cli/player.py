"""Video player launching and episode downloading.

Handles MPV on desktop, Android intents on Termux, and VLC links on iOS/iSH.

On desktop, MPV is launched with an IPC socket so we can be notified when the
episode ends. ``wait_for_end()`` blocks until MPV exits, which the TUI uses to
auto-advance to the next episode when ``auto_next`` is enabled.
"""

import os
import subprocess
import tempfile
import time
import uuid
from typing import Optional

from donghua_cli import config
from donghua_cli.utils import sanitize_filename


def _ipc_socket_path() -> str:
    """Return a unique, platform-appropriate path for an MPV IPC socket."""
    tag = uuid.uuid4().hex[:8]
    if config.PLATFORM == "windows":
        return rf"\\.\pipe\dhua-{tag}"
    return os.path.join(tempfile.gettempdir(), f"dhua-mpv-{tag}.sock")


class Player:
    """Launch video in the best available player for the current platform."""

    def __init__(self, quality: str | None = None):
        self.quality = quality or config.get_quality()
        self._process: Optional[subprocess.Popen] = None
        self._ipc_path: Optional[str] = None

    def play(self, stream_url: str, title: str = "Donghua") -> bool:
        """Launch playback. Returns True if a player started successfully."""
        platform = config.PLATFORM

        if platform == "android":
            return self._play_android(stream_url, title)
        if platform == "ish":
            return self._play_ish(stream_url)
        return self._play_desktop(stream_url, title)

    def wait_for_end(self, poll_interval: float = 0.5) -> bool:
        """Block until the player process exits.

        Returns True if the player finished naturally (e.g. end of file or
        user-quit). Returns False if there was no live player to begin with.
        Safe to call repeatedly.
        """
        # Bind the process locally: a concurrent stop() (e.g. the user pressed
        # Next before this episode ended) sets self._process = None, which would
        # otherwise NoneType-crash the poll loop here.
        proc = self._process
        if proc is None:
            return False
        while proc.poll() is None:
            time.sleep(poll_interval)
        self._cleanup_socket()
        return True

    def stop(self) -> None:
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                time.sleep(0.3)
                if self._process.poll() is None:
                    self._process.kill()
                self._process.wait(timeout=2)
            except OSError:
                pass
        self._process = None
        # Reap the IPC socket too — without this, every superseded player leaks
        # a stale socket file in tmp until reboot.
        self._cleanup_socket()

    def _cleanup_socket(self) -> None:
        """Remove the IPC socket file if it's still on disk. Idempotent."""
        if self._ipc_path and os.path.exists(self._ipc_path):
            try:
                os.unlink(self._ipc_path)
            except OSError:
                pass
        self._ipc_path = None

    def is_playing(self) -> bool:
        return self._process is not None and self._process.poll() is None

    # ── platform-specific launchers ──────────────────────────────────────

    def _play_desktop(self, url: str, title: str) -> bool:
        self._ipc_path = _ipc_socket_path()
        cmd = [
            "mpv",
            url,
            f"--force-media-title={title}",
            f"--ytdl-format=bestvideo[height<={self.quality}]+bestaudio/best[height<={self.quality}]/best",
            "--cache=yes",
            "--cache-secs=60",
            "--no-terminal",
            f"--input-ipc-server={self._ipc_path}",
        ]

        if config.PLATFORM == "windows":
            cmd += ["--no-border", "--volume=50"]

        try:
            kwargs: dict = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "start_new_session": True,
            }
            if config.PLATFORM == "windows":
                si = subprocess.STARTUPINFO()  # type: ignore[attr-defined]
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore[attr-defined]
                kwargs["startupinfo"] = si

            self._process = subprocess.Popen(cmd, **kwargs)
            return True
        except FileNotFoundError:
            pass

        # Fallback: VLC
        try:
            self._process = subprocess.Popen(
                [
                    "vlc", url,
                    "--play-and-exit",
                    f"--meta-title={title}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except FileNotFoundError:
            return False

    def _play_android(self, url: str, title: str) -> bool:
        safe_url = url.replace(" ", "%20")
        intents = [
            f"am start --user 0 -a android.intent.action.VIEW -d '{safe_url}' -n is.xyz.mpv/.MPVActivity",
            f"am start --user 0 -a android.intent.action.VIEW -d '{safe_url}' -n org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity -e 'title' '{title}'",
            f"am start --user 0 -a android.intent.action.VIEW -d '{safe_url}' -n com.mxtech.videoplayer.ad/com.mxtech.videoplayer.ActivityScreen -e 'title' '{title}'",
            f"am start --user 0 -a android.intent.action.VIEW -d '{safe_url}' -t 'video/*'",
        ]
        for cmd in intents:
            r = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if r.returncode == 0:
                return True

        # Ultimate fallback
        subprocess.run(f"termux-open-url '{safe_url}'", shell=True)
        return True

    def _play_ish(self, url: str) -> bool:
        safe_url = url.replace(" ", "%20")
        print(f"\033]8;;vlc://{safe_url}\a")
        print("~~~~~~~~~~~~~~~~~~~~")
        print("~ Tap to open VLC ~")
        print("~~~~~~~~~~~~~~~~~~~~")
        print("\033]8;;\a")
        time.sleep(3)
        return True


class Downloader:
    """Download episodes via yt-dlp."""

    @staticmethod
    def download(
        stream_url: str,
        series_title: str,
        ep_title: str,
        quality: str,
    ) -> bool:
        series_dir = os.path.join(
            config.get_download_dir(), sanitize_filename(series_title)
        )
        os.makedirs(series_dir, exist_ok=True)

        filename = f"{sanitize_filename(ep_title)}.%(ext)s"
        output_path = os.path.join(series_dir, filename)

        cmd = [
            "yt-dlp",
            "-f", f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best",
            "-o", output_path,
            "--no-check-certificates",
            "--no-part",
            "--concurrent-fragments", "4",
            stream_url,
        ]

        try:
            kwargs: dict = {"check": True, "capture_output": True, "text": True}
            if config.PLATFORM == "windows":
                si = subprocess.STARTUPINFO()  # type: ignore[attr-defined]
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore[attr-defined]
                kwargs["startupinfo"] = si

            subprocess.run(cmd, **kwargs)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
