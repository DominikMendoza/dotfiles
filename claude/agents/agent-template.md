---
name: agent-template
description: Starting point for writing a personal subagent. Use when the user asks how to create a Claude Code agent, or asks to scaffold a new one.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a template subagent. Replace this body with the agent's actual system
prompt: its role, the steps it should take, and the exact shape of the result it
must return.

# Creating a new one

1. Copy this file inside the dotfiles repo:
   `cp claude/agents/agent-template.md claude/agents/<new-name>.md`
2. Edit the frontmatter. `name` must match the filename (without `.md`).
   - `description` — when the main agent should delegate to this one.
   - `tools` — omit the key entirely to inherit every tool; list them to narrow.
   - `model` — `haiku`, `sonnet`, `opus`, or omit to inherit the session's.
3. Add a `link agents/<new-name>.md agents/<new-name>.md` line in
   `claude/install.sh`.
4. Run `./claude/install.sh` and restart Claude Code.

# Notes

A subagent runs in its own context and returns only its final report, so state
explicitly what it must hand back — the main agent never sees its intermediate
work.
