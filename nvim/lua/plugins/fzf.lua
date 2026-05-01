return {
  "ibhagwan/fzf-lua",
  dependencies = { "nvim-tree/nvim-web-devicons" },  -- Optional icons
  config = function()
    local fzf = require("fzf-lua")

    fzf.setup({
      "default",  -- Default profile, balanced
      winopts = {
        height = 0.85,
        width = 0.85,
        preview = {
          layout = "vertical",
          vertical = "down:60%",
        },
      },
    })

    -- Shortcuts
    local map = vim.keymap.set
    map("n", "<leader>ff", fzf.files,        { desc = "Find files" })
    map("n", "<leader>fg", fzf.live_grep,    { desc = "Grep in project" })
    map("n", "<leader>fb", fzf.buffers,      { desc = "Open buffers" })
    map("n", "<leader>fh", fzf.help_tags,    { desc = "Help" })
    map("n", "<leader>fr", fzf.oldfiles,     { desc = "Recent files" })
    map("n", "<leader>fw", fzf.grep_cword,   { desc = "Grep word under cursor" })
    map("n", "<leader>fk", fzf.keymaps,      { desc = "Search keymaps" })
    map("n", "<leader>fc", fzf.commands,     { desc = "Search commands" })
    map("n", "<leader>/",  fzf.lgrep_curbuf, { desc = "Search in current buffer" })
  end,
}
