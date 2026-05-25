# PROMAT Spec: Intake Workbook

## Status

This file is the binding source of truth for the PROMAT intake workbook contract.

## Workbook Purpose

- The workbook is the intake contract for structured acquisition of PROMAT data.
- It is not the runtime data source.
- Runtime session metadata and PostgreSQL research metadata are derived later from the workbook contract by the central production importer.

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
- If `session_id` is accidentally filled in intake, the active importer ignores that cell and still derives the canonical runtime `session_id`.

### Exposure linkage

- `Exposure` is session-related.
- `Exposure` links to intake sessions through `person_id` plus `session_ref`.
- `Exposure` does not link through `session_id`.

### Scope-aware import

- The central production importer scopes one run by requested `target_language` first and validates only the workbook rows for that in-scope language strictly.
- Out-of-scope workbook rows may remain incomplete for later corpus runs and do not block an in-scope import.
- The first productive import scope is `ES`.

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
research_consent_signed
consent_date
consent_file
teaching_consent_signed
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
- `research_consent_signed` records consent for protected research use.
- `teaching_consent_signed` records the separate safety and eligibility flag for manual public Teaching selection.
- `research_consent_signed` and `teaching_consent_signed` use `yes`, `no`, or `unknown`.
- `teaching_consent_signed` is never an automatic Teaching import or release switch by itself.
- For a transition period, the importer may accept the deprecated workbook column `consent_signed` as `research_consent_signed` and must emit a warning.
- `verified_by` and `verified_date` stay empty until review has happened.

### `Research_Person`

```text
person_id
speaker_type
l1
l1_additional
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
- `l1`, `l1_additional`, `mother_l1`, and `father_l1` use the same value list as `l1_code`.
- `l1_additional` is optional, remains separate from `additional_languages`, and stores multiple values as semicolon-separated L1 codes.
- `current_region` and `childhood_region` are learner-oriented fields.
- `origin_country` and `origin_region` are native-comparison fields.
- `origin_region` should stay concise and readable.
- Complex biographical details belong in `person_notes`, not in `origin_region`.
- `person_notes` is an internal research note field and is not part of public Teaching or other public-facing views.

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
- `target_language` uses the active language codes and may appear in workbook practice as uppercase corpus codes such as `ES`; the importer normalizes them to lowercase runtime values.
- `standard_variety` may appear in workbook practice as uppercase values such as `ES_STD`; the importer normalizes them to lowercase runtime values.
- Intake may use `CH_FR_STD` and `CH_DE_STD`; runtime canonical values remain `fr_ch_std` and `de_ch_std`.
- `context` uses `baseline` or `follow_up` when relevant.
- If `level_self = B1-B2`, then `level_code = B1`.
- `session_notes` is an internal note for this exact recording session and is not part of public Teaching or other public-facing views.

### `Exposure`

```text
person_id
session_ref
target_language
country
duration_months
type
exposure_notes
needs_review
```

Rules:

- Each row must match an existing combination of `person_id` and `session_ref`.
- If there is no exposure, there is no row.
- In the active workbook contract, exposure is session-related and links through `person_id` plus `session_ref`, not through `session_id`.
- In active practice there is at most one `Exposure` row per `person_id` plus `session_ref`.
- That single row may summarize multiple countries or stays in `country` and `exposure_notes`.
- The importer must not split one `Exposure` row into multiple exposure records heuristically.
- `country` may be `unknown` if exposure exists but country is not known.
- `duration_months` stays empty if the duration is not known reliably.
- `duration_months` stores numeric month values.
- Decimal values are allowed.
- The importer accepts decimal comma and decimal point and normalizes them transparently, for example `0,75` to `0.75` and `3,5` to `3.5`.
- Non-numeric prose such as `unknown`, `about three weeks`, or `6 months` is not silently reinterpreted; the importer warns and leaves the field empty.
- The workbook header is the literal column name `type`; the importer maps it to session exposure metadata internally.
- `Vocabularies.exposure_type` provides the controlled values for `Exposure.type`.
- `exposure_notes` stores the full internal free-text stay description and is never regenerated from other fields.

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

Examples:

```text
ES
FR
EN
DE
```

Rule:

- The workbook may use uppercase corpus-style codes.
- The importer normalizes them to the canonical lowercase runtime values `es`, `fr`, `en`, and `de`.

### `standard_variety`

Workbook values:

```text
ES_STD
MX_STD
AR_STD
CO_STD
EC_STD
CL_STD
PE_STD
BO_STD
UY_STD
PY_STD
VE_STD
GB_STD
US_STD
AU_STD
NZ_STD
FR_STD
CA_STD
CH_FR_STD
BE_STD
DE_STD
AT_STD
CH_DE_STD
DE_SOUTH_STD
```

Rule:

- Workbook values may use uppercase forms.
- The importer normalizes them to the canonical lowercase runtime values.
- Swiss workbook aliases `CH_FR_STD` and `CH_DE_STD` normalize to the runtime canonical values `fr_ch_std` and `de_ch_std`.

### `exposure_type`

```text
study
erasmus
work
travel
family
volunteering
school_exchange
other
unknown
```

Rules:

- `Vocabularies.exposure_type` is the controlled list for `Exposure.type`.
- The deprecated value `unspecified` is not an active standard and should be migrated to `unknown`.
- The importer may still accept `unspecified` defensively during transition and must normalize it transparently with a warning.

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

Rules:

- This list applies to `research_consent_signed`, `teaching_consent_signed`, and `needs_review`.

## Learner Example

### `Research_Person`

```text
person_id: ES-L-0001
speaker_type: learner
l1: DE
l1_additional: IT; EN
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
l1_additional:
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
