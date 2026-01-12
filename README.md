# Claude Skills

Skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Skills

### Apple Ecosystem

#### [apple-notes](./apple-notes/SKILL.md)

Read/write Apple Notes. Uses `macnotesapp` CLI for fast content search, JXA for CRUD.

#### [apple-reminders](./apple-reminders/SKILL.md)

CRUD Apple Reminders. Uses `reminders-cli` for fast performance.

#### [apple-calendar](./apple-calendar/SKILL.md)

CRUD Apple Calendar events. Uses `icalbuddy` CLI for fast reads, JXA for writes.

#### [apple-mail](./apple-mail/SKILL.md)

Read Apple Mail via JXA (read-only).

### Utilities

#### [clipboard](./clipboard/SKILL.md)

Read/write system clipboard via `pbcopy`/`pbpaste`. No dependencies.

### Code Review

#### [commit-review](./commit-review/SKILL.md)

Multi-agent code review for commits. Runs 5 parallel Sonnet agents (CLAUDE.md compliance, bugs, git history, previous feedback, code comments), scores issues, filters false positives. Works on single commits or ranges.

### External Services

#### [azure-devops](./azure-devops/SKILL.md)

Fetch Azure DevOps work items by ID. Requires config with PAT at `~/.config/azure-devops/config.json`.

## Installation

Symlink skills to `~/.claude/skills/`:

```bash
mkdir -p ~/.claude/skills
for skill in apple-notes apple-reminders apple-calendar apple-mail clipboard azure-devops commit-review; do
  ln -s /path/to/claude-skills/$skill ~/.claude/skills/
done
```

### Prerequisites

Some skills require CLI tools:

| Skill | Dependency | Install |
|-------|------------|---------|
| apple-notes | macnotesapp | `pipx install macnotesapp` |
| apple-reminders | reminders-cli | `brew install keith/formulae/reminders-cli` |
| apple-calendar | icalbuddy | `brew install ical-buddy` |
| azure-devops | jq | `brew install jq` |

First run of Apple skills requires macOS automation permission approval.

## Private Config

Skills that need credentials store them outside the repo:

- **azure-devops**: `~/.config/azure-devops/config.json` (chmod 600)

## License

MIT
