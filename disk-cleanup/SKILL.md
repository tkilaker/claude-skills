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
- `~/Library/Caches/`: measure subdirs first (`du -sm ~/Library/Caches/* | sort -rn`), then sweep every subdir's contents with `find "$dir" -mindepth 1 -maxdepth 1 -exec rm -rf {} +`. Skip `CloudKit` and `FamilyCircle` (system-managed). Re-measure the total after — it should land near zero; if not, the sweep silently failed.
- Xcode: `rm -rf ~/Library/Developer/Xcode/DerivedData`, `xcrun simctl delete unavailable`
- Docker/OrbStack: `docker system prune -f`, `docker builder prune -af`, `docker volume prune -f` (dangling only). **Never `docker system prune -a` on images, never remove named volumes** — compose project data lives there.
- `rm -rf ~/dev/brain/scratch/*` (documented safe to clobber)

## Tier 2 — stale build artifacts (always delete)

In each `~/dev/*` repo where the last git commit is >6 months old AND nothing in the working tree was modified in the last 6 months: delete `node_modules`, `.venv`, `venv`, `target`, `dist`, `build`, `.next`, `bin`, `obj` (search top 2 levels). All rebuildable. Never delete the repo itself. Non-git dirs: use dir mtime alone, same 6-month rule, artifacts only.

## Tier 3 — Downloads (rules + judgment)

`~/Downloads` is TCC-protected: in a launchd context without a Full Disk Access grant, any touch of it **blocks forever** on an invisible permission prompt. Probe before doing anything else in this tier:

```sh
rm -f /tmp/dl-probe; ( ls ~/Downloads >/dev/null 2>&1 && touch /tmp/dl-probe ) & sleep 5
[ -f /tmp/dl-probe ] && echo accessible || echo BLOCKED
```

If BLOCKED: skip Tier 3 entirely, flag "Downloads inaccessible (TCC) — grant Full Disk Access to claude" in the report, and move on. Also pass an explicit short timeout on every Bash call in this tier so no single command can stall the run.

If accessible, delete files older than 30 days that are:

- **Clearly software installers**: `.dmg`, `.pkg`, `.iso`, and `.zip` only when the name is unambiguously an app/tool release (e.g. `Tool-1.2.3-arm64.zip`). Judge each file by name.
- **Dated system exports** (approved 2026-07-06): re-exportable dumps from Data Portal/ERP/GitHub, recognizable as `Name_YYYY-MM-DD.(xlsx|csv|json)` or families like `SearchResults_*`, `Sustainability_Export_*`, `Assembly_Compliance_*`, `SalesOrder*`, `SerialNumber*`, `BulkImportErrors*`, `bom-compare-*`, `WhereUsed_*`, `manufacturers-*`, `*_PCN_Report_*`, BOM XML/pick-place outputs.
- **Exact duplicates**: ` (N)`/` copy`/`-N` suffixed files whose checksum matches the base file. Differing content → keep both.

Ambiguous or data-looking archives → flag in the report, do not delete.

Downloads keeps a sorted structure (est. 2026-07-06): `docs/`, `assets/`, `dev/`, `media/` subfolders. File stray keepers into these rather than leaving them loose.

Never touch in Downloads: the `watch-*` alias files (intentional shortcuts to NAS shares), and anything that looks like non-regenerable work data (contracts, received documents, recordings).

## Never touch, ever

- `~/dev/scratch/` (holds SQL recon referenced by Ekman docs — NOT the same as brain/scratch)
- `~/dev/prodia/legacy/` (irreplaceable) — and no old zips in Downloads that could be its source
- `/Volumes/*` (NAS, T7), `~/Library/Mobile Documents` (iCloud), Photos library
- Named Docker volumes
- Never use `sudo`. Stay inside `$HOME`.

## Execution gotchas (learned 2026-07-06)

- **Never sweep with shell globs** (`rm -rf dir/* dir/.[!.]*`): zsh aborts the whole command when any glob has no match, so nothing is deleted while the log claims success. Use `find -mindepth 1 -maxdepth 1 -exec rm -rf {} +`, or `setopt null_glob` first.
- **Verify every tier with du**: measure → delete → re-measure. A logged deletion is not a completed deletion.
- **`df` may not move after freeing space**: local Time Machine snapshots pin deleted blocks for up to 24h. Check `tmutil listlocalsnapshots /`; if snapshots predate the run, report freed space as "snapshot-held, reclaims <24h" — don't re-run tiers or delete snapshots.
- **Don't script with `ls`** — it's aliased (eza) and behaves differently piped. Use `find` for listing/counting.
- `docker volume prune -f` only removes anonymous volumes on modern Docker — named compose volumes are safe, but verify with `docker volume ls` after anyway.

## Report

Final message AND appended to the log:

- Freed total (file-level, from du) and per tier; free space before → after. If df's delta is smaller than file-level freed, say why (snapshot-held).
- Ranked list of flagged manual candidates with sizes: big idle user content (e.g. ComfyUI models on mbp), large non-installer Downloads, whole stale repos. Suggest the NAS `dat` share as archive target for anything worth keeping.
- Push summary: `curl -s -H "Title: disk-cleanup" -d "$(hostname -s): freed <X>GB, <Y>GB free, <N> flagged" ntfy.sh/tim-claude-7k9x2m`
