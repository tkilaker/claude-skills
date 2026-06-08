---
name: azure-devops
description: Read Azure DevOps work items by ID or URL, including fields, acceptance criteria, comments, relations, and downloaded images/attachments. Use when the user mentions Azure DevOps, ADO, work item, PBI, bug, task, feature, user story, or asks about an issue/ticket such as "#12345".
---

# Azure DevOps Work Items

Always fetch the complete work item before answering: fields, comments, relations, and images/attachments. Do not infer ticket contents from the ID or title alone.

## Quick Start

Use the bundled fetcher:

```bash
python3 ~/.agents/skills/azure-devops/scripts/fetch_work_item.py 12345
```

For bare IDs, it reads `~/.config/azure-devops/config.json`. For Azure DevOps URLs, it infers the organization/project from the URL and selects a matching `*.json` profile under `~/.config/azure-devops/`. It writes raw API responses and downloaded attachments under `/tmp/ado-workitems/<id>/`, and prints a markdown summary. It uses only the Python standard library.

Expected config:

```json
{
  "pat": "YOUR_PAT",
  "organization": "YOUR_ORG",
  "project": "YOUR_PROJECT"
}
```

PAT scope: Work Items (Read).

Multiple orgs are supported by adding more JSON files in the same directory, for example:

- `~/.config/azure-devops/config.json` for the default profile.
- `~/.config/azure-devops/other-project.json` for another organization/project.

If the input is a bare ID but a non-default profile is needed, pass the profile explicitly:

```bash
python3 ~/.agents/skills/azure-devops/scripts/fetch_work_item.py 27897 --config other-project
```

## Workflow

1. Extract the work item ID from the user's text. Accept plain IDs, `#12345`, PBI/bug/task references, or Azure DevOps URLs.
2. Run `scripts/fetch_work_item.py <id-or-url>`. Prefer the full Azure DevOps URL when the org/project is not the default profile.
3. Read the printed markdown. If images were downloaded, inspect relevant local files with image tools before making visual claims.
4. Answer with the ticket facts the user needs. Include important state, title, description, acceptance criteria, comments, blockers, and image paths when relevant.

For multiple IDs, run the script once per ID.

## Output Files

For ID `12345`, the script writes:

- `/tmp/ado-workitems/12345/workitem.json`
- `/tmp/ado-workitems/12345/comments.json`
- `/tmp/ado-workitems/12345/summary.md`
- `/tmp/ado-workitems/12345/attachments/*`

Use `summary.md` for compact context and raw JSON only when you need exact field names or relation details.

## Notes

- Never print or expose the PAT.
- HTML in Azure DevOps fields and comments is converted to plain text in the markdown summary.
- The script downloads relation attachments and embedded image URLs found in description, acceptance criteria, reproduction steps, system info, and comments.
- If the script reports an auth or config error, surface the exact missing prerequisite without guessing.
