---
name: jobbagent
description: Daglig jobbevakning och ansökningsutkast för en person (först Ellen). WATCH hämtar och matchar nya annonser mot profilen och mailar digest; DRAFT skriver CV-variant + personligt brev för en vald annons. Triggers on "jobbagent", "jobbevakning", "utkast för annons", "jobbdigest".
---

# Jobbagent

## Stoppregel — läs först

Parametrarna `MODE`, `SINCE`, `RUN_START` och `STATE_DIR` kommer från wrappern i
prompten. Härled dem aldrig om, läs inga env-variabler, gissa inget tidsfönster.
Saknas de och detta inte är en interaktiv DRAFT-förfrågan: avsluta direkt med
`PASS: blocked (missing params)`.

`MODE=dry-run`: kör hela passet men skriv digesten till
`$STATE_DIR/digest-dry-run.md` istället för att maila. Skicka aldrig mail i dry-run.

Saknas `$STATE_DIR/profile-ellen.md`: avsluta `PASS: blocked (no profile)`.

## Filer

Allt state ligger i `STATE_DIR` (normalt `~/dev/brain/projects/jobbagent/`):

- `profile-ellen.md` — profilen som allt matchas mot. Gitignorerad, lämna orörd.
- `search-config.json` — filter för hämtningen.
- `seen.jsonl` — en rad per bedömd annons: `{"id","date","score","verdict","headline"}`.
- `passes.jsonl` — en rad per pass: `{"run_start","mode","fetched","new","matched","result"}`.
- `log.md` — läsbar logg: datum + vad som mailades.

## WATCH — dagligt pass

1. **Hämta**: `scripts/fetch-ads.sh "$SINCE" "$STATE_DIR/search-config.json"` → JSON-array.
2. **Dedupe**: släng annonser vars `id` redan finns i `seen.jsonl`.
3. **Bedöm varje ny annons** mot `profile-ellen.md`. Score 0–10 och en rads "varför".
   Hårda diskvalificeringar (score 0, oavsett annan matchning):
   - Kvälls-, helg- eller skiftarbete enligt annonstexten. Osäkert schema för en
     roll som typiskt är dagtid (kontor, skola, förvaltning) är ok; osäkert schema
     för vård/handel/restaurang räknas som kväll/helg.
   - Körkortskrav i texten (API-filtret missar ibland krav som bara nämns i brödtext).
   - Arbetsplats som rimligen inte nås med tåg/buss från Lund C inom profilens
     restidsgräns. Bedöm från adress och ort.
   - Krav profilen uppenbart inte uppfyller (legitimationsyrken, specifik examen).
   Väg in: kompetensmatch mot profilens transfererbara styrkor, omfattning mot
   profilens krav, kultur-nära är plus men aldrig krav.
4. **Digest**: träffar med score ≥ 6, max 5 stycken, rankade. Per träff: rubrik,
   arbetsgivare, ort, omfattning, en rads varför, ansök-länk, sista ansökningsdag.
   Svenska, kort, ingen AI-prosa. Inga träffar ≥ 6 → ingen mail, ingen fil.
5. **Skicka** (endast skarpt läge): `scripts/send-digest.sh` med digesten.
   Mottagare står i profilen.
6. **Logga**: append till `seen.jsonl` (alla bedömda, även score 0), `passes.jsonl`,
   och `log.md` (bara om digest skickades).
7. **Kvitto**: sista raden på stdout är alltid `PASS: ok` eller `PASS: blocked (<orsak>)`.
   Inga träffar är `PASS: ok`.

## DRAFT — utkast på begäran (interaktivt)

Trigger: någon ber om utkast för en annons (länk, id eller rubrik ur en digest).

1. Hämta annonsen (id → `https://jobsearch.api.jobtechdev.se/ad/<id>`, annars läs länken).
2. Läs `profile-ellen.md` inklusive CV-master och tonalitet.
3. Skriv två saker på svenska (om inte annonsen är på engelska):
   - **CV-variant**: mastern omvinklad mot annonsen. Ordningen och betoningen får
     ändras, fakta får aldrig ändras eller läggas till.
   - **Personligt brev**: max en halv sida. Konkret koppling mellan hennes bakgrund
     och just denna roll. Ingen AI-prosa, inga superlativ, inga fraser som
     "brinner för". Använd hennes egna formuleringar ur profilen där de finns.
4. Visa båda för granskning. Ansökan skickas alltid manuellt av Ellen — erbjud
   aldrig att skicka, fyll aldrig i formulär.

## Fel

Nätverksfel mot API:t: försök igen en gång, sedan `PASS: blocked (api)`.
Allt oväntat: hellre `PASS: blocked (<orsak>)` än ett halvt genomfört pass —
skriv aldrig till `seen.jsonl` om bedömningen inte fullföljdes.
