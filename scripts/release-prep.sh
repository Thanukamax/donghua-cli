#!/usr/bin/env bash
# Bump the AUR PKGBUILD + Homebrew formula + Scoop manifest to the latest
# published PyPI sdist. Run AFTER `twine upload` succeeds, BEFORE merging
# release-bump back into main. The publish.yml workflow runs this for you;
# you only need it locally when CI is bypassed.
#
# Usage:  scripts/release-prep.sh [<version>]
#   - With no arg, reads the version from src/donghua_cli/__init__.py.

set -euo pipefail

cd "$(dirname "$0")/.."

VERSION="${1:-$(python3 -c 'import re,sys; print(re.search(r"\"([^\"]+)\"", open("src/donghua_cli/__init__.py").read()).group(1))')}"
SDIST_URL="https://files.pythonhosted.org/packages/source/d/donghua-cli/donghua_cli-${VERSION}.tar.gz"

echo "Fetching sdist for v${VERSION}..."
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

# PyPI propagation can lag a few seconds after twine upload returns.
for i in 1 2 3 4 5 6; do
    if curl -sfL "$SDIST_URL" -o "$tmp"; then
        break
    fi
    echo "  waiting for PyPI (attempt $i)..."
    sleep 5
done

if [[ ! -s "$tmp" ]]; then
    echo "ERROR: couldn't fetch $SDIST_URL after retries." >&2
    exit 1
fi

SHA=$(sha256sum "$tmp" | cut -d' ' -f1)
echo "sha256: $SHA"

# AUR PKGBUILD
sed -i "s/^pkgver=.*/pkgver=${VERSION}/" packaging/aur/PKGBUILD
sed -i "s/^sha256sums=.*/sha256sums=('${SHA}')/" packaging/aur/PKGBUILD
echo "  + AUR PKGBUILD updated"

# Homebrew formula
sed -i "s|^  url \".*\"$|  url \"${SDIST_URL}\"|" packaging/homebrew/donghua-cli.rb
sed -i "s/^  sha256 \".*\"$/  sha256 \"${SHA}\"/" packaging/homebrew/donghua-cli.rb
echo "  + Homebrew formula updated"

# Scoop manifest (uses the Windows EXE artifact, not the sdist — Scoop's
# autoupdate fetches the EXE hash from the SHA256SUMS release artifact, so
# we only need to bump the version pin here.)
sed -i "s/\"version\": \".*\"/\"version\": \"${VERSION}\"/" packaging/scoop/donghua-cli.json
sed -i "s|releases/download/v[0-9.]*/donghua.exe|releases/download/v${VERSION}/donghua.exe|" packaging/scoop/donghua-cli.json
echo "  + Scoop manifest updated"

echo ""
echo "Done. Commit and push the bumped formulas:"
echo "  git add packaging/ && git commit -m \"chore: bump formulas to v${VERSION}\""
