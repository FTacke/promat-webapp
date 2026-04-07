# Wordlist Compare Layout Rework

Datum: 2026-04-06

## Ziel

Den bestehenden produktiven `wordlist`-Player-Compare-Modus strukturell neu ordnen: eine gemeinsame volle Kontrollleiste, kompakte Speaker-Karten darunter und eine horizontale Vollbreiten-Vergleichsliste ohne beengte Kartenoptik.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `app/templates/pages/research_player.html`
- `app/src/app/research_views.py`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`
- `docs/spec/research-player.md`

## Wichtige Entscheidungen

- Compare bleibt Teil desselben Players und bekommt keine zweite Oberflächenlogik.
- Universelle Transport- und Download-Aktionen werden visuell icon-only geführt; Zugänglichkeit bleibt über `aria-label` und `title` erhalten.
- Compare bleibt auf Desktop beschränkt; kleinere Viewports fallen bewusst auf die Primäransicht zurück.
- Die aktiven Speed-Stufen werden auf `0.5` bis `1.5` begrenzt.
- Die Metadatenkarten übernehmen ihre Rahmenfarbe direkt aus derselben Session-Akzentlogik wie die bestehende `border-top`-Kodierung der Speaker-/Session-Karten.
- Die finale Control-Bar verzichtet auf eingebettete Zurück-/Profil-Navigation und konzentriert sich auf Sessionwahl, Compare-Modus und Transport; die Seitenrücknavigation sitzt oberhalb des Players, Profil-Links direkt in den Metadatenkarten.
- Die Player-Metadaten bleiben bewusst listening-relevant; `Explorator:in` wurde aus der Player-Karte entfernt.

## Abweichungen

- Keine Abweichung von Spezifikation, Routing oder Runtime-Grenzen.

## Verifikation

- Template-Struktur nach der Reparatur gegen Restduplikate geprüft.
- Player-Tests für Compare-Markup und Rate-Liste ergänzt.
- Mehrere lokale Screenshot-Pässe gegen den laufenden Dev-Server ausgewertet:
	- `tmp/ui-qa/player-compare-pass1/`
	- `tmp/ui-qa/player-compare-pass2/`
	- `tmp/ui-qa/player-compare-pass3/`
	- `tmp/ui-qa/player-compare-pass4/`
	- `tmp/ui-qa/player-compare-pass5/`
- Dabei wurde ein Responsive-Bug identifiziert und behoben: `pm-player-compare-desktop` wurde auf schmalen Breiten durch spätere `display:grid`-Regeln wieder eingeblendet und wird nun explizit ausgeblendet.
- Zusätzlich wurde ein lokaler Validierungsfehler im Arbeitsablauf bereinigt: Nach Python-Änderungen musste der Dev-Server ohne ReLoader hart neu gestartet werden, damit Screenshots nicht weiter alten View-State zeigten.
- Problems-Check für die geänderten Template- und CSS-Dateien ausgeführt.
- `pytest app/tests/test_research_sessions.py`

## Offene Punkte

- Keine akuten offenen Punkte; weitere Feintypografie oder Mikroabstände wären nur noch optionales Polishing.

## Nächste sinnvolle Schritte

- Compare-Verhalten einmal manuell im Browser auf Desktop und kleiner Breite gegen das neue Layout prüfen.
- Bei späterem `text`-Player-Ausbau die gleiche horizontale Compare-Sprache nur dann übernehmen, wenn sie zur Satzlistenstruktur passt.