#!/bin/bash
# Test script for Apple Reminders skill

echo "=== Apple Reminders Skill Test ==="

# Create
echo "1. Creating test reminder..."
osascript -l JavaScript -e 'const app = Application("Reminders"); const r = app.Reminder({name: "__SKILL_TEST__", body: "Test notes"}); app.defaultList.reminders.push(r);'
sleep 1

# Read
echo "2. Reading..."
NAME=$(osascript -l JavaScript -e 'const app = Application("Reminders"); const r = app.reminders.whose({name: "__SKILL_TEST__"})(); r.length > 0 ? r[0].name() : "FAIL"')
if [ "$NAME" = "__SKILL_TEST__" ]; then
    echo "   PASS: Found reminder"
else
    echo "   FAIL: Could not read reminder"
fi

# Update (mark complete)
echo "3. Marking complete..."
osascript -l JavaScript -e 'const app = Application("Reminders"); const r = app.reminders.whose({name: "__SKILL_TEST__"})()[0]; if (r) r.completed = true;'

# Verify update
echo "4. Verifying completion..."
COMPLETED=$(osascript -l JavaScript -e 'const app = Application("Reminders"); const r = app.reminders.whose({name: "__SKILL_TEST__"})()[0]; r ? r.completed() : "FAIL"')
if [ "$COMPLETED" = "true" ]; then
    echo "   PASS: Marked complete"
else
    echo "   FAIL: Not marked complete"
fi

# Delete
echo "5. Deleting..."
osascript -l JavaScript -e 'const app = Application("Reminders"); const r = app.reminders.whose({name: "__SKILL_TEST__"})()[0]; if (r) app.delete(r);'
sleep 1

# Verify deletion
echo "6. Verifying deletion..."
COUNT=$(osascript -l JavaScript -e 'const app = Application("Reminders"); app.reminders.whose({name: "__SKILL_TEST__"})().length')
if [ "$COUNT" = "0" ]; then
    echo "   PASS: Reminder deleted"
else
    echo "   FAIL: Reminder still exists"
fi

echo "=== Done ==="
