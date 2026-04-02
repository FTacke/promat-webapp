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

* Wortliste
* Text
* Interview zur Aussprache
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

  * Wortliste
  * Text
  * Interview zur Aussprache

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

#### Wortliste

* einzelne Wörter
* Fokus auf segmentale und prosodische Aspekte

#### Text

* Aussprache im Kontext zusammenhängender Sprache

#### Interview zur Aussprache

* halbgeleitete Gesprächssituation mit spontaner Aussprache

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
[CORPUS_CODE]-[SPEAKER_MARKER]-[NNNN]
```

Beispiele:

```text
ES-L-0001
ES-N-0001
EN-L-0001
FR-N-0001
```

Eigenschaften:

* eindeutig
* anonym
* stabil
* korpus- bzw. zielsprachgebunden
* verknüpft mehrere Sessions derselben Person

---

### `session_id`

Die `session_id` beschreibt eine konkrete Aufnahme.

Format:

```text
{person_id}-{YYYY}-S{NN}
```

Beispiele:

```text
ES-L-0001-2026-S01
ES-L-0001-2027-S02
ES-N-0001-2026-S01
FR-N-0004-2025-S03
```

Hinweis:

* `person_id` ist immer der erste Teil der `session_id`
* `YYYY` ist vierstellig und muss mit `recording_year` übereinstimmen
* `SNN` ist die zweistellige Session-Nummer innerhalb genau dieser Person
* Level, L1 und Standardvarietät bleiben Metadaten und werden nicht in die `session_id` eingebaut

---

## 13. Bedeutung der Session-Segmente

```text
CORPUS_CODE
SPEAKER_MARKER
NNNN

person_id
YYYY
SNN
```

Bedeutung:

* `CORPUS_CODE`: ES / FR / EN / DE
* `SPEAKER_MARKER`: L / N
* `NNNN`: laufende Personnummer innerhalb von Korpuscode plus Sprecherstatus
* `person_id`: vollständige Personen-ID
* `YYYY`: vierstelliges Aufnahmejahr
* `SNN`: laufende Session-Nummer derselben Person

Regel:

* aktive Speaker-Marker sind nur `L` für `learner` und `N` für `native_speaker`
* `H` und `heritage_speaker` sind kein aktiver Projektstandard

---

## 14. Nummernvergabe

Die Personnummer `NNNN` wird innerhalb von `(CORPUS_CODE, SPEAKER_MARKER)` vergeben. Die Session-Nummer `SNN` wird innerhalb genau einer `person_id` vergeben.

Regeln:

* keine Ableitung der Personnummer aus Level, L1 oder Standardvarietät
* keine Gruppierung der Session-Nummer nach Level oder Herkunft
* Follow-up-Aufnahmen derselben Person erhöhen nur `SNN`
* `recording_year` wird sowohl in `session_id` als auch in den Metadaten geführt und muss konsistent bleiben

---

## 15. Umgang mit mehrfachen Aufnahmen derselben Person

Mehrere Aufnahmen derselben Person werden nicht über die `session_id`, sondern über die `person_id` verknüpft.

Beispiel:

```text
person_id = ES-L-0001

ES-L-0001-2026-S01   → erste Aufnahme
ES-L-0001-2027-S02   → zweite Aufnahme
```

Die zeitliche Einordnung erfolgt primär über das Jahr in der `session_id` und zusätzlich über Metadaten.

Optionale Felder:

```text
recording_date
context
recorded_by
```

`context` bleibt kontrolliert und knapp:

```text
baseline
follow_up
```

Was zwischen den Aufnahmen passiert ist, wird nicht im Feld `context`, sondern an anderer Stelle dokumentiert, z. B. über Sprachaufenthalte, strukturierte `exposure_entries` und Notizen.

Für die Webapp bedeutet das verbindlich:

* `speakers` aggregiert pro `person_id`
* es gibt genau eine Profilseite pro Person
* auf dieser Personenseite bleiben alle Sessions sichtbar
* `recordings` bleibt session- und taskbasiert
* Native-Speaker-Vergleichsprofile bleiben ein Sonderfall mit genau einer Session pro nativer `person_id`

Regel:

* `context` bleibt ein technisches Ordnungsfeld und wird in Profilen nicht als Rohwert `baseline` oder `follow_up` sichtbar gezeigt

---

## 16. Core Data Fields

### Person

```text
person_id
l1
mother_l1
father_l1
additional_languages
gender
birth_year
current_region
childhood_region
origin_region
origin_country
```

Regel:

* `current_region` und `childhood_region` sind die aktiven Regionalfelder fuer Lernendenprofile
* `origin_region` und `origin_country` sind die aktiven Herkunftsfelder fuer Native-Speaker-Profile
* `mother_l1` und `father_l1` dokumentieren die sprachbiographische Familienumgebung auf Personenebene
* `additional_languages` speichert eine normalisierte Liste weiterer Sprachen der Person
* das allgemeine Modell kann diese sprachbiographischen Personenfelder technisch fuehren; in den aktiven Native-Speaker-Vergleichsprofilen und den aktuellen Dev-Native-Seeds bleiben `l1`, `mother_l1`, `father_l1` und `additional_languages` jedoch ungenutzt

### ExposureEntry

```text
country
duration_months
type
exposure_notes
```

Regel:

* `exposure_entries` werden in `metadata.json` als Liste von Objekten unter der Session gespeichert
* im Intake-Workbook werden Zeilen des Blatts `Exposure` über `person_id` plus `session_ref` an `Research_Session_Intake` gebunden und danach als `exposure_entries` in die Session-Metadaten serialisiert
* `duration_months` ist ganzzahlig oder `null`
* `type` bleibt technisch englisch, zum Beispiel `erasmus`, `study`, `work` oder `travel`

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
recorded_by
stays_in_target_country
exposure_entries
standard_variety
notes
```

Regel:

* `stays_in_target_country` ist das kanonische boolesche/nullable Summenfeld fuer relevante Aufenthalte im Zielland vor der Aufnahme
* `exposure_entries` dokumentiert die detaillierte Struktur dieser Aufenthalte, wenn solche Informationen vorliegen
* die Runtime arbeitet dafuer mit `stays_in_target_country` und `exposure_entries`; im Intake bleibt das Blatt `Exposure` der kanonische tabellarische Erfassungsort
* Native Speaker werden im aktiven Forschungs-UI primär über `standard_variety`, `origin_country` und `origin_region` als Vergleichsgrößen beschrieben, nicht über lernendenzentrierte Sprachbiographiefelder

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
```

Regel:

* nur `learner` und `native_speaker` sind aktive Projektwerte
* `heritage_speaker` ist kein aktiver Soll-Stand

---

### `target_language`

```text
es
fr
en
de
```

Regel:

* technische Zielsprachenwerte bleiben durchgehend lowercase
* davon getrennt bleiben `person_id`-Segmente wie `ES` oder `FR` uppercase

---

### `l1_code`

```text
DE
ES
EN
FR
IT
PT
RU
```

Regel:

* `l1`, `mother_l1` und `father_l1` greifen auf dieselbe uppercase-Liste wie `l1_code` zurück
* `target_language` und `l1_code` bleiben bewusst unterschiedlich gecased

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

### `yes_no_unknown`

```text
yes
no
unknown
```

Regel:

* `unknown` ist die kanonische aktive Kleinform
* `UNKNOWN` ist kein aktiver Standardwert

---

### `recorded_by`

Freitextfeld fuer die dokumentierte Person oder Rollenbezeichnung, die eine Session aufgenommen bzw. explorativ verantwortet hat.

Regel:

* der technische Feldname bleibt `recorded_by`
* die UI darf dafuer lokalisierte sichtbare Labels wie `Explorator:in` verwenden

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
fr_ch_std
be_std
```

#### German

```text
de_std
at_std
de_ch_std
de_south_std
```

Hinweis:

* `standard_variety` bleibt immer lowercase snake_case
* Schweizer Varietäten werden aktiv disambiguiert als `fr_ch_std` und `de_ch_std`
* `ch_std` ist kein aktiver Standardwert
* feinere Differenzierungen können über Metadaten ergänzt werden
* Herkunftsregionen werden nicht in der `session_id` kodiert

---

### Intake-Workbook `Vocabularies`

Im aktiven Intake bleibt `Vocabularies` ein breites Kontrollblatt mit genau diesen Spalten:

```text
gender
speaker_type
l1_code
target_language
level_code
level_self
standard_variety
context
exposure_type
task_type
recorded_by
yes_no_unknown
```

Regel:

* das breite Blatt ist der einzige aktive Soll-Stand fuer das Intake-Workbook
* eine normalisierte Alternative wie `field_name`/`value`/`label`/`sort_order`/`notes` ist kein aktiver PROMAT-Standard
* `task_type` führt nur `wordlist`, `text`, `interview`
* `recorded_by` wird nur dann als kontrollierte Liste gefuehrt, wenn das Projekt dafuer tatsaechlich feste Werte pflegt

---

## 18. Sprachbiographie und Sprachaufenthalte

### Aktiver Feldanker

```text
stays_in_target_country
exposure_entries
```

Regel:

* `stays_in_target_country` ist das aktive boolesche/nullable Kernfeld fuer die kompakte Ja/Nein/Unbekannt-Zusammenfassung forschungsrelevanter Aufenthalte im Zielland vor der Aufnahme
* Werte sind `true`, `false` oder `null`
* `exposure_entries` enthält bei Bedarf die detaillierte Aufschlüsselung nach `country`, `duration_months`, `type` und `exposure_notes`
* die Webapp verwendet dafuer die UI-Labels `Sprachaufenthalte` bzw. `Stays in target-language country`
* in Profilen werden vorhandene `exposure_entries` sichtbar priorisiert; `stays_in_target_country` bleibt die kompakte Fallback- und Filterinformation
* im Intake-Workbook bleibt `Exposure` der aktive Blattname; ausserhalb dieses Workbook-Kontexts werden fuer Runtime und neue Metadaten die Felder `stays_in_target_country` und `exposure_entries` bevorzugt

### Kompatibilitaet fuer Bestandsdaten

Historische Importquellen duerfen weiterhin generische Exposure-Felder enthalten, zum Beispiel:

```text
previous_exposure
has_previous_exposure
prior_exposure
exposure
exposures
exposure_history
exposure_notes
```

Regel:

* diese Felder gelten nur noch als Kompatibilitaets- oder Importquelle
* neue Seeds und neue `metadata.json`-Dateien sollen `stays_in_target_country` und, wenn vorhanden, strukturierte `exposure_entries` schreiben
* neue Intake-Mappings verwenden dafuer das Blatt `Exposure` mit Bezug auf `person_id` plus `session_ref`
* aus historischen generischen Exposure-Feldern werden beim Import sowohl die Ja/Nein-Zusammenfassung als auch optional detaillierte `exposure_entries` normalisiert

---

## 19. Tasks

Die Aufgabentypen werden intern sprachübergreifend mit stabilen englischen Keys geführt.

```text
wordlist
text
interview
```

Bedeutung:

* `wordlist`
  einzelne Wörter oder vergleichbare isolierte Einheiten
  UI-Label:

  * Deutsch: Wortliste
  * Englisch: wordlist

* `text`
  Text, Satzliste oder andere Formen zusammenhängender Aussprache
  UI-Label:

  * Deutsch: Text
  * Englisch: text

* `interview`
  halbgeleitete Gesprächssituation mit spontaner Aussprache
  UI-Label:

  * Deutsch: Interview zur Aussprache
  * Englisch: interview

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

Normativ:

* `raw/` enthält ausschließlich unbearbeitete Original-WAVs aus der Aufnahme

#### `source/`

* bereinigte WAV-Dateien
* Arbeitsbasis für Annotation und weitere Verarbeitung
* z. B. standardisierte Pausen, entfernte Störgeräusche

Normativ:

* `source/` enthält bearbeitete Arbeits-WAVs mit standardisierten Pausen, Normalisierung oder vergleichbaren Vorverarbeitungsschritten

#### `alignment/`

* TextGrid
* Annotationen
* reduzierte, webapp-taugliche JSON-basierte Segmentdaten der Gesamtaufnahme

Beispiele:

```text
/alignment/wordlist.TextGrid
/alignment/wordlist.json
```

Normativ:

* Alignment-JSON gehört logisch zur Alignment-Ebene der Gesamtaufnahme und nie unter `items/`

#### `derived/`

* abgeleitete Dateien für die Webapp
* z. B. MP3-Dateien

Normativ:

* `derived/` enthält daraus abgeleitete Webformate der Gesamtaufnahme, insbesondere MP3

#### `items/`

* gesplittete Item-Dateien
* z. B. Einzel-MP3s für Vergleichs- und Analysewerkzeuge
* keine Alignment-JSON-Dateien

Normativ:

* `items/{task}/` enthält nur gesplittete Einzel-MP3s

#### `metadata.json`

* kompakte sessionbezogene Metadaten für technische Nutzung

---

## 21. Dateibenennung

Da der Ordner bereits die `session_id` trägt, sollen Dateinamen innerhalb des Session-Ordners kurz und funktional bleiben.

Beispiele:

```text
/source/wordlist.wav
/source/text.wav
/source/interview.wav

/alignment/wordlist.TextGrid
/alignment/wordlist.json
/alignment/text.TextGrid
/alignment/interview.TextGrid

/derived/wordlist.mp3
/derived/text.mp3
/derived/interview.mp3
```

Für Items:

```text
/items/wordlist/es_wordlist_001.mp3
/items/wordlist/es_wordlist_002.mp3
/items/text/es_text_002.mp3
```

Regeln:

* interne Split-Dateinamen basieren auf stabiler `item_id`, nicht auf langen Textlabels
* längere Dateinamen wie `ES-L-DE-B1-26-001_es_wordlist_001_mesa.mp3` sind für Download- oder UI-Logik sinnvoll, aber nicht die interne Pflichtbenennung im Session-Ordner

Hinweis für aktuelle Dev-Beispieldaten:

* die vorhandenen spanischen Beispiel-WAVs sind de facto `source` und nicht `raw`
* sie liegen deshalb fachlich korrekt unter `source/wordlist.wav`
* für diese Beispielsessions liegen aktuell keine echten `raw`-Dateien vor

---

## 22. Files: technische Felder

### `file_role`

```text
audio_raw
audio_source
audio_mp3
textgrid
alignment_json
items_audio
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

## 23. Alignment-JSON und Items für Vergleichstools

### Alignment-JSON der Gesamtaufnahme

`alignment/{task}.json` beschreibt die Segmente der Gesamtaufnahme in reduzierter, webapp-tauglicher Form.

Eigenschaften:

* logisch Teil der Alignment-Ebene, nicht der Items-Ebene
* enthält keine redundanten Session-Metadaten; diese bleiben in `metadata.json`
* enthält nur sprechbezogene Segmente; Pausenintervalle wie `silent` werden nicht übernommen
* dient später für synchronisierte Textanzeige, App-Logik und Item-Splitting

Empfohlene Pipeline:

```text
TextGrid -> alignment JSON -> Item-Splits
```

Regeln:

* spätere Split-Skripte nutzen `alignment/{task}.json` als kanonische Segmentquelle
* spätere Split-Skripte schneiden aus `/source/{task}.wav`, nicht aus MP3-Dateien
* `silent`-Intervalle werden nicht in die reduzierte Alignment-JSON übernommen

### Beispielhafte Item-Felder in der Alignment-JSON

```text
item_id
item_number
text
start_time
end_time
duration
audio_file
```

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
audio_file
```

Regel:

* Items sollen stabile `item_id`s erhalten
* interne Item-Dateinamen folgen der `item_id`, z. B. `es_wordlist_001.mp3`
* längere Download-Dateinamen können `session_id` + `item_id` + Label kombinieren, ohne die interne Speicherung zu verändern
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
* `raw` enthält ausschließlich unveränderte Master-WAVs
* `source` enthält bearbeitete Arbeitsfassungen für Annotation, Alignment-JSON und spätere Splits
* `alignment` enthält TextGrid und reduzierte Alignment-JSON der Gesamtaufnahme
* `derived` enthält abgeleitete Gesamtdateien für die Webapp
* `items` enthält nur Split-MP3s
* aktuelle Dev-Beispiel-WAVs sind `source`-Audio und keine `raw`-Masterdateien
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
