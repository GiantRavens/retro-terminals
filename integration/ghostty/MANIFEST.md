# Ghostty workbench execution manifest

Inputs observed: Ghostty 1.4.0 on macOS; an existing Atari default include;
47 generated retro profiles; bundled and local color themes; installed fonts;
an existing SSH/tmux discovery script coupled to the iTerm2 Python runtime.

Strategies:

| Input | Strategy | Expected outcome |
|---|---|---|
| Retro profile | Read appearance settings only; clear inherited lists first | Actual font, palette, and optional CRT shader in Ghostty |
| Color theme | Merge safe color keys with Ghostty defaults | Complete palette without leftover Atari colors |
| Font | Use Ghostty's font discovery; reset all font-family lists | Real rendered normal/bold/italic sample |
| CRT | Off / profile default / shared CRT shader | Compare plain and tube versions |
| User config | Append one final managed include, back up once | Keep existing scrollback and unrelated preferences |
| Preview | Lock, journal, atomic writes, reload; restore on cancel | Enter commits; cancel/interruption restores; next run recovers crashes |
| Remote server | Discover once; manifest; attach by stable tmux ID | One tab per discovered session, no new sessions |

Events: operation.failed; preview.start/finish; restore.finish;
apply.finish; discover.start/finish; launch.start/finish. JSONL records include
failure class and reason. Reload acknowledgement proves action dispatch, not
visual rendering. SSH attachment is explicitly unverified until run in its tab.

Verification: isolated config fixtures for layering, cancel/crash restoration,
concurrent-edit protection and quoting; compile AppleScript; discover real
installed inputs; live Ghostty preview when automation is available. Avoid SSH
connections to an unspecified server. UI preview changes the shared config and
can affect other windows using it. Explicit launch-time overrides may win.

## Predicted versus observed — 2026-10-28

- Discovered 913 looks: 47 full retro profiles and 866 color themes.
- Ghostty's general font list showed 31 families. Explicit family queries
  resolved four more usable retro families: 35 total, with every referenced
  retro profile font available. This shifted fallback detection upstream into
  discovery; a regression test covers sparse-family resolution.
- Native config validation and effective-config checks passed for HAL/CRT off,
  HAL/Monaco/CRT on, and Catppuccin Mocha/Monaco/CRT off. The original scrollback
  setting survived each combination. Ghostty acknowledged native reload.
- 16 tests cover state recovery, edits, locking, font/shader reset, SSH errors,
  session quoting, font discovery and an actual curses PTY. The PTY test checks
  look/font/CRT navigation and both cancel and save with native reload mocked.
- Native AppleScript tab-creation code compiles against Ghostty 1.4.0.
  No remote connection or attachment was attempted without a specified host.
- Visual inspection remains unverified: this session's computer-use tool
  cannot access Ghostty. Native config acceptance is not proof of GPU shader
  rendering. The existing shared CRT shader is reused without modification.
- Existing `ghostty-random` shell behavior is preserved. The new persistent
  random-selection command is `ghostty-roll` to avoid a name collision.
