return {
  "nvim-treesitter/nvim-treesitter",
  branch = "master",
  build = ":TSUpdate",
  config = function()
    require("nvim-treesitter.configs").setup({
      ensure_installed = {
        "lua", "vim", "vimdoc",
        "javascript", "typescript", "tsx",
        "python", "bash", "json", "yaml",
        "html", "css", "markdown", "markdown_inline",
      },
      highlight = { enable = true },
      indent = { enable = true },
    })
  end,
}
