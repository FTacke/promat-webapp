# Speech/Text Sync auf der Player-Seite

Diese Notiz beschreibt die aktive technische Umsetzung der Audio-Text-Synchronisierung auf der Player-Seite in CORAPAN. Ziel ist nicht eine allgemeine Theorie, sondern eine belastbare Zerlegung der tatsächlich laufenden Implementierung, damit sich das Muster in einem anderen Projekt nachbauen laesst.

## Kurzfassung

Die Loesung besteht aus vier sauber getrennten Bausteinen:

1. Die Flask-Route uebergibt Audio-, JSON- und optional `token_id`-Informationen als `data-*`-Attribute an die Player-Seite.
2. Ein Initialisierungsmodul baut Audio-Player, UI-Helfer, Letter-Highlighting und Transkriptionsmanager zusammen.
3. Der Transkriptionsmanager rendert jedes Wort als eigenes `span.word` mit Zeitmarken in `data-start` und `data-end`.
4. Waehend der Wiedergabe laeuft die visuelle Synchronisierung nicht ueber `timeupdate`, sondern ueber eine `requestAnimationFrame`-Schleife, die fortlaufend die aktuelle Audio-Position gegen die Wort-Zeitfenster prueft und CSS-Zustandsklassen setzt.

Genau diese Kombination erzeugt den Eindruck eines "smoothe" laufenden Textcursors mit Vorschau auf den naechsten Text und normalisiertem Rueckblick auf bereits Gesagtes.

## Aktive Dateikette

Die derzeit aktive Kette ist:

- `app/src/app/routes/player.py`
- `app/templates/pages/player.html`
- `app/static/js/modules/player/entry.js`
- `app/static/js/player/player-init.js`
- `app/static/js/player/modules/audio.js`
- `app/static/js/player/modules/transcription.js`
- `app/static/js/player/modules/highlighting.js`
- `app/static/css/md3/components/transcription-shared.css`
- `app/static/css/md3/components/player.css`
- `app/static/css/md3/components/audio-player.css`

Wichtig: `app/static/js/player/player-main.js` enthaelt ebenfalls einen Player-Controller, ist aber nicht der aktive Einstiegspunkt der Seite. Die Seite laedt aktuell `app/static/js/modules/player/entry.js`, und dieses Modul importiert `app/static/js/player/player-init.js`.

## 1. Backend-zu-Frontend-Uebergabe

Die Route `app/src/app/routes/player.py` rendert die Seite nur fuer authentifizierte Nutzer und uebergibt diese Werte an das Template:

- `transcription`: Pfad zur JSON-Transkription
- `audio`: Pfad zur MP3-Datei
- `token_id`: optionaler Ziel-Token fuer Deep-Linking/Hervorhebung

Das Template `app/templates/pages/player.html` schreibt diese Werte in den Root-Knoten:

- `data-transcription`
- `data-audio`
- `data-token-id`

Das ist bewusst simpel und robust: kein Inline-State-Blob aus grosser JSON, sondern nur die minimalen Dateiverweise. Die eigentlichen Daten werden erst clientseitig geladen.

## 2. Page-Bootstrap und Modul-Orchestrierung

`app/static/js/modules/player/entry.js` liest die `data-*`-Attribute aus dem Root-Element und setzt daraus `window.PLAYER_CONFIG`.

`app/static/js/player/player-init.js` initialisiert dann in fester Reihenfolge:

1. `MobileHandler`
2. `UIManager`
3. `TokenCollector`
4. `HighlightingManager`
5. `AudioPlayer`
6. `TranscriptionManager`
7. `ExportManager`

Fuer die Synchronisierung entscheidend ist die Kopplung zwischen Audio und Transkriptionsmanager:

- `audioPlayer.onPlay -> transcriptionManager.startWordHighlighting()`
- `audioPlayer.onPause -> transcriptionManager.stopWordHighlighting()`
- `audioPlayer.onEnded -> transcriptionManager.stopWordHighlighting()`

Das ist der Kern der Loesung: Der Audio-Player liefert nicht selbst die Wortlogik, sondern signalisiert nur den Wiedergabestatus. Die gesamte Wortzuordnung sitzt zentral im Transkriptionsmanager.

## 3. JSON-Datenmodell als Basis fuer die Synchronisierung

Die aktive Implementierung erwartet in der JSON-Datei mindestens:

- Top-Level-Metadaten wie `filename`, `country_display`, `radio`, `city`, `revision`, `date`
- `segments`, ein Array von Sprechersegmenten
- pro Segment: `speaker_code` und `words`
- pro Wort: `text`, `start_ms`, `end_ms`, `token_id`, plus linguistische Felder wie `lemma`, `pos`, `morph`, `dep`, `head_text`

Fuer die Synchronisierung sind die kritischen Felder nur diese drei:

- `text`
- `start_ms`
- `end_ms`

Alles andere ist Zusatznutzen fuer Tooltip, Suche, Export oder Token-Referenzen.

## 4. Rendering-Strategie des Transkripts

`app/static/js/player/modules/transcription.js` laedt die JSON-Datei mit:

- `fetch(url, { credentials: "same-origin", cache: "no-store" })`

Danach passieren drei Dinge:

1. Metadaten werden in die Sidebar geschrieben.
2. Alle Segmente werden in `#transcriptionContainer` gerendert.
3. Optional wird ein Ziel-Token hervorgehoben und ins Viewport gescrollt.

Ein Segment wird als `.md3-speaker-turn` aufgebaut. Darin gibt es:

- einen Header mit Sprecher-Chips und Zeitspanne
- einen Textblock `.md3-speaker-text`

Jedes Wort wird als eigenes `span.word` erzeugt. Das ist die wichtigste strukturelle Entscheidung der ganzen Loesung. Pro Wort werden direkt am DOM-Element gespeichert:

- `data-start`
- `data-end`
- `data-token-id`
- `data-token-id-lower`
- `data-group-index`

Dadurch ist die spaetere Synchronisierung nur noch ein Vergleich zwischen `audio.currentTime` und DOM-Datensaetzen. Es wird keine zweite, getrennte Indexstruktur benoetigt.

## 5. Warum die Wiedergabe visuell "smooth" wirkt

Der entscheidende Punkt ist, dass die aktive Wortmarkierung nicht auf das native `timeupdate`-Event des Audio-Elements vertraut.

Stattdessen macht `TranscriptionManager.startWordHighlighting()` Folgendes:

- setzt `isPlaying = true`
- startet eine Endlosschleife via `requestAnimationFrame`
- ruft pro Frame `updateWordsHighlight()` auf

Das bedeutet praktisch:

- Abfragefrequenz nahe der Bildschirm-Refresh-Rate statt nur sporadischer Audio-Events
- wesentlich weichere Uebergaenge beim Wortwechsel
- konsistentere visuelle Vorschau fuer kommende Woerter

Gerade dieser Punkt ist der wichtigste technische Unterschied zwischen einer einfachen "Audio laeuft, Wort springt manchmal weiter"-Implementierung und einer optisch hochwertigen Loesung.

## 6. Zustandsmaschine fuer vergangen, aktuell und bevorstehend

`updateWordsHighlight()` arbeitet nicht nur mit einem Zustand, sondern mit mehreren gleichzeitig sichtbaren Zustandsklassen.

### 6.1 Aktuelles Wort finden

In jedem Frame werden alle `.word`-Elemente durchlaufen. Fuer jedes Wort wird geprueft:

- `currentTime >= data-start`
- `currentTime <= data-end`

Das erste passende Wort wird als aktives Wort genommen.

### 6.2 Segment- und Gruppenkontext bestimmen

Jedes Wort hat ein `data-group-index` im Format `segmentIndex-groupIndex`.

Die Gruppen entstehen in `_groupWords(words)` mit zwei Regeln:

- Pause von mindestens `0.25` Sekunden trennt eine Gruppe
- spaetestens nach 3 Woertern wird eine Gruppe ebenfalls abgeschlossen

Das ist visuell sehr wichtig: Die UI arbeitet nicht nur mit einem einzelnen aktiven Wort, sondern mit "Sprechhaeppchen". Dadurch entsteht eine lesbarere Vorschau.

### 6.3 CSS-Klassen, die pro Frame gesetzt werden

Fuer das aktive Segment werden die Wortklassen neu berechnet:

- `is-current`: genau das aktuelle Wort
- `playing`: Zusatzklasse fuer dasselbe aktuelle Wort
- `is-past`: alle Woerter vor dem aktuellen Wort
- `is-future`: alle Woerter nach dem aktuellen Wort
- `is-active-group-context`: andere Woerter derselben Gruppe wie das aktuelle Wort
- `is-preview-group`: Woerter der direkt folgenden Gruppe

Die Wirkung in CSS ist:

- aktuelles Wort: stark gelber, kontrastreicher Fokus
- vergangene Woerter: normal lesbar
- kommende Woerter: sichtbar, aber abgedimmt
- Rest der aktuellen Gruppe: leicht hinterlegt
- naechste Gruppe: dezente Vorschau-Flaeche

Das ist genau der Effekt, den du beschrieben hast: zurueckliegender Text bleibt normal, bevorstehender Text wird heller bzw. schwacher, und das aktuelle Wort laeuft fliegend durch den Text.

## 7. Flimmervermeidung und Lesefluss

Die Implementierung enthaelt zwei kleine, aber sehr wirksame Entscheidungen:

1. Bei kurzen Pausen oder Zwischenraeumen ohne aktives Wort werden die Klassen nicht sofort global geloescht. Der letzte visuelle Zustand bleibt stehen, statt zu flackern.
2. Es wird nur gescrollt, wenn das aktuelle Wort im Viewport zu weit nach unten rutscht. Dann erfolgt `scrollIntoView({ behavior: "smooth", block: "center" })`.

Beides zusammen verhindert das hektische Springen, das viele einfachere Karaoke-/Transcript-Implementierungen schlecht lesbar macht.

## 8. Audio-Player: getrennte Kontrolle, nicht getrennte Wahrheit

`app/static/js/player/modules/audio.js` kapselt die Audio-Wiedergabe:

- Play/Pause
- Skip `-3s` / `+3s`
- Progress-Bar
- Lautstaerke / Mute
- Geschwindigkeit
- Tastaturkuerzel

Die Synchronisierungswahrheit liegt aber nicht im Audio-Modul, sondern im Wort-DOM plus `currentTime`.

Das Audio-Modul stellt nur bereit:

- `playSegment(startTime, endTime = null)`
- `getCurrentTime()`
- `isPlaying()`

Das ist ein gutes Muster fuer Nachbauprojekte: Audio-Steuerung und Text-Synchronisierung getrennt halten, aber ueber schmale Callbacks verbinden.

## 9. Klick-Interaktionen auf Wortebene

Jedes Wortspan ist nicht nur Anzeige, sondern Interaktionsflaeche.

Die aktive Logik in `_createWordElement()` unterstuetzt:

- `Ctrl+Click`: nur dieses Wort abspielen
- `Shift+Click`: von diesem Wort bis Segmentende abspielen
- normaler Klick: Wort mit Kontext abspielen

Fuer den normalen Klick wird absichtlich nicht nur das Zielwort gespielt, sondern Kontext davor und danach:

- Start = bis zu zwei Woerter frueher
- Ende = bis zu zwei Woerter spaeter

Das ist keine reine Sync-Funktion, aber eine wichtige UX-Entscheidung. Wer Text und Audio gekoppelt nutzt, will meistens nicht auf exakt einem isolierten Token beginnen, sondern mit etwas Einbettung.

Zusatzfunktion: jeder Wortklick kann die `token_id` an den Token-Collector weitergeben.

## 10. Deep-Linking ueber `token_id`

Die Player-Seite unterstuetzt ein gezieltes Anspringen eines Token-Elements.

Die Implementierung normalisiert `token_id` konsequent in Kleinschreibung und trimmt Leerzeichen. Das passiert sowohl im Bootstrap (`player-init.js`) als auch beim Rendern der Wortspans.

Es gibt zwei Sicherheitsnetze:

1. Beim Erzeugen des Wortspans wird direkt verglichen, ob `data-token-id-lower === targetTokenId`.
2. Nach dem Rendern erfolgt zusaetzlich eine DOM-Suche mit `CSS.escape()` auf `[data-token-id-lower="..."]`.

Wenn ein Treffer existiert:

- das Wort bekommt `word-token-id`
- es wird sanft ins Zentrum gescrollt
- das Audio wird auf `start - 0.25s` vorpositioniert

Wichtig fuer die Analyse: in der aktiven JS-Kette gibt es keine Verarbeitung von `#t=...` aus dem URL-Hash. In `app/templates/search/_results.html` werden zwar Links mit `#t=<sekunden>` erzeugt, aber die aktive Player-Initialisierung wertet diesen Hash nicht aus. Aktiv implementiert ist die token-basierte Vorpositionierung, nicht die hash-basierte Startzeit.

## 11. Letter- und Teilwort-Markierung

Die Funktion fuer manuelles Markieren sitzt in `app/static/js/player/modules/highlighting.js`.

### 11.1 Bedienmodell

Die UI dazu steht in `app/templates/pages/player.html`:

- Textfeld `#markInput`
- Button `#markButton`
- Container `#buttonsContainer` fuer aktive Markierungen

`HighlightingManager.init()` bindet:

- Klick auf den Markieren-Button
- `Enter` im Eingabefeld

### 11.2 Suchmodi

Es gibt drei Modi:

- normal: exakte Teilstring-Suche innerhalb eines Wortes
- Suffix `_`: nur Treffer, auf die direkt Whitespace folgt
- Suffix `#`: nur Treffer vor Satzzeichen wie `.,;!?`

Beispiele aus der aktuellen Semantik:

- `s_` markiert nur ein `s` am Wortende
- `s#` markiert nur ein `s` vor Interpunktion

### 11.3 Wie markiert wird

Die Markierung geschieht nicht am aeusseren `.word`-Element, sondern innerhalb seines Inhalts:

- das aeussere `span.word` bleibt bestehen
- passende Buchstabenfolgen werden in innere `<span class="highlight">...</span>` gewrappt

Genau das ist wichtig, weil dadurch die Synchronisierung intakt bleibt:

- `data-start`, `data-end`, `data-group-index` bleiben am aeusseren Wortspan erhalten
- Klick-Handler bleiben am aeusseren Wortspan erhalten
- die Audio-Sync-Klassen wie `is-current` und `is-future` bleiben ebenfalls am aeusseren Wortspan aktiv

Die Buchstabenmarkierung ueberlagert also die Sync-Logik, statt sie zu zerstoeren.

### 11.4 Zaehlen und Rueckgaengigmachen

Fuer jede Suchanfrage wird gezaehlt, in wie vielen Woertern mindestens ein Treffer vorkam. Das Ergebnis erscheint als kleines Chip-Button mit Trefferzahl.

Beispiel:

- `que (17)`

Jeder dieser Buttons kann seine eigene Markierung wieder entfernen. Intern wird dabei der Inhalt der betroffenen Wortspans wieder zurueckgebaut.

Nuance der aktuellen Implementierung:

- die Trefferzahl zaehlt pro Wort, nicht pro einzelner Buchstabenstelle
- innerhalb eines einzelnen Wortes koennen aber mehrere Teiltreffer mit `.highlight` umschlossen werden

## 12. CSS als eigentliche Zustandsanzeige

Die JavaScript-Logik setzt fast nur Klassen. Die sichtbare Bedeutung kommt aus `app/static/css/md3/components/transcription-shared.css`.

Die zentralen visuellen Regeln sind:

- `.word.is-current` und `.word.playing`: gelbe Vollflaeche, schwarze Schrift, hohes Gewicht
- `.word.is-past`: normale Farbe, volle Deckkraft
- `.word.is-future`: reduzierte Deckkraft, `on-surface-variant`
- `.word.is-active-group-context`: leichte Container-Hinterlegung
- `.word.is-preview-group`: sanfte Vorschau-Hinterlegung
- `.word.word-token-id`: amberfarbener Fokus plus Puls-Animation
- `.word .highlight`: innere Buchstabenmarkierung mit eigener Hintergrundfarbe und Unterstreichung

Das ist architektonisch sauber, weil die Semantik in JS und die Darstellung in CSS getrennt bleiben. Wer das nachbaut, sollte diese Trennung beibehalten.

## 13. Tooltip-System pro Wort

Jedes Wort erhaelt in `data-tooltip` vorgerendertes HTML mit linguistischen Informationen:

- Lemma
- POS / Morphologie
- Dependency-Info
- Kopfwort
- `token_id`

Beim `mouseenter` wird dynamisch ein Floating-Tooltip an `document.body` angehaengt und am Viewport positioniert. Beim `mouseleave` wird er wieder entfernt.

Das ist fuer die Sync-Funktion nicht zwingend notwendig, aber fuer ein Replikat oft wertvoll: Die Wortspans sind nicht nur Timestamps, sondern koennen zugleich als Annotationstraeger dienen.

## 14. Wiederverwendbarkeit: Beleg durch den Editor

Der beste Nachweis fuer die Modularitaet ist `app/static/js/editor/editor-player.js`.

Dort wird derselbe `AudioPlayer` und derselbe `TranscriptionManager` erneut verwendet. Im Editor wird nur das normale Klickverhalten abgeschaltet:

- normale Klicks dienen dem Editieren
- `Ctrl+Click` und `Shift+Click` fuer Audio bleiben erhalten

Das zeigt: die Kernlogik ist nicht an die Player-Seite geklebt, sondern als wiederverwendbare Audio/Transkript-Kopplung implementiert.

## 15. Was du fuer ein anderes Projekt wirklich uebernehmen solltest

Wenn du nur die tragenden Ideen replizieren willst, sind diese Punkte die Pflichtliste:

1. Rendere jedes Wort als eigenes DOM-Element.
2. Speichere `start` und `end` direkt am Wort-Element.
3. Verwende `requestAnimationFrame` statt nur `audio.timeupdate` fuer die laufende Synchronisierung.
4. Arbeite mit mehreren visuellen Zustandsklassen gleichzeitig: aktuell, vergangen, zukuenftig, aktuelle Gruppe, naechste Gruppe.
5. Lasse das Audio-Modul nur Audio machen; die Wortlogik soll in einem eigenen Sync-Manager sitzen.
6. Halte Letter-Highlights im Inneren des Wortspans, damit die aeusseren Zeitdaten und Event-Handler unbeschaedigt bleiben.
7. Fuehre Scrollen nur kontrolliert und situationsabhaengig aus, nicht bei jedem Wortwechsel blind.

## 16. Minimale Nachbau-Architektur

Fuer ein neues Projekt wuerde ich die CORAPAN-Idee in dieser reduzierten Form uebernehmen:

### A. Datenvertrag

```json
{
  "segments": [
    {
      "speaker": "spk1",
      "words": [
        { "text": "hola", "start_ms": 1200, "end_ms": 1540 },
        { "text": "mundo", "start_ms": 1550, "end_ms": 1980 }
      ]
    }
  ]
}
```

### B. DOM-Modell

```html
<span class="word" data-start="1.2" data-end="1.54">hola </span>
```

### C. Laufender Sync-Loop

```js
function animate() {
  if (!isPlaying) return;
  updateWordsHighlight(audio.currentTime);
  requestAnimationFrame(animate);
}
```

### D. CSS-Zustaende

- `.is-past`
- `.is-current`
- `.is-future`
- `.is-active-group-context`
- `.is-preview-group`

Mehr braucht man fuer den Kern zunaechst nicht.

## 17. Technische Einschraenkungen der aktuellen Loesung

Ein paar Punkte sind beim Nachbau bewusst zu entscheiden:

- `updateWordsHighlight()` iteriert aktuell pro Frame ueber alle `.word`-Elemente. Das ist fuer normale Transkriptgroessen akzeptabel, aber bei sehr langen Dokumenten koennte ein Index oder Cursor-Cache sinnvoll werden.
- Die Letter-Markierung arbeitet ueber `innerHTML`-Manipulation. Das ist pragmatisch und funktioniert hier, ist aber grundsaetzlich fragiler als ein modellbasiertes Rendern.
- Der Player verarbeitet aktiv `token_id`, aber nicht `#t=`-Hash-Startzeiten.
- Es existiert eine aeltere bzw. alternative Controller-Datei `player-main.js`; aktiv ist jedoch die `entry.js -> player-init.js`-Kette.

## Fazit

Die entscheidende technische Idee in CORAPAN ist nicht einfach "Wortzeiten aus JSON lesen", sondern diese drei Dinge gleichzeitig richtig zu kombinieren:

- Wortweise DOM-Struktur mit Zeitdaten direkt am Element
- visuelle Zustandsmaschine mit mehreren parallelen Klassen statt nur einem Highlight
- kontinuierlicher Sync per `requestAnimationFrame`

Die Buchstabenmarkierung ist davon sauber entkoppelt, weil sie nur innere Teilbereiche eines Wortes mit `.highlight` umschliesst, waehrend das aeussere Wort-Element seine Sync-Semantik behaelt.

Wenn du dieses Muster uebernimmst, bekommst du nicht nur eine funktionierende Audio-Text-Kopplung, sondern genau die Art von flussiger, lesbarer Wiedergabe, die auf der Player-Seite den hochwertigen Eindruck erzeugt.