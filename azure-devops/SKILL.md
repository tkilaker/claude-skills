---
name: azure-devops
description: Fetch Azure DevOps work items by ID. Triggers on "work item", "ADO", "azure devops", "PBI", "bug #", "task #".
---

# Azure DevOps Work Items

**IMPORTANT: Always fetch the COMPLETE work item - fields, comments, AND images. Run ALL commands below.**

## Prerequisites

Config file at `~/.config/azure-devops/config.json`:

```json
{
  "pat": "YOUR_PAT",
  "organization": "YOUR_ORG",
  "project": "YOUR_PROJECT"
}
```

## Complete Fetch (run ALL of these)

**1. Fetch work item + comments + images:**
```bash
ID=12345 && CONFIG=~/.config/azure-devops/config.json && PAT=$(jq -r .pat "$CONFIG") && ORG=$(jq -r .organization "$CONFIG") && PROJECT=$(jq -r .project "$CONFIG" | sed 's/ /%20/g') && curl -s -u ":$PAT" "https://dev.azure.com/$ORG/$PROJECT/_apis/wit/workitems/$ID?api-version=7.0&\$expand=All" > /tmp/wi${ID}.json && curl -s -u ":$PAT" "https://dev.azure.com/$ORG/$PROJECT/_apis/wit/workitems/$ID/comments?api-version=7.0-preview" > /tmp/wi${ID}_comments.json && IMG_DIR=/tmp/ado-images/workitem_$ID && mkdir -p "$IMG_DIR" && i=1 && for url in $(jq -r '.fields["System.Description"] // ""' /tmp/wi${ID}.json | grep -oE 'https://dev\.azure\.com[^"]+attachments/[^"]+' || true); do guid=$(echo "$url" | grep -oE 'attachments/[a-f0-9-]+' | cut -d/ -f2); curl -s -u ":$PAT" "$url" -o "$IMG_DIR/image_${i}_${guid:0:8}.png"; i=$((i+1)); done && echo "Fetched work item $ID"
```

**2. Display work item fields:**
```bash
ID=12345 && jq '{id: .id, type: .fields["System.WorkItemType"], title: .fields["System.Title"], state: .fields["System.State"], assignedTo: .fields["System.AssignedTo"].displayName, description: .fields["System.Description"], acceptanceCriteria: .fields["Microsoft.VSTS.Common.AcceptanceCriteria"], priority: .fields["Microsoft.VSTS.Common.Priority"], tags: .fields["System.Tags"], areaPath: .fields["System.AreaPath"], iterationPath: .fields["System.IterationPath"]}' /tmp/wi${ID}.json
```

**3. Display comments:**
```bash
ID=12345 && jq '.comments[] | {author: .createdBy.displayName, date: .createdDate, text: .text}' /tmp/wi${ID}_comments.json
```

**4. List downloaded images:**
```bash
ID=12345 && ls -la /tmp/ado-images/workitem_$ID 2>/dev/null || echo "No images"
```

Then use the Read tool on any downloaded images to view them.

## Output format (markdown)

```markdown
# [Type] #ID: Title

**State:** X | **Assigned:** Y | **Priority:** Z

## Description
[Plain text, strip HTML]

## Acceptance Criteria
[Plain text, strip HTML]

## Images
[Local paths to downloaded images]

## Comments
### Author - Date
[Comment text]

---
Tags: a, b, c
Area: X | Iteration: Y
```

## Notes

- PAT needs "Work Items (Read)" scope
- URL-encode project name if it has spaces (`sed 's/ /%20/g'`)
- Save API responses to files to avoid shell escaping issues with JSON
- HTML in description/AC: strip tags, decode entities
- For clipboard: pipe final markdown to `pbcopy`
