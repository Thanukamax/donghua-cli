@echo off
REM Donghua CLI Windows Launcher
REM Double-click this to open Donghua CLI in TUI mode
title Donghua CLI
donghua --tui
if errorlevel 1 (
    echo.
    echo Donghua CLI not found. Run: pip install donghua-cli
    pause
)
