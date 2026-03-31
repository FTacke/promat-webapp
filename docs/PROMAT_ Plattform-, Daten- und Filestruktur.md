---
tags: promat, Pronunciation Matters, webdesign
---

# PROMAT: Plattform-, Daten- und Filestruktur

## 1. Grundprinzip

PROMAT wird so aufgebaut, dass

- die UI zunächst auf Deutsch erscheint
- später parallel eine englische UI ergänzt werden kann
- Routing, technische Keys, Datenfelder und Controlled Vocabularies intern konsequent auf Englisch basieren
- sensible Daten strikt von Forschungsdaten und öffentlich zugänglichen Inhalten getrennt bleiben
- die Webapp nie auf Klardaten zugreift

Die Plattform trennt damit klar zwischen

- UI-Sprache
- technischer Struktur
- Datenarchitektur
- Dateisystem
- Zugriffsrechten

---

## 2. Plattformstruktur

### Hauptnavigation

UI-Labels können lokalisiert werden.

Deutsch:

- Projekt
- Forschung
- Unterricht
- Sample

Englisch:

- Project
- Research
- Teaching
- Sample

Interne Keys:

```text
project
research
teaching
sample
````

---

## 3. Routing-Prinzip

Die URL enthält vier Ebenen:

```text
/{ui_lang}/{section}/{corpus_language}/{page}
```

Bedeutung:

* `ui_lang` = Sprache der Benutzeroberfläche
  z. B. `de`, `en`

* `section` = Plattformbereich
  z. B. `project`, `research`, `teaching`, `sample`

* `corpus_language` = Sprache des Korpus bzw. Teilbereichs
  z. B. `spanish`, `french`, `german`, `english`

* `page` = Seitentyp
  z. B. `design`, `speakers`, `recordings`, `comparison`, `phenomena`

Beispiele:

```text
/de/research/spanish
/de/research/spanish/speakers

/en/research/spanish
/en/research/spanish/speakers
```

Wichtig:

* `de` und `en` steuern nur die UI-Sprache
* `spanish` bezeichnet das spanische Korpus
* die technische Routenstruktur bleibt in allen UI-Sprachen gleich
* Slugs bleiben durchgehend englisch

---

## 4. Forschung: Sitemap

### Konzeptuelle Struktur

```text
/{ui_lang}/research
/{ui_lang}/research/{language}
/{ui_lang}/research/{language}/design
/{ui_lang}/research/{language}/speakers
/{ui_lang}/research/{language}/recordings
/{ui_lang}/research/{language}/comparison
/{ui_lang}/research/{language}/phenomena
```

### Aktueller Ausbau

* `/de/research`
  → Sprachauswahl (Spanisch, Französisch, Deutsch, Englisch)

* `/de/research/spanish`
  → Korpus-Startseite

  * `/de/research/spanish/design`
  * `/de/research/spanish/speakers`
  * `/de/research/spanish/recordings`
  * `/de/research/spanish/comparison`
  * `/de/research/spanish/phenomena`

* `/de/research/french`

* `/de/research/german`

* `/de/research/english`

Aktuell dient Spanisch als Referenzimplementierung. Die gleiche Struktur soll später für die anderen Sprachen übernommen werden.

---

## 5. Zugriffslogik (Forschung)

Öffentlich:

* `design`

Geschützt (Login erforderlich):

* `speakers`
* `recordings`
* `comparison`
* `phenomena`

Die Zugriffslogik ist unabhängig von der UI-Sprache.

---

## 6. Forschung: Seitenlogik des Korpus

Das Korpus ist über mehrere gleichwertige Zugänge erschlossen.
Alle Seiten greifen auf denselben Datenbestand zu, folgen aber unterschiedlichen Zugriffslogiken.

### `speakers`

Zugang über Personen

### `recordings`

Zugang über Aufgabentypen

### `comparison`

itembasierter Vergleich über mehrere Sprecher:innen hinweg

### `phenomena`

linguistisch motivierter Zugang über Kategorien und Phänomene

### `design`

frei zugängliche Dokumentation der methodischen Anlage

---

## 7. Forschung: Seitentypen im Detail

### Startseite: `/{ui_lang}/research/spanish`

Zweck:

* Orientierung im Korpus
* kurze Einführung in Inhalt und Nutzung

Inhalt:

* knapper Beschreibungstext
* Hinweis auf unterschiedliche Zugänge
* Verweis auf `design`

Keine interaktiven Elemente, keine Datenanzeige.

---

### `design`: `/{ui_lang}/research/spanish/design`

Zweck:

* Dokumentation der sprachspezifischen Anlage des Korpus

Inhalt:

* isolierte Aussprache (Wortliste)
* zusammenhängende Aussprache (Text/Sätze)
* Interview (kurze Reflexion)
* Auswahlprinzipien und Itemstruktur
* Bezug zu bestehender Forschung
* sprachspezifische Entscheidungen des Teilprojekts

Keine Interaktion.

---

### `speakers`: `/{ui_lang}/research/spanish/speakers`

Zweck:

* Zugang zu Aufnahmen über Personen

Aufbau:

#### Übersicht

* card-basierte Darstellung
* reduzierte Metadaten, z. B.:

  * ID
  * level
  * L1
  * ggf. weitere zentrale Informationen

#### Interaktion

* direkte Aktionen pro Person:

  * isolierte Aussprache (Wortliste)
  * zusammenhängende Aussprache (Text/Sätze)
  * Interview (kurze Reflexion)

Diese führen jeweils zur Player-Seite.

#### Filter

* nach zentralen Merkmalen, z. B.:

  * level
  * L1
  * speaker_type
  * gender
  * standard_variety

#### Tabellenansicht (optional)

* vollständige Metadaten
* für detaillierte Analyse

---

### `recordings`: `/{ui_lang}/research/spanish/recordings`

Zweck:

* Zugang zu Daten über Aufgabentypen

Struktur:

#### isolierte Aussprache (Wortliste)

* einzelne Wörter
* Fokus auf segmentale und prosodische Aspekte

#### zusammenhängende Aussprache (Text/Sätze)

* Aussprache im Kontext zusammenhängender Sprache

#### Interview (kurze Reflexion)

* kurze metasprachliche Aussagen oder Reflexionen

Interaktion:

* Auswahl eines Aufgabentyps
* danach Auswahl einer Sprecher:in
* danach Player-Seite mit vollständiger Aufgabe

Keine Vergleichsfunktion auf dieser Seite.

---

### `comparison`: `/{ui_lang}/research/spanish/comparison`

Zweck:

* kontrastive Analyse über Sprecher:innen hinweg

Aufbau:

* grid- oder tabellenbasiertes Interface

  * Zeilen: Items
  * Spalten: Sprecher:innen

Interaktion:

* Klick auf ein Item spielt Audio direkt inline ab

Kein Seitenwechsel, kein eigener Player im engeren Sinn.

---

### `phenomena`: `/{ui_lang}/research/spanish/phenomena`

Zweck:

* Zugang über linguistische Kategorien

Struktur:

#### Auswahl eines Phänomens

* Liste von Aussprachephänomenen

#### Anzeige zugeordneter Items

* Items, die das Phänomen potenziell enthalten

Interaktion:

* Auswahl von Item und ggf. Sprecher:innen
* Audio wird inline abgespielt

Wichtiger Hinweis:

* Zuordnung ist heuristisch
* sie garantiert keine eindeutige Realisierung des Phänomens

---

## 8. Übergreifende Logik der Audiowiedergabe

Es gibt zwei Modi:

### Inline-Audio

Verwendung bei:

* `comparison`
* `phenomena`

Eigenschaft:

* direktes Abspielen ohne Seitenwechsel

### Player-Seite

Verwendung bei:

* `speakers`
* `recordings`

Eigenschaft:

* vollständige Aufgabe mit Kontext

Jede Seite folgt genau einer Zugriffslogik und mischt diese nicht.

---

## 9. Data Architecture: Grundprinzip

PROMAT trennt strikt zwischen

* Klardaten
* pseudonymisierten Forschungsdaten
* öffentlich freigegebenen Medien
* Webapp-Code
* Verarbeitungsskripten

Die zentrale Regel lautet:

* die Webapp greift nie auf `/secure/` zu
* geschützte Forschungsdaten liegen unter `/data/`
* frei zugängliche Medien liegen unter `/public/`

---

## 10. Projektstruktur im Filesystem

```text
/promat/
  /secure/           ← nie für Webapp zugänglich
  /data/             ← geschützte Forschungsdaten
    research.db
    /sessions/
  /public/           ← frei zugängliche Medien (Unterricht, Sample)
  /app/              ← Webapp
  /scripts/          ← Verarbeitung, Import, Ableitungen
```

### Logik der Hauptordner

#### `/secure/`

Enthält Klardaten und Re-Identifikationsinformationen, z. B.:

* Name
* Kontakt
* Einwilligung
* Fragebögen
* Zuordnung zu `person_id`

Dieser Bereich ist strikt geschützt und nicht Teil der Webapp.

#### `/data/`

Enthält alle pseudonymisierten Forschungsdaten und Sessions.

Dieser Bereich ist die einzige Datenquelle der Webapp für geschützte Forschungsbereiche.

#### `/public/`

Enthält ausschließlich bewusst freigegebene Dateien, z. B.:

* Unterrichtsaudios
* Sample-Dateien
* frei sichtbare Medien

Freie Inhalte werden nicht direkt aus `/data/` bedient, sondern gezielt nach `/public/` exportiert.

#### `/app/`

Enthält Frontend, Backend, API und UI-Logik.

#### `/scripts/`

Enthält alle Verarbeitungsschritte, z. B.:

* Import
* Session-Anlage
* Audio-Konvertierung
* Annotationsexporte
* Ableitung von Item-Dateien
* Export nach `/public/`

---

## 11. Datenebenen

### Secure Layer

Enthält Klardaten und Re-Identifikationsdaten.

Beispielhafte Felder:

```text
person_id
name
contact
consent
questionnaire
```

Eigenschaften:

* einzige Stelle, an der reale Personen identifizierbar sind
* stark eingeschränkter Zugriff

---

### Research Layer

Enthält pseudonymisierte Forschungsdaten.

Beispielhafte Felder:

```text
person_id
session_id
pseudonymized metadata
```

Eigenschaften:

* zentrale Arbeits- und Analysebasis
* keine Klardaten

---

### Asset Layer

Enthält technische Dateien zu Sessions.

Beispielhafte Felder:

```text
session_id
files
```

Eigenschaften:

* vollständig über `session_id` organisiert
* Audio, TextGrid, JSON und Derivate

---

## 12. Zentrale IDs

### `person_id`

Format:

```text
P-0001
P-0002
```

Eigenschaften:

* eindeutig
* anonym
* stabil
* sprachunabhängig
* verknüpft mehrere Sessions derselben Person

---

### `session_id`

Die `session_id` beschreibt eine konkrete Aufnahme.

#### Lerner:innen

Format:

```text
[TARGET_LANGUAGE]-L-[L1]-[LEVEL]-[YEAR]-[NNN]
```

Beispiele:

```text
ES-L-DE-B2-24-001
FR-L-DE-B1-24-007
EN-L-DE-C1-25-003
DE-L-AR-B2-25-002
```

#### Native Speaker

Format:

```text
[TARGET_LANGUAGE]-N-[STANDARD_VARIETY]-[YEAR]-[NNN]
```

Beispiele:

```text
ES-N-ES_STD-24-001
ES-N-MX_STD-24-002
EN-N-GB_STD-24-001
EN-N-US_STD-24-002
FR-N-FR_STD-24-001
DE-N-DE_STD-24-001
```

#### Heritage Speaker

Format:

```text
[TARGET_LANGUAGE]-H-[L1]-[LEVEL]-[YEAR]-[NNN]
```

Beispiel:

```text
ES-H-DE-B2-25-001
```

Hinweis:

* `H` ist nur zu verwenden, wenn `heritage_speaker` als eigener Sprecherstatus geführt wird
* wenn das nicht gewünscht ist, kann auch `speaker_type` ausschließlich als Metadatum geführt werden

---

## 13. Bedeutung der Session-Segmente

```text
TARGET_LANGUAGE
SPEAKER_MARKER
L1 or STANDARD_VARIETY
LEVEL
YEAR
NNN
```

Bedeutung:

* `TARGET_LANGUAGE`: ES / FR / EN / DE
* `SPEAKER_MARKER`: L / N / H
* `L1`: Erstsprache, z. B. DE, AR, FR
* `STANDARD_VARIETY`: z. B. ES_STD, MX_STD, GB_STD, US_STD
* `LEVEL`: A1–C2, immer ein einzelner Wert
* `YEAR`: zweistellig, z. B. 24, 25
* `NNN`: laufende Nummer innerhalb der Gruppe

---

## 14. Nummernvergabe

Die laufende Nummer `NNN` wird gruppenbasiert vergeben.

Schlüssel:

```text
(TARGET_LANGUAGE, SPEAKER_MARKER, PROFILE, YEAR)
```

Beispiel:

```text
(ES, L, DE-B2, 24)
```

Daraus ergeben sich dann z. B.:

```text
ES-L-DE-B2-24-001
ES-L-DE-B2-24-002
ES-L-DE-B2-24-003
```

Regeln:

* keine globale Zählung
* keine chronologische Bedeutung
* unabhängig vom Aufnahmezeitpunkt
* neue Sessions werden in ihrer jeweiligen Gruppe fortlaufend ergänzt

---

## 15. Umgang mit mehrfachen Aufnahmen derselben Person

Mehrere Aufnahmen derselben Person werden nicht über die `session_id`, sondern über die `person_id` verknüpft.

Beispiel:

```text
person_id = P-0012

ES-L-DE-B1-24-003   → erste Aufnahme
ES-L-DE-C1-26-001   → zweite Aufnahme
```

Die zeitliche Einordnung erfolgt primär über das Jahr in der `session_id` und zusätzlich über Metadaten.

Optionale Felder:

```text
recording_date
context
```

`context` bleibt kontrolliert und knapp:

```text
baseline
follow_up
```

Was zwischen den Aufnahmen passiert ist, wird nicht im Feld `context`, sondern an anderer Stelle dokumentiert, z. B. über Exposure-Daten und Notizen.

---

## 16. Core Data Fields

### Person

```text
person_id
l1
gender
birth_year
current_region
childhood_region
```

### Session

```text
session_id
person_id
target_language
speaker_type
level_code
level_self
recording_year
recording_date
context
standard_variety
notes
```

---

## 17. Controlled Vocabularies

### `gender`

```text
female
male
diverse
unknown
```

---

### `speaker_type`

```text
learner
native_speaker
heritage_speaker
```

---

### `target_language`

```text
es
fr
en
de
```

---

### `level_code`

```text
A1
A2
B1
B2
C1
C2
```

Regel:

* `level_code` enthält immer genau einen Wert

---

### `level_self`

```text
A1
A2
B1
B2
C1
C2
A1-A2
B1-B2
B2-C1
```

Regel:

* wenn die Selbsteinschätzung als Spannweite vorliegt, bleibt diese in `level_self` erhalten
* in der `session_id` und in `level_code` wird immer der niedrigere Wert verwendet

Beispiel:

```text
level_self = B1-B2
level_code = B1
```

---

### `context`

```text
baseline
follow_up
```

---

### `standard_variety`

#### Spanish

```text
es_std
mx_std
ar_std
co_std
cl_std
```

#### English

```text
gb_std
us_std
au_std
nz_std
```

#### French

```text
fr_std
ca_std
ch_std
be_std
```

#### German

```text
de_std
at_std
ch_std
de_south_std
```

Hinweis:

* feinere Differenzierungen können über Metadaten ergänzt werden
* Herkunftsregionen werden nicht in der `session_id` kodiert

---

## 18. Sprachbiographie und Exposure

### Strukturierte Felder

```text
country
duration_months
type
```

### `type`

```text
study
erasmus
work
travel
family
other
```

### Freitextfeld

```text
exposure_notes
```

Regel:

* Exposure wird möglichst strukturiert erfasst
* komplexe oder schwer kategorisierbare Fälle können zusätzlich in `exposure_notes` beschrieben werden

---

## 19. Tasks

Die Aufgabentypen werden intern sprachübergreifend mit stabilen englischen Keys geführt.

```text
isolated_speech
connected_speech
interview
```

Bedeutung:

* `isolated_speech`
  einzelne Wörter oder vergleichbare isolierte Einheiten
  UI-Label:

  * Deutsch: isolierte Aussprache (Wortliste)
  * Englisch: isolated speech (wordlist)

* `connected_speech`
  Text, Satzliste oder andere Formen zusammenhängender Aussprache
  UI-Label:

  * Deutsch: zusammenhängende Aussprache (Text/Sätze)
  * Englisch: connected speech (text/sentences)

* `interview`
  kurze Reflexion oder metasprachliches Interview
  UI-Label:

  * Deutsch: Interview (kurze Reflexion)
  * Englisch: interview (short reflection)

---

## 20. Session-basierte Filestruktur

Alle zu einer Session gehörigen Dateien werden in einem gemeinsamen Session-Ordner abgelegt.

```text
/data/sessions/{language}/{session_id}/
  metadata.json
  /raw/
  /source/
  /alignment/
  /derived/
  /items/
```

### Bedeutung der Unterordner

#### `raw/`

* originale WAV-Dateien
* unbearbeitet
* werden nie überschrieben
* Master-Dateien

#### `source/`

* bereinigte WAV-Dateien
* Arbeitsbasis für Annotation und weitere Verarbeitung
* z. B. standardisierte Pausen, entfernte Störgeräusche

#### `alignment/`

* TextGrid
* Annotationen
* ggf. weitere Alignments oder JSON-basierte Segmentdaten

#### `derived/`

* abgeleitete Dateien für die Webapp
* z. B. MP3-Dateien

#### `items/`

* gesplittete Item-Dateien
* z. B. Einzel-MP3s für Vergleichs- und Analysewerkzeuge

#### `metadata.json`

* kompakte sessionbezogene Metadaten für technische Nutzung

---

## 21. Dateibenennung

Da der Ordner bereits die `session_id` trägt, sollen Dateinamen innerhalb des Session-Ordners kurz und funktional bleiben.

Beispiele:

```text
/source/isolated_speech.wav
/source/connected_speech.wav
/source/interview.wav

/alignment/isolated_speech.TextGrid
/alignment/connected_speech.TextGrid
/alignment/interview.TextGrid

/derived/isolated_speech.mp3
/derived/connected_speech.mp3
/derived/interview.mp3
```

Für Items:

```text
/items/isolated_speech/001_casa.mp3
/items/isolated_speech/002_perro.mp3
/items/connected_speech/001.mp3
```

---

## 22. Files: technische Felder

### `file_role`

```text
audio_raw
audio_source
audio_mp3
textgrid
items_audio
items_json
metadata
```

### `format`

```text
wav
mp3
textgrid
json
```

### `status`

```text
raw
processed
aligned
checked
final
```

---

## 23. Items für Vergleichstools

### `item`

```text
item_id
task_type
label
position
```

### `item_instance`

```text
session_id
item_id
start_time
end_time
file
```

Regel:

* Items sollen stabile `item_id`s erhalten
* `item_id` ist von konkreten Dateinamen getrennt zu führen
* Vergleichstools arbeiten auf Basis von `item_id` + `session_id`

---

## 24. Leitprinzipien

* IDs sind kurz, eindeutig und stabil
* sensible Daten erscheinen nie in IDs oder Dateinamen
* interne Felder und Werte sind immer Englisch
* UI-Labels sind lokalisierbar
* Routing bleibt englisch und sprachneutral
* `person_id` verknüpft Personen über mehrere Sessions hinweg
* `session_id` beschreibt konkrete Aufnahmen
* `raw` bleibt unverändert
* `source`, `derived` und `items` sind verarbeitete bzw. ableitbare Daten
* freie Inhalte werden bewusst nach `/public/` exportiert
* die Webapp greift nie auf `/secure/` zu

---

## 25. Status dieses Dokuments

Dieses Dokument ist die verbindliche Referenz für

* Plattformstruktur
* Routing
* Datenarchitektur
* ID-Logik
* Controlled Vocabularies
* Dateisystem
* Session- und File-Konventionen

Weitere Arbeiten an Webapp, Datenimport, Annotation, Audioverarbeitung und Metadatenmodellierung sollen sich an dieser Spezifikation orientieren.
