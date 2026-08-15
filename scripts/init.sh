#!/usr/bin/env bash
# Run once after cloning from the template to rename all placeholders.
# Usage: bash scripts/init.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# ── helpers ──────────────────────────────────────────────────────────────────
ask() { printf "%s: " "$1"; read -r REPLY; echo "$REPLY"; }

validate_package_name() {
    local name="$1"
    if [[ ! "$name" =~ ^[a-z][a-z0-9_]*$ ]]; then
        echo "Error: package name must be lowercase, start with a letter, and contain only letters, digits, and underscores." >&2
        exit 1
    fi
}

# ── gather info ───────────────────────────────────────────────────────────────
echo ""
echo "=== package-template initializer ==="
echo "Answer the prompts below (press Enter to keep the placeholder)."
echo ""

PKG_NAME=$(ask    "Package name (e.g. my_cool_package)")
GITHUB_ORG=$(ask  "GitHub org / username          (YOUR_ORG)")
AUTHOR=$(ask      "Author full name               (YOUR NAME)")
EMAIL=$(ask       "Author email                   (your@email.com)")
DESCRIPTION=$(ask "One-line description           (SHORT DESCRIPTION OF YOUR PACKAGE)")

validate_package_name "$PKG_NAME"

# ── replace in files ──────────────────────────────────────────────────────────
echo ""
echo "Replacing placeholders..."

# Files to process (exclude .git, binary-like assets, and this script itself)
FILES=$(git ls-files | grep -v 'scripts/init.sh' | grep -v '\.svg$' | grep -v '\.png$' | grep -v '\.ico$')

for f in $FILES; do
    [ -f "$f" ] || continue
    sed -i '' \
        -e "s|package_name|${PKG_NAME}|g" \
        -e "s|YOUR_ORG|${GITHUB_ORG}|g" \
        -e "s|YOUR_GITHUB_USERNAME|${GITHUB_ORG}|g" \
        -e "s|YOUR NAME|${AUTHOR}|g" \
        -e "s|YOUR_LAST_NAME|${AUTHOR##* }|g" \
        -e "s|YOUR_FIRST_NAME|${AUTHOR%% *}|g" \
        -e "s|your@email\.com|${EMAIL}|g" \
        -e "s|SHORT DESCRIPTION OF YOUR PACKAGE|${DESCRIPTION}|g" \
        -e "s|SHORT DESCRIPTION|${DESCRIPTION}|g" \
        "$f"
done

# ── rename source directory ───────────────────────────────────────────────────
if [ -d "src/package_name" ] && [ "$PKG_NAME" != "package_name" ]; then
    git mv "src/package_name" "src/${PKG_NAME}"
    echo "Renamed src/package_name → src/${PKG_NAME}"
fi

# ── done ─────────────────────────────────────────────────────────────────────
echo ""
echo "Done! See CHECKLIST.md for next steps."
