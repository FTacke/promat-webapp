# Speaker And Player Neutral Meta Cards

Datum: 2026-04-15

## Ziel

Die neutrale Kartenlogik fuer Research-Speaker-Cards konsequent zu Ende fuehren: Learner-Uebersichtskarten ohne Rest-Top-Bar und mit gestraffter Faktorauswahl, Player-Metakarten ebenfalls ohne farbigen Card-Chrome, und Badge-Inhalte systemweit klar als UI-Meta in UI-Schrift statt Buchschrift.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/runbooks/ui-change-workflow.md`
- `app/src/app/research_views.py`
- `app/src/app/routes/public.py`
- `app/templates/partials/_research_speaker_card.html`
- `app/templates/pages/research_player.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`

## Geaenderte Bereiche

- Learner-Speaker-Card-Builder fuer die reduzierte Uebersichtsmetadaten-Auswahl
- Player-Summary-Card-Builder fuer neutrale Container und explizite Badge-Payloads
- Shared Badge-CSS fuer UI-Font-Typografie auf Research-/Comparison-/Player-Badges
- Speaker-Card- und Player-Card-Template fuer dieselbe Badge-Renderlogik
- Sample-Spiegel, aktive Specs und Browser-QA-Artefakte

## Wichtige Entscheidungen

- Learner-Speaker-Cards zeigen in der Uebersicht nur noch Level-Badge, `L1`, Geschlecht und Sprachaufenthalte; `Sessions` und `Aufnahmejahre` wurden entfernt.
- Der dekorative neutrale Restbalken auf Learner-Karten wurde entfernt; Native-Speaker-Overview-Cards duerfen ihre eigene Teal-Top-Bar als Sprechergruppen-Semantik behalten.
- Player-Metakarten sind jetzt fuer Lernende und Native Speaker gleichermassen neutrale Container; Rolle, Sprechergruppe, Level, Varietaet und `L1` sitzen ausschliesslich auf Badges oder Pills innerhalb der Karte.
- Badge-Inhalte bleiben systemisch UI-Meta und werden deshalb auf der UI-Font-Familie gehalten, auch wenn benachbarte Wort- oder Satzinhalte in Buchschrift stehen.

## Abweichungen

- Keine fachliche Abweichung von der aktiven Spec. `docs/spec/platform-data-files.md` und `docs/spec/research-player.md` wurden im selben Run auf die neue neutrale Badge-Logik angehoben.

## Verifikation

- `get_errors` auf den geaenderten Python-, Template-, CSS- und Test-Dateien: keine relevanten Fehler
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "sample_speaker_cards_keep_focused_learner_meta_selection or speakers_page_uses_neutral_learner_cards_with_level_badges or player_page_builds_material_bar_and_footer_actions or player_route_uses_neutral_meta_cards_and_shared_badges"`: `4 passed`
- `Run research sessions tests`: `150 passed`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_comparison.py -q`: `9 passed`
- Browser-QA gegen `http://127.0.0.1:8000` nach expliziter Listener-Bereinigung auf Port `8000`:
  - `de/research/spanish/speakers` und `en/research/spanish/speakers`: Learner-Karten ohne Rest-Top-Bar, ohne `Sessions`/`Aufnahmejahre`, mit Level-Badge plus Geschlecht
  - `de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings`: neutrale Learner-Metakarte mit Badges `Lernende`, Level und `L1`
  - `de/research/spanish/player/ES-N-0001-2026-S01/wordlist?source=recordings`: neutrale Native-Metakarte mit Badges fuer Sprechergruppe, Varietaet und Herkunft
  - `de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings&compare_session=ES-N-0001-2026-S01`: zwei neutrale Player-Metakarten mit Badge-basierter Rollen- und Sprechersemantik
  - mobile Gegenpruefung fuer `de/research/spanish/speakers` und denselben compare-faehigen Player-Pfad
- Screenshot- und Text-Artefakte liegen unter `tmp/ui-qa/2026-04-15-speaker-player-neutral-cards-109/`

## Offene Punkte

- Keine in-scope offenen UI-Punkte. Die finalen Browser-Artefakte wurden nach einem stale Listener auf Port `8000` erneut erzeugt, damit die Live-HTML dem aktuellen Code entspricht.