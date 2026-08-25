---
name: mac-cleanup
description: Städa upp ordningen på Macen, en domän i taget - menyraden, autostart, oanvända appar, Homebrew, rester efter avinstallerade appar, filer och mappar, systeminställningar. Triggers on "städa datorn", "rensa upp", "menyraden", "vad startar automatiskt", "oanvända appar", "declutter mac", "vad är det här för app".
---

# Mac Cleanup

Ordning, inte utrymme. Skillen `disk-cleanup` frigör plats; den här handlar om
att varje app, ikon, autostart och mapp ska finnas där för att Tim använder den.
De två överlappar aldrig.

Arbetet går över flera sessioner. Projektet
`~/dev/brain/projects/mac-cleanup/README.md` är sanningen om var ni är.

## Varje pass

1. **Läs `~/dev/brain/projects/mac-cleanup/README.md` först.** Saknas den, skapa
   från `~/dev/brain/projects/TEMPLATE.md` med domäntabellen nedan.
2. Kör **en domän**. Tim väljer, annars nästa öppna i tabellen.
3. Uppdatera README, committa, stanna. Föreslå nästa domän, börja den inte.

Ett pass rör en domän. Blandade pass gör loggen obrukbar och tröttar ut Tim.

## De fyra stegen i en domän

**Inventera.** Belägg varje påstående med ett kommando. "Används nog inte" är
värdelöst; `kMDItemLastUsedDate: 2024-08-11` är ett beslutsunderlag. Presentera
en tabell: vad det är, vad det gör, senast använt, storlek, din bedömning.
*Klart när varje post i domänen har ägare, bevis och bedömning.* Ställ inga
frågor innan tabellen är komplett.

**Fråga.** AskUserQuestion, batchat per domän. Förklara vad något är innan du
frågar om det ska bort - Tim känner inte igen hälften, det är hela poängen med
övningen. När flera verktyg gör samma jobb, fråga vilket som vinner i stället
för att välja åt honom.

**Föreslå.** Tre högar, åtskilda: **skräp** (pekar på något som inte finns,
dubbletter, appar för tjänster han lämnat), **kandidater** (kräver hans ja),
**fredat**. Varje våg ska vara kort nog att orka läsa.

**Utför.** Efter godkännande. Allt som tas bort går i karantän.

## Karantän

Flytta till `~/.trash-cleanup/ÅÅÅÅ-MM-DD/` med bevarad sökvägsstruktur, och
skriv `MANIFEST.md` i samma mapp: var varje sak låg, varför den flyttades.
Karantänen töms bara när Tim säger till. Appar från brew eller App Store går
direkt, de installeras om på en rad.

Fråga innan `sudo`.

## Domäner

Kör i ordning om Tim inte säger annat. Menyraden först, den stör mest dagligen.

### 1. Menyraden

Bartender 6:s inställningar listar varje ikon med ägande app, även de dolda. Be
Tim öppna den och läsa upp listan - det är den enda kompletta källan.

Programmatiskt får du ägare men inte ikoner:

```sh
osascript -e 'tell application "System Events" to get name of every process whose background only is true'
```

Fråga aldrig `every process` efter `menu bar 2`, det hänger i minuter. Kör mot
en namngiven kandidatlista med `timeout 25`.

Beslut per ikon: synlig, dold i Bartender, avstängd i appens egna inställningar,
eller appen bort. Föredra att stänga av i appen framför att dölja i Bartender -
en dold ikon betyder att processen fortfarande kör.

*Klart när varje ikon har ägare och beslut.*

### 2. Autostart

- System Settings → General → Login Items & Extensions - be Tim läsa upp den,
  BTM går inte att läsa utan `sudo sfltool dumpbtm`
- `ls ~/Library/LaunchAgents /Library/LaunchAgents /Library/LaunchDaemons`
- `launchctl list | grep -v com.apple`
- `brew services list`

Hitta agenter som pekar i tomma luften:

```sh
for f in ~/Library/LaunchAgents/*.plist /Library/LaunchAgents/*.plist; do
  prog=$(/usr/libexec/PlistBuddy -c "Print :ProgramArguments:0" "$f" 2>/dev/null \
      || /usr/libexec/PlistBuddy -c "Print :Program" "$f" 2>/dev/null)
  [ -n "$prog" ] && [ ! -e "$prog" ] && echo "SAKNAS: $f -> $prog"
done
```

Säg för varje post vad som faktiskt går sönder om den stängs av.

*Klart när varje post som startar av sig själv har ägare och beslut.*

### 3. Appar

`/Applications` och `~/Applications`.

```sh
mdls -name kMDItemLastUsedDate -name kMDItemDisplayName /Applications/*.app
```

Sortera på senast använd. Jämför mot `brew list --cask` - det avgör hur den
avinstalleras.

Leta överlapp där han kör flera verktyg för samma jobb: diktering, webbläsare,
editorer och IDE:er, virtualisering, terminaler, git-GUI:n, fönsterhantering,
urklippshanterare. Föreslå en vinnare per kategori, fråga.

Avinstallation: `brew uninstall --cask <namn>` när den vägen finns. Annars appen
plus dess `Application Support`, `Preferences`, `Caches`, `LaunchAgents` och
`Saved Application State` till karantän.

*Klart när varje app har senast använd-datum och beslut.*

### 4. Homebrew

- `brew leaves` mot vad han faktiskt kör, `brew uses --installed <formula>` för
  att se vad som håller kvar en beroendekedja
- `brew autoremove --dry-run`
- casks utan app kvar i `/Applications`
- `brew services list` - tjänster ingen använder

*Klart när varje `leaf` har ett skäl att finnas kvar.*

### 5. Rester efter avinstallerade appar

`~/Library/Application Support`, `Preferences`, `Containers`, `Caches`,
`Saved Application State`, `LaunchAgents`.

Bygg listan över installerade bundle-ID:n och matcha mot vad som ligger kvar:

```sh
mdfind "kMDItemContentType == 'com.apple.application-bundle'" -onlyin /Applications
```

Föräldralösa poster till karantän. Prefs för appar han har kvar rörs inte -
de innehåller inställningar han skulle sakna.

*Klart när varje föräldralös post är listad och beslutad.*

### 6. Filer och mappar

`~/Desktop`, `~/Downloads`, `~/Documents`, iCloud Drive, `~/dev`.

I `~/dev`: repos utan commits på över ett år, och repos utan remote. Repos utan
remote raderas inte - de pushas eller arkiveras, fråga vilket.

Föreslå struktur, inte bara radering. En mapp som får ett hem är städad.

*Klart när varje topplevel-objekt i de fem platserna har ett beslut.*

### 7. Systeminställningar

Dock, Finder (sidopanel, standardvy, filändelser), Spotlight-kategorier, Control
Center, notiser per app, Focus-lägen, hot corners, Stage Manager, delning.

Här raderas inget. Gå igenom vad som är på och fråga vad han vill ha. Målet är
mindre brus.

*Klart när varje yta är genomgången och besluten är loggade.*

## Fredat

Fråga innan något av det här rörs:

- `~/dev/dotfiles`, `~/dev/brain`, `~/dev/claude-skills` och allt som symlänkas
  därifrån
- launchd-jobben `com.tkilaker.*` och `com.user.mount-nas-shares`
- `watch-*`-aliasen i `~/Downloads` - avsiktliga NAS-genvägar
- `~/bin`, `~/.local/bin`
- `~/.claude`, `~/.codex`, `~/.agents`, `~/.secrets`
- `~/Library/Mobile Documents` (iCloud)
- 1Password, KeePassXC, Tailscale, agent-secret-kedjan

## Domäntabell i README

| # | Domän | Status | Datum | Kvar att göra |
|---|-------|--------|-------|---------------|
| 1 | Menyraden | öppen | | |
| 2 | Autostart | öppen | | |
| 3 | Appar | öppen | | |
| 4 | Homebrew | öppen | | |
| 5 | Rester | öppen | | |
| 6 | Filer och mappar | öppen | | |
| 7 | Systeminställningar | öppen | | |

Logga varje beslut i README:s beslutstabell, även "behåller, för att X". Det är
de besluten som gör att nästa pass inte frågar om samma sak igen.
