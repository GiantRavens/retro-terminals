#!/usr/bin/env python3
"""
Embed the freely-redistributable fonts into the standalone preview HTML as
base64 @font-face rules, so the GitHub Pages gallery/playground render in the
real fonts for visitors who don't have them installed.

Only OFL / public-domain fonts are embedded (safe to redistribute):
  Terminus (OFL), IBM 3270 (OFL), Departure Mono (OFL), Bedstead (public domain),
  Convair Mono (OFL, built in this repo — see fonts/convair-mono/).
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

# css family name -> [(file, css format, mime, font-weight, font-style), ...]
# Most families ship one face; Convair Mono has real Bold and Italic cuts, and
# embedding them stops the browser SYNTHESISING those styles -- a fake bold
# smears the uniform stroke that font is built around.
#
# Convair Mono lives in its own repo (GiantRavens/convair-mono) and installs
# like any other font here, so it is read from ~/Library/Fonts. Its TTFs are
# ~87 KB each; woff2() shrinks them ~4x before base64, which matters when three
# faces go inline.
CONVAIR = "ConvairMono-%s.ttf"
FONTS = {
    "Terminus (TTF)": [(find("TerminusTTF-4*.ttf"), "truetype", "font/ttf", "normal", "normal")],
    "IBM 3270":       [(os.path.join(HOME, "3270-Regular.otf"), "opentype", "font/otf", "normal", "normal")],
    "Departure Mono": [(os.path.join(HOME, "DepartureMono-Regular.otf"), "opentype", "font/otf", "normal", "normal")],
    "Bedstead":       [(os.path.join(HOME, "Bedstead.otf"), "opentype", "font/otf", "normal", "normal")],
    "Convair Mono":   [(os.path.join(HOME, CONVAIR % "Regular"), "woff2", "font/woff2", "normal", "normal"),
                       (os.path.join(HOME, CONVAIR % "Bold"),    "woff2", "font/woff2", "700",    "normal"),
                       (os.path.join(HOME, CONVAIR % "Italic"),  "woff2", "font/woff2", "normal", "italic")],
}

# which families each page actually uses
TARGETS = {
    "index.html":         ["Terminus (TTF)", "IBM 3270", "Departure Mono", "Bedstead",
                           "Convair Mono"],
    "crt-playground.html": ["IBM 3270", "Bedstead"],
    # Embed into the studio TEMPLATE so fonts survive every `build_ghostty.py
    # --studio` regeneration (the generated ghostty-studio.html copies the head).
    "tools/studio-template.html": ["Terminus (TTF)", "IBM 3270", "Departure Mono",
                                   "Bedstead", "Convair Mono"],
}

ATTRIB = ("<!-- Embedded fonts (base64): Terminus & IBM 3270 & Departure Mono & "
          "Convair Mono under SIL OFL 1.1; Bedstead is public domain. "
          "See fonts/INSTALL.md. -->")


def woff2(path):
    """Compress a TTF/OTF to woff2 in a temp dir. Falls back to the original
    bytes if woff2_compress is absent -- bigger page, still correct."""
    import shutil, subprocess, tempfile
    if path.endswith(".woff2"):
        return open(path, "rb").read()
    if not shutil.which("woff2_compress"):
        print(f"    note: woff2_compress not found, embedding {os.path.basename(path)} raw")
        return open(path, "rb").read()
    tmp = tempfile.mkdtemp()
    copy = os.path.join(tmp, os.path.basename(path))
    shutil.copy(path, copy)
    subprocess.run(["woff2_compress", copy], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = os.path.splitext(copy)[0] + ".woff2"
    data = open(out, "rb").read()
    shutil.rmtree(tmp, ignore_errors=True)
    return data


def face(family):
    out = []
    for path, fmt, mime, weight, style in FONTS[family]:
        raw = woff2(path) if fmt == "woff2" else open(path, "rb").read()
        b64 = base64.b64encode(raw).decode()
        out.append(f"@font-face{{font-family:'{family}';"
                   f"src:url(data:{mime};base64,{b64}) format('{fmt}');"
                   f"font-weight:{weight};font-style:{style};font-display:swap}}")
    return "\n".join(out)


# Anchor on the <style id>, NOT on the comment text. Keying the idempotent
# replace to the exact ATTRIB string meant that editing ATTRIB made every
# subsequent run silently match nothing, leave the file untouched, and still
# report success. Anchor on the one part that does not change.
BLOCK_RE = re.compile(
    r'(?:<!-- Embedded fonts.*?-->\s*)?<style id="rt-embedded-fonts">.*?</style>',
    re.S,
)

for fname, families in TARGETS.items():
    html = open(fname, encoding="utf-8").read()
    css = "\n".join(face(f) for f in families)
    block = f'{ATTRIB}\n<style id="rt-embedded-fonts">\n{css}\n</style>'
    if BLOCK_RE.search(html):
        # function replacement: never let base64 be read as a backreference
        html = BLOCK_RE.sub(lambda _m: block, html, count=1)
    else:
        html = html.replace("</head>", block + "\n</head>", 1)

    # Verify rather than assert. The whole point of this pass is that a page
    # renders in the real face for visitors who have installed nothing.
    missing = [f for f in families if f"font-family:'{f}'" not in html]
    if missing:
        raise SystemExit(f"ERROR: {fname} still missing {missing} after embed")

    open(fname, "w", encoding="utf-8").write(html)
    faces = sum(len(FONTS[f]) for f in families)
    print(f"embedded {len(families)} families / {faces} faces into {fname}"
          f"  ({len(html) // 1024} KB total)")
