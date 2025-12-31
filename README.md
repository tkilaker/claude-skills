# Claude Skills

A collection of skills and extensions for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - Anthropic's official CLI for Claude AI.

## About

This repository provides reusable **skills** that extend Claude Code's capabilities with specialized functionality. Skills are triggered by natural language patterns and provide Claude with domain-specific knowledge and tool access.

## Available Skills

### Apple Notes Integration

Full read/write access to Apple Notes on macOS via JXA (JavaScript for Automation).

**Features:**
- List all notes
- Search notes by title
- Read note content
- Create new notes
- Update existing notes
- Delete notes (moves to Recently Deleted)

**Triggers:** "my notes", "save to notes", "check notes", "create note", "find note", "note about", "add to notes", "in my notes"

[View documentation →](./apple-notes/SKILL.md)

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Anthropic's CLI for Claude)
- macOS (for Apple Notes skill)

## Installation

Skills from this repository can be used with Claude Code on the web or CLI. Follow the [Claude Code skills documentation](https://docs.anthropic.com/en/docs/claude-code) for setup instructions.

## Contributing

Contributions are welcome! To add a new skill:

1. Create a new directory with your skill name
2. Add a `SKILL.md` file with frontmatter (name, description, triggers)
3. Include documentation and usage examples
4. Submit a pull request

## Keywords

`claude` `anthropic` `claude-code` `ai-assistant` `skills` `extensions` `plugins` `macos` `apple-notes` `jxa` `javascript-automation` `automation` `productivity` `ai-tools` `llm` `large-language-model`

## License

MIT

---

*Built for the Claude Code ecosystem by the community.*
