---
name: disk-cleanup
description: Free disk space on this Mac. Cleans caches, stale build artifacts, and old installers; flags big items for a human call. Triggers on "clean up disk", "free up space", "disk full", "disk cleanup".
---

# Disk Cleanup

One full cleanup pass. Runs on both mbp and mini — probe before cleaning (`command -v brew npm docker xcrun uv pip`), silently skip tools that aren't installed. Everything you delete must be regenerable or re-downloadable; there may be no live backup.

## Procedure

1. Record `df -h /System/Volumes/Data` (before).
2. Work the tiers below. Log every deletion with its size.
3. Record `df -h /System/Volumes/Data` (after), write the report, push the ntfy summary.

Log file: `~/Library/Logs/disk-cleanup.log`. Start each run with a header line: `=== disk-cleanup $(date '+%Y-%m-%d %H:%M') $(hostname -s) ===`.

## Tier 1 — caches (always delete)

- `brew cleanup --prune=all` and `rm -rf "$(brew --cache)"`
- `npm cache clean --force`
- `uv cache clean`, `pip cache purge`
- `rm -rf ~/.cargo/registry/cache ~/.cache/*`
- `~/Library/Caches/`: measure subdirs first (`du -sm ~/Library/Caches/* | sort -rn`), delete contents of subdirs >500MB, then sweep the rest. Skip `CloudKit` and `FamilyCircle` (system-managed).
- Xcode: `rm -rf ~/Library/Developer/Xcode/DerivedData`, `xcrun simctl delete unavailable`
- Docker/OrbStack: `docker system prune -f`, `docker builder prune -af`, `docker volume prune -f` (dangling only). **Never `docker system prune -a` on images, never remove named volumes** — compose project data lives there.
- `rm -rf ~/dev/brain/scratch/*` (documented safe to clobber)

## Tier 2 — stale build artifacts (always delete)

In each `~/dev/*` repo where the last git commit is >6 months old AND nothing in the working tree was modified in the last 6 months: delete `node_modules`, `.venv`, `venv`, `target`, `dist`, `build`, `.next`, `bin`, `obj` (search top 2 levels). All rebuildable. Never delete the repo itself. Non-git dirs: use dir mtime alone, same 6-month rule, artifacts only.

## Tier 3 — Downloads (rules + judgment)

Delete files in `~/Downloads` older than 30 days that are **clearly software installers**: `.dmg`, `.pkg`, `.iso`, and `.zip` only when the name is unambiguously an app/tool release (e.g. `Tool-1.2.3-arm64.zip`). Judge each file by name. Ambiguous or data-looking archives → flag in the report, do not delete.

Never touch in Downloads: `~/Downloads/camel/`, spreadsheets, PDFs, CSVs, exports, anything that looks like work data.

## Never touch, ever

- `~/dev/scratch/` (holds SQL recon referenced by Ekman docs — NOT the same as brain/scratch)
- `~/dev/prodia/legacy/` (irreplaceable) — and no old zips in Downloads that could be its source
- `/Volumes/*` (NAS, T7), `~/Library/Mobile Documents` (iCloud), Photos library
- Named Docker volumes
- Never use `sudo`. Stay inside `$HOME`.

## Report

Final message AND appended to the log:

- Freed total and per tier; free space before → after
- Ranked list of flagged manual candidates with sizes: big idle user content (e.g. ComfyUI models on mbp), large non-installer Downloads, whole stale repos. Suggest the NAS `dat` share as archive target for anything worth keeping.
- Push summary: `curl -s -H "Title: disk-cleanup" -d "$(hostname -s): freed <X>GB, <Y>GB free, <N> flagged" ntfy.sh/tim-claude-7k9x2m`
