---
name: brain
description: Access Tim's personal knowledge base at ~/brain/. Use when asked about Tim's preferences, systems, setup, past learnings, or when asked to remember something. Triggers on "remember this", "my setup", "my preferences", "my taste", "my profile", "based on my", "use my", "apply my", "what do I use", "what did we learn", "recommend for me".
---

# Tim's Brain - Personal Knowledge Base

## Structure

```
~/brain/
├── CLAUDE.md        # Entry point - quick reference
├── profile.md       # Taste, philosophy, preferences
├── systems.md       # Hardware, software, network setup
├── learnings.md     # Discoveries from sessions (topic-indexed)
├── projects/        # Active projects
│   ├── TEMPLATE.md  # Scaffold for new projects
│   └── ...
└── scratch/         # Temp work (gitignored)
```

## Tim's Core Philosophy

**High-Performance Unix Futurist + Zero-Friction Industrial Essentialism**

- Native code over Electron/Java
- CLI/TUI, keyboard-centric
- Small tools, loosely joined
- No bloat, no magic, no over-engineering
- Plug-and-play, no tinkering
- Function over form, repairable, durable

## How to Use

### Looking Up Information

1. Read the relevant file directly:
   - Preferences/taste → `~/brain/profile.md`
   - Computer/NAS/network → `~/brain/systems.md`
   - Past discoveries → `~/brain/learnings.md`
   - Project context → `~/brain/projects/<name>/`

2. For quick context, `~/brain/CLAUDE.md` has the summary.

### Adding New Learnings

When Tim says "remember this" or you discover something worth keeping:

1. Read `~/brain/learnings.md`
2. Find or create the appropriate **topic section** (## heading):
   - Use broad categories: macOS, Hardware, Networking, Dev, Claude, Shell, etc.
   - Check existing sections first — don't create duplicates
3. Add a sub-heading with topic + date: `### Topic name (YYYY-MM-DD)`
4. Bullet points for facts, no prose
5. Format:
   ```markdown
   ## Topic Category

   ### Specific thing (YYYY-MM-DD)
   - Key point one
   - Key point two
   ```
6. Commit: `cd ~/brain && git add learnings.md && git commit -m "Learn: topic"`

**Proactive capture triggers** — consider logging a learning when:
- A non-obvious workaround is found
- A tool/config choice is made with rationale
- Something breaks unexpectedly and gets fixed
- A CLI flag or API quirk is discovered

### Working with Projects

Projects live in `~/brain/projects/`. Use `projects/TEMPLATE.md` as a scaffold for new ones.

Each project should have:
- **Status** (planning/active/paused/done)
- **Decisions table** — capture choices with rationale
- **Log** — dated entries for progress

### Updating Systems

When Tim's setup changes (new software, config, hardware):

1. Read `~/brain/systems.md`
2. Update the relevant section
3. Commit: `cd ~/brain && git add systems.md && git commit -m "Update: section name"`

## Formatting Conventions

- Markdown only
- Terse, no fluff
- Code blocks for commands/scripts
- Tables for structured data
- No emojis
