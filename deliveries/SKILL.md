---
name: deliveries
description: Bevakar all orderrelaterad kommunikation (mail + SMS), håller state per leverans, lägger påminnelser för avhämtning och larmar om något inte kommer fram. Triggers on "leveranser", "paket", "mina beställningar", "delivery-watch", "vad väntar jag på".
---

# Leveransbevakning

Ett pass läser ny mail och nya SMS, uppdaterar leveransstate, utför åtgärder och arkiverar behandlad mail. Körs schemalagt på Mac Mini via `~/bin/delivery-watch`, men kan köras manuellt var som helst.

## Config

| Env | Default | Betydelse |
|-----|---------|-----------|
| `DELIVERY_MAIL_ACCOUNT` | `Privat` | Mail-konto. Heter `tkilaker@icloud.com` på mbp, `Privat` på mini. |
| `DELIVERY_STATE_DIR` | `~/dev/brain/projects/deliveries` | State och logg. |
| `DELIVERY_LIST` | `Life Hub 🎯` | Reminders-lista. Matcha på prefix `Life Hub` om namnet inte träffar exakt. |
| `DELIVERY_NTFY` | `https://ntfy.sh/tim-claude-7k9x2m` | Notiskanal. |
| `DELIVERY_DRY_RUN` | tom | `1` = utför inga sidoeffekter, skriv bara ut vad som skulle hända. |
| `DELIVERY_SINCE` | tom | ISO-tid eller `30d`. Överstyr `last_run` för backfill. |

Skripten ligger i `~/dev/claude-skills/deliveries/scripts/` (samma katalog som denna fil). Använd den sökvägen rakt av.

## State

`$DELIVERY_STATE_DIR/state.json`:

```json
{
  "last_run": "2026-08-20T09:07:00Z",
  "deliveries": [ { …post… } ],
  "seen": ["mail:<message-id>", "sms:48896"]
}
```

En post:

```json
{
  "id": "amazon-402-1234567",
  "merchant": "Amazon",
  "items": "USB-C-hubb",
  "order_ref": "402-1234567",
  "ordered": "2026-08-14",
  "carrier": "PostNord",
  "tracking": "003701234567890",
  "eta": "2026-08-20",
  "status": "shipped",
  "pickup": "ICA Maxi Malmö",
  "pickup_code": "482913",
  "pickup_deadline": "2026-08-27",
  "return_by": "2026-09-13",
  "sources": ["mail:…", "sms:48896"],
  "notified": ["shipped"],
  "reminder_id": null,
  "last_event": "2026-08-19 Skickad från terminal Malmö"
}
```

`seen` håller bara de senaste ~400 källorna, klipp äldre. Avslutade poster flyttas till `closed.jsonl`, en rad per post. `log.md` är den läsbara händelseloggen.

Statusar: `ordered` → `shipped` → `out_for_delivery` → `ready_for_pickup` → `delivered` → `closed`. Plus `overdue` som sätts vid sidan av, och `unknown` när mailet är orderrelaterat men inget går att slå fast.

## Körsekvens

1. Läs `state.json`. Saknas den, skapa `{"last_run": null, "deliveries": [], "seen": []}`.
2. Bestäm fönster: `DELIVERY_SINCE` om satt, annars `last_run` minus 24 h marginal, annars 7 dagar bakåt.
3. Harvesta:
   ```bash
   osascript -l JavaScript ~/dev/claude-skills/deliveries/scripts/harvest-mail.js "$SINCE_ISO" 60
   ~/dev/claude-skills/deliveries/scripts/harvest-sms.sh "$SINCE_ISO" 80
   ```
4. Släng allt vars `source` redan finns i `seen`.
5. Klassa varje post: orderrelaterad eller inte. Se nedan.
6. För varje orderrelaterad post: extrahera fälten, matcha mot befintlig leverans, uppdatera eller skapa.
7. Räkna fram förseningar över hela `deliveries`, även poster som inte fick ny inkommande post detta pass.
8. Utför åtgärder.
9. Arkivera mail som tolkades och sparades:
   ```bash
   osascript -l JavaScript ~/dev/claude-skills/deliveries/scripts/archive-mail.js <mailbox_id> [...]
   ```
10. Skriv state atomiskt (`tmp` + `mv`), appenda `log.md`, sätt `last_run` till passets starttid.

## Klassning

Orderrelaterat är allt som rör en vara Tim beställt eller returnerar: orderbekräftelse, betalningsbekräftelse kopplad till en order, fraktbesked, avi, avhämtningsnotis, leveransbekräftelse, förseningsbesked, returetikett, återbetalning.

Inte orderrelaterat, rör aldrig: nyhetsbrev och kampanjmail även från handlare där Tim har ordrar, prenumerationskvitton utan fysisk leverans, kalendernotiser, bank- och myndighetsmail, biblioteksmail, personliga meddelanden. Ett kampanjmail från Amazon är inte en order.

Är du osäker: klassa som icke-orderrelaterat. Falska positiver flyttar mail Tim ville ha kvar i inkorgen.

## Matchning

Matcha ny information mot befintlig leverans i denna ordning: `order_ref` → `tracking` → `merchant` + liknande artikel inom 30 dagar. Ingen träff ger ny post. `id` byggs som `<merchant-slug>-<order_ref eller tracking>`.

En order kan bli flera leveranser (delleverans). Skapa då en post per kolli och sätt samma `order_ref`.

## Åtgärder

| Händelse | Åtgärd |
|----------|--------|
| Ny order | Spara tyst. Ingen notis, Tim vet att han beställt. |
| Skickad, ETA satt eller ändrad | Spara. Ingen notis. |
| `ready_for_pickup` | Reminder + ntfy. |
| `delivered` hem eller i postlåda | ntfy. Sätt `closed`. |
| Ohämtad ≥ 4 dagar efter avisering | ntfy med skarpare ton, uppdatera befintlig reminder. Ombudet returnerar snart. |
| `overdue` | ntfy + reminder `Kolla leverans: <merchant> <order_ref>`. |
| Retur påbörjad, `return_by` känt | Reminder 3 dagar före deadline. |
| Återbetalning bekräftad | ntfy. Sätt `closed`. |

Förseningsregler, kör mot alla öppna poster:

- `eta` passerad med mer än 1 dygn och status inte `delivered`/`closed` → `overdue`
- `shipped` utan `eta` i mer än 7 dagar → `overdue`
- `ordered` utan fraktbesked i mer än 10 dagar → `overdue`

Reminder för avhämtning:

```bash
reminders add "$DELIVERY_LIST" "Hämta: <artiklar> – <ombud>" \
  --due-date "today 17:00" \
  --notes "Kod: <pickup_code>
Kolli: <tracking> (<carrier>)
Sista dag: <pickup_deadline>" \
  --format json
```

Spara `externalId` ur JSON-svaret som `reminder_id`. Finns redan ett `reminder_id` för posten, skapa inte ett till.

## Notiser

Max en ntfy per pass. Slå ihop alla händelser till ett meddelande. Inga händelser: skicka ingenting, logga bara.

```bash
curl -s -H "Title: Leveranser" -H "Tags: package" \
  -d "<rad per händelse>" "$DELIVERY_NTFY"
```

Radform: `✅ Hämta hos ICA Maxi: USB-C-hubb (kod 482913)`, `📦 Levererat: Zalando-paketet`, `⚠️ Försenat: Amazon 402-1234567, ETA var 2026-08-18`.

## Säkerhet

- Mail flyttas, raderas aldrig. Bara `Archive` på samma konto.
- Arkivera bara mail som faktiskt tolkades och skrevs till state. Blev något osäkert, låt mailet ligga.
- SMS rörs aldrig, bara läses.
- `seen` gör passen idempotenta. `notified` hindrar dubbelnotiser, `reminder_id` hindrar dubbla påminnelser.
- Skriv aldrig state innan åtgärderna är gjorda, och skriv atomiskt.
- Är `DELIVERY_DRY_RUN=1`: skriv ut planerade åtgärder till stdout, rör inte mail, reminders, ntfy eller state.

## Personlig integritet

`harvest-sms.sh` filtrerar bort svenska mobilnummer och Apple ID-adresser i SQL, så personliga konversationer lämnar aldrig maskinen. Bara kortnummer och alfanumeriska avsändare (PostNord, Bring, DHL, Instabox, Budbee, Zalando) kommer med. Sänk aldrig det filtret i schemalagd drift.

## Manuell körning

```bash
DELIVERY_DRY_RUN=1 DELIVERY_SINCE=30d ~/bin/delivery-watch   # se vad den skulle göra
~/bin/delivery-watch                                          # ett skarpt pass
```

Frågar Tim "vad väntar jag på", läs `state.json` och svara ur den. Kör inget pass om han bara frågar.
