# Session Metadata XLSX Mapping

Dieses Dokument definiert den aktiven XLSX-Importvertrag fuer das PROMAT-Intake-Workbook. Es folgt dem Endstand aus `docs/data-intake/README_promat_intake_template_revised.md` und fuehrt keine parallele zweite Mapping-Logik ein.

## Status

- Die aktive Research-Webapp liest Sessions derzeit direkt aus `data/sessions/{language}/{session_id}/metadata.json`.
- Eine echte XLSX-Importpipeline ist weiterhin nicht verdrahtet; die Mapping-Dateien definieren nur den verbindlichen Vertrag fuer die spaetere Implementierung.
- Das Intake-Workbook ist person-, session-intake- und exposurebezogen aufgebaut; `speaker_type` ist personbezogen, Exposure ist ueber `session_ref` an die Intake-Session gebunden.

## Workbook-Struktur

- `Secure_Person_Intake`: Klardaten, ausserhalb des Research-Runtimes.
- `Research_Person`: genau eine Zeile pro `person_id`.
- `Research_Session_Intake`: eine Zeile pro geplanter oder erfasster Session.
- `Exposure`: null bis viele Zeilen pro Kombination aus `person_id` und `session_ref`.
- `Vocabularies`: breites Kontrollblatt mit stabilen Werte-Spalten.

## Grundregeln

- XLSX-Spalten verwenden englische Snake-Case-Namen.
- `person_id` folgt `{CORPUS_CODE}-{SPEAKER_MARKER}-{NNNN}`.
- `session_ref` ist die lokale Session-Referenz im Intake, z. B. `S01`.
- `session_id` bleibt im Intake leer und wird spaeter aus `person_id`, `recording_year` und `session_ref` abgeleitet.
- `speaker_type` steht nur in `Research_Person`, nicht in `Research_Session_Intake`.
- Exposure bleibt sessionbezogen und wird ueber `person_id` plus `session_ref` verknuepft.
- Die kanonische Form fuer unbekannte, aber relevante Werte ist `unknown` in Kleinbuchstaben.
- Fuer `speaker_type` werden aktuell nur die aktiv genutzten Werte gepflegt: `learner`, `native_speaker`.
- `target_language` fuehrt nur die lowercase-Werte `es`, `fr`, `en`, `de`.
- `standard_variety` fuehrt nur lowercase snake_case und disambiguiert Schweizer Varietaeten als `fr_ch_std` und `de_ch_std`.
- `l1_code` bleibt uppercase und gilt gleichermassen fuer `l1`, `mother_l1` und `father_l1`.
- Technische Task-Werte sind `wordlist`, `text`, `interview`; alte Parallelwerte wie `isolated_speech` oder `connected_speech` sind im Intake unzulaessig.

## Worksheet `Research_Person`

| XLSX column | Scope | future metadata key | Type | Nullable | Applies to | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| person_id | person | person_id | string | no | all | Stable person identifier |
| speaker_type | person | speaker_type | string | no | all | Controlled vocabulary: `learner`, `native_speaker` |
| l1 | person | l1 | string | yes | all | Uses the same value list as `l1_code` |
| mother_l1 | person | mother_l1 | string | yes | all | Uses the same value list as `l1_code` |
| father_l1 | person | father_l1 | string | yes | all | Uses the same value list as `l1_code` |
| additional_languages | person | additional_languages | string | yes | all | Free collection field, e.g. `EN; FR` |
| gender | person | gender | string | yes | all | Controlled vocabulary: `female`, `male`, `diverse`, `unknown` |
| birth_year | person | birth_year | integer | yes | all | Four-digit year |
| current_region | person | current_region | string | yes | learner | Learner-oriented regional field |
| childhood_region | person | childhood_region | string | yes | learner | Learner-oriented regional field |
| origin_country | person | origin_country | string | yes | native_speaker | Native comparison field |
| origin_region | person | origin_region | string | yes | native_speaker | Native comparison field |
| needs_review | person | needs_review | string | yes | all | Controlled vocabulary: `yes`, `no`, `unknown` |
| person_notes | person | person_notes | string | yes | all | Optional intake note |

## Worksheet `Research_Session_Intake`

| XLSX column | Scope | future metadata key | Type | Nullable | Applies to | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| person_id | session | person_id | string | no | all | Foreign key to `Research_Person` |
| session_ref | session | session_ref | string | no | all | Local intake session ref such as `S01` |
| session_id | session | session_id | string | yes | all | Must stay empty in intake |
| target_language | session | target_language | string | no | all | Controlled vocabulary: `es`, `fr`, `en`, `de` |
| standard_variety | session | standard_variety | string | yes | native_speaker | Lowercase snake_case, e.g. `es_std`, `mx_std`, `fr_ch_std`, `de_ch_std` |
| level_self | session | level_self | string | yes | learner | Free or controlled self-assessment value |
| level_code | session | level_code | string | yes | learner | Controlled vocabulary: `A1`, `A2`, `B1`, `B2`, `C1`, `C2` |
| recording_year | session | recording_year | integer | no | all | Used later to derive `session_id` |
| recording_date | session | recording_date | date | yes | all | ISO date |
| recorded_by | session | recorded_by | string | yes | all | Technical field name stays English |
| context | session | context | string | yes | all | Controlled vocabulary: `baseline`, `follow_up` |
| needs_review | session | needs_review | string | yes | all | Controlled vocabulary: `yes`, `no`, `unknown` |
| session_notes | session | session_notes | string | yes | all | Optional intake note |

## Worksheet `Exposure`

| XLSX column | Scope | future metadata key | Type | Nullable | Applies to | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| person_id | exposure | person_id | string | no | learner | Must match `Research_Person.person_id` |
| session_ref | exposure | session_ref | string | no | learner | Must match `Research_Session_Intake.session_ref` |
| target_language | exposure | target_language | string | no | learner | Controlled vocabulary: `es`, `fr`, `en`, `de` |
| country | exposure | country | string | yes | learner | `unknown` allowed if relevant but not known |
| duration_months | exposure | duration_months | integer | yes | learner | Integer or empty |
| exposure_type | exposure | type | string | yes | learner | Controlled vocabulary from `Vocabularies.exposure_type` |
| exposure_notes | exposure | exposure_notes | string | yes | learner | Optional note |
| needs_review | exposure | needs_review | string | yes | learner | Controlled vocabulary: `yes`, `no`, `unknown` |

## Worksheet `Vocabularies`

Breites Kontrollblatt mit genau diesen Spalten:

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

Regeln:

- `speaker_type` fuehrt aktuell nur `learner` und `native_speaker`.
- `l1_code` bleibt uppercase, z. B. `DE`, `ES`, `EN`, `FR`, `IT`, `PT`, `RU`.
- `target_language` fuehrt nur `es`, `fr`, `en`, `de`.
- `standard_variety` fuehrt nur lowercase snake_case; `ch_std` ist kein aktiver Wert, stattdessen `fr_ch_std` bzw. `de_ch_std`.
- `task_type` fuehrt `wordlist`, `text`, `interview`.
- `yes_no_unknown` verwendet `yes`, `no`, `unknown`.
- `Vocabularies` bleibt das breite Kontrollblatt; eine normalisierte Alternative wie `field_name`/`value`/`label`/`sort_order`/`notes` ist kein aktiver Soll-Stand.
- `recorded_by` wird nur dann als kontrollierte Liste gefuehrt, wenn das Projekt wirklich mit festen Werten arbeitet.

## Projektion in `metadata.json`

- `Research_Person` liefert die personenbezogenen Felder fuer jede spaetere Session-Metadatei.
- `Research_Session_Intake` liefert die sessionbezogenen Felder.
- `Exposure` wird nach `person_id` plus `session_ref` gruppiert und als `exposure_entries` serialisiert.
- Aus vorhandenen Exposure-Zeilen wird fuer Lernenden-Sessions zusaetzlich das Summenfeld `stays_in_target_country` abgeleitet.
- `tasks` in `metadata.json` werden nicht direkt als eigenes Intake-Blatt erfasst; ihre erlaubten technischen Werte werden aber ueber `Vocabularies.task_type` verbindlich festgelegt.

## Validierungsregeln

- Jede `Exposure`-Zeile muss zu einer vorhandenen Kombination aus `person_id` und `session_ref` passen.
- Native-Speaker-Vergleichsprofile sollen im Intake in der Regel genau eine Session mit `session_ref = S01` haben.
- `standard_variety` bleibt bei Lernenden leer.
- `level_self` und `level_code` bleiben bei Native Speakers leer.
- Wenn ein Feld nicht relevant ist, bleibt es leer und wird nicht mit `unknown` befuellt.
