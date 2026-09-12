---
name: apple-calendar
description: Manage Apple Calendar events. Triggers on "my calendar", "schedule", "add event", "create event", "meeting", "appointment", "calendar event", "what's on my calendar", "free time".
---

# Apple Calendar

Access via `ekit` (`~/dev/ekit`, installed at `~/.local/bin/ekit`). JSON in, JSON out.

`icalbuddy` and other EventKit CLIs do **not** work when invoked from Claude
Code: the bundle declares no Calendars usage string, so TCC hard-denies with no
prompt and `icalbuddy` reports "No calendars" or nothing at all. `ekit` falls back
to its LaunchAgent, which holds the grant. See `~/dev/ekit/README.md`.

Event routing per account is in `~/dev/brain/projects/calendar/README.md`. Read it
before creating anything. Busy-time mirroring is owned by `calsync` — never copy
events between calendars by hand.

## Reading

```bash
ekit calendars                                              # all calendars
ekit events                                                 # today
ekit events --from 2026-09-15 --to 2026-09-22               # range
ekit events --from 2026-09-15 --to 2026-09-17 --cal Personlig
ekit events --from 2026-09-15 --to 2026-10-15 --search rep  # title, notes, location
ekit events --limit 20
```

`--to` defaults to one day after `--from`. Recurring events are expanded within
the range, and each carries `"recurring": true`.

Next 48 hours:

```bash
ekit events --from "$(date +%Y-%m-%d)" --to "$(date -v+2d +%Y-%m-%d)"
```

Output times are local ISO8601 with offset (`2026-09-12T10:00:00+02:00`).

## Writing

```bash
ekit event-add --cal Personlig --title "Möte" \
  --start "2026-09-15 14:00" --end "2026-09-15 15:00" \
  --location "Malmö" --notes "..."

ekit event-add --cal Personlig --title "Semester" --start 2026-09-20 --allday

ekit event-edit <id> --title "..." --start "..." --end "..." --location "..." --notes "..."
ekit event-delete <id>
```

`<id>` is the `id` field from any read. `--end` defaults to one hour after
`--start`. Delete is permanent.

**Language:** check existing entries in the target calendar first and write new
events in the same language Tim uses there.

## When something fails

Run `ekit status` first. It reports authorization per domain and never prompts:

```json
{ "calendar": "writeOnly", "reminders": "authorized", "responsibleHint": "direct" }
```

`"calendar": "writeOnly"` on the direct path is expected — reads route through the
agent. Report the output verbatim rather than switching mechanism. Do not fall
back to JXA: a date-range `whose` query across these calendars exceeds 110s and
will look like a hang.

Force a sync from the calendar servers:

```bash
osascript -l JavaScript -e 'Application("Calendar").reloadCalendars()'
```
