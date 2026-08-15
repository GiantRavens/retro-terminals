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
| Symbols Nerd Font Mono | all (non-ASCII fallback: nvim devicons, Neo-tree, any TUI icons) | `brew install --cask font-symbols-only-nerd-font` | MIT |
| Convair Mono | Convair Blueprint, Convair Whiteprint | [GiantRavens/convair-mono](https://github.com/GiantRavens/convair-mono) — *built*, not fetched from a foundry | OFL |
| Courier / Menlo | Paper, Sun, IRIX, NeXT, OpenStep, Plan 9, Steampunk, Atompunk, Seegson, Wallace | macOS system | — |

\* ZX Spectrum and Atari fall back to Departure Mono — their authentic fonts
aren't freely hosted. The palette carries the identity.

Font family names must match exactly in `build_profiles.py` (e.g. `Terminus (TTF)`,
`Glass TTY VT220`), or iTerm2 silently substitutes a default. The symbols
fallback is referenced by its PostScript name, `SymbolsNFM`.

**Install before generating profiles.** iTerm2 resolves a dynamic profile's font
when it loads the file and caches the result, so a profile written *before* its
font is installed silently falls back to Menlo and stays there. If a machine
renders in the wrong face, install the font, then re-run `build_profiles.py`.

**iTerm2 and Ghostty disagree about font names.** iTerm2 resolves some faces only
by their PostScript name — its own font picker writes that form back into the
profile — while Ghostty needs the *family* name to find bold and italic members.
`machine(..., iterm_font=...)` overrides just the string iTerm2 reads; the `font`
argument stays the true family, keys the metric tables, and is what Ghostty gets.
Convair Mono needs this (`ConvairMono-Regular` vs `Convair Mono`).
