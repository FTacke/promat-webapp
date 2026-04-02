# README: Intake-Arbeitsmappe für PROMAT

Diese Arbeitsmappe dient der strukturierten Erfassung von Teilnehmendendaten und Sitzungsdaten für PROMAT.

Sie ist eine **Intake-Vorlage**, nicht die endgültige Forschungsdatenbank.

Wichtig:

- Klardaten bleiben ausschließlich im **Secure-Bereich**.
- Pseudonymisierte Forschungsdaten werden getrennt davon erfasst.
- Die Arbeitsmappe dient der sauberen Vorbereitung für den späteren Import.
- Nicht jedes Feld muss immer ausgefüllt werden.
- Manche Felder müssen bewusst **leer bleiben**, wenn etwas **nicht zutrifft**.
- `unknown` wird nur verwendet, wenn eine Information **eigentlich relevant wäre, aber unbekannt ist**.

## Grundprinzip

Die Mappe ist in genau diese Blätter gegliedert, in genau dieser Reihenfolge:

1. `Secure_Person_Intake`
2. `Research_Person`
3. `Research_Session_Intake`
4. `Exposure`
5. `Vocabularies`

Jede Person erhält eine stabile `person_id`, zum Beispiel:

- `P-0001`
- `P-0002`

Diese ID verbindet die verschiedenen Blätter miteinander.

## Ganz wichtig vorab

### 1. Klardaten nur im Secure-Blatt

Namen, E-Mail-Adressen und Dateinamen von Einwilligung und Fragebogen dürfen nur im Blatt `Secure_Person_Intake` stehen.

### 2. Pseudonymisierte Daten in die Research-Blätter

Die Blätter `Research_Person`, `Research_Session_Intake` und `Exposure` dürfen keine Klarnamen enthalten.

### 3. Leere Felder sind manchmal richtig

Nicht jedes leere Feld ist ein Fehler.

Beispiele:

- kein Exposure vorhanden → **keine Zeile in `Exposure` anlegen**
- `standard_variety` bei Lernenden → meist **leer**
- `level_code` bei Native Speakers → **leer**
- `recording_date` unbekannt → je nach Projektregel leer lassen

### 4. `unknown` nicht inflationär benutzen

`unknown` nur dann eintragen, wenn eine Information nicht bekannt ist, aber grundsätzlich relevant wäre.

Beispiele:

richtig:
- Geburtsjahr unbekannt → `unknown`
- `mother_l1` relevant, aber unbekannt → `unknown`
- `father_l1` relevant, aber unbekannt → `unknown`

nicht richtig:
- keine Auslandserfahrung → nicht `unknown`, sondern **keine Exposure-Zeile**
- kein passender `standard_variety`-Wert nötig → Feld **leer**

### 5. Umlaute

In Personenfeldern werden Namen normal geschrieben:

- `Müller`
- `Öztürk`

In Dateinamen werden Umlaute technisch vereinfacht:

- `mueller`
- `oeztuerk`

---

# 1. Blatt: `Secure_Person_Intake`

Dieses Blatt enthält die **Klardaten** und den Verweis auf die zugehörigen Secure-Dateien.

Hier dürfen Namen stehen.

## Zweck

Dieses Blatt dokumentiert:

- wer die Person ist
- welche Secure-Dokumente zu ihr gehören
- wer die Daten erfasst hat
- ob der Fall geprüft wurde
- ob noch Klärungsbedarf besteht

## Spalten in exakt dieser Reihenfolge

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
```

## Erläuterung der Felder

### `person_id`
Stabile interne Personen-ID.

Beispiel:
- `P-0001`

### `last_name`, `first_name`
Klarname der Person.

Beispiel:
- `Müller`
- `Anna`

### `email`
Falls erhoben und für eure Verwaltung nötig.

Wenn keine E-Mail vorliegt oder ihr sie nicht erhebt:
- Feld leer lassen

### `consent_signed`
Eintrag nach der vorgegebenen Liste, zum Beispiel:
- `yes`
- `no`
- `unknown`

### `consent_date`
Datum der Einwilligung, wenn bekannt.

Wenn unbekannt:
- nach Projektregel entweder leer lassen
- oder `unknown`, falls das Feld nicht streng als Datumsfeld geführt wird

Wichtig: innerhalb des Projekts immer dieselbe Regel verwenden.

### `consent_file`
Dateiname der Einwilligung im Secure-Ordner.

Beispiel:
- `consent_mueller_anna_2026-03-14.pdf`

### `questionnaire_file`
Dateiname des Fragebogens im Secure-Ordner.

Beispiel:
- `questionnaire_mueller_anna_2026-03-14.pdf`

### `paper_original_location`
Nur wenn zusätzlich Papieroriginale verwaltet werden.

Beispiel:
- `Ordner A / Fach 3`

Falls nicht relevant:
- Feld leer lassen

### `intake_date`
Datum der Erfassung in die Mappe.

### `intake_by`
Kürzel oder Name der Person, die die Daten eingetragen hat.

Beispiele:
- `AB`
- `SHK1`

### `needs_review`
Kennzeichnet Fälle, die noch überprüft werden müssen.

Werte:
- `yes`
- `no`

`yes` verwenden, wenn etwas unklar ist oder nicht sauber zugeordnet werden konnte.

### `verified_by`
Wer den Fall geprüft hat.

Beispiele:
- `SK`
- `PI`

Wenn noch nicht geprüft:
- leer lassen

### `verified_date`
Datum der Prüfung.

Wenn noch nicht geprüft:
- leer lassen

### `secure_notes`
Freitext für organisatorische oder dokumentbezogene Hinweise.

Beispiele:
- Einwilligung nachgereicht
- Scan schwer lesbar
- Name auf Consent abweichend geschrieben

## Beispielzeile

| person_id | last_name | first_name | consent_signed | consent_file | questionnaire_file | intake_by | needs_review | verified_by | verified_date | secure_notes |
|---|---|---|---|---|---|---|---|---|---|---|
| P-0001 | Müller | Anna | yes | consent_mueller_anna_2026-03-14.pdf | questionnaire_mueller_anna_2026-03-14.pdf | AB | no | SK | 2026-03-20 |  |

---

# 2. Blatt: `Research_Person`

Dieses Blatt enthält **pseudonymisierte personenbezogene Forschungsdaten**.

Hier dürfen **keine Klarnamen** stehen.

## Zweck

Dieses Blatt beschreibt die Person auf einer allgemeinen Ebene, unabhängig von einer konkreten Aufnahme.

Hier steht vor allem die stabile Sprachbiographie der Person.

## Spalten in exakt dieser Reihenfolge

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
needs_review
person_notes
```

## Erläuterung der Felder

### `person_id`
Muss mit dem Secure-Blatt übereinstimmen.

Beispiel:
- `P-0001`

### `l1`
Erstsprache der Person gemäß festgelegter Vokabelliste.

Beispiele:
- `DE`
- `RU`
- `IT`
- `KU`
- `EL`

Wenn unklar:
- `unknown`

Wenn mehrere Sprachen genannt wurden, aber nur ein Feld für die Haupt-L1 vorgesehen ist:
- die primäre oder dominierende Erstsprache eintragen
- zusätzliche Information in `person_notes` notieren

### `mother_l1`
Erstsprache bzw. Hauptsprache der Mutter gemäß derselben Vokabelliste wie `l1`.

Beispiele:
- `DE`
- `IT`
- `TR`

Wenn unbekannt, aber grundsätzlich relevant:
- `unknown`

### `father_l1`
Erstsprache bzw. Hauptsprache des Vaters gemäß derselben Vokabelliste wie `l1`.

Beispiele:
- `DE`
- `AR`
- `PL`

Wenn unbekannt, aber grundsätzlich relevant:
- `unknown`

### `additional_languages`
Weitere gelernte oder regelmäßig verwendete Sprachen zusätzlich zur Haupt-L1.

Dieses Feld ist eine pragmatische Sammelspalte für die Intake-Mappe.

Empfohlene Schreibweise:
- Codes oder stabile Kurzformen, getrennt durch Semikolon

Beispiel:
- `EN; FR; PT`

Wenn keine weiteren Sprachen erhoben wurden:
- Feld leer lassen

Wenn die Sprachbiographie komplex ist:
- Kurzangabe hier eintragen
- genauere Erläuterung in `person_notes`

### `gender`
Nur Werte aus der Vokabelliste verwenden.

Beispiele:
- `female`
- `male`
- `diverse`
- `unknown`

### `birth_year`
Geburtsjahr, wenn vorhanden.

Beispiel:
- `2001`

Wenn unbekannt:
- `unknown` oder die projektintern festgelegte Missing-Regel verwenden

### `current_region`
Aktuelle Region bzw. aktueller Wohn- oder Studienort, wenn erhoben.

Beispiele:
- `NRW`
- `Berlin`
- `Madrid`

Wenn nicht erhoben:
- leer lassen

### `childhood_region`
Region des Aufwachsens, wenn erhoben.

Wenn nicht bekannt oder nicht erhoben:
- leer lassen oder `unknown` nach Projektregel

### `needs_review`
`yes`, wenn etwas an der Personenkodierung unklar ist.

Beispiele:
- L1 mehrdeutig
- Elternsprachen unklar
- zusätzliche Sprachen schwer interpretierbar
- biographische Angaben widersprüchlich

Sonst:
- `no`

### `person_notes`
Freitext für zusätzliche pseudonymisierte Hinweise.

Beispiele:
- mehrsprachig aufgewachsen
- L1-Angabe im Fragebogen mehrdeutig
- Sprachbiographie komplex, später prüfen

## Beispielzeile

| person_id | l1 | mother_l1 | father_l1 | additional_languages | gender | birth_year | current_region | childhood_region | needs_review | person_notes |
|---|---|---|---|---|---|---|---|---|---|---|
| P-0001 | DE | IT | DE | EN; FR | female | 2001 | NRW | Bayern | no |  |

---

# 3. Blatt: `Research_Session_Intake`

Dieses Blatt enthält Daten zu einer **konkreten Aufnahme-Session**.

Eine Person kann mehrere Sessions haben.

## Zweck

Dieses Blatt beschreibt die einzelne Aufnahmesituation bzw. den einzelnen Datensatz, der später eine `session_id` erhält.

## Ganz wichtig

Die `session_id` wird **nicht manuell vergeben**, sondern später automatisch erzeugt.

Deshalb:

- Feld `session_id` bei der Erfassung **leer lassen**, wenn es noch nicht automatisch erzeugt wurde

## Spalten in exakt dieser Reihenfolge

```text
session_id
person_id
target_language
speaker_type
l1
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

## Erläuterung der Felder

### `session_id`
Bei der Erfassung zunächst leer lassen.

Nicht manuell ausdenken.

### `person_id`
Verknüpft die Session mit der Person.

Beispiel:
- `P-0001`

### `target_language`
Zielsprache der Aufnahme.

Beispiele:
- `es`
- `fr`
- `en`
- `de`

### `speaker_type`
Nur Werte aus der Vokabelliste verwenden.

Beispiele:
- `learner`
- `native_speaker`
- `heritage_speaker`

Wenn unklar:
- nicht frei raten
- `needs_review = yes` setzen

### `l1`
Erstsprache auf Session-Ebene, wenn sie für die Session-ID, die Analyse oder die spätere Einordnung relevant ist.

Beispiele:
- `DE`
- `RU`

Wenn für den Workflow nicht nötig oder in diesem Fall nicht relevant:
- leer lassen

### `standard_variety`
Nur für Native Speakers oder andere Fälle, in denen eine Standardvarietät relevant ist.

Beispiele:
- `es_std`
- `mx_std`
- `gb_std`
- `us_std`

Für Lernende meist:
- leer lassen

### `level_self`
Selbsteinschätzung der Person.

Beispiele:
- `A2`
- `B1`
- `B2`
- `B1-B2`

Wenn keine Selbsteinschätzung vorliegt:
- leer lassen oder `unknown` nach Projektregel

### `level_code`
Normalisierte Einzelstufe, die später für Verarbeitung oder ID-Logik verwendet werden kann.

Beispiele:
- `A2`
- `B1`
- `B2`

Wichtig:
Wenn `level_self = B1-B2`, dann wird in `level_code` der niedrigere Wert eingetragen:

- `level_self = B1-B2`
- `level_code = B1`

Bei Native Speakers meist:
- leer lassen

### `recording_year`
Jahr der Aufnahme.

Beispiel:
- `2026`

### `recording_date`
Genaues Datum, wenn bekannt.

Wenn nicht bekannt:
- leer lassen oder nach eurer Missing-Regel verfahren

### `recorded_by`
Explorator:in bzw. aufnehmende Person.

Empfohlene Schreibweise:
- stabiles Kürzel oder fest definierter Name

Beispiele:
- `AB`
- `CD`
- `SHK1`

Wichtig:
- innerhalb des Projekts konsistent schreiben
- keine wechselnden Schreibvarianten für dieselbe Person verwenden

### `context`
Nur Werte aus der Vokabelliste.

Beispiele:
- `baseline`
- `follow_up`

Wenn kein solcher Kontext vorliegt oder nicht entschieden wurde:
- leer lassen oder `unknown`, je nach Projektregel

### `needs_review`
`yes`, wenn Sessiondaten unklar oder widersprüchlich sind.

Beispiele:
- Level schwer ableitbar
- L1 unklar
- Standardvarietät fraglich
- Aufnahmejahr unsicher
- Explorator:in nicht eindeutig dokumentiert

Sonst:
- `no`

### `session_notes`
Freitext für Hinweise zur Aufnahme.

Beispiele:
- Nebengeräusche
- zweite Aufnahme am selben Tag
- Textteil unvollständig
- Interview abgebrochen

## Beispiele

### Beispiel 1: lernende Person

| session_id | person_id | target_language | speaker_type | l1 | standard_variety | level_self | level_code | recording_year | recording_date | recorded_by | context | needs_review | session_notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | P-0001 | es | learner | DE |  | B1-B2 | B1 | 2026 | 2026-03-14 | AB | baseline | no |  |

### Beispiel 2: Native Speaker

| session_id | person_id | target_language | speaker_type | l1 | standard_variety | level_self | level_code | recording_year | recording_date | recorded_by | context | needs_review | session_notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | P-0002 | en | native_speaker |  | gb_std |  |  | 2026 | 2026-03-15 | CD |  | no |  |

Wichtig:
Bei Native Speakers bleiben `level_self` und `level_code` in der Regel leer.

---

# 4. Blatt: `Exposure`

Dieses Blatt enthält strukturierte Angaben zu Sprachbiographie und Aufenthalten.

## Zweck

Hier werden nur tatsächliche Exposure-Fälle eingetragen.

## Ganz wichtig

Wenn **kein Exposure vorhanden** ist:

- **keine Zeile anlegen**

Nicht:
- keine Fake-Zeile mit `unknown`
- keine Platzhalter-Zeile
- keine Null-Zeile

## Spalten in exakt dieser Reihenfolge

```text
person_id
target_language
country
duration_months
type
exposure_notes
needs_review
```

## Erläuterung der Felder

### `person_id`
Verweist auf die Person.

### `target_language`
Auf welche Zielsprache sich der Exposure bezieht.

Beispiele:
- `es`
- `fr`

### `country`
Land des Aufenthalts oder Bezugs.

Beispiele:
- `Spain`
- `France`
- `Mexico`

Wenn unbekannt, aber es gab Exposure:
- `unknown`

### `duration_months`
Dauer in Monaten.

Beispiele:
- `6`
- `12`

Wenn nicht bekannt:
- leer lassen oder nach Projektregel verfahren

### `type`
Nur Werte aus der Vokabelliste.

Beispiele:
- `study`
- `erasmus`
- `work`
- `travel`
- `family`
- `other`

Wenn unklar, aber Exposure vorhanden:
- `unknown`

### `exposure_notes`
Zusätzliche Informationen für komplexe Fälle.

Beispiele:
- mehrere kürzere Aufenthalte
- regelmäßige Familienbesuche
- teilweise unklare Zeitangaben

### `needs_review`
`yes`, wenn der Exposure-Fall unklar oder schwierig zu kodieren ist.

Sonst:
- `no`

## Beispiele

### Beispiel 1: echter Exposure-Fall

| person_id | target_language | country | duration_months | type | exposure_notes | needs_review |
|---|---|---|---|---|---|---|
| P-0001 | es | Spain | 6 | erasmus |  | no |

### Beispiel 2: Exposure vorhanden, Detail unklar

| person_id | target_language | country | duration_months | type | exposure_notes | needs_review |
|---|---|---|---|---|---|---|
| P-0003 | fr | unknown | 3 | family | Aufenthalte laut Fragebogen regelmäßig, Land unklar | yes |

### Beispiel 3: kein Exposure

Dann wird **gar keine Zeile** angelegt.

---

# 5. Blatt: `Vocabularies`

Dieses Blatt enthält die vorgegebenen Werte, die in bestimmten Feldern verwendet werden sollen.

## Zweck

Hier stehen die kontrollierten Vokabulare für Felder wie:

- `gender`
- `speaker_type`
- `target_language`
- `level_code`
- `level_self`
- `context`
- `type`
- `l1`
- `mother_l1`
- `father_l1`
- gegebenenfalls auch `recorded_by`, wenn dafür ein kontrolliertes Set geführt wird

## Spalten in exakt dieser Reihenfolge

```text
field_name
value
label
sort_order
notes
```

## Erläuterung der Felder

### `field_name`
Name des Feldes, für das der Vokabulareintrag gilt.

Beispiele:
- `gender`
- `speaker_type`
- `l1`
- `context`

### `value`
Technischer Wert, der in den anderen Blättern tatsächlich verwendet wird.

Beispiele:
- `female`
- `learner`
- `es`
- `B1`
- `erasmus`
- `DE`

### `label`
Lesbare Bezeichnung, falls eine menschenfreundliche Anzeigeform gewünscht ist.

Beispiele:
- `Female`
- `Learner`
- `Spanish`
- `German`

Wenn kein separates Label gebraucht wird:
- denselben Wert wie in `value` eintragen

### `sort_order`
Numerische Reihenfolge für stabile Dropdowns und konsistente Anzeige.

Beispiele:
- `1`
- `2`
- `3`

### `notes`
Kurze Zusatzhinweise, wenn ein Wert erläuterungsbedürftig ist.

## Regel

Wenn ein Feld an eine Liste gebunden ist:

- nur Werte aus dieser Liste verwenden
- nichts frei abwandeln
- keine Tippvarianten einführen

Also zum Beispiel nicht:

- `femalee`
- `b2`
- `B-2`
- `Erasmus`
- `study abroad`

sondern genau die vorgesehenen Werte.

---

# 6. Dateibenennung der Audio- und Arbeitsdateien

Die Hilfskräfte legen die Dateien **nicht final ins Zielsystem** ab.
Sie verwenden nur eine einfache Übergangsbenennung.

## Übergangsregeln

Schema:

```text
nachname_vorname_task_raw.wav
nachname_vorname_task_source.wav
nachname_vorname_task.TextGrid
```

Erlaubte `task`-Werte:

- `wordlist`
- `text`
- `interview`

## Beispiele

```text
mueller_anna_wordlist_raw.wav
mueller_anna_wordlist_source.wav
mueller_anna_wordlist.TextGrid

mueller_anna_text_raw.wav
mueller_anna_text_source.wav
mueller_anna_text.TextGrid

mueller_anna_interview_raw.wav
mueller_anna_interview_source.wav
```

Falls später auch ein Interview-TextGrid vorliegt:

```text
mueller_anna_interview.TextGrid
```

## Technische Regeln für Dateinamen

- nur Kleinbuchstaben
- keine Leerzeichen
- nur Unterstriche
- Umlaute umschreiben:
  - `ä -> ae`
  - `ö -> oe`
  - `ü -> ue`
  - `ß -> ss`
- keine freien Zusätze wie:
  - `neu`
  - `final`
  - `1`
  - `neu2`

Wenn wirklich eine zweite Version nötig ist, dann nur kontrolliert:

```text
mueller_anna_wordlist_source_v2.wav
```

---

# 7. Typische Fehler, die vermieden werden müssen

## Keine Klarnamen in Research-Blättern

Klarname nur in `Secure_Person_Intake`.

## Keine manuell erfundene `session_id`

Dieses Feld bleibt zunächst leer.

## Kein `unknown`, wenn etwas einfach nicht zutrifft

Beispiel:

- kein Exposure → keine Zeile, nicht `unknown`

## Keine freien Varianten bei kontrollierten Werten

Nur Werte aus `Vocabularies`.

## Keine inhaltlichen Informationen in Dateinamen improvisieren

Nur das festgelegte Übergangsschema benutzen.

## Keine Informationen doppelt und widersprüchlich eintragen

Wenn etwas unklar ist:

- `needs_review = yes`
- kurze Notiz ins passende Notizfeld

## Elternsprachen und weitere Sprachen nicht in Notizen verstecken

Wenn `mother_l1`, `father_l1` oder `additional_languages` erhoben wurden:
- in die dafür vorgesehenen Felder eintragen
- Notizen nur für Erläuterungen verwenden

## Explorator:in nicht vergessen

Jede Session soll nach Möglichkeit einen Eintrag in `recorded_by` haben.

---

# 8. Praktischer Ablauf für die Erfassung

## Schritt 1

Im `Secure_Person_Intake` einen neuen Fall anlegen und `person_id` eintragen.

## Schritt 2

Klarname und Dateinamen von Consent und Fragebogen ergänzen.

## Schritt 3

Im Blatt `Research_Person` die pseudonymisierten Personendaten mit derselben `person_id` eintragen.

Wichtig:
- Haupt-L1 erfassen
- Elternsprachen erfassen
- weitere gelernte Sprachen erfassen, wenn vorhanden

## Schritt 4

Im Blatt `Research_Session_Intake` eine Zeile für jede Session anlegen.

Wichtig:
- `session_id` leer lassen
- Sessiondaten sauber ausfüllen
- `recorded_by` nicht vergessen

## Schritt 5

Nur wenn es tatsächlichen Exposure gibt:
- im Blatt `Exposure` eine oder mehrere Zeilen anlegen

## Schritt 6

Wenn etwas unklar ist:
- `needs_review = yes`
- kurze, sachliche Notiz ergänzen

## Schritt 7

Nach Prüfung:
- `verified_by`
- `verified_date`

nur im Secure-Blatt ergänzen

---

# 9. Kurzfassung der wichtigsten Regeln

- `person_id` verbindet alle Blätter
- Klardaten nur im Secure-Blatt
- `session_id` nicht manuell eintragen
- `recorded_by` gehört in jede Session, wenn bekannt
- `mother_l1`, `father_l1` und `additional_languages` gehören ins Blatt `Research_Person`
- `unknown` nur bei wirklich unbekannten Werten
- wenn kein Exposure vorliegt: keine Exposure-Zeile
- Notizen nur kurz und sachlich
- kontrollierte Werte immer exakt aus `Vocabularies`
- Dateinamen nur nach festgelegtem Übergangsschema
