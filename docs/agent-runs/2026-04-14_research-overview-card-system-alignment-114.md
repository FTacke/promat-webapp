# Research Overview Card System Alignment 114

Datum: 2026-04-14

## Ziel

Die Korpus-Karten auf der Research-Übersichtsseite gestalterisch in das bestehende Card-System der Webapp integrieren: keine Sonderlösung mehr, sondern klare Anlehnung an Speaker-Cards mit fester Struktur aus Titel, Primärblock, Sekundärblock und Footer-CTA.

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
- Produktive Referenzflächen geprüft: `app/templates/partials/_research_speaker_card.html`, `app/templates/pages/research_player.html`, `app/templates/pages/research_speaker_profile.html`, `app/static/css/40_cards.css`, `app/static/css/30_components.css`, `app/static/css/10_typography.css`, `app/static/css/20_layout.css`

## Geänderte Bereiche

- Gemeinsames Corpus-Card-Rendering unter `app/templates/partials/_corpus_card.html`
- Research- und Sample-Seiten unter `app/templates/pages/promat_page.html` und `app/templates/pages/sample_page.html`
- Research-Corpus-Card-Modifier in `app/src/app/routes/public_content.py`
- Bestehende Karten-Styles in `app/static/css/40_cards.css` und `app/static/css/10_typography.css`
- Fokus-Regressionen in `app/tests/test_research_sessions.py`
- Bindende Gestaltungsregeln in `docs/spec/platform-data-files.md` und `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Die Research-Karten verwenden jetzt dieselbe Grundmaterialität wie Speaker-Cards: `pm-card`, dieselbe Accent-Bar-Logik, dieselben Divider-Abstände und denselben ruhigen Footer-Abschluss.
- Für Primärinformationen wurden keine neuen Meta-Textstile eingeführt; stattdessen werden `pm-speaker-card__meta-item`, `pm-speaker-card__meta-label` und `pm-speaker-card__meta-value` in einer einspaltigen, längenzeilensicheren Research-Card-Variante wiederverwendet.
- Der Footer-CTA nutzt die bestehende Inline-Action-Familie `pm-research-inline-action pm-research-inline-action--compact pm-research-inline-action--secondary` statt einer neuen CTA-Sonderlösung.
- Die Research-Karten behalten ihre eigene Inhaltslogik, übernehmen aber bewusst die Speaker-Card-Segmentierung: Header, erster Divider-Block für Primärdaten, zweiter Divider-Block für Statusdaten und abgesetzter Footer.
- Für die Farbkante werden bestehende Sprach-Modifikatoren `pm-card--lang-*` mitgenutzt, sodass die Karten auch innerhalb der übrigen Corpus-Card-Familie anschlussfähig bleiben.

## Abweichungen

- Keine Abweichung von der neuen aktiven Gestaltungsregel.
- Es wurde bewusst keine mehrspaltige Speaker-Card-Metadatenanordnung kopiert; die Research-Karten nutzen eine einspaltige Variante derselben Komponentenfamilie, damit längere Namen und Statuszeilen ruhig umbrechen.

## Verifikation

- Editor-Fehlerprüfung für die geänderten Templates, CSS-Dateien und Python-Datei: ohne neue relevante Fehler; verbleibende Browser-Kompatibilitätsmeldungen in `10_typography.css` sind vorbestehende Hinweise außerhalb dieses Scopes.
- Fokussierter Pytest-Lauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "test_research_overview_renders_structured_corpus_metadata_and_dynamic_counts or test_research_overview_localizes_structured_corpus_cards_in_english or test_sample_page_reflects_current_landing_and_corpus_cards"`
  - Ergebnis: `3 passed`
- Live-HTML-Prüfung gegen lokale Instanz `http://127.0.0.1:8010` für `/de/research` und `/en/research`
  - geprüft: Titel, Primärblock, Sekundärblock, Footer-CTA, dynamische Statuszeilen
- Browser-Öffnung der realen Overview-Routen in `de` und `en` auf der lokalen Instanz durchgeführt.

## Offene Punkte

- Die Research-Karten sind jetzt systemisch an Speaker-Cards angebunden. Falls Teaching-Corpus-Karten später ähnlich stark segmentiert werden sollen, sollte dieselbe gemeinsame Partial weiterverwendet oder erweitert werden statt eine dritte Corpus-Card-Sprache einzuführen.
- Ein vollständiger visueller Screenshot-Vergleich war mit den verfügbaren Browser-Werkzeugen in diesem Run nicht automatisiert auslesbar; die Live-HTML- und Browser-Prüfung wurde dennoch durchgeführt.

## Nächste sinnvolle Schritte

- Falls gewünscht, die Teaching-Korpus-Karten im nächsten Schritt auf dieselbe gemeinsame Partial-Basis konsolidieren, sofern ihre Inhaltsdichte steigt.
- Den bestehenden Player-/Research-Sets-Testfehler separat beheben, damit `app/tests/test_research_sessions.py` wieder als kompletter Voll-Lauf nutzbar ist.