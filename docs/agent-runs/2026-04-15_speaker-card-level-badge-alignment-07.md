# Speaker Card Level Badge Alignment

Datum: 2026-04-15

## Ziel

Die Learner-Speaker-Cards auf eine semantisch saubere Level-Darstellung umstellen: neutrale Card-Container ohne levelcodierte Top-Bar, klare Level-Badges am eigentlichen Level-Datenelement und eine bewusste Angleichung an die neutrale Container-Logik der Comparison-Speaker-Rows.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/runbooks/ui-change-workflow.md`
- `app/static/css/00_tokens.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/templates/partials/_research_speaker_card.html`
- `app/templates/pages/research_speakers.html`
- `app/static/js/pages/research-comparison.js`
- `app/src/app/research_views.py`
- `app/src/app/routes/public.py`
- `app/tests/test_research_sessions.py`

## Geaenderte Bereiche

- Speaker-Card-Builder fuer die Trennung von Learner- und Native-Containerlogik
- gemeinsames Badge-System fuer Research-Level-Badges und Comparison-Level-Badges
- Speaker-Card-Template fuer Level-Badges in der bestehenden Level-Meta-Zeile
- Sample-Dummy-Daten und Regressionen fuer die neue Learner-Card-Semantik
- aktive Plattform-Spec fuer die neutrale Learner-Card-Regel

## Wichtige Entscheidungen

- Die Learner-Level-Farbe sitzt nicht mehr auf dem Card-Chrome, sondern nur noch am Level-Datenelement selbst ueber Badges in der bestehenden Level-Zeile.
- Native-Speaker-Cards behalten ihre eigene Teal-Top-Bar, weil diese Sprechergruppe und nicht CEFR-Level kodiert.
- Die Level-Farben wurden als ruhige Mauve-/Plum-Familie neu abgestuft, damit Level-Badges und Comparison-Badges dieselbe semantische Farblogik teilen.
- Die Informationsarchitektur der Speaker-Cards bleibt unveraendert; geaendert wurden nur Container-Neutralitaet und Level-Kennzeichnung.

## Abweichungen

- Keine fachliche Abweichung von aktiver Spec. Die neue Rule wurde direkt in `docs/spec/platform-data-files.md` nachgezogen.

## Verifikation

- `get_errors` auf den geaenderten Python-, Template-, CSS-, Test- und Doku-Dateien: keine relevanten Fehler
- `Run research sessions tests`: `148 passed`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "sample_page_uses_current_research_component_patterns or speakers_page_uses_neutral_learner_cards_with_level_badges"`: `2 passed`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_comparison.py -q`: `9 passed`
- Live-HTML-Pruefung nach Dev-Server-Neustart gegen `http://127.0.0.1:8000`:
  - authentifiziert `de/research/spanish/speakers`: neutrale `pm-speaker-card--learner`, Native `pm-speaker-card--native`, Level-Badges vorhanden, alte `pm-speaker-card--a*`-Klassen nicht mehr im Markup
  - authentifiziert `en/research/spanish/speakers`: neutrale Learner-Container und Level-Badges vorhanden
  - oeffentlich `de/sample`: dieselbe neutrale Learner-Card-Logik und dieselben Level-Badge-Klassen vorhanden
- Stale-Runtime-Pruefung wie im Runbook verlangt: der erste Live-Check zeigte wieder alten HTML-Stand; nach Kill des Listeners auf Port `8000` und Neustart ueber `scripts/dev-start.ps1` stimmte die Live-HTML mit dem aktuellen Code ueberein

## Offene Punkte

- Es wurde Live-HTML gegen die echten Routen geprueft, aber in diesem Run kein archivierter Screenshot-Satz unter `tmp/ui-qa/` erzeugt.

## Naechste sinnvolle Schritte

- Falls ein formaler visueller Abnahmestand benoetigt wird, die geprueften Sprecher:innen- und Sample-Routen noch als Screenshot-Satz fuer Desktop und mobil archivieren