# PROMAT Spec: Research Capabilities

## Status

This file is the binding source of truth for the active research capability model in the PROMAT webapp.

## Scope and Canonical Runtime Contract

- This spec defines the canonical capability contract for research pages, tasks, player render modes, workbench subsets, and corpus-specific surface differences.
- The canonical implementation mirror of this contract lives in `app/src/app/research_capabilities.py`.
- Research routing, access checks, task availability, set filtering, comparison behavior, phenomena task subsets, and player render-mode resolution must derive from that capability layer instead of maintaining parallel literals in multiple modules.
- `docs/spec/platform-data-files.md` remains binding for route families and runtime boundaries.
- `docs/spec/research-access.md` remains binding for access semantics and research IA.
- `docs/spec/research-player.md` remains binding for the unified player contract.

## Canonical Research Pages

- The corpus root `/{ui_lang}/research/{corpus}` is a public orientation surface and not part of the fixed page-slug set below; page capability rules continue to apply only to the canonical corpus-scoped page slugs and detail routes.

### Active page slugs

- `design`
- `speakers`
- `comparison`
- `phenomena`

### Page metadata rules

- `design` is the only public corpus-scoped research page and uses page kind `reading`.
- `speakers`, `comparison`, and `phenomena` use page kind `workbench` and are protected research-app surfaces.
- Detail routes such as `player`, `speaker profile`, `phenomena` preset editor, `phenomena` set editor, and protected player-media delivery are always authenticated research-detail surfaces.
- Page order for corpus-scoped research navigation is fixed as `design`, `speakers`, `comparison`, `phenomena`.

## Canonical Research Tasks

### Active task keys

- `wordlist`
- `text`
- `interview`

### Task key rules

- Technical task keys stay stable English machine values.
- Visible corpus-specific labels do not create new task keys or second task families.
- `interview` remains an explicit limited special case inside the shared capability layer: it is productive inside the unified player shell, does not support compare, does not support set filtering, and does not create a second player architecture, task-specific route family, or separate upper player zone.

### Canonical task labels

- Default short labels are `Wortliste`/`Wordlist`, `Text`/`Text`, and `Interview`/`Interview`.
- Material labels may differ from the short labels where the workbench should read as material choice rather than generic task naming.
- For the technical task key `text`, a corpus-specific visible material label such as `Satzliste` changes only the display text.
- Corpus task-catalog `display_label` may override the material label only for the German UI of catalog-backed material workbench surfaces. English-visible labels fall back to the canonical bilingual capability labels unless a later active spec says otherwise.

## Workbench Capability Matrix

### `wordlist`

- visible in the shared player task switch
- productive in the current unified player
- supports bounded direct player compare
- supports owner-bound set filtering
- visible in `comparison`
- visible in `phenomena`
- does not support running-text view
- available for learner and native-speaker sessions

### `text`

- visible in the shared player task switch
- productive in the current unified player
- supports bounded direct player compare
- supports owner-bound set filtering
- visible in `comparison`
- visible in `phenomena`
- may support both `sentence_list` and `running_text` depending on source metadata
- available for learner and native-speaker sessions

### `interview`

- visible in the shared player task switch
- productive in the current unified player through the existing shared player shell
- not compare-capable
- not set-filter-capable
- not part of the current `comparison` or `phenomena` workbench subsets
- not available for native-speaker sessions
- uses the productive runtime artifacts `alignment/interview.json` plus `derived/interview.mp3`
- uses a segment-oriented renderer inside the shared player content area below the existing player-control zone

## Canonical Workbench Subsets

- Player-visible tasks: `wordlist`, `text`, `interview`
- Player-productive tasks: `wordlist`, `text`, `interview`
- Player-compare tasks: `wordlist`, `text`
- Set-filter-capable tasks: `wordlist`, `text`
- `phenomena` task subset: `wordlist`, `text`
- `comparison` view-task subset: `all`, `wordlist`, `text`
- The default visible comparison task is the first compare-capable task in the canonical capability order and is currently `wordlist`.

## Player Render and View Rules

- `wordlist` and `interview` do not expose alternate text render modes.
- `text` render capability is determined from source metadata plus the central capability layer, not from UI heuristics.
- When a `text` source supports both list and connected-text rendering, the canonical render modes are `sentence_list` and `running_text`.
- If direct compare is active for `text`, the allowed render modes collapse to `sentence_list`.
- If a valid set excerpt is active for `text`, the allowed render modes collapse to `sentence_list`.
- A source may only expose `running_text` when its source metadata explicitly allows the text view.

## Corpus-Specific Surface Modes

- All active corpora share the same page slugs and the same access model.
- Surface-mode differences describe whether a protected page currently renders productive content or a protected placeholder; they must not weaken auth behavior.
- `design` is content-bearing for all corpora.
- For the active Spanish protected workbench pages, `speakers` and `comparison` stay on their productive final surfaces even when canonical runtime session data is currently empty.
- In that empty-runtime case, `speakers` must render its normal final page with a plain empty state instead of protected planning copy or dummy cards.
- In that empty-runtime case, `comparison` must render its normal final workbench with plain empty result areas instead of protected planning copy or dummy rows.
- `phenomena` is productive for a corpus when the canonical task catalogs and `phenomena_presets.json` load successfully through the shared research-player config layer.
- A canonical `phenomena_presets.json` may contain an empty `presets` list for corpora that currently have no curated preset items yet; that is a valid config state and should yield an empty productive overview rather than a config failure.
- When a corpus has no runtime sessions, `phenomena` overview entries must collapse to a plain empty state rather than showing planning placeholders or set lists detached from runtime availability.
- Protected planning placeholders for `speakers`, `comparison`, and `phenomena` are retired; headings such as `Geplante Übersicht`, `Geplante Filter`, `Struktureller Stand`, or `Geplante Oberfläche` are not part of the active protected research contract.
- Corpus-specific productive readiness must be expressed through the capability layer, not through corpus-specific access exceptions or ad hoc router branches.

## Non-Negotiable Consistency Rules

- There must be no second competing truth source for research page order, task subsets, compare capability, set-filter capability, render-mode vocabulary, or page access semantics.
- Access logic may wrap the capability layer for compatibility, but it must not redefine the rules elsewhere.
- Session, preset, set, comparison, phenomena, public-content, and player helpers must consume the same capability-owned task and page vocabulary.
- Future research work surfaces must extend the capability layer first before adding new route or workbench-specific literals.