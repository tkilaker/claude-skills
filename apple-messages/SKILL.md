---
name: apple-messages
description: Send and read iMessages. Triggers on "imessage", "send message", "text someone", "message to", "my messages", "unread messages", "recent messages".
---

# Apple Messages (iMessage) Integration

Send and read iMessages via `osascript` (AppleScript) and `sqlite3`.

## Prerequisites

- **Full Disk Access** for terminal (System Settings > Privacy & Security > Full Disk Access) — required for reading `~/Library/Messages/chat.db`
- No extra CLI tools — uses built-in `osascript` and `sqlite3`

## Operations

### Send iMessage

**Always confirm with the user before sending — this is irreversible.**

Base64-encode the message body to handle Swedish characters, special characters, and newlines:

```bash
RECIPIENT="0701234567"
MSG_B64=$(echo -n "MESSAGE_TEXT" | base64)
LC_ALL=sv_SE.UTF-8 osascript <<'APPLESCRIPT' "$RECIPIENT" "$MSG_B64"
on run argv
    set recipient to item 1 of argv
    set encodedMsg to item 2 of argv
    set decodingCmd to "echo " & quoted form of encodedMsg & " | base64 --decode"
    set messageText to do shell script decodingCmd
    tell application "Messages"
        set targetService to missing value
        try
            set targetService to 1st service whose service type = iMessage
        on error
            try
                set targetService to 1st service whose service type = SMS
            on error
                error "No messaging service available"
            end try
        end try
        set recipientBuddy to buddy recipient of targetService
        send messageText to recipientBuddy
    end tell
    return "Sent to " & recipient
end run
APPLESCRIPT
```

### Read recent messages from a contact

Query `chat.db` by phone number. The `text` column is preferred; `attributedBody` contains binary NSAttributedString data that's hard to decode — show `[Rich text]` as fallback.

```bash
PHONE="+467XXXXXXXX"
sqlite3 -json ~/Library/Messages/chat.db "
SELECT
    m.rowid,
    m.text,
    CASE WHEN m.is_from_me = 1 THEN 'me' ELSE 'them' END AS sender,
    datetime(m.date/1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime') AS timestamp
FROM message m
JOIN handle h ON m.handle_id = h.rowid
WHERE h.id LIKE '%' || replace('$PHONE', '+', '') || '%'
    OR h.id LIKE '%$PHONE%'
ORDER BY m.date DESC
LIMIT 20;
"
```

If `text` is null for a row, the message used rich text. Show `[Rich text - content not readable]`.

### Get unread messages

```bash
sqlite3 -json ~/Library/Messages/chat.db "
SELECT
    h.id AS sender,
    m.text,
    datetime(m.date/1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime') AS timestamp
FROM message m
JOIN handle h ON m.handle_id = h.rowid
WHERE m.is_read = 0
    AND m.is_from_me = 0
    AND m.item_type = 0
ORDER BY m.date DESC
LIMIT 50;
"
```

### List recent conversations

```bash
sqlite3 -json ~/Library/Messages/chat.db "
SELECT
    h.id AS contact,
    MAX(datetime(m.date/1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime')) AS last_message,
    COUNT(*) AS message_count
FROM message m
JOIN handle h ON m.handle_id = h.rowid
GROUP BY h.id
ORDER BY MAX(m.date) DESC
LIMIT 20;
"
```

### Search contacts by name

```bash
osascript -e '
tell application "Contacts"
    set matchedPeople to every person whose name contains "SEARCH_NAME"
    set output to ""
    repeat with p in matchedPeople
        set output to output & name of p & linefeed
        repeat with ph in phones of p
            set output to output & "  Phone: " & value of ph & linefeed
        end repeat
        repeat with em in emails of p
            set output to output & "  Email: " & value of em & linefeed
        end repeat
    end repeat
    return output
end tell
'
```

## Notes

- **Phone numbers**: Swedish format `0701234567` (no +46 prefix for buddy lookup). For international, use full `+XXXXXXXXXXX`.
- **Buddy must exist**: Recipient must have an existing conversation in Messages app.
- **Messages date epoch**: `date/1000000000 + strftime('%s', '2001-01-01')` converts to Unix time, then use `'unixepoch', 'localtime'`.
- **`attributedBody`**: Binary NSAttributedString — don't try to decode it. Use `text` column. If null, show `[Rich text - content not readable]`.
- **Swedish characters**: Set `LC_ALL=sv_SE.UTF-8` when sending.
- **Multiple recipients**: Send one at a time with 0.5s delay between sends.
