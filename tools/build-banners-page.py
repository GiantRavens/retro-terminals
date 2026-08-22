#!/usr/bin/env python3
"""Generate banners.html: every boot banner rendered to static HTML.

Each banner is produced by the real engine (tools/retro-banner) and its
ANSI output converted to <pre> + <span> runs, so the page can never
drift from what a terminal actually shows. Grouped by pack in the same
curated order as the demo tour.
"""
import html
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import build_profiles as bp              # noqa: E402
from build_ghostty import GROUPS, base_name  # noqa: E402

SGR = re.compile(r"\x1b\[([0-9;]*)m")


STYLES: dict = {}


def cls(fg, bg):
    key = (fg, bg)
    if key not in STYLES:
        STYLES[key] = f"s{len(STYLES)}"
    return STYLES[key]


def ansi_to_html(text: str) -> str:
    """Convert 24-bit SGR runs to spans. Only handles what retro-banner emits."""
    out, fg, bg = [], None, None
    pos = 0

    def flush(chunk):
        if not chunk:
            return
        if fg or bg:
            out.append(f'<span class="{cls(fg, bg)}">{html.escape(chunk)}</span>')
        else:
            out.append(html.escape(chunk))

    for m in SGR.finditer(text):
        flush(text[pos:m.start()])
        pos = m.end()
        parts = [int(x) for x in m.group(1).split(";") if x] or [0]
        i = 0
        while i < len(parts):
            p = parts[i]
            if p == 0:
                fg = bg = None
            elif p == 38 and parts[i+1:i+2] == [2]:
                fg = "{:02x}{:02x}{:02x}".format(*parts[i+2:i+5]); i += 4
            elif p == 48 and parts[i+1:i+2] == [2]:
                bg = "{:02x}{:02x}{:02x}".format(*parts[i+2:i+5]); i += 4
            elif p == 49:
                bg = None
            i += 1
    flush(text[pos:])
    return "".join(out)


def main():
    key_of = bp.SHELL_KEY
    cards = []
    for group, tag in GROUPS:
        rows = []
        for profile in group:
            name = base_name(profile)
            key = key_of.get(name)
            if not key:
                continue
            r = subprocess.run([os.path.join(HERE, "retro-banner"), key],
                               capture_output=True, text=True)
            if r.returncode != 0 or not r.stdout.strip():
                print(f"  skip {key}: no render", file=sys.stderr)
                continue
            rows.append((name, key, ansi_to_html(r.stdout.rstrip("\n"))))
        if not rows:
            continue
        cards.append(f'<h2 id="{tag}">{tag}</h2>\n<div class="grid">')
        for name, key, art in rows:
            cards.append(
                f'<figure><figcaption>{html.escape(name)} '
                f'<code>{key}</code></figcaption>\n<pre>{art}</pre></figure>')
        cards.append("</div>")

    style_rules = "\n".join(
        "  ." + name + " { "
        + (f"color:#{fg};" if fg else "")
        + (f"background:#{bg};" if bg else "")
        + " }"
        for (fg, bg), name in STYLES.items())
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>retro-terminals · boot banners</title>
<style>
  body {{ background:#0b0b10; color:#d8d8e0; margin:2rem;
         font:15px/1.45 -apple-system, "Segoe UI", sans-serif; }}
  h1 {{ font-weight:600; }}  a {{ color:#7ab8ff; }}
  h2 {{ margin:2.2rem 0 .8rem; text-transform:uppercase;
        letter-spacing:.15em; font-size:.9rem; color:#9a9ab0; }}
  .grid {{ display:flex; flex-wrap:wrap; gap:1.2rem; }}
  figure {{ margin:0; }}
  figcaption {{ margin-bottom:.4rem; font-size:.85rem; color:#b8b8c8; }}
  figcaption code {{ color:#7a7a90; }}
  pre {{ margin:0; padding:.8rem 1rem; border-radius:6px; overflow-x:auto;
        font:12px/1.15 "Menlo", "DejaVu Sans Mono", "Cascadia Mono",
        "Noto Sans Mono", monospace; }}
{style_rules}
</style></head><body>
<h1>Boot banners</h1>
<p>Every profile's startup screen, rendered by the real banner engine —
many now carry braille logo art. Back to the
<a href="index.html">palette gallery</a>.</p>
{chr(10).join(cards)}
</body></html>
"""
    dest = os.path.join(ROOT, "banners.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(page)
    n = page.count("<figure>")
    print(f"banners.html: {n} banners, {len(page)//1024} KB")


if __name__ == "__main__":
    main()
