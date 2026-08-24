#!/bin/zsh
# fetch-ads.sh <SINCE_ISO> <CONFIG_JSON>
# Hämtar annonser publicerade efter SINCE från JobSearch-API:t enligt config.
# Deterministiskt: alla filter kommer ur config, inga beslut här.
# Output: JSON-array på stdout med trimmade fält per annons.
set -euo pipefail

SINCE="${1:?usage: fetch-ads.sh <SINCE_ISO> <CONFIG_JSON>}"
CONFIG="${2:?usage: fetch-ads.sh <SINCE_ISO> <CONFIG_JSON>}"

python3 - "$SINCE" "$CONFIG" <<'EOF'
import json, sys, urllib.parse, urllib.request

API = "https://jobsearch.api.jobtechdev.se/search"
since, config_path = sys.argv[1], sys.argv[2]
cfg = json.load(open(config_path))

params = [("published-after", since), ("limit", "100")]
for code in cfg["municipalities"].values():
    params.append(("municipality", code))
if cfg.get("driving_license_required") is False:
    params.append(("driving-license-required", "false"))
for f in cfg.get("occupation_fields", []):
    params.append(("occupation-field", f))
# freetext_queries körs som separata sökningar och unionas
queries = cfg.get("freetext_queries") or [None]

seen, out = set(), []
for q in queries:
    offset = 0
    while True:
        p = params + ([("q", q)] if q else []) + [("offset", str(offset))]
        url = API + "?" + urllib.parse.urlencode(p)
        req = urllib.request.Request(url, headers={"accept": "application/json"})
        data = json.load(urllib.request.urlopen(req, timeout=30))
        hits = data.get("hits", [])
        for h in hits:
            if h["id"] in seen:
                continue
            seen.add(h["id"])
            addr = h.get("workplace_address") or {}
            out.append({
                "id": h["id"],
                "headline": h.get("headline"),
                "employer": (h.get("employer") or {}).get("name"),
                "municipality": addr.get("municipality"),
                "address": addr.get("street_address"),
                "working_hours_type": (h.get("working_hours_type") or {}).get("label"),
                "scope_of_work": h.get("scope_of_work"),
                "published": h.get("publication_date"),
                "deadline": h.get("application_deadline"),
                "url": h.get("webpage_url"),
                "description": ((h.get("description") or {}).get("text") or "")[:2500],
            })
        offset += 100
        if offset >= min(data.get("total", {}).get("value", 0), 2000) or not hits:
            break

json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
print()
EOF
