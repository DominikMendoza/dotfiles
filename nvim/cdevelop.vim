" C# development
" Supprot for different goto definitions for different file types.
autocmd FileType cs nmap <silent> gd :OmniSharpGotoDefinition<CR>
autocmd FileType cs nnoremap <buffer> <Leader>fu :OmniSharpFindUsages<CR>
autocmd FileType cs nnoremap <buffer> <Leader>fi :OmniSharpFindImplementations<CR>
autocmd FileType cs nnoremap <Leader><Space> :OmniSharpGetCodeActions<CR>
" Ejeruction C#
autocmd FileType cs nnoremap <Leader>g+ :FloatermNew --autoclose=0 dotnet build && echo -e "\n" && dotnet run<CR>
autocmd FileType cs nmap <Leader>at :FloatermNew dotnet run<CR>
" ts and html
autocmd FileType ts nmap <silent> gd :call CocActionAsync('jumpDefinition')<CR>
autocmd FileType html nmap <silent> gd :call CocActionAsync('jumpDefinition')<CR>
" Setting for c++
nmap <Leader>t :FloatermNew <CR>
"autocmd FileType cpp nmap <Leader>g+ :!g++ % && ./a.out<CR>
autocmd FileType cpp nmap <Leader>g+ :FloatermNew --autoclose=0 g++ % && ./a.out <CR>
autocmd FileType cpp nmap <Leader>at :FloatermNew ./a.out <CR>
autocmd FileType cpp nmap <Leader>art :FloatermNew --autoclose=0 g++ % && ./a.out --success <CR>
"The following commands are contextual, based on the cursor position.
" autocmd FileType cs nnoremap <buffer>
" autocmd FileType cs nnoremap <buffer> <Leader>fs :OmniSharpFindSymbol<CR>
let g:vimspector_enable_mappings = 'HUMAN'
"let g:tmuxline_powerline_separators = 0
"set directory^=$HOME/tempswap//

" This directory should exist.
" Always enable preview window on the right with 60% width
"let g:fzf_preview_window = 'right:60%'

" vim wiki settings.
let g:ale_linters_ignore = {
      \   'typescript': ['tslint'],
      \}

let g:ale_linters = {
\ 'cs': ['OmniSharp']
\}
