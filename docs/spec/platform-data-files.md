# PROMAT Spec: Platform, Data, and Files

## Status

This file is the binding source of truth for PROMAT platform structure, routing, runtime boundaries, IDs, filesystem semantics, and active controlled vocabularies.

## Platform Structure

- `app/` is the only versioned application source root.
- `data/` is the protected research-data space.
- `public/` is the explicitly released public-media space.
- `secure/` is the clear-text space and is never accessed by the webapp.
- `scripts/` contains repeatable import, export, setup, and pipeline steps.

## Routing

### Public route schema

```text
/{ui_lang}/{section}/{corpus_language}/{page}
```

### Active technical route values

- `ui_lang`: `de`, `en`
- `section`: `project`, `research`, `teaching`, `sample`
- `corpus_language`: `spanish`, `french`, `german`, `english`

### Active research pages

- `design`
- `speakers`
- `recordings`
- `comparison`
- `phenomena`

### Active teaching pages

- `phenomena`
- `materials`

### Routing rules

- Technical slugs and route segments stay English.
- UI language and technical routing language must not be mixed.
- Old German technical slugs and old public routes must not be reintroduced.

## Runtime Boundaries

- `AUTH_DATABASE_URL` is the canonical auth/core database variable.
- `PROMAT_RUNTIME_ROOT` is the canonical runtime root.
- `PROMAT_PUBLIC_ROOT` is the canonical public root.
- Paths are derived through runtime/config wiring, not freehand string paths.

## Dev/Prod Parity

- Dev and Prod use the same architecture, terminology, routing, and data semantics.
- Allowed differences are infrastructure-level only.
- Research-data architecture must not diverge into Dev-only fallback stores or shadow structures.
- PostgreSQL is the binding database strategy for research-data work.

## Data Spaces

### `data/`

- Protected research data only.
- Public assets are never served directly from `data/`.

### `public/`

- Only explicitly released assets.
- Export to `public/` is always an explicit pipeline step.

### `secure/`

- Clear-text and re-identification data.
- Never used as a webapp runtime source.

## IDs

### `person_id`

```text
{CORPUS_CODE}-{SPEAKER_MARKER}-{NNNN}
```

Examples:

```text
ES-L-0001
ES-N-0001
FR-N-0004
```

### `session_id`

```text
{person_id}-{YYYY}-S{NN}
```

Examples:

```text
ES-L-0001-2026-S01
ES-L-0001-2027-S02
ES-N-0001-2026-S01
```

### ID rules

- Active speaker markers are only `L` and `N`.
- Active speaker types are only `learner` and `native_speaker`.
- `H` and `heritage_speaker` are not active standards.
- `session_id` contains only `person_id`, four-digit recording year, and two-digit session number.
- Level, L1, standard variety, and origin data stay in metadata, not in IDs.
- Native-speaker comparison profiles map one `person_id` to exactly one session.

## Session Filesystem

### Session root

```text
data/sessions/{language}/{session_id}/
```

### Required session structure

```text
raw/
source/
alignment/
derived/
items/
metadata.json
```

### Semantics

- `raw/` contains untouched original WAV masters only.
- `source/` contains processed working WAVs.
- `alignment/` contains whole-session TextGrid files and reduced alignment JSON such as `alignment/wordlist.json`.
- `derived/` contains webapp-facing derivatives such as MP3.
- `items/{task}/` contains split MP3 files only.

### File rules

- Canonical task filenames use `wordlist`, `text`, `interview`.
- Reduced alignment JSON belongs under `alignment/{task}.json`, never under `items/`.
- Internal split filenames use stable `item_id`s.
- Longer filenames with `session_id` and labels are for later download logic, not canonical storage.
- Current Spanish dev example WAVs are processed `source` audio, not `raw` masters.

## Active Metadata Semantics

### Person-level fields

- `person_id`
- `l1`
- `mother_l1`
- `father_l1`
- `additional_languages`
- `gender`
- `birth_year`
- `current_region`
- `childhood_region`
- `origin_country`
- `origin_region`

### Session-level fields

- `session_id`
- `person_id`
- `target_language`
- `speaker_type`
- `level_code`
- `level_self`
- `recording_year`
- `recording_date`
- `context`
- `recorded_by`
- `stays_in_target_country`
- `exposure_entries`
- `standard_variety`
- `notes`
- `tasks`
- `files`

### Exposure semantics

- `stays_in_target_country` is the compact session-level summary field.
- `exposure_entries` stores structured stay details per session.
- Each entry may contain `country`, `duration_months`, `type`, and optional `exposure_notes`.

## Controlled Vocabularies

### `gender`

```text
female
male
diverse
unknown
```

### `speaker_type`

```text
learner
native_speaker
```

### `target_language`

```text
es
fr
en
de
```

Rule:

- `target_language` stays lowercase.
- This is intentionally different from uppercase corpus-code segments in IDs.

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

Rule:

- `l1`, `mother_l1`, and `father_l1` use the same uppercase value list as `l1_code`.

### `level_code`

```text
A1
A2
B1
B2
C1
C2
```

### `level_self`

Examples:

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

Rule:

- If a range is given in `level_self`, `level_code` stores the lower level.

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

Rule:

- `isolated_speech` and `connected_speech` are not active task keys.

### `standard_variety`

```text
es_std
mx_std
ar_std
co_std
cl_std
gb_std
us_std
au_std
nz_std
fr_std
ca_std
fr_ch_std
be_std
de_std
at_std
de_ch_std
de_south_std
```

Rules:

- `standard_variety` always stays lowercase snake_case.
- Swiss varieties are actively disambiguated as `fr_ch_std` and `de_ch_std`.
- `ch_std` is not an active standard.

### `yes_no_unknown`

```text
yes
no
unknown
```

Rules:

- `unknown` is the canonical lowercase active form.
- `UNKNOWN` is not an active standard value.

### `recorded_by`

- Technical field name stays `recorded_by`.
- A controlled list is optional and only used if the project actually maintains one.
