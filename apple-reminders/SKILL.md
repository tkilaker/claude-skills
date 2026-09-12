---
name: apple-reminders
description: Manage Apple Reminders. Triggers on "my reminders", "remind me", "add reminder", "create reminder", "reminder list", "todo", "due date", "mark complete", "check off".
---

# Apple Reminders

Access via `pim` (`~/dev/pim`, installed at `~/.local/bin/pim`). JSON in, JSON out.

`reminders-cli` and other EventKit CLIs do **not** work when invoked from Claude
Code: the bundle declares no Reminders usage string, so TCC hard-denies with no
prompt. `pim` falls back to its LaunchAgent, which holds the grant. See
`~/dev/pim/README.md`.

## Reading

```bash
pim lists                                    # reminder lists
pim reminders                                # all incomplete, all lists
pim reminders --list "Life Hub 🎯"
pim reminders --overdue
pim reminders --due-before "2026-09-15"      # due today or earlier, etc.
pim reminders --search "faktura"             # matches title and notes
pim reminders --completed                    # completed instead of incomplete
pim reminders --all                          # both
pim reminders --limit 20
```

Flags combine: `pim reminders --list "Life Hub 🎯" --search färg --overdue`.

Dates in output are **local ISO8601 with offset** (`2026-09-13T09:00:00+02:00`).
No UTC conversion needed — filter with `--due-before`/`--overdue` rather than
post-processing.

Due today or overdue:

```bash
pim reminders --due-before "$(date -v+1d +%Y-%m-%d)"
```

## Writing

```bash
pim add --list "Life Hub 🎯" --title "Ring tandläkaren" --due "2026-09-15 09:00" --notes "..."
pim edit   <id> --title "..." --due "..." --notes "..." --list "..." [--clear-due]
pim complete <id>
pim uncomplete <id>
pim delete <id>
```

`<id>` is the `id` field from any read. It is stable — never use list positions.
Adding a `--due` also sets an alarm at that time.

Dates accept ISO8601, `"YYYY-MM-DD HH:mm"`, or `"YYYY-MM-DD"`.

## Where items go

**"Life Hub 🎯"** is the single bin, for personal and work alike. There is no
"Work 🏢" list on mini — verified 2026-09-12, `pim lists` returns 10 lists and
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

Run `pim status` first. It reports authorization per domain and never prompts:

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
