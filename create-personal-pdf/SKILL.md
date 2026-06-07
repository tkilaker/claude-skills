---
name: create-personal-pdf
description: Create polished, repeatable personal-style PDFs from Markdown using Pandoc, XeLaTeX, and the Eisvogel pandoc-latex-template. Use when you need to create, render, format, or refine a PDF document, report, brief, proposal, note, or handout from Markdown while preserving Tim's consistent PDF style and supporting Eisvogel/Pandoc custom template variables.
---

# Create Personal PDF

## Workflow

Use `scripts/build_pdf.py` as the default entry point. It pins the bundled
Eisvogel template and applies the personal style metadata in
`assets/styles/tim-default.yaml`.

```bash
python3 ~/.agents/skills/create-personal-pdf/scripts/build_pdf.py input.md
```

Prefer Markdown as the source. If the user provides prose, create a temporary
Markdown file in the relevant project or `~/brain/scratch/`, then render it.

## Document Defaults

Use concise, professional Markdown:

- Put document-specific metadata in YAML frontmatter when the content needs it.
- Use `title`, `subtitle`, `author`, `date`, `subject`, `keywords`, and `lang`.
- Keep headings shallow and scannable.
- Use tables for comparison, bullets for decisions, and fenced code blocks for logs.
- Avoid decorative LaTeX unless the user asks for it.

Start from `assets/metadata-template.yaml` when a new document needs metadata.

## Build Commands

Render with defaults:

```bash
python3 ~/.agents/skills/create-personal-pdf/scripts/build_pdf.py report.md
```

Set a specific output path:

```bash
python3 ~/.agents/skills/create-personal-pdf/scripts/build_pdf.py report.md -o report.pdf
```

Add a table of contents or numbered sections:

```bash
python3 ~/.agents/skills/create-personal-pdf/scripts/build_pdf.py report.md --toc --number-sections
```

Pass custom Eisvogel or Pandoc variables:

```bash
python3 ~/.agents/skills/create-personal-pdf/scripts/build_pdf.py report.md \
  --variable watermark="DRAFT" \
  --variable titlepage-color=111111 \
  --variable titlepage-rule-color=FF5A1F
```

Use an extra metadata file for project-specific overrides:

```bash
python3 ~/.agents/skills/create-personal-pdf/scripts/build_pdf.py report.md \
  --metadata-file project-pdf.yaml
```

## Custom Variables

Read `references/eisvogel-variables.md` when the user asks for a custom title
page, headers, footers, logos, backgrounds, watermarks, code block sizing,
caption behavior, table coloring, books, or other Eisvogel-specific features.

Important path rule: `titlepage-logo`, `titlepage-background`, and page
background paths are resolved by Pandoc/LaTeX from the execution directory.
Run the build script from the source document's project root or pass
`--resource-path` for normal images.

## Validation

After rendering, verify:

```bash
ls -lh output.pdf
```

For meaningful deliverables, inspect the first page visually or run:

```bash
pdfinfo output.pdf
```

If LaTeX fails because a package is missing, read the error and install the
missing TeX package. Do not switch away from the template unless the user asks.
