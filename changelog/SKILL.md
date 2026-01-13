---
name: changelog
description: Generate Teams-friendly release notes from git commits for App test group.
argument-hint: "[frontend-tag] [api:commit]"
allowed-tools:
  - Bash
  - Read
---

# Changelog Generator

Generate release notes for the App test group in Microsoft Teams.

## Usage

```
/changelog                      # Latest frontend tag only
/changelog v3.0.51              # Specific frontend tag only
/changelog api:abc123           # Backend only (from commit to HEAD)
/changelog v3.0.51 api:abc123   # Both frontend tag and backend commit
```

## Instructions

1. **Parse arguments:**
   - Frontend tag: bare argument like `v3.0.51` (optional)
   - Backend commit: prefixed with `api:` like `api:abc123` (optional)
   - If no frontend tag specified, use latest tag on HEAD

2. **Get frontend commits (if frontend tag provided or defaulted):**
   ```bash
   cd /path/to/frontend-app && git describe --tags --abbrev=0 HEAD
   # Find previous tag
   git describe --tags --abbrev=0 <target-tag>^
   # Get commits between tags
   git log <previous-tag>..<target-tag> --format="%s" --no-merges
   ```

3. **Get backend commits (if api: argument provided):**
   ```bash
   cd /path/to/backend-api && git log <commit>..HEAD --format="%s" --no-merges
   ```
   - The commit is the "last deployed" commit - changes FROM there TO HEAD are included

4. **Filter commits:**
   - Include: `feat:`, `fix:` (user-visible changes)
   - Exclude: `refactor:`, `chore:`, `test:`, `docs:`, `perf:`, `ci:`, `style:`, `revert:`
   - Exception: Include `perf:` only if it's user-noticeable (e.g., "faster search")

5. **Rewrite for testers:**
   Transform developer language into user-facing descriptions:
   - "feat: add manufacturer and forecast to Where Used" → "Manufacturer and sales forecast columns in Where Used"
   - "fix: widen Z-BOM description column" → "Wider Z-BOM description column"
   - Remove technical details (API, hooks, services, etc.)
   - Focus on what users SEE, not how it's implemented
   - Use active voice, present tense

6. **Group backend changes:**
   - Only include backend changes that enable visible frontend features
   - Group them under "BACKEND" section with brief explanation
   - Skip pure backend refactors, internal fixes, test changes

7. **Output format (Teams plain text):**

If frontend only:
```
App <tag> - <date>

NEW
- <feature description>

FIXED
- <fix description>
```

If backend only:
```
App API - <date>

NEW
- <feature description>

FIXED
- <fix description>
```

If both:
```
App <tag> - <date>

NEW
- <feature description>

FIXED
- <fix description>

BACKEND
- <backend change>
```

## Rules

- No emojis
- No markdown formatting (Teams doesn't render it on paste)
- ALL CAPS section headers
- Simple dashes for bullets
- Keep descriptions short (one line each)
- Date format: "Jan 13" (short month, day only)
- If no changes in a category, omit that section entirely
- If no user-visible changes at all, say "Internal improvements only - no user-visible changes"

## Example Output

```
App v3.0.51 - Jan 13

NEW
- Manufacturer and 12-month sales forecast columns in Where Used and item details

FIXED
- Forecast column renamed to "Sales Forecast 12M" for clarity
- Wider Z-BOM description column
- Better aligned nested table columns
```
