# dotfiles
```bash
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

## Git

### `bb`

Alias que carga la llave ssh de Bitbucket en el agente de la sesion actual.

```bash
alias bb='eval "$(ssh-agent -s)" && ssh-add ~/.ssh/bitbucket'
```

Hace falta antes de cualquier git que toque la red contra Bitbucket. El agente
vive mientras viva el shell, asi que en una terminal basta correrlo una vez,
pero en scripts o herramientas que abren un shell por comando hay que
encadenarlo: `bb && git fetch origin staging`.

### Convenciones de ramas

Las reglas de nombre, rama base y creacion de worktrees viven en
`claude/CLAUDE.md`, porque las consume Claude Code en cada sesion.
