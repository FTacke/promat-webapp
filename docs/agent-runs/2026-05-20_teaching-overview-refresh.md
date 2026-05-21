# Teaching-Übersichtsseiten überarbeitet und mobile Teaching-Header bereinigt

Datum: 2026-05-20

## Ziel

Die öffentliche Teaching-Startseite unter `/{ui_lang}/teaching` und die nachgelagerte Spanisch-Hubseite unter `/{ui_lang}/teaching/spanish` gestalterisch ruhiger und weniger trocken überarbeiten, dabei die bestehende neue Teaching-Themenseiten-Sprache weiterführen, Pending-Themen technisch sauber abbilden und Desktop- sowie Mobile-QA auf den realen Routen abschließen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `docs/AGENTS.md`
- `app/AGENTS.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- Teaching-Strings und Builder in `app/src/app/i18n.py`, `app/src/app/routes/public_content.py` und `app/src/app/teaching_content.py`
- gemeinsame Teaching-Templates in `app/templates/pages/teaching_page.html`, `app/templates/partials/_teaching_blocks.html` und `app/templates/pages/sample_page.html`
- Teaching-Layout und Komponenten in `app/static/css/20_layout.css` und `app/static/css/30_components.css`
- spanische Teaching-Indexinhalte in `content/teaching/spanish/de/index.yaml` und `content/teaching/spanish/en/index.yaml`
- fokussierte Regressionen in `app/tests/test_teaching_content.py` und `app/tests/test_research_sessions.py`
- aktive Plattform-Spec in `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- Die Root-Auswahl und die Sprach-Hubseiten bleiben innerhalb der bestehenden Teaching-UI-Familien; es wurde kein neues Karten- oder Hero-System eingeführt.
- Hub-Themen ohne vorhandene Topic-Datei gelten jetzt bewusst als geplante Einträge: Sie werden als Pending-Karten gerendert, ohne Linkziel und ohne Fokusziel.
- Die ruhige Orientierung unter dem Header ist jetzt sowohl auf der Root-Auswahl als auch auf Hubseiten ein explizit unterstützter Bestandteil der Teaching-Oberfläche.
- Der verbleibende Mobile-Overflow wurde nicht über globales Overflow-Clipping gelöst, sondern durch schmalere echte Mobile-Spalten für Hub- und Topic-Header sowie für den Topic-Body-Container.

## Abweichungen

- Keine Abweichung von den aktiven Public-Teaching-, Routing- oder App-Shell-Regeln.
- Kein Research-Auth-, Datenpfad- oder Sidebar-Verhalten wurde in Teaching eingeführt.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q -k "build_teaching_hub_page"` -> 4 bestanden
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_overview_keeps_language_selection_label or teaching_language_root_uses_shared_topbar_and_mobile_drawer or teaching_english_hub_stays_within_english_edition_topics"` -> 3 bestanden
- Editor-Diagnostik auf den geänderten Python-Dateien: keine Fehler in `app/tests/test_research_sessions.py`, `app/src/app/teaching_content.py`, `app/src/app/routes/public_content.py`, `app/src/app/i18n.py`
- Reale Browser-QA auf `http://127.0.0.1:8010` mit Headless Edge bei 390 px Breite für:
  - `/de/teaching`
  - `/de/teaching/spanish`
  - `/de/teaching/spanish/which-pronunciation`
- Desktop-Screenshots und Mobile-Artefakte liegen unter `tmp/ui-qa/2026-05-20-teaching-overviews/`

## Offene Punkte

- Headless-Edge-Artefakte decken jeweils den sichtbaren Viewport ab; für tiefer gescrollte Hub-Bereiche gibt es in diesem Run keinen separaten Full-Page-Mobile-Capture.
- Die betroffenen Kartensysteme wurden jedoch auf Root und Hub in Desktop sowie auf den mobilen Header- und Topic-Slices der realen Routen geprüft.

## Nächste sinnvolle Schritte

- Bei einer nächsten Teaching-QA-Runde einen wiederverwendbaren Full-Page-Mobile-Capture unter `scripts/qa/` ergänzen, damit lange öffentliche Teaching-Seiten ohne Anker-Workarounds vollständig abgenommen werden können.
- Wenn weitere geplante Hub-Themen ergänzt werden, denselben Pending-Kartenpfad weiterverwenden statt leere Topic-Dateien anzulegen.
