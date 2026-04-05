# Breadcrumb Depth Rule And Spanish Research Followup

Datum: 2026-04-02

## Ziel

Die Breadcrumb-Logik systemweit auf eine einheitliche Tiefenregel umstellen, die spanische Forschungs-Landingpage als echte Orientierungsseite ausbauen und die spanische Designseite textlich straffen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- `app/src/app/content_navigation.py`
- `app/src/app/routes/public.py`
- `app/src/app/research_views.py`
- `app/src/app/routes/public_content.py`
- `app/templates/partials/_content_header.html`
- `app/static/css/20_layout.css`
- `app/tests/test_research_sessions.py`
- `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- Breadcrumbs werden nicht mehr pro Seite ad hoc zusammengesetzt, sondern über einen gemeinsamen Hierarchie-Helfer erzeugt.
- Tiefe 2 bleibt auf Mobile sichtbar, wird auf Desktop aber bewusst unterdrückt, weil dort Sidebar und Bereichskontext bereits Orientierung liefern.
- Die spanische Forschungs-Landingpage benennt jetzt alle vorgesehenen Zugänge des Sprachbereichs statt nur Design sowie die zwei aktuell stärksten Arbeitseinstiege.

## Abweichungen

- Keine Abweichung von der aktiven Spezifikation; die neue Breadcrumb-Regel wurde im selben Run in die zentrale Spezifikation aufgenommen.

## Verifikation

- Render- und View-Regressionen in `app/tests/test_research_sessions.py`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sessions.py` → `24 passed`

## Offene Punkte

- Die Sichtbarkeitsregel zwischen Mobile und Desktop wird derzeit über CSS am bestehenden Breakpoint umgesetzt; falls der Shell-Breakpoint später geändert wird, muss diese Kopplung mitgeführt werden.

## Nächste sinnvolle Schritte

- Breadcrumb-Regressionen bei weiteren Detailseiten ergänzen, falls neue tiefere Routen außerhalb des Forschungsbereichs hinzukommen.