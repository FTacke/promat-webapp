# PROMAT App Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` für Arbeiten innerhalb von `app/`.

## Scope

- `src/app/` enthält die Flask-Anwendung und das Runtime-Wiring.
- `templates/` und `static/` bilden das UI-System.

## Regeln

- Implement application behavior against `docs/spec/`, not against older local notes or deleted doc paths.
- If routing, research-access behavior, IDs, vocabularies, or runtime boundaries change, update the relevant file in `docs/spec/` in the same run.
- If shared app-shell or sidebar-navigation rules change, update `docs/spec/platform-data-files.md` in the same run.
- If a shared layout element changes on a real page and `sample` showcases it, update `templates/pages/sample_page.html` in the same run.
- Before adding new template, CSS, or page-JS patterns, inspect the relevant productive templates, shared partials, and shared CSS families first.
- Reuse or extend existing UI families before creating page-local variants for buttons, form controls, badges or chips, cards or list rows, dialogs, empty states, sticky anchors, or overflow actions.
- For research UI, use `comparison` as the main reference for step containers, selection blocks, badge or meta rhythm, and linear work sequences; use `player` as the main reference for dense material rows, compact work heads, sticky anchors, and muted versus active row states.
- Prefer calm, linear flows and keep overview surfaces distinct from editor or detail surfaces; avoid extra mini-overlabels or parallel work islands unless the active spec calls for them.
- Changes to `20_layout.css`, `30_components.css`, `40_cards.css`, or shared partials require regression checks on at least one unaffected page using the same family.
- Substantial UI changes require browser validation and screenshots, not only code review or pytest.
- Use `PROMAT_RUNTIME_ROOT` and `PROMAT_PUBLIC_ROOT` as the only runtime boundaries.
- Do not access `secure/` from web-facing runtime code.
- Do not serve public content directly from `data/`.

## No-Go

- No new German technical slugs.
- No shadow docs inside `app/` for active architecture or product rules.