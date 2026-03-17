#!/bin/bash
# Test script for Apple Messages skill (read-only — never sends real messages)

echo "=== Apple Messages Skill Test ==="

# 1. Check Messages app responds
echo "1. Checking Messages app..."
NAME=$(osascript -e 'tell application "Messages" to get name' 2>&1)
if [ "$NAME" = "Messages" ]; then
    echo "   PASS: Messages app responds"
else
    echo "   FAIL: Messages app not responding: $NAME"
    exit 1
fi

# 2. Check iMessage service exists
echo "2. Checking iMessage service..."
SVC=$(osascript -e 'tell application "Messages" to get service type of 1st service whose service type = iMessage' 2>&1)
if echo "$SVC" | grep -qi "imessage"; then
    echo "   PASS: iMessage service found"
else
    echo "   WARN: iMessage service not found (SMS may still work): $SVC"
fi

# 3. Check SQLite access to chat.db
echo "3. Checking chat.db access..."
if [ -f "$HOME/Library/Messages/chat.db" ]; then
    COUNT=$(sqlite3 "$HOME/Library/Messages/chat.db" "SELECT count(*) FROM message;" 2>&1)
    if [[ "$COUNT" =~ ^[0-9]+$ ]]; then
        echo "   PASS: chat.db accessible ($COUNT messages)"
    else
        echo "   WARN: chat.db exists but query failed (Full Disk Access needed?): $COUNT"
    fi
else
    echo "   WARN: chat.db not found at ~/Library/Messages/chat.db"
fi

# 4. Query recent message count (last 24h)
echo "4. Checking recent messages..."
RECENT=$(sqlite3 "$HOME/Library/Messages/chat.db" "
SELECT count(*) FROM message
WHERE date/1000000000 + strftime('%s', '2001-01-01') > strftime('%s', 'now', '-1 day');
" 2>&1)
if [[ "$RECENT" =~ ^[0-9]+$ ]]; then
    echo "   PASS: $RECENT messages in last 24h"
else
    echo "   SKIP: Could not query recent messages: $RECENT"
fi

# 5. Test contact search
echo "5. Checking Contacts app..."
CONTACT_TEST=$(osascript -e 'tell application "Contacts" to get name of first person' 2>&1)
if [ -n "$CONTACT_TEST" ] && ! echo "$CONTACT_TEST" | grep -qi "error"; then
    echo "   PASS: Contacts accessible (first contact: $CONTACT_TEST)"
else
    echo "   WARN: Could not read contacts: $CONTACT_TEST"
fi

echo "=== Done ==="
