#!/usr/bin/env bash
# install-fonts.sh — fetch the free retro fonts the profiles reference, into
# ~/Library/Fonts. All are free / redistributable; sources are documented in
# INSTALL.md. Safe to re-run (skips what's already present).
set -uo pipefail

FONTDIR="$HOME/Library/Fonts"
mkdir -p "$FONTDIR"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

have() { system_profiler SPFontsDataType 2>/dev/null | grep -qi "Family: $1"; }
valid() { case "$(file -b "$1" 2>/dev/null)" in *TrueType*|*OpenType*|*Zip*) return 0;; *) return 1;; esac; }

echo "==> Homebrew casks (Terminus, IBM 3270, Departure Mono)"
if command -v brew >/dev/null 2>&1; then
  for c in font-terminus font-3270 font-departure-mono; do
    brew install --cask "$c" >/dev/null 2>&1 && echo "   ok: $c" || echo "   (already installed or failed: $c)"
  done
else
  echo "   brew not found — install Homebrew or add these fonts manually."
fi

echo "==> Glass TTY VT220 (sensi.org)"
if ! have "Glass TTY VT220"; then
  curl -fsSL -A "$UA" "https://sensi.org/~svo/glasstty/Glass_TTY_VT220.ttf" -o "$TMP/glasstty.ttf" \
    && valid "$TMP/glasstty.ttf" && cp "$TMP/glasstty.ttf" "$FONTDIR/Glass_TTY_VT220.ttf" && echo "   ok" || echo "   FAILED"
else echo "   present"; fi

echo "==> C64 Pro Mono (style64.org)"
if ! have "C64 Pro Mono"; then
  curl -fsSL -A "$UA" "https://style64.org/file/C64_TrueType_v1.2.1-STYLE.zip" -o "$TMP/c64.zip" \
    && valid "$TMP/c64.zip" && unzip -oq "$TMP/c64.zip" -d "$TMP/c64" \
    && find "$TMP/c64" -iname "C64_Pro_Mono-STYLE.ttf" -exec cp {} "$FONTDIR/" \; && echo "   ok" || echo "   FAILED"
else echo "   present"; fi

echo "==> Print Char 21 — Apple ][ (kreativekorp.com)"
if ! have "Print Char 21"; then
  curl -fsSL -A "$UA" "https://www.kreativekorp.com/swdownload/fonts/retro/pr.zip" -o "$TMP/pr.zip" \
    && valid "$TMP/pr.zip" && unzip -oq "$TMP/pr.zip" -d "$TMP/pr" \
    && find "$TMP/pr" -iname "PrintChar21.ttf" -exec cp {} "$FONTDIR/" \; && echo "   ok" || echo "   FAILED"
else echo "   present"; fi

echo "==> Bedstead — teletext (bjh21.me.uk)"
if ! have "Bedstead"; then
  curl -fsSL -A "$UA" "https://bjh21.me.uk/bedstead/bedstead.otf" -o "$TMP/bedstead.otf" \
    && valid "$TMP/bedstead.otf" && cp "$TMP/bedstead.otf" "$FONTDIR/Bedstead.otf" && echo "   ok" || echo "   FAILED"
else echo "   present"; fi

echo
echo "Done. (Courier / Menlo are macOS system fonts. ZX Spectrum & Atari"
echo "profiles use Departure Mono as a fallback — no free originals hosted.)"
