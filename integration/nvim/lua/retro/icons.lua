-- retro.icons — ASCII icon sets for the purist. Part of retro-terminals.
--
-- A real VT220 never drew a folder glyph. If you'd rather keep Neo-tree in
-- pure ASCII than lean on the profiles' Nerd Font fallback (SymbolsNFM),
-- merge this into your neo-tree opts:
--
--   require("neo-tree").setup(vim.tbl_deep_extend(
--     "force", my_opts, require("retro.icons").neotree))
--
-- or with lazy.nvim:
--
--   opts = function(_, opts)
--     return vim.tbl_deep_extend("force", opts, require("retro.icons").neotree)
--   end
--
-- Works with zero Nerd Fonts installed; pairs well with :Retro (retro-ansi).

local M = {}

M.neotree = {
  default_component_configs = {
    icon = {
      folder_closed = "+",
      folder_open = "-",
      folder_empty = ".",
      default = " ",
      -- neo-tree v3's default provider pulls file glyphs from
      -- nvim-web-devicons; a no-op keeps `default` for every file.
      provider = function() end,
    },
    indent = {
      with_expanders = true,
      expander_collapsed = "+",
      expander_expanded = "-",
    },
    modified = { symbol = "*" },
    git_status = {
      symbols = {
        added = "A", modified = "M", deleted = "D", renamed = "R",
        untracked = "?", ignored = "I", unstaged = "U", staged = "S",
        conflict = "!",
      },
    },
  },
}

return M
