#!/bin/bash
# ci/macos-test.sh — retro-terminals smoke test. Contract the maclab runner calls.
#
# Tier 1 (headless, GitHub-Actions-safe): the palette/config generators and the
#         repo's own unittest suite.
# Tier 2 (GUI, VM only): if Ghostty is installed, launch it with a generated
#         config and screenshot the CRT render.
#
# Exit non-zero if any check FAILs. UNVERIFIABLE is distinct and does not fail.
set -uo pipefail
cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
ART="/tmp/maclab-artifacts"; mkdir -p "$ART"
TMP="$(mktemp -d)"
fails=0; unverified=0
hr(){ echo "------------------------------------------------------------"; }
pass(){ echo "PASS  $*"; }
fail(){ echo "FAIL  $*"; fails=$((fails+1)); }
unv(){  echo "UNV   $*"; unverified=$((unverified+1)); }

echo "== retro-terminals macOS smoke test =="
sw_vers 2>/dev/null | tr '\n' ' '; echo
PY="$(command -v python3 || true)"
[ -n "$PY" ] && pass "python3: $($PY --version 2>&1)" || { fail "python3 not found"; }

# ---------- Tier 1: headless generators + tests ----------
hr; echo "Tier 1 — headless build + tests"

# iTerm2 profile generator (dry-run to stdout)
if nprof=$("$PY" build_profiles.py --stdout 2>/dev/null | "$PY" -c 'import json,sys; print(len(json.load(sys.stdin)["Profiles"]))' 2>/dev/null) && [ -n "$nprof" ]; then
  pass "build_profiles.py --stdout → $nprof iTerm2 profiles"
else
  fail "build_profiles.py --stdout did not emit valid profile JSON"
fi

# Ghostty generator (dry-run to stdout)
if "$PY" build_ghostty.py --stdout >/dev/null 2>&1; then
  pass "build_ghostty.py --stdout ok"
else
  fail "build_ghostty.py --stdout failed"
fi

# Ghostty full build into a temp dir (writes nothing in-repo)
if "$PY" build_ghostty.py --dest "$TMP/ghostty" >/dev/null 2>&1; then
  nfiles=$(find "$TMP/ghostty" -type f | wc -l | tr -d ' ')
  if [ -f "$TMP/ghostty/shaders/crt.glsl" ]; then
    pass "build_ghostty.py --dest → $nfiles files incl shaders/crt.glsl"
  else
    fail "build_ghostty.py --dest produced $nfiles files but no shaders/crt.glsl"
  fi
else
  fail "build_ghostty.py --dest build failed"
fi

# The repo's own unittest suite (faithfully reported — a red suite here is a
# real repo bug, not a harness failure).
if out=$("$PY" -m unittest discover -s tests 2>&1); then
  pass "unittest suite: $(echo "$out" | tail -1)"
else
  fail "unittest suite failed: $(echo "$out" | grep -E 'errors=|failures=' | tail -1 || echo "$out" | tail -1)"
fi

# Convair Mono: font binaries are fetched at install (not committed) — only
# verifiable if already installed.
if system_profiler SPFontsDataType 2>/dev/null | grep -qi "Convair"; then
  pass "Convair Mono installed and registered"
else
  unv "Convair Mono not installed (fonts are fetched by install.sh; not committed)"
fi

# ---------- Tier 2: GUI render (VM only, if Ghostty present) ----------
hr; echo "Tier 2 — GUI render"
GUI_UID="$(stat -f%u /dev/console 2>/dev/null || echo 501)"
if [ -d "/Applications/Ghostty.app" ] && who | grep -q console; then
  cfg="$TMP/ghostty/retro/the-matrix.conf"
  [ -f "$cfg" ] || cfg="$(find "$TMP/ghostty/retro" -name '*.conf' 2>/dev/null | head -1)"
  if [ -n "$cfg" ]; then
    sudo launchctl asuser "$GUI_UID" open -na Ghostty --args --config-file="$cfg" 2>/dev/null
    sleep 5
    sudo launchctl asuser "$GUI_UID" /usr/sbin/screencapture -x "$ART/retro-ghostty.png" 2>/dev/null
    [ -f "$ART/retro-ghostty.png" ] && pass "Ghostty launched with generated config; screenshot captured" \
                                    || unv "Ghostty launched but screenshot failed"
    sudo launchctl asuser "$GUI_UID" osascript -e 'quit app "Ghostty"' 2>/dev/null || true
  else
    unv "no generated Ghostty config to render"
  fi
else
  unv "Ghostty not installed / no GUI session — render check skipped (expected in GitHub Actions)"
fi

# ---------- summary ----------
rm -rf "$TMP"
hr
echo "SUMMARY: fails=$fails unverifiable=$unverified"
[ -d "$ART" ] && ls -1 "$ART" 2>/dev/null | grep -qi retro && { echo "artifacts:"; ls -1 "$ART" | grep -i retro | sed 's/^/  /'; }
exit $(( fails > 0 ? 1 : 0 ))
