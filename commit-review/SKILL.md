---
name: commit-review
description: Multi-agent code review for commits. Triggers on "review commit", "review commits", "commit review".
---

# Commit Review

Multi-agent code review for individual commits or ranges. Mirrors `/code-review` approach but targets commits instead of PRs.

## Usage

```
/commit-review HEAD           # Review last commit
/commit-review abc1234        # Review specific commit
/commit-review HEAD~5..HEAD   # Review range (5 commits)
/commit-review main..feature  # Review branch commits
```

## Execution Steps

Follow these steps precisely:

### 1. Parse input and get commit(s)

```bash
# Single commit
git show --stat <sha>

# Range
git log --oneline <range>
```

### 2. Gather CLAUDE.md files (Haiku agent)

Find relevant CLAUDE.md files:
- Root CLAUDE.md
- CLAUDE.md in directories containing modified files

### 3. For each commit, run 5 parallel Sonnet agents

Each agent reviews `git show <sha>` output:

| Agent | Focus | Method |
|-------|-------|--------|
| #1 | CLAUDE.md compliance | Check changes against project guidelines |
| #2 | Obvious bugs | Shallow scan of diff, major issues only |
| #3 | Historical context | `git blame` and `git log -p` on modified lines |
| #4 | Previous feedback | Check `git log` for related commits/reverts |
| #5 | Code comments | Verify changes respect inline guidance |

Each agent returns: `{file, line, issue, reason, severity}`

### 4. Score issues (parallel Haiku agents)

For each issue, score 0-100:

- **0**: False positive, pre-existing, or doesn't survive scrutiny
- **25**: Might be real, can't verify. Stylistic issues not in CLAUDE.md
- **50**: Real but minor/nitpick. Low practical impact
- **75**: Verified real. Will impact functionality. Mentioned in CLAUDE.md
- **100**: Definitely real. Will happen frequently. Evidence confirms

### 5. Filter and output

Keep only issues scoring >= 80.

## Output Format

For each commit reviewed:

```
### <short-sha> <first line of commit message>

**Files:** file1.cs, file2.cs

**Issues:**

1. [85] <description> (<reason>)
   <file>:<line> - <code snippet>

2. [92] <description> (<reason>)
   <file>:<line> - <code snippet>

---
```

Or if clean:

```
### <short-sha> <first line of commit message>

No issues (checked bugs + CLAUDE.md compliance)

---
```

## False Positives to Ignore

- Pre-existing issues (not introduced by this commit)
- Linter/compiler-catchable issues
- General quality issues unless CLAUDE.md requires them
- Intentional functionality changes
- Issues on unchanged lines

## Notes

- Do not build or typecheck - assume CI handles that
- Focus on bugs that matter, skip pedantic nitpicks
- Cite CLAUDE.md sections when flagging compliance issues
- For ranges, summarize at end: "Reviewed N commits, found M issues"
