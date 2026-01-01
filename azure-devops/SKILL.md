---
name: azure-devops
description: Fetch Azure DevOps work items by ID. Triggers on "work item", "ADO", "azure devops", "PBI", "bug #", "task #".
---

# Azure DevOps Work Items

Fetch work item details by ID from Azure DevOps.

## Prerequisites

Config file at `~/.config/azure-devops/config.json`:

```json
{
  "pat": "YOUR_PAT",
  "organization": "YOUR_ORG",
  "project": "YOUR_PROJECT"
}
```

## Get work item by ID

```bash
CONFIG=~/.config/azure-devops/config.json
PAT=$(jq -r .pat "$CONFIG")
ORG=$(jq -r .organization "$CONFIG")
PROJECT=$(jq -r .project "$CONFIG" | sed 's/ /%20/g')
ID=12345

# Fetch work item (save to file to avoid shell escaping issues)
curl -s -u ":$PAT" \
  "https://dev.azure.com/$ORG/$PROJECT/_apis/wit/workitems/$ID?api-version=7.0&\$expand=All" \
  > /tmp/wi${ID}.json

# Parse fields
jq '{
  id: .id,
  type: .fields["System.WorkItemType"],
  title: .fields["System.Title"],
  state: .fields["System.State"],
  assignedTo: .fields["System.AssignedTo"].displayName,
  description: .fields["System.Description"],
  acceptanceCriteria: .fields["Microsoft.VSTS.Common.AcceptanceCriteria"],
  priority: .fields["Microsoft.VSTS.Common.Priority"],
  tags: .fields["System.Tags"],
  areaPath: .fields["System.AreaPath"],
  iterationPath: .fields["System.IterationPath"]
}' /tmp/wi${ID}.json
```

## Get comments

```bash
curl -s -u ":$PAT" \
  "https://dev.azure.com/$ORG/$PROJECT/_apis/wit/workitems/$ID/comments?api-version=7.0-preview" \
  > /tmp/wi${ID}_comments.json

jq '.comments[] | {author: .createdBy.displayName, date: .createdDate, text: .text}' /tmp/wi${ID}_comments.json
```

## Download embedded images

Two types of images:

### 1. URL-based images (description/AC)

```bash
IMG_DIR=/tmp/ado-images/workitem_$ID
mkdir -p $IMG_DIR

# Extract attachment URLs and download with unique names
i=1
jq -r '.fields["System.Description"]' /tmp/wi${ID}.json | \
  grep -oE 'https://dev\.azure\.com[^"]+attachments/[^"]+' | \
  while read url; do
    guid=$(echo "$url" | grep -oE 'attachments/[a-f0-9-]+' | cut -d/ -f2)
    filename="image_${i}_${guid:0:8}.png"
    curl -s -u ":$PAT" "$url" -o "$IMG_DIR/$filename"
    i=$((i+1))
  done
```

### 2. Base64 embedded images (comments)

```bash
# Extract base64 data URIs from comments
jq -r '.comments[].text' /tmp/wi${ID}_comments.json | \
  grep -oE 'data:image/[^"]+' | \
  while read -r datauri; do
    base64data=$(echo "$datauri" | sed 's/.*base64,//')
    echo "$base64data" | base64 -d > "$IMG_DIR/comment_image_$((++n)).jpg"
  done
```

### Use images in output

Include local paths so Claude can Read them:

```markdown
## Images
![image_1](/tmp/ado-images/workitem_12345/image_1_3c0307bd.png)
```

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
