---
name: clipboard
description: Read/write system clipboard. Use PROACTIVELY — whenever generating content the user will paste elsewhere (SQL queries, messages, text snippets, emails, code blocks, URLs, commands), copy it to clipboard automatically. Also triggers on "copy", "clipboard", "paste", "give me", "put in clipboard".
---

# Clipboard

macOS clipboard via `pbcopy`/`pbpaste`. No dependencies.

## Proactive behavior

**Auto-copy to clipboard** whenever you produce output the user will likely paste somewhere else. Don't wait to be asked. Examples:

- SQL queries (for a DB client)
- Email drafts or message text (for mail/Slack/Teams)
- Code snippets the user asked to be generated for use elsewhere
- Shell commands meant to be run in another terminal
- URLs, connection strings, config values
- Any text the user explicitly or implicitly needs to transfer

When it's obvious the output is "for pasting", just copy it. Mention briefly that it's in the clipboard.

## Multiple items

Tim uses Raycast's clipboard manager. Copying multiple times is fine — each item stays in history. When producing several distinct pasteable items (e.g. multiple SQL queries, a subject + body for an email), copy them **one at a time in sequence** so each lands as a separate clipboard entry. Copy in the order the user will paste them.

## Write to clipboard

```bash
echo -n "TEXT" | pbcopy
```

Or multiline:

```bash
pbcopy << 'EOF'
CONTENT
EOF
```

## Read from clipboard

```bash
pbpaste
```

## Notes

- Use `echo -n` to avoid trailing newline
- Heredoc with `'EOF'` (quoted) prevents variable expansion
- Clipboard persists until overwritten or system restart
- When auto-copying, keep the conversational response short — the clipboard is the deliverable
