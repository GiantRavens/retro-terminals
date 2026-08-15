"""Regression tests for the real-window demo's viewport envelope."""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
DEMO_PATH = ROOT / "tools/retro-demo"
SPEC = importlib.util.spec_from_loader("retro_demo", SourceFileLoader("retro_demo", str(DEMO_PATH)))
assert SPEC and SPEC.loader
demo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(demo)

import build_profiles as bp  # noqa: E402
from build_ghostty import GROUPS, is_tube, parse_font  # noqa: E402

# Conservative logical-pixel viewport: smaller than the measured 1920x1243
# desktop on the development Mac, and representative of a standard laptop.
VIEWPORT_WIDTH = 1440
VIEWPORT_HEIGHT = 900
WINDOW_CHROME_WIDTH = 100
WINDOW_CHROME_HEIGHT = 100


def estimated_window(profile: dict) -> tuple[float, float]:
    family, raw_size = parse_font(profile["Normal Font"])
    size = float(raw_size)
    cell_width = size * bp.FONT_CELL_EM.get(family, 0.6)
    cell_width *= float(profile.get("Horizontal Spacing", 1.0))
    cell_height = size * float(profile.get("Vertical Spacing", 1.0))
    pad_x, pad_y = (26, 24) if is_tube(profile) else (12, 10)
    return (
        demo.DEMO_COLUMNS * cell_width + 2 * pad_x + WINDOW_CHROME_WIDTH,
        demo.DEMO_ROWS * cell_height + 2 * pad_y + WINDOW_CHROME_HEIGHT,
    )


class DemoSizeTest(unittest.TestCase):
    def test_every_profile_fits_standard_mac_viewport(self):
        failures = []
        for group, _tag in GROUPS:
            for profile in group:
                width, height = estimated_window(profile)
                if width > VIEWPORT_WIDTH or height > VIEWPORT_HEIGHT:
                    failures.append(f"{profile['Name']}: {width:.0f}x{height:.0f}")
        self.assertEqual([], failures, "oversize profiles: " + ", ".join(failures))

    def test_ms_dos_editor_has_bounded_geometry(self):
        profile = next(p for group, _ in GROUPS for p in group if p["Name"].endswith("MS-DOS Editor"))
        width, height = estimated_window(profile)
        self.assertLessEqual(width, VIEWPORT_WIDTH)
        self.assertLessEqual(height, VIEWPORT_HEIGHT)

    def test_ghostty_launch_overrides_restored_window_size(self):
        profile = demo.profile_manifest("retro")[0]
        args = demo.GhosttyWindow(profile, "ghostty", dry_run=True).launch_arguments()
        self.assertIn(f"--window-width={demo.DEMO_COLUMNS}", args)
        self.assertIn(f"--window-height={demo.DEMO_ROWS}", args)
        self.assertIn("--window-save-state=never", args)


if __name__ == "__main__":
    unittest.main()
