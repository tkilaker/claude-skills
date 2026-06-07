# Eisvogel Variables

Pinned template: Eisvogel 3.4.0 from Wandmalfarbe/pandoc-latex-template.
Source: https://github.com/Wandmalfarbe/pandoc-latex-template
Release: https://github.com/Wandmalfarbe/pandoc-latex-template/releases/tag/v3.4.0

Use these through YAML frontmatter, `--metadata-file`, or `--variable KEY=VALUE`.
Keep Eisvogel title-page hex colors without `#`. Hyperref colors such as
`linkcolor`, `urlcolor`, and `toccolor` should be defined LaTeX color names.

## Common Document Metadata

- `title`
- `subtitle`
- `author`
- `date`
- `subject`
- `keywords`
- `lang`
- `papersize`
- `fontsize`
- `geometry`
- `colorlinks`
- `linkcolor`
- `urlcolor`
- `toccolor`

## Title Page

- `titlepage`: enable title page with `true`.
- `titlepage-color`: background color, for example `"111111"`.
- `titlepage-text-color`: text color.
- `titlepage-rule-color`: accent rule color.
- `titlepage-rule-height`: rule height in points.
- `titlepage-logo`: logo path. Resolve from the Pandoc execution directory.
- `logo-width`: logo width with a TeX unit, for example `35mm`.
- `titlepage-background`: full-page title background path.

## Backgrounds

- `page-background`: background image for each page.
- `page-background-opacity`: opacity, default is `0.2`.

## Headers And Footers

- `disable-header-and-footer`: disable all headers and footers.
- `header-left`
- `header-center`
- `header-right`
- `footer-left`
- `footer-center`
- `footer-right`

Defaults from the template use title, date, author, and page number when these
fields are not explicitly set.

## Tables, Figures, And Captions

- `caption-justification`: caption alignment, commonly `raggedright`.
- `float-placement-figure`: figure placement, for example `H` or `htbp`.
- `table-use-row-colors`: enable alternating row color for tables.

## Code Blocks

- `code-block-font-size`: LaTeX font size command, for example `\small` or `\footnotesize`.
- `listings-disable-line-numbers`: disable line numbers when listings are used.
- `listings-no-page-break`: avoid page breaks inside listings.

## Books And Long Documents

- `book`: typeset as book.
- `first-chapter`: first chapter number.
- `toc-own-page`: start content on a new page after the table of contents.

## Special Effects

- `watermark`: repeat a text watermark on each page.
- `footnotes-pretty`: improve footnote formatting.
- `footnotes-disable-backlinks`: disable footnote backlinks.

`watermark` requires the LaTeX package `draftwatermark`.

## Notes

The Eisvogel README says the single-file `eisvogel.latex` is distributed in
release archives, while the Git repository contains the split source template.
This skill bundles the released single-file template to keep builds stable.
