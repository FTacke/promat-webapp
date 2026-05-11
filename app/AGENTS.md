# PROMAT App Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` für Arbeiten innerhalb von `app/`.

## Scope

- `src/app/` enthält die Flask-Anwendung und das Runtime-Wiring.
- `templates/` und `static/` bilden das UI-System.

## Regeln

- Implement application behavior against `docs/spec/`, not against older local notes or deleted doc paths.
- If routing, research-access behavior, IDs, vocabularies, or runtime boundaries change, update the relevant file in `docs/spec/` in the same run.
- Route research task subsets, compare rules, set-filter rules, render-mode vocabularies, and corpus surface readiness through `app/src/app/research_capabilities.py`; do not introduce parallel capability literals in page builders, routes, sessions, sets, or presets.
- For corpus-scoped research routing, keep the access boundary generic: only `design` may remain public, and all other research pages, profile/detail routes, and protected player-media routes must enforce auth before page or media rendering.
- If shared app-shell or sidebar-navigation rules change, update `docs/spec/platform-data-files.md` in the same run.
- If a shared layout element changes on a real page and `sample` showcases it, update `templates/pages/sample_page.html` in the same run.
- Before adding new template, CSS, or page-JS patterns, inspect the relevant productive templates, shared partials, and shared CSS families first.
- Reuse or extend existing UI families before creating page-local variants for buttons, form controls, badges or chips, cards or list rows, dialogs, empty states, sticky anchors, or overflow actions.
- Finished UI inside `app/` must ship in `de` and `en` together; do not defer English-visible copy on already-finished surfaces.
- Visible UI strings in Python builders, templates, and page JS must resolve through the shared translation layer or server-provided localized state, not through local hardcoded branches.
- For research UI, use `comparison` as the main reference for step containers, selection blocks, badge or meta rhythm, and linear work sequences; use `player` as the main reference for dense material rows, compact work heads, sticky anchors, and muted versus active row states.
- Prefer calm, linear flows and keep overview surfaces distinct from editor or detail surfaces; avoid extra mini-overlabels or parallel work islands unless the active spec calls for them.
- Changes to `20_layout.css`, `30_components.css`, `40_cards.css`, or shared partials require regression checks on at least one unaffected page using the same family.
- Substantial UI changes require browser validation and screenshots, not only code review or pytest.
- For finished bilingual surfaces, browser validation must cover the real routes in both `de` and `en`, and include dialogs, placeholders, empty states, overflow actions, and longer English labels when relevant.
- Do not mark a substantial UI run complete until the screenshot pass is clean for the in-scope surfaces.
- If a UI request specifies exact footer order, inline placement, label wording, or screenshot-backed corrections, implement and validate that exact arrangement rather than a nearby interpretation.
- For template/CSS/page-JS changes that affect visible order or labels, add or update focused tests and QA checks that assert the exact order and wording rendered on the affected surface.
- If browser output disagrees with the latest code or tests, verify the active runtime listener and live HTML before treating the discrepancy as resolved.
- Use `PROMAT_RUNTIME_ROOT` and `PROMAT_PUBLIC_ROOT` as the only runtime boundaries.
- Keep Teaching separate from Research inside `app/`: no research-auth gate, protected player route, owner-bound state, or `data/` lookup belongs on Teaching pages.
- Resolve Teaching editorial files only from `content/teaching/...` or `PROMAT_TEACHING_CONTENT_ROOT`, and resolve released Teaching media only from `PROMAT_PUBLIC_ROOT/teaching/...`.
- Do not access `secure/` from web-facing runtime code.
- Do not serve public content directly from `data/`.

## No-Go

- No new German technical slugs.
- No shadow docs inside `app/` for active architecture or product rules.