# Bilinguale UI-Infrastruktur, erste produktive Welle

Datum: 2026-04-11

## Ziel

Eine zentrale bilinguale UI-Grundlage für PROMAT produktiv einziehen, ohne die gesamte Webapp sofort vollständig englisch auszurollen. Die erste Welle sollte Shared Shell plus die produktiven Bereiche `phenomena`, `comparison` und `player` sauber auf `de` und `en` vorbereiten.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- Root `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- Zentrale UI-Übersetzungen in `app/src/app/i18n.py`
- Template- und Shell-Wiring in `app/src/app/__init__.py`, `app/src/app/routes/public_content.py`, `app/templates/base.html`, `app/templates/partials/_top_app_bar.html`, `app/templates/partials/_navigation_drawer.html`, `app/static/js/theme-toggle.js`
- Produktive erste Welle in `app/src/app/research_phenomena_views.py`, `app/src/app/research_views.py`, den zugehörigen Templates und Page-JS-Dateien für `phenomena`, `comparison` und `player`
- Bilinguale Tests in `app/tests/test_research_phenomena.py`, `app/tests/test_research_comparison.py`, `app/tests/test_research_sessions.py`
- Normative Governance-Regel in `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- Es gibt jetzt eine gemeinsame zentrale Übersetzungsschicht mit einem aktiven Katalog für `de` und `en`; sichtbare UI-Texte für die erste Welle werden nicht mehr parallel in Python, Templates und JS gepflegt.
- Jinja nutzt einen gemeinsamen `t(...)`-Helper; Page-JS bekommt lokalisierte Labels über serverseitigen State statt sichtbare Fallback-Texte lokal zu besitzen.
- Die erste produktive Welle bleibt bewusst auf Shared Shell, `phenomena`, `comparison` und `player` begrenzt; andere Forschungsseiten wurden in diesem Run nicht vollständig migriert.
- Player-Tests wurden nicht abgeschwächt, sondern an die aktuelle Runtime-Realität angepasst: die Fixture seeded jetzt die minimal nötige `research_player`-Konfiguration.

## Abweichungen

- Keine Abweichung bei Routing, Runtime-Grenzen oder Datenräumen.
- Keine Browser-Screenshots in diesem Run; die Verifikation lief code- und testseitig. Das bleibt gegenüber der UI-Governance ein offener Nachzug.

## Verifikation

- Rest-Suchläufe auf verbleibende sichtbare `de`/`en`-Branches und harte JS-Fallbacks in den migrierten Bereichen
- Fehlerprüfung der geänderten Python-, JS-, Test- und Spec-Dateien über den Editor-Fehlercheck
- Pytest:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_phenomena.py tests/test_research_comparison.py tests/test_research_sessions.py`
  - Ergebnis: `52 passed`
- Zusätzliche EN-Coverage für produktive erste Welle:
  - `phenomena` Overview + Editor
  - `comparison` Workspace-Labels
  - `player` Wordlist-Surface

## Offene Punkte

- Die übrigen Forschungsseiten (`speakers`, `recordings`, Profilflächen und weitere Hilfsfunktionen in `research_views.py`) enthalten weiterhin sichtbare Sprachlogik außerhalb dieser ersten Welle.
- Ein echter Browser-Pass mit Screenshots für `de` und `en` auf laufender App-Instanz steht noch aus.
- Weitere zukünftige UI-Arbeit muss die neue Spec-Regel aktiv befolgen, damit keine neuen sichtbaren Strings wieder verstreut entstehen.

## Nächste sinnvolle Schritte

- Browser-Validierung mit Screenshots für die migrierten Oberflächen in `de` und `en` nachziehen.
- Die nächste UI-Welle auf `recordings`, `speakers` und Profilseiten erweitern.
- Verbleibende ältere `ui_lang`-Verzweigungen in `app/src/app/research_views.py` schrittweise in den zentralen Katalog überführen.