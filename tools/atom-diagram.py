#!/usr/bin/env python3
"""Braille atom: 2x4 subpixel resolution per char cell.

A terminal cell is ~1:2 (w:h); braille dots split it 2 wide x 4 tall,
so each dot is a square subpixel — same geometry as the half-block
renderer but at 4x the resolution, which is what makes the orbits
smooth. Orbits stroke via implicit-function distance in dot space;
nucleus stays a ▓ blob and electrons ● so retro-banner paint rules
can color them independently of the braille orbits.
"""
import math

W, H = 58, 24                    # char grid -> dot grid (2W) x (4H)
R_LONG, R_SHORT = 46.0, 15.5     # ellipse semi-axes in DOT units
STROKE = 1.55                    # half-width of orbit stroke, dots
NUCLEUS_R = 7.5                  # dots
ORBITS = [90, 210, 330]

DW, DH = 2 * W, 4 * H
CX, CY = DW / 2.0, DH / 2.0

def on_orbit(x, y):
    for th_deg in ORBITS:
        th = math.radians(th_deg)
        xr = x * math.cos(th) + y * math.sin(th)
        yr = -x * math.sin(th) + y * math.cos(th)
        f = (xr / R_LONG) ** 2 + (yr / R_SHORT) ** 2
        gx, gy = 2 * xr / R_LONG ** 2, 2 * yr / R_SHORT ** 2
        g = math.hypot(gx, gy)
        if g > 1e-9 and abs(f - 1) / g < STROKE:
            return True
    return False

dots = [[False] * DW for _ in range(DH)]
for r in range(DH):
    for c in range(DW):
        x, y = (c + 0.5) - CX, CY - (r + 0.5)
        if on_orbit(x, y):
            dots[r][c] = True

# braille bit layout: (sx, sy) -> bit
BITS = {(0, 0): 0x01, (0, 1): 0x02, (0, 2): 0x04, (0, 3): 0x40,
        (1, 0): 0x08, (1, 1): 0x10, (1, 2): 0x20, (1, 3): 0x80}

grid = []
for r in range(H):
    row = []
    for c in range(W):
        v = 0
        for sy in range(4):
            for sx in range(2):
                if dots[4 * r + sy][2 * c + sx]:
                    v |= BITS[(sx, sy)]
        row.append(chr(0x2800 + v) if v else " ")
    grid.append(row)

# nucleus: ▓ blob (distinct glyph -> own paint color)
for r in range(H):
    for c in range(W):
        x = (2 * c + 1) - CX          # cell center in dot coords
        y = CY - (4 * r + 2)
        if math.hypot(x, y) <= NUCLEUS_R:
            grid[r][c] = "▓"

def orbit_pt(th_deg, t):
    th = math.radians(th_deg)
    x, y = R_LONG * math.cos(t), R_SHORT * math.sin(t)
    return (x * math.cos(th) - y * math.sin(th),
            x * math.sin(th) + y * math.cos(th))

for th_deg, t in [(90, -0.5), (210, 0.4), (330, 0.6)]:
    x, y = orbit_pt(th_deg, t)
    c = int(round((CX + x) / 2 - 0.5))
    r = int(round((CY - y) / 4 - 0.5))
    if 0 <= r < H and 0 <= c < W:
        grid[r][c] = "●"

out = ["".join(r).rstrip() for r in grid]
while out and not out[0]: out.pop(0)
while out and not out[-1]: out.pop()
print("\n".join(out))
