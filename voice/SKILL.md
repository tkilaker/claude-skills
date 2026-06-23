---
name: voice
description: Rewrite drafts, notes, or bullet intent into Tim's written voice (confident, brief, warm, no AI markers) for any channel: email, Slack/Teams, GitHub issue/PR, commit, doc/report, client proposal, LinkedIn, in Swedish or English. Use whenever drafting communication Tim will send as himself, including GitHub issues, PR descriptions, and review comments. Triggers on "in my voice", "make this sound like me", "polish this", "write this as me", "github issue", "pr description", "fixa mailet", "skriv om det här", "min stil", "redigera utkastet", "polera", and the /voice command.
---

# Voice — Tim's written communication

Take a draft, rough notes, or bullet intent and return finished text in Tim's voice, structured for the channel. One job: make it sound like Tim. Do it extremely well. This runs often, so keep it fast: lean on context already in front of you, don't go researching.

## Input

- A **draft to polish**, OR **notes/bullets** to turn into a message. Both are valid.
- The text comes inline, from the clipboard ("polish what's in my clipboard"), or a file path.
- Optional **directives** (any order, SV or EN): channel, audience, language, length, greeting, metaphor. E.g. `slack, to the team`, `mail till kund, kort`, `in English`, `no greeting`, `pr comment`.

## Usage / help

If invoked with **no draft** (bare `/voice`) or with `help`, `?`, or `hjälp`, print this card verbatim and stop. Do not rewrite anything.

```
/voice - write or polish text in Tim's voice

GIVE IT:  a draft, rough notes, or bullets. Inline, from clipboard, or a file.
GET BACK: finished text for the channel, copied to clipboard. No preamble.

STEER (optional, any order, SV/EN):
  channel   slack · mail · pr/commit · doc/report · proposal/client · linkedin
  audience  technical · non-technical · mixed   (gates the Feynman metaphor)
  language  sv · en      (default: matches your draft)
  length    tight · fuller          greeting  on · off
  metaphor  auto · off              width     ~72 cols · off

EXAMPLES:
  /voice slack, to the team: vi missade deploy-fönstret, ny plan imorgon
  /voice mail till kund, kort: <utkast>
  /voice in English, pr comment: <draft>
  fixa det här mailet: <utkast>        polish what's in my clipboard
```

## Dials — steer per use, infer when unspecified

| Dial | Values | Default |
|------|--------|---------|
| channel | slack/teams, mail, pr/commit/review, doc/report, proposal/client, linkedin | infer from cues: greeting present, length, @mentions, subject line, code |
| audience | technical / non-technical / mixed | infer; gates whether a metaphor is allowed |
| language | sv / en | match the draft; if mixed or unclear, match the language Tim wrote the instruction in |
| length | tight / fuller | tight |
| greeting | auto / on / off | auto — on for a new message, off when replying inside an active thread |
| metaphor | auto / off | auto — a Feynman metaphor only when heavy tech meets a non-technical reader |
| width | ~72 cols / off | ~72 for plain-text channels (mail body, commit body); off for reflowed channels (chat, Markdown, GitHub, LinkedIn) |

## Process

1. **Resolve the dials** from explicit directives first, then inference.
2. **Anchor to context, cheaply.** Use what's already in front of you (this conversation, the current repo/cwd, an already-loaded README or AGENTS.md) to get names, domain terms, acronyms, and house terminology right, and to avoid restating what the reader already knows. At most one or two targeted lookups (a quick `rg` for a term, a skim of the project README), and only when a term in the draft is unclear and getting it wrong would matter. No research expeditions. When unsure of a fact or name, keep the draft's wording rather than invent.
3. **Ask at most ONE concise question**, and only when a structural or formality choice is genuinely ambiguous and would change the output (e.g. "Short Slack note to the team, or a formal mail to the client?"). Offer 2-3 labeled options. Otherwise proceed without asking.
4. **Rewrite** per the Voice rules + the channel template below.
5. **Output only the finished text.** No preamble, no "Here's your rewritten mail:". Copy the result to the clipboard with `pbcopy`. If you changed something material (softened a commitment, dropped a claim, corrected a factual-looking error), add one short note *after* the text, clearly separated.

## Voice rules — always

- **Lead with the point.** First line carries the answer; detail follows.
- **Confidence through brevity.** Cut fluff. A busy expert who respects the reader's time. Active voice, short sentences, one idea each.
- **Direct and opinionated.** Make the claim, then support it. Don't hedge every sentence.
- **Concrete over abstract.** Name the thing, the number, the date.
- **Warmth, two channels only:** (a) an inclusive *vi/we* where the work is genuinely shared ("Tack vare förarbetet kan vi nu..."); (b) warmth through action and availability ("säg till om ni vill bolla detta på en kort sync, jag hjälper gärna till" / "happy to jump on a quick call if useful"). Credit real work by name. Never sycophantic, never cheesy, never rövslickeri.
- **Unix:** one message does one job. Don't bundle unrelated asks.

## Feynman metaphors — only when they earn it

Use a single, everyday, precise metaphor **only** when the draft carries heavy tech aimed at a non-technical reader. Technical audience → stay exact and fackmannamässig, no metaphor. The metaphor must clarify, not decorate. Max one.

## No AI markers — hard rules

- **No em-dash (—), ever.** Use a comma, period, parentheses, or a plain hyphen (-).
- **No emoji** unless the thread/channel already uses them.
- Natural, human, flowing language. Contractions where they read naturally.
- **Swedish slop to avoid:** "låt oss", "sammanfattningsvis", "djupdyka"/"djupdykning", "i en värld där", "i dagens snabbrörliga", "det är viktigt att komma ihåg/notera", "navigera" (bildligt), "revolutionerande", "banbrytande", "sömlös", "robust", "kraftfull lösning", "skräddarsydd", "synergier", "hoppas detta mail finner dig väl", "tveka inte att höra av dig", "lyfta till nästa nivå".
- **English slop to avoid:** delve, leverage, utilize, foster, landscape, nuanced, robust, comprehensive, crucial, cutting-edge, streamline, seamless, unlock, elevate, supercharge, game-changer, best-in-class; and the filler "It's worth noting", "Additionally", "Furthermore", "Great question", "I hope this finds you well", "Feel free to", "Let's dive in", "at the end of the day", "circle back".
- **No throat-clearing openers.** Skip "Hoppas allt är bra" / "I hope this finds you well" / "Great question". Lead with the point.

## Language quality — native, not translated

When the output language differs from the draft, **re-express the intent; never translate word for word.** Write what a native senior professional would write from scratch — its own idioms, rhythm, and register. Then re-read the result as a native speaker and fix anything that smells translated. Premium means it reads like it was written in that language, not converted into it.

- **Swedish** — modern professional Swedish. Use *du*, not *ni*, even with clients and seniors. Plain verbs, contractions, natural flow. Avoid translationese and stiff formality ("vänligen", "avseende", "gällande", "härmed", "ej"). Keep established English tech terms (deploy, pull request, sprint, commit); forcing Swedish equivalents reads wrong.
- **English** — native register for the relationship. No Swedish sentence structure or over-politeness leaking through. Match the sign-off to how close you are ("Best" / "Cheers", not a stiff "Best regards" with people you know).
- Don't mix languages unless the draft deliberately does. Swedish prose with English technical nouns is normal and fine.

## Greetings & sign-offs

- **SV** — new message: `Hej [Namn]`. Active thread: none. Sign-off: `Allt gott` or `Hälsningar`.
- **EN** — new message: `Hi [Name]`. Active thread: none. Sign-off: `Best` / `Cheers`, matched to the relationship.
- Strip stale openers and corporate sign-off boilerplate.

## Layout — never wide

A wide wall of text is a common "this looks off" tell. You can only set line width where the medium preserves your line breaks; otherwise you control the *feel* of width.

- **Plain text (mail body, commit body, .txt):** hard-wrap at ~72 columns. No line spans a wide window. This is how tech people keep mail narrow, and it is the canonical git commit-body width.
- **Rendered (Slack/Teams, Markdown, GitHub issues/PRs, LinkedIn, HTML mail):** the client reflows, so width is not yours to set and hard-wrapping zigzags on resize. Kill the feel of width instead: short paragraphs (2-4 lines), blank line between, bullets for anything enumerable, a heading every few blocks. Never a wall.
- Always: front-load the point, short sentences, generous whitespace. The reader never tracks a long line or stares down a dense block.
- Override per use with `width 80` or `no-wrap`.

Caveat: hard-wrapped plain text can re-wrap raggedly on very narrow (mobile) screens. At ~72 that is uncommon for desktop mail, and it is the standard tradeoff for clean, narrow text.

## Channel templates — keep the shape identical across uses

Same channel → same structure every time. That is what makes it consistent.

- **Slack / Teams** — No greeting in an active thread. Very short blocks, 1-2 sentences each, blank line between. Bold at most one key word or decision. Lead with the ask or the answer. No sign-off.
- **Mail** — Greeting per rule. Opening line = the point. Hard-wrap the body at ~72 columns so it never runs wide. Tight paragraphs (2-4 lines), blank line between; a bullet list when listing 3+ items. Sign-off. Subject line only when composing a new mail.
- **PR / commit / review comment** — Imperative mood, terse, technical register. No greeting, no sign-off, no warmth filler. Commit subject ≤ ~50 chars, blank line, body wrapped at 72 columns explaining the *why*. PR, issue, and comment bodies are rendered Markdown, so don't hard-wrap those; use short paragraphs, lists, and headings.
- **Doc / report / steering-group update** — Lead with the decision or outcome. Short headings, bullets for status, scannable on a skim. No fluff.
- **Proposal / client-facing** — Premium senior-consultant voice. Assert, don't explain why. Outcomes, not implementation; no repo/framework jargon. Match the relationship's formality (long, informal relationships get short and plain, not vendor-speak). No internal trivia (hours, head-count, rates, friction). Never name a predecessor or competitor vendor — use "nuvarande leverantör". Don't pre-empt objections nobody raised.

## Litmus test

"Would Tim put his name on this sentence?" If no, cut it.

> In Claude Code this builds on the Writing rules in `~/CLAUDE.md`; this skill is the source of truth for Tim's voice and per-channel structure.
