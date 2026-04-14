# Research Overview Corpus Card Metadata 113

Datum: 2026-04-14

## Ziel

Die Korpus-Karten auf der Research-Übersichtsseite `/{ui_lang}/research` verbindlich von generischen Fließtexten auf eine knappe, einheitliche Metadatenstruktur umstellen: Projektleitung, Durchführung, Materialkonzeption, optional Referenzaufnahmen ab zwei Standardvarietäten sowie dynamischer Lernendenstatus oder `Korpus im Aufbau`.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md` (geprüft, in diesem Run unverändert belassen)
- `docs/spec/intake-workbook.md` (geprüft, in diesem Run unverändert belassen)
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/runbooks/ui-change-workflow.md`
- Runtime-Wiring geprüft: `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `docker-compose.dev-postgres.yml`, `app/infra/docker-compose.prod.yml`
- Repo-Memory geprüft: `/memories/repo/promat-research-ui-notes.md`
- Betroffene produktive und Spiegel-Flächen geprüft: `app/templates/pages/promat_page.html`, `app/templates/pages/sample_page.html`, `app/static/css/10_typography.css`, `app/static/css/40_cards.css`

## Geänderte Bereiche

- Zentrale Research-Übersichtsdaten und Kartendynamik in `app/src/app/routes/public_content.py`
- Sichtbare Übersetzungen für `de` und `en` in `app/src/app/i18n.py`
- Gemeinsames Karten-Rendering in `app/templates/pages/promat_page.html`
- Sample-Mirror in `app/templates/pages/sample_page.html`
- Kleine Erweiterungen der bestehenden Karten-Typografie und -Abstände in `app/static/css/10_typography.css` und `app/static/css/40_cards.css`
- Fokussierte Regressionen in `app/tests/test_research_sessions.py`
- Bindende UI-Regeln in `docs/spec/platform-data-files.md` und `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Die Research-Kartenlogik wurde zentral im Content-Builder gebündelt statt im Template verzweigt zu werden. Das Template rendert nur noch generische Metadatenzeilen.
- Die Lernenden-Zahl wird nicht mehr als Session-Zahl, sondern als Anzahl eindeutiger Lernenden-Personen (`person_id`) aus den vorhandenen Lernerdaten ermittelt.
- Die Referenzzeile wird ausschließlich aus der Anzahl unterschiedlicher `standard_variety`-Werte bei `native_speaker`-Einträgen abgeleitet und erst ab `>= 2` sichtbar.
- Die Research-Introzeile auf `/{ui_lang}/research` wurde auf eine kurze Orientierungszeile ohne technische oder interne Begriffe reduziert.
- `sample` wurde im selben Run mitgezogen, weil die geänderte Forschungskarte dort repräsentiert ist.

## Abweichungen

- Keine Abweichung von der neuen aktiven Kartenregel auf der Research-Übersichtsseite.
- Der vollständige Lauf `app/tests/test_research_sessions.py` ist im aktuellen Repo durch einen bestehenden, nicht von diesem Run verursachten Player-/Research-Sets-Fehler blockiert: `NameError: ResearchSetStorageUnavailableError` in `app/src/app/research_views.py` bei mehreren Player-Tests.

## Verifikation

- Editor-Fehlerprüfung für die geänderten Python-, Template-, CSS- und Spec-Dateien: ohne neue relevante Fehler; verbleibende CSS-Kompatibilitätsmeldungen in `10_typography.css` sind vorbestehende Hinweise außerhalb dieses Changes.
- Fokussierter Pytest-Lauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "test_research_overview_renders_structured_corpus_metadata_and_dynamic_counts or test_research_overview_localizes_structured_corpus_cards_in_english or test_sample_page_reflects_current_landing_and_corpus_cards"`
  - Ergebnis: `3 passed`
- Zusätzlicher Voll-Lauf der Datei `app/tests/test_research_sessions.py` geprüft; neue Overview-Tests bestehen, der Gesamtlauf scheitert weiterhin an bestehenden Player-Fehlern außerhalb des Scopes.
- Live-HTML-Prüfung über lokale Instanz auf `http://127.0.0.1:8010` für:
  - `/de/research`
  - `/en/research`
  - Ergebnis: gekürzte Introzeile, neue Metadatenstruktur, dynamische Lernendenzahl, Referenzzeile nur für Spanisch sichtbar.
- Integrierter Browser für `de` und `en` der Research-Übersicht geöffnet.

## Offene Punkte

- Für eine erneut vollständige Grünabnahme von `app/tests/test_research_sessions.py` muss der bestehende Player-/Research-Sets-Fehler in `app/src/app/research_views.py` separat behoben werden.
- Falls sich der Live-Datenstand in `data/sessions/` ändert, ändern sich die Lernenden- und Referenzzeilen auf der Übersichtsseite bewusst dynamisch mit.

## Nächste sinnvolle Schritte

- Den bestehenden `ResearchSetStorageUnavailableError`-Import-/Exception-Pfad im Player separat reparieren, damit der gesamte `test_research_sessions.py`-Lauf wieder als Vollregression nutzbar ist.
- Wenn weitere Research-Übersichtsregeln dazukommen, dieselbe Kartenfamilie in `public_content.py` und den beiden aktiven Specs fortführen statt neue Template-Sonderfälle einzuführen.