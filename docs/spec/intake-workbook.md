# PROMAT Spec: Intake Workbook

## Status

This file is the binding source of truth for the PROMAT intake workbook contract.

## Workbook Purpose

- The workbook is the intake contract for structured acquisition of PROMAT data.
- It is not the runtime data source.
- Runtime session metadata is derived later from the workbook contract.

## Binding Workbook Logic

### Active imported sheets

The active import-relevant sheets are exactly:

1. `Secure_Person_Intake`
2. `Research_Person`
3. `Research_Session_Intake`
4. `Exposure`
5. `Vocabularies`

### Optional `README` sheet

- A workbook may include a human-facing `README` sheet.
- A `README` sheet is explanatory only and is never part of the import contract.
- If helper text in a workbook conflicts with this spec, this spec wins.

## Core Workbook Rules

### ID logic

- `person_id` follows `{CORPUS_CODE}-{SPEAKER_MARKER}-{NNNN}`.
- `session_ref` is the local intake session reference such as `S01`.
- `session_id` stays empty in intake and is generated later.

### Exposure linkage

- `Exposure` is session-related.
- `Exposure` links to intake sessions through `person_id` plus `session_ref`.
- `Exposure` does not link through `session_id`.

### Empty fields and `unknown`

- Leave a field empty when it is not relevant.
- Use `unknown` only when a value would be relevant but is not known.
- Do not create dummy `Exposure` rows if no exposure exists.

### Native and learner scope

- `speaker_type` belongs in `Research_Person`, not in `Research_Session_Intake`.
- `l1` belongs in `Research_Person`, not in `Research_Session_Intake`.
- `standard_variety` stays empty for learners.
- `level_self` and `level_code` stay empty for native speakers.

## Sheet Order and Columns

### `Secure_Person_Intake`

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

Rules:

- Clear names and other identifying data stay in this sheet only.
- `verified_by` and `verified_date` stay empty until review has happened.

### `Research_Person`

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

Rules:

- `speaker_type` is a person-level field.
- `l1`, `mother_l1`, and `father_l1` use the same value list as `l1_code`.
- `current_region` and `childhood_region` are learner-oriented fields.
- `origin_country` and `origin_region` are native-comparison fields.

### `Research_Session_Intake`

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

Rules:

- The sheet begins with `person_id`, `session_ref`, `session_id`.
- `session_ref` is filled in intake.
- `session_id` stays empty in intake.
- `target_language` uses the controlled lowercase values.
- `context` uses `baseline` or `follow_up` when relevant.
- If `level_self = B1-B2`, then `level_code = B1`.

### `Exposure`

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

Rules:

- Each row must match an existing combination of `person_id` and `session_ref`.
- If there is no exposure, there is no row.
- `country` may be `unknown` if exposure exists but country is not known.
- `duration_months` stays empty if the duration is not known reliably.

### `Vocabularies`

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

Rules:

- This broad sheet is the only active vocabulary-sheet model.
- A normalized alternative such as `field_name` / `value` / `label` / `sort_order` / `notes` is not an active PROMAT standard.
- `recorded_by` is controlled only if the project actually maintains a fixed list.

## Active Vocabulary Constraints for the Workbook

### `speaker_type`

```text
learner
native_speaker
```

### `l1_code`

Examples:

```text
DE
ES
EN
FR
IT
PT
RU
```

### `target_language`

```text
es
fr
en
de
```

### `standard_variety`

Examples:

```text
es_std
mx_std
fr_ch_std
de_ch_std
```

### `context`

```text
baseline
follow_up
```

### `task_type`

```text
wordlist
text
interview
```

### `yes_no_unknown`

```text
yes
no
unknown
```

## Learner Example

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

## Native-Speaker Example

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

Rules:

- Native-speaker intake normally uses exactly one session with `session_ref = S01`.
- There is normally no `Exposure` row for the native-speaker comparison profile.
