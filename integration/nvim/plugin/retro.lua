-- :Retro — toggle the palette-following colorscheme. Part of retro-terminals.
--
-- Flips between `retro-ansi` (16-color mode, follows the terminal's ANSI
-- palette) and whatever truecolor scheme you were using. It SAVES your current
-- colorscheme + termguicolors on the way in and RESTORES them on the way out,
-- so it's daily-driver-agnostic — no scheme name is hardcoded.
--
-- Auto-loaded when this repo's integration/nvim dir is on the runtimepath
-- (via a lazy.nvim `dir` spec, or `vim.opt.rtp:append` + sourcing this file).

if vim.g.loaded_retro_ansi then return end
vim.g.loaded_retro_ansi = true

local saved = nil

vim.api.nvim_create_user_command("Retro", function()
  if vim.g.colors_name == "retro-ansi" then
    -- leaving: restore the look you came from (fall back to truecolor on)
    vim.o.termguicolors = saved and saved.tgc or true
    if saved and saved.scheme then
      pcall(vim.cmd.colorscheme, saved.scheme)
    end
    saved = nil
  else
    -- entering: remember the current look, then follow the terminal
    saved = { scheme = vim.g.colors_name, tgc = vim.o.termguicolors }
    vim.cmd.colorscheme("retro-ansi")   -- the scheme sets notermguicolors itself
  end
end, { desc = "toggle retro-ansi (nvim follows the terminal ANSI palette)" })
