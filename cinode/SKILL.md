---
name: cinode
description: View and manage your Cinode consultant profile
argument-hint: "[bio|skills|work]"
---

# Cinode Profile Command

Manage your Cinode consultant profile directly from the command line.

## Usage

- `/cinode` - Show profile overview
- `/cinode bio` - Show/update bio
- `/cinode skills` - List skills
- `/cinode work` - List work experiences

## Configuration

Credentials are stored in `~/.config/cinode/config.json`:

```json
{
  "accessId": "your-access-id",
  "accessSecret": "your-access-secret"
}
```

## Authentication

1. Read credentials from `~/.config/cinode/config.json`
2. Get JWT token: `curl -s -u "$accessId:$accessSecret" https://api.cinode.com/token`
3. Cache token in `/tmp/cinode-token-$USER` (refresh if older than 55 min)
4. Use `Authorization: Bearer $token` for API calls

### Token Helper

```bash
# Get or refresh token
CONFIG="$HOME/.config/cinode/config.json"
TOKEN_FILE="/tmp/cinode-token-$USER"

get_token() {
  # Check cache (55 min = 3300 seconds)
  if [[ -f "$TOKEN_FILE" ]] && [[ $(($(date +%s) - $(stat -f%m "$TOKEN_FILE"))) -lt 3300 ]]; then
    cat "$TOKEN_FILE"
    return
  fi

  # Read credentials
  ACCESS_ID=$(jq -r '.accessId' "$CONFIG")
  ACCESS_SECRET=$(jq -r '.accessSecret' "$CONFIG")

  # Get new token
  TOKEN=$(curl -s -u "$ACCESS_ID:$ACCESS_SECRET" https://api.cinode.com/token | jq -r '.access_token')
  echo "$TOKEN" > "$TOKEN_FILE"
  chmod 600 "$TOKEN_FILE"
  echo "$TOKEN"
}
```

## API Endpoints

Base URL: `https://api.cinode.com`

### Identity

```bash
# Get company and user ID
curl -s -H "Authorization: Bearer $TOKEN" https://api.cinode.com/_whoami
# Returns: { "companyId": 123, "id": 456, ... }
```

### Profile

```bash
CID=<companyId>
UID=<userId>
BASE="https://api.cinode.com/v0.1/companies/$CID/users/$UID/profile"

# Full profile
curl -s -H "Authorization: Bearer $TOKEN" "$BASE"

# Bio/presentation
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/presentation"

# Update bio
curl -s -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "New bio text"}' \
  "$BASE/presentation"

# Skills
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/skills"

# Add skill
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Rust", "level": 4}' \
  "$BASE/skills"

# Work experiences
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/workexperiences"
```

## Implementation

When the user runs `/cinode`, you should:

1. **Check config exists**: Read `~/.config/cinode/config.json`
2. **Get/refresh token**: Use the token helper logic above
3. **Get identity**: Call `/_whoami` to get companyId and userId
4. **Execute command**:
   - No args: Show profile overview (name, title, bio summary, skill count, experience count)
   - `bio`: Show full bio, offer to update
   - `skills`: List all skills with levels
   - `work`: List work experiences

## Output Format

Keep output concise and scannable:

```
# Profile Overview
John Doe
Senior Software Engineer

Bio: Unix philosophy advocate...
Skills: 12 | Experience: 5 positions

Run /cinode bio|skills|work for details
```

For skills:
```
# Skills (12)
Rust         ████████░░  4/5
TypeScript   ██████████  5/5
Go           ██████░░░░  3/5
...
```
