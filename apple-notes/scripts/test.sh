#!/bin/bash
# Test script for Apple Notes skill

echo "=== Apple Notes Skill Test ==="

# Test: title should appear exactly once when created correctly (no title in body)
echo "0. Testing title appears exactly once..."
osascript -l JavaScript -e 'Application("Notes").make({new: "note", withProperties: {name: "__DUPE_TEST__", body: "<div>Content only</div>"}})'
sleep 1
DUPE_CHECK=$(osascript -l JavaScript -e '
const app = Application("Notes");
const n = app.notes.whose({name: "__DUPE_TEST__"})();
if (n.length > 0) {
    const body = n[0].body();
    // Title should appear exactly once (auto-added by Apple Notes)
    const matches = body.match(/<div>__DUPE_TEST__<\/div>/g);
    const count = matches ? matches.length : 0;
    count === 1 ? "PASS" : "FAIL (title appears " + count + " times, expected 1)";
} else { "FAIL (note not found)"; }
')
echo "   Title count test: $DUPE_CHECK"
# Cleanup
osascript -l JavaScript -e 'var app = Application("Notes"); var notes = app.notes.whose({name: "__DUPE_TEST__"})(); if (notes.length > 0) { app.delete(notes[0]); }'
sleep 1

# Create
echo "1. Creating test note..."
osascript -l JavaScript -e 'Application("Notes").make({new: "note", withProperties: {name: "__SKILL_TEST__", body: "<div>Test</div>"}})'
sleep 1

# Read
echo "2. Reading..."
BODY=$(osascript -l JavaScript -e 'const app = Application("Notes"); const n = app.notes.whose({name: "__SKILL_TEST__"})(); n.length > 0 ? n[0].body() : "FAIL"')
echo "   Body: $BODY"

# Update
echo "3. Updating..."
osascript -l JavaScript -e 'const app = Application("Notes"); const n = app.notes.whose({name: "__SKILL_TEST__"})(); if (n.length > 0) { n[0].body = "<div>__SKILL_TEST__</div><div>Updated!</div>"; "OK"; }'

# Verify update
echo "4. Verifying update..."
BODY=$(osascript -l JavaScript -e 'const app = Application("Notes"); const n = app.notes.whose({name: "__SKILL_TEST__"})(); n.length > 0 ? n[0].body() : "FAIL"')
echo "   Body: $BODY"

# Delete
echo "5. Deleting (moves to trash)..."
osascript -l JavaScript -e 'var app = Application("Notes"); var notes = app.notes.whose({name: "__SKILL_TEST__"})(); if (notes.length > 0) { app.delete(notes[0]); }'
sleep 2

# Verify deletion - check main Notes folder only (not trash)
echo "6. Verifying not in main folder..."
RESULT=$(osascript -l JavaScript -e '
const app = Application("Notes");
const folder = app.folders.whose({name: "Notes"})()[0];
folder.notes.whose({name: "__SKILL_TEST__"})().length === 0 ? "PASS" : "FAIL";
')
echo "   Result: $RESULT"

echo "=== Done ==="
