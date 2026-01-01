---
name: apple-reminders
description: Manage Apple Reminders. Triggers on "my reminders", "remind me", "add reminder", "create reminder", "reminder list", "todo", "due date", "mark complete", "check off".
---

# Apple Reminders Integration

Access Apple Reminders via JXA (JavaScript for Automation).

## Operations

### List all reminder lists

```bash
osascript -l JavaScript -e '
const app = Application("Reminders");
app.lists().map(l => l.name());
'
```

### List reminders in a list

```bash
osascript -l JavaScript -e '
const app = Application("Reminders");
app.lists.byName("LIST_NAME").reminders().map(r => ({
    name: r.name(),
    dueDate: r.dueDate(),
    completed: r.completed()
}));
'
```

### List incomplete reminders

```bash
osascript -l JavaScript -e '
const app = Application("Reminders");
app.lists.byName("LIST_NAME").reminders.whose({completed: false})().map(r => r.name());
'
```

### Search reminders by name

```bash
osascript -l JavaScript -e '
const app = Application("Reminders");
app.reminders.whose({name: {_contains: "QUERY"}})().map(r => ({
    name: r.name(),
    list: r.container().name()
}));
'
```

### Create reminder (basic)

```bash
osascript -l JavaScript -e '
const app = Application("Reminders");
const r = app.Reminder({name: "TITLE", body: "NOTES"});
app.defaultList.reminders.push(r);
'
```

### Create reminder with due date

```bash
osascript -l JavaScript -e '
const app = Application("Reminders");
const dueDate = new Date("2024-12-31T10:00:00");
const r = app.Reminder({name: "TITLE", body: "NOTES", dueDate: dueDate});
app.lists.byName("LIST_NAME").reminders.push(r);
'
```

### Create reminder with remind date

```bash
osascript -l JavaScript -e '
const app = Application("Reminders");
const remindDate = new Date("2024-12-31T09:00:00");
const r = app.Reminder({name: "TITLE", remindMeDate: remindDate});
app.defaultList.reminders.push(r);
'
```

### Mark reminder complete

```bash
osascript -l JavaScript -e '
const app = Application("Reminders");
const r = app.reminders.whose({name: "TITLE"})()[0];
if (r) r.completed = true;
'
```

### Update reminder due date

```bash
osascript -l JavaScript -e '
const app = Application("Reminders");
const r = app.reminders.whose({name: "TITLE"})()[0];
if (r) r.dueDate = new Date("2024-12-31T15:00:00");
'
```

### Delete reminder

```bash
osascript -l JavaScript -e '
const app = Application("Reminders");
const r = app.reminders.whose({name: "TITLE"})()[0];
if (r) app.delete(r);
'
```

## Important Notes

- `dueDate` sets when the reminder is due
- `remindMeDate` sets when the alert fires (can differ from dueDate)
- `app.defaultList` is user's default list
- `app.reminders` searches ALL lists
- `priority` is integer: 0 = none, 1 = high, 5 = medium, 9 = low
- Delete is permanent (no trash like Notes)
- Use `{_contains: "..."}` for partial name matching
