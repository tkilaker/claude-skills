---
name: clipboard
description: Read/write system clipboard. Triggers on "copy", "clipboard", "paste", "give me", "put in clipboard".
---

# Clipboard

macOS clipboard via `pbcopy`/`pbpaste`. No dependencies.

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
