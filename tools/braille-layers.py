#!/usr/bin/env python3
"""Merge N color-mask layers into one braille art block + paint rules.

Each layer is a grayscale mask (white = that layer's ink) paired with a
hex color. All masks are sampled onto one braille dot grid; each cell is
owned by the layer with the most lit dots there. retro-banner paint
rules are glyph-keyed, so a glyph must be unique to one layer's set —
collisions are resolved by dropping the owner cell's least significant
dots until its glyph is unused by other layers.

Usage:
  braille-layers.py --layer body.png:DCF2FF --layer drape.png:3874E8 \
      --width 46 [--crop WxH+X+Y] [--base-layer 0]

Output: the art block, then '#: paint <hex> <glyphs>' lines ready to
paste into a banner header. A layer whose color is '-' gets no paint
rule (it inherits the banner base color).
"""
import argparse
import subprocess
import sys

BITS = [(0x01, 0, 0), (0x02, 0, 1), (0x04, 0, 2), (0x40, 0, 3),
        (0x08, 1, 0), (0x10, 1, 1), (0x20, 1, 2), (0x80, 1, 3)]


def resolve(want, taken_glyphs):
    """Nearest glyph (by Hamming distance, then popcount drift) not
    already claimed by another layer. Solid regions in two layers both
    want 0xFF; the loser gets a visually identical one-dot variant."""
    if chr(0x2800 + want) not in taken_glyphs:
        return want
    wp = bin(want).count("1")
    best = 0
    for cand in range(1, 256):
        if chr(0x2800 + cand) in taken_glyphs:
            continue
        d = bin(cand ^ want).count("1")
        pd = abs(bin(cand).count("1") - wp)
        key = (d, pd, cand)
        if best == 0 or key < best_key:
            best, best_key = cand, key
    return best


def sample(png, crop, dw, dh):
    cmd = ["magick", png]
    if crop:
        cmd += ["-crop", crop, "+repage"]
    cmd += ["-resize", f"{dw}x{dh}!", "-depth", "8", "gray:-"]
    out = subprocess.run(cmd, capture_output=True)
    if len(out.stdout) != dw * dh:
        sys.exit(f"sample failed for {png}: {out.stderr.decode()[:200]}")
    raw = out.stdout
    return [[raw[y * dw + x] > 100 for x in range(dw)] for y in range(dh)]


def dims(png, crop):
    cmd = ["magick", png]
    if crop:
        cmd += ["-crop", crop, "+repage"]
    cmd += ["-format", "%w %h", "info:"]
    w, h = map(int, subprocess.run(cmd, capture_output=True).stdout.split())
    return w, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", action="append", required=True,
                    metavar="MASK.png:HEX", help="mask and color, first listed wins ties")
    ap.add_argument("--width", type=int, default=40, help="output columns")
    ap.add_argument("--crop", default=None, help="WxH+X+Y applied to every mask")
    args = ap.parse_args()

    layers = []
    for spec in args.layer:
        png, _, hexc = spec.rpartition(":")
        layers.append((png, hexc))

    sw, sh = dims(layers[0][0], args.crop)
    dw = args.width * 2
    dh = round(sh / sw * dw)
    dh -= dh % 4
    grids = [sample(png, args.crop, dw, dh) for png, _ in layers]

    used = [set() for _ in layers]
    rows = []
    for r in range(dh // 4):
        row = []
        for c in range(args.width):
            best, best_bits, best_n = -1, 0, 0
            for i, g in enumerate(grids):
                bits = 0
                for bit, sx, sy in BITS:
                    if g[4 * r + sy][2 * c + sx]:
                        bits |= bit
                n = bin(bits).count("1")
                if n > best_n:
                    best, best_bits, best_n = i, bits, n
            if best < 0:
                row.append(" ")
                continue
            others = set().union(*(used[j] for j in range(len(layers)) if j != best))
            bits = resolve(best_bits, others)
            if not bits:
                row.append(" ")
                continue
            used[best].add(chr(0x2800 + bits))
            row.append(chr(0x2800 + bits))
        rows.append("".join(row).rstrip())

    while rows and not rows[0]: rows.pop(0)
    while rows and not rows[-1]: rows.pop()
    print("\n".join(rows))
    print("#PAINT")
    for (png, hexc), glyphs in zip(layers, used):
        if hexc != "-" and glyphs:
            print(f"#: paint {hexc} {''.join(sorted(glyphs))}")


if __name__ == "__main__":
    main()
