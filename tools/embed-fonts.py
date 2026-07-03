#!/usr/bin/env python3
"""
Embed the freely-redistributable fonts into the standalone preview HTML as
base64 @font-face rules, so the GitHub Pages gallery/playground render in the
real fonts for visitors who don't have them installed.

Only OFL / public-domain fonts are embedded (safe to redistribute):
  Terminus (OFL), IBM 3270 (OFL), Departure Mono (OFL), Bedstead (public domain).
Glass TTY VT220, C64 Pro Mono and the Apple/Kreative faces are NOT embedded —
their licenses make bundling dicey; those cards fall back to monospace.

Idempotent: re-running replaces the injected <style id="rt-embedded-fonts">.
Run from the repo root:  python3 tools/embed-fonts.py
"""
import base64
import glob
import os
import re

HOME = os.path.expanduser("~/Library/Fonts")


def find(pattern):
    hits = sorted(glob.glob(os.path.join(HOME, pattern)))
    if not hits:
        raise FileNotFoundError(pattern)
    return hits[0]

# (css family name, file, css format, mime)
FONTS = {
    "Terminus (TTF)": (find("TerminusTTF-4*.ttf"), "truetype", "font/ttf"),
    "IBM 3270":       (os.path.join(HOME, "3270-Regular.otf"), "opentype", "font/otf"),
    "Departure Mono": (os.path.join(HOME, "DepartureMono-Regular.otf"), "opentype", "font/otf"),
    "Bedstead":       (os.path.join(HOME, "Bedstead.otf"), "opentype", "font/otf"),
}

# which families each page actually uses
TARGETS = {
    "index.html":         ["Terminus (TTF)", "IBM 3270", "Departure Mono", "Bedstead"],
    "crt-playground.html": ["IBM 3270", "Bedstead"],
}

ATTRIB = ("<!-- Embedded fonts (base64): Terminus & IBM 3270 & Departure Mono "
          "under SIL OFL 1.1; Bedstead is public domain. See fonts/INSTALL.md. -->")


def face(family):
    path, fmt, mime = FONTS[family]
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return (f"@font-face{{font-family:'{family}';"
            f"src:url(data:{mime};base64,{b64}) format('{fmt}');font-display:swap}}")


for fname, families in TARGETS.items():
    html = open(fname, encoding="utf-8").read()
    css = "\n".join(face(f) for f in families)
    block = f'{ATTRIB}\n<style id="rt-embedded-fonts">\n{css}\n</style>'
    if 'id="rt-embedded-fonts"' in html:
        html = re.sub(
            re.escape(ATTRIB) + r'\s*<style id="rt-embedded-fonts">.*?</style>',
            block, html, count=1, flags=re.S,
        )
    else:
        html = html.replace("</head>", block + "\n</head>", 1)
    open(fname, "w", encoding="utf-8").write(html)
    kb = len(html) // 1024
    print(f"embedded {len(families)} fonts into {fname}  ({kb} KB total)")
