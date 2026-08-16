import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build_ghostty  # noqa: E402
import build_profiles  # noqa: E402


def profile_named(name):
    """Look a machine up by its exact name.

    This used to match on a " · <name>" suffix, from when profiles carried a
    pack prefix ("Sci-Fi · Cyberpunk 2077"). 58147dd dropped that prefix -- and
    took this lookup with it, silently: `next()` raised StopIteration, which
    reads as a test ERROR rather than a failed assertion, so the contrast check
    below stopped checking anything the same day the commit message claimed to
    have fixed contrast. A disarmed test is worse than a missing one; it reports
    green on the suite it belongs to and nobody re-reads the traceback.
    """
    profiles = (
        build_profiles.PROFILES
        + build_profiles.FICTION
        + build_profiles.AESTHETIC
        + build_profiles.CORP
    )
    for profile in profiles:
        if profile["Name"] == name:
            return profile
    raise AssertionError(
        f"no machine named {name!r}; the spec has "
        f"{', '.join(sorted(p['Name'] for p in profiles))}"
    )


class SoundAndContrastTests(unittest.TestCase):
    def test_boot_engine_has_no_audio_playback_or_terminal_bell(self):
        source = (ROOT / "tools" / "retro-boot").read_text()
        self.assertNotIn("afplay", source)
        self.assertNotIn("printf '\\a'", source)
        self.assertNotIn("snd_", source)

    def test_shipped_boot_files_do_not_select_sound_packs(self):
        offenders = [
            path.name
            for path in (ROOT / "banners").glob("*.boot")
            if "#: sound " in path.read_text()
        ]
        self.assertEqual([], offenders)

    def test_solarpunk_corrects_low_contrast_application_colors(self):
        solar = profile_named("Solarpunk")
        self.assertGreater(solar["Minimum Contrast"], 0)
        self.assertEqual(3.0, solar["_ghostty_min_contrast"])
        self.assertIn("minimum-contrast = 3", build_ghostty.render_theme(solar))


if __name__ == "__main__":
    unittest.main()
