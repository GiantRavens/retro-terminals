# Fonts

The profiles reference these fonts. All are free / redistributable. The fonts
themselves are **not** committed to this repo — run `./fonts/install-fonts.sh`
(or `./install.sh`) to fetch them into `~/Library/Fonts`.

| Font | Used by | Source | License |
|---|---|---|---|
| Glass TTY VT220 | CRT green/amber, Matrix, HAL, Pip-Boy, Blade Runner, WY, MOTHER, Tyrell, VK | [sensi.org/~svo/glasstty](https://sensi.org/~svo/glasstty/) | free |
| C64 Pro Mono | Commodore 64 | [style64.org](https://style64.org/c64-truetype) | free (personal) |
| Print Char 21 | Apple II | [kreativekorp.com](https://www.kreativekorp.com/software/fonts/apple2/) | free |
| Bedstead | BBC Micro Mode 7 | [bjh21.me.uk/bedstead](https://bjh21.me.uk/bedstead/) | public domain |
| Terminus (TTF) | Linux Console | `brew install --cask font-terminus` | OFL |
| IBM 3270 | MS-DOS, WOPR, Dieselpunk | `brew install --cask font-3270` | OFL |
| Departure Mono | Amiga, ZX*, Atari*, Cyberpunk, Outrun, Vaporwave | `brew install --cask font-departure-mono` | OFL |
| Courier / Menlo | Paper, Sun, IRIX, NeXT, OpenStep, Plan 9, Steampunk, Atompunk, Seegson, Wallace | macOS system | — |

\* ZX Spectrum and Atari fall back to Departure Mono — their authentic fonts
aren't freely hosted. The palette carries the identity.

Font family names must match exactly in `build_profiles.py` (e.g. `Terminus (TTF)`,
`Glass TTY VT220`), or iTerm2 silently substitutes a default.
