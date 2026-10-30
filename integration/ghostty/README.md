# Ghostty workbench

A Python standard-library tool for choosing a look **in Ghostty's real
renderer**. It reuses the generated retro profiles, installed fonts, bundled
Ghostty themes, and this repo's CRT shader. No Python packages or server needed.

Install after `python3 build_ghostty.py` and the font setup:

```sh
python3 tools/ghostty-workbench install
```

This installs symlinks in `~/.local/bin`, backs up the existing config as
`config.before-workbench` (or `config.ghostty.before-workbench`), and appends
one final include of `workbench-appearance.conf`. It keeps your existing
settings, including the retro-default block. Appearance choices in the final
include take precedence; an explicit `--config-file` at launch can still win.
Run the picker in a normal Ghostty window. It also works inside local tmux
when Ghostty's environment is inherited.

```sh
ghostty-show                         # retro profiles AND ordinary themes
ghostty-show --kind retro            # full machine looks, including fonts
ghostty-show --kind theme            # ordinary color themes
ghostty-fonts                        # browse installed fonts, actually rendered
ghostty-crt                          # tune shared curvature, bloom, scanlines, etc.
ghostty-roll                       # save a random full retro look
ghostty-roll --kind theme          # save a random ordinary theme
ghostty-roll --match phosphor --crt off
ghostty-workbench apply 'retro:sci-fi-hal-9000' --crt on
ghostty-workbench apply 'theme:Catppuccin Mocha' --font Monaco --crt off
```

`ghostty-roll` updates the shared default and reloads it. Your existing
`ghostty-random` shell function continues to open a separate random machine
instance without changing the shared default. The underlying command is
`tools/retro-random --terminal ghostty`. The distinct names avoid shadowing the
existing function loaded by `retro/aliases.sh`.

## Picker controls

| Key | Action |
|---|---|
| Up/down, left/right, h/j/k/l | Navigate and preview |
| Tab | Switch between looks and fonts |
| / | Search; Enter finishes editing the search |
| r / t / a | Retro profiles / ordinary themes / all |
| c | CRT: profile default → on → off |
| + / - | Adjust font size |
| d | Restore the profile's font and size |
| Enter | Apply the highlighted entry and save the combination |
| Escape / q / Ctrl-C | Cancel and restore the previous appearance |
| ? | Help |

The specimen includes ordinary text, ambiguous characters, ligatures,
bold/italic, ANSI colors, Unicode and Nerd Font glyphs. Ghostty may synthesize
styles or use fallback fonts for missing glyphs. CRT "on" uses the repo's
current `shaders/crt.glsl`; "auto" uses the selected profile's shader setting.
Run `ghostty-crt` (or `ghostty-workbench crt`) from any local Ghostty session
to tune the nine CRT dials in the actual terminal. Up/down selects a dial;
left/right or +/- adjusts it; `d` resets all dials to the shipped defaults.
Changes preview live across sessions using the shared configuration/shader.
Enter saves; Escape/q/Ctrl-C restores both the prior shader and appearance.
Your colors and fonts are retained, and CRT is enabled when the tuner opens.
Saved values are read on the next visit. The browser Studio is also available.
The workbench and Studio use the installed `shaders/crt.glsl`; rebuilding
profiles or publishing from Studio can replace your saved tuning.
Launch-time overrides can prevent a session from adopting the shader.
After a crash, `ghostty-workbench recover` restores both files.
`ghostty-workbench crt --dry-run` prints the input manifest without changes.

**Preview reloads the shared config and can affect other Ghostty windows.**
The font, palette, and shader are real terminal settings. The manifest and
events distinguish successful reload dispatch from actual visual verification.
Running shells retain their environment; new shells get the selected machine's
`RETRO_MACHINE`. Existing boot chatter is not replayed by an appearance change.
Font sizes manually zoomed in Ghostty may retain that zoom after a reload.

The picker holds a lock and writes a recovery journal before previewing. On
cancel it restores the previous appearance exactly. After an abrupt crash:

```sh
ghostty-workbench recover
```

The next picker/apply invocation also recovers an abandoned preview first.
External edits are never overwritten during recovery: a conflict keeps the
journal and prints its path for inspection. SIGKILL/power loss cannot restore
the screen immediately; recovery restores it on the next invocation.

## Remote tmux sessions

```sh
ghostty-tmux myserver --dry-run        # SSH discovery + JSON manifest; no tabs
ghostty-tmux myserver                  # one new window, one tab per session
ghostty-tmux myserver --session work   # exact session name or $ID
ghostty-tmux myserver --socket other -p 2222 -i ~/.ssh/id_ed25519
```

SSH aliases, jump hosts, and authentication use your existing `~/.ssh/config`.
Discovery has a 30-second timeout. Session names are display data; attachment
uses stable tmux IDs with shell quoting. No sessions are created and existing
clients are not detached. If launch fails partway, already opened tabs remain
and the error reports that failure; inspect before rerunning. Successful tab
creation does not prove successful SSH attachment; errors stay visible in each
tab. macOS may request its normal Automation permission on the first run.

## Inspection and telemetry

```sh
ghostty-workbench doctor               # JSON input manifest, no config writes
ghostty-roll --dry-run               # predicted selection/config, no writes
python3 -m unittest discover -s tests -p test_ghostty_workbench.py -v
```

`~/.config/ghostty/workbench-events.jsonl` records previews, commits,
restoration, discovery, tab creation and classified failures. No telemetry is
sent anywhere. `--config-dir /path/to/ghostty` before the subcommand supports
isolated fixtures. The workbench is currently macOS-specific for native reload
and tab automation; the rendering and state-management code is ordinary Python.

To stop using the workbench, remove only its fenced include from the main
config and reload Ghostty. Your previous retro default and preferences remain.
