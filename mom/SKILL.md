---
name: mom
description: Generate standardized Minutes of Meeting (MOM) from raw meeting transcription. Use when the user asks for a meeting summary, minutes of meeting, MOM, summarize meeting, motessammanfattning, or motesprotokoll.
---

# Minutes of Meeting Generator

Generate a standardized MOM `.txt` file from a raw meeting transcription and optional context.

## Input

The user provides:

1. Transcription - raw text file path, pasted text, or reference to a file
2. Context, optional - background info, project details, attendee roles, etc.

If the user does not specify attendees or context, extract what you can from the transcription itself.

## Process

1. Inspect the current context before summarizing:
   - Check the current working directory and nearby project instructions.
   - Read likely context files when present, especially `AGENTS.md`, `README.md`, `docs/README.md`, and existing `docs/meetings/` MOM files.
   - Use targeted searches for participant names, project names, system names, glossary terms, NDA/client context, and meeting-doc naming patterns.
2. Read the full transcription. For large files, inspect metadata first and read in chunks with shell tools.
3. Extract attendees, topics discussed, decisions, action items, and key quotes.
4. Organize into the standard format below.
5. Save using the current project's established meeting-document convention when one is discoverable. Otherwise write the result to `~/Downloads/Meeting Summary YYYY-MM-DD.txt`.
6. Copy the output file path to the clipboard with `pbcopy` when available. If clipboard copy fails, report the path.

## Output Format

The output must always follow this exact structure. Omit sections with no content entirely. Use plain text, no Markdown formatting.

```text
MEETING SUMMARY
[Project/Company] - [Other party]
YYYY-MM-DD, HH:MM
[Location or "Remote"]

Attendees:  [Name] ([Role], [Org])
            [Name] ([Role], [Org])

Absent:     [Name] ([Role], [Org]) - [reason if known]


1. [TOPIC HEADING IN CAPS]

[Prose paragraphs and/or indented bullet points. Mix as appropriate.
Keep it factual. Use direct quotes sparingly - only when the exact
wording matters.]

  - Bullet point
  - Another point


2. [NEXT TOPIC]

[Continue same pattern...]


N. NEXT STEPS

1. [Action item with owner if known]
2. [Next action item]


[Any standing notes like NDA status, follow-up meetings, etc.]
```

## Rules

- Plain `.txt`, no Markdown, no HTML.
- Section numbering is sequential: `1`, `2`, `3`, etc.
- Topic headings are ALL CAPS.
- Attendees block is aligned with spaces, not tabs.
- Prose style is factual, third person, past tense.
- No filler and no "the meeting began with" preamble.
- Include specific numbers, dates, amounts, and names mentioned.
- The last numbered section is always `NEXT STEPS`, or `DECISIONS AND NEXT STEPS` if there are few decisions.
- If the transcription is in Swedish, output in English. Meeting language does not dictate output language.
- Soft-wrap lines around 70 characters for readability.
- Use UTF-8 encoding.

## Context and Quality Rules

- Treat a MOM as a durable project record, not a raw transcript digest.
- Prefer local project terminology over phonetic transcript guesses when project context establishes the correct term.
- Use discovered roles, organizations, locations, project names, and standing notes in the header and attendee block.
- If the repo has an established meeting-doc location or naming pattern, follow it instead of defaulting to `~/Downloads`.
- Keep operationally relevant personal context, such as availability or leave timing.
- Omit sensitive personal health or family details unless the user explicitly asks to preserve them.
- Prefer concise, confident project language over repeated "X said" phrasing.
- If no relevant local context or project convention is found, use only the transcript and the default Downloads workflow.
