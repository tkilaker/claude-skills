#!/bin/bash
# Test script for Apple Calendar skill

echo "=== Apple Calendar Skill Test ==="

# Get first writable calendar name
CAL=$(osascript -l JavaScript -e 'const app = Application("Calendar"); const cals = app.calendars().filter(c => c.writable()); cals.length > 0 ? cals[0].name() : ""')
if [ -z "$CAL" ]; then
    echo "FAIL: No writable calendar found"
    exit 1
fi
echo "Using calendar: $CAL"

# Create
echo "1. Creating test event..."
osascript -l JavaScript -e "
const app = Application('Calendar');
const cal = app.calendars.byName('$CAL');
const start = new Date();
start.setHours(start.getHours() + 1, 0, 0, 0);
const end = new Date(start.getTime() + 3600000);
const event = app.Event({summary: '__SKILL_TEST__', startDate: start, endDate: end});
cal.events.push(event);
"
sleep 2

# Read
echo "2. Reading..."
SUMMARY=$(osascript -l JavaScript -e "
const app = Application('Calendar');
const cal = app.calendars.byName('$CAL');
const e = cal.events.whose({summary: '__SKILL_TEST__'})();
e.length > 0 ? e[0].summary() : 'FAIL';
")
if [ "$SUMMARY" = "__SKILL_TEST__" ]; then
    echo "   PASS: Found event"
else
    echo "   FAIL: Could not read event"
fi

# Update
echo "3. Updating location..."
osascript -l JavaScript -e "
const app = Application('Calendar');
const cal = app.calendars.byName('$CAL');
const e = cal.events.whose({summary: '__SKILL_TEST__'})();
if (e.length > 0) e[0].location = 'Test Location';
"

# Verify
echo "4. Verifying update..."
LOC=$(osascript -l JavaScript -e "
const app = Application('Calendar');
const cal = app.calendars.byName('$CAL');
const e = cal.events.whose({summary: '__SKILL_TEST__'})();
e.length > 0 ? e[0].location() : 'FAIL';
")
if [ "$LOC" = "Test Location" ]; then
    echo "   PASS: Location updated"
else
    echo "   FAIL: Location not updated"
fi

# Delete
echo "5. Deleting..."
osascript -l JavaScript -e "
const app = Application('Calendar');
const cal = app.calendars.byName('$CAL');
const e = cal.events.whose({summary: '__SKILL_TEST__'})();
if (e.length > 0) app.delete(e[0]);
"
sleep 1

# Verify deletion
echo "6. Verifying deletion..."
COUNT=$(osascript -l JavaScript -e "
const app = Application('Calendar');
const cal = app.calendars.byName('$CAL');
cal.events.whose({summary: '__SKILL_TEST__'})().length;
")
if [ "$COUNT" = "0" ]; then
    echo "   PASS: Event deleted"
else
    echo "   FAIL: Event still exists"
fi

echo "=== Done ==="
