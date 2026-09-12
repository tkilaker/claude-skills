ObjC.import('Foundation');

const Mail = Application('Mail');
let cliArgs = [];
const fileManager = $.NSFileManager.defaultManager;

function fail(message) { throw new Error(message); }
function json(value) { return JSON.stringify(value, null, 2); }
function request() {
  if (cliArgs.length !== 1) fail('Pass exactly one JSON request argument.');
  try { return JSON.parse(cliArgs[0]); } catch (error) { fail(`Invalid JSON: ${error.message}`); }
}
function homePath() { return ObjC.unwrap($.NSHomeDirectory()); }
function defaultStateDirectory() { return `${homePath()}/Library/Application Support/apple-mail-agent`; }
function defaultRulesPath() { return `${defaultStateDirectory()}/rules.json`; }
function defaultAuditPath() { return `${defaultStateDirectory()}/audit.jsonl`; }
function stringAt(path) {
  const value = $.NSString.stringWithContentsOfFileEncodingError($(path), $.NSUTF8StringEncoding, null);
  if (!value) fail(`Cannot read ${path}`);
  return ObjC.unwrap(value);
}
function ensureDirectory(path) {
  const error = Ref();
  if (!fileManager.createDirectoryAtPathWithIntermediateDirectoriesAttributesError($(path), true, $(), error)) {
    fail(`Cannot create ${path}: ${ObjC.unwrap(error[0].localizedDescription)}`);
  }
}
function appendJsonLine(path, value) {
  const directory = path.replace(/\/[^/]+$/, '');
  ensureDirectory(directory);
  const text = `${JSON.stringify(value)}\n`;
  const handle = fileManager.fileExistsAtPath($(path))
    ? $.NSFileHandle.fileHandleForWritingAtPath($(path))
    : ($.NSFileManager.defaultManager.createFileAtPathContentsAttributes($(path), $(text).dataUsingEncoding($.NSUTF8StringEncoding), $()), null);
  if (handle) {
    handle.seekToEndOfFile;
    handle.writeData($(text).dataUsingEncoding($.NSUTF8StringEncoding));
    handle.closeFile;
  }
}
function loadJson(path) {
  try { return JSON.parse(stringAt(path)); } catch (error) { fail(`Invalid JSON in ${path}: ${error.message}`); }
}
function mailbox(accountName, mailboxName) {
  const account = Mail.accounts.byName(accountName);
  const box = account.mailboxes.byName(mailboxName);
  try { box.name(); } catch (_) { fail(`Mailbox not found: ${accountName}/${mailboxName}`); }
  return box;
}
function message(spec) {
  if (!spec.account || !spec.mailbox || !Number.isInteger(spec.id)) fail('Message actions require account, mailbox, and numeric id.');
  const result = mailbox(spec.account, spec.mailbox).messages.byId(spec.id);
  try { result.subject(); } catch (_) { fail(`Message not found: ${spec.account}/${spec.mailbox}/${spec.id}`); }
  return result;
}
function summary(item, includeContent = false) {
  const box = item.mailbox();
  const result = {
    id: item.id(), messageId: item.messageId(), account: box.account().name(), mailbox: box.name(),
    subject: item.subject(), sender: item.sender(), dateReceived: item.dateReceived(),
    read: item.readStatus(), flagged: item.flaggedStatus(), hasAttachments: item.mailAttachments().length > 0
  };
  if (includeContent) result.content = item.content();
  return result;
}
function escapeRegex(value) { return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
function splitHeaderBody(raw) {
  const match = raw.match(/\r?\n\r?\n/);
  if (!match) return {head: raw, body: ''};
  return {head: raw.slice(0, match.index), body: raw.slice(match.index + match[0].length)};
}
function parseHeaders(head) {
  const result = {};
  head.replace(/\r?\n[ \t]+/g, ' ').split(/\r?\n/).forEach(line => {
    const match = line.match(/^([A-Za-z0-9-]+):[ \t]*(.*)$/);
    if (!match) return;
    const key = match[1].toLowerCase();
    result[key] = result[key] === undefined ? match[2] : [].concat(result[key], match[2]);
  });
  return result;
}
function decodeBase64(text) {
  const data = $.NSData.alloc.initWithBase64EncodedStringOptions($(text), $.NSDataBase64DecodingIgnoreUnknownCharacters);
  if (!data) return '';
  const utf8 = $.NSString.alloc.initWithDataEncoding(data, $.NSUTF8StringEncoding);
  if (utf8) return ObjC.unwrap(utf8);
  const latin1 = $.NSString.alloc.initWithDataEncoding(data, $.NSISOLatin1StringEncoding);
  return latin1 ? ObjC.unwrap(latin1) : '';
}
function decodeQuotedPrintable(text) {
  return text.replace(/=\r?\n/g, '').replace(/=([0-9A-Fa-f]{2})/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)));
}
function decodePart(headers, body) {
  const encoding = String(headers['content-transfer-encoding'] || '').toLowerCase();
  if (encoding.includes('base64')) return decodeBase64(body);
  if (encoding.includes('quoted-printable')) return decodeQuotedPrintable(body);
  return body;
}
function textParts(raw, depth = 0) {
  const {head, body} = splitHeaderBody(raw);
  const headers = parseHeaders(head);
  const contentType = String(headers['content-type'] || 'text/plain');
  const type = contentType.toLowerCase();
  const boundary = (contentType.match(/boundary="?([^";\s]+)"?/i) || [])[1];
  if (type.startsWith('multipart/') && boundary && depth < 5) {
    return body.split(new RegExp(`--${escapeRegex(boundary)}(?:--)?[ \t]*\r?\n?`))
      .slice(1)
      .filter(chunk => chunk.trim())
      .flatMap(chunk => textParts(chunk, depth + 1));
  }
  if (!type.startsWith('text/')) return [];
  return [decodePart(headers, body)];
}
function extractLinks(text) {
  const found = text.match(/https?:\/\/[^\s"'<>)\]]+/g) || [];
  const seen = [];
  found.forEach(value => {
    const url = value.replace(/(&amp;)/g, '&').replace(/[.,;:]+$/, '');
    if (!seen.includes(url)) seen.push(url);
  });
  return seen;
}
const UNSUBSCRIBE_PATTERN = /unsub|opt[-_]?out|avregistrer|avanm[aä]l|avprenumerer|prenumeration|preferences|email[-_]?settings/i;
function unsubscribeTargets(headers, links) {
  const header = [].concat(headers['list-unsubscribe'] || []).join(', ');
  return {
    header: (header.match(/<([^>]+)>/g) || []).map(value => value.slice(1, -1)),
    oneClick: /one-click/i.test(String(headers['list-unsubscribe-post'] || '')),
    body: links.filter(url => UNSUBSCRIBE_PATTERN.test(url))
  };
}
const SUMMARY_HEADERS = [
  'date', 'from', 'reply-to', 'to', 'cc', 'subject', 'message-id', 'return-path',
  'list-id', 'list-unsubscribe', 'list-unsubscribe-post', 'content-type', 'authentication-results'
];
function pickHeaders(headers) {
  const result = {};
  SUMMARY_HEADERS.forEach(key => { if (headers[key] !== undefined) result[key] = headers[key]; });
  return result;
}
function inspectSource(spec, item) {
  const raw = item.source();
  const headers = parseHeaders(splitHeaderBody(raw).head);
  const links = extractLinks(textParts(raw).join('\n'));
  const linkLimit = Number.isInteger(spec.linkLimit) ? spec.linkLimit : 50;
  const result = summary(item);
  result.headers = spec.allHeaders === true ? headers : pickHeaders(headers);
  result.unsubscribe = unsubscribeTargets(headers, links);
  result.linkCount = links.length;
  result.links = links.slice(0, linkLimit);
  if (spec.raw === true) {
    const rawLimit = Number.isInteger(spec.rawLimit) ? spec.rawLimit : 20000;
    result.raw = raw.slice(0, rawLimit);
    result.rawTruncated = raw.length > rawLimit;
    result.rawLength = raw.length;
  }
  return result;
}
function requireApply(spec) { if (spec.apply !== true) return false; return true; }
function requireSendConfirmation(spec) { if (spec.confirm !== 'send') fail('Sending requires confirm:"send".'); }
function validateSender(sender) {
  if (!Mail.accounts().some(account => account.emailAddresses().includes(sender))) fail(`Sender is not configured in Apple Mail: ${sender}`);
}
function addRecipients(draft, type, addresses) {
  if (!Array.isArray(addresses) || addresses.length === 0 || !addresses.every(value => typeof value === 'string' && value.includes('@'))) fail(`${type} must contain valid email addresses.`);
  const property = `${type}Recipients`;
  const constructor = type === 'to' ? Mail.ToRecipient : type === 'cc' ? Mail.CcRecipient : Mail.BccRecipient;
  addresses.forEach(address => draft[property].push(constructor({address})));
}
function audit(spec, item, outcome, extra = {}) {
  auditRecord(spec, {
    messageId: item.messageId(), account: item.mailbox().account().name(), mailbox: item.mailbox().name(), subject: item.subject()
  }, outcome, extra);
}
function auditRecord(spec, message, outcome, extra = {}) {
  appendJsonLine(spec.auditPath || defaultAuditPath(), {
    at: new Date().toISOString(), rule: spec.rule || null, action: spec.action,
    ...message, outcome, ...extra
  });
}
function processed(spec, item) {
  const path = spec.auditPath || defaultAuditPath();
  if (!fileManager.fileExistsAtPath($(path))) return false;
  const key = item.messageId();
  return stringAt(path).split('\n').some(line => {
    try { const row = JSON.parse(line); return row.rule === spec.rule && row.messageId === key && row.outcome === 'applied'; } catch (_) { return false; }
  });
}
function plan(action, item, details = {}) { return {status: 'dry-run', action, message: summary(item), ...details}; }
function applyMove(spec, source, destinationName) {
  const destination = mailbox(spec.account, destinationName);
  if (!requireApply(spec)) return plan(spec.action, source, {destination: `${spec.account}/${destinationName}`});
  const record = {
    messageId: source.messageId(), account: source.mailbox().account().name(), mailbox: source.mailbox().name(), subject: source.subject()
  };
  Mail.move(source, {to: destination});
  auditRecord(spec, record, 'applied', {destination: `${spec.account}/${destinationName}`});
  return {status: 'applied', action: spec.action, id: spec.id, destination: `${spec.account}/${destinationName}`};
}
function applyStatus(spec, source) {
  if (!requireApply(spec)) return plan(spec.action, source, {read: spec.read, flagged: spec.flagged});
  if (typeof spec.read === 'boolean') source.readStatus = spec.read;
  if (typeof spec.flagged === 'boolean') source.flaggedStatus = spec.flagged;
  audit(spec, source, 'applied', {read: source.readStatus(), flagged: source.flaggedStatus()});
  return {status: 'applied', action: spec.action, id: spec.id, read: source.readStatus(), flagged: source.flaggedStatus()};
}
function createOutgoing(spec, original) {
  if (spec.from) validateSender(spec.from);
  if (!requireApply(spec)) return plan(spec.action, original || { mailbox: () => ({account: () => ({name: () => null}), name: () => null}), id: () => null, messageId: () => null, subject: () => spec.subject || '', sender: () => null, dateReceived: () => null, readStatus: () => null, flaggedStatus: () => null, mailAttachments: () => [] }, {from: spec.from || null, to: spec.to || [], send: spec.send === true});
  let draft;
  if (spec.action === 'compose') {
    draft = Mail.OutgoingMessage({subject: spec.subject || '', content: spec.body || '', visible: false});
    Mail.outgoingMessages.push(draft);
  } else {
    draft = spec.action === 'reply' ? Mail.reply(original, {withOpeningWindow: false}) : Mail.forward(original, {withOpeningWindow: false});
    draft.visible = false;
    if (spec.body) draft.content = `${spec.body}\n\n${draft.content()}`;
  }
  if (spec.from) draft.sender = spec.from;
  if (spec.action === 'compose' || spec.action === 'forward') {
    addRecipients(draft, 'to', spec.to);
    if (spec.cc) addRecipients(draft, 'cc', spec.cc);
    if (spec.bcc) addRecipients(draft, 'bcc', spec.bcc);
  }
  if (spec.send === true) {
    requireSendConfirmation(spec);
    Mail.send(draft);
    if (original) audit(spec, original, 'applied', {delivery: 'sent', to: spec.to || []});
    return {status: 'sent', subject: draft.subject(), sender: draft.sender()};
  }
  Mail.save(draft);
  if (original) audit(spec, original, 'applied', {delivery: 'draft', to: spec.to || []});
  return {status: 'draft-created', subject: draft.subject(), sender: draft.sender()};
}
function validateRule(rule) {
  const errors = [];
  if (!rule || typeof rule !== 'object') errors.push('rule must be an object');
  if (!rule.name) errors.push('rule.name is required');
  if (!rule.source || !rule.source.account || !rule.source.mailbox) errors.push('rule.source.account and rule.source.mailbox are required');
  if (!rule.match || !Array.isArray(rule.match.senders) || rule.match.senders.length === 0) errors.push('rule.match.senders must contain exact addresses');
  if (!rule.action || !['archive', 'move', 'forward'].includes(rule.action.type)) errors.push('rule.action.type must be archive, move, or forward');
  if (rule.action && rule.action.type === 'move' && !rule.action.destination) errors.push('move needs action.destination');
  if (rule.action && rule.action.type === 'forward') {
    if (!rule.action.from || !Array.isArray(rule.action.to) || rule.action.to.length === 0) errors.push('forward needs action.from and action.to');
    if (!['draft', 'send'].includes(rule.action.mode)) errors.push('forward needs action.mode draft or send');
  }
  return errors;
}
function matchingMessages(rule) {
  const senders = rule.match.senders.map(value => value.toLowerCase());
  return mailbox(rule.source.account, rule.source.mailbox).messages().filter(item => {
    const sender = item.sender().toLowerCase();
    const senderMatch = senders.some(value => sender === value || sender.includes(`<${value}>`));
    const subjectMatch = !rule.match.subjectIncludes || rule.match.subjectIncludes.every(value => item.subject().toLowerCase().includes(value.toLowerCase()));
    const attachmentMatch = rule.match.hasAttachments !== true || item.mailAttachments().length > 0;
    return senderMatch && subjectMatch && attachmentMatch;
  });
}
function runRule(spec) {
  const path = spec.rulesPath || defaultRulesPath();
  const config = loadJson(path);
  if (config.version !== 1 || !Array.isArray(config.rules)) fail('Rules config must contain version: 1 and rules: [].');
  const rule = config.rules.find(value => value.name === spec.name);
  if (!rule) fail(`Rule not found: ${spec.name}`);
  const errors = validateRule(rule);
  if (errors.length) fail(`Invalid rule ${rule.name}: ${errors.join('; ')}`);
  if (!rule.enabled) return {status: 'disabled', rule: rule.name};
  const source = matchingMessages(rule);
  const results = [];
  for (const item of source) {
    const operation = { ...spec, ...rule.source, rule: rule.name, id: item.id(), action: rule.action.type, auditPath: spec.auditPath };
    if (processed(operation, item)) { results.push({status: 'skipped', reason: 'already-processed', message: summary(item)}); continue; }
    if (rule.action.type === 'archive') results.push(applyMove(operation, item, 'Archive'));
    else if (rule.action.type === 'move') results.push(applyMove(operation, item, rule.action.destination));
    else results.push(createOutgoing({ ...operation, from: rule.action.from, to: rule.action.to, body: rule.action.body || '', send: rule.action.mode === 'send' }, item));
  }
  return {status: spec.apply === true ? 'applied' : 'dry-run', rule: rule.name, matched: source.length, results};
}
function execute() {
  const spec = request();
  if (spec.action === 'paths') return {rulesPath: defaultRulesPath(), auditPath: defaultAuditPath()};
  if (spec.action === 'audit-healthcheck') {
    const auditPath = spec.auditPath || defaultAuditPath();
    appendJsonLine(auditPath, {at: new Date().toISOString(), action: 'healthcheck', outcome: 'ok'});
    return {status: 'ok', auditPath};
  }
  if (spec.action === 'accounts') return Mail.accounts().map(account => ({account: account.name(), emailAddresses: account.emailAddresses(), mailboxes: account.mailboxes().map(box => box.name())}));
  if (spec.action === 'list' || spec.action === 'search') {
    const limit = Number.isInteger(spec.limit) ? spec.limit : 20;
    let items = spec.account && spec.mailbox ? mailbox(spec.account, spec.mailbox).messages() : Mail.inbox.messages();
    if (spec.unread === true) items = items.filter(item => !item.readStatus());
    if (spec.action === 'search') {
      if (!spec.query) fail('Search requires query.');
      const query = spec.query.toLowerCase();
      items = items.filter(item => `${item.subject()} ${item.sender()}`.toLowerCase().includes(query));
    }
    return items.slice(0, limit).map(item => summary(item));
  }
  if (spec.action === 'show') return summary(message(spec), true);
  if (spec.action === 'source') return inspectSource(spec, message(spec));
  if (spec.action === 'archive') return applyMove(spec, message(spec), 'Archive');
  if (spec.action === 'move') { if (!spec.destination) fail('Move requires destination.'); return applyMove(spec, message(spec), spec.destination); }
  if (spec.action === 'set-status') return applyStatus(spec, message(spec));
  if (['compose', 'reply', 'forward'].includes(spec.action)) return createOutgoing(spec, spec.action === 'compose' ? null : message(spec));
  if (spec.action === 'validate-rules') {
    const config = loadJson(spec.rulesPath || defaultRulesPath());
    const errors = config.version === 1 && Array.isArray(config.rules) ? config.rules.flatMap(validateRule) : ['Rules config must contain version: 1 and rules: [].'];
    return {valid: errors.length === 0, errors, rules: config.rules ? config.rules.map(rule => ({name: rule.name, enabled: rule.enabled === true})) : []};
  }
  if (spec.action === 'run-rule') return runRule(spec);
  fail(`Unknown action: ${spec.action}`);
}
function run(argv) { cliArgs = argv; return json(execute()); }
