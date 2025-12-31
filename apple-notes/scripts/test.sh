#!/bin/bash
# Test script for Apple Notes skill

echo "=== Apple Notes Skill Test ==="

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
