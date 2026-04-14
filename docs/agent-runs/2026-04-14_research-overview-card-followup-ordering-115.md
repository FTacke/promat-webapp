# Research Overview Card Followup Ordering 115

Datum: 2026-04-14

## Ziel

Die letzte Abnahmekorrektur für die Research-Karten auf `/{ui_lang}/research` umsetzen: Footer-CTA konsequent unten halten, Primär- und Sekundärreihenfolge anpassen, CTA-Textfarbe auf neutrale UI-Farbe zurückführen und die Unterzeile unter der Seitenüberschrift entfernen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/runbooks/ui-change-workflow.md`
- `app/templates/partials/_corpus_card.html`
- `app/src/app/routes/public_content.py`
- `app/static/css/40_cards.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- Reihenfolge und Intro-Entfernung in `app/src/app/routes/public_content.py`
- CTA-Farb-Rückbau in `app/static/css/40_cards.css`
- Sample-Spiegelung in `app/templates/pages/sample_page.html`
- Fokussierte Assertions in `app/tests/test_research_sessions.py`
- Aktive Regeln in `docs/spec/platform-data-files.md` und `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Die Research-Overview rendert keine Intro-/Unterzeile mehr; die Seite bleibt bei der reinen Überschrift.
- Die Primärdaten der Korpus-Karten folgen jetzt verbindlich der Reihenfolge Projektleitung, Materialkonzeption, Durchführung.
- Die Sekundärdaten folgen jetzt verbindlich der Reihenfolge Lernendenstatus bzw. `Korpus im Aufbau`, danach optional Referenzaufnahmen.
- Der CTA bleibt auf der bestehenden `pm-research-inline-action--secondary`-Familie und verzichtet auf sprachfarbige Textakzente.

## Abweichungen

- Keine Abweichung in der Implementierung.
- Die laufende lokale Instanz auf `127.0.0.1:8000` zeigte beim Check zunächst stale HTML mit der alten Unterzeile und alten Reihenfolge. Die aktuelle Codefassung wurde deshalb zusätzlich auf einer frischen lokalen Instanz unter `127.0.0.1:8010` geprüft.

## Verifikation

- Fokussierter Pytest-Lauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "test_research_overview_renders_structured_corpus_metadata_and_dynamic_counts or test_research_overview_localizes_structured_corpus_cards_in_english or test_sample_page_reflects_current_landing_and_corpus_cards"`
  - Ergebnis: `3 passed`
- Direkter HTML-Check auf frischer Runtime `http://127.0.0.1:8010/de/research`
  - bestätigt: keine Unterzeile unter der Seitenüberschrift
  - bestätigt: Projektleitung -> Materialkonzeption -> Durchführung
  - bestätigt: Aufnahmen von X Lernenden -> Referenzaufnahmen
  - bestätigt: Footer-CTA weiter auf neutraler Secondary-Action-Familie

## Offene Punkte

- Für die produktive lokale Abnahme auf `8000` muss die stale Runtime neu gestartet werden, damit der aktuelle Code sichtbar wird.

## Nächste sinnvolle Schritte

- Falls die `8000`-Instanz weiterhin genutzt wird, den Dev-Server sauber neu starten und den aktuellen Stand dort gegenprüfen.