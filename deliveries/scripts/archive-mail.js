// archive-mail.js <mailbox_id> [mailbox_id ...]
// Marks the given INBOX messages as read and moves them to Archive.
// Never deletes. Ids come from harvest-mail.js (field "mailbox_id").
// Account from DELIVERY_MAIL_ACCOUNT, default "Privat".

// Resolves the mail account: exact name first, then any account with an iCloud address.
function resolveAccount(app, name) {
    try {
        const a = app.accounts.byName(name);
        a.name();
        return a;
    } catch (e) {}
    const accts = app.accounts();
    for (let i = 0; i < accts.length; i++) {
        let addrs = [];
        try { addrs = accts[i].emailAddresses(); } catch (e2) {}
        if (addrs.join(",").indexOf("icloud.com") !== -1) return accts[i];
    }
    throw new Error("Hittar inget mail-konto som matchar '" + name + "'");
}

function run(argv) {
    const app = Application("Mail");

    const env = $.NSProcessInfo.processInfo.environment;
    const acctVal = env.objectForKey("DELIVERY_MAIL_ACCOUNT");
    const account = acctVal.isNil() ? "Privat" : ObjC.unwrap(acctVal);

    const acct = resolveAccount(app, account);
    const inbox = acct.mailboxes.byName("INBOX");
    const archive = acct.mailboxes.byName("Archive");

    const moved = [];
    const missing = [];

    argv.forEach(function (raw) {
        const id = parseInt(raw, 10);
        if (isNaN(id)) { missing.push(raw); return; }
        const hits = inbox.messages.whose({ id: id })();
        if (hits.length === 0) { missing.push(id); return; }
        const m = hits[0];
        try { m.readStatus = true; } catch (e) {}
        try {
            app.move(m, { to: archive });
            moved.push(id);
        } catch (e) {
            missing.push(id);
        }
    });

    return JSON.stringify({ moved: moved, missing: missing });
}
