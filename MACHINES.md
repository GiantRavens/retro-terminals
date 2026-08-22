# The machines

All 47 palettes, grouped into the four packs. Boot banners for every one
render on the site: <https://giantravens.github.io/retro-terminals/banners.html>

## `retro` (real machines)

The real iron — teletype paper, phosphor tubes, and that unmistakable C64 blue.

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

The screens that raised us. *Shall we play a game?*

| Profile | Look |
|---|---|
| The Matrix | Digital-rain green `#00FF41`, glow |
| TRON | ENCOM grid cyan + orange villain accent |
| Neuromancer | Ono-Sendai cyberspace: cyan + magenta neon |
| HAL 9000 | Red monochrome, ominous |
| Fallout Pip-Boy | RobCo Termlink green, heavy scanlines |
| Cyberpunk 2077 | Night City yellow + cyan |
| Blade Runner | Esper amber + teal, smoky |
| WOPR | NORAD radar blue — *shall we play a game?* |
| LCARS | Star Trek panel palette — orange / gold / mauve / blue on black |
| Rocinante | *The Expanse* — tactical navy, electric-blue wireframe, MISFIRE red |
| MCRN | Martian Congressional Republic Navy — hot red and burnt orange on black |
| MU-TH-UR 6000 | The Nostromo's MOTHER, stylized teal-green |
| MU-TH-UR 6000 CRT | Screen-accurate MOTHER — bright P1 phosphor green (*interface 2037, ready for inquiry*) |
| Nostromo | The ship herself — cornflower registration-plate blue on oxblood (*reg. 180924609*) |
| Nostromo CRT | Screen-accurate status panel — warm pink-white on brick red (*environ ctr / purge*) |

## `aesthetic` (genre movements)

For when you want a *vibe*, not a specific machine — pick your -punk.

| Profile | Look |
|---|---|
| Steampunk | Brass, copper, verdigris on aged mahogany |
| Solarpunk | Warm cream, leaf-green + gold (light) |
| Dieselpunk | Machine-age teal, rust, cream |
| Vaporwave | Pastel pink / cyan / lilac on purple |
| Outrun | Synthwave hot-pink + cyan on deep purple |
| Atompunk | Mid-century cream, atomic-coral + turquoise (light) |

## `corpo` (fictional megacorps)

The *corporations* — Alien + Blade Runner's shared universe plus
Severance's Lumon. The ships and their computers live in `sci-fi`.
The two franchises share a universe (Weyland → Tyrell), so they share a pack.
Spread across distinct hues so they don't all read as "amber sci-fi":

| Profile | Look |
|---|---|
| Weyland-Yutani | The Company — amber-gold CRT with green data accents |
| Seegson APOLLO | Sevastopol's budget AI — cold blue-white, red working light |
| Tyrell Corporation | Opulent candle-gold + deep red (*more human than human*) |
| Wallace Corporation | 2049 brutalist cold teal with one warm accent |
| Voight-Kampff | Clinical tungsten-orange empathy-test instrument |
| Severance Lumon | Teal on navy, corporate-creepy |

All three notional packs get boot banners too, and matching `retro` prompts
(`retro matrix`, `retro hal`, `retro weyland`, `retro tyrell`, `retro vk`, …).


All 47 banners render on the site: [giantravens.github.io/retro-terminals/banners.html](https://giantravens.github.io/retro-terminals/banners.html) — regenerate with `tools/build-banners-page.py` after editing banner art.

**Machines with logo-art banners.** Fifteen machines now boot with a real
mark instead of figlet text (the rest are queued — sources collect in the
local `reference/` stash):

| Machine | Mark | Technique |
|---|---|---|
| atompunk | orbital atom diagram | parametric (braille orbits, paintable core/electrons) |
| hal | HAL 9000 faceplate + glowing eye | parametric (dithered braille disc, popcount color buckets) |
| lcars | Starfleet delta | parametric (flare curve + star knockout) |
| wallace | three gold capsule bars | parametric |
| severance | Lumon globe | hybrid — parametric arcs + sampled wordmark |
| mother / muthur | Weyland-Yutani winged W | sampled, threshold keeps yellow only |
| bladerunner | POLICE 995 spinner decal | sampled |
| tyrell | owl seal | sampled |
| vk | VK badge letters | sampled, painted red via enumerated glyph rule |
| apple2 | six-stripe Apple + wordmark | sampled; stripes via line directives |
| roci | pin-up nose art + script | 3-layer color separation, per-cell braille merge |
| tron | beveled 1982 wordmark | 2-layer (blue faces + copper bevels) |
| next | B/W cube | sampled, knockout letters |
| openstep | OPENSTEP slab wordmark | sampled |

Tour just those: `tools/retro-demo --only hal,roci,tron,…` — and
`--sort alpha` re-orders any tour for lookup instead of the curated
era/franchise narrative.
