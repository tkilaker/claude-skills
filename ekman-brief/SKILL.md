---
name: ekman-brief
description: One-page PDF brief to Axel (or another Ekman reader) in Ekman Intelligence style, with the fixed header. Use when Tim wants to explain a change, decision, cost or result to Axel as a PDF, or says brief, uppdatering till Axel, PDF till Axel.
---

# Ekman brief

A brief is one A4 page a non-developer reads in two minutes and can act on. The header, fonts and colours are fixed in `brief.css` and `render.sh`; each brief only writes its body.

1. **Gather the facts** from the conversation: what changed, why, the evidence (before and after numbers with their measurement windows), the cost, what is left. A number without its window or source stays out.
2. **Write the body** as an HTML fragment in the session's scratchpad, starting from `examples/2026-10-01-storre-server.html`. Swedish, `voice` rules, du-form. Shape, top to bottom:
   - `h1`: the outcome as a sentence, not a topic.
   - `.lead`: two sentences, the result and when.
   - `.ask`: what the reader needs to do. "Inget, för kännedom" is a valid answer; the box is always there.
   - `.kpis`: three numbers. Benefits in blue; the price of the change goes in `.kpi.cost`.
   - Then why, the evidence (`.pair` bars for the one or two numbers that matter most, a table for the rest), cost, next step.
   - `footer`: source of the numbers and how long they cover.
   Plain words over jargon: "anrop" not "request", "serverfel" not "5xx", no SKU without saying what it means.
3. **Render**: `~/dev/claude-skills/ekman-brief/render.sh body.html ~/Downloads/<slug>.pdf --to Axel --kind Uppdatering`. `--date` defaults to today in Swedish.
4. **Look at the preview PNG** it writes. Done when the page is one page, nothing overlaps, every bar matches its number (width = value / largest value × 85 %), and every claim in the body is true at render time. Over one page: cut copy, keep the type sizes.
5. `open` the PDF.

New components go in `brief.css`, so the next brief gets them too.
