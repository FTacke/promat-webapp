# PROMAT Spec: Platform, Data, and Files

## Status

This file is the binding source of truth for PROMAT platform structure, routing, runtime boundaries, IDs, filesystem semantics, and active controlled vocabularies.

## Platform Structure

- `app/` is the only versioned application source root.
- `data/` is the protected research-data space.
- `public/` is the explicitly released public-media space.
- `secure/` is the clear-text space and is never accessed by the webapp.
- `scripts/` contains repeatable import, export, setup, and pipeline steps.
- `scripts/research_data_intake/` is the canonical root for research-data intake and derivation pipelines.
- General dev and maintenance scripts remain at the top level under `scripts/` and do not move into `scripts/research_data_intake/` unless they become part of the research-data intake pipeline.

## Routing

### Public route schema

```text
/{ui_lang}/{section}/{corpus_language}/{page}
```

### Research detail route schema

```text
/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}
```

### Research player delivery route schema

```text
/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}/audio.mp3
/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}/items/{item_id}.mp3
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

### Active research detail routes

- `player`
- `player`-scoped protected media delivery for current-session playback and single-item download

### Active teaching pages

- `phenomena`
- `materials`

### Routing rules

- Technical slugs and route segments stay English.
- UI language and technical routing language must not be mixed.
- `player` is a research detail route under one concrete corpus language and must not fork into separate task-specific route families.
- The `task` segment of the player route uses only the canonical research task keys `wordlist`, `text`, and `interview`.
- Player media delivery stays under the same `player` route family and resolves protected session artifacts through application logic, not through static publication of `data/`.
- Old German technical slugs and old public routes must not be reintroduced.

## Active App Shell

- All public non-landing inner pages use the same shared app shell.
- The landing page is the only public layout exception.
- The shared inner shell keeps the global topbar as the stable upper level and the local page shell below it.
- The local page shell uses a left sidebar for area navigation and a right main-content column.
- The sidebar begins with a permanent area header: section icon, section title, and a subtle divider.
- Language-context pages keep their language back-link and language title below that permanent area header, not instead of it.
- Breadcrumbs are rendered only when they add real orientation value, not as a pseudo-context line that merely repeats section or language.
- Desktop shows breadcrumbs only from hierarchy depth 3 onward because the sidebar already carries orientation on flatter levels.
- Mobile shows breadcrumbs from hierarchy depth 2 onward because the sidebar is reduced or absent there.
- When a breadcrumb is shown, it always renders the full path including the current page as the final, non-clickable item.

## Sample Surface

- `sample` is a showcase for current, already accepted layout elements of the webapp.
- `sample` never defines the target UI for product pages; it mirrors the current implementation on real pages.
- If an active layout element is changed on a real page and `sample` contains that element, `sample` must be updated in the same run.

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
- Protected research-player playback and single-item download may resolve session artifacts from `data/` only through explicit application routes under the canonical player family; this does not make those artifacts part of `public/`.

### `data/config/`

- Runtime configuration files belong under `data/config/`.
- Research-player corpus configuration belongs under `data/config/research_player/{language}/`.
- The canonical corpus-level research-player config files include `data/config/research_player/{language}/player_config.json`, `data/config/research_player/{language}/phenomena_presets.json`, and `data/config/research_player/{language}/task_catalogs/{task}.json`.
- Corpus-specific task catalogs under `data/config/research_player/{language}/task_catalogs/` are the canonical content source for task structure, ordering, stable IDs, and exact texts.
- Task catalogs may also carry corpus-specific grouped content structure such as top-level `groups` arrays for sentence-list blocks; these are catalog groupings, not session `segments`.
- Session-specific player artifacts such as `alignment/{task}.json` are derived from these task catalogs plus session alignment and audio data; task catalogs are not session outputs.
- Task catalogs may later support raw material views in the webapp, but this does not imply public release and does not bypass separate access or publication decisions.
- For the current Spanish sentence-list path, `data/config/research_player/spanish/task_catalogs/text.json` is the canonical content catalog for grouped block structure, visible `item_number`, stable `item_id`, and exact sentence strings.

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
- `source/` contains processed working WAVs and remains the operative audio basis for analysis-aware derivation steps.
- `alignment/` contains whole-session TextGrid files and reduced alignment JSON such as `alignment/wordlist.json`, derived from canonical task catalogs plus session-specific alignment and audio data.
- `derived/` contains webapp-facing derivatives such as MP3 and does not replace the WAV-based analysis basis in `raw/` or `source/`.
- `items/{task}/` contains split MP3 files only.

### File rules

- Canonical task filenames use `wordlist`, `text`, `interview`.
- Reduced alignment JSON belongs under `alignment/{task}.json`, never under `items/`.
- Player-facing full-task MP3 files use `derived/{task}.mp3`.
- Player-facing split MP3 paths use `items/{task}/{item_id}.mp3`.
- For the current Spanish sentence-list catalog, visible numbering remains `D1` through `D30`, `QY1` through `QY10`, and `QW1` through `QW10`, while stable technical IDs remain `d_01` through `d_30`, `qy_01` through `qy_10`, and `qw_01` through `qw_10`.
- The current player delivery routes map full-task playback to `.../player/{session_id}/{task}/audio.mp3` and single-item download to `.../player/{session_id}/{task}/items/{item_id}.mp3` without exposing internal runtime paths.
- For the current `wordlist` production path, web derivatives use MP3 in mono with `160 kbps` CBR for both `derived/wordlist.mp3` and `items/wordlist/{item_id}.mp3`.
- Internal split filenames use stable `item_id`s.
- Single-item download filenames are generated separately at delivery time and do not redefine internal storage paths.
- The prepared delivery filename contract is `{person_id}_{task}_{item_id}_{download_label}.mp3`.
- `download_label` is a readable delivery-only text component derived from the canonical text or label of the exported unit.
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
