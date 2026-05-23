# Performance-Diagnostik Research Player und Seitenstart

## Scope

- Fokus auf Research Player, Research Comparison und gemeinsame Seitenstartkosten.
- Keine weitere Teaching-Spezialoptimierung, außer bei gemeinsam genutzten Basisdateien.
- Messungen lokal gegen `http://127.0.0.1:8010` mit dem Fallback-Start `tmp/run_app_8010.py`.

## Messkontext

- `scripts/dev-start.ps1` war in diesem Lauf wegen eines lokalen PostgreSQL-Migrationszustands nicht als stabiler Messpfad nutzbar.
- Die lokale Development-Konfiguration liefert statische Assets und Player-Audio mit `Cache-Control: no-cache, max-age=0` aus. Die hier dokumentierten Request-Struktur-, HTML- und Payload-Befunde sind belastbar; absolute Ladezeiten bleiben lokale Dev-Werte.

## Direkt gemessene Werte

| Route | HTML-Größe | JSON-State | Requests | Audio-Requests vor Interaktion | DOM-Knoten | DCL / Load |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `/en` | 10.8 KB | 0 | 62 | 0 | 111 | 119 ms / 247 ms |
| `/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=speakers` | 158.0 KB | 16.6 KB | 63 | 1 | 1083 | 378 ms / 448 ms |
| `/en/research/spanish/player/ES-L-0001-2026-S01/text?source=speakers` | 223.8 KB | 72.2 KB | 63 | 1 | 1140 | 361 ms / 420 ms |
| `/en/research/spanish/comparison?task=wordlist` | 85.8 KB | 55.5 KB | 67 | 0 | 390 | 525 ms / 649 ms |

Weitere gemessene Größen:

- `app/static/js/pages/research-player.js`: 41.7 KB
- `app/static/js/pages/research-comparison.js`: 60.5 KB
- `app/static/css/30_components.css`: 239612 Bytes / 234.0 KB
- `app/static/css/00_tokens.css`: 59355 Bytes / 58.0 KB
- `app/static/css/40_cards.css`: 32307 Bytes / 31.5 KB
- `app/static/css/md3/components/top-app-bar.css`: 28990 Bytes / 28.3 KB
- `app/static/css/20_layout.css`: 28136 Bytes / 27.5 KB

## Engpässe

### 1. Research Player: `text` ist primär Payload- und DOM-schwer, nicht CPU-schwer

Der auffälligste Player-Fall ist die `text`-Route:

- 223.8 KB HTML
- 72.2 KB eingebetteter JSON-State
- 1140 DOM-Knoten
- 50 Item-Knoten im DOM
- 393 Token-Knoten im DOM

Der gleiche Token-Bestand liegt doppelt vor:

- 50 Items im JSON-State und 50 gerenderte `data-player-item`-Knoten
- 393 Tokens im JSON-State und 393 gerenderte `data-player-token`-Knoten

Die groben CPU-Kosten des aktuellen Initialcodes waren lokal klein:

- Durchschnittliche `JSON.parse(...)`-Kosten des `text`-State über 50 Iterationen: ca. 0.076 ms pro Parse
- Nachbau des `itemMap`-Scans aus `research-player.js` auf der `text`-Seite: ca. 0.6 ms

Das spricht gegen einen akuten JS-CPU-Engpass beim ersten Start. Der eigentliche Kostentreiber ist die doppelte Datenhaltung in HTML plus JSON sowie die daraus resultierende Dokumentgröße.

### 2. Research Player: frühe Audio-Metadaten werden geladen

Der Player rendert auf der Hauptfläche:

- primäres Audio mit `preload="metadata"`
- optional sekundäres Audio mit `preload="metadata"`
- Referenz-Dialog-Audio mit `preload="none"`

Gemessen wurde auf der Wordlist- und Text-Route jeweils genau ein Audio-Request vor Nutzerinteraktion. Der Server-Log zeigte für die Wordlist-Route direkt nach dem initialen Seitenaufbau einen `206`-Request auf `/audio.mp3`.

Das ist deutlich kleiner und kontrollierter als der frühere Teaching-Befund, aber es ist ein realer Vorab-Request auf einer Route mit einem 2.2-MB-Hauptaudio.

### 3. `research-player.js` ist nicht der Hauptblocker beim Initialstart

Die Datei ist mit 41.7 KB nicht klein, aber die teureren Laufpfade starten überwiegend erst bei Interaktion oder Wiedergabe:

- `requestAnimationFrame`-Sync-Loop startet erst während laufender Wiedergabe
- `timeupdate`-Highlighting läuft erst bei Audioaktivität
- `scrollIntoView(...)` wird nur für fokussierte Items benutzt
- Referenz-Audio wird erst im Dialog geladen

Die Initialisierung baut allerdings unmittelbar einen vollständigen DOM-Index für Items und Tokens auf. Das ist bei aktuellen Größen noch nicht der Hauptkostentreiber, skaliert aber mit mehr Text-/Interview-Material.

### 4. Research Player: In-Place-Navigation parst vollständiges HTML neu

`navigatePlayerInPlace(...)` lädt die nächste Player-Seite als vollständiges HTML, parst sie via `DOMParser`, ersetzt das `article`, entfernt und re-injiziert den JSON-State und initialisiert danach den gesamten Player erneut.

Das ist funktional sauber, bedeutet aber bei Set-/Session-/Task-Wechseln erneut vollständige HTML- und DOM-Arbeit statt kleiner state-basierter Updates.

### 5. Research Comparison: page-spezifisch geladen, aber mit teurem Initial-Boot

`app/static/js/pages/research-comparison.js` wird nur in `research_comparison.html` geladen. Das ist korrekt.

Trotzdem ist die Seite beim Initialstart merklich schwerer als der Player:

- 55.5 KB eingebetteter JSON-State
- 67 Requests im gemessenen Lauf
- DCL 525 ms, Load 649 ms

Der Initial-Boot macht zusätzliche Arbeit für authentifizierte Nutzer:innen ohne explizites `set_id`:

- `loadOwnedSetPresets()` lädt die sichtbaren Sets
- `bootstrapDefaultWorkspace()` erstellt implizit einen Draft
- anschließend wird `PUT .../items` mit dem Standardmaterial ausgeführt

Im Browser waren diese frühen Requests sichtbar als Set-Listen- und Item-Requests; der Initialzustand ist also nicht rein servergerendert, sondern baut sich mit API-Nachläufen auf.

Positiv: die Comparison-Seite lädt vor Interaktion keine Audio-Ressourcen und rendert initial keine `<audio>`-Tags. Die Audioarbeit beginnt dort erst über das explizite `new Audio()`-Playback.

### 6. Shared Startup: globale Basis bleibt breit

Alle gemessenen Seiten tragen weiterhin die breite gemeinsame Basis aus:

- 30 Stylesheet-Links im `base.html`-Pfad
- großes gemeinsames CSS, besonders `30_components.css`
- globaler `entry.js`-Boot plus `main.js` und Navigationsmodule
- zusätzlich ein globaler `auth/session`-Request

Auf der öffentlichen Landing-Page wurde die gefühlte Startlast stärker von Assets als von JS dominiert:

- `static/img/cards/unterricht_01.png` war mit rund 2.16 MB die größte Ressource
- `static/img/cards/research_title_image.jpg` lag bei rund 111 KB

Für allgemeine Seitenladezeiten ist daher nicht nur JS, sondern auch die Asset-Auswahl der Basisseiten relevant.

## Direkt umgesetzte sichere Fixes

### Shared `entry.js`: optionale Module nur noch bei passendem DOM laden

In `app/static/js/modules/core/entry.js` werden jetzt nur noch bei Bedarf nachgeladen:

- `datawrapper.js`
- `teaching-mini-player.js`
- `teaching-citation-copy.js`

Validiert wurde mit deaktiviertem Browser-Cache:

- Landing, Research Player und Comparison laden diese Module jetzt nicht mehr
- eine echte Teaching-Seite lädt sie weiterhin korrekt

Damit entfallen auf nicht passende Seiten drei zusätzliche JS-Requests und rund 11.6 KB unkomprimierter Modulcode plus Initialisierungsarbeit.

## Priorisierte nächste Maßnahmen

### P0

1. Research-Player-`text` von doppelter Datenhaltung entlasten.
   Aktuell liegen Items und Tokens sowohl im DOM als auch im eingebetteten JSON-State vor. Der größte direkte Hebel ist, die Token-/Item-Informationen nur noch einmal vollständig zu transportieren und die andere Darstellung schlanker abzuleiten.

2. Comparison-Boot ohne implizite Mehrfach-API-Kette entschärfen.
   Die Kombination aus Set-Liste laden, Draft erzeugen und Items schreiben verlangsamt den ersten authentifizierten Einstieg. Entweder muss der servergerenderte Erstzustand vollständiger werden oder der implizite Draft später entstehen.

3. Player-Audio-Preload fachlich entscheiden.
   Der aktuelle `metadata`-Preload erzeugt reale Vorab-Requests. Wenn die Initial-Daueranzeige nicht zwingend ist, ist `preload="none"` ein realistischer nächster Schritt. Wenn die Dauer sichtbar bleiben soll, sollte die Entscheidung explizit dokumentiert werden.

### P1

1. Gemeinsame Basiskette weiter segmentieren.
   Nach dem jetzt umgesetzten Optional-Modul-Lazy-Load bleibt `main.js` inklusive Navigationsmodulen ein Kandidat für bedingtes Laden auf Seiten ohne Drawer/App-Bar-Nutzen.

2. Große Shared-CSS-Familien prüfen.
   Besonders `30_components.css` ist ein starker Kandidat für spätere Aufteilung nach wirklich gemeinsamem Kern versus selteneren Oberflächenfamilien.

3. Landing-Assets komprimieren oder ersetzen.
   Für allgemeine Seitenladezeit ist die große PNG-Karte auf `/en` ein direkter Befund.

### P2

1. Playback-Mikrooptimierungen erst nach echter Wiedergabe-Messung.
   `timeupdate`, Highlighting und `requestAnimationFrame` sind im aktuellen Befund keine Initial-Load-Hauptursache. Optimierung lohnt sich erst nach gezielter Wiedergabe-Profilingrunde.

2. In-Place-Player-Navigation später state-basierter machen.
   Das vollständige HTML-Reparse bei Player-Navigation ist korrekt, aber eher ein mittelfristiger Architekturhebel als ein sicherer Sofortfix.

## Geänderte Dateien

- `app/static/js/modules/core/entry.js`
- `docs/performance-diagnostics-research-player.md`

## Ausgeführte Checks

- Lokaler Live-Server über `tmp/run_app_8010.py`
- Browser-Messung auf:
  - `/en`
  - `/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=speakers`
  - `/en/research/spanish/player/ES-L-0001-2026-S01/text?source=speakers`
  - `/en/research/spanish/comparison?task=wordlist`
- Authentifizierter Browser-Run mit lokalem Dev-Admin
- Messung mit deaktiviertem Browser-Cache für Request-Struktur nach dem `entry.js`-Fix
- Server-Log-Abgleich der frühen Audio-Requests
- Header-Check für Cache-Control und Content-Length von Shared-CSS, Shared-JS und Player-Audio
- `get_errors` auf `app/static/js/modules/core/entry.js`

## Offene Risiken

- Die dokumentierten Zeiten stammen aus einem lokalen Development-Setup mit `no-cache, max-age=0`; Produktionswerte werden davon abweichen.
- Für den Research Player fehlt noch eine echte Laufprofilingrunde während Wiedergabe und beim Umschalten zwischen Sessions/Sets.
- Für Comparison ist die Initial-API-Kette klar sichtbar, aber noch nicht in eine konkrete serverseitige Entschlackung übersetzt.
