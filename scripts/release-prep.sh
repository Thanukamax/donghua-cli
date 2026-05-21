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

# PyPI no longer reliably serves files at the legacy /packages/source/d/<pkg>/
# path from every CDN edge; use the JSON API to discover the canonical sdist
# URL + sha256 directly. Propagation can lag a few seconds after twine upload.
echo "Looking up PyPI metadata for v${VERSION}..."

JSON_URL="https://pypi.org/pypi/donghua-cli/${VERSION}/json"
SDIST_URL=""
SHA=""

for i in 1 2 3 4 5 6 7 8; do
    METADATA="$(curl -sf "$JSON_URL" || true)"
    if [[ -n "$METADATA" ]]; then
        read -r SDIST_URL SHA <<<"$(printf '%s' "$METADATA" | python3 -c '
import json, sys
d = json.load(sys.stdin)
for u in d.get("urls", []):
    if u.get("packagetype") == "sdist":
        print(u["url"], u["digests"]["sha256"])
        break
')"
        if [[ -n "$SDIST_URL" && -n "$SHA" ]]; then
            break
        fi
    fi
    echo "  waiting for PyPI (attempt $i)..."
    sleep 5
done

if [[ -z "$SDIST_URL" || -z "$SHA" ]]; then
    echo "ERROR: couldn't find sdist for donghua-cli ${VERSION} on PyPI after retries." >&2
    exit 1
fi

echo "  sdist:  $SDIST_URL"
echo "  sha256: $SHA"

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
