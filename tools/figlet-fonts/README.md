# Wordmark fonts

The figlet fonts the `banners/<key>.txt` wordmarks were set in (from the
patorjk.com/TAAG collection via github.com/xero/figlet-fonts). To set a new
wordmark, e.g. while redrawing a banner:

    figlet -d tools/figlet-fonts -f "ANSI Shadow" "LCARS CONSOLE"

Classic fonts (standard, big, small, slant) ship with figlet itself
(`brew install figlet`). Paste the output into a `banners/<key>.txt` under its
`#:` color header — see any existing banner for the format.

`figlet.js` here is patorjk's FIGfont driver (MIT, the engine behind
patorjk.com/software/taag). `build_ghostty.py --studio` inlines it plus every
`.flf` in this directory into the studio's **Wordmark lab**, so dropping a new
font file here makes it available in the browser tool on the next rebuild.
