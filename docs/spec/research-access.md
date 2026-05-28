# PROMAT Spec: Research Access

## Status

This file is the binding source of truth for the active research-access model in the PROMAT webapp.

Research page and task capability metadata are defined in `docs/spec/research-capabilities.md`.

## Runtime Source

- The active research runtime reads sessions directly from `data/sessions/{language}/{session_id}/metadata.json`.
- There is no second active research metadata source.
- `speakers`, the speaker profile, and `player` operate on the same datei-based session metadata.

## Page Model

### Research landing and sections

- The research section root is a corpus selection in the German UI (`Korpus wählen`), not a teaching-style language selection.
- The research section root uses metadata-first corpus cards and does not render an extra intro or subtitle line below the page heading.
- Those corpus cards always show project lead, material design, and execution in that order; they show learner-recordings counts or the status `Korpus im Aufbau`/`Corpus in progress` before any optional reference-recordings line, and that reference-recordings line counts distinct native-speaker/reference-speaker `person_id` values rather than standard-variety values.
- Those corpus cards remain part of the shared card system of the app: speaker cards are the primary visual reference, the visible card structure stays title, primary block, secondary block, and footer CTA, and the secondary status block keeps the same minimum inset above and below the surrounding divider rhythm instead of visually touching the footer divider.
- `design` documents corpus design.
- `speakers` is the person-based access path.
- `comparison` and `phenomena` remain conceptually part of the research IA.
- `player` is the session-centered research-detail workbench for concrete playback and bounded direct compare.

### Research detail workbench

- `player` is not a second section root and not a sidebar page of its own.
- `speakers` and the person profile are direct player entry points in the current IA.
- `comparison` is a first-class item-centered research workbench page and not just a player mode.
- `phenomena` is a split list-curation surface with one calm overview page plus dedicated editor detail routes, and it is not the primary listening surface.
- `comparison` may still launch the canonical player route with additional context, but neither `comparison` nor `phenomena` collapse into separate player implementations or new player route families.

## Binding Access Logic

- The access layer may wrap canonical capability helpers for compatibility, but it must not redefine page-publicness, protected detail routes, or corpus-specific research surface readiness in a second truth source.

### Corpus-scoped public boundary

- For all active corpora `spanish`, `french`, `german`, and `english` and for both active UI languages `de` and `en`, `/{ui_lang}/research/{corpus}/design` is the only public corpus-scoped research page.
- The corpus root `/{ui_lang}/research/{corpus}` is a public reduced orientation page. On desktop with the left sidebar visible, the main column stays limited to title, short subtitle, and two short prose paragraphs; signed-out users additionally see the two actions `Zugang beantragen`/`Request access` and `Zum Login`/`Go to login`, while authenticated users do not.
- On breakpoints where the left sidebar is hidden, the corpus-root main column replaces the longer desktop prose with one short orientation sentence and a compact link-pill block for `design`, `speakers`, `comparison`, and `phenomena`. Those pills reuse the same generic research-navigation order and auth/lock metadata as the sidebar; protected destinations remain visibly muted and locked for signed-out users.
- All other research pages and detail routes under one concrete corpus path are authenticated research-app surfaces.
- Access clarification belongs at the route boundary: unauthenticated requests are redirected to login with a safe return target, and the protected workbench or media response must not already render in the background.
- There are no corpus-specific access exceptions such as public comparison or public phenomena variants outside `design`.
- On public research pages for unauthenticated users, protected research destinations remain visibly linked but render in a muted locked state without repeating login CTA copy at each entry.
- When the public corpus root links to login, that login path preserves the exact corpus-root return target so successful authentication returns the user to the same corpus landing page.
- The public access-request journey for these corpus roots uses the canonical `/access-request` form surface; it does not fall back to a `mailto` draft.

### Protected research surfaces

- Protected research page routes include `speakers`, `comparison`, and `phenomena`.
- Protected research detail routes include the speaker profile, the canonical player route, the phenomena preset editor route, the phenomena owner-set editor route, and the protected player-media delivery routes.
- The same protected boundary also applies to later research work surfaces added under the corpus path unless an active spec explicitly defines a public exception.

### `speakers`

- `speakers` aggregates by `person_id`.
- There is exactly one profile page per `person_id`.
- A person card remains visible if at least one of that person's sessions matches all active filters.
- `speakers` remains person-based even when the visible result surface changes; it must not reintroduce a session-first workbench logic.
- The default `speakers` result view is cards; `?view=table` switches the same filtered person result set into a table view, and invalid `view` values degrade to cards.
- Cards and table rows render from the same already filtered person-based result structure with one selected or matching session per person; `speakers` must not perform a second session-first query or a separate session-counting result pass for the table.
- Locale changes inside `speakers` keep stable technical state such as the current `view`, `session` focus, and active filter keys; localized labels are never the source of truth for restoring the current result state.
- Cards link into the person profile and into recordings of the selected or matching session.
- On `speakers` cards, the quiet profile link sits directly below the person/session identity block; recordings remain grouped below in the separate task-pill section.
- The `speakers` table has one row per `person_id`, not one row per session and not one row per task.
- In the table, the leading column stays person-first: `person_id` is the primary line and the shared profile link sits directly below it; the selected or matching `session_id` remains internal for canonical routing and is not shown as visible table copy.
- The table recordings column exposes only the available player-task actions for that same selected session on the canonical route `/{ui_lang}/research/{language}/player/{session_id}/{task}`.
- Native-speaker table rows do not show a visible `Interview` action when the selected session does not provide that task.
- On small viewports, the `speakers` table must collapse into a stacked row-card presentation rather than forcing a broken wide table.

### `speakers` table semantics

- The German `speakers` table columns are `Sprecher:in`, `Sprechergruppe`, `Niveau`, `L1 / Varietät`, `Geschlecht`, `Aufenthalt`, and `Aufzeichnungen`.
- The English `speakers` table columns are `Speaker`, `Speaker group`, `Level`, `L1 / Variety`, `Gender`, `Stays`, and `Recordings`.
- Learner rows show the selected session level under `Niveau`, the learner `L1` under `L1 / Varietät`, and the localized stays summary under `Sprachaufenthalte`/`Stays`.
- Native-speaker rows leave `Niveau` and `Sprachaufenthalte` empty as `–` and show the canonical localized native reference under `L1 / Varietät`.

### Session focus

- The person page may focus one selected session via query parameter.
- Focusing a session must not hide the person's other sessions.
- The selected session is highlighted as `Ausgewählte Session`.
- In profile session cards, the selected state reuses the concrete session accent for outline and selected badge instead of introducing a second detached selection color.
- Profile-session color semantics stay session-bound, not person-bound, so different sessions of one person may carry different level accents.

### `player`

- `player` always has one primary `session_id` and one initial task key.
- The canonical player route is `/{ui_lang}/research/{language}/player/{session_id}/{task}`.
- Player entry may carry source context from `speakers`, `profile`, `comparison`, and `phenomena`; the legacy source value `recordings` may still be accepted for compatibility but resolves to the same speakers-table return context.
- The player keeps one shared session context while switching between all tasks that are documented as available for that session.
- Tasks that are unavailable for the session may remain visible as disabled, non-interactive controls, consistent with the broader research UI.
- The player may add one optional secondary `compare_session` for bounded direct compare without creating a second player route family.

### `comparison`

- `comparison` uses the existing research page route `/{ui_lang}/research/{language}/comparison`.
- `comparison` is item-centered, not session-first.
- `comparison` may launch the canonical player route for one concrete session and task, but it is not constrained to one primary session.
- `comparison` may work from owner-bound sets derived in `phenomena`, but it does not expose a first-class set-management workflow inside the workbench.
- The `comparison` HTML page is an authenticated workbench and is not publicly renderable outside the login boundary.
- Loading an existing `set_id`, creating the internal default draft, changing the active session selection, and persisting the comparison view filter require authenticated owner context through the canonical `/api/research/sets` route family.
- The canonical `/api/research/sets/{set_id}/save-as` flow remains part of the owner-bound set model, but `comparison` does not expose it as a visible primary workbench action.
- The standard owner flow of `comparison` bootstraps an internal draft automatically, without making explicit set selection the visible first step.
- The standard comparison material is `wordlist`; alternative material such as corpus-specific `text`/`Satzliste`, saved-set context, and the handoff to `phenomena` remain secondary.
- The productive `comparison` UI is a vertical first-workflow of `Sprecher:innen auswählen`, `Items auswählen`, and one full-width comparison matrix as the dominant work surface.
- Internal draft or set lifecycle state remains functional but must stay de-emphasized in the visible `comparison` UI; the workbench should primarily read as speaker selection, material choice, and matrix work rather than as exposed set architecture.
- The visible speaker selector in `comparison` is speaker-first, row-dense, and structurally split into three simultaneous areas: `Lernende`, `Native Speaker`, and the active `Ausgewählt` composition; `person_id` is the primary line, while level, localized native reference, and `L1` remain the secondary metadata, and internal `session_id` stays functional without becoming the visible headline pattern.
- In that visible three-column comparison selector, learners and native speakers are separate source lists, while `Ausgewählt` reads as the active assembly area rather than as a third source catalog; the selected list keeps learners above native speakers and exposes a direct remove action instead of a pure status indicator.
- The standard visible speaker filters in `comparison` are `Suche`, direct level chips `A1`, `A2`, `B1`, `B2`, and `L1 wählen`, with secondary controls such as `Geschlecht` and `Sprachaufenthalt` grouped under `Weitere Filter`; native-speaker access is handled primarily through the dedicated native source column rather than through a visible `Native` filter chip.
- The visible material control in `comparison` stays compact and honest: `Wortliste` is the standard, `Satzliste` is the secondary alternative, and the same first block may expose one adjacent secondary `Set wählen` select with a quiet info hint that sets are created and adjusted in `phenomena`; that select may list curated example sets plus saved owner-bound custom sets from `phenomena`, but `comparison` does not expose a separate handoff button or a second right-side material island.
- Choosing one of those visible curated or custom comparison sets reuses the current owner-bound comparison draft and replaces its item scope in place; the dropdown does not spin up a second visible draft workflow for every selection.
- The visible `comparison` surface does not repeat login or sign-in hints inside the workbench body; access clarification belongs before the page, not as a CTA inside the first comparison step.
- Locale changes inside `comparison` do not rebuild the workbench from localized labels; selected sessions, active compare composition, current task scope, and comparable filter state stay keyed by stable machine values such as `set_id`, `session_id`, task keys, and filter keys.
- The comparison matrix keeps `Item` as the left stub header, uses speaker badges in column headers for learner/native semantics, and exposes clip playback plus direct item download as the visible row actions.
- Comparison matrix playback and direct item download both stay on the canonical player item delivery family, but playback must use a browser-safe inline audio response while explicit download intent keeps the delivery filename contract without forcing attachment semantics onto matrix playback.
- The visible matrix controls reuse the same calm player control language for volume and speed, without a separate prominent `Stoppen` button, and the empty state should read as an informative note rather than as a blank dashed placeholder frame.
- The three speaker columns in `comparison` stay one shared container family with the same header divider logic; `Ausgewählt` may read only as a subtle active variant of that same pattern.
- The upper speaker selector cards are the visual reference component in `comparison`; matrix speaker headers reuse that same card family only as a denser, narrower adaptation and must not introduce a second independent header-card language.
- Learner speaker cards and matrix headers omit a redundant visible learner label; learners show `person_id`, level, and `L1`, while native speakers show `person_id` plus one translated native-reference badge. The visible native column context already names the role, so a second `Native` badge is not repeated inside each row.
- The comparison matrix keeps a fully opaque sticky top header and sticky left item stub as stable comparison anchors; the left stub uses a fixed three-zone layout with item number, left-aligned item text, and row-play action, stays visually stable in a desktop corridor of roughly 280-320 px, and must support both short `wordlist` items and later `text`/`Satzliste` items with a calm maximum of two visible text lines.
- Visible comparison playback state stays inside the matrix itself: there is no separate playback status line above the table, and the active matrix cell reads as a calm full-cell state with centered actions rather than as a small badge behind the controls.
- Active item curation still belongs to `phenomena` and not to a second comparison-only item editor.

### `phenomena`

- `phenomena` uses the existing research page route `/{ui_lang}/research/{language}/phenomena`.
- `phenomena` is a protected list-curation workbench with one overview route plus dedicated detail routes for curated presets and owner-bound custom sets.
- The productive overview route stays linear after login: page header, one `1 Set wählen` block with `Set suchen` plus `Neues Set`, one unified list of curated and custom entries, and only functional list-end empty states.
- The overview does not expose an active workspace, task/material configuration, save controls, player/comparison handoff, or other parallel work areas.
- Curated entries are distinguished only by badge/status, expose `Ansehen` and `Modifizieren`, and are never deletable from the overview.
- Custom entries are distinguished only by badge/status, expose `Bearbeiten` as the primary action, and keep `Umbenennen` plus `Löschen` in a secondary overflow action family.
- The curated preset editor route is an authenticated research-editor route; saving owner-bound work still requires authenticated owner context through the canonical `/api/research/sets` route family.
- The owner-bound custom-set editor route requires authenticated owner context; loading or mutating one concrete stored set without owner context is not part of the public web surface.
- The productive editor surface exposes one readable title field, one persisted `Notiz` field, a visible type/save-state status line, two stable source columns for the full `Wortliste` and `Satzliste`, and one lower `Ausgewählte Items` area with one explicit shared saved order across both task types.
- The productive editor exposes one visible save action, not a visible `Speichern als`; owner-bound save semantics now use the canonical `/api/research/sets` create, patch, delete, and item-replacement flows.
- If unsaved changes exist in the productive `phenomena` editor, normal in-app navigation uses the same app-level confirm dialog as discard flows; browser-native unload prompts remain only as fallback for reload, close, or comparable browser-level exits.
- In the current productive `phenomena` phase, player and comparison handoff are intentionally absent from both overview and editor so the page stays a focused list-curation surface.

## Card Logic

### Speaker cards

- One card per `person_id`.
- Cards show reduced person-facing metadata.
- `person_id` is the dominant primary line on the card.
- The selected session is shown as a secondary line under `person_id`.
- The footer label is `Aufzeichnungen`.
- The visible footer order is profile action first, then the recordings label, then the compact task actions.
- Cards expose compact direct task links for the currently selected or matched session.
- Compact task-entry links in speaker cards and speakers-table rows reuse the shared compact inline-action family with an arrow affordance; they must read as actions and stay visually distinct from chips and badges.
- The profile CTA remains visually secondary to the card identity and uses the shared localized `Profil`/`Profile` label with inline arrow affordance.
- The UI does not show a separate `Treffer über ...` match note on the card.
- Learner-level accents stay on the shared learner scale, while native-speaker cards and session containers use the dedicated native accent `#18677A`.
- Speaker cards and profile-session containers use a shared `0.5rem` top accent bar.
- In native-speaker overview cards, the `Standardvarietät` row renders the localized native-reference value as the shared `native-detail` badge instead of plain body text.
- Native-speaker overview cards keep localized variety or origin metadata and must not show both `standard_variety` and `origin_country` when they collapse to the same user-facing label.

### Matching behavior

- Matching is existential over sessions.
- A person matches filters when at least one session matches them.
- Session-based filters do not create duplicate person cards.

## Profile Logic

### Shared profile semantics

- The page is labeled `Profil` in the German UI and `Profile` in the English UI.
- The profile route is an authenticated research-detail route and is not publicly renderable outside the login boundary.
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
- The profile header shows the speaker-group badge plus one localized native-reference badge, and the metadata section does not repeat `Standardvarietät` separately when it resolves to the same localized label as `Herkunftsland`.

## Task Semantics in Research UI

The canonical task and workbench capability contract lives in `docs/spec/research-capabilities.md`. The rules below describe the active visible semantics that remain relevant for research access and UI behavior.

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

## Active UI-Metadata Contract

### Person fields used by the UI

- `person_id`
- `l1`
- `l1_additional`
- `mother_l1`
- `father_l1`
- `additional_languages`
- `gender`
- `birth_year`
- `current_region`
- `childhood_region`
- `origin_country`
- `origin_region`
- `person_notes`
- `research_consent_signed`
- `teaching_consent_signed`
- `consent_date`
- `consent_file`
- `questionnaire_file`
- `secure_notes`

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
- `session_notes`
- `notes`
- `tasks`
- `files`

### Exposure fields

- `exposure_entries.country`
- `exposure_entries.duration_months`
- `exposure_entries.type`
- `exposure_entries.exposure_notes`

Rules:

- These internal metadata fields are available only in protected Research contexts, not in public Teaching or other public routes.
- `person_notes`, `session_notes`, and `secure_notes` are internal readable notes.
- `teaching_consent_signed` is a protected safety and eligibility flag for manual Teaching selection only and is not an automatic publication switch.

## Non-goals of the Current Runtime

- no real XLSX import pipeline in the web runtime
- no second research data source
- no separate task-specific player families
- no separate comparison player
- no native-speaker interview path
