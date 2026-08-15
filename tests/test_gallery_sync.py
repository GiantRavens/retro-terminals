"""The gallery must advertise the palette the profiles actually ship.

index.html is split between two owners: build_profiles.py owns what a machine
looks like, the gallery owns what it says (era, meta labels, sample lines).
For a long time both halves were hand-typed, and the color half quietly went
stale -- Convair Blueprint's swatch sat two shades brighter than the profile it
was advertising, and Neuromancer showed a block cursor for a vbar machine.

Nothing downstream could catch that, because a stale swatch is still a valid
swatch: it parses, it renders, it just is not true any more. This is the check
that makes "correct but no longer true" fail loudly.

If this fails, do not hand-edit index.html -- run `python3 build_profiles.py`,
which rewrites the derived fields and leaves the prose alone.
"""
import importlib.util
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

_spec = importlib.util.spec_from_file_location(
    "build_profiles", os.path.join(REPO, "build_profiles.py")
)
bp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bp)


class GallerySyncTests(unittest.TestCase):
    def test_gallery_colors_match_the_generator(self):
        drift = bp.sync_gallery(REPO, apply=False)
        self.assertEqual(
            drift, [],
            "index.html has drifted from build_profiles.py on these "
            f"(machine, field) pairs: {drift}. Re-run build_profiles.py.",
        )

    def test_every_gallery_cursor_shape_has_a_css_rule(self):
        """GALLERY_CURSOR names the .screen modifier classes. A shape with no
        matching rule renders as the default block and silently misreports the
        profile -- which is exactly how the vbar machine went unnoticed."""
        css = open(os.path.join(REPO, "index.html"), encoding="utf-8").read()
        for shape in set(bp.GALLERY_CURSOR.values()):
            if shape == "block":
                continue  # the unmodified default; carries no class
            self.assertIn(
                f".screen.{shape} .cur", css,
                f"cursor shape {shape!r} has no .screen.{shape} rule in index.html",
            )


if __name__ == "__main__":
    unittest.main()
