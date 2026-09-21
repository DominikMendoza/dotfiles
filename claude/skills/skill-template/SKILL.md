---
name: skill-template
description: Starting point for writing a personal skill. Use when the user asks how to create a Claude Code skill, or asks to scaffold a new one.
---

# Skill template

A skill is a folder under `~/.claude/skills/<name>/` containing a `SKILL.md`.
Claude reads the frontmatter `description` to decide when to load it, then
follows the body as instructions.

## Creating a new one

1. Copy this folder inside the dotfiles repo:
   `cp -r claude/skills/skill-template claude/skills/<new-name>`
2. Edit the frontmatter: `name` must match the folder name.
3. Write the `description` for *triggering* — say when it applies, not what it
   is. This is the only part Claude sees before deciding to load the skill.
4. Add a `link skills/<new-name> skills/<new-name>` line in `claude/install.sh`.
5. Run `./claude/install.sh` and restart Claude Code. It shows up as
   `/<new-name>`.

## Writing the body

Everything below the frontmatter is the instruction set. Keep it imperative and
concrete: the steps to take, the commands to run, the format to return. Extra
files in the folder (scripts, references) can be called from here by path.
