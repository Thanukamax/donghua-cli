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
  donghua --classic                Classic Rich output mode
  donghua --logs                   Show live debug log in a second terminal
  dhua                             Interactive TUI (alias)
""",
    )

    parser.add_argument("query", nargs="?", help="Series to search for")
    parser.add_argument("-q", "--quality", default=None, help=f"Video quality (default: {config.get_quality()})")
    parser.add_argument("-d", "--download", action="store_true", help="Download instead of stream")
    parser.add_argument("--classic", action="store_true", help="Use classic Rich output instead of TUI")
    parser.add_argument("--logs", action="store_true", help="Write debug log to file and show path")
    parser.add_argument("--verbose", action="store_true", help="Print debug output to stderr")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the stream cache")
    parser.add_argument("--features", action="store_true", help="Show features and capabilities")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

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
