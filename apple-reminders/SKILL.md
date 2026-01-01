---
name: apple-reminders
description: Manage Apple Reminders. Triggers on "my reminders", "remind me", "add reminder", "create reminder", "reminder list", "todo", "due date", "mark complete", "check off".
---

# Apple Reminders Integration

Fast CLI access via [reminders-cli](https://github.com/keith/reminders-cli).

## Prerequisites

```bash
brew install keith/formulae/reminders-cli
```

## Operations

### List all reminder lists

```bash
reminders show-lists
```

### Show reminders in a list

```bash
reminders show "LIST_NAME" --format json
```

### Show all reminders

```bash
reminders show-all --format json
```

### Show overdue reminders

```bash
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
reminders show-all --format json | jq --arg now "$NOW" '[.[] | select(.dueDate) | select(.dueDate < $now)]'
```

### Search reminders by name

```bash
reminders show-all --format json | jq '[.[] | select(.title | test("QUERY"; "i"))]'
```

### Add reminder (basic)

```bash
reminders add "LIST_NAME" "TITLE"
```

### Add reminder with due date and notes

```bash
reminders add "LIST_NAME" "TITLE" --due-date "tomorrow 9am" --notes "NOTES" --format json
```

### Complete reminder

```bash
reminders complete "LIST_NAME" INDEX
```

### Delete reminder

```bash
reminders delete "LIST_NAME" INDEX
```

### Edit reminder title

```bash
reminders edit "LIST_NAME" INDEX "NEW_TITLE"
```

## Notes

- INDEX is 0-based, shown in `reminders show` output
- `--due-date` accepts natural language: "tomorrow", "next monday 3pm", "2025-06-15"
- `--priority` values: none (default), low, medium, high
- JSON output includes: externalId, isCompleted, list, priority, title, dueDate, startDate
- dueDate only present if reminder has due date set
- Delete is permanent (no trash)
- To delete completed reminders: `uncomplete` first, then `delete`
