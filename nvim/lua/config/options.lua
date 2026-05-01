local opt = vim.opt

-- Line numbers
opt.number = true
opt.relativenumber = true

-- Indentation
opt.expandtab = true
opt.shiftwidth = 2
opt.tabstop = 2
opt.smartindent = true

-- Search
opt.ignorecase = true
opt.smartcase = true
opt.hlsearch = true
opt.incsearch = true

-- Appearance
opt.termguicolors = true
opt.signcolumn = "yes"
opt.cursorline = true
opt.scrolloff = 8
opt.wrap = false

-- Behavior
opt.mouse = "a"
opt.clipboard = "unnamedplus"  -- Share with system clipboard
opt.undofile = true            -- Persistent undo history
opt.swapfile = false
opt.backup = false
opt.updatetime = 250

-- More natural splits
opt.splitright = true
opt.splitbelow = true

-- Leader
vim.g.mapleader = " "
vim.g.maplocalleader = " "
