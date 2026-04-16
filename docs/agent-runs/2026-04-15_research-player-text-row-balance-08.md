# Research Player Text Row Balance

Datum: 2026-04-15

## Ziel

Die Satzlistenansicht des produktiven Players nach der Buchtypografie-Umstellung vertikal nachschaerfen, damit ID-Badge, Satztext, Zeitangabe und Download wieder als ruhige, ausgewogene Zeile zusammenwirken.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/research-player.md`
- `docs/runbooks/ui-change-workflow.md`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/templates/pages/research_player.html`
- `app/tests/test_research_sessions.py`

## Geaenderte Bereiche

- Text-spezifische Player-List-Geometrie in `app/static/css/30_components.css`
- aktive Player-Spec fuer die optisch balancierte Satzlisten-Zeile

## Wichtige Entscheidungen

- Die Satzlistenansicht bleibt auf einer top-ausgerichteten Zeilenlogik, aber die einzelnen Teilbereiche wurden optisch und nicht nur mathematisch nachjustiert.
- Das linke ID-Badge wurde fuer `text` proportional vergroessert, statt die Satzschrift wieder zu verkleinern.
- Zeitangabe und Download wurden leicht zur Satzachse nachgezogen, damit die Buchschrift im Textcontainer die Metaspalte nicht optisch nach oben kippen laesst.
- Die Wordlist-Zeilen wurden nicht auf dieselbe Textgeometrie umgestellt; die Feinkorrektur bleibt auf `pm-player-list--text` begrenzt.

## Abweichungen

- Keine Abweichung von aktiver Spec; die bestehende Satzlisten-Regel wurde praezisiert.

## Verifikation

- `get_errors` auf `app/static/css/30_components.css`: keine Fehler
- `Run research sessions tests`: `148 passed`
- Live-HTML-Pruefung gegen die laufende App unter `http://127.0.0.1:8000` nach Login mit dem Dev-Admin:
  - `de/research/spanish/player/ES-L-0001-2026-S01/text?source=recordings&render_mode=sentence_list`: `200`, Text-Row-Klassen, Zeit-Meta und Download-Button vorhanden
  - `de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings`: `200`, keine Text-Row-Klasse im Wordlist-Markup, Download-Button weiterhin vorhanden

## Offene Punkte

- Es wurde die laufende Runtime geprueft, aber in diesem Run kein archivierter Screenshot-Satz fuer Desktop und mobil abgelegt.

## Naechste sinnvolle Schritte

- Falls fuer diese Zeilenfeinjustierung ein visueller Abnahmestand benoetigt wird, die Text-Satzliste mit ein- und mehrzeiligen Items sowie die Wordlist-Gegenprobe noch als Screenshot-Satz unter `tmp/ui-qa/` festhalten