"""tools/retro-default: fence splice is idempotent and preserves user config."""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_loader(
    "retro_default", SourceFileLoader("retro_default", str(ROOT / "tools/retro-default")))
assert SPEC and SPEC.loader
rd = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rd)


class SpliceTests(unittest.TestCase):
    def test_fresh_file_gets_fence(self):
        out = rd.splice_ghostty("", "sci-fi-tron")
        self.assertEqual(rd.current_ghostty_slug(out), "sci-fi-tron")
        self.assertTrue(out.startswith(rd.FENCE_OPEN))

    def test_user_lines_survive_and_fence_replaced_in_place(self):
        user = "font-size = 15\n# mine\n"
        first = rd.splice_ghostty(user, "retro-apple-ii")
        second = rd.splice_ghostty(first + "theme = after\n", "corpo-severance-lumon")
        self.assertIn("font-size = 15\n# mine\n", second)
        self.assertIn("theme = after\n", second)
        self.assertEqual(second.count(rd.FENCE_OPEN), 1)
        self.assertEqual(rd.current_ghostty_slug(second), "corpo-severance-lumon")
        self.assertNotIn("retro-apple-ii", second)

    def test_pick_avoids_current_and_every_slug_is_built(self):
        pool = rd.pool("all")
        slugs = {rd.slug_for(p) for p in pool}
        self.assertEqual(len(slugs), len(pool))
        worn = rd.slug_for(pool[0])
        for _ in range(50):
            self.assertNotEqual(rd.slug_for(rd.pick("all", avoid_slug=worn)), worn)
        # iTerm2 guid is deterministic on the name, so the pref stays valid.
        self.assertEqual(rd.bp.guid(pool[0]["Name"]), rd.bp.guid(pool[0]["Name"]))


if __name__ == "__main__":
    unittest.main()
