# PROMAT Spec: Research Player

## Status

This file is the binding source of truth for the target architecture of the research player in the PROMAT webapp.

## Scope and Relation

- This spec defines the unified research-player architecture for future implementation runs.
- `docs/spec/platform-data-files.md` remains binding for routing, runtime boundaries, and filesystem semantics.
- `docs/spec/research-access.md` remains binding for research IA and access logic around speakers, recordings, profiles, comparison, and phenomena.
- `docs/model_mds/speech_text_sync.md` is a technical reference only and is not normative for PROMAT.

## Core Architecture

- PROMAT has exactly one modular research player for the whole webapp.
- There are no separate player implementations for `wordlist`, `text`, and `interview`.
- Task differences are implemented through task modes, render modes, and optional context extensions, not through separate player products.
- Comparison is a bounded extension of the same player base.
- Phenomena presets are a bounded extension of the same player base.
- Shared player logic must be changeable once in the base architecture and must not require parallel task-specific rewrites.

## Route and Entry Contract

- The canonical player route is `/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}`.
- `task` uses only the canonical research task keys `wordlist`, `text`, and `interview`.
- The route path identifies the primary session and the initial task.
- The player is a research detail route, not a second section root and not an additional sidebar page.
- The same route family must be callable from `speakers`, `recordings`, `profile`, and later from `comparison` and `phenomena`.

### Optional query context

- `source`: identifies the entry source and may use `speakers`, `recordings`, `profile`, `comparison`, or `phenomena`.
- `preset_id`: identifies an optional phenomena preset context.
- `compare_session`: identifies an optional secondary comparison session.
- `compare_mode`: identifies an optional compare-item override and currently uses `manual`; omitted compare mode keeps the default compare item-check behavior `Beide abspielen`.
- `focus_item`: identifies an optional focused item.
- `focus_segment`: identifies an optional focused segment.
- `render_mode`: may override the corpus default render mode for the technical task `text`.

### Route rules

- Optional query context may refine the player state, but it must not create separate route families or separate player implementations.
- Invalid optional query context must degrade to the nearest valid base state instead of breaking the whole page.
- Source context is navigational context only and must not alter the base architecture of the player.
- Protected media delivery for the current player stays inside the same route family via `.../audio.mp3` for full-task playback and `.../items/{item_id}.mp3` for single-item download.
- These delivery routes resolve protected session artifacts through application logic; they do not redefine internal storage paths and they do not publish the artifacts under `public/`.

## Player State Model

The player state must be able to represent at least these values:

- `language_slug`
- `session_id`
- `person_id`
- `speaker_type`
- `recording_date`
- `task_key`
- `available_tasks`
- `render_mode`
- `preset_id` as optional preset context
- `compare_session_id` as optional comparison context
- `focused_item_id` as optional item focus
- `focused_segment_id` as optional segment focus

### State rules

- One primary session is always required.
- Speaker identity is derived from the primary session and is not a separate player root.
- The current productive compare extension also needs one optional comparison-playback value for the primary plus optional secondary state; omitted value keeps `Beide abspielen` as the default item-check behavior and `manual` switches item clicks back to per-side playback.
- A focused item or segment may narrow the visible context, but it does not replace the primary session or task state.
- Comparison context is optional and only valid for compatible tasks.
- Preset context is optional and may coexist with manual item additions inside the same player state.

## Shared Player Surface

- The player uses a neutral content header and must not hardcode learner-specific wording such as `Lernende` in the title block.
- The same surface must work for learner and native-speaker sessions.
- A compact metadata card appears in the player header area.

### Required metadata fields

- `session_id`
- `person_id`
- speaker group
- recording date
- profile link

### Optional directly listening-relevant fields

- learner level or native standard variety
- learner `L1` or native origin country
- further compact listening-relevant core facts that already exist in the research UI

### Metadata-card rules

- The metadata card reuses the existing visual semantics of speaker cards where appropriate, especially for speaker type and level or variety cues.
- The player must not introduce a second competing color or badge taxonomy.
- Productive player metadata cards keep the shared research accent system: learner levels stay on the learner scale, native sessions use the dedicated accent `#18677A`, and the family uses the shared `0.5rem` top accent bar.
- In the productive `wordlist` player, session selection belongs to the metadata-card identity layer, not to the playback toolbar: the visible `session_id` acts as the session switcher in the card header.
- The player may expose one compact page-level back action outside the playback control bar, but it must remain one route-context action and not expand into a second competing player header system.
- Each visible metadata card exposes its own profile action so that primary and comparison sessions can both open their corresponding speaker profile directly from the player surface.

## Task Switching

- Loading one task for a session opens the unified player base for that session.
- The player exposes all documented session-available tasks as one shared task switch.
- Switching tasks stays inside the same player architecture and does not jump into separate task-specific player implementations.
- The task switch retains the primary session, metadata card, and route family.
- Preset or focus context should be retained across task switches where it remains valid.
- Tasks that are not available for the current session may remain visible as disabled, non-interactive controls.
- In the current MVP, `wordlist` is the only production-ready task mode; documented `text` and `interview` tasks stay visible in the same switch but render as honest unavailable states until their task renderers exist.

## Task Modes

### `wordlist`

- The full player does not show phonetic transcription in the wordlist mode.
- The productive `wordlist` surface is ordered as metadata cards first, playback or compare controls second, and the wordlist or comparison list third.
- In single-session `wordlist` view, the primary metadata card uses the full available width.
- Compare is a conscious optional state in `wordlist`: the single-session view shows no permanently open comparison selector in the playback zone.
- In the productive `wordlist` player, the primary card exposes a secondary action `Vergleich hinzufügen`; activating that state reveals the secondary comparison card instead of introducing a permanently visible compare form in the toolbar.
- Once compare is active and a valid `compare_session` exists, the productive `wordlist` surface shows two equal-width metadata cards directly above the two aligned comparison columns.
- The productive playback zone for `wordlist` is a calm two-row transport area: row one contains play or pause, time, and seek; row two contains only global volume and speed controls.
- Clicking a `wordlist` item is always an item-level check and never means continuing the whole recording from that point onward.
- In single-session `wordlist` view, clicking an item plays only that specific primary clip.
- In productive compare-ready `wordlist`, `Beide abspielen` is enabled by default and item clicks play the primary item first and the matching comparison item second for exactly that chosen item.
- If the compare item toggle is disabled, left-item clicks play only the primary side and right-item clicks play only the comparison side for the chosen item.
- Global play remains separate from item checking: it resumes the current global audio context at its current position and does not reuse the item-click semantics.
- Productive `wordlist` compare does not expose a separate compare-mode block anymore; the only compare-item override is a single toggle labeled `Beide abspielen`.
- The compare item toggle belongs to the comparison-list header, not to the global playback controls, because it changes comparison-item click behavior rather than global transport.
- In single-session wordlist view, compare-only controls and the secondary comparison card collapse away so that the primary session remains the only visible speaker context.
- Wordlist is rendered as a calm list with stable numbering on the left and the item label or text on the right.
- Numbering is fachlich fixed and must come from production data, not from UI-generated ordinals.
- Clicking a wordlist item may directly trigger playback; a separate play button per item is optional and not required.
- The target contract includes downloading single split MP3 files from the full player when those artifacts exist.
- Full-task playback remains based on the full MP3 and does not require split MP3 playback as the primary logic.
- Shared transport actions such as play or download use icon-only controls with accessible labels rather than verbose button text.
- Shared playback speed is currently limited to `0.5`, `0.75`, `1.0`, `1.25`, and `1.5`.
- The productive speed control uses a compact direct slider with the fixed steps `0.5`, `0.75`, `1.0`, `1.25`, and `1.5`, not a large dropdown or a wide chip row.
- Player-header metadata for the productive wordlist surface stays compact and listening-relevant; fields such as `recorded_by` do not belong to the player card surface.
- Productive player metadata cards are a player-specific derivation of the speaker-card family: they reuse the same accent or top-border logic, chip language, and facts-grid principle, while adapting width and internal geometry to the player workbench.
- If one wordlist item corresponds to exactly one timing-bearing unit, the data contract does not require duplicating identical text or timing values on a second token layer.
- In that case the player may derive the timing-bearing render unit internally from the item itself.

### `text`

- The technical task key remains `text` in all corpora.
- `text` may render either as `sentence_list` or as `running_text`.
- Each corpus defines one default render mode for `text` through player configuration.
- Each corpus defines the visible task label for `text` through player configuration.
- Even in `running_text`, a small visible sentence or segment numbering remains present.
- In `sentence_list`, each row uses a stable left-side number or ID and the sentence text on the right.
- Numbering comes from source data and must not be synthesized in the web UI.
- In both `sentence_list` and `running_text`, visible sentence or segment numbering must remain quiet and secondary.
- Both render modes stay within the same task key and the same shared audio and sync architecture.

### `interview`

- Interview uses a dedicated interview-appropriate renderer.
- Interview does not use comparison mode.
- The interview renderer must support speaker changes and segment-based navigation.
- Interview must not be forced into the interaction model of isolated wordlist items or quiet sentence-list rows.
- Focus handling for interview may use segment identifiers where item identifiers are not the primary structure.

## Comparison Mode

- Comparison is an extension of the same player base and not a second player product.
- Comparison is desktop-only.
- Only `wordlist` and `text` support comparison.
- `interview` never supports comparison.
- Comparison adds one optional secondary session to the primary player state.
- Primary item matching uses stable `item_id` values.

### Graceful degradation

- Older or imported datasets may lack some matching comparison items.
- Missing secondary items must not break the whole comparison view.
- The primary side remains usable even when the secondary side has gaps.
- Missing comparison items are shown as unavailable or empty-state elements instead of causing route or rendering failure.
- On smaller viewports, compare-specific selectors, compare cards, and the aligned dual-column list collapse back to the primary single-session view instead of keeping a cramped compare layout.

## Phenomena Presets

- Phenomena does not get a separate special-purpose player.
- Phenomena launches the same player route with optional preset context.
- Presets are configuration, not part of the audio files or the alignment JSON.
- Corpus-specific player configuration lives under `data/config/research_player/{language}/`.

### Required configuration files

- `player_config.json`
- `phenomena_presets.json`

### Task catalogs

- Corpus-specific task catalogs live under `data/config/research_player/{language}/task_catalogs/`.
- If a task catalog exists for a task, that catalog is the canonical content source for the task inside the player architecture and downstream derivation pipelines.
- A task catalog carries the canonical unit sequence, stable IDs, visible numbering, exact texts, and optional provenance references for the corpus-specific task content.
- A task catalog may additionally carry corpus-specific `display_label` and top-level `groups` metadata when grouped task structure is part of the canonical content model.
- Session-specific `alignment/{task}.json` files are derived from the task catalog plus session-specific alignment and audio data.
- Production pipelines must not reconstruct canonical task texts from TextGrid labels, PDF extraction, or loose TXT sources when a canonical task catalog already exists.
- TextGrid labels may be used only for validation, explicit warning, or controlled failure and must not silently override task-catalog content.
- Task catalogs may later support raw material views on project or information pages without implying automatic public audio access or release.
- The first concrete task catalogs prepared for this architecture are `data/config/research_player/spanish/task_catalogs/wordlist.json` and `data/config/research_player/spanish/task_catalogs/text.json`.

### `player_config.json`

- `player_config.json` must at least define the corpus default for the technical task `text`.
- The minimum required field is `text.default_render_mode` with the allowed values `sentence_list` and `running_text`.
- `player_config.json` must also define the visible label for the technical task `text` via `text.display_label`.
- `text.display_label` may be values such as `Text` or `Satzliste`, depending on corpus conventions.
- Changing `text.display_label` changes only visible naming and never the technical task key.

### `phenomena_presets.json`

Each preset must carry at least:

- `preset_id`
- `label`
- `description`
- `language`
- `items`

Each preset item reference must carry at least:

- `task`
- `item_id`

Optional preset item fields may include:

- `segment_id`
- `note`
- `sort_key`

### Preset rules

- A preset may contain mixed task selections, for example `wordlist` and `text` items in one curated set.
- Preset data is maintained separately from session audio and alignment artifacts so that corpora can extend or revise presets without regenerating the source alignment data.
- In preset context, the player filters the active view to the curated items of the current task.
- In preset context, the player must allow users to add further explicit items to the active curated selection.
- Manual additions extend only the active player state and never mutate the preset configuration files.

## Data and Artifact Contract

- The primary playback artifact is the full-task MP3 at `derived/{task}.mp3`.
- The primary structural artifact is the player or alignment JSON at `alignment/{task}.json`.
- Split MP3 artifacts live under `items/{task}/{item_id}.mp3`.
- The player must remain usable with full MP3 plus alignment JSON even when split MP3 coverage is incomplete.
- Single-item split-MP3 download is part of the target contract when the artifact exists.
- The current web implementation delivers full-task playback through the protected route `.../audio.mp3` and split downloads through `.../items/{item_id}.mp3`, while keeping internal runtime paths private.

### Common top-level contract

`alignment/{task}.json` must transport at least:

- `session_id`
- `person_id`
- `task`
- `audio.full_mp3`

The top level may additionally include:

- `items`
- `segments`
- `meta`
- further task-compatible metadata fields that do not redefine the task key or the timing semantics

### Task-specific minimum container structure

- `wordlist` must include `items`.
- `text` must include `items`.
- `interview` must include `segments`.
- The contract must not require both `items` and `segments` for every task when one of them is not semantically needed.
- The contract must not require empty placeholder arrays only for structural uniformity.

### Timing-bearing render units

- The player architecture always operates on timing-bearing render units.
- A timing-bearing render unit is the smallest element that carries the timing used for playback focus, highlighting, or synchronization.
- Depending on task and data quality, the timing-bearing render unit may be the container itself or a nested token.

### `wordlist` container contract

- In `wordlist`, the leading container level is `items`.
- Each item is one wordlist entry.
- Each wordlist item must transport at least:
	- `item_id`
	- `item_number`
	- `text`
	- `split_mp3`
- A wordlist item may itself be the timing-bearing render unit.
- If the item itself is timing-bearing, it must also transport `start_ms` and `end_ms`.
- Optional item fields may include:
	- `tokens`
	- `label`
- `tokens` are optional in `wordlist` and are only used when finer sub-item timing is actually available and semantically useful.
- If one wordlist item maps exactly to one timing-bearing unit, the contract does not require duplicating identical `text`, `start_ms`, and `end_ms` values again inside `tokens`.

### Current `wordlist` production rules

- The first concrete production path prepared for implementation is `wordlist`.
- The current prepared corpus-specific `wordlist` path is the canonical Spanish wordlist with exactly 92 visible items.
- `data/config/research_player/spanish/task_catalogs/wordlist.json` is the canonical content catalog for the current Spanish `wordlist` path.
- The prepared artifact set for this path is `derived/wordlist.mp3`, `items/wordlist/{item_id}.mp3`, and `alignment/wordlist.json`.
- For the current Spanish wordlist, `item_number`, `item_id`, and `text` come from the task catalog.
- For the current Spanish wordlist, `item_number` is the fachlich visible number and runs from `1` through `92`.
- For the current Spanish wordlist, `item_id` is the stable technical ID and is derived deterministically from `item_number` as `wl_{NNN}` with fixed prefix `wl_` and three-digit zero padding, for example `wl_001` through `wl_092`.
- For the current `wordlist` production path, the sequence of non-silence intervals in `alignment/wordlist.TextGrid` is mapped positionally onto the canonical task-catalog items.
- Leading, intermediate, and trailing silence intervals are not `wordlist` items.
- The number of non-silence intervals must be exactly `92`; otherwise the production run fails and must not continue silently with missing or additional items.
- The current task catalog records that `docs/model_mds/01_Spanisch_Wortliste.pdf` is the order and numbering reference and that `docs/model_mds/spanish_wordlist.txt` is the authoritative reference for exact text forms.
- `alignment/wordlist.TextGrid` supplies the item boundaries and the non-silence sequence, but it does not override the canonical task-catalog texts used in JSON or split references.
- Session-specific `alignment/wordlist.json` is derived from the canonical task catalog plus TextGrid boundaries and session audio artifacts.
- JSON `text` values and all text-derived wordlist references for the current Spanish path must copy the canonical task-catalog strings exactly.
- No orthographic normalization, Unicode simplification, accent removal, automatic case conversion, or silent rewriting of spaces or dash-like characters is allowed.
- Multi-form entries remain exactly as authored in the authoritative source, for example `número – numero – numeró`.
- The implementation run may validate TextGrid labels against the canonical task catalog, but any detected deviation must result in an explicit warning or a controlled failure and must not be auto-normalized.
- Time values read from `alignment/wordlist.TextGrid` are rounded to four decimal places before further derivation into JSON time values or split-export boundaries.
- These rounded values are the basis for both the canonical JSON time fields and the later split-export boundary calculation.
- The current implementation serializes these canonical JSON time fields as integer milliseconds after rounding the TextGrid seconds to four decimal places and converting once into ms.
- `start_ms` and `end_ms` in `alignment/wordlist.json` remain the canonical annotation boundaries.
- Split-export padding does not modify these canonical boundaries.
- If canonical `wordlist` boundaries exceed the available session audio duration, that session is not processable for the current production path and must fail or be skipped explicitly instead of producing truncated canonical JSON.
- Web derivatives for `wordlist` use MP3 in mono with `160 kbps` CBR.
- Loudness standardization is applied only to `derived/wordlist.mp3`.
- Wordlist split MP3s are cut from the already standardized `derived/wordlist.mp3`.
- Wordlist split MP3s are not normalized again per item after the standardized full MP3 has been produced.
- Wordlist split MP3s use `250 ms` padding before and after the canonical item boundaries.
- Split-export boundaries are clamped to the available audio duration.

### Current MVP scope

- The current productive web-player MVP uses the shared player surface for all tasks but only implements real playback, progress, timing sync, active-item highlighting, split-download delivery, in-player session switching, and comparison for `wordlist`.
- If a session documents `wordlist` but lacks processable player artifacts, the player route must stay reachable and render an explicit unavailable state instead of failing the whole page.
- The current MVP keeps `text` and `interview` inside the shared task switch but does not fake playback or pseudo-renderers for them.
- The current productive comparison path is `wordlist` only; `text` remains future-capable in the architecture but not yet implemented productively.
- The current productive `wordlist` compare flow uses one active transport focus at a time and must not default to simultaneous dual-audio playback; the productive surface no longer needs a dedicated primary-versus-compare focus switch or a second transport toolbar.
- The current productive `wordlist` compare flow keeps item checking and global transport separate: item clicks run bounded clip checks, while global play resumes the current full-audio context.
- The current productive `wordlist` compare flow enables `Beide abspielen` by default when a valid comparison session is loaded; `compare_mode=manual` remains the lightweight override for per-side item checks.
- The current productive `wordlist` session switcher lives in the metadata cards, not in the playback controls; the visible `session_id` headers open the available session choices.
- The current productive `wordlist` compare flow is explicitly activated from the primary card and does not leave an always-open empty comparison selector in the playback zone.
- The productive compare item toggle is handled as a lightweight client-side state change on the already loaded compare surface and must not require a full player rebuild just to switch between `Beide abspielen` and manual per-side playback.
- The current productive compare UI is desktop-only, while smaller viewports degrade to the primary single-session view without breaking the route.
- The current productive shared controls expose fixed playback-rate steps `0.5`, `0.75`, `1.0`, `1.25`, and `1.5` via a compact slider plus shared volume control for active playback.

### `text` container contract

- In `text`, the leading container level is `items`.
- Each item is one sentence or one other explicitly defined text unit.
- Each text item must transport at least:
	- `item_id`
	- `item_number`
	- `text`
- Corpus-specific `text` production uses `data/config/research_player/{language}/task_catalogs/text.json` as the canonical content catalog for text units, numbering, and exact texts.
- Future session-specific `alignment/text.json` files are derived from that text catalog plus session-specific alignment and audio data.
- Text items may transport their own broader timing via `start_ms` and `end_ms`.
- For running synchronization, `text` should use nested `tokens` where sufficiently good word-level alignment exists.
- Optional text-item fields may include:
	- `split_mp3`
	- `tokens`
	- `label`

### Current `text` catalog rules

- The current prepared corpus-specific `text` path is the canonical Spanish sentence list with exactly `50` visible items.
- `data/config/research_player/spanish/task_catalogs/text.json` is the canonical content catalog for that sentence list.
- The current Spanish `text` catalog may use the visible `display_label` `Satzliste` without changing the technical task key `text`.
- The current Spanish sentence-list catalog contains top-level `groups` and `items`.
- These `groups` are canonical content-grouping metadata and must not be modeled as interview-like `segments`.
- The current Spanish sentence-list groups are `D`, `QY`, and `QW`.
- Their neutral machine-readable `group_type` values are `declarative`, `yes_no_question`, and `wh_question`.
- Visible German or English group labels are UI or configuration concerns and must not replace the machine-readable catalog structure as the only truth.
- The intended PDF reference `docs/model_mds/02_Spanisch_Satzliste.pdf` is the order and block-structure reference for the catalog.
- The user-provided canonical sentence-list text is the authoritative source for the exact `text` strings of the catalog.
- When this catalog exists, production pipelines must not reconstruct canonical sentence texts from PDF extraction, Word extraction, TextGrid labels, or other loose helper sources.
- No orthographic normalization, Unicode simplification, accent removal, automatic case conversion, punctuation rewriting, quote substitution, or silent whitespace rewriting is allowed.
- For the current Spanish sentence list, visible `item_number` values remain `D1` through `D30`, `QY1` through `QY10`, and `QW1` through `QW10`.
- For the current Spanish sentence list, stable technical `item_id` values are `d_01` through `d_30`, `qy_01` through `qy_10`, and `qw_01` through `qw_10`.
- The current canonical `text` catalog intentionally contains only sentence-level items and group metadata.
- Tokens are not part of this canonical sentence-list catalog.
- Future session-specific `alignment/text.json` files may add nested `tokens` for finer-grained synchronization.
- `wordlist_item_ref` remains the optional cross-task reference on token level, not on the canonical sentence-list catalog as a whole.
- The primary future correspondence between sentence-list material and wordlist material lives on token-level alignment data, not in the top-level sentence-list catalog structure.
- The same canonical sentence-list catalog may later support raw material views in the webapp without implying public audio release, automatic corpus release, or a second competing text source.

### `interview` container contract

- In `interview`, the leading container level is `segments`.
- Each segment is one speaker turn or one other defined interview section.
- Each interview segment must transport at least:
	- `segment_id`
	- `segment_number`
	- `speaker_code`
	- `start_ms`
	- `end_ms`
- Optional interview-segment fields may include:
	- `item_id`
	- `tokens`
	- `label`
- Tokens are optional in `interview`.
- If tokens are absent, segment-based behavior remains valid.

### Token contract

- `tokens` are optional nested timing-bearing elements.
- Each token should transport at least:
	- `text`
	- `start_ms`
	- `end_ms`
- Optional token fields may include:
	- `token_id`
	- `label`
	- `wordlist_item_ref`
- `wordlist_item_ref` is an optional reference field on `text` tokens.
- When present, `wordlist_item_ref` points to a canonical wordlist `item_id`.
- Not every token needs a `wordlist_item_ref`.

### Data rules

- Stable numbering, stable `item_id` values, and stable `segment_id` values are production data and must be transported unchanged into the player layer.
- The web UI must not invent replacement numbering when the source data is incomplete; such gaps are upstream data or pipeline issues.
- Production scripts must be able to derive player JSON and split artifacts from canonical task catalogs plus session alignment and audio data without redefining the web-level semantics of item numbering, IDs, or exact texts.
- `text` numbering and visible text-unit numbering come from production data and must not be synthesized freely in the web UI.
- The contract prefers semantically clean source structures over redundant duplication for superficial uniformity.

## Sync and Rendering Architecture

- PROMAT uses one reusable player architecture for audio control, sync logic, rendering, and highlighting.
- Rendered units should be word-near or token-near where alignment granularity makes that useful.
- Timing data belongs directly to renderable units.
- Active running highlight must use a `requestAnimationFrame` loop and not rely only on coarse `timeupdate` events.

### Required module boundaries

- audio control
- state and data loading
- sync logic
- task rendering
- highlighting and annotation

### Rendering rules

- Task renderers may differ, but the audio-control and sync modules stay shared.
- Highlighting classes or attributes are applied on timing-bearing outer nodes.
- Manual letter or sub-token marking is an additive inner layer and must not destroy the outer timing and sync structure.
- Task-specific renderers must plug into the same timing and highlighting model instead of rebuilding their own audio or sync stacks.
- The player may normalize different source granularities into one internal render and sync structure.
- A `wordlist` item without `tokens` may be normalized into one timing-bearing render unit.
- A `text` item with `tokens` may normalize those tokens into the timing-bearing render units while preserving the parent sentence or text item for numbering and grouping.
- An `interview` segment without `tokens` may normalize directly into a segment-level timing-bearing render unit.
- This normalization is an internal player concern and must not force production data to store redundant duplicate timing layers.

## Modularity Rules and Non-goals

- Base player components are built once and reused.
- Task-specific behavior is described through configuration or clearly bounded renderer modules.
- Corpus-specific behavior is described through configuration, not through cloned player products.
- There is no separate wordlist player.
- There is no separate text or sentence-list player.
- There is no separate interview player.
- There is no separate phenomena player.
- There is no separate comparison player.
- Interview comparison is out of scope for the target architecture.