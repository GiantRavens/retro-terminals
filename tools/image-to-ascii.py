#!/usr/bin/env python3
"""Convert a dark-on-light image to ASCII or ANSI-colored terminal art."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_RAMP = " .:-=+*#%@"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a dark-on-light image as ASCII art."
    )
    parser.add_argument("image", type=Path, help="input image")
    parser.add_argument("-w", "--width", type=int, default=72, help="columns (default: 72)")
    parser.add_argument(
        "--mode",
        choices=("ascii", "ansi", "half-block", "braille"),
        default="ascii",
        help="output style (default: ascii)",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=55.0,
        help="background-removal threshold, 0-100 (default: 55)",
    )
    parser.add_argument(
        "--char-aspect",
        type=float,
        default=0.5,
        help="terminal character width/height correction (default: 0.5)",
    )
    parser.add_argument(
        "--ramp",
        default=DEFAULT_RAMP,
        help="characters ordered from light to dark",
    )
    parser.add_argument(
        "--tint",
        metavar="R,G,B",
        help="override source colors, for example --tint 0,220,255",
    )
    parser.add_argument(
        "--trim",
        action="store_true",
        help="crop light margins before rendering",
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="source is light-on-dark (bright pixels are the ink)",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="emit bare glyphs with no ANSI colors (for banner files)",
    )
    parser.add_argument(
        "--solid-interior",
        action="store_true",
        help="braille mode: replace fully-lit cells whose neighbors are all "
             "inked with a full block, so large masses render dark while "
             "edges stay braille-smooth",
    )
    parser.add_argument("-o", "--output", type=Path, help="write to a text file")
    return parser.parse_args()


def run(command: list[str]) -> bytes:
    try:
        return subprocess.check_output(command, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as error:
        message = error.stderr.decode(errors="replace").strip()
        raise SystemExit(f"ImageMagick failed: {message}") from error


def parse_tint(value: str | None) -> tuple[int, int, int] | None:
    if value is None:
        return None
    try:
        color = tuple(int(part) for part in value.split(","))
    except ValueError as error:
        raise SystemExit("--tint must use R,G,B integers") from error
    if len(color) != 3 or any(channel < 0 or channel > 255 for channel in color):
        raise SystemExit("--tint channels must each be between 0 and 255")
    return color


def rgb_escape(foreground: tuple[int, int, int], background=None) -> str:
    fr, fg, fb = foreground
    sequence = f"\x1b[38;2;{fr};{fg};{fb}m"
    if background is not None:
        br, bg, bb = background
        sequence += f"\x1b[48;2;{br};{bg};{bb}m"
    else:
        sequence += "\x1b[49m"
    return sequence


def render_ascii(
    pixels: bytes,
    width: int,
    height: int,
    ramp: str,
    colors: bytes | None = None,
    tint: tuple[int, int, int] | None = None,
) -> str:
    last = len(ramp) - 1
    lines = []
    for row in range(height):
        start = row * width
        values = pixels[start : start + width]
        cells = []
        for column, value in enumerate(values):
            character = ramp[min(last, value * len(ramp) // 256)]
            if colors is not None and character != " ":
                color_start = (start + column) * 3
                color = tint or tuple(colors[color_start : color_start + 3])
                cells.append(rgb_escape(color) + character)
            else:
                cells.append(character)
        line = "".join(cells).rstrip()
        if colors is not None:
            line += "\x1b[0m"
        lines.append(line)
    return "\n".join(lines).strip("\n") + "\n"


def render_half_blocks(
    colors: bytes,
    width: int,
    rows: int,
    threshold: float,
    tint: tuple[int, int, int] | None,
    invert: bool = False,
    plain: bool = False,
) -> str:
    cutoff = threshold * 255 / 100

    def pixel(index: int) -> tuple[int, int, int]:
        start = index * 3
        return tuple(colors[start : start + 3])

    def visible(color: tuple[int, int, int]) -> bool:
        red, green, blue = color
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        return luminance >= cutoff if invert else luminance <= cutoff

    lines = []
    pixel_width = width
    for row in range(rows):
        cells = []
        for column in range(width):
            top = pixel((row * 2) * pixel_width + column)
            bottom = pixel((row * 2 + 1) * pixel_width + column)
            top_visible = visible(top)
            bottom_visible = visible(bottom)
            top_color = tint or top
            bottom_color = tint or bottom

            if plain:
                if top_visible and bottom_visible:
                    cells.append("█")
                elif top_visible:
                    cells.append("▀")
                elif bottom_visible:
                    cells.append("▄")
                else:
                    cells.append(" ")
            elif top_visible and bottom_visible:
                cells.append(rgb_escape(top_color, bottom_color) + "▀")
            elif top_visible:
                cells.append(rgb_escape(top_color) + "▀")
            elif bottom_visible:
                cells.append(rgb_escape(bottom_color) + "▄")
            else:
                cells.append("\x1b[0m ")
        lines.append("".join(cells).rstrip() + ("" if plain else "\x1b[0m"))
    return "\n".join(lines).strip("\n") + "\n"


def render_braille(
    colors: bytes,
    width: int,
    rows: int,
    threshold: float,
    tint: tuple[int, int, int] | None,
    invert: bool = False,
    plain: bool = False,
    solid_interior: bool = False,
) -> str:
    cutoff = threshold * 255 / 100
    pixel_width = width * 2
    dot_values = (
        (0, 0, 0x01),
        (0, 1, 0x02),
        (0, 2, 0x04),
        (1, 0, 0x08),
        (1, 1, 0x10),
        (1, 2, 0x20),
        (0, 3, 0x40),
        (1, 3, 0x80),
    )

    def pixel(x: int, y: int) -> tuple[int, int, int]:
        start = (y * pixel_width + x) * 3
        return tuple(colors[start : start + 3])

    def visible(color: tuple[int, int, int]) -> bool:
        red, green, blue = color
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        return luminance >= cutoff if invert else luminance <= cutoff

    cell_bits = [[0] * width for _ in range(rows)]
    for row in range(rows):
        for column in range(width):
            for dx, dy, bit in dot_values:
                if visible(pixel(column * 2 + dx, row * 4 + dy)):
                    cell_bits[row][column] |= bit

    def interior(row, column):
        if cell_bits[row][column] != 0xFF:
            return False
        for rr, cc in ((row-1, column), (row+1, column), (row, column-1), (row, column+1)):
            if not (0 <= rr < rows and 0 <= cc < width) or not cell_bits[rr][cc]:
                return False
        return True

    lines = []
    for row in range(rows):
        cells = []
        for column in range(width):
            bits = cell_bits[row][column]
            active_colors = []
            for dx, dy, bit in dot_values:
                color = pixel(column * 2 + dx, row * 4 + dy)
                if visible(color) :
                    active_colors.append(color)
            if not bits:
                cells.append(" " if plain else "\x1b[0m ")
                continue
            glyph = "█" if solid_interior and interior(row, column) else chr(0x2800 + bits)
            if plain:
                cells.append(glyph)
                continue
            if tint is None:
                count = len(active_colors)
                color = tuple(
                    sum(sample[channel] for sample in active_colors) // count
                    for channel in range(3)
                )
            else:
                color = tint
            cells.append(rgb_escape(color) + glyph)
        lines.append("".join(cells).rstrip() + ("" if plain else "\x1b[0m"))
    return "\n".join(lines).strip("\n") + "\n"


def main() -> None:
    args = parse_args()

    if shutil.which("magick") is None:
        raise SystemExit("ImageMagick is required: https://imagemagick.org/")
    if not args.image.is_file():
        raise SystemExit(f"Input file not found: {args.image}")
    if args.width < 1:
        raise SystemExit("--width must be at least 1")
    if not 0 <= args.threshold <= 100:
        raise SystemExit("--threshold must be between 0 and 100")
    if args.char_aspect <= 0:
        raise SystemExit("--char-aspect must be greater than 0")
    if len(args.ramp) < 2:
        raise SystemExit("--ramp must contain at least two characters")
    tint = parse_tint(args.tint)

    crop_args = []
    if args.trim:
        geometry = run(
            [
                "magick",
                str(args.image),
                "-colorspace",
                "Gray",
                "-threshold",
                f"{args.threshold}%",
                "-format",
                "%@",
                "info:",
            ]
        ).decode()
        crop_args = ["-crop", geometry, "+repage"]

    dimensions = run(
        [
            "magick",
            str(args.image),
            *crop_args,
            "-format",
            "%w %h",
            "info:",
        ]
    ).decode()
    source_width, source_height = map(int, dimensions.split())
    height = max(1, round(source_height / source_width * args.width * args.char_aspect))

    grayscale = run(
        [
            "magick",
            str(args.image),
            *crop_args,
            "-colorspace",
            "Gray",
            "-threshold",
            f"{args.threshold}%",
            *([] if args.invert else ["-negate"]),
            "-resize",
            f"{args.width}x{height}!",
            "-depth",
            "8",
            "gray:-",
        ]
    )

    expected = args.width * height
    if len(grayscale) != expected:
        raise SystemExit(f"Expected {expected} pixels, received {len(grayscale)}")

    if args.mode == "ascii":
        art = render_ascii(grayscale, args.width, height, args.ramp)
    else:
        if args.mode == "braille":
            rgb_width = args.width * 2
            rgb_height = height * 4
        else:
            rgb_width = args.width
            rgb_height = height * 2 if args.mode == "half-block" else height
        colors = run(
            [
                "magick",
                str(args.image),
                *crop_args,
                "-colorspace",
                "sRGB",
                "-resize",
                f"{rgb_width}x{rgb_height}!",
                "-depth",
                "8",
                "rgb:-",
            ]
        )
        color_expected = rgb_width * rgb_height * 3
        if len(colors) != color_expected:
            raise SystemExit(
                f"Expected {color_expected} color bytes, received {len(colors)}"
            )
        if args.mode == "ansi":
            art = render_ascii(
                grayscale, args.width, height, args.ramp, colors=colors, tint=tint
            )
        elif args.mode == "half-block":
            art = render_half_blocks(
                colors, args.width, height, args.threshold, tint,
                invert=args.invert, plain=args.plain,
            )
        else:
            art = render_braille(
                colors, args.width, height, args.threshold, tint,
                invert=args.invert, plain=args.plain,
                solid_interior=args.solid_interior,
            )
    if args.output:
        args.output.write_text(art, encoding="utf-8")
    else:
        sys.stdout.write(art)


if __name__ == "__main__":
    main()
