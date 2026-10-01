#!/usr/bin/env bash
# Wraps a brief body in the fixed Ekman Intelligence header and prints it to a one-page A4 PDF.
#
#   render.sh <body.html> <out.pdf> [--to Axel] [--kind Uppdatering] [--date "1 oktober 2026"]
#
# Writes <out>.png next to the PDF for a visual check, and fails if the PDF runs past one page.
set -euo pipefail

DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BODY=${1:?usage: render.sh <body.html> <out.pdf> [--to X] [--kind X] [--date X]}
OUT=${2:?usage: render.sh <body.html> <out.pdf>}
shift 2
TO=Axel KIND=Uppdatering
MONTHS=(januari februari mars april maj juni juli augusti september oktober november december)
DATE="$(date +%-d) ${MONTHS[$(( $(date +%-m) - 1 ))]} $(date +%Y)"
while [ $# -gt 0 ]; do
  case "$1" in
    --to) TO=$2; shift 2 ;;
    --kind) KIND=$2; shift 2 ;;
    --date) DATE=$2; shift 2 ;;
    *) echo "unknown flag $1" >&2; exit 2 ;;
  esac
done

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
cp "$DIR"/assets/* "$DIR/brief.css" "$WORK/"
TITLE=$(sed -n 's:.*<h1[^>]*>\(.*\)</h1>.*:\1:p' "$BODY" | head -1)

{
  cat <<EOF
<!doctype html><html lang="sv"><head><meta charset="utf-8"><title>${TITLE:-Ekman Intelligence}</title>
<link rel="stylesheet" href="brief.css"></head><body>
<header><img src="ekman-mark.png" alt=""><div><div class="n">Ekman Intelligence</div><div class="s">Ekman &amp; Co</div></div>
<div class="d"><div class="kind">$KIND</div>Till $TO, från Tim<br>$DATE</div></header>
EOF
  cat "$BODY"
  echo '</body></html>'
} > "$WORK/index.html"

"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$OUT" "file://$WORK/index.html" 2>/dev/null
PAGES=$(pdfinfo "$OUT" | awk '/^Pages:/ {print $2}')
pdftoppm -png -r 110 -singlefile "$OUT" "${OUT%.pdf}"
echo "$OUT ($PAGES page$([ "$PAGES" = 1 ] || echo s)), preview ${OUT%.pdf}.png"
[ "$PAGES" = 1 ] || { echo "runs past one page: cut copy before shrinking type" >&2; exit 1; }
