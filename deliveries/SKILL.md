---
name: deliveries
description: Bevakar all orderrelaterad kommunikation (mail + SMS), håller state per leverans, lägger påminnelser för avhämtning och larmar om något inte kommer fram. Triggers on "leveranser", "paket", "mina beställningar", "delivery-watch", "vad väntar jag på".
---

# Leveransbevakning

Ett pass läser ny mail och nya SMS, uppdaterar leveransstate, utför åtgärder och arkiverar behandlad mail. Körs schemalagt på Mac Mini via `~/bin/delivery-watch`, men kan köras manuellt var som helst.

## Parametrar

Wrappern `delivery-watch` skickar in alla parametrar i prompten. **Härled dem aldrig om, läs inga env-variabler, gissa inget tidsfönster.**

| Parameter | Betydelse |
|-----------|-----------|
| `MODE` | `DRY_RUN=1` eller `DRY_RUN=0`. Se stoppregeln nedan. |
| `SINCE` | ISO-tid. Harvesta allt efter denna tidpunkt, inget annat fönster. |
| `RUN_START` | Sätt `last_run` till detta värde när passet är klart. |
| `STATE_DIR` | Katalog för `state.json`, `closed.jsonl`, `log.md`. |
| `MAIL_ACCOUNT` | Mail-konto. Redan exporterat som `DELIVERY_MAIL_ACCOUNT` till skripten. |
| `REMINDER_LIST` | Reminders-lista. |
| `NTFY` | Notis-URL. |

Kommer prompten utan parametrar (Tim körde skillen för hand): fråga vad han vill, kör inget skarpt pass oombedd.

### Stoppregel för torra pass

Är `MODE` `DRY_RUN=1` gäller detta utan undantag:

- skriv inte `state.json`, `closed.jsonl` eller `log.md`
- skapa, ändra eller ta bort inga reminders
- flytta ingen mail
- skicka ingen ntfy
- committa och pusha ingenting

Skriv bara ut vad passet skulle ha gjort. Ett torrt pass som ändrar något är ett fel, inte en hjälpsamhet.

Skripten ligger i `~/dev/claude-skills/deliveries/scripts/` (samma katalog som denna fil). Använd den sökvägen rakt av.

## State

`$STATE_DIR/state.json`:

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
  "ready_since": "2026-08-20",
  "return_by": "2026-09-13",
  "sources": ["mail:…", "sms:48896"],
  "notified": ["shipped"],
  "reminder_id": null,
  "last_event": "2026-08-19 Skickad från terminal Malmö"
}
```

Alla tidsstämplar i state är UTC med `Z`, aldrig lokal tid. `seen` håller bara de senaste ~400 källorna, klipp äldre. Avslutade poster flyttas till `closed.jsonl`, en rad per post. `log.md` är den läsbara händelseloggen.

Sätt `ready_since` till aviseringsdatumet när status blir `ready_for_pickup`. Utan det datumet går ohämtad-regeln inte att köra, och paket ruttnar hos ombudet utan eskalering.

Statusar: `ordered` → `shipped` → `out_for_delivery` → `ready_for_pickup` → `delivered` → `closed`. Plus `overdue` som sätts vid sidan av, och `unknown` när mailet är orderrelaterat men inget går att slå fast.

## Körsekvens

1. Läs `$STATE_DIR/state.json`. Wrappern har redan skapat den om den saknades.
2. Fönstret är `SINCE` ur prompten. Räkna inte om det.
3. Harvesta:
   ```bash
   osascript -l JavaScript ~/dev/claude-skills/deliveries/scripts/harvest-mail.js "<SINCE>" 60
   ~/dev/claude-skills/deliveries/scripts/harvest-sms.sh "<SINCE>" 80
   ```
4. Läs av avbockade påminnelser innan något annat bedöms:
   ```bash
   reminders show "<REMINDER_LIST>" --only-completed --format json | jq -r '.[].externalId'
   reminders show "<REMINDER_LIST>" --format json | jq -r '.[].externalId'
   ```
   Har en öppen leverans ett `reminder_id` som ligger i den avbockade listan, eller som inte finns i någon av listorna alls (påminnelsen är raderad), är den hämtad. Sätt `delivered`, flytta till `closed.jsonl`, logga. Skicka ingen ntfy, Tim vet att han hämtade den.
5. Släng allt vars `source` redan finns i `seen`.
6. Klassa varje post: orderrelaterad eller inte. Se nedan.
7. För varje orderrelaterad post: extrahera fälten, matcha mot befintlig leverans, uppdatera eller skapa.
8. Räkna fram förseningar över hela `deliveries`, även poster som inte fick ny inkommande post detta pass.
9. Utför åtgärder.
10. Arkivera mail som tolkades och sparades:
   ```bash
   osascript -l JavaScript ~/dev/claude-skills/deliveries/scripts/archive-mail.js <mailbox_id> [...]
   ```
11. Skriv state atomiskt (`tmp` + `mv`, validera JSON före flytt), appenda `log.md`, sätt `last_run` till `RUN_START`. Ligger `STATE_DIR` i brain: committa och pusha enligt brains vanliga regler.

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
| Ohämtad ≥ 4 dagar räknat från `ready_since` | ntfy med skarpare ton, uppdatera befintlig reminder. Ombudet returnerar snart. |
| `overdue` | ntfy alltid. Reminder `Kolla leverans: <merchant> <order_ref>` bara när det finns något konkret att göra: kolli-id, ombud eller orderref att slå upp. Saknas allt sådant räcker ntfy, en reminder utan handling är brus. |
| Retur påbörjad, `return_by` känt | Reminder 3 dagar före deadline. |
| Återbetalning bekräftad | ntfy. Sätt `closed`. |

Förseningsregler, kör mot alla öppna poster:

- `eta` passerad med mer än 1 dygn och status inte `delivered`/`closed` → `overdue`
- `shipped` utan `eta` i mer än 7 dagar → `overdue`
- `ordered` utan fraktbesked i mer än 10 dagar → `overdue`

Reminder för avhämtning:

```bash
reminders add "$REMINDER_LIST" "Hämta: <artiklar> – <ombud>" \
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
  -d "<rad per händelse>" "$NTFY"
```

Radform: `✅ Hämta hos ICA Maxi: USB-C-hubb (kod 482913)`, `📦 Levererat: Zalando-paketet`, `⚠️ Försenat: Amazon 402-1234567, ETA var 2026-08-18`.

## Säkerhet

- Mail flyttas, raderas aldrig. Bara `Archive` på samma konto.
- Arkivera bara mail som faktiskt tolkades och skrevs till state. Blev något osäkert, låt mailet ligga.
- SMS rörs aldrig, bara läses.
- `seen` gör passen idempotenta. `notified` hindrar dubbelnotiser, `reminder_id` hindrar dubbla påminnelser.
- Skriv aldrig state innan åtgärderna är gjorda, och skriv atomiskt.
- Är `MODE` `DRY_RUN=1`: följ stoppregeln överst. Inga sidoeffekter, punkt.

## Personlig integritet

`harvest-sms.sh` filtrerar bort svenska mobilnummer och Apple ID-adresser i SQL, så personliga konversationer lämnar aldrig maskinen. Bara kortnummer och alfanumeriska avsändare (PostNord, Bring, DHL, Instabox, Budbee, Zalando) kommer med. Sänk aldrig det filtret i schemalagd drift.

## Stänga en leverans

Tre vägar, alla giltiga:

1. **Bocka av påminnelsen i Reminders.** Nästa pass läser av det och stänger posten. Detta är normalvägen, Tim behöver inte göra något annat.
2. **Säga det till en Claude-session**: "jag hämtade LAMPAN-paketet". Uppdatera state direkt, bocka av påminnelsen med `reminders complete`, flytta till `closed.jsonl`.
3. **Poster utan påminnelse** (försenade utan spårnummer) stängs bara på tillsägelse eller när ett mail bekräftar leverans eller återbetalning.

Stäng aldrig en post enbart för att den är gammal. En obekräftad leverans som tystnar är precis det som ska synas.

## Rätta och förbättra

Säger Tim att något är fel eller borde göras annorlunda, avgör först vilken av två saker det är.

**Fel i sakuppgifter** — fel handlare, fel matchning, dubblett, redan hämtat, fel innehåll. Rätta `state.json` direkt: läs, ändra, skriv atomiskt, committa. Slå ihop dubbletter genom att behålla den post som har mest ifyllt, slå ihop `sources` och `notified`, och skriv i `last_event` att posterna slogs ihop. Är påminnelsen fel, rätta den med `reminders edit` eller `reminders complete`. Logga rättelsen i `log.md`.

**Fel i beteendet** — för många notiser, fel tröskel, missad avsändartyp, ny speditör som inte tolkas rätt. Då ska denna fil ändras, inte state. Redigera `~/dev/claude-skills/deliveries/`, committa och pusha, och kör `git pull` på Mini. Skriv beslutet i beslutstabellen i `~/dev/brain/projects/deliveries/README.md` med skälet, inte bara ändringen.

Exempel på var gränsen går:

| Tim säger | Vad som ändras |
|-----------|----------------|
| "Instabox-paketet var Alvas skor" | `items` i state |
| "CityMail och Bow19 är samma paket" | slå ihop posterna i state |
| "sluta tjata om returer" | åtgärdstabellen i denna fil |
| "vänta tio dagar innan du larmar om frakt" | förseningsreglerna i denna fil |
| "DHL Freight-aviseringar tolkas fel" | klassnings- eller matchningsavsnittet i denna fil |

Är det oklart vilket det är: fråga. En regeländring som görs som en engångsrättelse i state kommer tillbaka nästa vecka.

## Manuell körning

```bash
delivery-watch --dry-run --since 30d   # se vad den skulle göra
delivery-watch                          # ett skarpt pass
```

Frågar Tim "vad väntar jag på", läs `state.json` och svara ur den. Kör inget pass om han bara frågar.
