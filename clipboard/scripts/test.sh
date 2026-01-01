#!/bin/bash
set -e

echo "Testing clipboard skill..."

# Test write
echo -n "test-clipboard-content" | pbcopy
result=$(pbpaste)

if [ "$result" = "test-clipboard-content" ]; then
    echo "PASS: Write/read works"
else
    echo "FAIL: Expected 'test-clipboard-content', got '$result'"
    exit 1
fi

# Test multiline
pbcopy << 'EOF'
line1
line2
EOF
result=$(pbpaste)

if [ "$result" = "line1
line2" ]; then
    echo "PASS: Multiline works"
else
    echo "FAIL: Multiline mismatch"
    exit 1
fi

echo "All tests passed"
