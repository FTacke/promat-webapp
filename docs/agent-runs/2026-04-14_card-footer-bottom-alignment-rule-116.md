# Card Footer Bottom Alignment Rule 116

Datum: 2026-04-14

## Ziel

Die Bottom-Ausrichtung von Action-/Footer-Bereichen als bindende Regel für das gesamte Card-System der Webapp festschreiben und in der gemeinsamen Card-Basis umsetzen, damit sichtbare CTA- oder Footer-Blöcke nicht je nach Inhaltslänge in der Karte wandern.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/static/css/40_cards.css`
- `app/templates/partials/_corpus_card.html`
- `app/templates/partials/_research_speaker_card.html`
- `app/templates/pages/research_player.html`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- Gemeinsame Kartenbasis in `app/static/css/40_cards.css`
- Aktive UI-Regel in `docs/spec/platform-data-files.md`
- Fokussierte Research-/Sample-Regressionen in `app/tests/test_research_sessions.py`

## Wichtige Entscheidungen

- Bottom-Ausrichtung von Card-Aktionsbereichen ist jetzt ausdrücklich eine systemweite Regel und nicht mehr nur eine Research-spezifische Erwartung.
- Die Umsetzung sitzt in der gemeinsamen Card-Basis über direkte Child-Selektoren auf `pm-card__body` für `pm-card__action`, `pm-card__link`, echte `footer`-Elemente sowie die aktuell produktiven Card-Footer-Blöcke.
- Bestehende Card-Familien wie Speaker-Cards, Player-Metadatenkarten und Research-Corpus-Karten bleiben damit in derselben Systemlogik, ohne neue page-lokale Footer-Hacks.

## Abweichungen

- Keine.

## Verifikation

- Fokussierter Testlauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "test_research_overview_renders_structured_corpus_metadata_and_dynamic_counts or test_research_overview_localizes_structured_corpus_cards_in_english or test_sample_page_reflects_current_landing_and_corpus_cards"`
  - Ergebnis: `3 passed`
- CSS- und Strukturprüfung der aktuellen Research-Corpus-Karten, Speaker-Cards und Player-Metadatenkarten gegen die gemeinsame Footer-Logik durchgeführt.

## Offene Punkte

- Wenn künftig weitere Card-Familien mit eigenen Footer-Klassen dazukommen, sollten sie an dieselbe gemeinsame Bottom-Ausrichtungsregel angeschlossen werden statt lokale Ausnahmen einzuführen.

## Nächste sinnvolle Schritte

- Bei künftigen neuen Card-Varianten früh prüfen, ob ihr Action- oder Footer-Bereich bereits über die gemeinsame `pm-card__body`-Regel abgedeckt ist.