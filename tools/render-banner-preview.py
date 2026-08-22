#!/usr/bin/env python3
"""Font-free banner rasterizer: draws glyph geometry directly to a PPM.

Handles braille (2x4 dots), block elements, shade blocks, and ● so
braille art can be previewed without terminal font fallback. Cell size
10x20 px (1:2). Usage: render_banner.py art.txt out.ppm [color_map.py-ish]
Colors: '#GLYPHS hex' lines on stdin-style map file optional; default one color.
"""
import sys

CW, CH = 10, 20
art = open(sys.argv[1]).read().rstrip("\n").split("\n")
out = sys.argv[2]
cmap = {}
if len(sys.argv) > 3:
    for line in open(sys.argv[3]):
        parts = line.split()
        if len(parts) == 2:
            hexc, glyphs = parts[1], parts[0]
            col = tuple(int(hexc[i:i+2], 16) for i in (0, 2, 4))
            for ch in glyphs:
                cmap[ch] = col
DEFAULT = (255, 72, 56)
BG = (10, 0, 0)

rows, cols = len(art), max(len(l) for l in art)
Wpx, Hpx = cols * CW, rows * CH
img = [[BG] * Wpx for _ in range(Hpx)]

def rect(x0, y0, x1, y1, col):
    for y in range(max(0, int(y0)), min(Hpx, int(y1))):
        for x in range(max(0, int(x0)), min(Wpx, int(x1))):
            img[y][x] = col

QUADS = {"▘": [(0,0)], "▝": [(1,0)], "▖": [(0,1)], "▗": [(1,1)],
         "▀": [(0,0),(1,0)], "▄": [(0,1),(1,1)], "▌": [(0,0),(0,1)],
         "▐": [(1,0),(1,1)], "▚": [(0,0),(1,1)], "▞": [(1,0),(0,1)],
         "▛": [(0,0),(1,0),(0,1)], "▜": [(0,0),(1,0),(1,1)],
         "▙": [(0,0),(0,1),(1,1)], "▟": [(1,0),(0,1),(1,1)],
         "█": [(0,0),(1,0),(0,1),(1,1)]}
SHADE = {"░": 0.25, "▒": 0.5, "▓": 0.75}
BITPOS = [(0x01,0,0),(0x02,0,1),(0x04,0,2),(0x40,0,3),
          (0x08,1,0),(0x10,1,1),(0x20,1,2),(0x80,1,3)]

for r, line in enumerate(art):
    for c, ch in enumerate(line):
        col = cmap.get(ch, DEFAULT)
        x0, y0 = c * CW, r * CH
        if 0x2800 <= ord(ch) <= 0x28FF:
            v = ord(ch) - 0x2800
            for bit, sx, sy in BITPOS:
                if v & bit:
                    rect(x0 + sx*CW/2 + 1, y0 + sy*CH/4 + 1,
                         x0 + (sx+1)*CW/2 - 1, y0 + (sy+1)*CH/4 - 1, col)
        elif ch in QUADS:
            for qx, qy in QUADS[ch]:
                rect(x0 + qx*CW/2, y0 + qy*CH/2,
                     x0 + (qx+1)*CW/2, y0 + (qy+1)*CH/2, col)
        elif ch in SHADE:
            a = SHADE[ch]
            mix = tuple(int(BG[i] + (col[i]-BG[i]) * a) for i in range(3))
            rect(x0, y0, x0+CW, y0+CH, mix)
        elif ch == "●":
            cx, cy, rad = x0 + CW/2, y0 + CH/2, CW * 0.45
            for y in range(int(cy-rad*2), int(cy+rad*2)):
                for x in range(int(cx-rad), int(cx+rad)+1):
                    if ((x-cx)**2 + ((y-cy)/2.0)**2) <= rad*rad:
                        if 0 <= y < Hpx and 0 <= x < Wpx:
                            img[y][x] = col
        elif ch != " ":
            rect(x0+2, y0+6, x0+CW-2, y0+CH-6, col)   # generic glyph blob

with open(out, "w") as f:
    f.write(f"P3\n{Wpx} {Hpx}\n255\n")
    for row in img:
        f.write(" ".join(f"{p[0]} {p[1]} {p[2]}" for p in row) + "\n")
