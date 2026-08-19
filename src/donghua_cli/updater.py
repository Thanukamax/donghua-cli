"""Update checks for donghua-cli and yt-dlp.

Two things rot on different clocks and both end as "the player stopped working":

* **yt-dlp** — the sites change, yt-dlp ships a fix, and a months-old build
  silently fails to extract. yt-dlp warns about its own age but only on the
  paths that shell out to it, which the user rarely sees.
* **donghua-cli** — scraper fixes only help someone running them.

Policy is notify-by-default, never mutate on its own: the check runs on a
background thread with a cached verdict, prints one line, and waits for an
explicit ``donghua --update``. Silently reinstalling a user's tooling mid-session
can break a working setup, and a streaming client has no business doing that
without being asked.

The check must never delay startup — this is a client with a
"time-to-first-frame" budget — so every network call here is off the hot path
and every failure is non-fatal.
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Optional

from donghua_cli import config
from donghua_cli.__init__ import __version__

log = logging.getLogger("donghua")

PYPI_JSON = "https://pypi.org/pypi/{pkg}/json"

#: How long a verdict stays good. Long enough that normal use checks about once
#: a day, short enough that a fix lands within a day of shipping.
CHECK_INTERVAL = 24 * 3600

#: Network budget for the whole check. It runs off the hot path, but a hung
#: socket would still keep a daemon thread (and the interpreter) alive.
TIMEOUT = 6

STATE_FILE = os.path.join(config.CACHE_DIR, "update-check.json")


# ── version comparison ────────────────────────────────────────────────────


def parse_version(v: str) -> tuple[int, ...]:
    """Numeric release tuple for a version string.

    Handles both schemes in play here: donghua-cli's semver (``3.2.1``) and
    yt-dlp's date versions (``2026.02.04``). Comparing those as tuples of ints
    is correct for both, and avoids taking a dependency on ``packaging`` just to
    order two numbers — this deliberately does not implement PEP 440, because
    neither package uses anything beyond plain numeric releases.

    Any pre-release/local suffix is dropped, so ``1.2.0rc1`` compares equal to
    ``1.2.0``. That is the safe direction: it can only suppress an update
    prompt, never fabricate one.
    """
    # Only the LEADING dotted-numeric run counts. Scraping every digit in the
    # string would read "3.2.1rc1" as (3,2,1,1) and rank a release candidate
    # above its own final release.
    m = re.match(r"\s*v?(\d+(?:\.\d+)*)", v or "")
    if not m:
        return (0,)
    return tuple(int(n) for n in m.group(1).split("."))


def is_newer(latest: str, current: str) -> bool:
    """True when ``latest`` is a strictly higher release than ``current``."""
    if not latest or not current:
        return False
    return parse_version(latest) > parse_version(current)


# ── install-method detection ──────────────────────────────────────────────


@dataclass(frozen=True)
class Install:
    """How a package got onto this machine, and the command that updates it."""

    method: str                 # 'pipx' | 'uv' | 'pip' | 'source' | 'system'
    command: tuple[str, ...]    # argv that performs the upgrade
    note: str = ""              # shown when we cannot update it ourselves

    @property
    def updatable(self) -> bool:
        return bool(self.command)


def _detect_self_install() -> Install:
    """Work out how *this* donghua-cli was installed.

    Path shape is the reliable signal: pipx and `uv tool` each own a predictable
    venv layout, and an editable/source checkout has no site-packages copy at
    all. Getting this wrong is worse than not updating — running `pip install -U`
    inside a pipx venv half-breaks it — so anything unrecognised returns a hint
    instead of a guess.
    """
    prefix = os.path.realpath(sys.prefix).replace("\\", "/")
    exe = sys.executable

    if "/pipx/venvs/" in prefix:
        return Install("pipx", ("pipx", "upgrade", "donghua-cli"))
    if "/uv/tools/" in prefix:
        return Install("uv", ("uv", "tool", "upgrade", "donghua-cli"))

    # An editable install points at the working tree, not site-packages.
    pkg_dir = os.path.realpath(os.path.dirname(__file__)).replace("\\", "/")
    if "/site-packages/" not in pkg_dir + "/":
        return Install(
            "source", (),
            note="running from a source checkout — update with git, not the installer",
        )

    return Install("pip", (exe, "-m", "pip", "install", "--upgrade", "donghua-cli"))


def _detect_ytdlp_install() -> Install:
    """Work out how yt-dlp got here, so we upgrade it the way it was installed."""
    import shutil

    path = shutil.which("yt-dlp")
    if not path:
        return Install("missing", (), note="yt-dlp is not installed — run `donghua doctor --fetch`")
    real = os.path.realpath(path).replace("\\", "/")

    if "/pipx/venvs/" in real:
        return Install("pipx", ("pipx", "upgrade", "yt-dlp"))
    if "/uv/tools/" in real:
        return Install("uv", ("uv", "tool", "upgrade", "yt-dlp"))
    # A distro package must be updated by the distro; pip would fight it.
    if real.startswith(("/usr/bin/", "/usr/local/bin/", "/bin/")):
        return Install("system", (), note="installed by your package manager — update it there")
    if os.path.realpath(config.BIN_DIR).replace("\\", "/") in real:
        return Install("managed", (), note="fetched by `donghua doctor --fetch` — re-run it to refresh")

    # A pip-installed yt-dlp belongs to whichever interpreter created it, which
    # is almost never the one running us: donghua-cli is typically its own pipx
    # venv while yt-dlp sits in `pip --user` against the system python. Using
    # `sys.executable` here would install a SECOND yt-dlp inside our venv and
    # leave the one on PATH untouched — an "update" that changes nothing.
    # The console script's shebang names its real owner, so use that.
    interp, user_site = _script_interpreter(real)
    cmd = [interp or sys.executable, "-m", "pip", "install", "--upgrade"]
    if user_site:
        cmd.append("--user")
    cmd.append("yt-dlp")
    return Install("pip", tuple(cmd))


def _script_interpreter(script_path: str) -> tuple[Optional[str], bool]:
    """The interpreter a console script was generated for, and whether it looks
    like a per-user (``pip --user``) install.

    Returns ``(None, ...)`` when the shebang is unreadable or not a real path;
    callers fall back to ``sys.executable``.
    """
    try:
        with open(script_path, "rb") as f:
            first = f.readline(512).decode("utf-8", "replace").strip()
    except OSError:
        return None, False
    interp = first[2:].strip() if first.startswith("#!") else ""
    # `#!/usr/bin/env python3` names the launcher, not the interpreter.
    if interp.startswith("/usr/bin/env "):
        interp = interp.split(None, 1)[1].strip()
    if not interp or not os.path.isabs(interp) or not os.path.exists(interp):
        return None, False
    # Do NOT realpath the interpreter: a venv's `python3` is a symlink to the
    # system one, so resolving it makes every venv look like a --user install.
    # The reliable signal is a pyvenv.cfg beside the interpreter's directory.
    venv_marker = os.path.join(os.path.dirname(os.path.dirname(interp)), "pyvenv.cfg")
    if os.path.exists(venv_marker):
        return interp, False

    # Not a venv: a script under $HOME on a system interpreter is the classic
    # `pip install --user` shape, and upgrading it needs --user too.
    home = os.path.realpath(os.path.expanduser("~"))
    in_home = os.path.realpath(script_path).startswith(home + os.sep)
    return interp, in_home


def _installed_ytdlp_version() -> Optional[str]:
    import shutil

    path = shutil.which("yt-dlp")
    if not path:
        return None
    try:
        out = subprocess.run(
            [path, "--version"], capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError) as e:
        log.debug("yt-dlp --version failed: %s", e)
        return None
    return (out.stdout or "").strip().splitlines()[0].strip() if out.stdout.strip() else None


# ── PyPI lookup ───────────────────────────────────────────────────────────


def latest_pypi_version(pkg: str) -> Optional[str]:
    """Newest release of ``pkg`` on PyPI, or None if the lookup failed.

    Never raises: an update check that breaks the app is worse than one that
    silently does nothing.
    """
    try:
        from donghua_cli.utils import get_client

        resp = get_client().get(PYPI_JSON.format(pkg=pkg), timeout=TIMEOUT)
        if resp.status_code != 200:
            log.debug("PyPI lookup for %s: HTTP %s", pkg, resp.status_code)
            return None
        return (resp.json().get("info") or {}).get("version")
    except Exception as e:  # network, JSON, client construction — all non-fatal
        log.debug("PyPI lookup for %s failed: %s", pkg, e)
        return None


# ── cached verdict ────────────────────────────────────────────────────────


@dataclass
class Update:
    """One package that has a newer release available."""

    package: str
    current: str
    latest: str
    install: Install


def _read_state() -> dict:
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _write_state(state: dict) -> None:
    try:
        os.makedirs(config.CACHE_DIR, exist_ok=True)
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f)
        os.replace(tmp, STATE_FILE)
    except OSError as e:
        log.debug("could not persist update state: %s", e)


def check(force: bool = False) -> list[Update]:
    """Packages with a newer release, hitting the network at most daily.

    ``force`` skips the cache — used by ``--update``, where the user is asking
    right now and a day-old verdict is not good enough.
    """
    state = _read_state()
    fresh = time.time() - float(state.get("at", 0)) < CHECK_INTERVAL
    if not force and fresh:
        return _from_cache(state)

    found: list[Update] = []
    cached: dict[str, str] = {}

    latest = latest_pypi_version("donghua-cli")
    if latest:
        cached["donghua-cli"] = latest
        if is_newer(latest, __version__):
            found.append(Update("donghua-cli", __version__, latest, _detect_self_install()))

    yt_current = _installed_ytdlp_version()
    yt_latest = latest_pypi_version("yt-dlp")
    if yt_latest:
        cached["yt-dlp"] = yt_latest
        if yt_current and is_newer(yt_latest, yt_current):
            found.append(Update("yt-dlp", yt_current, yt_latest, _detect_ytdlp_install()))

    _write_state({"at": time.time(), "latest": cached})
    return found


def _from_cache(state: dict) -> list[Update]:
    """Re-derive the verdict from cached *latest* versions.

    Only the remote lookup is cached; installed versions are re-read every time,
    so the notice disappears the moment an update is actually applied instead of
    lingering until the cache expires.
    """
    latest = state.get("latest") or {}
    out: list[Update] = []

    self_latest = latest.get("donghua-cli")
    if self_latest and is_newer(self_latest, __version__):
        out.append(Update("donghua-cli", __version__, self_latest, _detect_self_install()))

    yt_latest = latest.get("yt-dlp")
    yt_current = _installed_ytdlp_version()
    if yt_latest and yt_current and is_newer(yt_latest, yt_current):
        out.append(Update("yt-dlp", yt_current, yt_latest, _detect_ytdlp_install()))
    return out


# ── background notice ─────────────────────────────────────────────────────

_pending: list[Update] = []


def start_background_check() -> None:
    """Kick the check off on a daemon thread. Never blocks startup."""
    if not config.get_update_check():
        return

    def run() -> None:
        try:
            _pending.extend(check())
        except Exception as e:  # a broken check must never surface to the user
            log.debug("background update check failed: %s", e)

    threading.Thread(target=run, name="update-check", daemon=True).start()


def pending() -> list[Update]:
    """Whatever the background check found, if it has finished. Never waits."""
    return list(_pending)


def format_notice(updates: list[Update]) -> str:
    """One-line-per-package notice, with the command that applies it."""
    lines = []
    for u in updates:
        lines.append(f"{u.package} {u.current} → {u.latest}")
    return "update available: " + "; ".join(lines) + "  ·  run `donghua --update`"


# ── applying ──────────────────────────────────────────────────────────────


def apply(updates: list[Update], dry_run: bool = False) -> int:
    """Run each package's upgrade command. Returns a process-style exit code.

    Anything we cannot update safely (distro packages, source checkouts) is
    reported with the reason rather than attempted — a wrong upgrade command is
    how you end up with a half-broken venv.
    """
    from donghua_cli import theme
    from donghua_cli.palette import GLYPH

    console = theme.console
    if not updates:
        console.print(f"  {GLYPH['ok']} everything is up to date")
        return 0

    failed = 0
    for u in updates:
        head = f"{u.package} {u.current} → {u.latest}"
        if not u.install.updatable:
            console.print(f"  {GLYPH['fail']} {head}: {u.install.note}")
            failed += 1
            continue
        shown = " ".join(u.install.command)
        if dry_run:
            console.print(f"  {GLYPH['pending']} would run: {shown}")
            continue
        console.print(f"  {GLYPH['pending']} {head}  ({shown})")
        try:
            rc = subprocess.run(u.install.command, check=False).returncode
        except (OSError, subprocess.SubprocessError) as e:
            console.print(f"  {GLYPH['fail']} {u.package}: {e}")
            failed += 1
            continue
        if rc == 0:
            console.print(f"  {GLYPH['ok']} {u.package} updated")
        else:
            console.print(f"  {GLYPH['fail']} {u.package}: exit {rc}")
            failed += 1
    return 1 if failed else 0


def run_update(dry_run: bool = False) -> int:
    """`donghua --update` — check now, then apply."""
    from donghua_cli import theme
    from donghua_cli.palette import GLYPH

    console = theme.console
    console.print(f"  {GLYPH['pending']} checking for updates…")
    return apply(check(force=True), dry_run=dry_run)
