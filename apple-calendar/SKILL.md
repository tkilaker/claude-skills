---
name: apple-calendar
description: Manage Apple Calendar events. Triggers on "my calendar", "schedule", "add event", "create event", "meeting", "appointment", "calendar event", "what's on my calendar", "free time".
---

# Apple Calendar Integration

Hybrid approach: `icalbuddy` for fast reads, JXA for writes.

## Read Operations (icalbuddy)

### List events today

```bash
icalbuddy eventsToday
```

### List events tomorrow

```bash
icalbuddy eventsToday+1
```

### List events for specific date

```bash
icalbuddy eventsFrom:"2026-01-15" to:"2026-01-15"
```

### List events for date range

```bash
icalbuddy eventsFrom:"2026-01-01" to:"2026-01-31"
```

### List events from specific calendar

```bash
icalbuddy -ic "Work" eventsToday
```

### Search events by title

```bash
icalbuddy eventsToday+30 | grep -i "QUERY"
```

### List upcoming events (next 7 days)

```bash
icalbuddy eventsToday+7
```

### List all calendars

```bash
icalbuddy calendars
```

## Write Operations (JXA)

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

- **Reads**: Use `icalbuddy` - reads calendar DB directly, fast
- **Writes**: Use JXA - slower but necessary for create/update/delete
- `icalbuddy` requires: `brew install ical-buddy`
- Use `-ic "Name"` to include specific calendar, `-ec "Name"` to exclude
- JXA `whose` queries are slow on large calendars (avoid for reads)
- Delete is permanent
