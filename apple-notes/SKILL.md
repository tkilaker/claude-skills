---
name: apple-notes
description: Read and write Apple Notes. Triggers on "my notes", "save to notes", "check notes", "create note", "find note", "note about", "add to notes", "in my notes".
---

# Apple Notes Integration

Access Apple Notes via JXA (JavaScript for Automation).

## Operations

### List all note titles (excluding trash)

```bash
osascript -l JavaScript -e '
const app = Application("Notes");
const folder = app.folders.whose({name: "Notes"})()[0];
folder.notes.name();
'
```

### Search notes by title

```bash
osascript -l JavaScript -e '
const app = Application("Notes");
const folder = app.folders.whose({name: "Notes"})()[0];
folder.notes.whose({name: {_contains: "QUERY"}})().map(n => n.name());
'
```

### Read note content

```bash
osascript -l JavaScript -e '
const app = Application("Notes");
const notes = app.notes.whose({name: "TITLE"})();
notes.length > 0 ? notes[0].body() : "Not found";
'
```

### Create note

Do NOT include the title in body - Apple Notes auto-adds it as the first `<div>`.

```bash
osascript -l JavaScript -e '
const app = Application("Notes");
app.make({new: "note", withProperties: {name: "TITLE", body: "<div>CONTENT</div>"}});
'
```

Wrong (causes duplication): `body: "<div>TITLE</div><div>CONTENT</div>"`

### Update note

Note: Must include title as first div in body.

```bash
osascript -l JavaScript -e '
const app = Application("Notes");
const notes = app.notes.whose({name: "TITLE"})();
if (notes.length > 0) {
    notes[0].body = "<div>TITLE</div><div>NEW CONTENT</div>";
}
'
```

### Delete note

Moves to Recently Deleted folder (Apple Notes doesn't permanent delete via API).

```bash
osascript -l JavaScript -e '
const app = Application("Notes");
const notes = app.notes.whose({name: "TITLE"})();
if (notes.length > 0) { app.delete(notes[0]); }
'
```

## Important Notes

- Content is HTML (Apple Notes native format)
- Apple Notes auto-adds `name` as first `<div>` in body on create
- When creating: do NOT include title in body (causes duplication)
- When updating: MUST include title as first `<div>` (it's already there)
- Use `{_contains: "..."}` for partial title matching
- `app.notes` searches ALL folders including Recently Deleted
- Delete moves to trash, doesn't permanently delete
- To exclude trash: search in specific folder (see List example)
