#!/usr/bin/env bash
# Install the random-machine launcher into iTerm2's scripts folder.
#
# It asks iTerm2 where that folder IS rather than assuming. The documented
# default is ~/Library/Application Support/iTerm2/Scripts, but a custom folder
# can be set in Settings > General > Magic, and it lives in a pref key -- not
# on disk. Installing to the default when a custom one is set fails silently:
# the file is there, it compiles, it runs by hand, and iTerm2 never reads it.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LAUNCHER="$ROOT/tools/retro-random"
[[ -x "$LAUNCHER" ]] || { echo "missing $LAUNCHER" >&2; exit 1; }

DEST="$(defaults read com.googlecode.iterm2 CustomScriptsFolder 2>/dev/null || true)"
[[ -n "$DEST" ]] || DEST="$HOME/Library/Application Support/iTerm2/Scripts"
echo "iTerm2 scripts folder: $DEST"

SRC="$(dirname "${BASH_SOURCE[0]}")/random-retro-terminal.applescript"
TMP="$(mktemp -t retro-random-XXXX).applescript"
trap 'rm -f "$TMP"' EXIT
sed "s|@RETRO_RANDOM@|$LAUNCHER|" "$SRC" > "$TMP"

mkdir -p "$DEST/AutoLaunch"
osacompile -o "$DEST/Random Retro Terminal.scpt" "$TMP"
echo "   menu entry  -> $DEST/Random Retro Terminal.scpt"

if [[ "${1:-}" == "--no-autolaunch" ]]; then
  echo "   autolaunch  -> skipped (--no-autolaunch)"
else
  osacompile -o "$DEST/AutoLaunch/retro-random.scpt" "$TMP"
  echo "   autolaunch  -> $DEST/AutoLaunch/retro-random.scpt"
  echo "   (iTerm2 opens its own default window too; turn that off in"
  echo "    Settings > General > Startup if you want only the random one)"
fi
echo "Restart iTerm2 to pick up the Scripts menu."
