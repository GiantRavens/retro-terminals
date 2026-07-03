#!/usr/bin/env python3
"""
Retro terminal profile generator for iTerm2.

Compiles a compact, human-editable SPEC (hex palettes + a few settings per
"machine") into iTerm2's verbose Dynamic Profile JSON and writes it to the
folder iTerm2 hot-loads:

    ~/Library/Application Support/iTerm2/DynamicProfiles/retro-terminals.json

Design notes (Cognitive Honing: push logic down, keep the spec declarative):
  * Colors are authored as #RRGGBB hex; this tool expands them to iTerm2's
    {Red/Green/Blue Component} float dicts.
  * GUIDs are derived deterministically from the profile name (uuid5), so
    re-running UPDATES each profile in place instead of creating duplicates.
    (In iTerm2 the Guid is the identity — never randomize it between runs.)
  * Bitmap/pixel fonts (C64, Terminus, Glass TTY, IBM 3270, Departure Mono)
    render crisp only with anti-aliasing OFF, so each spec carries an `aa` flag.

Run:  python3 build_profiles.py           # write + report
      python3 build_profiles.py --stdout  # print JSON, don't write
"""

import json
import os
import sys
import uuid

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NS = uuid.uuid5(uuid.NAMESPACE_DNS, "retro-terminals.skiplevens")


def guid(name: str) -> str:
    return str(uuid.uuid5(NS, name)).upper()


def color(hexstr: str) -> dict:
    """#RRGGBB -> iTerm2 sRGB color dict (components 0..1)."""
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return {
        "Color Space": "sRGB",
        "Red Component": round(r, 6),
        "Green Component": round(g, 6),
        "Blue Component": round(b, 6),
        "Alpha Component": 1.0,
    }


# Cursor types
UNDERLINE, VBAR, BOX = 0, 1, 2


def machine(
    name,
    font,
    size,
    bg,
    fg,
    ansi,               # list of 16 hex strings (ANSI 0..15)
    bold=None,
    cursor=None,
    cursor_text=None,
    selection=None,
    selected_text=None,
    link=None,
    cursor_type=BOX,
    blink=False,
    aa=True,            # anti-alias ASCII glyphs (False = crisp pixels)
    bright_bold=True,
    min_contrast=0.0,
    transparency=0.0,
    blur=False,
    blur_radius=2.0,
    vspacing=1.0,
    hspacing=1.0,
    tab=None,           # optional tab-color accent hex
    blurb="",           # human note, dropped into a comment sibling file
    ns="Retro",         # namespace: name prefix ("Retro · X") + tag group
):
    bold = bold or fg
    cursor = cursor or fg
    cursor_text = cursor_text or bg
    selection = selection or ansi[8]
    selected_text = selected_text or fg
    link = link or ansi[12]
    fontstr = f"{font} {size}"

    p = {
        "Name": f"{ns} · {name}",
        "Guid": guid(name),
        "Tags": [ns.lower()],
        "Dynamic Profile Parent Name": "Default",
        # --- fonts ---
        "Normal Font": fontstr,
        "Non Ascii Font": fontstr,
        "Use Non-ASCII Font": False,
        "ASCII Anti Aliased": aa,
        "Non-ASCII Anti Aliased": aa,
        "Use Bold Font": True,
        "Use Italic Font": True,
        "Horizontal Spacing": hspacing,
        "Vertical Spacing": vspacing,
        "Draw Powerline Glyphs": False,
        # --- cursor ---
        "Cursor Type": cursor_type,
        "Blinking Cursor": blink,
        # --- rendering ---
        "Use Bright Bold": bright_bold,
        "Minimum Contrast": min_contrast,
        "Transparency": transparency,
        "Blur": blur,
        "Blur Radius": blur_radius,
        # --- core colors ---
        "Background Color": color(bg),
        "Foreground Color": color(fg),
        "Bold Color": color(bold),
        "Cursor Color": color(cursor),
        "Cursor Text Color": color(cursor_text),
        "Selection Color": color(selection),
        "Selected Text Color": color(selected_text),
        "Link Color": color(link),
        "Cursor Guide Color": color(selection),
    }
    for i, hx in enumerate(ansi):
        p[f"Ansi {i} Color"] = color(hx)
    if tab:
        p["Use Tab Color"] = True
        p["Tab Color"] = color(tab)
    p["_note"] = blurb  # ignored by iTerm2; handy when reading the JSON
    return p


# ---------------------------------------------------------------------------
# THE SPEC  --  edit palettes here, re-run, iTerm2 reloads live
# ---------------------------------------------------------------------------

# Canonical VGA/CGA 16-color palette (shared by Linux console + MS-DOS)
VGA = [
    "000000", "AA0000", "00AA00", "AA5500",
    "0000AA", "AA00AA", "00AAAA", "AAAAAA",
    "555555", "FF5555", "55FF55", "FFFF55",
    "5555FF", "FF55FF", "55FFFF", "FFFFFF",
]

PROFILES = [

    # 1. Paper printing terminal (DECwriter LA36 / Teletype ASR-33) -----------
    machine(
        "Paper Teletype", "Courier", 14,
        bg="F2EAD3", fg="3A2E1C", bold="1E160C",
        cursor="6B5A3C", cursor_text="F2EAD3",
        selection="D9C9A0", selected_text="201810", link="5A3A1F",
        cursor_type=UNDERLINE, blink=False, aa=True, bright_bold=False,
        ansi=[
            "2A2016", "8A2E1F", "4F5A2A", "8A6A1F",
            "3A4A66", "6E3A5A", "3F6660", "453720",
            "5A4C38", "B04A33", "6E7A3A", "B08A2A",
            "52618A", "8E5A7E", "57847C", "241B10",
        ],
        blurb="Sepia ink faded on aged fanfold paper. No glow, underline caret.",
    ),

    # 2. CRT green phosphor (P1) ----------------------------------------------
    machine(
        "CRT Green Phosphor", "Glass TTY VT220", 18,
        bg="001200", fg="33FF33", bold="66FF66",
        cursor="33FF33", cursor_text="001200",
        selection="0A5A0A", selected_text="CCFFCC", link="66FF99",
        cursor_type=BOX, blink=True, aa=True, bright_bold=True,
        transparency=0.06, blur=True, blur_radius=1.5, vspacing=1.05,
        ansi=[
            "003300", "00A000", "00CC00", "33DD00",
            "007700", "00B400", "00D060", "33FF33",
            "005500", "33DD33", "66FF66", "99FF33",
            "00CC66", "66FF99", "99FFCC", "CCFFCC",
        ],
        blurb="Monochrome P1 phosphor; whole palette is green intensities. Glow via blur+bright bold.",
    ),

    # 3. CRT amber phosphor (P3) ----------------------------------------------
    machine(
        "CRT Amber Phosphor", "Glass TTY VT220", 18,
        bg="180E00", fg="FFB000", bold="FFCC33",
        cursor="FFB000", cursor_text="180E00",
        selection="5A3C00", selected_text="FFE8C0", link="FFCC80",
        cursor_type=BOX, blink=True, aa=True, bright_bold=True,
        transparency=0.06, blur=True, blur_radius=1.5, vspacing=1.05,
        ansi=[
            "3A2600", "B36B00", "C88400", "E0A000",
            "8A5500", "C07000", "D89000", "FFB000",
            "5A3C00", "FFC233", "FFCC44", "FFD966",
            "E09000", "FFCC80", "FFE0A0", "FFE8C0",
        ],
        blurb="Monochrome P3 amber phosphor. The 'warm' CRT — DECwriter/Wyse vibe.",
    ),

    # 4. Early Linux console (VGA text mode, tty1) ----------------------------
    machine(
        "Linux Console", "Terminus (TTF)", 15,
        bg="000000", fg="AAAAAA", bold="FFFFFF",
        cursor="AAAAAA", cursor_text="000000",
        selection="333333", selected_text="FFFFFF", link="5555FF",
        cursor_type=UNDERLINE, blink=True, aa=False, bright_bold=True,
        ansi=VGA,
        blurb="Boot-to-tty1: VGA 16-color palette, Terminus (the actual Linux console font).",
    ),

    # 5. Early Sun (SunOS 4 / OpenWindows cmdtool) ----------------------------
    machine(
        "SunOS cmdtool", "Courier", 13,
        bg="DAD6C8", fg="14120C", bold="000000",
        cursor="14120C", cursor_text="DAD6C8",
        selection="B9C4D8", selected_text="000000", link="2A3A8A",
        cursor_type=BOX, blink=False, aa=True, bright_bold=False,
        tab="7B68A0",
        ansi=[
            "000000", "A02020", "207020", "8A6A00",
            "2A3A9A", "802A80", "1F7A7A", "555555",
            "808080", "C03030", "2F9A2F", "9A8000",
            "3A4AC0", "A03AA0", "2A9A9A", "14120C",
        ],
        blurb="Black-on-beige cmdtool under OpenWindows. Light workstation; purple tab accent.",
    ),

    # 6. Early IRIX (SGI Indigo / O2, wsh / winterm) --------------------------
    machine(
        "IRIX wsh", "Menlo", 13,
        bg="0C2530", fg="B8CCD0", bold="E4F0F2",
        cursor="5FD7D7", cursor_text="0C2530",
        selection="1E4A56", selected_text="E4F0F2", link="7FB0E0",
        cursor_type=BOX, blink=False, aa=True, bright_bold=True,
        tab="5B8AC4",
        ansi=[
            "0A1E26", "E05A5A", "5FD770", "E0C060",
            "5B8AC4", "C07AD0", "5FD7D7", "B8CCD0",
            "37545E", "FF8080", "8AF0A0", "F0E090",
            "86AEE0", "E0A0F0", "90F0F0", "E4F0F2",
        ],
        blurb="Deep-teal SGI console with the signature SGI blue (#5B8AC4). Crisp, cool, workstation.",
    ),

    # 7. Commodore 64 ---------------------------------------------------------
    machine(
        "Commodore 64", "C64 Pro Mono", 13,
        bg="40318D", fg="7869C4", bold="A59BE0",
        cursor="7869C4", cursor_text="40318D",
        selection="6C5EB5", selected_text="FFFFFF", link="9FE0E6",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        ansi=[
            "000000", "9F4E44", "5CAB5E", "C9D487",
            "50459B", "8B3F96", "6ABFC6", "ADADAD",
            "626262", "CB7E75", "ACEA88", "EDF171",
            "887ECB", "B65AC6", "9FE0E6", "FFFFFF",
        ],
        blurb="Light-blue-on-blue PETSCII. Pepto palette mapped onto ANSI. READY.",
    ),

    # 8. MS-DOS blue editor (edit.com / QBasic) -------------------------------
    machine(
        "MS-DOS Editor", "IBM 3270", 15,
        bg="0000AA", fg="C6C6C6", bold="FFFFFF",
        cursor="FFFFFF", cursor_text="0000AA",
        selection="00AAAA", selected_text="000000", link="FFFF55",
        cursor_type=UNDERLINE, blink=True, aa=False, bright_bold=True,
        ansi=VGA,
        blurb="The blue-screen DOS editor look; white on DOS blue, cyan highlight bar.",
    ),

    # 9. Amiga Workbench 1.3 --------------------------------------------------
    machine(
        "Amiga Workbench", "Departure Mono", 14,
        bg="0055AA", fg="FFFFFF", bold="FFFFFF",
        cursor="FF8800", cursor_text="0055AA",
        selection="FF8800", selected_text="000000", link="66BBFF",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        ansi=[
            "000000", "DD4400", "55AA55", "FF8800",
            "0055AA", "AA55AA", "55AAAA", "FFFFFF",
            "555555", "FF8800", "88DD88", "FFBB55",
            "66BBFF", "DD88DD", "88DDDD", "FFFFFF",
        ],
        blurb="Workbench 1.3 four-color world: blue, white, black, orange. 1.CLI> ",
    ),

    # 10. NeXTSTEP ------------------------------------------------------------
    machine(
        "NeXTSTEP", "Menlo", 13,
        bg="E8E8E8", fg="141414", bold="000000",
        cursor="000000", cursor_text="E8E8E8",
        selection="B4C8D8", selected_text="000000", link="204A80",
        cursor_type=BOX, blink=False, aa=True, bright_bold=False,
        ansi=[
            "000000", "9A2E2E", "2E7A2E", "7A6A1E",
            "2E4A8A", "7A2E7A", "1E6E6E", "4A4A4A",
            "7A7A7A", "C04040", "40A040", "A08A20",
            "4060C0", "A040A0", "30A0A0", "141414",
        ],
        blurb="Refined neutral-grey greyscale; the 1989 Terminal.app ancestor. Cool vs Sun's warm.",
    ),

    # 10b. OPENSTEP (1996) — NeXTSTEP's near-twin, cooler & lighter -----------
    machine(
        "OpenStep", "Menlo", 13,
        bg="ECEDEF", fg="1A1A20", bold="000008",
        cursor="000010", cursor_text="ECEDEF",
        selection="C0D0E0", selected_text="000010", link="2A4A9A",
        cursor_type=BOX, blink=False, aa=True, bright_bold=False,
        ansi=[
            "000008", "9A2E3A", "2E7A4A", "7A6A20",
            "2E4A9A", "7A2E7A", "1E6E7A", "4A4A52",
            "7A7A82", "C04048", "40A050", "A08A24",
            "4060D0", "A040A8", "30A0B0", "1A1A20",
        ],
        blurb="OPENSTEP 4.2: NeXTSTEP refined — cooler, lighter grey, bluer accent. A near-twin on purpose.",
    ),

    # ---- BONUS MACHINES ----------------------------------------------------

    # 11. Apple II (Applesoft BASIC, crisp green — deliberately un-glowy) ------
    machine(
        "Apple II", "Print Char 21", 16,
        bg="000800", fg="33E033", bold="7CFF7C",
        cursor="33E033", cursor_text="000800",
        selection="0A5A0A", selected_text="CCFFCC", link="66FF88",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        ansi=[
            "002000", "009000", "00BB00", "33C000",
            "007000", "00A030", "00C050", "33E033",
            "005000", "33CC33", "66FF66", "99FF44",
            "00CC55", "66FF88", "99FFBB", "CCFFCC",
        ],
        blurb="Applesoft green in the real Print Char 21 font. Crisp, no glow — the anti-VT220.",
    ),

    # 12. ZX Spectrum (white paper, saturated ULA primaries) ------------------
    machine(
        "ZX Spectrum", "Departure Mono", 14,
        bg="FFFFFF", fg="000000", bold="000000",
        cursor="000000", cursor_text="FFFFFF",
        selection="D7D700", selected_text="000000", link="0000D7",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        ansi=[
            "000000", "D70000", "00D700", "D7D700",
            "0000D7", "D700D7", "00D7D7", "D7D7D7",
            "555555", "FF0000", "00FF00", "FFFF00",
            "0000FF", "FF00FF", "00FFFF", "FFFFFF",
        ],
        blurb="Black ink on white paper; the ULA 8-color x2-bright palette is the whole identity.",
    ),

    # 13. Atari 8-bit (400/800/XL — cyan-blue screen, distinct from C64) -------
    machine(
        "Atari 8-bit", "Departure Mono", 14,
        bg="4351C7", fg="C7CFF7", bold="FFFFFF",
        cursor="FFFFFF", cursor_text="4351C7",
        selection="8090F0", selected_text="000000", link="90D0E8",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        ansi=[
            "000000", "C84C4C", "4CB84C", "D0A040",
            "4351C7", "A060C0", "4CB0C8", "C7CFF7",
            "5A64A0", "E08080", "90E090", "F0C060",
            "8090F0", "C090E0", "90D0E8", "FFFFFF",
        ],
        blurb="Atari's true-blue READY screen with a gold accent — cyan-blue, not C64 indigo.",
    ),

    # 14. BBC Micro (Mode 7 teletext, Bedstead) -------------------------------
    machine(
        "BBC Micro Mode 7", "Bedstead", 15,
        bg="000000", fg="FFFFFF", bold="FFFFFF",
        cursor="FFFFFF", cursor_text="000000",
        selection="0000FF", selected_text="FFFFFF", link="00FFFF",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        ansi=[
            "000000", "FF0000", "00FF00", "FFFF00",
            "0000FF", "FF00FF", "00FFFF", "FFFFFF",
            "555555", "FF0000", "00FF00", "FFFF00",
            "0000FF", "FF00FF", "00FFFF", "FFFFFF",
        ],
        blurb="SAA5050 teletext: pure RGB primaries in the real Bedstead font. Acorn DFS.",
    ),

    # 15. Plan 9 from Bell Labs (acme / rio — pale yellow) --------------------
    machine(
        "Plan 9 acme", "Menlo", 13,
        bg="FFFFEA", fg="000000", bold="000000",
        cursor="000000", cursor_text="FFFFEA",
        selection="EEEE9E", selected_text="000000", link="0000CC",
        cursor_type=BOX, blink=False, aa=True, bright_bold=False,
        tab="8888CC",
        ansi=[
            "000000", "99353A", "3B7A3B", "8A6A1E",
            "2E4A8A", "7A2E7A", "1E6E6E", "4A4A4A",
            "6E6E6E", "C04040", "40A040", "A08A20",
            "4060C0", "A040A0", "30A0A0", "000000",
        ],
        blurb="The unmistakable acme pale-yellow paper (#FFFFEA). Bell Labs, Rob Pike.",
    ),
]


# ---------------------------------------------------------------------------
# Boot banners  --  printed via iTerm2 "Initial Text" (Send text at start)
# ---------------------------------------------------------------------------
# Each banner is sent to the shell as ONE safe command: `clear; printf ...`,
# with every line single-quoted so backslashes / symbols stay literal. It
# prints in the profile's own colors, then hands you a normal prompt.

BANNERS = {
    "Paper Teletype":      ["TELETYPE MODEL 33 ASR      110 BAUD", "READY"],
    "CRT Green Phosphor":  ["ULTRIX V4.5  (rev 47)", "DIGITAL VT220 - ONLINE"],
    "CRT Amber Phosphor":  ["WYSE WY-50   AMBER", "SYSTEM READY"],
    "Linux Console":       ["Debian GNU/Linux 2.0  futhark  tty1",
                            "Linux 2.0.36 (i586)", "Welcome to Debian GNU/Linux"],
    "SunOS cmdtool":       ["SunOS Release 4.1.4  (GENERIC)",
                            "Copyright (c) Sun Microsystems, Inc."],
    "IRIX wsh":            ["IRIX Release 6.5  IP32", "Silicon Graphics, Inc."],
    "Commodore 64":        ["    **** COMMODORE 64 BASIC V2 ****", "",
                            " 64K RAM SYSTEM  38911 BASIC BYTES FREE", "", "READY."],
    "MS-DOS Editor":       ["Starting MS-DOS...", "", "MS-DOS Version 6.22"],
    "Amiga Workbench":     ["AmigaDOS   Workbench 1.3",
                            "Copyright (c) 1985-1988 Commodore-Amiga, Inc."],
    "NeXTSTEP":            ["NeXTSTEP 3.3  (mach)"],
    "OpenStep":            ["OPENSTEP 4.2  (mach)", "Copyright NeXT Software, Inc."],
    "Apple II":            ["Apple ][", ""],
    "ZX Spectrum":         ["(C) 1982 Sinclair Research Ltd", "", "0 OK, 0:1"],
    "Atari 8-bit":         ["ATARI 8-BIT COMPUTER", "MEMO PAD", "READY"],
    "BBC Micro Mode 7":    ["BBC Computer 32K", "", "Acorn DFS", "", "BASIC"],
    "Plan 9 acme":         ["Plan 9 from Bell Labs"],
}


def initial_text(lines):
    quoted = " ".join("'" + ln + "'" for ln in lines)
    return "clear; printf '%s\\n' " + quoted + "\n"


for _p in PROFILES:
    _base = _p["Name"].replace("Retro · ", "")
    if _base in BANNERS:
        _p["Initial Text"] = initial_text(BANNERS[_base])


# ---------------------------------------------------------------------------
# Scanline bezel  --  a subtle CRT overlay behind the text (real iTerm2)
# ---------------------------------------------------------------------------
# crt-bezel.png is a mostly-transparent scanline + vignette overlay. iTerm2
# draws it behind the glyphs; "Blend" scales how visible it is. Applied only to
# the "tube" machines — the ones that lived on a phosphor CRT.

BEZEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crt-bezel.png")
TUBES = {
    "CRT Green Phosphor", "CRT Amber Phosphor",
    "Apple II", "Commodore 64", "BBC Micro Mode 7",
}

for _p in PROFILES:
    if _p["Name"].replace("Retro · ", "") in TUBES:
        _p["Background Image Location"] = BEZEL
        _p["Background Image Mode"] = 0        # 0 = stretch to fill
        _p["Blend"] = 0.45                     # overlay strength (0..1)


# ===========================================================================
# FICTIONAL COMPUTERS  (ns="Sci-Fi", tag "sci-fi")
# ===========================================================================

FICTION = [
    machine("The Matrix", "Glass TTY VT220", 18, ns="Sci-Fi",
        bg="000000", fg="00FF41", bold="6BFFB0", cursor="00FF41", cursor_text="000000",
        selection="0A5A0A", selected_text="DFFFE8", link="6BFFB0",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=1.5, vspacing=1.05,
        ansi=["001200","008F11","00B72E","00D93B","006B0E","00A030","00C060","00FF41",
              "005A0E","22C24E","6BFF8B","9BFF6B","00CC55","6BFFB0","A8FFC0","DFFFE8"],
        blurb="Digital-rain green #00FF41. Wake up, Neo."),

    machine("TRON", "Glass TTY VT220", 18, ns="Sci-Fi",
        bg="010A12", fg="7EE8FF", bold="C8F6FF", cursor="FF9A3C", cursor_text="010A12",
        selection="14506A", selected_text="FFFFFF", link="FFD08C",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=1.5,
        ansi=["001018","FF6A3C","4CE0C0","FFB84C","2A9AD0","8CC8FF","7EE8FF","BCE8FF",
              "14506A","FF9A3C","8CFFE8","FFD08C","5AB8FF","B0D8FF","C8F6FF","FFFFFF"],
        blurb="ENCOM grid cyan with an orange villain accent. I fight for the Users."),

    machine("Neuromancer", "Menlo", 13, ns="Sci-Fi",
        bg="05060A", fg="00F0C0", bold="7CFFE0", cursor="FF2E97", cursor_text="05060A",
        selection="303048", selected_text="E8F4FF", link="C86CFF",
        cursor_type=VBAR, blink=True, bright_bold=True,
        transparency=0.06, blur=True, blur_radius=1.0,
        ansi=["0A0A12","FF2E97","00F0C0","F0E14C","3A5CFF","C86CFF","00D0FF","A8C0D0",
              "303048","FF6CB0","6CFFD8","FFF07C","6C90FF","E0A0FF","8CF0FF","E8F4FF"],
        blurb="Ono-Sendai cyberspace: neon cyan + magenta over the colorless void."),

    machine("HAL 9000", "Glass TTY VT220", 18, ns="Sci-Fi",
        bg="0A0000", fg="FF2A2A", bold="FF6B6B", cursor="FF2A2A", cursor_text="0A0000",
        selection="500000", selected_text="FFD0D0", link="FF7090",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=1.8,
        ansi=["200000","C00000","E02020","FF3030","900000","C81818","E04040","FF2A2A",
              "500000","FF5050","FF7070","FF9060","E03030","FF7090","FFA0A0","FFD0D0"],
        blurb="Red monochrome. I am putting myself to the fullest possible use."),

    machine("Fallout Pip-Boy", "Glass TTY VT220", 18, ns="Sci-Fi",
        bg="001200", fg="18FF6D", bold="6BFFA0", cursor="18FF6D", cursor_text="001200",
        selection="0A6030", selected_text="DFFFE8", link="6BFFC0",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=2.0, vspacing=1.08,
        ansi=["002400","12B04A","18D858","3AF06A","0C8038","14C050","1AE070","18FF6D",
              "0A6030","3AE070","6BFFA0","9BFF7A","18D080","6BFFC0","A8FFD0","DFFFE8"],
        blurb="RobCo Industries Termlink. Heavy phosphor + scanlines."),

    machine("Severance Lumon", "Menlo", 13, ns="Sci-Fi",
        bg="0A2440", fg="86D8E0", bold="C8F0F4", cursor="86D8E0", cursor_text="0A2440",
        selection="244A64", selected_text="E8F8FC", link="86B8F0",
        cursor_type=BOX, blink=False, bright_bold=True,
        ansi=["071A2E","E06A6A","6ED0B0","E0C878","5A9AD0","B08CD0","86D8E0","A8C8D0",
              "244A64","FF9090","9AF0D0","F0E0A0","86B8F0","D0B0F0","B0F0F8","E8F8FC"],
        blurb="Lumon MDR: teal on navy. Please enjoy each number equally."),

    machine("Cyberpunk 2077", "Departure Mono", 14, ns="Sci-Fi",
        bg="0A0A0F", fg="FCEE0A", bold="FFF66B", cursor="00F0FF", cursor_text="0A0A0F",
        selection="3A3A2A", selected_text="FFFFF0", link="00F0FF",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        ansi=["12121A","FF003C","00F0A0","FCEE0A","00B0FF","FF2E97","00F0FF","C0C0A0",
              "3A3A2A","FF4060","6CFFC0","FFF66B","6CC0FF","FF6CB0","8CF0FF","FFFFF0"],
        blurb="Night City yellow + cyan. Wake up, Samurai."),

    machine("Blade Runner", "Glass TTY VT220", 18, ns="Sci-Fi",
        bg="0E0A06", fg="FFB86B", bold="FFD9A0", cursor="6BD0D0", cursor_text="0E0A06",
        selection="503820", selected_text="FFE8D0", link="A8E8E8",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=1.8,
        ansi=["201408","E0603C","6BB0A0","FFA04C","4C8AA0","C88CA0","6BD0D0","E0C0A0",
              "503820","FF8A5C","9BD0C0","FFC87C","7CB0C8","E0A8C0","A8E8E8","FFE8D0"],
        blurb="Esper amber + teal, smoky. More human than human."),

    machine("WOPR", "IBM 3270", 16, ns="Sci-Fi",
        bg="000A18", fg="4CC8FF", bold="A6E4FF", cursor="FF8A2C", cursor_text="000A18",
        selection="0A3A5A", selected_text="FFFFFF", link="FF8A2C",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        transparency=0.04, blur=True, blur_radius=1.5,
        ansi=["001424","1E6AA0","3AA0C0","4CC8FF","185A90","6A8AC0","4CC8FF","A6E4FF",
              "0A3A5A","5AB0E0","8CD8FF","FFB84C","6AB0FF","B0C8FF","C8ECFF","FFFFFF"],
        blurb="NORAD radar blue. Shall we play a game?"),

    machine("Outrun", "Departure Mono", 14, ns="Sci-Fi",
        bg="1A0A2E", fg="FF3C8C", bold="FF8CC0", cursor="2DE2E6", cursor_text="1A0A2E",
        selection="4A2A6A", selected_text="FFE0FF", link="43D9FF",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        transparency=0.06, blur=True, blur_radius=1.5,
        ansi=["2A1040","FF2D6B","2DE2E6","FFB03A","7A4CFF","FF3C8C","43D9FF","E0B0FF",
              "4A2A6A","FF6BA0","6BF0F0","FFD06B","A07CFF","FF8CC0","8CF0FF","FFE0FF"],
        blurb="Miami-sunset synthwave: hot pink + cyan on deep purple."),

    machine("LCARS", "Menlo", 13, ns="Sci-Fi",
        bg="000000", fg="FF9900", bold="FFCC66", cursor="FF9900", cursor_text="000000",
        selection="55442A", selected_text="FFCC99", link="9999FF",
        cursor_type=BOX, blink=False, bright_bold=True,
        ansi=["000000","CC6666","66CC99","FFCC00","6688CC","CC99CC","99CCCC","FF9900",
              "55442A","FF8866","99DDAA","FFCC66","99AAFF","DDAAEE","AADDDD","FFCC99"],
        blurb="Star Trek LCARS: the orange / gold / mauve / blue panel palette on black."),
]

FBANNERS = {
    "The Matrix":       ["Wake up, Neo...", "The Matrix has you...", "Follow the white rabbit."],
    "TRON":             ["ENCOM MAINFRAME  OS-12", "TRON: I FIGHT FOR THE USERS", "END OF LINE."],
    "Neuromancer":      ["ONO-SENDAI CYBERSPACE 7",
                         "The sky above the port was the color of television,",
                         "tuned to a dead channel.", "", "> jacking in..."],
    "HAL 9000":         ["HAL 9000   HEURISTIC ALGORITHMIC COMPUTER",
                         "I am completely operational and all my circuits are functioning perfectly."],
    "Fallout Pip-Boy":  ["ROBCO INDUSTRIES (TM) TERMLINK", "", "Enter Password Now"],
    "Severance Lumon":  ["LUMON INDUSTRIES", "Macrodata Refinement", "Please enjoy each number equally."],
    "Cyberpunk 2077":   ["NIGHT CITY // NETWATCH", "BREACH PROTOCOL: ACTIVE",
                         "Wake up, Samurai. We have a city to burn."],
    "Blade Runner":     ["ESPER   -   TYRELL CORP", "ENHANCE 224 TO 176", "More human than human."],
    "WOPR":             ["GREETINGS PROFESSOR FALKEN.", "", "SHALL WE PLAY A GAME?"],
    "Outrun":           ["OUTRUN // 1986", "MIAMI  05:44   84F", "> DRIVE"],
    "LCARS":            ["LCARS 24-ALPHA", "LIBRARY COMPUTER ACCESS / RETRIEVAL SYSTEM",
                         "", "STARFLEET COMPUTER CORE  -  STATE YOUR INQUIRY"],
}

FTUBES = {"The Matrix", "TRON", "HAL 9000", "Fallout Pip-Boy", "Blade Runner", "WOPR"}


# ===========================================================================
# AESTHETIC MOVEMENTS  (ns="Aesthetic", tag "aesthetic")
# ===========================================================================

AESTHETIC = [
    machine("Steampunk", "Courier", 14, ns="Aesthetic",
        bg="1E140A", fg="E8B85C", bold="FFD98A", cursor="C87A3C", cursor_text="1E140A",
        selection="4A3820", selected_text="F0E0C0", link="7ABFA8",
        cursor_type=BOX, blink=False, bright_bold=False,
        ansi=["1A1008","B0562C","7A8A4C","E8B85C","6A7A8A","A06A8A","4C8A78","C8A878",
              "4A3820","D07A44","A8B86C","FFD98A","8A9AAA","C89AB0","7ABFA8","F0E0C0"],
        blurb="Brass, copper, and verdigris on aged mahogany. Aetheric difference engine."),

    machine("Solarpunk", "Menlo", 13, ns="Aesthetic",
        bg="F2EFDF", fg="24614A", bold="15402F", cursor="D9A441", cursor_text="F2EFDF",
        selection="CFE3C8", selected_text="15402F", link="2A7A8A",
        cursor_type=BOX, blink=False, bright_bold=False,
        ansi=["1E2A20","B0503A","3C8A50","C08A2A","2A7A8A","8A5A8A","2E9A88","5A6A58",
              "7A8A78","C86A50","4CA860","D9A441","3A9AAE","A87AA8","4CBAA0","24614A"],
        blurb="Warm cream, leaf-green and gold. The future is a garden."),

    machine("Dieselpunk", "IBM 3270", 15, ns="Aesthetic",
        bg="14201E", fg="D8CBA8", bold="F0E8D0", cursor="C05A2C", cursor_text="14201E",
        selection="3A4A46", selected_text="F0E8D0", link="6ABAB0",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        ansi=["101A18","C05A2C","6A8A5C","D9A85C","3A6A7A","9A6A6A","3A8A8A","C8BC98",
              "3A4A46","E07A44","8AAA6C","F0C878","5A9AAA","B08A8A","6ABAB0","F0E8D0"],
        blurb="Machine-age teal, rust and cream. Turbine online, for the Machine Age."),

    machine("Vaporwave", "Departure Mono", 14, ns="Aesthetic",
        bg="1B1030", fg="9FE7F5", bold="C0F0FA", cursor="FF9CE0", cursor_text="1B1030",
        selection="4A3A6A", selected_text="FFFFFF", link="C9A7FF",
        cursor_type=BOX, blink=True, aa=False, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=1.2,
        ansi=["2A1B45","FF7AB0","8CE0C8","F5D98C","8CA0F0","C9A7FF","9FE7F5","E8D8F0",
              "4A3A6A","FFA0D0","B0F0E0","FFE8B0","A8B8FF","E0C0FF","C0F0FA","FFFFFF"],
        blurb="Pastel pink / cyan / lilac on deep purple. Macintosh Plus // Floral Shoppe."),

    machine("Atompunk", "Courier", 14, ns="Aesthetic",
        bg="EAE3CE", fg="1E5A5A", bold="0E3A3A", cursor="E0654C", cursor_text="EAE3CE",
        selection="CFE0D8", selected_text="0E3A3A", link="D0503A",
        cursor_type=BOX, blink=False, bright_bold=False,
        ansi=["20302E","D0503A","4C8A6A","C08A2A","3A7A8A","A05A7A","2E9A9A","5A5A48",
              "7A7A68","E0654C","5CA87A","D9A441","4C9AAE","C07A9A","4CBABA","1E5A5A"],
        blurb="Mid-century cream, atomic-coral and turquoise. The World of Tomorrow, today."),
]

ABANNERS = {
    "Steampunk":  ["AETHERIC DIFFERENCE ENGINE  MK.III",
                   "By Appointment to Her Majesty", "STEAM PRESSURE: NOMINAL"],
    "Solarpunk":  ["SOLARPUNK COLLECTIVE // NODE 7", "Grid: 100% renewable",
                   "The future is a garden."],
    "Dieselpunk": ["ATLANTROPA WORKS   UNIT 09", "TURBINE ONLINE", "FOR THE MACHINE AGE"],
    "Vaporwave":  ["VAPOR OS   v3.11", "AESTHETIC LOADED", "PLAY AT YOUR OWN RISK"],
    "Atompunk":   ["ATOMIC ELECTRONIC BRAIN   MODEL 1959",
                   "THE WORLD OF TOMORROW... TODAY!", "POWERED BY THE ATOM"],
}


# ===========================================================================
# MEGACORPS  --  the Alien + Blade Runner shared universe (ns="Corp", "corp")
# ===========================================================================

CORP = [
    machine("Weyland-Yutani", "Glass TTY VT220", 18, ns="Corp",
        bg="0C0A04", fg="F5B942", bold="FFD97A", cursor="F5B942", cursor_text="0C0A04",
        selection="4A3A18", selected_text="FFF0C8", link="9BD86C",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=1.8,
        ansi=["1A1206","C85A2C","6BA84C","F5B942","7A8A5C","B08A5C","8AB86C","E0C88C",
              "4A3A18","E07A44","9BD86C","FFD97A","A8B87C","D0A87C","B8E098","FFF0C8"],
        blurb="The Company: amber-gold CRT with green data accents. Building Better Worlds."),

    machine("MU-TH-UR 6000", "Glass TTY VT220", 18, ns="Corp",
        bg="001208", fg="43E6B0", bold="8CFFD0", cursor="43E6B0", cursor_text="001208",
        selection="0A5A3C", selected_text="DFFFF0", link="8CFFE0",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=1.6, vspacing=1.05,
        ansi=["002012","2CB07A","22C88A","43E6B0","1A8A66","2CB490","30D0A0","43E6B0",
              "0A5A3C","4CE0A8","8CFFD0","AEFFDE","30C0A0","8CFFE0","B8FFE8","DFFFF0"],
        blurb="MOTHER, stylized teal-green. See 'MU-TH-UR 6000 CRT' for the screen-accurate green."),

    machine("MU-TH-UR 6000 CRT", "Glass TTY VT220", 18, ns="Corp",
        bg="000A00", fg="33FF2E", bold="7CFF6B", cursor="33FF2E", cursor_text="000A00",
        selection="0A5A0A", selected_text="DFFFD0", link="7CFF8B",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=1.7, vspacing=1.06,
        ansi=["001A00","0FA00F","1FC81F","4AE02A","0A7A0A","14B014","1FD040","33FF2E",
              "0A5A0A","4AE04A","7CFF6B","A6FF4A","2ADD5A","7CFF8B","B0FFA0","DFFFD0"],
        blurb="Screen-accurate MU/TH/UR: bright P1 phosphor green on black, heavy scanlines."),

    machine("Seegson APOLLO", "Menlo", 13, ns="Corp",
        bg="0A1018", fg="A8C8DC", bold="DCEAF4", cursor="FF6A4C", cursor_text="0A1018",
        selection="2A3A48", selected_text="DCEAF4", link="7AAAD0",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.04, blur=True, blur_radius=1.2,
        ansi=["0A141C","E05A4C","6EB0A0","D0B060","5A8AB0","9A7AB0","7AB0C8","A8C8DC",
              "2A3A48","FF7A6C","90D0C0","E8D090","7AAAD0","C0A0D0","A0D0E4","DCEAF4"],
        blurb="Sevastopol's budget AI: cold blue-white with a red working light."),

    machine("Tyrell Corporation", "Glass TTY VT220", 18, ns="Corp",
        bg="120A06", fg="E8C468", bold="FFE59A", cursor="C03A2C", cursor_text="120A06",
        selection="4A3418", selected_text="FFF4D0", link="C8C070",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=1.8,
        ansi=["201206","B03828","8A8A4C","E8C468","7A6A4C","A05A4C","B0A060","E0CC98",
              "4A3418","E05A44","C8C070","FFE59A","A08A5C","C88A6C","D8C888","FFF4D0"],
        blurb="Opulent candle-gold + deep red. More human than human."),

    machine("Wallace Corporation", "Menlo", 13, ns="Corp",
        bg="08100F", fg="6FC8C0", bold="B8ECE6", cursor="E0A040", cursor_text="08100F",
        selection="24403C", selected_text="DCF0EC", link="8CD8CE",
        cursor_type=BOX, blink=False, bright_bold=True,
        ansi=["0A1614","C86A5C","5EB0A6","D0A850","4C8A94","9A7A9A","6FC8C0","A8C4C0",
              "24403C","E08A7C","8CD8CE","E8C878","6CAAB4","B89ABA","A0E0D8","DCF0EC"],
        blurb="2049 brutalist cold teal with a single warm accent. A new model of perfection."),

    machine("Voight-Kampff", "Glass TTY VT220", 18, ns="Corp",
        bg="0E0704", fg="FF8A3C", bold="FFB870", cursor="FF8A3C", cursor_text="0E0704",
        selection="4A2A10", selected_text="FFE0C0", link="F0C888",
        cursor_type=BOX, blink=True, bright_bold=True,
        transparency=0.05, blur=True, blur_radius=1.8,
        ansi=["1E0E04","E0522C","B08A4C","FF9A48","8A6A4C","C0704C","D0A060","E8C090",
              "4A2A10","FF7A44","E0B070","FFB870","B08A5C","E0906C","F0C888","FFE0C0"],
        blurb="Clinical tungsten-orange empathy-test instrument."),
]

CBANNERS = {
    "Weyland-Yutani":      ["WEYLAND-YUTANI CORP   -   DIVISION 12", "BUILDING BETTER WORLDS",
                            "", "SPECIAL ORDER 937: CLASSIFIED"],
    "MU-TH-UR 6000":       ["INTERFACE 2037", "READY FOR INQUIRY"],
    "MU-TH-UR 6000 CRT":   ["MU/TH/UR 6000", "INTERFACE 2037 READY FOR INQUIRY",
                            "", "> WHAT IS THE NATURE OF THE EMERGENCY?"],
    "Seegson APOLLO":      ["SEEGSON APOLLO", "PERSONAL TERMINAL MODEL 3",
                            "", "How can I help you return to work?"],
    "Tyrell Corporation":  ["TYRELL CORPORATION", "MORE HUMAN THAN HUMAN", "", "NEXUS-6 REGISTRY"],
    "Wallace Corporation": ["WALLACE CORPORATION", "A NEW MODEL OF PERFECTION"],
    "Voight-Kampff":       ["VOIGHT-KAMPFF EMPATHY TEST", "SUBJECT: UNKNOWN",
                            "", "You are in a desert, walking along in the sand..."],
}

CTUBES = {"Weyland-Yutani", "MU-TH-UR 6000", "MU-TH-UR 6000 CRT", "Seegson APOLLO",
          "Tyrell Corporation", "Voight-Kampff"}


# ---------------------------------------------------------------------------
# Attach banners + bezels to the notional packs
# ---------------------------------------------------------------------------

def _attach(profiles, prefix, banners, tubes):
    for p in profiles:
        base = p["Name"].replace(prefix, "")
        if base in banners:
            p["Initial Text"] = initial_text(banners[base])
        if base in tubes:
            p["Background Image Location"] = BEZEL
            p["Background Image Mode"] = 0
            p["Blend"] = 0.45


_attach(FICTION,   "Sci-Fi · ",    FBANNERS, FTUBES)
_attach(AESTHETIC, "Aesthetic · ", ABANNERS, set())
_attach(CORP,      "Corp · ",      CBANNERS, CTUBES)


# ---------------------------------------------------------------------------
# Emit  --  one JSON file per group, all hot-loaded by iTerm2
# ---------------------------------------------------------------------------

def _write(dest_dir, filename, profiles):
    dest = os.path.join(dest_dir, filename)
    with open(dest, "w") as f:
        f.write(json.dumps({"Profiles": profiles}, indent=2))
    print(f"Wrote {len(profiles):>2} profiles -> {filename}")
    for p in profiles:
        print(f"    {p['Name']:<24} {p['Normal Font']:<20} guid={p['Guid'][:8]}")


def main():
    if "--stdout" in sys.argv:
        print(json.dumps({"Profiles": PROFILES + FICTION + AESTHETIC + CORP}, indent=2))
        return
    dest_dir = os.path.expanduser(
        "~/Library/Application Support/iTerm2/DynamicProfiles"
    )
    os.makedirs(dest_dir, exist_ok=True)
    _write(dest_dir, "retro-terminals.json", PROFILES)
    _write(dest_dir, "fictional-terminals.json", FICTION)
    _write(dest_dir, "aesthetic-terminals.json", AESTHETIC)
    _write(dest_dir, "corp-terminals.json", CORP)
    total = len(PROFILES) + len(FICTION) + len(AESTHETIC) + len(CORP)
    print(f"\nTotal: {total} profiles in 4 groups "
          f"(retro / sci-fi / aesthetic / corp).")


if __name__ == "__main__":
    main()
