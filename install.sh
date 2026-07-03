#!/usr/bin/env bash
# install.sh — build all profiles into your personal iTerm2 config.
#
# What it does:
#   1. fetches the free retro fonts into ~/Library/Fonts   (skip: --no-fonts)
#   2. runs build_profiles.py, which writes the profile JSON files into
#      ~/Library/Application Support/iTerm2/DynamicProfiles/  (iTerm2 hot-loads them)
#
# Usage:  ./install.sh            # fonts + profiles
#         ./install.sh --no-fonts # profiles only
set -euo pipefail
cd "$(dirname "$0")"

if [[ "${1:-}" != "--no-fonts" ]]; then
  echo "== Installing fonts =="
  bash ./fonts/install-fonts.sh
  echo
fi

echo "== Building profiles into iTerm2 =="
python3 build_profiles.py

cat <<'EOF'

Installed. In iTerm2:
  • press  ⌘O  and filter by tag:  retro / sci-fi / aesthetic / corp
  • or Profiles menu -> pick one

Optional — matching shell prompts (READY. / C:\> / MU/TH/UR> ...):
  echo 'source '"$PWD"'/retro-prompts.zsh' >> ~/.zshrc   # then:  retro c64

Re-run  ./install.sh --no-fonts  any time you edit a palette.
EOF
