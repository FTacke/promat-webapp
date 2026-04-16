# PROMAT Spec: Platform, Data, and Files

## Status

This file is the binding source of truth for PROMAT platform structure, routing, runtime boundaries, IDs, filesystem semantics, and active controlled vocabularies.

Research task and page capability semantics are defined in `docs/spec/research-capabilities.md`.

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
/{ui_lang}/research/{corpus_language}/phenomena/presets/{preset_id}
/{ui_lang}/research/{corpus_language}/phenomena/sets/{set_id}
```

### Research player delivery route schema

```text
/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}/audio.mp3
/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}/items/{item_id}.mp3
```

### Research set API route schema

```text
/api/research/sets
/api/research/sets/{set_id}
/api/research/sets/{set_id}/items
/api/research/sets/{set_id}/sessions
/api/research/sets/{set_id}/save-as
```

- The canonical server request and response shape for an owner-bound research set nests workbench-specific state under `workbench_state`.
- `workbench_state` carries `preferred_task`, `comparison_view_task`, and comparison session selections, while the set core keeps identity, lifecycle, label or note, provenance, and explicit item references.
- Top-level compatibility aliases such as `preferred_task`, `comparison_view_task`, and `sessions` are not part of the active set JSON contract.
- `/api/research/sets/{set_id}/sessions` mutates the owner-bound workbench session selection attached to that `set_id`; it does not redefine the canonical set item list.

### Active technical route values

- `ui_lang`: `de`, `en`
- `section`: `project`, `research`, `teaching`, `sample`
- `corpus_language`: `spanish`, `french`, `german`, `english`

### Auth route schema

```text
/login
/access-request
/auth/login
/auth/account
/auth/account/password
/auth/password/forgot
/auth/password/reset
/admin/users/page
/admin/analytics/page
/admin/users
```

### Active research pages

- `design`
- `speakers`
- `recordings`
- `comparison`
- `phenomena`

### Active research detail routes

- `player`
- `phenomena` preset editor
- `phenomena` owner-set editor
- `player`-scoped protected media delivery for current-session playback and single-item download

### Active teaching pages

- `phenomena`
- `materials`

### Routing rules

- Technical slugs and route segments stay English.
- UI language and technical routing language must not be mixed.
- The public login surface stays on `/login`, while mutating auth actions stay under `/auth/*`.
- PROMAT login is email-only. Public username login and self-registration are not part of the active product contract.
- Public access requests use the canonical `/access-request` page and store one request record in the auth/core database instead of sending users to a `mailto` draft.
- The canonical public access-request form requires at least first name, last name, institution, role or function, institutional email address, purpose of use, and one explicit confirmation of the data-protection and confidentiality obligations for pseudonymized research data.
- Public auth-entry pages `/login` and `/access-request` redirect already authenticated users to the safe requested target first, otherwise to the canonical protected default target for their role.
- Accounts are created administratively and use one password-setup/reset token flow that is valid for 14 days unless an active environment setting shortens or extends it.
- The productive protected-area role model contains only `user` and `admin`; `editor` is not part of the active PROMAT product contract.
- Account access must be blocked before session issuance when the account is inactive, not yet valid, expired, deleted, or temporarily locked.
- Admin user management uses the canonical `/admin/users` route family for account creation, status updates, optional expiry dates, and invitation/reset preparation.
- The canonical protected default targets after login are: safe requested target first, otherwise `/auth/account` for `user` and `/admin/users/page` for `admin`.
- Research page order, page access metadata, task subsets, compare capability, set-filter capability, render-mode vocabulary, and corpus-specific workbench readiness are defined centrally through the active research capability contract.
- For all active corpora `spanish`, `french`, `german`, and `english` and for both active UI languages `de` and `en`, `/{ui_lang}/research/{corpus_language}/design` is the only public corpus-scoped research page.
- The corpus root `/{ui_lang}/research/{corpus_language}` is a public corpus landing page that orients users to `design`, `speakers`, `recordings`, `comparison`, and `phenomena` through their canonical routes.
- All other corpus-scoped research pages and research detail routes, including protected player-media delivery, are authenticated app surfaces and must enforce access before the workbench or media response is rendered.
- `player` is a research detail route under one concrete corpus language and must not fork into separate task-specific route families.
- The `task` segment of the player route uses only the canonical research task keys `wordlist`, `text`, and `interview`.
- `comparison` and `phenomena` remain first-class research page routes; `phenomena` may additionally own dedicated editor subroutes, but neither page may collapse into alternate `player` path shapes.
- Mixed research selections stay in query context or server-side set state and must not introduce a `mixed` player task value.
- The current productive `player` query context may add `compare_session` plus optional `compare_mode=manual` for the bounded `wordlist` comparison extension without creating a second route family; omitted `compare_mode` keeps the default compare item-check behavior `Beide abspielen`.
- Player media delivery stays under the same `player` route family and resolves protected session artifacts through application logic, not through static publication of `data/`.
- Research access logic must stay corpus-generic; do not add corpus-specific public-workbench exceptions such as a Spanish-only protected path and public placeholders elsewhere.
- Corpus-specific productive-vs-placeholder research workbench readiness must be expressed through the canonical capability layer, not through router-local language branches.
- Owner-bound research set writes and reads use the `/api/research/sets` route family under JWT protection and must not trust client-supplied ownership fields.
- Old German technical slugs and old public routes must not be reintroduced.

## Active App Shell

- All public non-landing inner pages use the same shared app shell.
- The landing page is the only public layout exception.
- The shared inner shell keeps the global topbar as the stable upper level and the local page shell below it.
- If the authenticated account menu exists in the global topbar, it stays closed by default, opens only on explicit trigger activation, closes again on outside click, `Escape`, trigger re-click, and navigation, and must not persist a sticky-open state across reloads or page transitions.
- In the authenticated topbar user menu, `Mein Konto`/`My account` is always present, `Admin-Bereich`/`Admin area` appears only for admins and leads directly to `/admin/users/page`, and `Logout` stays the final item.
- The global topbar utility order is language switch, theme switch, then account or login control.
- The language switch is a compact text-based `DE | EN` control in the topbar utility zone, not a flag or primary globe-icon control, and it must keep users on the current route while switching `ui_lang`.
- The local page shell uses a left sidebar for area navigation and a right main-content column.
- The sidebar begins with a permanent area header: section icon, section title, and a subtle divider.
- Language-context pages keep their language back-link and language title below that permanent area header, not instead of it.
- On research language-context pages, that sidebar context title uses the same localized corpus title as the main page heading, for example `Spanisch-Korpus` / `Spanish corpus`, not only the bare language label.
- Sidebars are area navigation only and must not repeat account actions such as `Mein Konto`, `Admin-Bereich`, or `Logout`.
- Protected admin pages reuse the shared inner shell with one non-clickable `Admin-Bereich` sidebar header and the fixed linear navigation `Benutzer`, `Analytics`.
- On public research pages for unauthenticated users, protected research targets stay visible in the sidebar but use muted locked navigation states rather than per-item login notices.
- In those muted locked research sidebar states, the lock icon renders immediately after the visible page label and no additional visible `login required` helper line is repeated inside the navigation list.
- Breadcrumbs are rendered only when they add real orientation value, not as a pseudo-context line that merely repeats section or language.
- Desktop shows breadcrumbs only from hierarchy depth 3 onward because the sidebar already carries orientation on flatter levels.
- Mobile shows breadcrumbs from hierarchy depth 2 onward because the sidebar is reduced or absent there.
- When a breadcrumb is shown, it always renders the full path including the current page as the final, non-clickable item.

## Sample Surface

- `sample` is a showcase for current, already accepted layout elements of the webapp.
- `sample` never defines the target UI for product pages; it mirrors the current implementation on real pages.
- If an active layout element is changed on a real page and `sample` contains that element, `sample` must be updated in the same run.

## Active UI System

- Productive pages, shared partials, and established CSS families are the visual source for recurring UI work; `sample` mirrors them but does not replace them as the design reference.
- `de` and `en` are the active public UI languages for finished surfaces under the canonical `ui_lang` route context.
- Finished or newly completed UI surfaces must ship with both `de` and `en` display strings in the same run; do not treat English as a later copy-only follow-up for already-finished visible UI.
- Visible UI strings for finished surfaces must resolve through the shared translation layer and server-provided localized payloads; do not hardcode visible `de`/`en` branches or fallback copy in Python builders, Jinja templates, or page JavaScript.
- Technical keys, route values, IDs, and client-state field names remain stable English machine values and must stay separate from translated display labels.
- Standalone auth surfaces on `/login`, `/access-request`, and `/auth/password/*` use the dedicated auth shell without research sidebar, corpus navigation, or workbench framing.
- Visible auth-facing product naming uses `Pronunciation Matters`; `PROMAT` remains the internal or technical shorthand unless an active spec explicitly requires a visible exception.
- The public auth surfaces on `/login`, `/access-request`, and `/auth/password/*` reuse the current PROMAT action, input, and message families instead of page-local MD3 or legacy CORAPAN-looking controls.
- On `/login` and `/auth/password/*`, the access request remains a quieter secondary section below the primary sign-in or reset flow.
- On `/access-request`, the primary work surface is the form itself, while the login hint remains a quieter secondary card below it.
- The research section root `/{ui_lang}/research` stays a compact corpus-selection overview without an additional intro or subtitle block below the page heading.
- On that research section root, each corpus card shows only the localized corpus title, then the primary metadata order `Projektleitung`/`Project lead`, `Materialkonzeption`/`Material design`, `Durchführung`/`Conducted by`, and then the secondary status order learner-recordings count or `Korpus im Aufbau`/`Corpus in progress` followed by the optional reference-recordings line only when at least two distinct native-speaker `standard_variety` values exist.
- The research section-root corpus cards do not use repeated descriptive body copy such as generic learner-pronunciation summaries; the cards are metadata-first orientation surfaces, not mini content teasers.
- Those research section-root corpus cards stay inside the existing app card system rather than introducing a separate overview-card language: speaker cards are the primary visual reference for their accent bar, quiet materiality, divider rhythm, secondary-label styling, and bottom CTA treatment.
- The fixed visible structure of each research section-root corpus card is title, primary metadata block, secondary status block, and footer CTA; the CTA remains bottom-aligned and uses the neutral existing inline-action secondary styling instead of language-colored button text. Reuse existing tokens, card wrappers, divider spacing, and inline-action families before introducing any research-card-local style hooks.
- Across the shared app card system, if a card exposes a visible action area, footer CTA, or equivalent action/footer block, that action block stays bottom-aligned at the end of the card rather than floating in content height. This is a binding system rule for all card families, not a page-local preference.
- Across the shared app card system, any content block that sits directly above a divider-separated footer or follow-up action section keeps a minimum block-end inset via the shared divider spacing tokens, so status text, recordings labels, or comparable meta rows never visually stick to the next divider.
- The public corpus landing page `/{ui_lang}/research/{corpus_language}` is a reduced orientation page. The left sidebar remains the only area navigation, and the main column must not repeat `Design`, `Sprecher:innen`, `Aufnahmen`, `Vergleich`, or `Phänomene` as a second list, card set, or CTA wall.
- In the main column of that public corpus landing page, the visible structure is limited to the localized corpus title, one short subtitle, two short prose paragraphs, and for signed-out users one small action row with exactly two actions in this order: `Zugang beantragen`/`Request access`, then `Zum Login`/`Go to login`.
- The first prose paragraph on that public corpus landing page explains the corpus as a research area with public design information plus protected work areas and points users to the left navigation instead of rebuilding the area navigation in the body.
- The second prose paragraph explains the privacy and access frame in calm prose, explicitly names legitimate users as Angehörige von Forschungs- und Bildungseinrichtungen / members of research and educational institutions, and keeps the user journey order request-access first, login second.
- The login action on that public corpus landing page preserves the exact corpus-root return target, so a user who starts on one concrete corpus landing page returns to that same landing page after successful authentication instead of being dropped into a generic auth default.
- For authenticated users, that public corpus landing page suppresses the anonymous action row and keeps the reduced orientation copy only.
- Visible UI must not expose raw technical values such as UUID-like set identifiers, internal translation keys, or internal handoff/debug vocabulary when a user-facing label or omission is the truthful product behavior.
- When a recurring UI family already exists, it must be extended or reused before a page-local variant is introduced.
- Repeated UI families that must be treated systemically include action hierarchy (`buttons`, inline actions, overflow actions), form controls (`inputs`, `selects`, `textareas`), badges and chips, cards and list rows, step containers and work blocks, dialogs and confirm flows, empty states, sticky headers or anchors, and muted, active, or selected states.
- Badge, chip, and pill content across the active research UI stays on the regular UI font family rather than the reading or book typography, even when the surrounding item or content text uses the reading font.
- Research workbench UI uses current productive pages as reference surfaces: `comparison` for step containers, selection blocks, badge or meta rhythm, and clear vertical work sequences; `player` for dense material rows, compact work heads, sticky anchors, and muted versus active row states; `speakers`, `recordings`, and the person profile for speaker cards, compact task actions, and row or table action layout.
- Learner speaker cards in the `speakers` card family keep neutral card containers with no decorative top bar; CEFR or level color belongs on the explicit level badge in the level meta row, not on the card chrome. In the learner overview card, the compact visible fact set is level badge, `L1`, gender, and target-country stays; `Sessions` and recording-year summary do not belong to that overview card anymore. Native-speaker cards may keep their separate teal category accent because they encode speaker-group semantics rather than CEFR level.
- Across speaker cards, profile headers, player metadata cards, and comparison speaker rows, native-speaker variety or origin display uses one canonical localized native-reference value derived from `standard_variety` and `origin_country`; raw slugs such as `ES_STD` are never shown, and if variety and origin country resolve to the same user-facing label, that label is rendered only once.
- Shared profile CTAs in speaker cards and player metadata cards use the same localized `Profil`/`Profile` label with the existing inline-action arrow affordance; variant copy such as `Profil öffnen` or `Open profile` is not part of the active UI contract.
- Overview surfaces stay overview surfaces, and editor or detail surfaces stay editor or detail surfaces; active split flows must not be collapsed back into mixed one-page workbenches without an explicit spec change.
- If shared layout files, shared component CSS, or reused partials change, the affected repeated UI families must be regression-checked on at least one other active page that uses them.
- Visually substantial UI changes require browser validation and screenshot comparison against the affected productive reference surfaces before the run is considered complete.
- For finished bilingual surfaces, browser validation must cover the same real routes in `de` and `en` and explicitly include dialogs, placeholders, empty states, snackbars, overflow actions, and longer English labels where they affect layout or density.
- A substantial UI run is not accepted on green tests alone; visible defects found in the browser pass must be fixed and the screenshots regenerated until the in-scope surfaces are linguistically and visually clean.

## Runtime Boundaries

- `AUTH_DATABASE_URL` is the canonical auth/core database variable.
- `PROMAT_RUNTIME_ROOT` is the canonical runtime root.
- `PROMAT_PUBLIC_ROOT` is the canonical public root.
- Paths are derived through runtime/config wiring, not freehand string paths.
- For the default local development PostgreSQL URL `postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:54321/promat_auth`, `scripts/dev-start.ps1` is the canonical app entrypoint and must ensure the local `promat_auth_db` service plus the idempotent auth/core and research-set migrations are applied before the Flask app starts.
- In that canonical local development flow, `scripts/dev-start.ps1` also owns the live browser loop on `127.0.0.1:8000`: it must clear stale PROMAT dev listeners before launch and start the Flask app in development reload mode so code and template changes become visible in the browser without manual process hunting.
- If that default host port cannot be published on a dev machine, `scripts/dev-start.ps1` and `app/scripts/dev-setup.ps1` may select a free local fallback port through `PROMAT_DEV_DB_PORT`, but they must keep `AUTH_DATABASE_URL` aligned to the actually published local PostgreSQL host port before migrations, admin seeding, or app startup.
- In that canonical local dev flow, `scripts/dev-start.ps1` also seeds or updates one reliable default admin account with the reachable email `felix.tacke@uni-marburg.de` unless explicit overrides are supplied.
- `app/scripts/dev-setup.ps1` remains the canonical initial bootstrap path for the same local PostgreSQL setup; it provisions the local database, applies the same migration chain, and then may hand off to `dev-start` without re-running bootstrap work.

## Dev/Prod Parity

- Dev and Prod use the same architecture, terminology, routing, and data semantics.
- Allowed differences are infrastructure-level only.
- Research-data architecture must not diverge into Dev-only fallback stores or shadow structures.
- PostgreSQL is the binding database strategy for research-data work.
- The owner-bound research set model persists in PostgreSQL and does not get a second browser-only or file-backed storage path.
- The PostgreSQL model keeps one canonical set core plus a dedicated owner-bound workbench-state submodel; comparison filters or session selections must not be folded back into the set core columns.

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
- For the current English running-text path, `data/config/research_player/english/task_catalogs/text.json` is the canonical connected-text catalog under the technical task key `text`; it keeps visible item numbers `T1`, `T2`, `T3`, ... together with stable item IDs `t_01`, `t_02`, `t_03`, ... and includes `The Boy who Cried Wolf` as `T1` because the real material and the segment TextGrid show that title as spoken content.
- For the current English wordlist path, `data/config/research_player/english/task_catalogs/wordlist.json` is the canonical content catalog for the exact provided word and minimal-pair forms, including multi-word entries and punctuation exactly as sourced.

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
- When a batch provides real untouched original WAV masters under `scripts/research_data_intake/import/{batch_name}/raw/`, the productive session tree under `data/sessions/{language}/{session_id}/raw/` must archive them.
- `source/` contains processed working WAVs and remains the operative audio basis for analysis-aware derivation steps.
- `raw/` and `source/` are distinct archive versus working layers and must not be silently mixed or substituted for one another.
- `alignment/` contains whole-session TextGrid files and reduced alignment JSON such as `alignment/wordlist.json`, derived from canonical task catalogs plus session-specific alignment and audio data.
- `derived/` contains webapp-facing derivatives such as MP3 and does not replace the WAV-based analysis basis in `raw/` or `source/`.
- `items/{task}/` contains split MP3 files only.

### File rules

- Canonical task filenames use `wordlist`, `text`, `interview`.
- Reduced alignment JSON belongs under `alignment/{task}.json`, never under `items/`.
- Player-facing full-task MP3 files use `derived/{task}.mp3`.
- Player-facing split MP3 paths use `items/{task}/{item_id}.mp3`.
- Versioned runtime session trees under `data/sessions/` must not ship fictional, placeholder, or other dummy research sessions; production population of that tree is reserved for the central orchestrating import path.
- The only active path that may populate or update production runtime session trees from intake batches is `scripts/research_data_intake/import_batch_to_production.py`.
- That central importer must copy real batch raw masters into `raw/{task}.wav` whenever the batch provides an unambiguous untouched original WAV for that person and task.
- It must never synthesize `raw/` by copying processed `source/` WAVs, and a missing real raw master must remain visibly missing rather than be masked.
- If multiple raw-master candidates exist for one person and task or an archived raw file already differs from the current batch raw source, the importer must report a conflict instead of silently overwriting or guessing.
- For the current Spanish sentence-list catalog, visible numbering remains `D1` through `D30`, `QY1` through `QY10`, and `QW1` through `QW10`, while stable technical IDs remain `d_01` through `d_30`, `qy_01` through `qy_10`, and `qw_01` through `qw_10`.
- The current player delivery routes map full-task playback to `.../player/{session_id}/{task}/audio.mp3` and single-item item-media delivery to `.../player/{session_id}/{task}/items/{item_id}.mp3` without exposing internal runtime paths.
- The canonical single-item player route serves a playback-safe inline `audio/mpeg` response by default; explicit download semantics stay on the same route family through explicit download intent rather than through a separate media path.
- For the current `wordlist` production path, web derivatives use MP3 in mono with `160 kbps` CBR for both `derived/wordlist.mp3` and `items/wordlist/{item_id}.mp3`.
- Internal split filenames use stable `item_id`s.
- Single-item download filenames are generated separately at delivery time and do not redefine internal storage paths.
- The prepared delivery filename contract is `{person_id}_{task}_{item_id}_{download_label}.mp3`.
- `download_label` is a readable delivery-only text component derived from the canonical text or label of the exported unit.
- Longer filenames with `session_id` and labels are for later download logic, not canonical storage.
- Current Spanish dev example WAVs are processed `source` audio, not `raw` masters.

## Intake Batch Working Filesystem

### Batch root

```text
scripts/research_data_intake/import/{batch_name}/
```

### Batch substructure

```text
processed/
raw/
intake_data/
working/
```

### Semantics

- Batch directories under `scripts/research_data_intake/import/` are generic intake areas and are not hard-wired to one corpus language.
- A processable batch directory must keep `batch` in its directory name and must provide at least `processed/`.
- `processed/` is the primary intake input for file-based organization of task WAVs and TextGrids.
- `raw/` is optional at batch level, but when it contains real untouched original WAV masters it is the archival source for the productive session-tree `raw/` layer.
- Batch `raw/` must not be collapsed into `source/`; processed working WAVs remain a separate operative layer.
- `intake_data/` is optional and may carry workbook or helper material, but it is not itself the derived working tree.
- The active production importer reads workbook steering data from `intake_data/*.xlsx` together with the batch-local `working/` tree.
- `working/` is a pre-production, person- and task-centered preparation area inside one concrete batch.
- Batch-local `working/` outputs are preparatory only: they must not write into `data/`, must not create production session metadata, and any `alignment/text.json` created there remains a working-tree intermediate artifact rather than a transferred production session artifact.

### Working subtree

```text
working/{person_id}/wordlist/source/wordlist.wav
working/{person_id}/wordlist/alignment/wordlist.TextGrid
working/{person_id}/text/source/text.wav
working/{person_id}/text/alignment/text.TextGrid
working/{person_id}/text/alignment/text.json
working/{person_id}/text/mfa_corpus/
working/{person_id}/text/mfa_output/
working/{person_id}/text/mfa_manifest.json
working/{person_id}/interview/source/interview.wav
working/{person_id}/interview/alignment/interview.TextGrid
```

### Working rules

- The canonical task filenames inside `working/` are always task-based, for example `source/text.wav` and `alignment/text.TextGrid`, regardless of the intake filename that carried the file into the batch.
- Person and task assignment for batch-file organization must come from explicit filename logic only; the pipeline must not invent person IDs or task names heuristically.
- In the current preparatory `text` path, the TextGrid is only the segment-boundary source.
- The preparatory `text` MFA step may create only segmented WAVs, matching `.lab` transcripts, `mfa_output/` target directories, and a batch-local manifest for reverse mapping.
- The batch-local `text` import step may derive `working/{person_id}/text/alignment/text.json` from the preparatory manifest plus MFA `mfa_output/` TextGrids, while still staying inside the batch-local working tree.
- In this working-tree-only `text` JSON step, `audio.full_mp3` may already point to the canonical future relative artifact path `derived/text.mp3` even though the MP3 artifact is not produced yet in that same step.
- In this working-tree-only `text` JSON step, `session_id` may remain `null` until later metadata integration resolves the final production session identity.
- The preparatory `text` MFA step must obtain canonical item texts from an explicit external source such as a task catalog or mapping JSON and must not guess final texts from TextGrid labels.
- The current intake language configuration for this working path is prepared generically for `es`, `de`, `fr`, and `en`, including the mapped MFA acoustic and dictionary models per language.
- Final production transfer from intake batches into `data/sessions/` is executed only by the central importer `scripts/research_data_intake/import_batch_to_production.py`.
- That importer may populate PostgreSQL research metadata tables `research_people`, `research_sessions`, and `research_session_exposures` from workbook sheets `Research_Person`, `Research_Session_Intake`, and `Exposure`.
- The same importer projects canonical runtime `metadata.json` plus task artifacts into `data/sessions/{language}/{session_id}/`, archives real raw masters into `raw/`, and may sync only the productive task layers whose working inputs are actually available.
- For archive sync, raw master mapping must stay explicit and filename-driven by person and task; it must not be inferred heuristically from workbook prose or substituted from processed working files.
- Interview remains a declared task key and structure slot, but no productive interview artifact import exists yet.

## Active Metadata Semantics

### Person-level fields

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

- `l1`, `l1_additional`, `mother_l1`, and `father_l1` use the same uppercase value list as `l1_code`.
- `l1_additional` is optional, stores one or more semicolon-separated L1 codes, and stays separate from `additional_languages`.

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
