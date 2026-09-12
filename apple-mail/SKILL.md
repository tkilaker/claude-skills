---
name: apple-mail
description: "Manage Apple Mail on macOS: inspect and search inboxes, triage and archive messages, move, flag, mark read, create drafts, reply, forward, send mail, and run approved scheduled rules. Use for email, inbox, unread mail, mail organization, archive, forwarding, draft replies, sending mail, invoices, or Apple Mail automation."
---

# Apple Mail

Use the absolute-path launcher. It resolves the bundled JXA helper, so it works from any working directory.

```bash
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '<JSON request>'
```

## Operating model

- Read actions are immediate.
- Every write is a dry run unless `"apply":true` is present.
- Sending additionally requires `"confirm":"send"`.
- Every applied operation writes a JSONL audit record at `/Users/tim/Library/Application Support/apple-mail-agent/audit.jsonl` and uses the source RFC `Message-ID` to prevent a rule processing the same email twice.
- Scheduled work runs only named, enabled rules from `/Users/tim/dev/claude-skills/apple-mail/config/rules.json`. Keep that file untracked. Start from `config/rules.example.json`.

Never delete mail in an automated flow. Never enable a send rule without an exact source, recipient, sender address, and test run.

## Read and inspect

```bash
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"accounts"}'
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"list","unread":true,"limit":50}'
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"search","query":"invoice","limit":20}'
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"show","account":"Privat","mailbox":"INBOX","id":12345}'
```

## Inspect raw source, headers and links

`show` returns Mail's rendered text only: no headers, URLs stripped. Use `source` when you need headers, links or an unsubscribe target. It is a read action, no `apply` needed.

```bash
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"source","account":"Privat","mailbox":"INBOX","id":12345}'
```

Returns the normal summary plus:

- `headers`: common headers, unfolded and grouped (repeats become arrays). Add `"allHeaders":true` for every header.
- `unsubscribe.header`: URLs from `List-Unsubscribe`; `unsubscribe.oneClick` is true when the sender advertises RFC 8058.
- `unsubscribe.body`: body links that look like opt-outs, for senders with no header.
- `links` / `linkCount`: unique URLs from the text parts, MIME-decoded (multipart, base64 and quoted-printable). `"linkLimit":N` caps the list.
- `"raw":true` adds the RFC822 source, capped by `"rawLimit"` (default 20000) with `rawTruncated` and `rawLength`.

One-click unsubscribe is a plain POST, which keeps it out of Tim's Sent mail:

```bash
curl -sS -X POST -d 'List-Unsubscribe=One-Click' "$URL"
```

Prefer the header target over body links. Fetching source on a message with large attachments can exceed the 45s watchdog; raise `APPLE_MAIL_TIMEOUT_SECONDS` if needed.

## Organize mail

Inspect first, then dry-run the exact message. Re-run the same request with `"apply":true` only after reviewing the returned plan.

```bash
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"archive","account":"Privat","mailbox":"INBOX","id":12345}'
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"move","account":"Privat","mailbox":"INBOX","id":12345,"destination":"Later","apply":true}'
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"set-status","account":"Privat","mailbox":"INBOX","id":12345,"read":true,"apply":true}'
```

Use the returned `account`, `mailbox`, and numeric `id`. Re-list before acting if the message may have moved.

## Draft, forward, and send

`compose`, `reply`, and `forward` create a draft only when applied. Send requires both `"apply":true` and `"confirm":"send"`.

```bash
# Dry-run an invoice forward
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"forward","account":"Privat","mailbox":"INBOX","id":12345,"from":"tim.kilaker@livingit.se","to":["invoices@example.com"],"body":"Please process the attached invoice."}'

# Create the reviewed draft
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"forward","account":"Privat","mailbox":"INBOX","id":12345,"from":"tim.kilaker@livingit.se","to":["invoices@example.com"],"body":"Please process the attached invoice.","apply":true}'
```

Before an actual send, present recipient list, sender address, subject, and whether the original mail and attachments are preserved. Do not send payment-related mail without an explicit user instruction or an enabled rule whose `mode` is `send`.

## Rules and scheduling

Validate and dry-run before enabling a rule:

```bash
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"validate-rules","rulesPath":"/Users/tim/dev/claude-skills/apple-mail/config/rules.json"}'
/Users/tim/dev/claude-skills/apple-mail/scripts/mail '{"action":"run-rule","rulesPath":"/Users/tim/dev/claude-skills/apple-mail/config/rules.json","name":"livingit-invoice-to-kleer"}'
```

Set `"apply":true` only in the scheduler after the dry-run output is accepted. A send rule also needs `"confirm":"send"`. Review `/Users/tim/Library/Application Support/apple-mail-agent/audit.jsonl` after every run.

Rules must remain narrow: one source account/mailbox, exact approved senders, an attachment requirement for invoices, exact recipient addresses, and an explicit draft or send mode.

## Tests

Run `/Users/tim/dev/claude-skills/apple-mail/scripts/test.sh` for parser, audit, rule-schema, and live read checks. For an opt-in mutation check, set `APPLE_MAIL_TEST_ACCOUNT`, `APPLE_MAIL_TEST_MAILBOX`, and `APPLE_MAIL_TEST_MESSAGE_ID` to a dedicated test message, then run `/Users/tim/dev/claude-skills/apple-mail/scripts/integration-test.sh`. It flips that message's flag and restores it. It never sends mail.
