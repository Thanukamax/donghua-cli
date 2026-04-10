#!/bin/bash
# Install .desktop file for Linux application menu integration
DESKTOP_FILE="$(dirname "$0")/donghua-cli.desktop"
DEST="$HOME/.local/share/applications/donghua-cli.desktop"

cp "$DESKTOP_FILE" "$DEST"
chmod 644 "$DEST"
echo "✓ Desktop entry installed to $DEST"
echo "  Donghua CLI should now appear in your application menu."
