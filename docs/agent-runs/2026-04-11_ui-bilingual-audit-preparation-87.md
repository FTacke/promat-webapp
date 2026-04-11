# UI Bilingual Audit Preparation 87

Datum: 2026-04-11

## Ziel

Einen kompakten, aber systematischen Audit-Run zur Vorbereitung einer späteren zweisprachigen UI-Migration (`de`/`en`) im PROMAT-Webapp-Repo durchführen: aktuelle Textquellen inventarisieren, bestehende Sprach- und Routingmechanismen prüfen, Architektur- und Migrationsvorschläge formulieren und zentrale Risiken benennen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/runbooks/ui-change-workflow.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/__init__.py`
- `app/src/app/routes/public.py`
- `app/src/app/routes/public_content.py`
- `app/src/app/research_views.py`
- `app/src/app/research_phenomena_views.py`
- `app/src/app/research_sessions.py`
- `app/src/app/research_sets.py`
- `app/src/app/routes/auth.py`
- `app/templates/base.html`
- `app/templates/partials/_top_app_bar.html`
- `app/templates/partials/_navigation_drawer.html`
- repräsentative Templates unter `app/templates/auth/` und `app/templates/pages/`
- repräsentative Client-Dateien unter `app/static/js/auth/` und `app/static/js/pages/`

## Geänderte Bereiche

- neuer nicht-normativer Audit-Run-Log unter `docs/agent-runs/`
- keine produktiven Code-, Spec- oder UI-Änderungen in diesem Lauf

## Wichtige Entscheidungen

- Der Audit bleibt bewusst bei Befund, Zielarchitektur, Priorisierung und QA-Strategie; es wurde keine halbierte i18n-Implementierung begonnen.
- Die bestehende kleine `TEXTS`-Struktur in `app/src/app/routes/public_content.py` wird als sinnvoller Startpunkt bewertet, aber nicht als ausreichende Endarchitektur für eine echte Repo-weite de/en-Lokalisierung.
- Für die spätere Umsetzung sollte die Migration an der Shell und an geteilten Label-Quellen beginnen, bevor einzelne Research-Workbenches oder Auth-/Admin-Flows umgestellt werden.
- Technische Werte, Slugs und Routen bleiben Englisch/ASCII; sichtbar gerenderte Labels müssen konsequent davon getrennt werden.

## Abweichungen

- Der Audit hat eine relevante Ist-Abweichung zwischen Spec und Runtime sichtbar gemacht: `docs/spec/platform-data-files.md` führt `ui_lang` aktiv als `de`, `en`, während `app/src/app/routes/public_content.py` aktuell nur `SUPPORTED_UI_LANGUAGES = ("de",)` freischaltet.
- Darüber hinaus wurden keine neuen Abweichungen eingeführt, da dieser Lauf rein analysierend war.

## Verifikation

- gezielte Datei-Lektüre der aktiven Governance-, Spec-, Routing-, Template-, Python- und JS-Bereiche
- repoweite Suchläufe nach `ui_lang`, inline `if ui_lang == "de"`, möglichen i18n-Framework-Spuren sowie sprachspezifischen JS-Datumsformaten
- Abgleich der gefundenen Muster mit bestehenden Repo-Regeln und Research-UI-Konventionen

## Offene Punkte

- Vor einer großen Umsetzung muss entschieden werden, ob PROMAT bei einer internen Python/Jinja-Übersetzungsquelle bleibt oder bewusst auf ein echtes i18n-Framework umstellt.
- Für Auth-/Admin-Flows ist noch offen, wie serverseitige Flash- und Validierungsnachrichten sprachstabil an die UI gekoppelt werden sollen.
- Für Client-JS ist noch offen, ob Seiten ausschließlich serverinjizierte Label-Payloads erhalten oder zusätzlich einen gemeinsamen clientseitigen Übersetzungs-Lookup nutzen sollen.

## Nächste sinnvolle Schritte

- Den Auditbericht als Grundlage für einen großen Umsetzungs-Prompt oder ein phasenweises Arbeitsprogramm verwenden.
- Vor Implementierungsstart die Zielarchitektur für Übersetzungsquellen, Key-Struktur und JS-Anbindung verbindlich festlegen.
- In der ersten Umsetzungsphase Shell, geteilte Partial-Texte und zentrale Label-Registries vorziehen, erst danach Workbench-spezifische Tiefenbereiche migrieren.