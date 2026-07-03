-- retro-ansi — a Neovim colorscheme that FOLLOWS the terminal's ANSI palette.
--
-- Part of retro-terminals. Modern colorschemes bake 24-bit hex and ignore the
-- terminal's 16-color palette — which is why nvim doesn't wear your retro
-- Ghostty/iTerm2 profile even though tmux and starship do. This scheme turns
-- OFF termguicolors and paints every highlight group from cterm slots 0-15,
-- which each retro profile redefines. So nvim automatically wears whichever
-- machine the window is running: a green-phosphor window -> monochrome-green
-- nvim; C64 -> C64 colors. Authentically period: a real VT220 never had
-- truecolor syntax highlighting.
--
-- Install: put this repo's integration/nvim on the runtimepath (init.lua does
-- it), then `:colorscheme retro-ansi` — or `:Retro` to toggle in and back out.
--
-- Slot legend (whatever the ACTIVE profile defined for each):
--   0 bg-dark    8 grey        1 red      9 br-red
--   2 green     10 br-green    3 yellow  11 br-yellow
--   4 blue      12 br-blue     5 magenta 13 br-magenta
--   6 cyan      14 br-cyan     7 fg-light 15 br-white

vim.cmd("highlight clear")
if vim.fn.exists("syntax_on") == 1 then vim.cmd("syntax reset") end
vim.o.termguicolors = false          -- cterm (ANSI) colors -> follow the terminal
vim.g.colors_name = "retro-ansi"

-- Only sets the keys given, so nil fg/bg means "use the terminal default"
-- (that's how Normal inherits the profile's own ink-on-paper).
local function hi(group, fg, bg, attr)
  local o = {}
  if fg ~= nil then o.ctermfg = fg end
  if bg ~= nil then o.ctermbg = bg end
  if attr ~= nil then o.cterm = attr end
  vim.api.nvim_set_hl(0, group, o)
end
local function link(a, b) vim.api.nvim_set_hl(0, a, { link = b }) end

-- core --------------------------------------------------------------------
hi("Normal")                              -- terminal fg on terminal bg
hi("NormalNC")
hi("NormalFloat", 7, 0)
hi("FloatBorder", 8, nil)
hi("EndOfBuffer", 8)
hi("Cursor",      nil, nil, { reverse = true })
hi("TermCursor",  nil, nil, { reverse = true })

-- syntax ------------------------------------------------------------------
hi("Comment",      8,  nil, { italic = true })
hi("Constant",     6)
hi("String",       2)
hi("Character",    2)
hi("Number",       6)
hi("Boolean",      6,  nil, { bold = true })
hi("Float",        6)
hi("Identifier",   7)
hi("Function",     4,  nil, { bold = true })
hi("Statement",    4,  nil, { bold = true })
hi("Conditional",  4,  nil, { bold = true })
hi("Repeat",       4,  nil, { bold = true })
hi("Label",        4)
hi("Operator",     7)
hi("Keyword",      4,  nil, { bold = true })
hi("Exception",    1,  nil, { bold = true })
hi("PreProc",      5)
hi("Include",      5)
hi("Define",       5)
hi("Macro",        5)
hi("Type",         3)
hi("StorageClass", 3)
hi("Structure",    3)
hi("Typedef",      3)
hi("Special",      5)
hi("SpecialChar",  5)
hi("Delimiter",    7)
hi("Tag",          4)
hi("Underlined",   4,  nil, { underline = true })
hi("Error",        15, 1)
hi("Todo",         0,  3,   { bold = true })

-- ui ----------------------------------------------------------------------
hi("CursorLine",   nil, 0)
hi("CursorColumn", nil, 0)
hi("CursorLineNr", 3,   nil, { bold = true })
hi("LineNr",       8)
hi("SignColumn")
hi("ColorColumn",  nil, 0)
hi("Visual",       nil, nil, { reverse = true })
hi("Search",       0,   3)
hi("IncSearch",    0,   11,  { bold = true })
hi("CurSearch",    0,   11,  { bold = true })
hi("MatchParen",   11,  nil, { bold = true })
hi("StatusLine",   nil, nil, { reverse = true })
hi("StatusLineNC", 8,   0)
hi("WinSeparator", 8)
hi("VertSplit",    8)
hi("Pmenu",        7,   8)
hi("PmenuSel",     nil, nil, { reverse = true })
hi("PmenuSbar",    nil, 8)
hi("PmenuThumb",   nil, 7)
hi("TabLine",      7,   0)
hi("TabLineSel",   nil, nil, { bold = true, reverse = true })
hi("TabLineFill",  nil, 0)
hi("Folded",       8,   0)
hi("FoldColumn",   8)
hi("Directory",    4,   nil, { bold = true })
hi("Title",        5,   nil, { bold = true })
hi("NonText",      8)
hi("SpecialKey",   8)
hi("Whitespace",   8)
hi("WildMenu",     0,   3)
hi("QuickFixLine", nil, 0,   { bold = true })
hi("ModeMsg",      2)
hi("MoreMsg",      2)
hi("Question",     2)
hi("WarningMsg",   3,   nil, { bold = true })
hi("ErrorMsg",     1,   nil, { bold = true })

-- diffs / vcs -------------------------------------------------------------
hi("DiffAdd",    2, 0)
hi("DiffChange", 4, 0)
hi("DiffDelete", 1, 0)
hi("DiffText",   nil, nil, { reverse = true })
hi("Added",      2)
hi("Changed",    4)
hi("Removed",    1)

-- diagnostics -------------------------------------------------------------
hi("DiagnosticError", 1)
hi("DiagnosticWarn",  3)
hi("DiagnosticInfo",  6)
hi("DiagnosticHint",  8)
hi("DiagnosticOk",    2)
hi("DiagnosticUnderlineError", 1, nil, { undercurl = true })
hi("DiagnosticUnderlineWarn",  3, nil, { undercurl = true })
hi("DiagnosticUnderlineInfo",  6, nil, { undercurl = true })
hi("DiagnosticUnderlineHint",  8, nil, { undercurl = true })

-- spell -------------------------------------------------------------------
hi("SpellBad",   1, nil, { undercurl = true })
hi("SpellCap",   4, nil, { undercurl = true })
hi("SpellRare",  5, nil, { undercurl = true })
hi("SpellLocal", 6, nil, { undercurl = true })

-- treesitter (most @groups default-link to the above; pin the common ones) -
link("@comment", "Comment")
link("@keyword", "Keyword")
link("@keyword.function", "Keyword")
link("@keyword.return", "Keyword")
link("@conditional", "Conditional")
link("@repeat", "Repeat")
link("@string", "String")
link("@string.escape", "SpecialChar")
link("@character", "Character")
link("@number", "Number")
link("@boolean", "Boolean")
link("@float", "Float")
link("@function", "Function")
link("@function.call", "Function")
link("@function.builtin", "Function")
link("@method", "Function")
link("@constructor", "Type")
link("@variable", "Identifier")
link("@variable.member", "Identifier")
link("@variable.builtin", "Special")
link("@parameter", "Identifier")
link("@property", "Identifier")
link("@field", "Identifier")
link("@type", "Type")
link("@type.builtin", "Type")
link("@namespace", "Type")
link("@constant", "Constant")
link("@constant.builtin", "Constant")
link("@operator", "Operator")
link("@punctuation", "Delimiter")
link("@punctuation.bracket", "Delimiter")
link("@punctuation.delimiter", "Delimiter")
link("@tag", "Tag")
link("@tag.attribute", "PreProc")
link("@attribute", "PreProc")
link("@preproc", "PreProc")
