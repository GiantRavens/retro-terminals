#!/usr/bin/env python3
"""
Retro terminal palette port: iTerm2 -> Ghostty.

Reuses the exact SPEC in build_profiles.py (imported, never duplicated) and
compiles each profile into Ghostty config. The 39 palettes stay single-sourced:
edit a palette in build_profiles.py, re-run both builders, and iTerm2 + Ghostty
agree. iTerm2 stays the daily driver (unlimited scrollback, session logging);
Ghostty gets the real GPU CRT shader the iTerm2 profiles could only fake.

Emits under ~/.config/ghostty/ (override with --dest):

  themes/<slug>       colors only — drop-in for an existing setup:
                      put `theme = <slug>` in your main config, or browse them
                      with `ghostty +list-themes`.
  retro/<slug>        fully self-contained config (colors + font + window + CRT
                      shader). Launch a styled window with:
                        ghostty --config-file=~/.config/ghostty/retro/<slug>
                      (macOS: open -na Ghostty --args --config-file=...)
  shaders/crt.glsl    the CRT fragment shader, copied from this repo. Attached
                      to the same "tube" machines that got the iTerm2 bezel.
  retro/aliases.sh    one `ghostty-<name>` shell function per profile (macOS).

Where iTerm2 and Ghostty diverge (documented so the mapping isn't magic):
  * Transparency is INVERTED: iTerm2 0=opaque; Ghostty background-opacity 1=opaque.
  * iTerm2 "Blur Radius" (a Core Image sigma) has no 1:1 Ghostty analog ->
    we emit `background-blur = true`.
  * Vertical/Horizontal Spacing (a multiplier) -> adjust-cell-height/width (a %).
  * Bitmap/pixel fonts with AA off: Ghostty has no AA toggle; they may render
    soft. The palette still carries the identity.
  * Link Color, Minimum Contrast, Use Bright Bold, boot banners: no clean
    Ghostty equivalent -> dropped. (Banners belong in your shell rc anyway.)

Run:  python3 build_ghostty.py             # write into ~/.config/ghostty
      python3 build_ghostty.py --stdout    # print one example config, write nothing
      python3 build_ghostty.py --dest DIR  # write into DIR instead
      python3 build_ghostty.py --no-titles # don't pin the machine name in the title
"""

import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_profiles as bp  # noqa: E402  (path insert must precede import)

# Each pack + the tag it carries (matches build_profiles' ns.lower()).
GROUPS = [
    (bp.PROFILES,  "retro"),
    (bp.FICTION,   "sci-fi"),
    (bp.AESTHETIC, "aesthetic"),
    (bp.CORP,      "corp"),
]

# build_profiles: UNDERLINE, VBAR, BOX = 0, 1, 2
CURSOR = {0: "underline", 1: "bar", 2: "block"}

# Bake `title = <machine name>` into each config so the window/tab shows which
# profile it is. Static — it replaces the dynamic dir/command title. Default-on
# (these are aesthetic profiles; telling windows apart matters); --no-titles off.
WANT_TITLES = True

SHADER_SRC = os.path.join(HERE, "shaders", "crt.glsl")


# ---------------------------------------------------------------------------
# Conversions  (iTerm2 float-component color dicts -> Ghostty hex + config)
# ---------------------------------------------------------------------------

def to_hex(c: dict) -> str:
    """iTerm2 sRGB component dict -> #rrggbb. Round-trips the original byte."""
    return "#{:02x}{:02x}{:02x}".format(
        round(c["Red Component"] * 255),
        round(c["Green Component"] * 255),
        round(c["Blue Component"] * 255),
    )


def kebab(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def parse_font(normal_font: str):
    """'Glass TTY VT220 18' -> ('Glass TTY VT220', '18'). Size is the last token."""
    family, _, size = normal_font.rpartition(" ")
    return family, size


def color_lines(p: dict) -> list:
    L = [f"palette = {i}={to_hex(p[f'Ansi {i} Color'])}" for i in range(16)]
    L += [
        f"background = {to_hex(p['Background Color'])}",
        f"foreground = {to_hex(p['Foreground Color'])}",
        f"cursor-color = {to_hex(p['Cursor Color'])}",
        f"cursor-text = {to_hex(p['Cursor Text Color'])}",
        f"selection-background = {to_hex(p['Selection Color'])}",
        f"selection-foreground = {to_hex(p['Selected Text Color'])}",
    ]
    # bold-color needs Ghostty >= 1.1. If your build logs "unknown field
    # bold-color", delete these lines (they only warn, they don't stop launch).
    if to_hex(p["Bold Color"]) != to_hex(p["Foreground Color"]):
        L.append(f"bold-color = {to_hex(p['Bold Color'])}")
    return L


def config_lines(p: dict, tube: bool) -> list:
    family, size = parse_font(p["Normal Font"])
    L = [
        f'font-family = "{family}"',
        f"font-size = {size}",
        f"cursor-style = {CURSOR.get(p['Cursor Type'], 'block')}",
        f"cursor-style-blink = {'true' if p['Blinking Cursor'] else 'false'}",
    ]
    opacity = round(1.0 - float(p.get("Transparency", 0.0)), 3)  # iTerm2 is inverted
    if opacity < 1.0:
        L.append(f"background-opacity = {opacity}")
    if p.get("Blur"):
        L.append("background-blur = true")
    # Breathing room so glyphs sit off the edge. Tubes get more: the CRT
    # curvature bows the edge and the shader bezel frames a background margin
    # into a real gap between the frame and the text.
    px, py = (26, 24) if tube else (12, 10)
    L += [
        f"window-padding-x = {px}",
        f"window-padding-y = {py}",
        "window-padding-color = background",
        "window-padding-balance = true",
    ]
    vs = float(p.get("Vertical Spacing", 1.0))
    if abs(vs - 1.0) > 1e-6:
        L.append(f"adjust-cell-height = {round((vs - 1.0) * 100)}%")
    hs = float(p.get("Horizontal Spacing", 1.0))
    if abs(hs - 1.0) > 1e-6:
        L.append(f"adjust-cell-width = {round((hs - 1.0) * 100)}%")
    if WANT_TITLES:
        L.append(f"title = {base_name(p)}")   # static — shows the machine name
    return L


def base_name(p: dict) -> str:
    """'Sci-Fi · The Matrix' -> 'The Matrix'."""
    return p["Name"].split(" · ", 1)[1]


def is_tube(p: dict) -> bool:
    # Tube machines are exactly the ones build_profiles gave a scanline bezel.
    return "Background Image Location" in p


def render_theme(p: dict) -> str:
    head = [f"# retro-terminals -> Ghostty theme :: {p['Name']}",
            "# generated by build_ghostty.py — edit build_profiles.py, not this file",
            ""]
    return "\n".join(head + color_lines(p)) + "\n"


def render_config(p: dict, shader_path: str) -> str:
    head = [f"# retro-terminals -> Ghostty config :: {p['Name']}",
            "# generated by build_ghostty.py — edit build_profiles.py, not this file",
            "# launch:  ghostty --config-file=<this file>",
            ""]
    body = color_lines(p) + [""] + config_lines(p, is_tube(p))
    if is_tube(p):
        body += [f"custom-shader = {shader_path}", "custom-shader-animation = true"]
    return "\n".join(head + body) + "\n"


# ---------------------------------------------------------------------------
# Studio  --  browse + tune + publish, as a self-contained HTML page
# ---------------------------------------------------------------------------
# build_ghostty.py --studio fills tools/studio-template.html with the SPEC
# (same palettes iTerm2/Ghostty use) so the browser tool never drifts from the
# source. The page previews the CRT with the exact crt.glsl math and emits a
# paste-to-publish shell command that writes retro/<slug> + the shared shader.

# Boot banners live in build_profiles as per-pack dicts; merge for sample text.
ALL_BANNERS = {**bp.BANNERS, **bp.FBANNERS, **bp.ABANNERS, **bp.CBANNERS}


def profile_json(p: dict, tag: str) -> dict:
    base = base_name(p)
    family, size = parse_font(p["Normal Font"])
    sample = ALL_BANNERS.get(base) or [base, "", "READY."]
    return {
        "name": p["Name"],
        "base": base,
        "slug": f"{tag}-{kebab(base)}",
        "group": tag,
        "tube": is_tube(p),
        "pad": 26 if is_tube(p) else 12,   # default window-padding; studio dial overrides
        "bg": to_hex(p["Background Color"]),
        "fg": to_hex(p["Foreground Color"]),
        "ansi": [to_hex(p[f"Ansi {i} Color"]) for i in range(16)],
        "font": family,
        "size": int(size),
        "sample": "\n".join(sample),
        "themeText": "\n".join(color_lines(p)),
        # config WITHOUT the shader line — the studio appends it when CRT is on
        "configText": "\n".join(color_lines(p) + [""] + config_lines(p, is_tube(p))),
    }


def build_studio(dest: str) -> str:
    tmpl_path = os.path.join(HERE, "tools", "studio-template.html")
    with open(tmpl_path) as f:
        tmpl = f.read()
    profiles = [profile_json(p, tag) for group, tag in GROUPS for p in group]
    shader_src = ""
    if os.path.exists(SHADER_SRC):
        with open(SHADER_SRC) as f:
            shader_src = f.read()
    # Portable paths so a published config/command works on any machine, not
    # just this one (the studio may be served publicly from GitHub Pages). Shell
    # parts use $HOME (expands when pasted); the config's custom-shader uses ~
    # (Ghostty expands it). A non-home --dest falls back to absolute.
    home = os.path.expanduser("~")
    if dest == home or dest.startswith(home + os.sep):
        rel = os.path.relpath(dest, home)
        shell_base, conf_shader = f"$HOME/{rel}", f"~/{rel}/shaders/crt.glsl"
    else:
        shell_base, conf_shader = dest, os.path.join(dest, "shaders", "crt.glsl")
    studio = {
        "shaderPath": conf_shader,             # -> config `custom-shader =` (Ghostty ~-expands)
        "retroDir": f"{shell_base}/retro",     # -> shell command ("$HOME/…" on paste)
        "shadersDir": f"{shell_base}/shaders",
    }
    html = (tmpl
            .replace("/*__PROFILES__*/", json.dumps(profiles))
            .replace("/*__SHADER__*/", json.dumps(shader_src))
            .replace("/*__STUDIO__*/", json.dumps(studio)))
    out = os.path.join(HERE, "ghostty-studio.html")
    with open(out, "w") as f:
        f.write(html)
    return out


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------

def write_shader(dest: str) -> str:
    shaders_dir = os.path.join(dest, "shaders")
    os.makedirs(shaders_dir, exist_ok=True)
    out = os.path.join(shaders_dir, "crt.glsl")
    if os.path.exists(SHADER_SRC):
        shutil.copyfile(SHADER_SRC, out)
    else:
        print(f"  ! {SHADER_SRC} missing — tube profiles will point at a shader "
              f"that isn't there")
    return out


def main():
    argv = sys.argv[1:]

    dest = os.path.expanduser("~/.config/ghostty")
    if "--dest" in argv:
        dest = os.path.abspath(os.path.expanduser(argv[argv.index("--dest") + 1]))
    if "--no-titles" in argv:
        globals()["WANT_TITLES"] = False

    # Preview one representative tube config, write nothing.
    if "--stdout" in argv:
        matrix = next(p for g, _ in GROUPS for p in g if base_name(p) == "The Matrix")
        shader = os.path.join(dest, "shaders", "crt.glsl")
        print(render_config(matrix, shader))
        return

    # Build the browse/tune/publish studio page (into the repo root).
    if "--studio" in argv:
        out = build_studio(dest)
        n = sum(len(g) for g, _ in GROUPS)
        print(f"Wrote studio -> {out}  ({n} profiles, shader paths -> {dest})")
        print(f"Open it:  open {out}")
        return

    themes_dir = os.path.join(dest, "themes")
    retro_dir = os.path.join(dest, "retro")
    os.makedirs(themes_dir, exist_ok=True)
    os.makedirs(retro_dir, exist_ok=True)
    shader_path = write_shader(dest)

    aliases = [
        "# retro-terminals launchers (macOS). Source from your ~/.zshrc:",
        f"#   source {os.path.join(retro_dir, 'aliases.sh')}",
        "# Each opens a NEW Ghostty window fully styled as that machine.",
        "",
    ]

    total = tubes = 0
    for group, tag in GROUPS:
        print(f"\n[{tag}]")
        for p in group:
            base = base_name(p)
            slug = f"{tag}-{kebab(base)}"
            tube = is_tube(p)

            with open(os.path.join(themes_dir, slug), "w") as f:
                f.write(render_theme(p))
            cfg_path = os.path.join(retro_dir, slug)
            with open(cfg_path, "w") as f:
                f.write(render_config(p, shader_path))

            fn = "ghostty-" + kebab(base)
            aliases.append(
                f'{fn}() {{ open -na Ghostty --args --config-file="{cfg_path}"; }}'
                f'  # {p["Name"]}'
            )

            total += 1
            tubes += tube
            print(f"    {base:<22} {'[CRT]' if tube else '     '} theme+config -> {slug}")

    with open(os.path.join(retro_dir, "aliases.sh"), "w") as f:
        f.write("\n".join(aliases) + "\n")

    print(f"\nWrote {total} profiles ({tubes} with the CRT shader) to {dest}")
    print(f"  themes/   {total} color-only themes  ->  `theme = <slug>`")
    print(f"  retro/    {total} full configs        ->  ghostty --config-file=retro/<slug>")
    print(f"  shaders/crt.glsl, retro/aliases.sh")
    print("\nTry one:  open -na Ghostty --args "
          f'--config-file="{os.path.join(retro_dir, "sci-fi-the-matrix")}"')


if __name__ == "__main__":
    main()
