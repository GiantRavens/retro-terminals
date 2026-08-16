"""Every machine must have a banner that fits the window it boots into.

Rocinante and MCRN shipped at 88 columns. Nothing failed: retro-banner rendered
them, retro-boot played them, every other test stayed green. But an 80-column
window wraps every line of an 88-column banner, which turns a 24-row plate into
~48 rows, scrolls the whole presentation off, and drops you at a prompt having
seen a flicker. The bug reads as "the boot is broken" and is actually arithmetic.

So the envelope is asserted here rather than eyeballed. Two ceilings:

  columns  a banner is padded to max-line + 4 by retro-banner, and a line that
           reaches column 80 wraps because the cursor auto-wraps on the next
           character -- so 79 is the last safe column, not 80.

  rows     the presentation is banner + chatter + spec line. The banner alone
           has to leave room for the rest inside a 25-row window.

Count DECODED CHARACTERS, never bytes. The first audit of this used
`awk '{print length}'` and reported 223 columns for a 77-column banner, because
box-drawing glyphs are 3 bytes each in UTF-8. A byte-based width check on this
repo is not a stricter check, it is a wrong one.

The wiring checks below are the same sweep's cheap half: a machine with no
SHELL_KEY is invisible to `retro random`, and one with no .boot file falls back
to a bare banner with no chatter. Neither raises; both just quietly do less.
"""
from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
import io
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("build_profiles", ROOT / "build_profiles.py")
bp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bp)

# retro-banner has no .py suffix; load it the way test_retro_demo_size loads the demo.
_bspec = importlib.util.spec_from_loader(
    "retro_banner", SourceFileLoader("retro_banner", str(ROOT / "tools" / "retro-banner"))
)
rb = importlib.util.module_from_spec(_bspec)
_bspec.loader.exec_module(rb)

MAX_COLS = 79        # column 80 wraps; see docstring
MAX_ROWS = 24        # banner alone, inside a 25-row window

ALL = bp.PROFILES + bp.FICTION + bp.AESTHETIC + bp.CORP


def render(key):
    """Plain-text render of one banner, as characters."""
    buf = io.StringIO()
    import contextlib
    with contextlib.redirect_stdout(buf):
        rb.render(key, color=False)
    return [ln.rstrip("\n") for ln in buf.getvalue().split("\n")]


class BannerEnvelopeTests(unittest.TestCase):
    def test_every_machine_has_a_shell_key(self):
        missing = [p["Name"] for p in ALL if not bp.SHELL_KEY.get(p["Name"])]
        self.assertEqual([], missing, f"no SHELL_KEY (invisible to `retro random`): {missing}")

    def test_every_machine_resolves_a_banner_and_chatter(self):
        no_art, no_boot = [], []
        for p in ALL:
            key = bp.SHELL_KEY.get(p["Name"])
            if not key:
                continue
            if rb.find_banner(key) is None:          # honours the ALIASES map
                no_art.append(p["Name"])
            if not (ROOT / "banners" / f"{key}.boot").exists():
                no_boot.append(p["Name"])
        self.assertEqual([], no_art, f"no banner art (nor alias): {no_art}")
        self.assertEqual([], no_boot, f"no .boot chatter: {no_boot}")

    def test_no_banner_wraps_in_an_eighty_column_window(self):
        over = []
        for p in ALL:
            key = bp.SHELL_KEY.get(p["Name"])
            if not key or rb.find_banner(key) is None:
                continue
            w = max((len(l) for l in render(key)), default=0)
            if w > MAX_COLS:
                over.append(f"{p['Name']} ({key}) = {w} cols")
        self.assertEqual([], over, f"banners wrap at 80 columns: {over}")

    def test_no_banner_fills_the_whole_window(self):
        tall = []
        for p in ALL:
            key = bp.SHELL_KEY.get(p["Name"])
            if not key or rb.find_banner(key) is None:
                continue
            h = len([l for l in render(key)])
            if h > MAX_ROWS:
                tall.append(f"{p['Name']} ({key}) = {h} rows")
        self.assertEqual([], tall, f"banners leave no room for chatter: {tall}")


if __name__ == "__main__":
    unittest.main()
