#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAIL="$ROOT/scripts/mail"
RULES="$ROOT/config/rules.example.json"
export APPLE_MAIL_TIMEOUT_SECONDS="${APPLE_MAIL_TIMEOUT_SECONDS:-10}"
# Scheduled runs start without a locale; Ruby then reads stdin as US-ASCII and fails on non-ASCII subjects.
export LANG="${LANG:-en_US.UTF-8}"
STATE="$(mktemp -d)"
trap 'rm -rf "$STATE"' EXIT

json() { ruby -rjson -e 'JSON.parse(STDIN.read)' >/dev/null; }

"$MAIL" '{"action":"accounts"}' | json
"$MAIL" '{"action":"list","limit":3}' | json
"$MAIL" '{"action":"paths"}' | json
"$MAIL" "{\"action\":\"audit-healthcheck\",\"auditPath\":\"$STATE/audit.jsonl\"}" | ruby -rjson -e 'abort "audit failed" unless JSON.parse(STDIN.read).fetch("status") == "ok"'
test -s "$STATE/audit.jsonl"
"$MAIL" "{\"action\":\"validate-rules\",\"rulesPath\":\"$RULES\"}" | ruby -rjson -e 'abort "rules invalid" unless JSON.parse(STDIN.read).fetch("valid")'
"$MAIL" "{\"action\":\"run-rule\",\"rulesPath\":\"$RULES\",\"name\":\"example-invoice-forward\"}" | ruby -rjson -e 'abort "expected disabled" unless JSON.parse(STDIN.read).fetch("status") == "disabled"'

echo "PASS: read operations, rule validation, and disabled-rule guard"
