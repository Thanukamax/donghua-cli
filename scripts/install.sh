#!/bin/bash
# Donghua CLI Installer (Linux / macOS / Termux)
# Installs via pip and sets up shell aliases

set -e

echo "╔══════════════════════════════════════╗"
echo "║       Donghua CLI Installer          ║"
echo "║   武侠动画终端 · v3.1.0              ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Detect Python
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ Python not found. Install Python 3.9+ first."
    echo "   Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "   Fedora:        sudo dnf install python3 python3-pip"
    echo "   macOS:         brew install python"
    echo "   Termux:        pkg install python"
    exit 1
fi

PY_VER=$($PYTHON --version 2>&1)
echo "✓ Found $PY_VER"

# Install via pip
echo ""
echo "Installing donghua-cli..."
if command -v pipx &>/dev/null; then
    pipx install donghua-cli 2>/dev/null || pipx upgrade donghua-cli
    echo "✓ Installed via pipx"
else
    $PYTHON -m pip install --user donghua-cli
    echo "✓ Installed via pip (--user)"
fi

# Check for mpv
echo ""
if command -v mpv &>/dev/null; then
    echo "✓ mpv found"
elif command -v vlc &>/dev/null; then
    echo "✓ vlc found (mpv recommended for better experience)"
else
    echo "⚠ No video player found. Install mpv:"
    echo "   Ubuntu/Debian: sudo apt install mpv"
    echo "   Fedora:        sudo dnf install mpv"
    echo "   macOS:         brew install mpv"
    echo "   Termux:        pkg install mpv"
fi

# Detect shell config
RC_FILE="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
    RC_FILE="$HOME/.zshrc"
fi

# Add quality aliases if not already present
if ! grep -q "Donghua CLI" "$RC_FILE" 2>/dev/null; then
    echo ""
    echo "Adding shell aliases to $RC_FILE..."
    cp "$RC_FILE" "${RC_FILE}.bak" 2>/dev/null || true
    cat >> "$RC_FILE" << 'ALIASES'

# Donghua CLI Aliases
alias dhua360='donghua --quality 360'
alias dhua480='donghua --quality 480'
alias dhua720='donghua --quality 720'
alias dhua1080='donghua --quality 1080'
alias dhuadl='donghua --download'
ALIASES
    echo "✓ Aliases added (dhua360, dhua720, dhua1080, dhuadl)"
else
    echo "✓ Aliases already configured"
fi

echo ""
echo "══════════════════════════════════════"
echo "  ✓ Installation complete!"
echo ""
echo "  Usage:"
echo "    dhua                  # interactive mode"
echo "    donghua \"Soul Land\"   # direct search"
echo "    dhua --tui            # full-screen TUI"
echo "    dhua --download \"..\" # download mode"
echo ""
echo "  Restart your shell or run: source $RC_FILE"
echo "══════════════════════════════════════"
