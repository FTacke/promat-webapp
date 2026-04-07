# Wordlist Player Remove Fallback And Control Polish

Datum: 2026-04-07

## Ziel

Den bestehenden produktiven `wordlist`-Player in zwei engen Punkten korrigieren: den Geschwindigkeitswert im globalen Wiedergabebereich von einer Pille auf eine einfache Textanzeige zurücknehmen, den Playbutton tiefer an die Seekbar-Achse bringen und den Fehler beheben, dass `Vergleich entfernen` den Compare-Bereich ausblendet, ohne sofort zu einer sichtbaren Single-Liste zurückzukehren.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-player.js`
- `app/tests/test_research_sessions.py`
- `app/scripts/dev-start.ps1`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-player.js`
- `app/tests/test_research_sessions.py`

## Wichtige Entscheidungen

- Der Geschwindigkeitswert bleibt technisch dieselbe Live-Anzeige, wird aber visuell wie die Lautstärke als ruhiger Text gelesen statt als separate Pille.
- Der Playbutton wird nicht größer oder kleiner gemacht, sondern tiefer an den unteren Transportabschluss gekoppelt, damit er näher an der Seekbar-Mitte sitzt.
- `Vergleich entfernen` wird im compare-bereiten Zustand serverseitig als echter Link zur Single-View-Route gerendert; die bestehende JS-Navigation bleibt zusätzlich als Fallback. So hängt das Zurückschalten nicht mehr daran, dass im Compare-DOM bereits eine Single-Liste vorhanden ist.

## Abweichungen

- Keine Abweichung von aktiven Routing-, Runtime- oder Datenraumregeln.
- Keine Spezifikationsänderung nötig; der Run korrigiert Umsetzung und Interaktionsrobustheit innerhalb des bestehenden `wordlist`-Player-Vertrags.

## Verifikation

- VS-Code-Problems-Check für `research_views.py`, `research_player.html`, `30_components.css`, `research-player.js` und `test_research_sessions.py` ohne Fehler.
- `Set-Location c:/dev/promat/app; ../.venv/Scripts/python.exe -m pytest tests/test_research_sessions.py -q` → `32 passed`
- Zusätzliche Assertions decken jetzt ab, dass der compare-bereite Karten-Action-Pfad eine echte Single-View-`href` enthält.
- Lokaler Dev-Server auf Port `8000` explizit neu gestartet, damit Live-Prüfungen nicht auf einem veralteten Template-Stand laufen.
- Live-Single-HTML gegen den frisch gestarteten Dev-Server bestätigt weiterhin die aktualisierten Player-Marker wie `pm-player-list--single`, `data-player-rate-value` und `pm-player-control-bar__block--transport`.

## Offene Punkte

- Der compare-bereite Live-Request gegen den neu gestarteten lokalen Dev-Server lieferte in dieser Validierungsrunde keinen compare-aktiven HTML-Zustand zurück, obwohl die serverseitigen Compare-Tests weiter grün sind; die Funktionsabsicherung dieses Runs stützt sich daher primär auf den erweiterten Server-Test und den robusten direkten Remove-Link.

## Nächste sinnvolle Schritte

- Falls gewünscht, den compare-bereiten Live-Datenpfad gegen die aktuelle lokale Datengrundlage separat nachziehen, damit auch der Browser-Smoke-Test wieder gegen echte Dev-Daten läuft.