"""In-app updating: the capturing runner, the frozen-exe guard, and the TUI's
/update command + update strip."""

import asyncio
import subprocess
import sys

import pytest

from donghua_cli import updater


def _update(cmd=("pipx", "upgrade", "donghua-cli"), note=""):
    return updater.Update("donghua-cli", "4.0.0", "4.1.0", updater.Install("pipx", cmd, note))


class TestRunOne:
    def test_success_reports_new_version(self, monkeypatch):
        monkeypatch.setattr(updater.subprocess, "run",
                            lambda *a, **k: subprocess.CompletedProcess(a, 0, "", ""))
        r = updater.run_one(_update(), capture=True)
        assert r.ok and "4.1.0" in r.message

    def test_failure_surfaces_the_installers_last_line(self, monkeypatch):
        err = "Collecting donghua-cli\nERROR: No matching distribution found\n\n"
        monkeypatch.setattr(updater.subprocess, "run",
                            lambda *a, **k: subprocess.CompletedProcess(a, 1, "", err))
        r = updater.run_one(_update(), capture=True)
        assert not r.ok
        assert r.message == "ERROR: No matching distribution found"

    def test_capture_keeps_output_off_the_terminal(self, monkeypatch):
        seen = {}

        def fake_run(cmd, **kw):
            seen.update(kw)
            return subprocess.CompletedProcess(cmd, 0, "", "")

        monkeypatch.setattr(updater.subprocess, "run", fake_run)
        updater.apply_quiet([_update()])
        assert seen["capture_output"] is True
        assert seen["timeout"] == updater.APPLY_TIMEOUT

    def test_unupdatable_install_is_not_attempted(self, monkeypatch):
        def boom(*a, **k):
            raise AssertionError("must not run")

        monkeypatch.setattr(updater.subprocess, "run", boom)
        r = updater.run_one(_update(cmd=(), note="source checkout"), capture=True)
        assert not r.ok and r.message == "source checkout"

    def test_missing_installer_binary_is_a_result_not_a_crash(self, monkeypatch):
        def missing(*a, **k):
            raise FileNotFoundError("pipx")

        monkeypatch.setattr(updater.subprocess, "run", missing)
        r = updater.run_one(_update(), capture=True)
        assert not r.ok and "pipx" in r.message


def test_frozen_exe_never_runs_pip_on_itself(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    inst = updater._detect_self_install()
    assert not inst.updatable
    assert "donghua.exe" in inst.note


# ── TUI ────────────────────────────────────────────────────────────────


@pytest.fixture
def tui_app(monkeypatch):
    from donghua_cli import library
    from donghua_cli.tui import DonghuaTUI

    monkeypatch.setattr(library, "recent_history", lambda limit=3: [])
    monkeypatch.setattr(library, "list_bookmarks", lambda: [])
    monkeypatch.setattr(updater, "pending", lambda: [])
    return DonghuaTUI(app_core=None)


def _run(coro):
    asyncio.run(coro)


def test_slash_update_runs_the_updater_and_reports(tui_app, monkeypatch):
    from donghua_cli.tui import SearchScreen

    applied = []
    monkeypatch.setattr(updater, "check", lambda force=False: [_update()])
    monkeypatch.setattr(updater, "apply_quiet", lambda ups: (
        applied.extend(ups) or [updater.Result(ups[0], True, "donghua-cli updated to 4.1.0")]))
    searched = []
    monkeypatch.setattr(SearchScreen, "_do_search", lambda self, q: searched.append(q))

    async def go():
        async with tui_app.run_test() as pilot:
            await pilot.press(*"/update", "enter")
            await tui_app.workers.wait_for_complete()
            await pilot.pause()
            notes = [n.message for n in tui_app._notifications]
            assert any("4.1.0" in m and "Restart" in m for m in notes)
            assert tui_app.screen.query_one("#search-input").value == ""

    _run(go())
    assert [u.latest for u in applied] == ["4.1.0"]
    assert searched == []  # a command is never sent to the scrapers


def test_unknown_slash_command_warns_instead_of_searching(tui_app, monkeypatch):
    from donghua_cli.tui import SearchScreen

    searched = []
    monkeypatch.setattr(SearchScreen, "_do_search", lambda self, q: searched.append(q))

    async def go():
        async with tui_app.run_test() as pilot:
            await pilot.press(*"/nope", "enter")
            await pilot.pause()
            assert any("Unknown command /nope" in n.message for n in tui_app._notifications)

    _run(go())
    assert searched == []


def test_background_verdict_shows_a_clickable_strip(tui_app, monkeypatch):
    monkeypatch.setattr(updater, "pending", lambda: [_update()])

    async def go():
        async with tui_app.run_test() as pilot:
            await pilot.pause(1.3)
            strip = tui_app.screen.query_one("#update-strip")
            assert strip.has_class("shown") and strip.has_class("actionable")
            assert "4.1.0" in str(strip.render())

    _run(go())


def test_up_to_date_says_so(tui_app, monkeypatch):
    monkeypatch.setattr(updater, "check", lambda force=False: [])

    async def go():
        async with tui_app.run_test() as pilot:
            await pilot.press(*"/update", "enter")
            await tui_app.workers.wait_for_complete()
            await pilot.pause()
            assert any("latest version" in n.message for n in tui_app._notifications)
            assert not tui_app.screen.query_one("#update-strip").has_class("shown")

    _run(go())
