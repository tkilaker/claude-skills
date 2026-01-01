---
name: apple-calendar
description: Manage Apple Calendar events. Triggers on "my calendar", "schedule", "add event", "create event", "meeting", "appointment", "calendar event", "what's on my calendar", "free time".
---

# Apple Calendar Integration

Access Apple Calendar via JXA (JavaScript for Automation).

## Operations

### List all calendars

```bash
osascript -l JavaScript -e '
const app = Application("Calendar");
app.calendars().map(c => c.name());
'
```

### List events today

```bash
osascript -l JavaScript -e '
const app = Application("Calendar");
const start = new Date(); start.setHours(0,0,0,0);
const end = new Date(); end.setHours(23,59,59,999);
const cal = app.calendars.byName("CALENDAR_NAME");
cal.events.whose({
    _and: [
        {startDate: {_greaterThanEquals: start}},
        {startDate: {_lessThanEquals: end}}
    ]
})().map(e => ({
    summary: e.summary(),
    start: e.startDate(),
    end: e.endDate()
}));
'
```

### List events in date range

```bash
osascript -l JavaScript -e '
const app = Application("Calendar");
const start = new Date("2024-12-01");
const end = new Date("2024-12-31");
const cal = app.calendars.byName("CALENDAR_NAME");
cal.events.whose({
    _and: [
        {startDate: {_greaterThanEquals: start}},
        {endDate: {_lessThanEquals: end}}
    ]
})().map(e => e.summary());
'
```

### Search events by title

```bash
osascript -l JavaScript -e '
const app = Application("Calendar");
const cal = app.calendars.byName("CALENDAR_NAME");
cal.events.whose({summary: {_contains: "QUERY"}})().map(e => ({
    summary: e.summary(),
    start: e.startDate()
}));
'
```

### Create event

```bash
osascript -l JavaScript -e '
const app = Application("Calendar");
const cal = app.calendars.byName("CALENDAR_NAME");
const start = new Date("2024-12-15T14:00:00");
const end = new Date("2024-12-15T15:00:00");
const event = app.Event({
    summary: "TITLE",
    startDate: start,
    endDate: end,
    location: "LOCATION",
    description: "NOTES"
});
cal.events.push(event);
'
```

### Create all-day event

```bash
osascript -l JavaScript -e '
const app = Application("Calendar");
const cal = app.calendars.byName("CALENDAR_NAME");
const start = new Date("2024-12-25");
start.setHours(0,0,0,0);
const end = new Date("2024-12-25");
end.setHours(23,59,59,999);
const event = app.Event({
    summary: "TITLE",
    startDate: start,
    endDate: end,
    alldayEvent: true
});
cal.events.push(event);
'
```

### Update event

```bash
osascript -l JavaScript -e '
const app = Application("Calendar");
const cal = app.calendars.byName("CALENDAR_NAME");
const events = cal.events.whose({summary: "TITLE"})();
if (events.length > 0) {
    events[0].startDate = new Date("2024-12-16T14:00:00");
    events[0].endDate = new Date("2024-12-16T15:00:00");
}
'
```

### Delete event

```bash
osascript -l JavaScript -e '
const app = Application("Calendar");
const cal = app.calendars.byName("CALENDAR_NAME");
const events = cal.events.whose({summary: "TITLE"})();
if (events.length > 0) app.delete(events[0]);
'
```

### Reload calendars (sync)

```bash
osascript -l JavaScript -e '
Application("Calendar").reloadCalendars();
'
```

## Important Notes

- Calendar scripting can be slow (known OSA issue)
- Call `reloadCalendars()` to sync with server before queries
- `summary` is the event title (not `name`)
- `description` is the notes field
- `alldayEvent: true` for all-day events
- Date queries with `whose` can timeout on large calendars
- For recurring events, each occurrence is a separate event object
- Delete is permanent
- Use `{_contains: "..."}` for partial title matching
