import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "retro-prompts.zsh"


def startup_state(prompt_on_start=None):
    env = os.environ.copy()
    env["RETRO_MACHINE"] = "solarpunk"
    env.pop("RETRO_PROMPT_ON_START", None)
    if prompt_on_start is not None:
        env["RETRO_PROMPT_ON_START"] = prompt_on_start
    command = (
        "precmd_functions=(starship_precmd); PROMPT=starship; "
        f"source {PROMPTS}; "
        "print -r -- $PROMPT; print -r -- ${(j:,:)precmd_functions}"
    )
    result = subprocess.run(
        ["zsh", "-fic", command],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


class PromptStartupTests(unittest.TestCase):
    def test_profile_start_preserves_starship_by_default(self):
        self.assertEqual(["starship", "starship_precmd"], startup_state())

    def test_period_prompt_remains_available_as_opt_in(self):
        prompt, hooks = startup_state("1")
        self.assertEqual("%F{29}garden> %f", prompt)
        self.assertEqual("", hooks)


if __name__ == "__main__":
    unittest.main()
