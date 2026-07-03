# Retro Terminals — iTerm2 profiles

**37 iTerm2 profiles** in four groups — real historic machines (`retro`),
fictional computers (`sci-fi`), aesthetic movements (`aesthetic`), and the
Alien/Blade Runner megacorps (`corp`) — generated from a declarative palette spec
and installed as iTerm2 **Dynamic Profiles**. Each group is its own JSON file in
the DynamicProfiles folder, so you can enable or delete a whole pack
independently. Filter by the tag in the profile switcher.

## Install (build them into your iTerm2)

```bash
./install.sh              # fetch fonts + build all profiles into iTerm2
./install.sh --no-fonts   # profiles only (fonts already present)
```

Under the hood the profiles are built by one script:

```bash
python3 build_profiles.py
```

It writes four JSON files into `~/Library/Application Support/iTerm2/DynamicProfiles/`,
which iTerm2 **watches and hot-loads live** — no restart. Re-run it any time you
edit a palette; open tabs restyle within a second. Then in iTerm2 press **⌘O** and
filter by tag (`retro` / `sci-fi` / `aesthetic` / `corp`).

## What's installed — `retro` (real machines)

| Profile | Look | Font |
|---|---|---|
| Paper Teletype | Sepia ink on aged fanfold paper (DECwriter / ASR-33) | Courier |
| CRT Green Phosphor | P1 green monochrome, glow via blur + bright bold | Glass TTY VT220 |
| CRT Amber Phosphor | P3 amber monochrome | Glass TTY VT220 |
| Linux Console | Boot-to-tty1, VGA 16-color palette | Terminus (TTF) |
| SunOS cmdtool | Black-on-beige OpenWindows workstation | Courier |
| IRIX wsh | Deep-teal SGI console, signature SGI blue | Menlo |
| Commodore 64 | Light-blue-on-blue PETSCII, Pepto palette | C64 Pro Mono |
| MS-DOS Editor | Blue-screen edit.com / QBasic | IBM 3270 |
| Amiga Workbench | Workbench 1.3 blue / white / black / orange | Departure Mono |
| NeXTSTEP | Refined neutral-grey greyscale (1989 Terminal) | Menlo |
| OpenStep | NeXTSTEP's 1996 near-twin — cooler, lighter grey | Menlo |
| Apple II | Crisp green Applesoft (deliberately un-glowy) | Print Char 21 |
| ZX Spectrum | Black ink on white paper, ULA primaries | Departure Mono \* |
| Atari 8-bit | Cyan-blue READY screen with gold accent | Departure Mono \* |
| BBC Micro Mode 7 | Teletext pure-primary palette | Bedstead |
| Plan 9 acme | Bell Labs pale-yellow paper (`#FFFFEA`) | Menlo |

\* ZX Spectrum and Atari fall back to Departure Mono — their authentic fonts aren't
freely hosted. The palette does the identifying work.

## `sci-fi` (fictional computers)

| Profile | Look |
|---|---|
| The Matrix | Digital-rain green `#00FF41`, glow |
| TRON | ENCOM grid cyan + orange villain accent |
| Neuromancer | Ono-Sendai cyberspace: cyan + magenta neon |
| HAL 9000 | Red monochrome, ominous |
| Fallout Pip-Boy | RobCo Termlink green, heavy scanlines |
| Severance Lumon | Teal on navy, corporate-creepy |
| Cyberpunk 2077 | Night City yellow + cyan |
| Blade Runner | Esper amber + teal, smoky |
| WOPR | NORAD radar blue — *shall we play a game?* |
| Outrun | Synthwave hot-pink + cyan on deep purple |
| LCARS | Star Trek panel palette — orange / gold / mauve / blue on black |

## `aesthetic` (genre movements)

| Profile | Look |
|---|---|
| Steampunk | Brass, copper, verdigris on aged mahogany |
| Solarpunk | Warm cream, leaf-green + gold (light) |
| Dieselpunk | Machine-age teal, rust, cream |
| Vaporwave | Pastel pink / cyan / lilac on purple |
| Atompunk | Mid-century cream, atomic-coral + turquoise (light) |

## `corp` (Alien + Blade Runner megacorps)

The two franchises share a universe (Weyland → Tyrell), so they share a pack.
Spread across distinct hues so they don't all read as "amber sci-fi":

| Profile | Look |
|---|---|
| Weyland-Yutani | The Company — amber-gold CRT with green data accents |
| MU-TH-UR 6000 | The Nostromo's MOTHER, teal-green (*interface 2037, ready for inquiry*) |
| Seegson APOLLO | Sevastopol's budget AI — cold blue-white, red working light |
| Tyrell Corporation | Opulent candle-gold + deep red (*more human than human*) |
| Wallace Corporation | 2049 brutalist cold teal with one warm accent |
| Voight-Kampff | Clinical tungsten-orange empathy-test instrument |

All three notional packs get boot banners too, and matching `retro` prompts
(`retro matrix`, `retro hal`, `retro weyland`, `retro tyrell`, `retro vk`, …).

## Visual gallery & CRT playground

- **Gallery** — every profile rendered in its real font: <https://claude.ai/code/artifact/04f2755b-d0e1-4b63-ab7e-4fd1812a5460>
- **CRT playground** — a WebGL curved-glass shader (the effect iTerm can't do
  natively): <https://claude.ai/code/artifact/754420e0-22d9-4597-aca5-1f337b08e180>

The gallery links to the playground and explains how the five parts (profiles,
banners, prompts, bezel, playground) fit together.

## How it works

`build_profiles.py` holds a compact `PROFILES` spec — each machine is a set of
`#RRGGBB` hex colors plus a few settings (font, cursor, blink, glow). The script
compiles that into iTerm2's verbose float-based JSON and writes it to:

```
~/Library/Application Support/iTerm2/DynamicProfiles/retro-terminals.json
```

iTerm2 **watches that folder and hot-loads changes live** — no restart, no
manual import. The profiles appear in the profile switcher (`⌘⇧O`) tagged
`retro`.

GUIDs are derived deterministically from each profile name (`uuid5`), so
re-running the script **updates profiles in place** instead of creating
duplicates. Never hand-edit a `Guid`; in iTerm2 it's the profile's identity.

## Using a profile

- Browse: **Profiles** menu, or `⌘⇧O` and filter by `retro`.
- New tab in a profile: **Profiles ▸ Retro · …**.
- Make one your default: iTerm2 ▸ Settings ▸ Profiles ▸ select ▸ **Other Actions ▸ Set as Default**.

## Tweaking

Edit the hex values in `build_profiles.py`, then:

```bash
python3 build_profiles.py
```

The open tabs restyle within a second. Useful knobs per machine:

- `cursor_type`: `UNDERLINE` / `VBAR` / `BOX`
- `blink`: blinking cursor
- `aa`: anti-aliasing — **False** keeps bitmap fonts (C64, Terminus, Glass TTY,
  3270, Departure) crisp; **True** for outline fonts (Courier, Menlo)
- `transparency`, `blur`, `blur_radius`: the CRT glow approximation
- `min_contrast`: floor on text/background contrast (bump for readability)
- `vspacing` / `hspacing`: line/char spacing (a hair of `vspacing` fakes scanline gaps)

### Want "pure" vs "daily" variants?

Duplicate a `machine(...)` block, rename it (e.g. `"Commodore 64 (daily)"`), and
raise `min_contrast` / drop `transparency` + `blur`. The distinct name gives it
its own GUID automatically.

## Boot banners

Every profile prints its authentic startup screen when a **new tab** opens
(existing tabs won't re-run it) — the C64's `READY.`, the Amiga's `AmigaDOS`,
SunOS's release banner, and so on. It's the profile's `Initial Text`: one safe
`clear; printf …` command, after which you get a normal shell.

## Matching prompts — the `retro` command

Because this box runs **tmux + starship**, a prompt set at profile-open gets
overwritten by starship's `precmd` hook, and `ITERM_PROFILE` is stale inside
tmux. So prompts are a command you run, not per-profile magic:

```bash
source ~/Desktop/notebook/code/retro-terminals/retro-prompts.zsh   # once (or add to ~/.zshrc)
retro c64      # READY.        retro amiga   # 1>
retro dos      # C:\>          retro irix    # indy 1%
retro apple2   # ]             retro off     # back to starship
retro          # list them
```

`retro` removes starship's hook while active and restores it on `retro off`, so
it works in any shell, in or out of tmux.

## Scanline bezel (real iTerm2)

The five "tube" profiles — Green, Amber, Apple II, C64, BBC — carry
`crt-bezel.png`, a mostly-transparent scanline + vignette overlay drawn behind
the text. Tune its strength per profile with **Settings ▸ Profiles ▸ Window ▸
Background image ▸ Blend** (the generator sets `Blend` to `0.45`). Regenerate the
overlay itself with ImageMagick if you want it heavier/finer — the two `magick`
lines are in the project history. This nudges real iTerm toward the browser
playground's look; it's texture, not the full curved-glass shader.

## Fonts & provenance

Installed to `~/Library/Fonts` (all free):

- **Glass TTY VT220** — Viacheslav Slavinsky, `sensi.org/~svo/glasstty` (free)
- **C64 Pro Mono** — Style, `style64.org` (free for personal use)
- **Print Char 21** — Kreative Korp, `kreativekorp.com` (Apple ][ system font, free)
- **Bedstead** — bjh21, `bjh21.me.uk/bedstead` (SAA5050 teletext, public domain)
- **Terminus (TTF)** — `brew install --cask font-terminus` (OFL)
- **IBM 3270** — `brew install --cask font-3270` (OFL)
- **Departure Mono** — `brew install --cask font-departure-mono` (OFL)
- **Courier / Menlo** — macOS system fonts

## Notes on fidelity

iTerm2 has no CRT-shader support, so the green/amber tubes approximate the glow
with transparency + Gaussian blur + a brighter bold color and a touch of extra
line spacing. It reads as "phosphor," not as a curved-glass emulator. If you ever
want the full curvature/scanline treatment, that lives in dedicated emulators
(cool-retro-term) — but these stay real iTerm2 sessions you can actually work in.
