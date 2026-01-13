---
name: changelog
description: Generate Teams-friendly release notes from git commits for App test group.
argument-hint: "[tag]"
allowed-tools:
  - Bash
  - Read
---

# Changelog Generator

Generate release notes for the App test group in Microsoft Teams.

## Instructions

1. **Determine the tag range:**
   - If a tag argument is provided (e.g., `/changelog v3.1.0`), use that tag
   - Otherwise, get the latest tag on HEAD (not by version number):
     ```bash
     cd /path/to/frontend-app && git describe --tags --abbrev=0 HEAD
     ```
   - Find the previous tag (the tag before the target tag):
     ```bash
     git describe --tags --abbrev=0 <target-tag>^
     ```

2. **Gather commits from both repos:**

   **Frontend** (`/path/to/frontend-app`):
   ```bash
   cd /path/to/frontend-app && git log <previous-tag>..<target-tag> --format="%s" --no-merges
   ```

   **Backend** (`/path/to/backend-api`):
   - Get the date of the target frontend tag
   - Get the date of the previous frontend tag
   - Get backend commits between those dates:
   ```bash
   cd /path/to/backend-api && git log --since="<previous-tag-date>" --until="<target-tag-date>" --format="%s" --no-merges
   ```

3. **Filter commits:**
   - Include: `feat:`, `fix:` (user-visible changes)
   - Exclude: `refactor:`, `chore:`, `test:`, `docs:`, `perf:`, `ci:`, `style:`, `revert:`
   - Exception: Include `perf:` only if it's user-noticeable (e.g., "faster search")

4. **Rewrite for testers:**
   Transform developer language into user-facing descriptions:
   - "feat: add manufacturer and forecast to Where Used" → "Manufacturer and sales forecast columns in Where Used"
   - "fix: widen Z-BOM description column" → "Wider Z-BOM description column"
   - Remove technical details (API, hooks, services, etc.)
   - Focus on what users SEE, not how it's implemented
   - Use active voice, present tense

5. **Group backend changes:**
   - Only include backend changes that enable visible frontend features
   - Group them under "BACKEND" section with brief explanation
   - Skip pure backend refactors, internal fixes, test changes

6. **Output format (Teams plain text):**

```
App <tag> - <date>

NEW
- <feature description>
- <feature description>

FIXED
- <fix description>
- <fix description>

BACKEND
- <backend change> (enables <frontend feature>)
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
