#!/bin/bash
# Test script for Apple Reminders skill

echo "=== Apple Reminders Skill Test ==="

# Get first list
LIST=$(reminders show-lists | head -1)
echo "Using list: $LIST"

# Create
echo "1. Creating test reminder..."
reminders add "$LIST" "__SKILL_TEST__" --notes "Test notes" >/dev/null

# Read
echo "2. Reading..."
FOUND=$(reminders show "$LIST" --format json | jq -r '.[] | select(.title == "__SKILL_TEST__") | .title')
if [ "$FOUND" = "__SKILL_TEST__" ]; then
    echo "   PASS: Found reminder"
else
    echo "   FAIL: Could not read reminder"
    exit 1
fi

# Get index
INDEX=$(reminders show "$LIST" | grep -n "__SKILL_TEST__" | head -1 | cut -d: -f1)
INDEX=$((INDEX - 1))

# Complete
echo "3. Marking complete..."
reminders complete "$LIST" "$INDEX" >/dev/null

# Verify completion
echo "4. Verifying completion..."
COMPLETED=$(reminders show "$LIST" --include-completed --format json | jq -r '.[] | select(.title == "__SKILL_TEST__") | .isCompleted')
if [ "$COMPLETED" = "true" ]; then
    echo "   PASS: Marked complete"
else
    echo "   FAIL: Not marked complete"
fi

# Uncomplete first (required to delete)
echo "5. Uncompleting before delete..."
CINDEX=$(reminders show "$LIST" --only-completed | grep "__SKILL_TEST__" | cut -d: -f1)
reminders uncomplete "$LIST" "$CINDEX" >/dev/null 2>&1

# Get index from default view
INDEX=$(reminders show "$LIST" | grep "__SKILL_TEST__" | cut -d: -f1)

# Delete
echo "6. Deleting..."
reminders delete "$LIST" "$INDEX" >/dev/null

# Verify deletion
echo "7. Verifying deletion..."
COUNT=$(reminders show "$LIST" --include-completed --format json | jq '[.[] | select(.title == "__SKILL_TEST__")] | length')
if [ "$COUNT" = "0" ]; then
    echo "   PASS: Reminder deleted"
else
    echo "   FAIL: Reminder still exists"
fi

echo "=== Done ==="
