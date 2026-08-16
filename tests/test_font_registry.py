"""Every font a machine uses must be registered where it needs to be.

FONT_LEADING and FONT_CELL_EM are hand-kept tables that a new font has to be
added to, and both `.get(font, default)` -- so omitting one is not an error, it
is a silently wrong default. Radiant Prime Mono shipped that way: rows stacked
with no air at all, because its cell height equals its em and it was not in
FONT_LEADING, which already carries a comment documenting exactly that trap for
Convair Mono.

The naive fix -- "assert every font appears in both tables" -- is wrong. Menlo
legitimately wants neither entry; it carries its own line gap and sits at the
0.6 default. A blanket assertion would fail on a correct font and get muted.

So these checks MEASURE THE CONDITION instead of keeping a second list:

  leading   a font needs an entry only if it has no room of its own -- zero
            line gap AND ascent+descent equal to the em. That is a property of
            the font file, readable at test time, so the rule cannot drift from
            the reason for the rule.

  cell em   the symbol-fallback size is derived from this, so a wrong value
            means Nerd Font icons render at the wrong size in the cell. The
            true value is just advance/upem, which is also measurable.

Fonts that are not installed are SKIPPED and named in the skip message -- a
check that quietly passes because it could not look is the failure mode this
whole file exists to prevent.
"""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build_profiles  # noqa: E402

try:
    from fontTools.ttLib import TTFont
except ImportError:                                     # pragma: no cover
    TTFont = None

FONT_DIRS = [Path.home() / "Library" / "Fonts",
             Path("/Library/Fonts"), Path("/System/Library/Fonts")]


def _families():
    """Map family name -> a font file providing it, scanning name records.

    Reads nameID 16 (typographic family) then 1 (family); a face like
    ConvairMono-Bold reports family "Convair Mono", which is what machine()
    keys the tables on.
    """
    found = {}
    for d in FONT_DIRS:
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            if p.suffix.lower() not in (".ttf", ".otf", ".ttc"):
                continue
            try:
                f = TTFont(p, fontNumber=0, lazy=True)
                # getDebugName, not a platformID==3 filter: macOS system fonts
                # (Menlo.ttc, Courier.ttc) carry Macintosh-platform name records
                # only, so filtering to Windows silently loses them -- and they
                # then report as "not installed" rather than as unchecked.
                fam = f["name"].getDebugName(16) or f["name"].getDebugName(1)
                if fam:
                    found.setdefault(fam, p)
                f.close()
            except Exception:
                continue
    return found


def _machine_fonts():
    profiles = (build_profiles.PROFILES + build_profiles.FICTION
                + build_profiles.AESTHETIC + build_profiles.CORP)
    return sorted({p["Ghostty Font Family"] for p in profiles})


@unittest.skipIf(TTFont is None, "fonttools not available")
class FontRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.installed = _families()
        cls.fonts = _machine_fonts()

    def test_fonts_with_no_line_gap_are_registered_for_leading(self):
        missing, skipped = [], []
        for fam in self.fonts:
            path = self.installed.get(fam)
            if path is None:
                skipped.append(fam)
                continue
            f = TTFont(path, fontNumber=0, lazy=True)
            hhea, head = f["hhea"], f["head"]
            tight = (hhea.lineGap == 0
                     and hhea.ascender - hhea.descender == head.unitsPerEm)
            f.close()
            if tight and fam not in build_profiles.FONT_LEADING:
                missing.append(fam)
        if skipped:
            print(f"\n    (not installed, unchecked: {', '.join(skipped)})")
        self.assertEqual(
            [], missing,
            "these fonts have zero line gap and a cell equal to their em, so "
            "rows stack with no air, and they carry no FONT_LEADING entry: "
            f"{missing}",
        )

    def test_registered_cell_em_matches_the_actual_advance(self):
        wrong, skipped = [], []
        for fam in self.fonts:
            path = self.installed.get(fam)
            if path is None:
                skipped.append(fam)
                continue
            f = TTFont(path, fontNumber=0, lazy=True)
            cmap = f.getBestCmap()
            adv = f["hmtx"][cmap[ord("M")]][0] / f["head"].unitsPerEm
            f.close()
            declared = build_profiles.FONT_CELL_EM.get(fam)
            if declared is None:
                # No entry means the 0.6 default, which is only right if the
                # font actually sits near 0.6.
                if abs(adv - 0.6) > 0.03:
                    wrong.append((fam, "unregistered", round(adv, 3)))
            elif abs(declared - adv) > 0.01:
                wrong.append((fam, declared, round(adv, 3)))
        if skipped:
            print(f"    (not installed, unchecked: {', '.join(skipped)})")
        self.assertEqual(
            [], wrong,
            "FONT_CELL_EM sizes the Nerd Font symbol fallback; these disagree "
            f"with the font's real advance/upem (family, declared, actual): {wrong}",
        )


if __name__ == "__main__":
    unittest.main()
