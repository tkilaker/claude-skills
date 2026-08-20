// harvest-mail.js <since-iso> [max]
// Emits JSON array of INBOX messages received after <since-iso>.
// Account is taken from DELIVERY_MAIL_ACCOUNT, default "Privat".

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
    app.includeStandardAdditions = true;

    const env = $.NSProcessInfo.processInfo.environment;
    const acctVal = env.objectForKey("DELIVERY_MAIL_ACCOUNT");
    const account = acctVal.isNil() ? "Privat" : ObjC.unwrap(acctVal);

    const since = new Date(argv[0]);
    const max = parseInt(argv[1] || "60", 10);
    const BODY_MAX = 4000;

    const inbox = resolveAccount(app, account).mailboxes.byName("INBOX");
    const msgs = inbox.messages.whose({ dateReceived: { ">": since } })();

    const out = [];
    for (let i = 0; i < msgs.length && out.length < max; i++) {
        const m = msgs[i];
        let body = "";
        try { body = m.content() || ""; } catch (e) { body = ""; }
        if (body.length > BODY_MAX) body = body.slice(0, BODY_MAX) + "\n[trunkerad]";
        let mid = "";
        try { mid = m.messageId() || ""; } catch (e) { mid = ""; }
        out.push({
            source: "mail:" + mid,
            message_id: mid,
            mailbox_id: m.id(),
            sender: m.sender(),
            subject: m.subject(),
            date: m.dateReceived().toISOString(),
            read: m.readStatus(),
            body: body
        });
    }
    return JSON.stringify(out);
}
