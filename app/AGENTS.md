# PROMAT App Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` für Arbeiten innerhalb von `app/`.

## Scope

- `src/app/` enthält die Flask-Anwendung und das Runtime-Wiring.
- `templates/` und `static/` bilden das UI-System.

## Regeln

- Implement application behavior against `docs/spec/`, not against older local notes or deleted doc paths.
- If routing, research-access behavior, IDs, vocabularies, or runtime boundaries change, update the relevant file in `docs/spec/` in the same run.
- Use `PROMAT_RUNTIME_ROOT` and `PROMAT_PUBLIC_ROOT` as the only runtime boundaries.
- Do not access `secure/` from web-facing runtime code.
- Do not serve public content directly from `data/`.

## No-Go

- No new German technical slugs.
- No shadow docs inside `app/` for active architecture or product rules.