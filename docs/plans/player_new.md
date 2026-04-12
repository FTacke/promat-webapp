---
tags: promat, webdesign, planung
---

# Player_new

Statushinweis: Die aktive Umsetzung dieses Plans ist in den produktiven Player eingeflossen. Maßgeblich für den aktuellen Soll-Zustand ist jetzt `docs/spec/research-player.md`; dieses Dokument bleibt als Design- und Migrationsreferenz erhalten.

## Ziel

Der Player soll von einer task-getrennten Struktur zu einem **gemeinsamen, item-basierten Player** weiterentwickelt werden.

Er soll künftig dieselbe technische Grundlage für folgende Materialtypen nutzen:

- Wortliste
- Satzliste
- echte Textquellen
- gemischte Sets aus Wort- und Satz-/Text-Items

**Interview bleibt vorerst explizit ausgenommen** und wird nicht in diese Vereinheitlichung hineingezwungen.

Der neue Player soll also nicht mehr primär als „Wortlisten-Player“ oder „Text-Player“ gedacht werden, sondern als:

> **Unified Player für sequenziell abspielbare sprachliche Items**

---

## Grundprinzipien

### 1. Datengetrieben, nicht UI-getrieben
Der Player soll nicht aus dem sichtbaren Material erraten, was ein Wort, ein Satz oder ein Text ist.  
Diese Information muss sauber in den Daten und Metadaten vorliegen.

### 2. Eine gemeinsame Player-Architektur
Wortlisten-Items und Satz-/Text-Items sind technisch nah genug beieinander, um auf derselben Player-Grundstruktur zu laufen.

### 3. Text ist keine eigene Player-Welt
Ein echter Text ist **keine andere Player-Anwendung**, sondern eine **zusätzliche Ansicht auf dieselbe Item-Basis**.

### 4. Sets sind Listen, keine Texte
Auch wenn ein Set Items aus einer echten Textquelle enthält, wird ein Set **nicht** als Fließtext rekonstruiert.  
Sets bleiben im Player immer eine **lineare Listendarstellung**.

### 5. Audio-Logik folgt Materialtyp
Nicht jede Materialart bekommt dieselbe Audio-Logik.  
Insbesondere ist die Voll-MP3 bei echten Textquellen fachlich sinnvoll, bei Sets aber nicht die Grundlogik.

---

## Geltungsbereich

### Im Scope
- Vereinheitlichung von Wortliste, Satzliste und Text in einem Player-System
- Unterstützung gemischter Sets aus Wort- und Satz-/Text-Items
- unterschiedliche Views auf gemeinsame Datenbasis
- klare Metadatenregeln für Textfähigkeit, Default-View und Audio-Modus

### Außerhalb des Scopes
- Interview in denselben Player integrieren
- ad hoc automatische Texterkennung ohne Metadaten
- gemischte Sets als Fließtext rendern
- Voll-MP3 für Sets als Standard einführen
- sofortige perfekte Satz-Timing-Synchronisation, falls Timecodes noch nicht vorhanden sind

---

## Zielbild der Architektur

Der neue Player besteht konzeptionell aus mehreren klar getrennten Ebenen:

### 1. Source-Ebene
Beschreibt, **welche Art von Material** geladen wurde.

Beispiele:
- Wortliste
- Satzliste
- echter Text
- Set

### 2. Item-Ebene
Beschreibt die **einzelnen abspielbaren Einheiten**.

Beispiele:
- einzelnes Wort
- einzelner Satz

### 3. View-Ebene
Beschreibt, **wie dasselbe Material dargestellt wird**.

Beispiele:
- Liste
- Text

### 4. Audio-Ebene
Beschreibt, **welcher Audiomodus primär verwendet wird**.

Beispiele:
- Item-Audio
- Voll-Audio

Diese Ebenen dürfen nicht miteinander vermischt werden.

---

## Materialtypen

## Source-Klassen

Folgende Source-Klassen sollen im System explizit unterschieden werden:

- `wordlist`
- `sentence_list`
- `text`
- `set`
- `interview` (vorerst separat, nicht Teil des Unified Players)

### Bedeutung

#### `wordlist`
Sammlung einzelner Wort-Items.

#### `sentence_list`
Sammlung einzelner Satz-Items ohne Anspruch, ein zusammenhängender Fließtext zu sein.

#### `text`
Zusammenhängende Textquelle, die aus Satz-Items besteht, aber zusätzlich als echter Text modelliert ist.

#### `set`
Kuratiertes, benutzerdefiniertes oder phänomenbasiertes Material, das Items aus verschiedenen Quellen zusammenführen kann.

---

## Kernentscheidung zur Vereinheitlichung

### Vereinheitlicht werden
- Wort-Items
- Satz-Items

### Nicht vereinheitlicht werden
- Interview als eigener Modus / eigenes Werkzeug

Begründung:
Wort und Satz sind beide kurze, klar segmentierte Einheiten mit vergleichbarer Navigationslogik.  
Interview ist davon konzeptionell zu weit entfernt.

---

## Datenmodell: Item-Ebene

Jedes im Player darstellbare Element soll als **PlayerItem** normalisiert vorliegen.

## Minimale Item-Struktur

```ts
type PlayerItem = {
  id: string
  item_type: 'word' | 'sentence'
  source_kind: 'wordlist' | 'sentence_list' | 'text' | 'set'
  source_id: string

  label_short?: string
  label_full?: string

  display_text: string
  normalized_text?: string

  order_index: number

  audio_item_url?: string
  audio_item_duration_ms?: number

  text_container_id?: string
  text_order_index?: number

  paragraph_break_before?: boolean
  paragraph_id?: string

  metadata?: Record<string, unknown>
}
````

---

## Bedeutung der wichtigsten Felder

### `id`

Eindeutige ID des Items.

### `item_type`

Nur:

* `word`
* `sentence`

### `source_kind`

Gibt an, aus welcher Materialklasse das Item stammt.

### `source_id`

Verweist auf die konkrete Ursprungsliste / Textquelle / Setquelle.

### `display_text`

Text, der im Player sichtbar gerendert wird.

Beispiele:

* `reloj`
* `El ladrón buscó la llave correcta sin éxito.`

### `order_index`

Reihenfolge innerhalb der aktuell geladenen Sequenz.

### `audio_item_url`

Einzel-Audio des Items, falls vorhanden.

### `text_container_id`

ID der zugehörigen Textquelle, falls das Item Teil eines echten Textes ist.

### `text_order_index`

Satzreihenfolge innerhalb eines echten Textes.

### `paragraph_break_before`

Optionaler Marker für Absatzanfänge bei Textdarstellung.

---

## Datenmodell: Source-Ebene

Neben den Items braucht jede geladene Quelle eine explizite Source-Beschreibung.

## Minimale Source-Struktur

```ts
type PlayerSource = {
  id: string
  source_kind: 'wordlist' | 'sentence_list' | 'text' | 'set'

  title?: string
  subtitle?: string

  default_view: 'list' | 'text'
  allowed_views: Array<'list' | 'text'>

  primary_audio_mode: 'item' | 'full'
  supports_item_audio: boolean
  supports_full_audio: boolean

  full_audio_url?: string
  full_audio_duration_ms?: number

  supports_text_view: boolean

  metadata?: Record<string, unknown>
}
```

---

## Source-Regeln je Materialtyp

### 1. Wortliste

```ts
source_kind = 'wordlist'
default_view = 'list'
allowed_views = ['list']
primary_audio_mode = 'item'
supports_item_audio = true
supports_full_audio = false
supports_text_view = false
```

### 2. Satzliste

```ts
source_kind = 'sentence_list'
default_view = 'list'
allowed_views = ['list']
primary_audio_mode = 'item'
supports_item_audio = true
supports_full_audio = false
supports_text_view = false
```

### 3. Echte Textquelle

```ts
source_kind = 'text'
default_view = 'text'
allowed_views = ['text', 'list']
primary_audio_mode = 'full'
supports_item_audio = true | false
supports_full_audio = true
supports_text_view = true
```

### 4. Set

```ts
source_kind = 'set'
default_view = 'list'
allowed_views = ['list']
primary_audio_mode = 'item'
supports_item_audio = true
supports_full_audio = false
supports_text_view = false
```

Wichtig:
Ein Set bekommt **selbst dann keine Textansicht**, wenn es Items aus einer echten Textquelle enthält.

---

## Entscheidungskriterium: Wann ist etwas ein echter Text?

Das darf **nicht** aus Länge, Satzanzahl oder bloßer Reihenfolge erraten werden.

Eine Quelle gilt nur dann als echter Text, wenn dies in den Daten explizit modelliert ist.

## Empfohlene Metadaten auf Source-Ebene

```ts
type TextSourceMetadata = {
  content_mode: 'sentence_list' | 'connected_text'
  supports_text_view: boolean
  text_title?: string
  text_subtitle?: string
  paragraph_model?: 'none' | 'explicit'
}
```

### Regel

Nur wenn mindestens fachlich eindeutig vorliegt:

* `source_kind = 'text'`
* `content_mode = 'connected_text'`
* `supports_text_view = true`

darf im Player eine Textansicht angeboten werden.

---

## View-Logik

## Verfügbare Views

### `list`

Lineare, item-basierte Darstellung.

### `text`

Zusammenhängende Textdarstellung aus Satz-Items.

---

## Default-View-Regeln

### Wortliste

* Standard: Liste

### Satzliste

* Standard: Liste

### Text

* Standard: Text
* optional umschaltbar auf Liste

### Set

* Standard: Liste
* keine Textansicht

---

## UI-Regeln für den View-Switch

Ein View-Switch wird **nur angezeigt**, wenn die geladene Source mehr als eine erlaubte View hat.

Also praktisch nur bei echten Textquellen:

* `Text`
* `Liste`

### Nicht anzeigen bei

* Wortlisten
* Satzlisten
* Sets

---

## Wichtige UI-Logik

Der View-Switch darf niemals zwei getrennte Datenzustände erzeugen.

Er ist nur ein Wechsel zwischen zwei Darstellungen derselben Sequenz.

Das bedeutet:

* dieselben Items
* dieselbe Reihenfolge
* dieselbe Session
* dieselbe Auswahl
* dieselbe aktive Position
* dieselbe Audiobasis

---

## Verhalten bei echter Textquelle

Wenn eine echte Textquelle geladen wird:

### Standard

* View = `text`
* primärer Audiomodus = Voll-MP3

### Optional

* Umschalten auf `list`
* dort Darstellung als gelistete Satz-Items

### Konsistenzregeln

* Klick auf Satz in Textansicht aktiviert entsprechendes Satz-Item
* Wechsel in Listenansicht zeigt denselben aktiven Satz
* Wechsel zurück in Textansicht markiert denselben Satz weiter

---

## Audio-Logik

## Ziel

Audio darf nicht technisch bequem, sondern muss fachlich sinnvoll gewählt werden.

---

## Audiomodi

### `item`

Abspielen einzelner Item-MP3s.

### `full`

Abspielen einer zusammenhängenden Voll-MP3 der gesamten Quelle.

---

## Primäre Regeln

### Wortliste

* primär `item`

### Satzliste

* primär `item`

### Text

* primär `full`

### Set

* primär `item`

---

## Begründung für Texte = Voll-MP3 primär

Bei echten Textquellen ist der zusammenhängende Vortrag oft fachlich relevant:

* Prosodie über Satzgrenzen hinweg
* Übergänge
* Koartikulation
* natürlicher Sprechfluss
* nicht-harte Segmentierung zwischen Sätzen

Ein Abspielen nur über Einzel-MP3s würde genau diese Eigenschaften oft zerstören.

Daher gilt:

> Wenn ein echter Text vollständig als Text gerendert wird, soll die Voll-MP3 die primäre Audioform sein.

---

## Begründung für Sets = Item-MP3 primär

Sets sind kuratierte Sammlungen, keine originäre zusammenhängende Aufführung.

Auch wenn sie Sätze aus einem Text enthalten, sind sie im Player keine neue Textquelle.

Daher gilt:

> Sets werden audioseitig primär über Einzel-MP3s behandelt.

Keine Grundannahme:

* keine Voll-MP3 für das gesamte Set
* keine künstliche Fließtext-Logik
* keine automatische Rekonstruktion eines Vortragzusammenhangs

---

## Unterstützte Audio-Kombinationen

### Textquelle

Empfohlen:

* Voll-MP3 vorhanden: ja
* Item-MP3s optional: ja

Damit möglich:

* Standardnutzung über Voll-MP3
* gezieltes Springen auf Einzelsätze, falls technisch unterstützt

### Satzliste

* Item-MP3s ja
* Voll-MP3 nein

### Wortliste

* Item-MP3s ja
* Voll-MP3 nein

### Set

* Item-MP3s ja
* Voll-MP3 nein

---

## Synchronisation bei echter Textquelle

## Wunschziel

Wenn eine Textquelle mit Voll-MP3 abgespielt wird, sollte der Player idealerweise wissen, welcher Satz gerade aktiv ist.

## Dafür notwendige optionale Daten

```ts
type SentenceTiming = {
  item_id: string
  start_ms: number
  end_ms?: number
}
```

Oder äquivalent in Sekunden.

---

## Wenn Timecodes vorhanden sind

Dann soll möglich sein:

* aktiven Satz während Voll-Audio markieren
* Klick auf Satz springt an Satzbeginn
* Fortschritt im Text sichtbar machen
* Listenansicht und Textansicht synchron halten

---

## Wenn Timecodes nicht vorhanden sind

Dann gilt als Minimalverhalten:

* Voll-MP3 bleibt primärer Audiomodus
* Text wird vollständig angezeigt
* keine falsche Präzisionssimulation
* Satzklick kann optional deaktiviert bleiben
* oder Satzklick nutzt nur Item-MP3, wenn vorhanden

Wichtig:
Keine Pseudo-Synchronisation vortäuschen, wenn es dafür keine sauberen Daten gibt.

---

## Set-Verhalten

## Grundsatz

Sets verhalten sich im Player immer als **lineare Sequenzen einzelner Items**.

### Erlaubt

* gemischte Wort- und Satz-Items
* Reihenfolge des Sets
* Einzel-MP3 pro Item
* Navigation durch Itemliste

### Nicht erlaubt

* Textansicht des gesamten Sets
* automatische Rekonstruktion von Fließtext
* Voll-MP3 als Set-Standard
* Umschaltung in einen Textmodus

---

## Gründe für die Restriktion bei Sets

### 1. Konzeptionelle Klarheit

Ein Set ist ein kuratiertes Arbeitsmaterial, keine originäre Textquelle.

### 2. Technische Stabilität

Die Textansicht verlangt zusammenhängende Reihenfolge, Metadaten und meist eine eigenständige Audio-Logik.

### 3. Vermeidung falscher Rekonstruktionen

Ein Set kann aus Textbruchstücken, Einzelsätzen und Wörtern bestehen.
Daraus darf kein künstlicher „Text“ erzeugt werden.

---

## Routing- und Ladeverhalten

Der neue Player soll intern vereinheitlicht werden, ohne dass bestehende Nutzerlogik sofort zerstört werden muss.

## Empfohlenes Prinzip

Bestehende Einstiege dürfen zunächst erhalten bleiben, aber intern auf denselben Player-Stack zeigen.

Beispiele:

* Wortlisten-Route lädt Unified Player mit `source_kind = wordlist`
* Satz-/Text-Route lädt Unified Player mit `source_kind = sentence_list` oder `text`
* Set-Route lädt Unified Player mit `source_kind = set`
* Interview bleibt separat

---

## Player-Shell-Konzept

Empfohlene logische Komponenten:

### `PlayerShell`

Verantwortlich für globalen Zustand, Routing, Laden der Source und Player-Session.

### `SourceAdapter`

Normalisiert Rohdaten aus unterschiedlichen Quellsystemen in gemeinsame `PlayerSource`- und `PlayerItem`-Strukturen.

### `SequenceState`

Verwaltet aktive Position, Reihenfolge, Auswahl, Navigation.

### `AudioController`

Verwaltet Item-Audio und Voll-Audio inkl. Umschaltlogik.

### `ViewRenderer`

Entscheidet zwischen Listenansicht und Textansicht.

### `ItemRenderer`

Rendert einzelne Wort- oder Satz-Items innerhalb der Listenansicht.

### `TextRenderer`

Rendert zusammenhängenden Text aus Satz-Items, nur wenn `supports_text_view = true`.

---

## Minimale Normalisierungsanforderung

Bevor Material in den Player gelangt, muss es in ein einheitliches Format transformiert werden.

### Pflichtausgaben des Adapters

* eine `PlayerSource`
* eine geordnete Liste von `PlayerItem[]`

### Verboten

* Player-Komponenten direkt an task-spezifische Rohdaten hängen
* Sonderfälle nur im UI behandeln
* Textfähigkeit erst im Renderer erraten

---

## Darstellung in der Listenansicht

## Einheitliches Ziel

Wort-Items und Satz-Items sollen in derselben Grundlogik darstellbar sein.

Die Unterschiede sind primär:

* Textlänge
* Typografie
* eventuell Label/Metadaten

Nicht grundsätzlich:

* Navigation
* Auswahl
* Audioansteuerung
* Reihenfolge

---

## Darstellung in der Textansicht

Textansicht nur für echte Textquellen.

## Eigenschaften

* vollständiger Text aus geordneten Satz-Items rekonstruiert
* optional unter Berücksichtigung von Absatzmarkern
* aktiver Satz markierbar
* Satzklick optional nutzbar
* kein separater Datenzustand

## Keine Textansicht für

* Satzlisten
* Wortlisten
* Sets

---

## Auswahl- und Statuslogik

Die aktuelle aktive Position im Player muss unabhängig von der View existieren.

Beispiel:

* aktiver Satz ist Satz 7
* Nutzer wechselt von `text` zu `list`
* Satz 7 bleibt aktiv

Dasselbe gilt für:

* Scrollfokus
* Audiofokus
* Markierung
* ggf. Selektion

---

## Umgang mit gemischten Sets

Gemischte Sets sind explizit erlaubt.

## Beispiel

Ein Set kann enthalten:

* Wortliste 26: `ladrón`
* Wortliste 55: `llave`
* Satzliste D19: `El ladrón buscó la llave correcta sin éxito.`

Der Unified Player soll das als normale Sequenz behandeln.

### Darstellungsregeln

* alles in einer Liste
* Reihenfolge nach Set-Reihenfolge
* klare Item-Labels
* keine künstliche Trennung in Subplayer

---

## Empfohlene zusätzliche Set-Metadaten

```ts
type SetItemReference = {
  item_id: string
  origin_source_kind: 'wordlist' | 'sentence_list' | 'text'
  origin_source_id: string
  set_order_index: number
}
```

Optional zusätzlich:

* Phänomenbezug
* Kommentar
* manuell gesetzte Gruppierung

Aber:
Diese Metadaten dürfen **nicht** dazu führen, dass das Set in einen Textmodus kippt.

---

## Fachlich wichtige Entscheidung

Ein Satz aus einer Textquelle bleibt im Set zwar fachlich „aus Text stammend“, aber funktional im Player ein normales Satz-Item innerhalb einer Listenlogik.

Das ist ausdrücklich gewollt.

---

## Mindestanforderungen an Metadaten

Damit die Architektur stabil bleibt, sollten folgende Entscheidungen **nicht implizit**, sondern explizit in den Daten stehen:

### Pflicht auf Source-Ebene

* `source_kind`
* `default_view`
* `allowed_views`
* `primary_audio_mode`
* `supports_item_audio`
* `supports_full_audio`
* `supports_text_view`

### Pflicht auf Item-Ebene

* `id`
* `item_type`
* `display_text`
* `order_index`
* `source_kind`
* `source_id`

### Pflicht für Textquellen zusätzlich

* geordnete Satzreihenfolge
* explizite Kennzeichnung als `text`
* Voll-MP3, falls Textansicht mit zusammenhängendem Audio sinnvoll angeboten werden soll

---

## Was ausdrücklich vermieden werden soll

* Task-spezifische Sonderlogik tief im Player
* „Text“ nur als visuelles Theme statt als explizite Source-Klasse
* Set-Text-Rekonstruktion
* Voll-MP3-Fallbacks ohne fachliche Grundlage
* globale UI-Switches, die auf manchen Quellen sinnlos sind
* automatische Heuristiken wie „viele Sätze = wohl Text“

---

## Migrationsstrategie

## Empfohlene Reihenfolge

### Phase 1: Datenmodell stabilisieren

* gemeinsame `PlayerSource`- und `PlayerItem`-Struktur definieren
* Source-Metadaten für Wortliste, Satzliste, Text und Set festlegen

### Phase 2: SourceAdapter einführen

* bestehende Wortlisten- und Satzlistenquellen normalisieren
* Textquellen explizit als `text` modellieren
* Sets auf gemeinsame Sequenzform bringen

### Phase 3: Unified PlayerShell einführen

* bestehende Routen beibehalten
* intern denselben Player-Stack nutzen

### Phase 4: View-Logik ergänzen

* Textansicht nur für echte Textquellen
* Default-View für Texte = Text
* Sets strikt auf Liste begrenzen

### Phase 5: Audio-Logik schärfen

* Texte mit Voll-MP3 priorisieren
* Sets nur Item-Audio
* optionale Satzsynchronisation ergänzen, wenn Daten vorhanden

---

## Akzeptanzkriterien

Die Umstellung ist fachlich erst dann gelungen, wenn folgende Punkte erfüllt sind:

### A. Vereinheitlichung

* Wortliste und Satzliste laufen auf demselben Player-Grundsystem
* gemischte Sets aus Wort- und Satz-Items sind ladbar

### B. Textlogik

* echte Textquellen öffnen standardmäßig in Textansicht
* Textansicht wird nur angeboten, wenn Metadaten dies erlauben
* Textansicht und Listenansicht greifen auf dieselben Items zu

### C. Setlogik

* Sets öffnen immer in Listenansicht
* Sets können gemischte Items enthalten
* Sets bekommen keine Textansicht

### D. Audiologik

* Wortlisten und Satzlisten nutzen primär Item-Audio
* echte Textquellen nutzen primär Voll-Audio
* Sets nutzen primär Item-Audio

### E. Datenklarheit

* keine heuristische Texterkennung im Frontend
* alle relevanten Entscheidungen aus Source-Metadaten ableitbar

---

## Offene Erweiterungen für später

Diese Punkte sind sinnvoll, aber nicht Voraussetzung für die erste saubere Umsetzung:

* präzise Satz-Timecodes für Voll-MP3
* Absatzlogik in Textansicht
* Deep-Linking auf Satzebene
* persistente View-Präferenzen je Source-Typ
* semantische Gruppierung innerhalb von Sets
* kombinierte Filter für Set-Items
* Highlighting auf Phänomenebene im Player

---

## Kurzfassung der finalen Regeln

### Wortliste

* View: Liste
* Audio: Item
* kein Textmodus

### Satzliste

* View: Liste
* Audio: Item
* kein Textmodus

### Echte Textquelle

* Standard-View: Text
* optionale Zweit-View: Liste
* Audio primär: Voll-MP3
* Item-MP3 optional zusätzlich

### Set

* View: Liste
* Audio: Item
* keine Textansicht
* keine Set-Voll-MP3 als Grundlogik

### Interview

* separat halten

---

## Arbeitsthese für die Umsetzung

Der neue Player ist kein task-basierter Spezialplayer mehr, sondern ein:

> **Unified Item Player mit source-gesteuerter View- und Audio-Logik**

Das ist die fachlich saubere und technisch tragfähige Richtung für die weitere Entwicklung.
