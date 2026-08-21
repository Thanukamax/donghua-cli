"""Video player launching and episode downloading.

Handles MPV on desktop, Android intents on Termux, and VLC links on iOS/iSH.

On desktop, MPV is launched with an IPC socket so we can be notified when the
episode ends. ``wait_for_end()`` blocks until MPV exits, which the TUI uses to
auto-advance to the next episode when ``auto_next`` is enabled.
"""

import os
import shutil
import subprocess
import tempfile
import time
import uuid
from typing import Optional

from donghua_cli import config
from donghua_cli.utils import sanitize_filename

# The HLS downloader we prefer over yt-dlp+ffmpeg: parallel segment fetch plus a
# merge path that survives the malformed/encrypted playlists ffmpeg chokes on.
# Optional — absent installs fall straight back to yt-dlp.
_NM3U8DLRE_BIN = "N_m3u8DL-RE"


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

    def wait_until_playing(self, grace: float = 8.0, poll_interval: float = 0.25) -> bool:
        """Confirm playback actually survived startup.

        ``play()`` only reports that the player *process* spawned — mpv exits 0
        in well under a second when the URL is a pulled video (a 410, or an
        embed shell it demuxes as a zero-length file). Without this check the UI
        announces "Playing" over a window that has already closed, which reads
        to the user as a broken player rather than dead content.

        Returns True if the process is still alive after ``grace`` seconds, or
        if there is no process to judge (Android/iSH hand off to an external
        app and legitimately have nothing to poll). Returns False only when the
        process we launched exited on its own inside the grace window.

        ``grace`` is generous because a *healthy* start can be slow: mpv shells
        out to yt-dlp to resolve the page before opening the first segment, and
        that round trip alone runs several seconds on these hosts.
        """
        proc = self._process
        if proc is None:
            return True
        deadline = time.monotonic() + grace
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                self._cleanup_socket()
                return False
            time.sleep(poll_interval)
        return True

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
        # Send the same identity the download path does. Several of these hosts
        # hotlink-protect their segments and answer a naked player with 403 —
        # the download path has always passed these, playback never did, so the
        # two disagreed about whether a given episode worked.
        headers = config.get_headers()
        cmd = [
            "mpv",
            url,
            f"--force-media-title={title}",
            f"--ytdl-format=bestvideo[height<={self.quality}]+bestaudio/best[height<={self.quality}]/best",
            "--cache=yes",
            "--cache-secs=60",
            "--no-terminal",
            f"--user-agent={headers['User-Agent']}",
            f"--referrer={headers.get('Referer', url)}",
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
    """Download episodes.

    Prefers N_m3u8DL-RE for HLS — it fetches segments in parallel and merges the
    quirky playlists ffmpeg refuses — and falls back to yt-dlp for everything
    else (progressive files, or when N_m3u8DL-RE isn't installed). yt-dlp does
    double duty: it also resolves a page/embed URL down to the actual variant
    playlist we then hand to N_m3u8DL-RE.
    """

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

        # Fast path: resolve to a single HLS variant playlist at <=quality and
        # let N_m3u8DL-RE pull it. Any miss (no binary, not HLS, split
        # audio/video, resolve failure) drops through to the yt-dlp path.
        if shutil.which(_NM3U8DLRE_BIN):
            hls = Downloader._resolve_hls(stream_url, quality)
            if hls and Downloader._download_nm3u8dlre(hls, series_dir, ep_title):
                return True

        return Downloader._download_ytdlp(stream_url, series_dir, ep_title, quality)

    @staticmethod
    def _run(cmd: list[str], *, check: bool) -> subprocess.CompletedProcess | None:
        """Run a child process with the Windows console-window suppressed.

        Returns the completed process, or None on failure / missing binary.
        """
        kwargs: dict = {"capture_output": True, "text": True, "check": check}
        if config.PLATFORM == "windows":
            si = subprocess.STARTUPINFO()  # type: ignore[attr-defined]
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore[attr-defined]
            kwargs["startupinfo"] = si
        try:
            return subprocess.run(cmd, **kwargs)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    @staticmethod
    def _resolve_hls(stream_url: str, quality: str) -> str:
        """Return a single HLS/DASH manifest URL at <=quality, or "" if the
        source isn't HLS (progressive mp4, split tracks, resolve failure).

        When ``stream_url`` is already a manifest we pass it straight through;
        otherwise yt-dlp ``-g`` resolves the page/embed to its media URL(s).
        We only accept a *single* returned URL that is a playlist — split
        video+audio tracks (two lines) go to yt-dlp, which muxes them for us.
        """
        if stream_url.split("?")[0].endswith((".m3u8", ".mpd")):
            return stream_url

        headers = config.get_headers()
        proc = Downloader._run(
            [
                "yt-dlp",
                "-g",
                "-f", f"best[height<={quality}]/best",
                "--no-check-certificates",
                "--referer", stream_url,
                "--user-agent", headers["User-Agent"],
                stream_url,
            ],
            check=False,
        )
        if not proc or proc.returncode != 0:
            return ""
        urls = [ln for ln in proc.stdout.strip().splitlines() if ln.startswith("http")]
        if len(urls) == 1 and urls[0].split("?")[0].endswith((".m3u8", ".mpd")):
            return urls[0]
        return ""

    @staticmethod
    def _download_nm3u8dlre(manifest_url: str, series_dir: str, ep_title: str) -> bool:
        """Download an HLS/DASH manifest via N_m3u8DL-RE, muxed to mp4."""
        headers = config.get_headers()
        cmd = [
            _NM3U8DLRE_BIN,
            manifest_url,
            "--save-dir", series_dir,
            "--save-name", sanitize_filename(ep_title),
            "--auto-select",
            "--thread-count", "16",
            "-H", f"User-Agent: {headers['User-Agent']}",
        ]
        referer = headers.get("Referer")
        if referer:
            cmd += ["-H", f"Referer: {referer}"]
        cmd += ["-M", "format=mp4"]

        proc = Downloader._run(cmd, check=False)
        return bool(proc and proc.returncode == 0)

    @staticmethod
    def _download_ytdlp(
        stream_url: str, series_dir: str, ep_title: str, quality: str
    ) -> bool:
        output_path = os.path.join(series_dir, f"{sanitize_filename(ep_title)}.%(ext)s")
        cmd = [
            "yt-dlp",
            "-f", f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best",
            "-o", output_path,
            "--no-check-certificates",
            "--no-part",
            "--concurrent-fragments", "4",
            stream_url,
        ]
        proc = Downloader._run(cmd, check=True)
        return proc is not None
