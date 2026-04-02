# Session Metadata XLSX Mapping

Dieses Dokument definiert den aktuellen kanonischen XLSX-Importvertrag für PROMAT-Session-Metadaten.

## Status

- Die aktive Research-Webapp liest Sessions derzeit direkt aus `data/sessions/{language}/{session_id}/metadata.json`.
- Es gibt aktuell noch keine verdrahtete Research-Metadatentabelle in PostgreSQL.
- Der Importvertrag ist bereits in drei fachliche Ebenen gegliedert: Person, Session und `exposure_entries`.

## Workbook-Struktur

- Worksheet `sessions`: genau eine Zeile pro `session_id`; enthält alle Person- und Session-Felder.
- Worksheet `exposure_entries`: null bis viele Zeilen pro `session_id`; enthält detaillierte Sprachaufenthalte für Lernenden-Sessions.

## Grundregeln

- XLSX-Spalten verwenden dieselben englischen Snake-Case-Namen wie die kanonischen `metadata.json`-Keys.
- Leere XLSX-Zellen werden als `null` behandelt.
- `speaker_type`, `context`, `standard_variety` und `type` in `exposure_entries` verwenden kontrollierte technische Vokabulare.
- `recorded_by` bleibt technisch englisch benannt, auch wenn die UI dafür lokalisierte Labels wie `Explorator:in` zeigt.
- `context` bleibt technisch und wird in Profilen nicht als Rohwert `baseline` oder `follow_up` sichtbar wiedergegeben.
- `additional_languages` wird im Worksheet `sessions` als JSON-Array-String serialisiert, zum Beispiel `["English", "French"]`.
- Wenn für eine Session Zeilen in `exposure_entries` vorliegen, soll `stays_in_target_country` in `sessions` auf `TRUE` gesetzt werden.

## Person- und Session-Felder im Worksheet `sessions`

| XLSX column | Scope | metadata.json key | future DB column | Type | Nullable | Applies to | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| person_id | person | person_id | person_id | string | no | all | Stable person identifier, e.g. `P-0001` |
| session_id | session | session_id | session_id | string | no | all | Stable session identifier, e.g. `ES-L-DE-A1-26-001` |
| target_language | session | target_language | target_language | string | no | all | Controlled vocabulary: `es`, `fr`, `en`, `de` |
| speaker_type | session | speaker_type | speaker_type | string | no | all | Controlled vocabulary: `learner`, `native_speaker`, `heritage_speaker` |
| l1 | person | l1 | l1 | string | yes | all | Primary L1 label for the recorded person |
| mother_l1 | person | mother_l1 | mother_l1 | string | yes | all | Person-level family-language field |
| father_l1 | person | father_l1 | father_l1 | string | yes | all | Person-level family-language field |
| additional_languages | person | additional_languages | additional_languages | json-array-string | yes | all | Serialized JSON array in a single cell |
| gender | person | gender | gender | string | yes | all | Controlled vocabulary: `female`, `male`, `diverse`, `unknown` |
| birth_year | person | birth_year | birth_year | integer | yes | all | Four-digit year |
| current_region | person | current_region | current_region | string | yes | learner | Active learner-only regional field |
| childhood_region | person | childhood_region | childhood_region | string | yes | learner | Active learner-only regional field |
| origin_country | person | origin_country | origin_country | string | yes | native_speaker | Active native-only origin field |
| origin_region | person | origin_region | origin_region | string | yes | native_speaker | Active native-only origin field |
| level_code | session | level_code | level_code | string | yes | learner | Controlled vocabulary: `A1`, `A2`, `B1`, `B2`, `C1`, `C2` |
| level_self | session | level_self | level_self | string | yes | learner | May contain ranges such as `A2-B1` |
| standard_variety | session | standard_variety | standard_variety | string | yes | native_speaker | Controlled vocabulary depends on target language |
| recording_year | session | recording_year | recording_year | integer | no | all | Year of recording |
| recording_date | session | recording_date | recording_date | date | yes | all | ISO date, e.g. `2026-03-10` |
| context | session | context | context | string | yes | all | Controlled vocabulary: `baseline`, `follow_up` |
| recorded_by | session | recorded_by | recorded_by | string | yes | all | Person or documented role responsible for recording the session |
| stays_in_target_country | session | stays_in_target_country | stays_in_target_country | boolean | yes | learner | Summary field for profile/filter logic |
| notes | session | notes | notes | string | yes | all | Free text note |

## Detaillierte Sprachaufenthalte im Worksheet `exposure_entries`

| XLSX column | Scope | metadata.json key | future DB column | Type | Nullable | Applies to | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| session_id | exposure | session_id | session_id | string | no | learner | Foreign key to the `sessions` worksheet |
| entry_index | exposure | entry_index | entry_index | integer | no | learner | Stable row order within one session |
| country | exposure | country | country | string | no | learner | Technical country value; UI may localize separately |
| duration_months | exposure | duration_months | duration_months | integer | yes | learner | Integer month count or `null` |
| type | exposure | type | type | string | yes | learner | Controlled vocabulary such as `erasmus`, `study`, `work`, `travel` |
| exposure_notes | exposure | exposure_notes | exposure_notes | string | yes | learner | Optional free-text note |

## Serialisierungsregeln für `metadata.json`

- Das Worksheet `sessions` wird in die flachen Person- und Session-Felder von `metadata.json` geschrieben.
- Die Zeilen des Worksheets `exposure_entries` werden nach `session_id` gruppiert und als Liste unter `metadata.json.exposure_entries` serialisiert.
- `additional_languages` wird beim Import aus dem JSON-Array-String in eine JSON-Liste umgewandelt.
- Wenn keine Zeilen für `exposure_entries` vorliegen, darf `metadata.json.exposure_entries` fehlen oder als leere Liste geschrieben werden.

## Beispiel Lernenden-Session

### Worksheet `sessions`

```text
person_id=P-0001
session_id=ES-L-DE-A1-26-001
target_language=es
speaker_type=learner
l1=DE
mother_l1=DE
father_l1=PL
additional_languages=["English", "French"]
gender=female
birth_year=1998
current_region=Berlin, Germany
childhood_region=Saxony, Germany
origin_country=
origin_region=
level_code=A1
level_self=A1
standard_variety=
recording_year=2026
recording_date=2026-03-10
context=baseline
recorded_by=Ana Romero
stays_in_target_country=TRUE
notes=Fully fictional local dev seed mapped from data/example_data/test_person_ (1).*
```

### Worksheet `exposure_entries`

```text
session_id=ES-L-DE-A1-26-001 | entry_index=1 | country=spain | duration_months=6 | type=erasmus | exposure_notes=Austauschsemester in Madrid.
session_id=ES-L-DE-A1-26-001 | entry_index=2 | country=mexico | duration_months=2 | type=travel | exposure_notes=
```

## Beispiel Native-Speaker-Session

```text
person_id=P-0002
session_id=ES-N-ES_STD-26-001
target_language=es
speaker_type=native_speaker
l1=ES
mother_l1=ES
father_l1=ES
additional_languages=["English"]
gender=male
birth_year=1992
current_region=
childhood_region=
origin_country=Spain
origin_region=Castile and Leon
level_code=
level_self=
standard_variety=es_std
recording_year=2026
recording_date=2026-03-10
context=baseline
recorded_by=Ana Romero
stays_in_target_country=
notes=Fully fictional local dev seed mapped from data/example_data/test_person_ (2).*
```
