# PROMAT Spec: Research Player

## Status

This file is the binding source of truth for the active architecture of the research player in the PROMAT webapp.

## Scope and Relation

- This spec defines the active unified research-player architecture.
- `docs/spec/platform-data-files.md` remains binding for routing, runtime boundaries, and filesystem semantics.
- `docs/spec/research-access.md` remains binding for research IA and access logic around speakers, recordings, profiles, comparison, and phenomena.
- `docs/spec/research-capabilities.md` remains binding for task subsets, compare capability, set-filter capability, render-mode vocabulary, and corpus-specific surface readiness.
- `docs/model_mds/speech_text_sync.md` is a technical reference only and is not normative for PROMAT.

## Core Architecture

- PROMAT has exactly one modular research player for the whole webapp.
- There are no separate player products for `wordlist`, sentence-list `text`, connected-text `text`, and set excerpts.
- Task differences are implemented through normalized source metadata, render modes, and optional context extensions, not through parallel player implementations.
- The player includes a bounded direct-compare extension with at most one optional secondary session.
- The standalone `comparison` page is separate from the player surface but reuses shared loader, item, and media logic where practical.
- `phenomena` is a separate curated launcher and selection page; when it opens the player, it does so through the same player route family with additional preset or set context.
- Shared player logic must be changeable once in the base architecture and must not require parallel task-specific rewrites.
- Player helpers must derive task subsets, compare eligibility, render-mode vocabulary, and set-aware view degradation from the canonical capability layer instead of local duplicate literals.
- The canonical player runtime seam is `app/src/app/research_player_runtime.py`; it resolves source, set context, media availability, normalized items, and bounded compare state before page composition.
- `app/src/app/research_views.py` remains the player-facing page builder, but it must compose navigation, summary cards, task bars, and template payloads from the normalized runtime state instead of re-owning the same resolution logic.

### Internal runtime seams

- Source resolution, set-context resolution, media loading, item normalization, and compare-state resolution are separate bounded responsibilities inside the player runtime layer.
- View composition stays separate from runtime resolution: page builders may assemble metadata cards, controls, and route-aware links, but they must not become a second source of truth for source or item semantics.
- Compare remains a bounded extension of the same runtime state and must not fork a second player loading pipeline.
- Interview uses its dedicated segment-oriented renderer inside the same unified player shell and runtime seam; it does not create a second player product, a task-specific route family, or a second upper player zone.

## Source and Item Normalization

- Each productive player surface resolves the current request into one normalized player source plus one ordered item sequence before template rendering begins.
- The normalized source is explicit and data-driven. It must not be guessed from visible text length, item count, or loose ordering heuristics.
- For catalog-backed task sources, the canonical source metadata lives in `task_catalogs/{task}.json` under `player_source`.
- `player_source` must define at least `source_kind`, `content_mode`, `default_view`, `allowed_views`, `primary_audio_mode`, `supports_item_audio`, `supports_full_audio`, `supports_text_view`, and `paragraph_model`.
- The active source kinds are `wordlist`, `sentence_list`, `text`, and `set`.
- `set` is a runtime source kind produced by owner-bound set context. It is not a separate route task key.
- Every rendered item is normalized to one shared item structure carrying stable `item_id`, source-backed numbering, visible text, and optional text metadata such as `text_container_id`, `text_order_index`, `paragraph_break_before`, or `paragraph_id`.
- Sets filter the visible sequence but do not redefine item IDs or rebuild a second item system.

## Route and Entry Contract

- The canonical player route is `/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}`.
- `task` uses only the canonical research task keys `wordlist`, `text`, and `interview`.
- The route path identifies the primary session and the initial task.
- The player is a research detail route, not a second section root and not an additional sidebar page.
- The same route family must be callable from `speakers`, `recordings`, `profile`, and later from `comparison` and `phenomena`.

### Optional query context

- `source`: identifies the entry source and may use `speakers`, `recordings`, `profile`, `comparison`, or `phenomena`.
- `preset_id`: identifies an optional phenomena preset context.
- `set_id`: identifies an optional user-owned draft or saved set context.
- `compare_session`: identifies an optional secondary comparison session.
- `compare_mode`: identifies an optional compare-item override and currently uses `manual`; omitted compare mode keeps the default compare item-check behavior `Beide abspielen`.
- `focus_item`: identifies an optional focused item.
- `focus_segment`: identifies an optional focused segment.
- `render_mode`: may override the corpus default render mode for the technical task `text`.

### Route rules

- Optional query context may refine the player state, but it must not create separate route families or separate player implementations.
- Invalid optional query context must degrade to the nearest valid base state instead of breaking the whole page.
- Source context is navigational context only and must not alter the base architecture of the player.
- If `set_id` and `preset_id` are both present, `set_id` wins for the active working selection and `preset_id` remains provenance or bootstrap context only.
- The player route stays task-specific even when the referenced set contains mixed `wordlist` and `text` items; no `mixed` task value is allowed.
- When the HTML player route is rendered without owner-bound access to the requested `set_id`, the page degrades to the nearest session-and-task base state and may show only a generic set-context notice; it must not leak owner-bound set contents, labels, or existence details.
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
- `set_id` as optional user-owned working-set context
- `compare_session_id` as optional comparison context
- `focused_item_id` as optional item focus
- `focused_segment_id` as optional segment focus

### State rules

- One primary session is always required.
- Speaker identity is derived from the primary session and is not a separate player root.
- The current productive compare extension also needs one optional comparison-playback value for the primary plus optional secondary state; omitted value keeps `Beide abspielen` as the default item-check behavior and `manual` switches item clicks back to per-side playback.
- A focused item or segment may narrow the visible context, but it does not replace the primary session or task state.
- Comparison context is optional and only valid for compatible tasks.
- Set context is optional and carries the active user-owned selection when the player is opened from `phenomena` or `comparison`.
- Preset context is optional curated provenance or bootstrap context.
- Manual additions or removals belong to the active set state and never mutate the preset configuration files.
- In the productive player, a valid `set_id` filters the visible item list and any bounded direct-compare rows to the current task-specific excerpt of that set.
- If the current task has no items in the active set excerpt, the player renders an explicit empty or unavailable state for that task and must not silently fall back to the full session list.
- When a valid `set_id` is active for technical task `text`, the normalized source kind becomes `set`, the allowed view collapses to list-only `sentence_list`, and the player must not reconstruct a running-text surface from the excerpt.

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

- The metadata card reuses the existing visual semantics of speaker cards where appropriate, especially for speaker type and level or variety cues, but the productive player keeps the card container itself neutral.
- The player must not introduce a second competing color or badge taxonomy.
- Productive player metadata cards do not use level-, role-, or native-coded top borders or other card-chrome accents; semantic color stays on explicit badges and pills inside the card.
- Productive player metadata cards keep the same neutral-container plus badge-driven coding logic as the current `speakers` learner cards and the comparison speaker rows.
- In the productive `wordlist` player, session selection belongs to the metadata-card identity layer, not to the playback toolbar: the visible `session_id` acts as the session switcher in the card header.
- The player may expose one compact page-level back action outside the playback control bar, but it must remain one route-context action and not expand into a second competing player header system.
- The top-right metadata-card action zone keeps only the compact role badge such as `Primär` or `Vergleich`; profile access belongs to the card footer and not to a second header action row.
- Badge and pill content on player metadata cards, comparison speaker rows, and speaker-card meta badges stays on the regular UI font family rather than the book or reading font.
- Each visible metadata card exposes its own profile action in the footer so that primary and comparison sessions can both open their corresponding speaker profile directly from the player surface.
- Native-speaker metadata cards do not add a second speaker-group badge when the surrounding player card context already identifies the session role; instead they show one canonical localized native-reference badge derived from standard variety and origin country.
- In single-session mode, the primary footer may expose one compact compare-entry action plus the profile action; once compare is active, the primary footer keeps only the profile action and the comparison footer owns the `Vergleich entfernen` action.
- The productive player does not expose a separate `Vergleich ändern` button; changing the comparison session happens through the comparison card's session switcher.

## Task Switching

- Loading one task for a session opens the unified player base for that session.
- The player exposes all documented session-available tasks as one shared task switch.
- Switching tasks stays inside the same player architecture and does not jump into separate task-specific player implementations.
- The task switch retains the primary session, metadata card, and route family.
- On productive item tasks, the task switch sits in one compact material bar directly below the metadata cards.
- The player route and its protected media-delivery routes are authenticated research-detail surfaces; unauthenticated access is clarified before the player or media response is rendered.
- Set context, preset provenance, or focus context should be retained across task switches where they remain valid.
- Task switching with an active `set_id` retains the same owner-bound set reference and recalculates the task-specific excerpt for the new task instead of dropping back to full-session content.
- The same material bar places the `Set wählen` control on the right; its default visible value is `Alle Items`, and a selected set filters the visible task-specific sequence without redefining the task switch itself.
- The visible player set select offers the same fachlich visible source families as the shared research-set model: curated presets, saved custom sets, and the already active draft as a contextual option when the player was opened with that exact `set_id`.
- Unrelated drafts stay hidden, and visible labels in that selector use curated or saved set titles rather than raw technical IDs.
- Source-driven view switching remains separate from task and set controls. If a source supports both list and connected-text rendering, the view switch appears as a compact local control in the content-panel header on the right, opposite the content title and item count, and it must not introduce a second standalone control box between the material bar and playback.
- Tasks that are not available for the current session may remain visible as disabled, non-interactive controls.
- `wordlist`, `text`, and `interview` are productive task modes when the session has valid alignment and audio artifacts for the respective task.
- `interview` stays inside the same task switch and same upper player frame as the other productive tasks; only the content renderer below the control zone changes to the segment-oriented transcript surface.

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
- The visible linguistic item content in productive wordlist rows uses the shared book-style content typography, while numbering, timings, counts, toggles, and other UI or meta layers stay on the regular UI typography.
- Clicking a wordlist item may directly trigger playback; a separate play button per item is optional and not required.
- A valid `focus_item` may highlight and reveal the initial visible wordlist entry, but it must not autoplay and it must degrade cleanly when the focused item is outside the current task-specific excerpt.
- The target contract includes downloading single split MP3 files from the full player when those artifacts exist.
- Full-task playback remains based on the full MP3 and does not require split MP3 playback as the primary logic.
- Shared transport actions such as play or download use icon-only controls with accessible labels rather than verbose button text.
- Shared playback speed is currently limited to `0.5`, `0.75`, `1.0`, `1.25`, and `1.5`.
- The productive speed control uses a compact direct slider with the fixed steps `0.5`, `0.75`, `1.0`, `1.25`, and `1.5`, not a large dropdown or a wide chip row.
- Player-header metadata for the productive wordlist surface stays compact and listening-relevant; fields such as `recorded_by` do not belong to the player card surface.
- Productive player metadata cards are a player-specific derivation of the speaker-card family: they reuse the same badge language and compact facts-grid principle, while adapting width and internal geometry to the player workbench; unlike native overview speaker cards, they keep the card shell neutral and move level, speaker-group, variety, `L1`, and role semantics onto badges inside the card.
- If one wordlist item corresponds to exactly one timing-bearing unit, the data contract does not require duplicating identical text or timing values on a second token layer.
- In that case the player may derive the timing-bearing render unit internally from the item itself.

### `text`

- The technical task key remains `text` in all corpora.
- `text` may render either as `sentence_list` or as `running_text`.
- The active render behavior for `text` is driven by the task catalog `player_source`, not by UI heuristics.
- Sentence-list sources keep `allowed_views = ['list']` and therefore render only as `sentence_list`.
- Connected-text sources use `source_kind = 'text'`, `content_mode = 'connected_text'`, and `supports_text_view = true`; they may expose both `running_text` and `sentence_list` on the same item basis.
- Visible task labeling for `text` still comes from the canonical task catalog and stays independent from the technical task key.
- Even in `running_text`, a small visible sentence or segment numbering remains present.
- In productive connected-text `running_text`, the text view is a calm reading mode rather than a second workbench: numbering stays visibly secondary, the active item highlight stays subtle, and per-item download actions remain visually quiet until hover, focus, or the active segment state reveals them.
- In `sentence_list`, each row uses a stable left-side number or ID and the sentence text on the right.
- Numbering comes from source data and must not be synthesized in the web UI.
- In both `sentence_list` and `running_text`, visible sentence or segment numbering must remain quiet and secondary.
- In both `sentence_list` and `running_text`, the visible linguistic item content uses the shared book-style content typography, while timings, badges, switches, counts, and other UI or meta layers remain in the regular UI typography.
- Both render modes stay within the same task key and the same shared audio and sync architecture.
- The productive `text` sentence-list renderer uses the canonical task catalog plus session-specific `alignment/text.json` artifacts for stable numbering, texts, item IDs, and clip boundaries.
- In productive `text` sentence-list rows, the visible display numbering appears only once in the dedicated left number badge; technical item IDs such as `d_02` and auxiliary grouping markers such as `D` are runtime or catalog helpers and must not be repeated as visible row metadata beneath the sentence text.
- In productive `text` sentence-list rows, the timing label remains part of the row meta but is right-aligned inside the item field, analogous to the `wordlist` timing placement.
- In productive `text` sentence-list rows, the left number badge, sentence container, timing label, and per-item download action use one optically balanced top-aligned row logic; the taller book-typography sentence text must not leave the badge or meta actions looking undersized, too high, or vertically detached.
- In productive `text` sentence-list rows, the timing label and any per-item icon actions align to the first text line rather than centering against the full row block.
- In productive `text` sentence-list playback, the active sentence highlight is resolved strictly from stable `item_id` timing matches; if playback sits briefly in a gap between two timed sentence items, the previous valid sentence item remains active until the next valid item match is reached, and the UI must never fall back to the global last sentence item.
- For connected-text sources, `running_text` is the default only when the source metadata explicitly permits it; otherwise the player must degrade to `sentence_list`.
- Running-text sources currently fall back to `sentence_list` while direct comparison is active, so sentence matching and compare rows stay on the stable item list contract.
- In productive connected-text `running_text`, hidden per-item download controls must not reserve permanent layout width; the reading flow stays continuous until hover, focus, or active-state reveal.
- A valid `set_id` filters the visible sentence-list rows task-specifically, and an empty `text` excerpt renders an explicit empty state instead of falling back to the full session list.
- A valid `focus_item` may highlight and reveal the initial visible `text` row, but it must not autoplay and it must degrade cleanly when the focused item is outside the current `text` excerpt.
- The current productive `text` surface may use item-level clip actions where session artifacts provide reliable split clips.
- If session-specific `alignment/text.json` items also carry valid nested token timings, the same unified player may render additive token spans inside the existing text item markup and synchronize one active token inside the already active item while full-audio playback is running.
- Token-level highlighting is optional, item-local, and data-driven. Missing, invalid, or out-of-bounds token timings degrade cleanly to the existing sentence-only rendering without changing the surrounding player layout, typography, numbering, compare contract, or task architecture.
- Outer item or sentence highlighting remains the primary visible sync contract for `text`; token highlighting is an additive inner layer and must not replace the stable item-level active state.

### `interview`

- Interview uses a dedicated interview-appropriate renderer.
- Interview does not use comparison mode.
- Interview does not introduce set-filter logic and does not expose the `Set wählen` control.
- The interview renderer works from the productive imported runtime artifacts `alignment/interview.json` plus `derived/interview.mp3`.
- The interview renderer must support speaker changes and segment-based navigation.
- Interview must not be forced into the interaction model of isolated wordlist items or quiet sentence-list rows.
- Focus handling for interview uses `focus_segment` where segment identifiers are the primary structure.
- Material references embedded in interview segments open a small contextual reference overlay inside the shared player page, with an `Im Kontext öffnen` or `Open in context` link back into the relevant productive player task and an optional mini-player for the referenced split clip when such a clip exists.

## Direct Comparison in Player

- Direct comparison inside the player is a bounded extension of the same player base and not a second player product.
- The standalone `comparison` research page remains separate from this bounded player mode.
- Direct comparison in the player is desktop-only.
- Only `wordlist` and `text` support direct comparison in the player.
- `interview` never supports direct comparison in the player.
- Direct comparison adds one optional secondary session to the primary player state.
- Primary item matching uses stable `item_id` values.
- The active player keeps productive direct comparison enabled for both `wordlist` and `text`, while compare rendering stays on the stable sentence-list or item-list contract even when the underlying `text` source also supports `running_text`.

### Graceful degradation

- Older or imported datasets may lack some matching comparison items.
- Missing secondary items must not break the whole comparison view.
- The primary side remains usable even when the secondary side has gaps.
- Missing comparison items are shown as unavailable or empty-state elements instead of causing route or rendering failure.
- In productive `text` compare, matching stays on stable `item_id` values from the canonical sentence-list task catalog and never falls back to loose text matching.
- In productive `text` compare, a valid `set_id` filters both sides to the same task-specific sentence-list excerpt; the player must not silently widen back to the full session when that excerpt is empty or partial.
- In productive `text` compare, sentence-level item playback may still use full-audio timing boundaries when those are available, but missing split downloads stay visibly absent and do not become a second promised artifact contract.
- On smaller viewports, compare-specific selectors, compare cards, and the aligned dual-column list collapse back to the primary single-session view instead of keeping a cramped compare layout.

## Phenomena Presets and Set Context

- `phenomena` is a separate research page and not a special-purpose player surface.
- `phenomena` may launch either the canonical player route or the standalone `comparison` workbench.
- Presets are configuration, not part of the audio files or the alignment JSON.
- Corpus-specific player configuration lives under `data/config/research_player/{language}/`.

### Required configuration files

- `player_config.json`
- `phenomena_presets.json`

### Task catalogs

- Corpus-specific task catalogs live under `data/config/research_player/{language}/task_catalogs/`.
- If a task catalog exists for a task, that catalog is the canonical content source for the task inside the player architecture and downstream derivation pipelines.
- A task catalog carries the canonical unit sequence, stable IDs, visible numbering, exact texts, and optional provenance references for the corpus-specific task content.
- A task catalog also carries the active player-source contract under `player_source`.
- A task catalog may additionally carry corpus-specific `display_label` and top-level `groups` metadata when grouped task structure is part of the canonical content model.
- Connected-text catalogs may additionally carry item-level `text_container_id`, `text_order_index`, `paragraph_break_before`, and `paragraph_id` fields for running-text rendering.
- If connected-text source material begins with a separate title line that is not part of the spoken item sequence, that title remains source metadata and must not be auto-promoted to the first catalog item.
- Session-specific `alignment/{task}.json` files are derived from the task catalog plus session-specific alignment and audio data.
- Production pipelines must not reconstruct canonical task texts from TextGrid labels, PDF extraction, or loose TXT sources when a canonical task catalog already exists.
- TextGrid labels may be used only for validation, explicit warning, or controlled failure and must not silently override task-catalog content.
- Task catalogs may later support raw material views on project or information pages without implying automatic public audio access or release.
- The first concrete task catalogs prepared for this architecture are `data/config/research_player/spanish/task_catalogs/wordlist.json` and `data/config/research_player/spanish/task_catalogs/text.json`.

### `player_config.json`

- `player_config.json` remains a compatibility file for corpus-wide player defaults and legacy tooling.
- The active player no longer infers real text capability from `player_config.json`; true text behavior comes from the explicit `player_source` metadata in the task catalog.
- `text.display_label` and `text.default_render_mode` may remain present for compatibility, but they must not override a task catalog that explicitly declares sentence-list or connected-text behavior.

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
- Opening a preset for active user work must resolve into one server-side set context instead of a browser-only working state.
- In player context, the player filters the referenced set to the curated or edited items of the current task.
- Manual additions or removals mutate the active set state and never mutate the preset configuration files.

### Set-context rules

- Active user work across `phenomena`, `comparison`, and `player` uses one server-side set model in PostgreSQL.
- The canonical working reference for user-owned selection state is `set_id`.
- Draft and saved sets are lifecycle states of the same technical model rather than separate storage mechanisms.
- The canonical set core stores owner-bound lifecycle, label or note, preset provenance, and explicit item references; it is the only truth for durable set content.
- Workbench-specific state lives in a dedicated owner-bound `workbench_state` attached to the same `set_id`; it currently carries persisted comparison task filters and comparison session selections without redefining the set core.
- The active set JSON contract exposes that workbench-specific state only under `workbench_state`; parallel top-level alias fields for those values are not part of the productive API anymore.
- `phenomena` and `comparison` each expose exactly one visible owner-side persistence action `Als neues Set speichern`; it reuses the canonical set `save-as` flow, creates a new saved copy, and switches the active workbench context to that new `set_id`.
- `phenomena` may expose presets and launcher structure before login, but draft materialization, owner-bound `set_id` loading, and set mutation always go through authenticated set API access.
- The first productive set model stores explicit item references as `task + item_id` plus optional `segment_id` and is limited to the curated tasks `wordlist` and `text`.
- Comparison session selections and the persisted `comparison_view_task` filter stay server-side and owner-bound, but they are not part of the set core aggregate itself.
- Drafts refresh `last_accessed_at` and `expires_at` server-side, while saved sets keep `expires_at = null`.
- Server-side set reads and writes are owner-scoped through the authenticated user and never trust client-supplied ownership fields.
- In the normal loaded player success state, the surface does not keep a permanent generic set-context container; only targeted exceptional notices such as inaccessible set degradation, storage unavailability, or focus-missed degradation may remain visible.

## Data and Artifact Contract

- The primary playback artifact is the full-task MP3 at `derived/{task}.mp3`.
- The primary structural artifact is the player or alignment JSON at `alignment/{task}.json`.
- Split MP3 artifacts live under `items/{task}/{item_id}.mp3`.
- The player must remain usable with full MP3 plus alignment JSON even when split MP3 coverage is incomplete.
- Single-item split-MP3 download is part of the target contract when the artifact exists.
- The current web implementation delivers full-task playback through the protected route `.../audio.mp3` and split downloads through `.../items/{item_id}.mp3`, while keeping internal runtime paths private.
- Inline playback and download remain distinct intents on that item route family: default item URLs stay browser-playable, while explicit download actions use the same route with download intent so the browser receives an attachment response instead of inline navigation.

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

- The current productive web-player MVP uses the shared player surface for all tasks but currently implements real playback, progress, timing sync, active-item highlighting, split-download delivery, and in-player session switching productively for `wordlist` and `text`, with bounded direct compare on both tasks.
- The current productive player now evaluates `set_id` server-side for owner-bound access and applies task-specific filtering of the visible wordlist excerpt and any bounded direct-compare rows.
- The current productive player now evaluates `focus_item` for visible `wordlist` entries as an initial reveal and highlight only, without autoplay.
- The current productive player now also renders `text` in one real sentence-list mode when `alignment/text.json` plus playable task audio are available.
- If a session documents `wordlist` but lacks processable player artifacts, the player route must stay reachable and render an explicit unavailable state instead of failing the whole page.
- The current MVP keeps `interview` inside the shared task switch as an honest unavailable state.
- The current productive direct-compare path inside the player now covers `wordlist` and bounded `text` sentence-list comparisons through the same player base.
- The current productive `text` renderer stays deliberately conservative: it supports task-level audio, sentence-level item playback, bounded direct compare, set-aware filtering, and focus reveal, but it does not claim token-level sync or a productive `running_text` compare renderer.
- The standalone `comparison` page now productively uses mixed `wordlist` and `text` set contents, owner-bound session selections, persisted `all | wordlist | text` filtering, and reduced split-clip listening when matching artifacts exist.
- This standalone `comparison` workbench does not redefine the player architecture: it launches the canonical player route with optional `set_id` and `focus_item` context instead of becoming a second player implementation.
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

### Current working-tree `text` MFA import rules

- The current prepared `text` import step reads one batch-local manifest item sequence plus one MFA `words` tier TextGrid per utterance from `working/{person_id}/text/mfa_output/`.
- Manifest items remain the leading `items` container and define the canonical sentence boundaries for `start_ms` and `end_ms`.
- MFA-derived word intervals are imported as nested `tokens` on the corresponding item and do not redefine the sentence-level item structure.
- MFA token times are converted from utterance-relative time to source-audio-global time by adding the manifest `source_start_seconds` offset before the canonical ms conversion.
- Silence, empty intervals, and technical non-words from the MFA output must not become visible `tokens`.
- The current working import aligns canonical target words; dysfluencies, self-repairs, and OOV findings may remain MFA quality warnings without becoming a second mandatory token model in this step.
- Batch-local working import may serialize `session_id = null` until later metadata integration resolves the final session identity; this is a temporary working-tree state only and not the final production metadata contract.
- Batch-local working import may already serialize `audio.full_mp3 = derived/text.mp3` as the expected future relative full-audio artifact path even though this step does not generate the MP3 itself.

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