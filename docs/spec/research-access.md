# PROMAT Spec: Research Access

## Status

This file is the binding source of truth for the active research-access model in the PROMAT webapp.

## Runtime Source

- The active research runtime reads sessions directly from `data/sessions/{language}/{session_id}/metadata.json`.
- There is no second active research metadata source.
- `speakers` and `recordings` operate on the same datei-based session metadata.

## Page Model

### Research landing and sections

- The research section root is a corpus selection in the German UI (`Korpus wählen`), not a teaching-style language selection.
- `design` documents corpus design.
- `speakers` is the person-based access path.
- `recordings` is the session- and task-based access path.
- `comparison` and `phenomena` remain conceptually part of the research IA.
- `player` is the shared research-detail workbench for concrete playback, preset, and comparison contexts.

### Research detail workbench

- `player` is not a second section root and not a sidebar page of its own.
- `speakers`, `recordings`, and the person profile are direct player entry points in the current IA.
- `comparison` and `phenomena` must later open the same player base with additional context, not separate player implementations.

## Binding Access Logic

### `speakers`

- `speakers` aggregates by `person_id`.
- There is exactly one profile page per `person_id`.
- A person card remains visible if at least one of that person's sessions matches all active filters.
- Cards link into the person profile and into recordings of the selected or matching session.

### `recordings`

- `recordings` remains session- and task-based.
- Each row refers to one concrete session and one task.
- A recordings row may link back to the person profile with an optional session focus.

### Session focus

- The person page may focus one selected session via query parameter.
- Focusing a session must not hide the person's other sessions.
- The selected session is highlighted as `Ausgewählte Session`.

### `player`

- `player` always has one primary `session_id` and one initial task key.
- The canonical player route is `/{ui_lang}/research/{language}/player/{session_id}/{task}`.
- Player entry may carry source context from `speakers`, `recordings`, `profile`, and later `comparison` or `phenomena`, but all of them resolve to the same route family.
- The player keeps one shared session context while switching between all tasks that are documented as available for that session.
- Tasks that are unavailable for the session may remain visible as disabled, non-interactive controls, consistent with the broader research UI.
- Comparison is an optional extension of the same player and never a separate route family.

## Card Logic

### Speaker cards

- One card per `person_id`.
- Cards show reduced person-facing metadata.
- `person_id` is the dominant primary line on the card.
- The selected session is shown as a secondary line under `person_id`.
- The footer label is `Aufzeichnungen`.
- Cards expose compact direct task links for the currently selected or matched session.
- The profile CTA remains visually secondary to the card identity and recording links.
- The UI does not show a separate `Treffer über ...` match note on the card.

### Matching behavior

- Matching is existential over sessions.
- A person matches filters when at least one session matches them.
- Session-based filters do not create duplicate person cards.

## Profile Logic

### Shared profile semantics

- The page is labeled `Profil` in the German UI and `Profile` in the English UI.
- The profile header remains person-based and shows the number of associated sessions, not the currently selected session.
- A stable person section appears first.
- All sessions of that person appear below as separate session containers.
- Each session container shows its own metadata and its own recording links.
- `context` stays technical and is not displayed raw as `baseline` or `follow_up`.
- `recorded_by` is shown to users as `Explorator:in`.

### Learner profile semantics

Learner profiles may show:

- `Level (Selbsteinschätzung)`
- `L1`
- `L1 der Mutter`
- `L1 des Vaters`
- `Zusätzliche Sprachen`
- `Geschlecht`
- `Geburtsjahr`
- `Aktuelle Region`
- `Region Kindheit`
- `Sprachaufenthalte`

Rules:

- `Sprachaufenthalte` prioritizes structured `exposure_entries`.
- If no detailed entries exist, `stays_in_target_country` remains the compact fallback.
- Structured exposure entries are rendered as a simple vertical list with one primary summary line per stay and an optional secondary note line.

### Native-speaker profile semantics

Native-speaker profiles are comparison profiles, not learner-style biographies.

They show:

- `Person-ID`
- `Ausgewählte Session`
- `Sprechergruppe`
- `Geschlecht`
- `Geburtsjahr`
- `Aufnahmedatum`
- `Aufnahmejahr`
- `Explorator:in`
- `Herkunftsland`
- `Herkunftsregion`
- `Standardvarietät`

They do not show:

- `L1`
- `L1 der Mutter`
- `L1 des Vaters`
- `Zusätzliche Sprachen`
- `Sprachaufenthalte`
- `Level (Selbsteinschätzung)`

Additional rule:

- Each native-speaker comparison profile maps to exactly one session.

## Task Semantics in Research UI

### Active task keys

- `wordlist`
- `text`
- `interview`

Rule:

- These task keys are also the only legal task values in the canonical research-player route.

### Visible short labels

- `Wortliste`
- `Text`
- `Interview`

Rules:

- These are the default visible German short labels of the research UI.
- The technical task key remains `text` in all corpora even when a corpus-specific visible label such as `Satzliste` is configured for the player or other task-entry UI.
- A corpus-specific visible label changes only display text and does not create a new task key or a second task family.

### Frozen task descriptions

- `wordlist`: Isolierte Aussprache über das Vorlesen einer Wortliste.
- `text`: Zusammenhängende Aussprache über das Vorlesen eines Textes oder einer Satzliste.
- `interview`: Halbgeleitete Gesprächssituation mit spontaner Aussprache.

### Availability rules

- Task availability is derived from documented session tasks.
- Native-speaker sessions do not offer `interview`.
- Tasks that are unavailable in the current UI context may still remain visible as disabled, non-interactive panels or links.
- The same availability semantics apply inside the unified player task switch.

## Recordings Table Semantics

- The leading recordings-table column is `Aufzeichnung (Sprecher:in)` in the German UI.
- That leading column shows `session_id` as the primary line and linked `person_id` as the quieter secondary line.
- The recordings table does not use a separate standalone `person_id` column.
- The UI does not repeat the recording year as a second line below `session_id`.
- The learner-facing metadata columns are labeled `Niveau` and `L1`.
- Native-speaker rows leave `Niveau` and `L1` empty instead of reusing variety or origin values in those columns.

## Active UI-Metadata Contract

### Person fields used by the UI

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

### Session fields used by the UI

- `session_id`
- `target_language`
- `speaker_type`
- `level_code`
- `level_self`
- `recording_year`
- `recording_date`
- `context`
- `recorded_by`
- `stays_in_target_country`
- `standard_variety`
- `notes`
- `tasks`
- `files`

### Exposure fields

- `exposure_entries.country`
- `exposure_entries.duration_months`
- `exposure_entries.type`
- `exposure_entries.exposure_notes`

## Non-goals of the Current Runtime

- no real XLSX import pipeline in the web runtime
- no second research data source
- no separate task-specific player families
- no separate comparison player
- no native-speaker interview path
