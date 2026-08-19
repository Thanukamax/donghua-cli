"""CLI entry point -- argument parsing and dispatch."""

import logging
import sys

from donghua_cli import __version__, config


def _setup_logging(log_file: str | None = None, verbose: bool = False) -> None:
    """Configure the donghua logger.

    --logs:    writes to ~/.cache/donghua/donghua.log and tails it
    --verbose: prints debug output to stderr
    """
    logger = logging.getLogger("donghua")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    if log_file:
        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = logging.FileHandler(log_file, mode="w")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    if verbose:
        sh = logging.StreamHandler(sys.stderr)
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(fmt)
        logger.addHandler(sh)


def main() -> None:
    if config.PLATFORM == "windows":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

    # Managed (doctor-fetched) binaries live in BIN_DIR; make them findable.
    config.ensure_bin_on_path()

    import argparse

    parser = argparse.ArgumentParser(
        prog="donghua",
        description="Donghua CLI -- Wuxia-themed terminal streaming client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  donghua                          Interactive TUI mode
  donghua "soul land"              Search and stream
  donghua "btth" -q 1080           Stream at 1080p
  donghua "martial peak" -d        Download mode
  donghua doctor                   Check dependencies + run a smoke test
  donghua doctor --fetch           …and auto-fetch missing static builds
  donghua update                   Update donghua-cli + yt-dlp
  donghua --update --dry-run       …show what would run, change nothing
  donghua --classic                Classic Rich output mode
  donghua --logs                   Show live debug log in a second terminal
  dhua                             Interactive TUI (alias)
""",
    )

    parser.add_argument("query", nargs="?", help="Series to search for (or 'doctor')")
    parser.add_argument("-q", "--quality", default=None, help=f"Video quality (default: {config.get_quality()})")
    parser.add_argument("-d", "--download", action="store_true", help="Download instead of stream")
    parser.add_argument("--classic", action="store_true", help="Use classic Rich output instead of TUI")
    parser.add_argument("--logs", action="store_true", help="Write debug log to file and show path")
    parser.add_argument("--verbose", action="store_true", help="Print debug output to stderr")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the stream cache")
    parser.add_argument("--features", action="store_true", help="Show features and capabilities")
    parser.add_argument("--doctor", action="store_true", help="Check dependencies + run a smoke test")
    parser.add_argument("--fetch", action="store_true", help="With doctor: auto-fetch missing static builds")
    parser.add_argument("--update", action="store_true",
                        help="Check for and install updates (donghua-cli + yt-dlp)")
    parser.add_argument("--dry-run", action="store_true",
                        help="With --update: show what would run, change nothing")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    # Accept the bare subcommand form `donghua doctor` as well as `--doctor`.
    if args.query == "doctor":
        args.doctor = True
        args.query = None
    if args.query == "update":
        args.update = True
        args.query = None

    # Set up logging
    import os
    log_file = None
    if args.logs:
        log_file = os.path.join(config.CACHE_DIR, "donghua.log")
        _setup_logging(log_file=log_file, verbose=False)
        print(f"Logging to: {log_file}")
        print(f"Watch live:  tail -f {log_file}")
        print()
    elif args.verbose:
        _setup_logging(verbose=True)
    else:
        # Silence logs by default
        logging.getLogger("donghua").addHandler(logging.NullHandler())

    if args.update:
        from donghua_cli import updater
        try:
            sys.exit(updater.run_update(dry_run=args.dry_run))
        except KeyboardInterrupt:
            sys.exit(130)

    if args.doctor:
        from donghua_cli import doctor
        try:
            sys.exit(doctor.run_doctor(fetch=args.fetch))
        except KeyboardInterrupt:
            sys.exit(130)

    # Fire-and-forget: a daemon thread with a day-cached verdict. Deliberately
    # after the one-shot subcommands above, which should not pay for it.
    from donghua_cli import updater
    updater.start_background_check()

    from donghua_cli.app import DonghuaCLI
    app_core = DonghuaCLI(quality=args.quality)

    if args.features:
        app_core.show_features()
        return

    if args.clear_cache:
        app_core.clear_cache()
        if not args.query:
            return

    # Classic mode or direct query: use Rich console output
    if args.classic or args.query or args.download:
        try:
            if args.query:
                app_core.run_direct(args.query, download=args.download)
            else:
                app_core.run_interactive()
        except KeyboardInterrupt:
            from donghua_cli import theme
            theme.divider()
            theme.status("info", "Farewell, cultivator!")
            sys.exit(0)
        except Exception as e:
            from donghua_cli import theme
            theme.status("error", f"Fatal: {e}")
            sys.exit(1)
        return

    # Default: Textual TUI mode
    try:
        from donghua_cli.tui import DonghuaTUI
        tui = DonghuaTUI(app_core)
        tui.run()
    except ImportError:
        try:
            app_core.run_interactive()
        except KeyboardInterrupt:
            sys.exit(0)
    except Exception as e:
        from donghua_cli import theme
        theme.status("error", f"TUI error: {e}")
        sys.exit(1)
