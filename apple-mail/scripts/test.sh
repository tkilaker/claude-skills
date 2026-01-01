#!/bin/bash
# Test script for Apple Mail skill (read-only)

echo "=== Apple Mail Skill Test (Read-Only) ==="

# List accounts
echo "1. Listing accounts..."
ACCOUNTS=$(osascript -l JavaScript -e 'const app = Application("Mail"); app.accounts().map(a => a.name()).join(", ")' 2>/dev/null)
if [ -n "$ACCOUNTS" ]; then
    echo "   PASS: Accounts: $ACCOUNTS"
else
    echo "   WARN: No accounts or Mail not configured"
fi

# Unread count
echo "2. Getting unread count..."
UNREAD=$(osascript -l JavaScript -e 'const app = Application("Mail"); app.inbox.unreadCount()' 2>/dev/null)
if [ -n "$UNREAD" ]; then
    echo "   PASS: Unread: $UNREAD"
else
    echo "   WARN: Could not get unread count"
fi

# Recent emails
echo "3. Listing recent emails (up to 3)..."
EMAILS=$(osascript -l JavaScript -e '
const app = Application("Mail");
const msgs = app.inbox.messages().slice(0, 3);
msgs.map(m => "  - " + m.subject().substring(0, 50)).join("\n");
' 2>/dev/null)
if [ -n "$EMAILS" ]; then
    echo "   PASS: Recent emails found"
    echo "$EMAILS"
else
    echo "   WARN: No emails or inbox empty"
fi

# Search capability check
echo "4. Search capability check..."
SEARCH_RESULT=$(osascript -l JavaScript -e '
const app = Application("Mail");
try {
    app.inbox.messages.whose({subject: {_contains: "test"}})().length >= 0 ? "PASS" : "FAIL";
} catch(e) { "FAIL: " + e; }
' 2>/dev/null)
if [ "$SEARCH_RESULT" = "PASS" ]; then
    echo "   PASS: Search working"
else
    echo "   WARN: Search may have issues"
fi

echo "=== Done ==="
