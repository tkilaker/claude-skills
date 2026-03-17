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

### Show reminders due today

**Important:** `dueDate` is stored in UTC. Tim is in Europe/Stockholm (CET/CEST). A reminder due "Feb 26" locally is stored as `2026-02-25T23:00:00Z` in winter (UTC+1) or `2026-02-25T22:00:00Z` in summer (UTC+2). Always convert local day boundaries to UTC when filtering by date.

```bash
# python3 reliably converts local day boundaries to UTC (macOS date -j is unreliable for this)
TODAY_START=$(python3 -c "from datetime import datetime,timezone,timedelta;import zoneinfo;tz=zoneinfo.ZoneInfo('Europe/Stockholm');n=datetime.now(tz);print(n.replace(hour=0,minute=0,second=0,microsecond=0).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))")
TODAY_END=$(python3 -c "from datetime import datetime,timezone,timedelta;import zoneinfo;tz=zoneinfo.ZoneInfo('Europe/Stockholm');n=datetime.now(tz);print((n+timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))")
reminders show-all --format json | jq --arg start "$TODAY_START" --arg end "$TODAY_END" \
  '[.[] | select(.dueDate) | select(.dueDate >= $start and .dueDate < $end)]'
```

### Show overdue reminders

```bash
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
reminders show-all --format json | jq --arg now "$NOW" '[.[] | select(.dueDate) | select(.dueDate < $now)]'
```

### Show reminders due today or overdue

```bash
TODAY_END=$(python3 -c "from datetime import datetime,timezone,timedelta;import zoneinfo;tz=zoneinfo.ZoneInfo('Europe/Stockholm');n=datetime.now(tz);print((n+timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))")
reminders show-all --format json | jq --arg end "$TODAY_END" \
  '[.[] | select(.dueDate) | select(.dueDate < $end)]'
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

## Default lists

- **"Life Hub 🎯"** — default for personal reminders
- **"Work 🏢"** — use for all work-related reminders (replaces `#work` tag, see Limitations)

## Tags Limitation

Apple Reminders tags (`#work`, etc.) are **NOT accessible** via any scripting API:
- JXA: no `tags` property on Reminder objects
- EventKit: no tags API exposed
- reminders-cli: no tag support

**Workaround:** Use the **"Work 🏢"** list for work-related items instead of tagging. Tim manages Smart Lists by tag manually in the Reminders app.

## Notes

- **Timezone:** `dueDate` is UTC. Tim is in `Europe/Stockholm`. Always convert local dates to UTC for filtering.
- INDEX is 0-based, shown in `reminders show` output
- `--due-date` accepts natural language: "tomorrow", "next monday 3pm", "2025-06-15"
- `--priority` values: none (default), low, medium, high
- JSON output includes: externalId, isCompleted, list, priority, title, dueDate, startDate
- dueDate only present if reminder has due date set
- Delete is permanent (no trash)
- To delete completed reminders: `uncomplete` first, then `delete`
