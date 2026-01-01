# Claude Skills

Skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Skills

### [apple-notes](./apple-notes/SKILL.md)

Read/write Apple Notes on macOS via JXA.

### [apple-reminders](./apple-reminders/SKILL.md)

CRUD Apple Reminders on macOS via JXA.

### [apple-calendar](./apple-calendar/SKILL.md)

CRUD Apple Calendar events on macOS via JXA.

### [apple-mail](./apple-mail/SKILL.md)

Read Apple Mail on macOS via JXA (read-only).

## Installation

Symlink skills to `~/.claude/skills/`:

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/claude-skills/apple-notes ~/.claude/skills/
ln -s /path/to/claude-skills/apple-reminders ~/.claude/skills/
ln -s /path/to/claude-skills/apple-calendar ~/.claude/skills/
ln -s /path/to/claude-skills/apple-mail ~/.claude/skills/
```

First run requires macOS automation permission approval.

## License

MIT
