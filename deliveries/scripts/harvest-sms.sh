#!/bin/sh
# harvest-sms.sh <since-iso> [max]
# Emits JSON array of inbound SMS/iMessages received after <since-iso>.
# Requires Full Disk Access for the calling process (reads ~/Library/Messages/chat.db).
#
# Privacy: personal conversations never leave the machine. Swedish mobile numbers
# (+467XXXXXXXX) and Apple ID addresses are filtered out in SQL, so only shortcodes
# and alphanumeric sender IDs (PostNord, Budbee, DHL, Zalando, ...) are emitted.
# DELIVERY_SMS_ALL=1 disables the filter, for debugging only.

set -eu

SINCE="${1:?since-iso required}"
MAX="${2:-80}"
DB="$HOME/Library/Messages/chat.db"

[ -r "$DB" ] || { echo '[]'; exit 0; }

if [ "${DELIVERY_SMS_ALL:-0}" = "1" ]; then
    SENDER_FILTER=""
else
    SENDER_FILTER="AND h.id IS NOT NULL
  AND h.id NOT LIKE '%@%'
  AND NOT h.id GLOB '+467[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'
  AND NOT h.id GLOB '07[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'"
fi

sqlite3 -json -readonly "$DB" "
SELECT
    'sms:' || m.rowid            AS source,
    m.rowid                      AS row_id,
    h.id                         AS sender,
    m.service                    AS service,
    m.text                       AS body,
    datetime(m.date/1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS date
FROM message m
LEFT JOIN handle h ON m.handle_id = h.rowid
WHERE m.is_from_me = 0
  AND m.text IS NOT NULL
  AND length(trim(m.text)) > 0
  AND m.date > (strftime('%s', '$SINCE') - strftime('%s','2001-01-01')) * 1000000000
  $SENDER_FILTER
ORDER BY m.date DESC
LIMIT $MAX;
" 2>/dev/null | grep . || echo '[]'
