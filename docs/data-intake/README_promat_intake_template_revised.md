# README: Intake-Arbeitsmappe für PROMAT

Diese Arbeitsmappe dient der strukturierten Erfassung von Intake-Daten für PROMAT.

Sie ist eine Intake-Vorlage und eine Arbeitsgrundlage für die spätere Datenübernahme. Sie ist nicht die endgültige Forschungsdatenbank.

Wichtig:

- Klardaten stehen nur im Blatt `Secure_Person_Intake`.
- Pseudonymisierte Forschungsdaten stehen nur in den Research-Blättern.
- `person_id` verbindet die Blätter.
- `person_id` plus `session_ref` verbinden `Research_Session_Intake` und `Exposure`.
- `session_id` wird im Intake nicht manuell vergeben, sondern später automatisch erzeugt.
- Nicht jedes Feld muss ausgefüllt werden.
- Manche Felder müssen bewusst leer bleiben, wenn etwas nicht zutrifft.
- `unknown` wird nur verwendet, wenn eine Information grundsätzlich relevant wäre, aber unbekannt ist.

## Blätter in dieser Reihenfolge

1. `Secure_Person_Intake`
2. `Research_Person`
3. `Research_Session_Intake`
4. `Exposure`
5. `Vocabularies`

---

## 1. ID-Logik

### `person_id`

Jede Person erhält eine stabile, korpusspezifische `person_id`.

Beispiele:

- `ES-L-0001`
- `ES-N-0001`
- `EN-L-0001`
- `FR-N-0001`

Bedeutung:

- Korpus bzw. Zielsprache
- Sprecher:innentyp
- fortlaufende Nummer

Die kanonische Form ist:

`{CORPUS_CODE}-{SPEAKER_MARKER}-{NNNN}`

Beispiele für Marker:

- `L` = learner
- `N` = native_speaker

Wichtig:

- `person_id` ist korpusspezifisch.
- Dieselbe reale Person könnte in einem anderen Sprachkorpus eine andere `person_id` haben.
- Eine globale Forschungs-ID wird in dieser Arbeitsmappe nicht geführt.

### `session_ref`

`session_ref` ist die lokale Session-Referenz im Intake.

Beispiele:

- `S01`
- `S02`
- `S03`

Wichtig:

- `session_ref` wird im Intake gesetzt.
- `session_ref` ist nicht die finale `session_id`.
- `session_ref` dient zusammen mit `person_id` der Verknüpfung von `Research_Session_Intake` und `Exposure`.

### `session_id`

Die finale `session_id` wird später automatisch erzeugt.

Beispiele:

- `ES-L-0001-2026-S01`
- `ES-L-0001-2027-S02`

Bedeutung:

- `person_id`
- `recording_year`
- `session_ref`

Wichtig:

- `session_id` im Intake leer lassen.
- `session_id` nicht manuell ausdenken.
- Informationen wie L1, Niveau oder Standardvarietät gehören nicht in die `session_id`.

---

## 2. Grundregeln für leere Felder und `unknown`

### Leere Felder sind oft korrekt

Nicht jedes leere Feld ist ein Fehler.

Beispiele:

- kein Exposure vorhanden → keine Zeile in `Exposure`
- `standard_variety` bei Lernenden → leer
- `level_self` bei Native Speakers → leer
- `level_code` bei Native Speakers → leer
- `context` bei Native Speakers in der Regel → leer
- `additional_languages` → leer, wenn nicht erhoben
- `origin_country` und `origin_region` bei Lernenden → oft leer
- `current_region` und `childhood_region` bei Native Speakers → oft leer

### `unknown` nur bei wirklich unbekannten, aber relevanten Angaben

Richtig:

- Geburtsjahr unbekannt → `unknown`
- `mother_l1` relevant, aber unbekannt → `unknown`
- `father_l1` relevant, aber unbekannt → `unknown`
- Exposure vorhanden, aber Land unbekannt → `country = unknown`

Nicht richtig:

- kein Exposure → keine Zeile
- Standardvarietät bei Lernenden nicht relevant → Feld leer
- Level bei Native Speakers nicht relevant → Feld leer

---

## 3. Blatt: `Secure_Person_Intake`

Dieses Blatt enthält die Klardaten und organisatorischen Secure-Angaben.

Nur hier dürfen Klarnamen stehen.

### Zweck

- Identität der Person
- Consent- und Fragebogenbezug
- Erfassungs- und Prüfstatus
- organisatorische Hinweise

### Spalten in exakt dieser Reihenfolge

```text
person_id
last_name
first_name
email
consent_signed
consent_date
consent_file
questionnaire_file
paper_original_location
intake_date
intake_by
needs_review
verified_by
verified_date
secure_notes
````

### Hinweise

* `person_id` muss eindeutig sein und dem neuen Schema folgen.
* `email` leer lassen, wenn keine E-Mail erhoben wurde.
* `paper_original_location` nur ausfüllen, wenn es tatsächlich Papieroriginale gibt.
* `verified_by` und `verified_date` bleiben leer, bis der Fall geprüft wurde.

---

## 4. Blatt: `Research_Person`

Dieses Blatt enthält stabile, pseudonymisierte Personendaten.

Hier dürfen keine Klarnamen stehen.

### Zweck

* sprecherbezogene Grunddaten
* Sprachbiographie
* personenbezogene Vergleichsmerkmale

### Spalten in exakt dieser Reihenfolge

```text
person_id
speaker_type
l1
mother_l1
father_l1
additional_languages
gender
birth_year
current_region
childhood_region
origin_country
origin_region
needs_review
person_notes
```

### Hinweise

* `speaker_type` ist ein Personenmerkmal und steht deshalb hier.
* `l1`, `mother_l1` und `father_l1` verwenden dieselbe L1-Werteliste wie `l1_code` im Blatt `Vocabularies`.
* `additional_languages` ist eine Sammelspalte für weitere regelmäßig verwendete oder gelernte Sprachen.
* `current_region` und `childhood_region` sind vor allem für Lernende relevant.
* `origin_country` und `origin_region` sind vor allem für Native Speakers relevant.
* Wenn eine Information nicht erhoben wurde und nicht zwingend relevant ist, Feld leer lassen.
* Wenn eine Information relevant, aber unbekannt ist, `unknown` verwenden.
* `needs_review = yes`, wenn eine Angabe widersprüchlich, unklar oder schwer kodierbar ist.

---

## 5. Blatt: `Research_Session_Intake`

Dieses Blatt enthält die konkrete Aufnahme-Session.

Eine Person kann mehrere Sessions haben. Für Native Speakers gilt in der Regel nur eine Session.

### Zweck

* sessionbezogene Metadaten
* Grundlage für die spätere Generierung der `session_id`

### Spalten in exakt dieser Reihenfolge

```text
person_id
session_ref
session_id
target_language
standard_variety
level_self
level_code
recording_year
recording_date
recorded_by
context
needs_review
session_notes
```

### Hinweise

* `person_id` steht zuerst, danach `session_ref`.
* `session_ref` im Intake setzen, z. B. `S01`.
* `session_id` leer lassen.
* `target_language` verwendet die kontrollierten Werte aus `Vocabularies`.
* `standard_variety` ist vor allem für Native Speakers relevant.
* `level_self` und `level_code` sind vor allem für Lernende relevant.
* `recording_year` ist wichtig, weil es später in die `session_id` eingeht.
* `recording_date` leer lassen, wenn das genaue Datum nicht bekannt ist.
* `recorded_by` möglichst immer ausfüllen.
* `context` nur mit kontrollierten Werten befüllen, z. B. `baseline` oder `follow_up`.
* Wenn `level_self = B1-B2`, dann `level_code = B1`.
* Wenn ein Feld nicht relevant ist, leer lassen, nicht `unknown` eintragen.

---

## 6. Blatt: `Exposure`

Dieses Blatt enthält strukturierte Angaben zu Sprachaufenthalten bzw. Exposure.

Exposure ist sessionbezogen.

### Zweck

* Erfassung von tatsächlichem sprachbezogenem Exposure
* Verknüpfung mit einer konkreten Session im Intake

### Spalten in exakt dieser Reihenfolge

```text
person_id
session_ref
target_language
country
duration_months
exposure_type
exposure_notes
needs_review
```

### Hinweise

* Jede Zeile muss zu einer vorhandenen Kombination aus `person_id` und `session_ref` passen.
* Wenn kein Exposure vorliegt, wird keine Zeile angelegt.
* `country` kann `unknown` sein, wenn Exposure vorliegt, aber das Land nicht bekannt ist.
* `duration_months` leer lassen, wenn die Dauer unbekannt ist und keine verlässliche Angabe vorliegt.
* `exposure_type` nur aus kontrolliertem Vokabular wählen.
* `needs_review = yes`, wenn Angaben unklar oder nur ungefähr ableitbar sind.

---

## 7. Blatt: `Vocabularies`

Dieses Blatt enthält die kontrollierten Werte für die Intake-Felder.

### Zweck

* stabile Dropdown-Werte
* konsistente Eingabe
* Vermeidung von Tippvarianten

### Breites Blatt mit diesen Spalten

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

### Hinweise

* Nur Werte aus diesem Blatt verwenden.
* Für `speaker_type` nur die aktiven Projektwerte `learner` und `native_speaker` pflegen.
* `l1`, `mother_l1` und `father_l1` in `Research_Person` greifen auf dieselbe Werteliste wie `l1_code` zu.
* `l1_code` bleibt uppercase, zum Beispiel `DE`, `ES`, `EN`, `FR`, `IT`, `PT`, `RU`.
* `target_language` verwendet nur die lowercase-Werte `es`, `fr`, `en`, `de`.
* `standard_variety` verwendet nur lowercase snake_case, zum Beispiel `es_std`, `mx_std`, `fr_ch_std`, `de_ch_std`.
* `task_type` soll die konkreten Projektwerte verwenden:

  * `wordlist`
  * `text`
  * `interview`
* Keine parallele zweite Tasklogik mit abstrakteren Werten wie `isolated_speech` oder `connected_speech` verwenden.
* Keine normalisierte Zweitlogik wie `field_name`/`value`/`label`/`sort_order`/`notes` als aktiven Soll-Stand führen.
* `recorded_by` nur dann als kontrolliertes Vokabular pflegen, wenn tatsächlich mit einer festen Liste gearbeitet wird.
* Die kanonische Form für unbekannte Werte ist überall `unknown` in Kleinbuchstaben.

---

## 8. Native Speaker und Learner: was ist unterschiedlich?

### Learner

Typische Merkmale:

* `speaker_type = learner`
* `standard_variety` leer
* `level_self` ausgefüllt, wenn vorhanden
* `level_code` ausgefüllt, wenn ableitbar
* `context` häufig relevant
* `current_region` und `childhood_region` oft relevant
* `origin_country` und `origin_region` oft leer
* `Exposure` häufig möglich
* erwartete Aufgaben: `wordlist`, `text`, `interview`

### Native Speaker

Typische Merkmale:

* `speaker_type = native_speaker`
* genau eine Session pro `person_id`
* `session_ref` in der Regel `S01`
* `standard_variety` ausfüllen
* `level_self` leer
* `level_code` leer
* `context` in der Regel leer
* `current_region` und `childhood_region` meist leer, wenn nicht erhoben
* `origin_country` und `origin_region` relevant
* meist keine `Exposure`-Zeile
* erwartete Aufgaben in der Regel: `wordlist`, `text`
* `interview` in der Regel nicht vorgesehen

---

## 9. Beispiel: Intake für einen Learner

### `Secure_Person_Intake`

```text
person_id: ES-L-0001
last_name: Müller
first_name: Anna
email: anna.mueller@example.org
consent_signed: yes
consent_date: 2026-03-14
consent_file: consent_mueller_anna_2026-03-14.pdf
questionnaire_file: questionnaire_mueller_anna_2026-03-14.pdf
paper_original_location: Ordner A / Fach 3
intake_date: 2026-03-20
intake_by: SHK1
needs_review: no
verified_by:
verified_date:
secure_notes:
```

### `Research_Person`

```text
person_id: ES-L-0001
speaker_type: learner
l1: DE
mother_l1: IT
father_l1: DE
additional_languages: EN; FR
gender: female
birth_year: 2001
current_region: NRW
childhood_region: Bayern
origin_country:
origin_region:
needs_review: no
person_notes:
```

### `Research_Session_Intake`

```text
person_id: ES-L-0001
session_ref: S01
session_id:
target_language: es
standard_variety:
level_self: B1-B2
level_code: B1
recording_year: 2026
recording_date: 2026-03-14
recorded_by: Ana Romero
context: baseline
needs_review: no
session_notes:
```

### `Exposure`

```text
person_id: ES-L-0001
session_ref: S01
target_language: es
country: Spain
duration_months: 6
exposure_type: erasmus
exposure_notes:
needs_review: no
```

### Was bei diesem Learner leer bleibt

* `origin_country`
* `origin_region`
* `standard_variety`
* `session_id`
* `verified_by`
* `verified_date`

Diese Felder bleiben leer, weil sie hier nicht relevant sind oder erst später gefüllt werden.

---

## 10. Beispiel: Intake für einen Native Speaker

### `Secure_Person_Intake`

```text
person_id: ES-N-0001
last_name: García
first_name: Lucía
email:
consent_signed: yes
consent_date: 2026-03-15
consent_file: consent_garcia_lucia_2026-03-15.pdf
questionnaire_file: questionnaire_garcia_lucia_2026-03-15.pdf
paper_original_location:
intake_date: 2026-03-20
intake_by: SHK1
needs_review: no
verified_by:
verified_date:
secure_notes:
```

### `Research_Person`

```text
person_id: ES-N-0001
speaker_type: native_speaker
l1: ES
mother_l1: ES
father_l1: ES
additional_languages:
gender: female
birth_year: 1994
current_region:
childhood_region:
origin_country: Mexico
origin_region: Jalisco
needs_review: no
person_notes:
```

### `Research_Session_Intake`

```text
person_id: ES-N-0001
session_ref: S01
session_id:
target_language: es
standard_variety: mx_std
level_self:
level_code:
recording_year: 2026
recording_date: 2026-03-15
recorded_by: Ana Romero
context:
needs_review: no
session_notes:
```

### `Exposure`

Für diesen Native Speaker wird keine Zeile angelegt.

### Was bei diesem Native Speaker leer bleibt

* `email` wenn nicht erhoben
* `paper_original_location` wenn keine Papierablage geführt wird
* `additional_languages` wenn nicht erhoben
* `current_region`
* `childhood_region`
* `level_self`
* `level_code`
* `context`
* `session_id`
* `verified_by`
* `verified_date`

Außerdem gibt es hier keine `Exposure`-Zeile, weil kein entsprechender Fall erfasst wird.

---

## 11. Dateibenennung für Arbeitsdateien

Die Hilfskräfte legen die Dateien nicht final ins Zielsystem ab. Sie verwenden nur eine einfache Übergangsbenennung.

### Schema

```text
nachname_vorname_task_raw.wav
nachname_vorname_task_source.wav
nachname_vorname_task.TextGrid
```

### Erlaubte `task`-Werte für Lernende

* `wordlist`
* `text`
* `interview`

### Erlaubte `task`-Werte für Native Speakers in der Regel

* `wordlist`
* `text`

### Technische Regeln

* nur Kleinbuchstaben
* keine Leerzeichen
* nur Unterstriche
* Umlaute umschreiben:

  * `ä -> ae`
  * `ö -> oe`
  * `ü -> ue`
  * `ß -> ss`

---

## 12. Typische Fehler, die vermieden werden müssen

* Keine Klarnamen in `Research_Person`, `Research_Session_Intake` oder `Exposure`.
* `session_id` nicht manuell eintragen.
* `session_ref` nicht vergessen.
* Kein `unknown`, wenn etwas einfach nicht zutrifft.
* Bei fehlendem Exposure keine Dummy-Zeile anlegen.
* `speaker_type` nicht in `Research_Session_Intake` eintragen.
* `l1` nicht zusätzlich in `Research_Session_Intake` pflegen.
* `standard_variety` nicht bei Lernenden ausfüllen.
* `level_self` und `level_code` nicht bei Native Speakers ausfüllen.
* `recorded_by` konsistent schreiben.
* Nur kontrollierte Werte aus `Vocabularies` verwenden.

---

## 13. Kurzcheck vor dem Speichern

* `person_id` korrekt und im neuen Schema?
* `speaker_type` in `Research_Person` eingetragen?
* `session_ref` gesetzt?
* `session_id` leer gelassen?
* `recorded_by` eingetragen?
* `standard_variety` nur dort ausgefüllt, wo relevant?
* `level_self` und `level_code` nur bei Lernenden?
* `Exposure` nur bei tatsächlichem Exposure?
* nur kontrollierte Werte aus `Vocabularies` verwendet?
