"""``donghua doctor`` — dependency diagnosis, guided install, and a smoke test.

The app shells out to external binaries it doesn't ship: ``mpv`` (playback),
``ffmpeg`` (muxing), ``yt-dlp`` (extraction fallback + downloads) and, optionally,
``N_m3u8DL-RE`` (fast parallel HLS downloads). A fresh machine is missing some of
them and today the only signal is a terminal "install mpv or vlc" string at the
worst possible moment — mid-playback.

The doctor turns that into an upfront, actionable report:

  * **Detect**   — find each tool on ``PATH`` *and* in our managed ``BIN_DIR``,
                   with version and what breaks without it.
  * **Delegate** — print the exact package-manager command for *this* OS/manager
                   (apt/dnf/pacman/zypper/brew/scoop/winget/pkg). Always correct,
                   never touches the system without the user running it.
  * **Fetch**    — for the tools with clean per-arch static builds (ffmpeg,
                   N_m3u8DL-RE), optionally download → ``BIN_DIR``, checksum, and
                   unpack, all stdlib. Off by default; ``--fetch`` opts in.
  * **Smoke**    — confirm at least one source answers and a player is present.

Design note: this is a one-shot Rich report, not a Textual app — a full TUI for a
linear diagnostic printout would be ceremony. It reuses the theme tokens so it
reads as part of the same product.
"""

from __future__ import annotations

import hashlib
import os
import platform
import re
import shutil
import stat
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Optional

from donghua_cli import config, theme
from donghua_cli.palette import GLYPH

console = theme.console


# ── tool registry ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Tool:
    key: str
    cmd: str                       # executable name (sans extension)
    label: str
    unlocks: str                   # what the user loses without it
    required: bool                 # True → core; False → optional/speed-up
    version_args: tuple[str, ...] = ("--version",)
    # GitHub "owner/repo" whose latest release carries a per-arch static build,
    # or "" when we only ever delegate this tool to a package manager / pip.
    github_repo: str = ""


TOOLS: tuple[Tool, ...] = (
    Tool("mpv", "mpv", "mpv", "streaming playback", required=True),
    Tool("ytdlp", "yt-dlp", "yt-dlp", "extraction fallback + downloads", required=True),
    Tool("ffmpeg", "ffmpeg", "FFmpeg", "muxing merged video+audio", required=False,
         version_args=("-version",), github_repo="yt-dlp/FFmpeg-Builds"),
    Tool("nm3u8dlre", "N_m3u8DL-RE", "N_m3u8DL-RE", "fast parallel HLS downloads",
         required=False, github_repo="nilaoda/N_m3u8DL-RE"),
)


def get_tool(key: str) -> Optional[Tool]:
    return next((t for t in TOOLS if t.key == key), None)


# ── platform / arch normalisation ─────────────────────────────────────────


def _os_tag() -> str:
    """Normalised OS tag used for asset matching: linux / win / osx."""
    if config.PLATFORM == "windows":
        return "win"
    if platform.system() == "Darwin":
        return "osx"
    return "linux"


def _arch_tag() -> str:
    """Normalised CPU arch tag: x64 / arm64 / armhf / x86."""
    m = platform.machine().lower()
    if m in ("x86_64", "amd64"):
        return "x64"
    if m in ("aarch64", "arm64"):
        return "arm64"
    if m.startswith("armv") or m == "arm":
        return "armhf"
    if m in ("i386", "i686", "x86"):
        return "x86"
    return m or "x64"


def _exe(name: str) -> str:
    """Append .exe on Windows."""
    return name + ".exe" if config.PLATFORM == "windows" else name


# ── detection ─────────────────────────────────────────────────────────────


@dataclass
class ToolStatus:
    tool: Tool
    path: Optional[str] = None
    version: Optional[str] = None
    source: str = "missing"        # "path" | "managed" | "missing"

    @property
    def ok(self) -> bool:
        return self.path is not None


def _which(cmd: str) -> tuple[Optional[str], str]:
    """Locate ``cmd``, preferring our managed BIN_DIR over the system PATH.

    Returns ``(path, source)`` where source is "managed" (found in BIN_DIR),
    "path" (found on the system PATH), or ("", "missing").
    """
    managed = os.path.join(config.BIN_DIR, _exe(cmd))
    if os.path.isfile(managed) and os.access(managed, os.X_OK):
        return managed, "managed"
    found = shutil.which(cmd)
    if found:
        return found, "path"
    return None, "missing"


def _probe_version(path: str, tool: Tool) -> Optional[str]:
    """Run the tool's version command and return a trimmed first line."""
    try:
        out = subprocess.run(
            [path, *tool.version_args],
            capture_output=True, text=True, timeout=6,
        )
        lines = (out.stdout or out.stderr).strip().splitlines()
        if not lines:
            return None
        # Drop the "Copyright …" tail mpv/ffmpeg append so the line doesn't get
        # truncated mid-word — we only want the version token.
        return re.split(r"\s+Copyright", lines[0])[0].strip()[:40]
    except (OSError, subprocess.SubprocessError):
        return None


def detect(tool: Tool) -> ToolStatus:
    path, source = _which(tool.cmd)
    if not path:
        return ToolStatus(tool)
    return ToolStatus(tool, path=path, version=_probe_version(path, tool), source=source)


def detect_all() -> list[ToolStatus]:
    return [detect(t) for t in TOOLS]


# ── delegate: package-manager guidance ────────────────────────────────────

# Per-manager package names. None → that manager can't install this tool
# cleanly, so we don't pretend it can.
_PKG_NAMES: dict[str, dict[str, Optional[str]]] = {
    "mpv":       {"apt": "mpv", "dnf": "mpv", "pacman": "mpv", "zypper": "mpv",
                  "brew": "mpv", "scoop": "mpv", "winget": None, "pkg": "mpv"},
    "ffmpeg":    {"apt": "ffmpeg", "dnf": "ffmpeg", "pacman": "ffmpeg",
                  "zypper": "ffmpeg", "brew": "ffmpeg", "scoop": "ffmpeg",
                  "winget": "Gyan.FFmpeg", "pkg": "ffmpeg"},
    "ytdlp":     {"apt": None, "dnf": None, "pacman": "yt-dlp", "zypper": None,
                  "brew": "yt-dlp", "scoop": "yt-dlp", "winget": "yt-dlp.yt-dlp",
                  "pkg": "yt-dlp"},
    "nm3u8dlre": {"apt": None, "dnf": None, "pacman": None, "zypper": None,
                  "brew": None, "scoop": "n_m3u8dl-re", "winget": None, "pkg": None},
}

_MANAGER_INSTALL = {
    "apt": "sudo apt install {pkg}",
    "dnf": "sudo dnf install {pkg}",
    "pacman": "sudo pacman -S {pkg}",
    "zypper": "sudo zypper install {pkg}",
    "brew": "brew install {pkg}",
    "scoop": "scoop install {pkg}",
    "winget": "winget install {pkg}",
    "pkg": "pkg install {pkg}",
}

# Which managers to even consider on each OS, in preference order.
_OS_MANAGERS = {
    "linux": ("apt", "dnf", "pacman", "zypper"),
    "osx": ("brew",),
    "win": ("winget", "scoop"),
    "android": ("pkg",),
}


def _present_managers() -> list[str]:
    """Package managers actually installed on this machine, in OS preference
    order."""
    os_key = "android" if config.PLATFORM == "android" else _os_tag()
    return [m for m in _OS_MANAGERS.get(os_key, ()) if shutil.which(m)]


def delegate_hint(tool: Tool) -> Optional[str]:
    """Best single install command for this tool on this machine, or None.

    yt-dlp always falls back to pip (it's a Python package and rides the venv),
    which is the recommended path regardless of OS.
    """
    for mgr in _present_managers():
        pkg = _PKG_NAMES.get(tool.key, {}).get(mgr)
        if pkg:
            return _MANAGER_INSTALL[mgr].format(pkg=pkg)
    if tool.key == "ytdlp":
        return "python -m pip install -U yt-dlp"
    return None


# ── fetch: per-arch static builds from GitHub releases ────────────────────


@dataclass
class FetchPlan:
    tool: Tool
    url: str
    asset_name: str
    member_hint: str               # executable basename expected inside archive
    digest_url: str = ""           # optional sidecar checksum (best-effort)
    notes: str = ""


def fetchable(tool: Tool) -> bool:
    """True if we know how to auto-fetch a static build for this OS/arch.

    Mirrors the memory's asymmetry: ffmpeg + N_m3u8DL-RE have clean per-arch
    archives (stdlib-extractable). mpv has no good static build on Linux/macOS
    and only a .7z on Windows (needs a 7z extractor we won't drag in), so mpv is
    always delegated.
    """
    if not tool.github_repo:
        return False
    if tool.key == "ffmpeg" and _os_tag() == "osx":
        return False  # evermeet/brew territory; delegate instead of guessing
    return True


def _match_asset(assets: list[dict], os_tag: str, arch: str) -> Optional[dict]:
    """Pick the release asset matching this OS+arch from a GitHub release's
    asset list. Skips checksum/signature sidecars."""
    def score(name: str) -> int:
        n = name.lower()
        if os_tag not in n:
            return -1
        if arch not in n and not (arch == "x64" and ("win64" in n or "amd64" in n or "x86_64" in n)):
            return -1
        if n.endswith((".sha256", ".sig", ".txt", ".asc")):
            return -1
        pref = 0
        if n.endswith((".tar.gz", ".tgz", ".tar.xz", ".zip")):
            pref = 1
        return pref

    best, best_score = None, 0
    for a in assets:
        s = score(a.get("name", ""))
        if s > best_score:
            best, best_score = a, s
    return best


def plan_fetch(tool: Tool) -> Optional[FetchPlan]:
    """Resolve the download URL for ``tool``'s latest per-arch static build.

    Hits the GitHub releases API through the shared impersonated client. Returns
    None if nothing matches (caller falls back to delegate guidance).
    """
    if not fetchable(tool):
        return None
    from donghua_cli.utils import get_client

    os_tag, arch = _os_tag(), _arch_tag()

    # ffmpeg on Linux: John Van Sickle's static builds are the canonical source
    # and are keyed by a different arch spelling than GitHub assets.
    if tool.key == "ffmpeg" and os_tag == "linux":
        jvs_arch = {"x64": "amd64", "arm64": "arm64", "armhf": "armhf", "x86": "i686"}.get(arch, "amd64")
        base = f"https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-{jvs_arch}-static.tar.xz"
        return FetchPlan(tool, url=base, asset_name=os.path.basename(base),
                         member_hint="ffmpeg", digest_url=base + ".sha256",
                         notes="johnvansickle.com static build")

    try:
        api = f"https://api.github.com/repos/{tool.github_repo}/releases/latest"
        resp = get_client().get(api, timeout=12)
        if resp.status_code != 200:
            return None
        assets = resp.json().get("assets", [])
    except Exception:
        return None

    asset = _match_asset(assets, os_tag, arch)
    if not asset:
        return None
    return FetchPlan(
        tool,
        url=asset["browser_download_url"],
        asset_name=asset["name"],
        member_hint=_exe(tool.cmd),
        notes=f"{tool.github_repo} latest release",
    )


def _extract_binary(archive: str, member_hint: str, dest_dir: str) -> Optional[str]:
    """Pull the executable out of a downloaded archive into ``dest_dir``.

    Handles .zip and .tar.(gz|xz) with the stdlib only. Matches the member whose
    basename equals ``member_hint`` (case-insensitive), else the first member
    whose basename starts with it. Returns the placed path or None.
    """
    import tarfile
    import zipfile

    target = os.path.join(dest_dir, member_hint)
    want = member_hint.lower()

    def _pick(names: list[str]) -> Optional[str]:
        for n in names:
            if os.path.basename(n).lower() == want:
                return n
        for n in names:
            if os.path.basename(n).lower().startswith(want.replace(".exe", "")):
                return n
        return None

    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zf:
            member = _pick(zf.namelist())
            if not member:
                return None
            with zf.open(member) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
    elif tarfile.is_tarfile(archive):
        with tarfile.open(archive) as tf:
            member = _pick(tf.getnames())
            if not member:
                return None
            extracted = tf.extractfile(member)
            if extracted is None:
                return None
            with extracted as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
    else:
        return None

    os.chmod(target, os.stat(target).st_mode | stat.S_IEXEC | stat.S_IRUSR)
    return target


def fetch_tool(plan: FetchPlan, on_progress=None) -> tuple[bool, str]:
    """Download, checksum, and unpack a static build into BIN_DIR.

    Returns ``(ok, message)``. Best-effort by design: any failure returns
    ``(False, reason)`` and the caller falls back to delegate guidance. The
    SHA-256 is always computed and surfaced; when the source publishes a
    checksum sidecar we verify against it, otherwise we report the digest so a
    cautious user can cross-check.
    """
    from donghua_cli.utils import get_client

    os.makedirs(config.BIN_DIR, exist_ok=True)
    client = get_client()

    fd, tmp = tempfile.mkstemp(prefix="dhua-dl-", dir=config.BIN_DIR)
    os.close(fd)
    try:
        digest = hashlib.sha256()
        try:
            with client.stream("GET", plan.url, timeout=60) as resp:
                if resp.status_code != 200:
                    return False, f"download HTTP {resp.status_code}"
                with open(tmp, "wb") as out:
                    for chunk in resp.iter_content():
                        out.write(chunk)
                        digest.update(chunk)
        except Exception as e:
            return False, f"download failed: {e}"

        got = digest.hexdigest()
        expected = _fetch_expected_digest(plan, client)
        if expected and expected.lower() != got.lower():
            return False, f"checksum mismatch (expected {expected[:12]}…, got {got[:12]}…)"

        placed = _extract_binary(tmp, plan.member_hint, config.BIN_DIR)
        if not placed:
            return False, "could not find the executable inside the archive"

        verified = "verified" if expected else f"sha256 {got[:12]}… (unverified)"
        return True, f"installed to {placed} ({verified})"
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def _fetch_expected_digest(plan: FetchPlan, client) -> str:
    """Fetch a published SHA-256 sidecar if the plan names one."""
    if not plan.digest_url:
        return ""
    try:
        r = client.get(plan.digest_url, timeout=10)
        if r.status_code == 200:
            # Sidecars are usually "<hex>  <filename>" or bare hex.
            m = re.search(r"\b([0-9a-fA-F]{64})\b", r.text)
            return m.group(1) if m else ""
    except Exception:
        pass
    return ""


# ── smoke test ────────────────────────────────────────────────────────────


@dataclass
class SmokeResult:
    checks: list[tuple[str, bool, str]] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append((name, ok, detail))

    @property
    def ok(self) -> bool:
        return all(ok for _, ok, _ in self.checks)


def smoke_test(query: str = "battle through the heavens") -> SmokeResult:
    """Prove the end-to-end path is wired: a source answers and a player exists.

    Deliberately light — one real search (network) plus a local player check —
    so it runs in a couple of seconds and degrades gracefully offline.
    """
    result = SmokeResult()

    player_status = detect(get_tool("mpv"))  # type: ignore[arg-type]
    if not player_status.ok and shutil.which("vlc"):
        result.add("player", True, "vlc (mpv not found)")
    else:
        result.add("player", player_status.ok,
                   player_status.version or "mpv not found — playback will fail")

    try:
        from donghua_cli.scraper import search_all
        hits = search_all(query)
        result.add("source reachable", bool(hits),
                   f"{len(hits)} result(s) for '{query}'" if hits else "no source answered")
    except Exception as e:
        result.add("source reachable", False, f"search errored: {e}")

    return result


# ── rendering / orchestration ─────────────────────────────────────────────


def _status_line(st: ToolStatus) -> None:
    tool = st.tool
    if st.ok:
        tag = f"[accent.alt]{GLYPH['ok']}[/]"
        where = "[faint](managed)[/]" if st.source == "managed" else ""
        ver = f"[faint]{st.version}[/]" if st.version else ""
        console.print(f"  {tag} [text]{tool.label:<14}[/] {ver} {where}")
    else:
        glyph = GLYPH["fail"]
        colour = "danger" if tool.required else "accent"
        role = "required" if tool.required else "optional"
        console.print(
            f"  [{colour}]{glyph}[/] [text]{tool.label:<14}[/] "
            f"[{colour}]missing[/] [faint]({role} · {tool.unlocks})[/]"
        )


def run_doctor(fetch: bool = False, do_smoke: bool = True) -> int:
    """Render the full diagnostic. Returns a process exit code (0 = healthy)."""
    from donghua_cli import ui

    ui.show_banner()
    theme.section_header("Diagnostics", "Environment Doctor",
                         "Checking the tools Donghua CLI shells out to")

    statuses = detect_all()
    for st in statuses:
        _status_line(st)
    console.print()

    missing = [st for st in statuses if not st.ok]
    missing_required = [st for st in missing if st.tool.required]

    if missing:
        theme.section_header("Remedy", "Install what's missing")
        for st in missing:
            tool = st.tool
            hint = delegate_hint(tool)
            plan_note = ""
            if fetch and fetchable(tool):
                theme.status("loading", f"Fetching {tool.label}…")
                plan = plan_fetch(tool)
                if plan:
                    ok, msg = fetch_tool(plan)
                    theme.status("success" if ok else "error", f"{tool.label}: {msg}")
                    if ok:
                        continue
                else:
                    theme.status("warning", f"{tool.label}: no static build for this OS/arch")
            if hint:
                console.print(f"  [accent.bold]{tool.label}[/] [ghost]»[/] [text]{hint}[/]")
            elif fetchable(tool):
                plan_note = "auto-fetch with [accent]donghua doctor --fetch[/]"
                console.print(f"  [accent.bold]{tool.label}[/] [ghost]»[/] [faint]{plan_note}[/]")
            else:
                console.print(f"  [accent.bold]{tool.label}[/] [ghost]»[/] [faint]see the project README[/]")
        console.print()
        if fetch:
            _print_path_note()

    if do_smoke:
        theme.section_header("Smoke test", "End-to-end check")
        res = smoke_test()
        for name, ok, detail in res.checks:
            theme.status("success" if ok else "error", f"{name}: {detail}")
        console.print()

    if missing_required:
        theme.status("error", "Core tools missing — streaming won't work until fixed")
        return 1
    theme.status("success", "All core tools present. Enjoy the cultivation!")
    return 0


def _print_path_note() -> None:
    """After a fetch, remind the user managed binaries live in BIN_DIR (which
    the app puts on PATH automatically at startup)."""
    console.print(
        theme.tip_box(
            "Managed binaries",
            f"Fetched tools live in {config.BIN_DIR}\n"
            "Donghua CLI adds this to PATH on launch — no shell config needed.",
        )
    )
