#!/usr/bin/env bash
set -euo pipefail

changelog_file="$(mktemp)"
cz bump --changelog-to-stdout --git-output-to-stderr > "$changelog_file"

git push origin main --tags

gh release create "$(cz version -p)" -d -F "$changelog_file"
rm "$changelog_file"
