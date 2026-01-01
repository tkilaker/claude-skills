---
name: apple-mail
description: Read Apple Mail (read-only). Triggers on "my email", "my mail", "inbox", "unread emails", "check email", "email from", "recent emails", "mail search".
---

# Apple Mail Integration (Read-Only)

Access Apple Mail via JXA (JavaScript for Automation). Read-only operations.

## Operations

### List mail accounts

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
app.accounts().map(a => a.name());
'
```

### List mailboxes for account

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
app.accounts.byName("ACCOUNT_NAME").mailboxes().map(m => m.name());
'
```

### Get unread count (inbox)

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
app.inbox.unreadCount();
'
```

### Get unread count (all accounts)

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
app.accounts().reduce((sum, a) => {
    const inbox = a.mailboxes.byName("INBOX");
    try { return sum + inbox.unreadCount(); } catch(e) { return sum; }
}, 0);
'
```

### List recent emails (inbox, last 10)

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
const msgs = app.inbox.messages().slice(0, 10);
msgs.map(m => ({
    subject: m.subject(),
    sender: m.sender(),
    date: m.dateReceived(),
    read: m.readStatus()
}));
'
```

### List unread emails

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
app.inbox.messages.whose({readStatus: false})().slice(0, 20).map(m => ({
    subject: m.subject(),
    sender: m.sender(),
    date: m.dateReceived()
}));
'
```

### Read email content

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
const msgs = app.inbox.messages.whose({subject: {_contains: "SUBJECT"}})();
if (msgs.length > 0) {
    const m = msgs[0];
    ({
        subject: m.subject(),
        sender: m.sender(),
        date: m.dateReceived(),
        content: m.content()
    });
}
'
```

### Search emails by sender

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
app.inbox.messages.whose({sender: {_contains: "SENDER"}})().slice(0, 10).map(m => ({
    subject: m.subject(),
    date: m.dateReceived()
}));
'
```

### Search emails by subject

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
app.inbox.messages.whose({subject: {_contains: "QUERY"}})().slice(0, 10).map(m => ({
    subject: m.subject(),
    sender: m.sender()
}));
'
```

### Get email headers

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
const msgs = app.inbox.messages.whose({subject: {_contains: "SUBJECT"}})();
if (msgs.length > 0) msgs[0].allHeaders();
'
```

### List emails from specific account

```bash
osascript -l JavaScript -e '
const app = Application("Mail");
const inbox = app.accounts.byName("ACCOUNT_NAME").mailboxes.byName("INBOX");
inbox.messages().slice(0, 10).map(m => ({
    subject: m.subject(),
    sender: m.sender()
}));
'
```

## Important Notes

- **Read-only**: This skill does not send, delete, or modify emails
- `app.inbox` is the unified inbox across all accounts
- `content()` returns plain text; `source()` returns raw RFC822
- `readStatus` is boolean (true = read, false = unread)
- `dateReceived` for received time, `dateSent` for sent time
- Messages are ordered newest first by default
- Large mailboxes: use `.slice(0, N)` to limit results
- `whose` queries can be slow on large mailboxes
- Accessing `content()` on many messages is slow
- Use `{_contains: "..."}` for partial matching
