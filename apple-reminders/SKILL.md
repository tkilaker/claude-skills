---
name: apple-reminders
description: Manage Apple Reminders. Triggers on "my reminders", "remind me", "add reminder", "create reminder", "reminder list", "todo", "due date", "mark complete", "check off".
---

# Apple Reminders

Access via `ekit` (`~/dev/ekit`, installed at `~/.local/bin/ekit`). JSON in, JSON out.

`reminders-cli` and other EventKit CLIs do **not** work when invoked from Claude
Code: the bundle declares no Reminders usage string, so TCC hard-denies with no
prompt. `ekit` falls back to its LaunchAgent, which holds the grant. See
`~/dev/ekit/README.md`.

## Reading

```bash
ekit lists                                    # reminder lists
ekit reminders                                # all incomplete, all lists
ekit reminders --list "Life Hub 🎯"
ekit reminders --overdue
ekit reminders --due-before "2026-09-15"      # due today or earlier, etc.
ekit reminders --search "faktura"             # matches title and notes
ekit reminders --completed                    # completed instead of incomplete
ekit reminders --all                          # both
ekit reminders --limit 20
```

Flags combine: `ekit reminders --list "Life Hub 🎯" --search färg --overdue`.

Dates in output are **local ISO8601 with offset** (`2026-09-13T09:00:00+02:00`).
No UTC conversion needed — filter with `--due-before`/`--overdue` rather than
post-processing.

Due today or overdue:

```bash
ekit reminders --due-before "$(date -v+1d +%Y-%m-%d)"
```

## Writing

```bash
ekit add --list "Life Hub 🎯" --title "Ring tandläkaren" --due "2026-09-15 09:00" --notes "..."
ekit edit   <id> --title "..." --due "..." --notes "..." --list "..." [--clear-due]
ekit complete <id>
ekit uncomplete <id>
ekit delete <id>
```

`<id>` is the `id` field from any read. It is stable — never use list positions.
Adding a `--due` also sets an alarm at that time.

Dates accept ISO8601, `"YYYY-MM-DD HH:mm"`, or `"YYYY-MM-DD"`.

## Where items go

**"Life Hub 🎯"** is the single bin, for personal and work alike. There is no
"Work 🏢" list on mini — verified 2026-09-12, `ekit lists` returns 10 lists and
none is Work. Do not create one.

Work items take a context prefix in the title, matching existing entries:
`"HMS: …"`, `"Living IT: …"`.

The Work Smart List filters on the `#work` tag, which **cannot be set from any
scripting API**. An item written here will not appear in that list until Tim tags
it in the app. Say so plainly rather than implying the tag was applied.

Full rules: `~/dev/brain/projects/personal-assistant/README.md`.

## Tags are not scriptable

Verified 2026-09-12 against both APIs:

- EventKit: no tag property on `EKReminder` or `EKCalendarItem`
- AppleScript: a reminder's full property list is `completed, flagged, container,
  modification date, completion date, remind me date, body, priority, id,
  allday due date, name, creation date, due date`

No tool can work around this. Tim maintains tag-based Smart Lists manually in the
app; see "Where items go" above for what to do instead.

## When something fails

Run `ekit status` first. It reports authorization per domain and never prompts:

```json
{ "calendar": "writeOnly", "reminders": "authorized", "responsibleHint": "direct" }
```

Report that output verbatim. Do not switch to AppleScript or Computer Use as a
workaround — JXA reads of Reminders take 88-150s on this data set and will look
like a hang.

## Notes

- Delete is permanent, no trash.
- To delete a completed reminder, `uncomplete` first.
- `--priority` takes an integer (0 = none).
