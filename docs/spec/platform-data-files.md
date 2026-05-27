# PROMAT Spec: Platform, Data, and Files

## Status

This file is the binding source of truth for PROMAT platform structure, routing, runtime boundaries, IDs, filesystem semantics, and active controlled vocabularies.

Research task and page capability semantics are defined in `docs/spec/research-capabilities.md`.

## Platform Structure

- `app/` is the only versioned application source root.
- `data/` is the protected research-data space.
- `public/` is the explicitly released public-media space.
- `content/` is the versioned editorial content space for fully public file-based surfaces such as Teaching.
- `secure/` is the clear-text space and is never accessed by the webapp.
- `scripts/` contains repeatable import, export, setup, and pipeline steps.
- `scripts/research_data_intake/` is the canonical root for research-data intake and derivation pipelines.
- General dev and maintenance scripts remain at the top level under `scripts/` and do not move into `scripts/research_data_intake/` unless they become part of the research-data intake pipeline.

## Routing

### Public route schema

```text
/{ui_lang}/{section}/{corpus_language}/{page}
```

### Public teaching route schema

```text
/{ui_lang}/teaching
/{ui_lang}/teaching/{teaching_language}
/{ui_lang}/teaching/{teaching_language}/{topic_slug}
```

### Public teaching asset route schema

```text
/teaching-media/{teaching_language}/{topic_slug}/{media_type}/{filename}
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
- `section`: `project`, `research`, `teaching`
- `corpus_language`: `spanish`, `french`, `german`, `english`
- `teaching_language`: `spanish`, `french`, `german`, `english`

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
- `comparison`
- `phenomena`

### Active research detail routes

- `player`
- `phenomena` preset editor
- `phenomena` owner-set editor
- `player`-scoped protected media delivery for current-session playback and single-item download

### Active teaching surfaces

- section root `/{ui_lang}/teaching`
- edition hub `/{ui_lang}/teaching/{teaching_language}`
- topic page `/{ui_lang}/teaching/{teaching_language}/{topic_slug}`

### Routing rules

- Technical slugs and route segments stay English.
- UI language and technical routing language must not be mixed.
- The public login surface stays on `/login`, while mutating auth actions stay under `/auth/*`.
- For routes without a `/{ui_lang}` path prefix such as `/`, `/login`, and `/access-request`, UI language resolution follows one shared priority order: explicit `lang` or `ui_lang` URL value first, then a stored user preference, then local route-context hints such as `next` or same-app referrer language, then `Accept-Language` with `de*` mapping to `de` and all other values falling back to `en`.
- PROMAT login is email-only. Public username login and self-registration are not part of the active product contract.
- Public access requests use the canonical `/access-request` page, store one request record in the auth/core database, and on valid submission attempt one server-side operator notification through the configured mail backend instead of exposing a public `mailto` draft as the active journey. The supported direct mail backends are `sendmail`, `smtp`, and `disabled`; production on vhrz2184 should use the local sendmail-compatible backend unless a future deployment explicitly configures SMTP.
- Access-request notification mail uses the configured server-allowed sender address and uses the requester email address as `Reply-To` after form validation. Routine notification failures must keep a non-secret failure path and must not expose stack traces to the public user.
- The canonical public access-request form requires at least first name, last name, institution, role or function, institutional email address, purpose of use, and one explicit confirmation of the data-protection and confidentiality obligations for pseudonymized research data.
- The canonical public access-request submit path applies route-level throttling plus basic bot-resistance guards through a hidden honeypot field, a signed form-age token, and one generic success response for suspicious submissions so the public surface does not amplify spam or probe feedback.
- Routine server logging for public access requests must stay metadata-only. Full applicant email addresses, institution and purpose text, or complete notification bodies are not part of the normal log contract.
- Production may load GoatCounter only when the public deploy environment provides `VITE_GOATCOUNTER_URL`; the active endpoint is `https://pronunciation-matters.goatcounter.com/count` and the script source is `https://gc.zgo.at/count.js`. Development, testing, and non-production app environments must not render the GoatCounter script even if that variable is accidentally set.
- Public auth-entry pages `/login` and `/access-request` redirect already authenticated users to the safe requested target first, otherwise to the canonical protected default target for their role.
- Accounts are created administratively and use one password-setup/reset token flow that is valid for 14 days unless an active environment setting shortens or extends it.
- The productive protected-area role model contains only `user` and `admin`; `editor` is not part of the active PROMAT product contract.
- Account access must be blocked before session issuance when the account is inactive, not yet valid, expired, deleted, or temporarily locked.
- Admin user management uses the canonical `/admin/users` route family for account creation, status updates, optional expiry dates, invitation/reset preparation, and explicit admin-triggered invitation/reset email sending. Opening the prepared invitation dialog must not send mail. The manual copy fallback for link, subject, and body remains available even when direct sending is disabled or fails.
- Admin invitation/reset email uses the configured server-allowed sender address and uses the authenticated triggering admin's email address as `Reply-To`; if that address is unexpectedly invalid, the configured default reply-to may be used as a guarded fallback without logging tokens, full links, full message bodies, or secrets.
- The canonical protected default targets after login are: safe requested target first, otherwise `/auth/account` for `user` and `/admin/users/page` for `admin`.
- Research page order, page access metadata, task subsets, compare capability, set-filter capability, render-mode vocabulary, and corpus-specific workbench readiness are defined centrally through the active research capability contract.
- For all active corpora `spanish`, `french`, `german`, and `english` and for both active UI languages `de` and `en`, `/{ui_lang}/research/{corpus_language}/design` is the only public corpus-scoped research page.
- The corpus root `/{ui_lang}/research/{corpus_language}` is a public corpus landing page that orients users to `design`, `speakers`, `comparison`, and `phenomena` through their canonical routes.
- All other corpus-scoped research pages and research detail routes, including protected player-media delivery, are authenticated app surfaces and must enforce access before the workbench or media response is rendered.
- The public Teaching area is a separate fully public content surface and does not reuse research auth, owner-bound set state, protected player routing, or protected research-data paths.
- Teaching content is file-based under `content/teaching/{teaching_language}/hubs/{ui_lang}.yaml` for hub editions and `content/teaching/{teaching_language}/{topic_slug}/{ui_lang}.yaml` for topic editions.
- New local Teaching imports are staged only under `content/teaching_import/{import-topic-folder}/` and must follow the binding workflow in `content/teaching_import/README.md` before anything is written into the productive Teaching tree.
- Topic-local Teaching media lives beside the topic source under `content/teaching/{teaching_language}/{topic_slug}/media/{media_type}/...` and is delivered publicly only through `/teaching-media/{teaching_language}/{topic_slug}/{media_type}/{filename}`. Public Teaching media delivery must resolve only against that topic-local media root, never against `data/`, `secure/`, or protected research routes.
- Each `teaching_language` plus `ui_lang` pair is a Teaching edition. Editions may differ in topic set, order, copy, and didactic focus; they are not required to be one-to-one translations.
- The Teaching section root `/{ui_lang}/teaching` is a teacher-first language selection that lists only languages with an available edition in the requested UI language or a valid edition fallback, shows their current topic-count status from the resolved edition, and renders as one neutral single-column selection list of compact clickable rows rather than a multi-column language-card grid. The page-entry `h1` is the direct selection question (`Welche Sprache unterrichten Sie?` / `Which language do you teach?`), and the former duplicate hero subtitle line is not part of the active contract.
- On desktop, each Teaching root selection row keeps one calm horizontal axis with the language title on the left, muted status centered toward the right, and the quiet `Öffnen`/`Open` CTA at the far right for available rows. On mobile, rows may stack into compact two-step text/action flow without a cramped three-column line. Languages whose public Teaching edition exists but currently has no released topic pages remain visible as muted non-link pending rows with `In Vorbereitung` / `In preparation` instead of a CTA.
- Teaching hub content headers, group headings, and optional muted introductory sentences sit as calm centered orientation blocks above the card groups, while topic-page content headers and section headings remain article-like and left-aligned to the teaching content grid. Hub category heading underlines reuse the same pseudo-element geometry as topic `section_heading` underlines (position, size, and offset), adapted only to centered alignment and shared accent tokens.
- On desktop, the Teaching root selection remains visibly narrower than the main Teaching content, while Teaching hubs and topic pages use a broader main content width of roughly 1080-1180 px to reduce unnecessary title wrapping and support denser editorial layouts.
- The Teaching root and edition hubs may show one short calm orientation paragraph directly below the main header to frame the page before users enter the selection list or topic groups.
- Teaching hub groups may carry one short muted introductory sentence from the content model to orient teachers before the topic cards.
- Teaching hub topic cards remain one uniform card family with no featured, wide, compact, or mixed-height variants; hub grids may expand from one column on mobile to two on tablet and up to three equal-width columns on desktop.
- Teaching hub files define grouping, order, and optional release-state overrides only; public card title, summary, and authorship come from the referenced topic edition file, not from duplicated card copy inside the hub.
- Teaching hub cards may show one quiet byline line sourced from topic authors directly below the summary. Missing authors simply omit that line; the card family does not introduce a second metadata chip row in compact hub mode.
- Planned topics remain visible only when the hub references a real topic edition file whose topic metadata explicitly marks the page as not yet public. Those entries render as muted pending cards with a visible status label, but without a link target, keyboard focus target, or fake empty topic route.
- Teaching hub group membership follows editorial content and didactic grouping, not layout demonstration goals; topics must not be regrouped only to fill a three-column row, and groups with one or two cards stay in the same card family on a compact centered row instead of stretching into special sizes.
- Teaching topic pages render content in narrative sections. Blocks before the first `section_heading` form an intro section, each `section_heading` starts a new section, and `next_topics`/`citation` may close the page as their own sections. The section wrapper carries the outer rhythm while the existing two-column block grid continues to handle `layout.span: 1 | 2` inside each section; mobile stays one column, and no masonry, height balancing, right-hand aside column, or visual reordering is part of the active Teaching contract.
- Topic routes use their own calmer header composition: the shared Teaching content header remains the only page-entry `h1` surface, but it sits inside a narrower centered topic-header container than the topic content grid. Hero content may supply the intro text, but it must not re-render as a duplicate visible title block inside the body. Topic metadata sits directly below the intro as part of the header composition, not as a visible body card, and citation content may close the page as one full-width block.
- The closing Teaching `citation` block renders through the shared admonition family as the dedicated `citation` variant: quote icon on the left, citation body in the standard admonition rhythm, and a right-aligned copy action that copies only the citation content without surrounding UI labels.
- Shared Teaching admonitions and admonition-derived public box variants are always fully visible in the active contract: no toggle button, chevron, `aria-expanded` state, or collapsed body is part of the supported public pattern.
- Visible Teaching editorial prose fields sourced from YAML, including topic titles or intros, hub card summaries, section headings, labels, captions, citation text, and further-reading labels, may use safe CommonMark emphasis, links, and inline code. They render through one centralized Markdown normalization path with raw HTML disabled. Technical IDs, raw URLs, token fields, audio source paths, and other machine-value fields stay outside that Markdown pass.
- The canonical public Teaching topic block catalog is: `text`, `rich_text`, `section_heading`, `overview`, `info_box`, `tip_box`, `warning_box`, `image`, optional `embed`, `audio_examples`, `audio_contrast`, `download`, `video`, `next_topics`, `topic_meta`, `further_reading`, `citation`, plus legacy `credits`. The old singular `audio_example` input may remain as a backward-compatible alias but must normalize to the same rendered `audio_examples` family.
- `overview` is the dedicated quick-scan intro block for short title-plus-bullet orientation in the topic lead area. It is not a generic definition or info box and should render through its own calm wordmark-accent variant instead of being downgraded to `info_box`.
- `topic_meta` is the canonical editorial marker for authorship, peer review, created date, and updated date on Teaching topic pages. It renders once directly below the lead as header-local metadata, not as a visible body block. The active topic composition uses up to two centered quiet lines: authors on the first line, then peer review, created, and updated details on the second line when present; missing fields are simply omitted.
- `further_reading` is the calm closing follow-up block before citation content. When it uses structured items, it presents one visible block title, one short description, and compact follow-up cards with quiet text CTAs instead of a normal section-heading stripe plus loose text columns.
- `section_heading` renders only its title on Teaching topic pages and acts as the title of the containing narrative section. Explanatory copy belongs in following `text` or `rich_text` blocks in source order; legacy `lead` values may remain in YAML temporarily for migration, but they are not a visible subtitle contract on topic routes.
- `audio_examples` is the canonical container for one or more non-contrastive listening examples. On public Teaching topic pages it now shares the same audible-material surface family as `audio_contrast`: one calm `audio-section` container with a common header rhythm, one block-level source line, and an internal `audio-grid` of equal-rank `audio-card` items. The active public topic presentation uses a neutral card container with top accent instead of a hard left rail. Each example item may show label or title, transcript, short note, token or speaker ID, and one compact public audio player only when a public Teaching audio asset exists. Token IDs stay letter-true, visually quiet, and anchored in the lower-right area of the transcript quote. Missing public audio must not create broken controls or public pending placeholders. On desktop the internal example grid may use two columns; on mobile it stacks vertically. During playback, a longer example transcript quote may enter a compact active state driven by the real mini-player state (`playing` or `paused`) with a subtle secondary-accent tint or glow, but public Teaching examples do not imply token- or word-level timing without explicit alignment data.
- `audio_contrast` is the dedicated comparison block for directly opposed pronunciation models or realizations. Block-level `transcript` values are inherited by examples unless an example overrides them locally. On public Teaching topic pages, `audio_contrast` is not collapsible in the active contract: it uses the same `audio-section` family as `audio_examples`, with a shared header, a localized sequence row such as `Wortfolge` or `Word sequence`, and an internal `audio-grid` of comparison `audio-card` items below. Two-example comparison blocks render side by side on desktop and stack on mobile. Each example shows its label or title, optional subtitle, short note, and one compact public audio player bound only to a public Teaching asset URL. The compact sequence pill links to the currently active example in its own comparison block through the real mini-player state and may render a left-to-right progress fill derived from the actual audio progress; unrelated audio blocks must not drive that pill, and the surface still does not imply token-level alignment.
- `embed` is the canonical structured block for safe public external teaching embeds. The active provider is `datawrapper`, carried only through structured fields such as `provider`, `src`, `height`, `title`, and optional `caption`; raw iframe or script HTML from YAML is not part of the Teaching contract. Unknown providers or missing required fields must fail closed without rendering a broken block. For the active `datawrapper` provider, `src` must resolve only to an HTTPS embed URL on `datawrapper.dwcdn.net`; arbitrary third-party embed hosts, protocol-relative URLs, and non-HTTPS schemes are not part of the contract. Public topic embeds render inside a dedicated material-like embed card instead of as a raw iframe floating on the page background. A visible PROMAT caption remains optional and should be used only for deliberate non-redundant editorial context, not to repeat Datawrapper's own descriptive text, legend, note, or source.
- On public Teaching topic pages, a Datawrapper `title` is reserved for accessibility and the iframe title attribute; it does not render as an extra visible PROMAT card heading above the embed. Datawrapper embed wrappers must stay visually neutral: no opacity, blend, or filter treatment on the wrapper or iframe. PROMAT must not force a fixed light-only appearance, but it may synchronize the Datawrapper iframe `color-scheme` and the safe Datawrapper `dark=true|false` embed flag to the effective site theme so explicit light-mode and dark-mode selections both stay legible, including mobile Safari.
- Datawrapper resize handling is centralized in static application JavaScript, not injected per block from editorial YAML.
- In two-column Teaching topic groups, `info_box` companion blocks remain editorially secondary to the main reading column. They stay compact inside their own column and must not visually compete as a peer hero surface.
- `further_reading` is a dedicated topic block for optional follow-up references; it remains fully visible and only renders follow-up copy or links when real content is present.
- Teaching inline code markup inside editorial Markdown is didactic text styling for graphemes, forms, and short sequences. It must render as quiet textbook-style emphasis rather than technical monospace badge UI, and topic-page reading typography should support a calmer article rhythm than the denser hub or root overview surfaces.
- Topic pages use article-like visual proportions distinct from hubs and roots: the topic-header container stays narrower than the topic content grid, the metadata rows belong to the header composition, and the vertical rhythm between header and first content row is visibly larger than the lead-to-metadata gap. Section headings may span the full topic grid width without an extra narrow subtitle container. Hub cards and root selection rows keep their denser UI typography and must not inherit that topic reading scale.
- Section headings that introduce grouped follow-up content inside Teaching topic pages, such as `next_topics`/`topic_grid`, use the full content width with left-aligned headings; when the related card row contains only one or two cards, the row may use a compact centered card width without changing the card family.
- Each public Teaching hub route for the active teaching languages `spanish`, `french`, `german`, and `english` must render either grouped topic cards or a quiet empty state; missing public hub content must not degrade into a 404 when a language manifest and index exist.
- The global `DE | EN` switch must stay route-aware on Teaching routes: it preserves the current Teaching edition when available, switches to an equivalent topic when one exists, and otherwise falls back to the target edition hub.
- Teaching may add edition-only UI languages inside `content/teaching` in the future without expanding the global app-wide `ui_lang` contract beyond the active public `de` and `en` routes.
- Teaching remains editorial file content only; no admin editor or research workbench surface is part of the active Teaching contract.
- The canonical editorial validator for Teaching content is the repository script `scripts/validate_teaching_content.py`. It validates manifests, hub references, topic files, topic-equivalent links, and topic-local media references against the active content tree.
- The local Teaching import workflow is repository-only: stage new topic packages in `content/teaching_import/{import-topic-folder}/`, let an agent or small script normalize them into `content/teaching/{teaching_language}/{topic_slug}/` plus the matching hub file, then run the validator, check the affected Teaching pages locally in dev, and commit plus push. There is no server upload, DB workflow, admin surface, or research-pipeline handoff for Teaching imports.
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
- The landing page still reuses the shared compact `DE | EN` language-switch component, but it renders that control in a small landing utility container instead of showing the full global topbar.
- The shared inner shell keeps the global topbar as the stable upper level and the local page shell below it.
- If the authenticated account menu exists in the global topbar, it stays closed by default, opens only on explicit trigger activation, closes again on outside click, `Escape`, trigger re-click, and navigation, and must not persist a sticky-open state across reloads or page transitions.
- In the authenticated topbar user menu, `Mein Konto`/`My account` is always present, `Admin-Bereich`/`Admin area` appears only for admins and leads directly to `/admin/users/page`, and `Logout` stays the final item.
- The global topbar utility order is language switch, theme switch, then account or login control.
- The language switch is a compact text-based `DE | EN` control in the topbar utility zone, not a flag or primary globe-icon control, and it must keep users on the current route while switching `ui_lang`.
- That language switch must derive its target from the current live route state, not from stale initial markup: active player/comparison query state, stable set IDs, session IDs, compare-session context, render modes, and comparable workbench state survive a locale change, while only visible labels are re-localized.
- On the shared mobile topbar, the visible row is reduced to exactly three functions: left menu button, one-line `Pronunciation Matters` wordmark, and the compact `DE | EN` switch on the right.
- On that shared mobile topbar, theme and account or login controls move out of the visible bar and into the drawer; a second utility row below the wordmark is not part of the active shell contract.
- On small mobile widths, the shared wordmark stays on one line beside the burger and must not be split into separate stacked `Pronunciation` and `Matters` lines.
- On that shared mobile topbar, the visible language switch stays compact and secondary: no oversized pill chrome, no heavy border dominance, and no separate utility-bar impression above the page content.
- The shared mobile drawer is the mobile equivalent of desktop topbar plus sidebar: it starts with the shared `Pronunciation Matters` wordmark, then a compact top-level tab row for `Projekt`, `Forschung`, and `Unterricht`, then the current-area navigation block, and finally quieter account or login plus appearance utilities in the lower drawer zone. The drawer wordmark and the mobile topbar wordmark must use the same shared component treatment or the same mobile brand tokens; the drawer brand may not render larger than the topbar brand, and the shared mobile wordmark must still read as primary branding rather than collapsing into meta-text at 320 px.
- The compact top-level mobile tab row should stay visually close to the desktop topbar navigation: the active marker must sit no farther from the label than the desktop underline treatment, and the active tab should use the same restrained underline rhythm instead of a looser bottom gap.
- In that drawer, the top-level mobile navigation is a compact mini-tabbar directly below the wordmark rather than a second large vertical list: the active top-level area uses a subtle bottom indicator, not a left rail, oversized pill, or competing filled block.
- The mobile current-area block follows directly below that mini-tabbar and uses one compact contextual title only when it is more specific than the active main area already shown in the mini-tabbar: show the deeper local context name when one exists, for example `Spanisch-Korpus`, and suppress repeated main-area labels such as `Projekt`, `Forschung`, or `Unterricht` below the tabs. A large repeated `Hauptnavigation` or `Aktueller Bereich` label is not part of the active mobile drawer contract when the hierarchy is already clear.
- The mobile drawer begins near the top safe area with the shared `Pronunciation Matters` text-wordmark treatment rather than a generic heading, and its overlay offset must not be derived from the mobile topbar height. Use a moderate safe-area-aware top inset of roughly 24-32 px plus safe area instead of pushing the drawer body below the topbar.
- In that drawer, local active page links may use a restrained accent-tint pill without left-border markers, and account plus appearance utilities sit as quieter, compact secondary controls in the lower drawer zone instead of competing with main navigation.
- The mobile drawer opens as an off-canvas left panel with a matching backdrop fade and closes through the same animated path for backdrop click, `Escape`, and programmatic close, while reduced-motion users receive the same state change without perceptible motion.
- The local page shell uses a left sidebar for area navigation and a right main-content column.
- The sidebar begins with a permanent area header: section icon, section title, and a subtle divider.
- Language-context pages keep their language back-link and language title below that permanent area header, not instead of it.
- On research language-context pages, that sidebar context title uses the same localized corpus title as the main page heading, for example `Spanisch-Korpus` / `Spanish corpus`, not only the bare language label.
- Sidebars are area navigation only and must not repeat account actions such as `Mein Konto`, `Admin-Bereich`, or `Logout`.
- Protected admin pages reuse the shared inner shell with one non-clickable `Admin-Bereich` sidebar header and the fixed linear navigation `Benutzer`, `Analytics`.
- On public research pages for unauthenticated users, protected research targets stay visible in the sidebar but use muted locked navigation states rather than per-item login notices.
- In those muted locked research sidebar states, the lock icon renders immediately after the visible page label and no additional visible `login required` helper line is repeated inside the navigation list.
- Breadcrumbs are rendered only when they add real orientation value, not as a pseudo-context line that merely repeats section or language.
- Page-level back navigation uses one shared compact back-link family across public, auth, protected-account, research, and teaching surfaces: the control sits above breadcrumbs and the page-entry heading, stays left-aligned inside the current content container even when the surrounding header copy is centered or kept on a narrower inner measure, and uses the shared back-pill arrow plus a target-only localized label such as `Sprachauswahl` / `Language selection` rather than visible helper phrases like `Zurück`, `Zur`, `Zu`, or `Back to`.
- An optional second back link may repeat at the bottom only on long detail pages, but it must reuse the same compact back-link component and target-only label; full-width back bars or page-local back-button families are not part of the active contract.
- Shared back-links must not be re-wrapped in `pm-container`, `pm-reading`, or other helper wrappers that narrow the row, create panel chrome, or move the pill off the main content axis; top and bottom instances align to the same page content edge.
- Desktop shows breadcrumbs only from hierarchy depth 3 onward because the sidebar already carries orientation on flatter levels.
- Mobile shows breadcrumbs from hierarchy depth 2 onward because the sidebar is reduced or absent there.
- When a breadcrumb is shown, it always renders the full path including the current page as the final, non-clickable item.
- The shared shell must not hide horizontal layout defects through body-level overflow clipping; mobile overflow is corrected at the responsible grid, menu, popover, control cluster, or scroll-container level.

## Active UI System

- Productive pages, shared partials, and established CSS families are the visual source for recurring UI work.
- `de` and `en` are the active public UI languages for finished surfaces under the canonical `ui_lang` route context.
- Finished or newly completed UI surfaces must ship with both `de` and `en` display strings in the same run; do not treat English as a later copy-only follow-up for already-finished visible UI.
- Visible UI strings for finished surfaces must resolve through the shared translation layer and server-provided localized payloads; do not hardcode visible `de`/`en` branches or fallback copy in Python builders, Jinja templates, or page JavaScript.
- Technical keys, route values, IDs, and client-state field names remain stable English machine values and must stay separate from translated display labels.
- Standalone auth surfaces on `/login`, `/access-request`, and `/auth/password/*` use the dedicated auth shell without research sidebar, corpus navigation, or workbench framing.
- Visible auth-facing product naming uses `Pronunciation Matters`; `PROMAT` remains the internal or technical shorthand unless an active spec explicitly requires a visible exception.
- The public auth surfaces on `/login`, `/access-request`, and `/auth/password/*` reuse the current PROMAT action, input, and message families instead of page-local MD3 or legacy CORAPAN-looking controls.
- On `/login` and `/auth/password/*`, the access request remains a quieter secondary section below the primary sign-in or reset flow.
- On `/access-request`, the primary work surface is the form itself, while the login hint remains a quieter secondary card below it.
- The public project area uses exactly four canonical visible pages in this order: `about`, `structure`, `data-methods`, `team`.
- The old project slug `research-design` is legacy redirect-only and must not remain as a visible project navigation entry beside `structure`.
- The public project `team` page is a scan-friendly credits and contributors surface, not a manifesto-like prose page. It uses the shared metadata-card family only for the project lead or coordination and language-corpora sections; the Language Center context and acknowledgements remain normal reading-text sections, with the acknowledgements names rendered as a simple list rather than an additional card grid.
- In the first card-based `team` section, the two lead cards use short role titles as the visible card heading and place the concrete contributor name as the first prominent line directly below that heading; the detailed role and focus metadata remains below as structured rows.
- On the public project `team` page, both card-based sections share one calm team-grid rule: one column on mobile, two equal-width columns from tablet upward, no four-column corpus row, a denser shared gap than the generic metadata grid, and a centered narrower max-width inside the normal feature band so all six cards read as one compact 2-column block instead of spreading across the full content width.
- The public project `team` page must not reintroduce the old standalone student-participant prose block as a primary visible section.
- The research section root `/{ui_lang}/research` stays a compact corpus-selection overview without an additional intro or subtitle block below the page heading.
- On public research and teaching overview roots that use the shared corpus-card grid, mobile widths collapse to one column and must not rely on hidden overflow to keep cards inside the viewport.
- On that research section root, each corpus card shows only the localized corpus title, then the primary metadata order `Projektleitung`/`Project lead`, `Materialkonzeption`/`Material design`, `Durchführung`/`Conducted by`, and then the secondary status order learner-recordings count or `Korpus im Aufbau`/`Corpus in progress` followed by the optional reference-recordings line only when at least two distinct native-speaker `standard_variety` values exist.
- The research section-root corpus cards do not use repeated descriptive body copy such as generic learner-pronunciation summaries; the cards are metadata-first orientation surfaces, not mini content teasers.
- On the research section root, all corpus cards share one unified primary-blue top accent bar; corpus- or language-specific accent colors do not belong on that overview-card group even if those colors remain meaningful on other surfaces.
- Those research section-root corpus cards stay inside the existing app card system rather than introducing a separate overview-card language: speaker cards are the primary visual reference for their accent bar, quiet materiality, divider rhythm, secondary-label styling, and bottom CTA treatment.
- The fixed visible structure of each research section-root corpus card is title, primary metadata block, secondary status block, and footer CTA; the CTA remains bottom-aligned and uses the neutral existing inline-action secondary styling instead of language-colored button text. Reuse existing tokens, card wrappers, divider spacing, and inline-action families before introducing any research-card-local style hooks.
- Across the shared app card system, if a card exposes a visible action area, footer CTA, or equivalent action/footer block, that action block stays bottom-aligned at the end of the card rather than floating in content height. This is a binding system rule for all card families, not a page-local preference.
- Across the shared app card system, any content block that sits directly above a divider-separated footer or follow-up action section keeps a minimum block-end inset via the shared divider spacing tokens, so status text, recordings labels, or comparable meta rows never visually stick to the next divider.
- The public corpus landing page `/{ui_lang}/research/{corpus_language}` is a reduced orientation page. The left sidebar remains the only area navigation, and the main column must not repeat `Design`, `Sprecher:innen`, `Vergleich`, or `Phänomene` as a second list, card set, or CTA wall.
- In the main column of that public corpus landing page, the visible structure is limited to the localized corpus title, one short subtitle, two short prose paragraphs, and for signed-out users one small action row with exactly two actions in this order: `Zugang beantragen`/`Request access`, then `Zum Login`/`Go to login`.
- The first prose paragraph on that public corpus landing page explains the corpus as a research area with public design information plus protected work areas and points users to the left navigation instead of rebuilding the area navigation in the body.
- The second prose paragraph explains the privacy and access frame in calm prose, explicitly names legitimate users as Angehörige von Forschungs- und Bildungseinrichtungen / members of research and educational institutions, and keeps the user journey order request-access first, login second.
- The login action on that public corpus landing page preserves the exact corpus-root return target, so a user who starts on one concrete corpus landing page returns to that same landing page after successful authentication instead of being dropped into a generic auth default.
- For authenticated users, that public corpus landing page suppresses the anonymous action row and keeps the reduced orientation copy only.
- Visible UI must not expose raw technical values such as UUID-like set identifiers, internal translation keys, or internal handoff/debug vocabulary when a user-facing label or omission is the truthful product behavior.
- External HTTP(S) links on user-facing app surfaces open in a separate browser tab or window through centralized app behavior and must carry `noopener noreferrer` protection instead of relying on page-local ad hoc link markup.
- When a recurring UI family already exists, it must be extended or reused before a page-local variant is introduced.
- Repeated UI families that must be treated systemically include action hierarchy (`buttons`, inline actions, overflow actions), form controls (`inputs`, `selects`, `textareas`), badges and chips, cards and list rows, step containers and work blocks, dialogs and confirm flows, empty states, sticky headers or anchors, and muted, active, or selected states.
- The shared interaction system now separates productive action buttons, navigation pills, CTA links, and chips or tabs by function instead of visual coincidence.
- The productive icon system is intentionally dual-track and must stay explicit rather than drifting into ad hoc mixtures.
- `Material Symbols Rounded` is the canonical font-based icon path for inline or text-near action icons, form icons, status icons, and other compact interaction icons embedded in buttons, labels, cards, alerts, snackbars, or messages. It is delivered self-hosted, uses the rounded variant, and follows the shared base axis defaults already defined in the active CSS (`FILL 0`, `wght 300`, `GRAD 0`, `opsz 24`) unless one documented shared component family requires a different override. Size, line-height, and alignment must flow through existing shared classes and tokens instead of page-local ad hoc rules.
- `pm-icon-mask` is the canonical chrome or utility icon path for shell, topbar, drawer, navigation, player, audio, lock, theme, admonition, and comparable larger surface icons. It is a centralized CSS-mask system backed by shared SVG data-URI tokens, keeps size on the shared `--pm-icon-size-*` tokens, and leaves icon color token- or context-driven.
- Allowed icon exceptions must stay deliberate: inline SVGs may be used when UI is built dynamically in JavaScript and forcing the canonical path would be disproportionate; typographic arrows or symbols may remain when they are intentionally part of the text treatment rather than a generic icon slot; centralized SVG masks managed through the shared `pm-icon-mask` token system remain part of the canonical utility-icon path.
- New Font Awesome usage, new Bootstrap Icons usage, new external icon CDNs, unexplained Material Symbols variant drift, and random one-off inline SVGs without a shared reason are not part of the active UI contract.
- Action buttons are reserved for contextual actions such as login, save, refresh, create, compare, modify, and form submission; they do not use trailing arrows.
- Navigation pills are reserved for compact navigation targets inside auth, app, and data contexts; forward pills keep one trailing arrow rendered by the component, while explicit back or return pills use one leading left arrow and no trailing arrow.
- CTA links are reserved for editorial landing and overview cards; they stay text-like, keep one trailing arrow rendered by the component, and must not fall back to pill-button chrome.
- Shared CTA-link underline states are rendered from the anchor container so the underline runs continuously under both label text and trailing arrow on hover, focus-visible, and active states.
- Chips, tabs, active filter states, and similar selection controls remain a separate component family and must not be collapsed into action-button or navigation-pill variants.
- Shared topbar actions, action buttons, filter chips, drawer navigation rows, nav pills, form controls, and comparable primary mobile controls use a minimum 44 px touch-target height; smaller inline editorial breadcrumb links may remain text-sized when they are not the primary action surface.
- Google Fonts remain an explicitly accepted external dependency in the active product contract. The shared base template loads `Inter` for UI, navigation, display, labels, and meta typography, and `Source Serif 4` for reading, card, and long-form text zones. As long as that policy remains active, `fonts.googleapis.com` stays required for the stylesheet request and `fonts.gstatic.com` stays required for the delivered font files.
- Local hosting of `Inter` or `Source Serif 4` is not part of the current contract and must not happen as a stealth asset swap. Any later localization run must prove visual parity or deliberately documented typography changes through a dedicated follow-up with the same or explicitly changed font version, the intended weights including any intermediate values such as `font-weight: 450`, before-or-after screenshots on representative real routes, and a clear rollback path.
- The shared footer release label is generated from deployment metadata, not from a hardcoded template string. Production deploys set `VITE_APP_VERSION` from the latest GitHub Release tag and the app renders that tag exactly, for example `v0.7`; missing local or non-production metadata falls back to `dev`.
- On narrow mobile widths, the shared footer becomes a compact meta footer: only the copyright line and inline legal text links remain visible, while larger footer branding, release version, and secondary attribution lines may be hidden.
- In that compact mobile footer, legal links remain typographic inline text links with close underline behavior; they do not inherit button or drawer-row geometry.
- When admin or data-heavy tables do not provide a dedicated mobile card/list mode, they must render inside an explicit horizontal scroll container with a visible cue or hint instead of being clipped by the surrounding layout.
- Structured data tables, compact data lists, player wordlists, admin or analytics tables, speaker tables, and comparable workbench rows must stay recognizable as tables or dense lists on mobile; prefer local horizontal scroll containers or compact two-line rows over per-cell card decomposition.
- In the wordlist player on small mobile widths, one item row keeps the visible number, item text, time range, and download action in one compact row or a controlled two-line row; full-width number pills above the item text are not part of the active UI contract.
- Normal inline text links and quiet meta links keep typographic underline behavior close to the text and must not inherit 44 px action geometry; the shared mobile touch-target floor applies to explicit controls and action-link families, not to ordinary inline prose or breadcrumb links.
- Legacy inline-action and older button classes may remain temporarily where migration is incomplete, but new or migrated productive surfaces must use the semantic interaction system rather than extending the older generic inline-action styling.
- Badge, chip, and pill content across the active research UI stays on the regular UI font family rather than the reading or book typography, even when the surrounding item or content text uses the reading font.
- Research workbench UI uses current productive pages as reference surfaces: `comparison` for step containers, selection blocks, badge or meta rhythm, and clear vertical work sequences; `player` for dense material rows, compact work heads, sticky anchors, and muted versus active row states; `speakers` and the person profile for speaker cards, compact task actions, and row or table action layout.
- Learner speaker cards in the `speakers` card family keep neutral card containers with no decorative top bar; CEFR or level color belongs on the explicit level badge in the level meta row, not on the card chrome. In the learner overview card, the compact visible fact set is level badge, `L1`, gender, and target-country stays; `Sessions` and recording-year summary do not belong to that overview card anymore. Native-speaker cards may keep their separate teal category accent because they encode speaker-group semantics rather than CEFR level.
- Across speaker cards, profile headers, player metadata cards, and comparison speaker rows, native-speaker variety or origin display uses one canonical localized native-reference value derived from `standard_variety` and `origin_country`; raw slugs such as `ES_STD` are never shown, and if variety and origin country resolve to the same user-facing label, that label is rendered only once.
- Shared profile CTAs in speaker cards and player metadata cards use the same localized `Profil`/`Profile` label with the existing inline-action arrow affordance; variant copy such as `Profil öffnen` or `Open profile` is not part of the active UI contract.
- Locale changes in protected research workbenches must keep stable technical state on stable machine values such as `set_id`, `session_id`, `compare_session`, task keys, render-mode keys, and comparable filter keys; localized labels such as `Spanien`/`Spain` or other translated UI strings are never the source of truth for restoring workbench state.
- Overview surfaces stay overview surfaces, and editor or detail surfaces stay editor or detail surfaces; active split flows must not be collapsed back into mixed one-page workbenches without an explicit spec change.
- If shared layout files, shared component CSS, or reused partials change, the affected repeated UI families must be regression-checked on at least one other active page that uses them.
- Visually substantial UI changes require browser validation and screenshot comparison against the affected productive reference surfaces before the run is considered complete.
- For finished bilingual surfaces, browser validation must cover the same real routes in `de` and `en` and explicitly include dialogs, placeholders, empty states, snackbars, overflow actions, and longer English labels where they affect layout or density.
- A substantial UI run is not accepted on green tests alone; visible defects found in the browser pass must be fixed and the screenshots regenerated until the in-scope surfaces are linguistically and visually clean.

## Runtime Boundaries

- `AUTH_DATABASE_URL` is the canonical auth/core database variable.
- `RATE_LIMIT_STORAGE_URI` is the canonical shared rate-limit backend variable.
- `PROMAT_RUNTIME_ROOT` is the canonical runtime root.
- `PROMAT_PUBLIC_ROOT` is the canonical public root.
- `PROMAT_TEACHING_CONTENT_ROOT` is the canonical optional override for the file-based Teaching content root; when unset in local development, the default is the repo-root `content/teaching` tree.
- Paths are derived through runtime/config wiring, not freehand string paths.
- In development and testing, the rate-limit backend may use `memory://`.
- In non-development environments, `RATE_LIMIT_STORAGE_URI` must be set to one shared non-memory backend; silent production fallback to `memory://` is not part of the active runtime contract.
- For the default local development PostgreSQL URL `postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:54321/promat_auth`, `scripts/dev-start.ps1` is the canonical app entrypoint and must ensure the local `promat_auth_db` service plus the idempotent auth/core and research-set migrations are applied before the Flask app starts.
- In that canonical local development flow, `scripts/dev-start.ps1` also owns the live browser loop on `127.0.0.1:8000`: it must clear stale PROMAT dev listeners before launch and start the Flask app in development reload mode so code and template changes become visible in the browser without manual process hunting.
- If that default host port cannot be published on a dev machine, `scripts/dev-start.ps1` and `app/scripts/dev-setup.ps1` may select a free local fallback port through `PROMAT_DEV_DB_PORT`, but they must keep `AUTH_DATABASE_URL` aligned to the actually published local PostgreSQL host port before migrations, admin seeding, or app startup.
- In that canonical local dev flow, `scripts/dev-start.ps1` also seeds or updates one reliable default admin account with the reachable email `felix.tacke@uni-marburg.de` unless explicit overrides are supplied.
- `app/scripts/dev-setup.ps1` remains the canonical initial bootstrap path for the same local PostgreSQL setup; it provisions the local database, applies the same migration chain, and then may hand off to `dev-start` without re-running bootstrap work.

## Dev/Prod Parity

- Dev and Prod use the same architecture, terminology, routing, and data semantics.
- Allowed differences are infrastructure-level only.
- Production WSGI delivery runs through Gunicorn or an equivalent production-grade WSGI server; the local development entrypoint `python -m src.app.main` remains development-only and must not be reused as the production container server command.
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
- For the current English running-text path, `data/config/research_player/english/task_catalogs/text.json` is the canonical connected-text catalog under the technical task key `text`; it keeps visible item numbers `T1`, `T2`, `T3`, ... together with stable item IDs `t_01`, `t_02`, `t_03`, ... and marks `t_01` with `spoken_title_item: true` because the title is a catalog item when spoken.
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
alignment/
derived/
items/
metadata.json
```

### Semantics

- `data/sessions/` is the webapp-facing research runtime only.
- Runtime session trees may contain only final player-facing artifacts: `metadata.json`, `alignment/{task}.json`, `derived/{task}.mp3`, and `items/{task}/{item_id}.mp3`.
- Runtime session trees must not contain WAVs, TextGrids, XLSX workbooks, secure files, MFA working directories, batch-local working state, or other intake/intermediate artifacts.
- `alignment/` contains reduced runtime JSON only, never whole-session TextGrids.
- `derived/` contains webapp-facing full-task MP3 files only.
- `items/{task}/` contains split MP3 files only.

### File rules

- Canonical task filenames use `wordlist`, `text`, `interview`.
- Reduced alignment JSON belongs under `alignment/{task}.json`, never under `items/`.
- Player-facing full-task MP3 files use `derived/{task}.mp3`.
- Player-facing split MP3 paths use `items/{task}/{item_id}.mp3`.
- Versioned runtime session trees under `data/sessions/` must not ship fictional, placeholder, or other dummy research sessions; production population of that tree is reserved for the central orchestrating import path.
- The only active path that may populate or update production runtime session trees from intake batches is `scripts/research_data_intake/import_batch_to_production.py`.
- That importer may derive runtime artifacts only from explicit classified batch inputs plus the batch-local `working/` tree.
- Runtime imports must not invent metadata, audio, task mappings, or person assignment heuristically from workbook prose or loose filenames.
- Runtime imports must not delete unrelated existing task artifacts from the same session unless one explicit reset or replace mode authorizes that removal.
- For the current Spanish sentence-list catalog, visible numbering remains `D1` through `D30`, `QY1` through `QY10`, and `QW1` through `QW10`, while stable technical IDs remain `d_01` through `d_30`, `qy_01` through `qy_10`, and `qw_01` through `qw_10`.
- The current player delivery routes map full-task playback to `.../player/{session_id}/{task}/audio.mp3` and single-item item-media delivery to `.../player/{session_id}/{task}/items/{item_id}.mp3` without exposing internal runtime paths.
- The canonical single-item player route serves a playback-safe inline `audio/mpeg` response by default; explicit download semantics stay on the same route family through explicit download intent rather than through a separate media path.
- For the current `wordlist` production path, web derivatives use MP3 in mono with `160 kbps` CBR for both `derived/wordlist.mp3` and `items/wordlist/{item_id}.mp3`.
- Internal split filenames use stable `item_id`s.
- Single-item download filenames are generated separately at delivery time and do not redefine internal storage paths.
- The prepared delivery filename contract is `{person_id}_{task}_{item_id}_{download_label}.mp3`.
- `download_label` is a readable delivery-only text component derived from the canonical text or label of the exported unit.
- Longer filenames with `session_id` and labels are for later download logic, not canonical storage.

## Local Archive Filesystem

### Archive root

```text
PROMAT_LOCAL_ARCHIVE_ROOT
```

Default local example:

```text
C:/dev/promat_data_archive/
```

### Session archive structure

```text
PROMAT_LOCAL_ARCHIVE_ROOT/
	sessions/
		{language_code}/
			{session_id}/
				secure/
				raw/
				source/
				alignment_source/
				runtime/
				metadata/archive_manifest.json
				reports/
```

### Archive semantics

- The local long-term archive is outside the repository workspace and is session-centered, not batch-centered.
- `secure/` is reserved for local secure-only files such as consent PDFs, questionnaire PDFs, and `secure_person_intake.json`; those files never belong in `data/sessions/`, Git, or prod upload packages.
- `raw/` contains untouched original WAV masters when delivered.
- `source/` contains processed/source WAVs that form the operative derivation basis. When no processed WAV exists, the raw WAV is also copied here so derivation tooling always finds a WAV under `source/`.
- `alignment_source/` contains TextGrids, Amberscript JSON, MFA source exports, or comparable source/intermediate alignment inputs.
- `runtime/` mirrors the final generated runtime artifacts for traceability.
- `metadata/archive_manifest.json` is the canonical per-session archive manifest and must record source batch, timestamps, input/output checksums, warnings, and skipped or missing artifacts without duplicating unnecessary clear-text personal data.
- `reports/` may contain session-local validation, import, or archive reports.

## Intake Batch Working Filesystem

### Batch root

```text
scripts/research_data_intake/import/{batch_name}/
```

### Drop-in semantics

- Batch directories under `scripts/research_data_intake/import/` are generic intake drop-in areas and are not hard-wired to one corpus language.
- A processable batch directory must keep `batch` in its directory name.
- There is no manual subfolder requirement for `processed/`, `raw/`, `source/`, or `intake_data/`.
- Users may place the workbook, WAVs, TextGrids, Amberscript JSON, and other task-related intake files directly under the batch root or in optional helper subfolders.
- The active batch scanner must classify files strictly from explicit filename signals for `person_id`, target corpus, task, role, and file type.
- If filename classification is ambiguous, conflicting, or incomplete, the pipeline must warn, skip the affected unit, or fail explicitly; it must not guess.
- Workbook prose may refine metadata, but it must not substitute for missing explicit filename-based file identity.

### Batch-local working subtree

```text
working/.intake_state.json
working/{person_id}/wordlist/source/wordlist.wav
working/{person_id}/wordlist/alignment/wordlist.TextGrid
working/{person_id}/text/source/text.wav
working/{person_id}/text/alignment/text.TextGrid
working/{person_id}/text/alignment/text.json
working/{person_id}/text/mfa_corpus/
working/{person_id}/text/mfa_output/
working/{person_id}/text/mfa_manifest.json
working/{person_id}/text/mfa_state.json
working/{person_id}/interview/source/interview.wav
working/{person_id}/interview/alignment/interview.json
```

### Working rules

- `working/` is a pre-production, person- and task-centered preparation area inside one concrete batch.
- The batch-local working organizer updates that tree incrementally per `person_id` and task instead of deleting the whole `working/` subtree for each run.
- Batch-local `working/` outputs are preparatory only: they must not write directly into prod paths and must not redefine the runtime contract.
- The canonical task filenames inside `working/` are always task-based, for example `source/text.wav` and `alignment/text.TextGrid`, regardless of the intake filename that carried the file into the batch.
- `working/.intake_state.json` is the batch-local technical state for incremental organization and records recognized task inputs, size-plus-`mtime` snapshots, last task status, last evaluation time, and the managed working outputs per `person_id` and task.
- Person and task assignment for batch-file organization must come from explicit filename logic only; the pipeline must not invent person IDs or task names heuristically.
- For `wordlist` and `text`, the organizer treats classified source WAV plus alignment-source TextGrid as the relevant working inputs for the task-local subtree.
- When a task changes, replacement stays task-local: the organizer may replace only `working/{person_id}/{task}/` and must not delete the whole person subtree or the whole batch `working/` directory.
- In the current preparatory `text` path, the TextGrid is only the segment-boundary source.
- The preparatory `text` MFA step may create only segmented WAVs, matching `.lab` transcripts, `mfa_output/` target directories, and a batch-local manifest for reverse mapping.
- The preparatory `text` MFA step also writes a task-local `mfa_state.json` that records the input signatures, preparation version, and MFA run identity so unchanged text inputs can reuse the existing working alignment instead of rerunning MFA.
- The preparatory `text` MFA step may clamp tiny TextGrid-to-WAV frame-boundary overruns caused by rounding to the source WAV duration and must record a warning; larger timing mismatches remain hard errors.
- For connected text catalogs with a first item marked `spoken_title_item: true`, the preparatory `text` MFA step may omit that first title item only when the catalog contains exactly one more item than the spoken TextGrid intervals and every spoken interval matches the following catalog items in order. The omitted item must be recorded as `omitted_items[]` with `omitted: true` and `omit_reason: "unspoken_title"` and must not receive timings or split audio. Any count mismatch, missing title marker, or later text mismatch remains a hard conflict.
- The batch-local `text` import step may derive `working/{person_id}/text/alignment/text.json` from the preparatory manifest plus MFA `mfa_output/` TextGrids, while still staying inside the batch-local working tree.
- If the task-local signatures still match and `working/{person_id}/text/alignment/text.json` already exists, the importer may reuse the current text alignment instead of rerunning MFA; if `text.json` is missing but the cached MFA outputs still match, the importer may import the cached alignment without repeating MFA.
- In this working-tree-only `text` JSON step, `audio.full_mp3` may already point to the canonical future relative artifact path `derived/text.mp3` even though the MP3 artifact is not produced yet in that same step.
- In this working-tree-only `text` JSON step, `session_id` may remain `null` until later metadata integration resolves the final production session identity.
- The preparatory `text` MFA step must obtain canonical item texts from an explicit external source such as a task catalog or mapping JSON and must not guess final texts from TextGrid labels.
- For `interview`, the working organizer now requires a classified source WAV and a classified alignment-source JSON; raw-only interview delivery is not an operative fallback for runtime derivation.
- In that interview alignment JSON, spoken token cores stay in `tokens[].text`, punctuation that originally followed a material-reference marker such as `25[wl_025].` stays token-local in `tokens[].suffix`, and `annotations[]` keep only the structured `material_ref` payload plus `insert_after_token_id` without any parallel `trailing_punctuation` field.
- Interview transcript bracket annotations that are not PROMAT material references, including IPA forms such as `[θ]` or `[x]` and unintelligible markers such as `[u]`, stay token text and must not produce `material_ref` annotations.
- PROMAT material references are limited to the controlled item-id patterns used by task catalogs, such as `wl_059`, `t_18`, `d_01`, `qy_01`, and `qw_01`; unknown material-ref-like prefixes remain errors instead of being guessed.
- Amberscript segment speaker IDs may be mapped from the export-local `speakers[]` table only when the table unambiguously maps an alternate ID such as a UUID to `Speaker 1` or `Speaker 2`; otherwise the interview task must report a speaker-mapping error instead of guessing.
- Amberscript zero-duration words or segments may be clamped to a minimum duration of 1 ms with an import warning; negative or otherwise incoherent timing remains an explicit error.
- That interview source selection remains explicit and filename-driven. If multiple equally ranked candidates exist for the same required input, the organizer must report a hard conflict instead of guessing.
- For `interview`, `person_id` values with speaker marker `-N-` and workbook rows with `speaker_type = native_speaker` are a neutral not-expected case: missing batch WAV or JSON must not be reported as missing or incomplete, and organizer or importer status must stay a non-deficit value such as `not_expected_for_native_speaker`.
- The batch-local interview JSON is a productive working-tree preparation artifact for the central production importer.
- The current intake language configuration for this working path is prepared generically for `es`, `de`, `fr`, and `en`, including the mapped MFA acoustic and dictionary models per language.
- Final production transfer from intake batches into runtime and local archive is executed only by the central importer `scripts/research_data_intake/import_batch_to_production.py`.
- That importer may populate PostgreSQL research metadata tables `research_people`, `research_sessions`, and `research_session_exposures` from workbook sheets `Research_Person`, `Research_Session_Intake`, and `Exposure`.
- The same importer projects canonical runtime `metadata.json` plus task artifacts into `data/sessions/{language}/{session_id}/`, writes per-session archive trees under `PROMAT_LOCAL_ARCHIVE_ROOT`, and may sync only the productive task layers whose working inputs are actually available.
- Workbook rows without new files are not an error by themselves: they may still update existing DB or runtime metadata, and otherwise must report as out-of-batch or no-files-with-no-existing-target rather than inventing audio artifacts.

## Prod Upload Package Filesystem

```text
scripts/research_data_intake/exports/{upload_id}/
	sessions/
	db/import_payload.json
	config/research_player/
	manifest.json
	checksums.sha256
	reports/
```

- Prod upload packages are explicit allowlist exports built from already validated runtime artifacts plus optional DB payloads or runtime-relevant config JSON.
- Runtime session paths in upload packages must use the runtime corpus slug under `sessions/{corpus_slug}/{session_id}/...` (for example `sessions/french/...`), not the two-letter `target_language` code form.
- Runtime filesystem and upload-package filesystem must stay aligned by corpus slug: local runtime under `data/sessions/{corpus_slug}/{session_id}/...` and package payload under `sessions/{corpus_slug}/{session_id}/...`.
- `checksums.sha256` in prod upload packages is UTF-8 with LF-only line endings and strict line format `<sha256><two spaces><relative-posix-path>` so raw Linux verification via `sha256sum -c checksums.sha256` remains deterministic.
- If a real DB payload exists for the batch, the package includes `db/import_payload.json`; upload packaging must not invent or synthesize dummy payloads.
- Package validation must preflight server gates locally before transfer: allowlist paths, corpus-slug session directories, manifest file list parity, checksum file format and encoding, LF-only, and file hash verification.
- Prod upload packages must not contain WAVs, TextGrids, XLSX workbooks, secure files, raw/source/alignment_source trees, MFA working directories, or other temporary artifacts.
- The package builder is not a second importer: it must not reinterpret the original batch or re-derive truth from workbook prose once the runtime and import payload already exist.
- The initial v0.7 production server model is data-only: prod upload delivery targets `/srv/webapps_storage/promat/data/incoming/{upload_id}/` first, validates allowlist paths plus checksums plus file counts, stages a new release under `data/releases/{release_id}/`, and promotes with an atomic `data/current` symlink switch instead of writing directly into the live target.
- The initial v0.7 production deployment has no separate `/srv/webapps/promat/media` or `/app/media` bind mount. A separate media root may be added later only if application code gains a real runtime need for it and the platform spec is updated first.
- Upload omission must never delete existing production files implicitly; deletion is always a separate explicit mechanism, and failed incoming or staging trees stay in place until explicit cleanup approval.

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
- `person_notes`
- `research_consent_signed`
- `teaching_consent_signed`
- `consent_date`
- `consent_file`
- `questionnaire_file`
- `secure_notes`

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
- `session_notes`
- `notes`
- `tasks`
- `files`

### Exposure semantics

- `stays_in_target_country` is the compact session-level summary field.
- `exposure_entries` stores structured stay details per session.
- Each entry may contain `country`, `duration_months`, `type`, and optional `exposure_notes`.
- Active intake practice uses at most one exposure entry per session, but the stored entry may summarize multiple places or stays.
- `country` may remain a semicolon-separated original string such as `France; Israel`.
- `duration_months` may be an integer or decimal month count.
- `unknown`, `unspecified`, `other`, and empty exposure types are non-prominent fallback states and must not appear as visible UI type labels.
- Protected research profile views show stay details as `{duration} · {country} · {type}` when present and show `exposure_notes` in full below.
- Speaker cards and speaker-table summaries reduce stays to `None`, `Yes`, or `Yes · {duration}` without countries, types, or notes.

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
ec_std
cl_std
pe_std
bo_std
uy_std
py_std
ve_std
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
- Intake workbook aliases `CH_FR_STD` and `CH_DE_STD` normalize to the same runtime canonical values.

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
