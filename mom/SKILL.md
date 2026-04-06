---
name: mom
description: Generate standardized Minutes of Meeting (MOM) from raw meeting transcription. Triggers on "meeting summary", "minutes of meeting", "MOM", "summarize meeting", "mötessammanfattning", "mötesprotokoll".
---

# Minutes of Meeting Generator

Generate a standardized MOM .txt file from a raw meeting transcription and optional context.

## Input

The user provides:
1. **Transcription** - raw text file path, pasted text, or reference to a file
2. **Context** (optional) - background info, project details, attendee roles, etc.

If the user doesn't specify attendees or context, extract what you can from the transcription itself.

## Process

1. Read the full transcription (use an Agent for large files)
2. Extract: attendees, topics discussed, decisions, action items, key quotes
3. Organize into the standard format below
4. Write to `~/Downloads/Meeting Summary YYYY-MM-DD.txt`
5. Copy the file path to clipboard

## Output Format

The output must ALWAYS follow this exact structure. Sections with no content should be omitted entirely. Plain text, no markdown formatting.

```
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

- Plain .txt, no markdown, no HTML
- Section numbering: 1, 2, 3... Sequential
- Topic headings: ALL CAPS
- Attendees block: aligned with spaces, not tabs
- Prose style: factual, third person, past tense
- No filler, no "the meeting began with..." preamble
- Include specific numbers, dates, amounts mentioned
- Last numbered section is always NEXT STEPS (or DECISIONS AND NEXT STEPS if few decisions)
- If transcription is in Swedish, output in English. Meeting language doesn't dictate output language.
- Line width: soft-wrap around 70 characters for readability
- Encoding: UTF-8
