# Research Player System Cleanup

Datum: 2026-04-15

## Ziel

Die bereits umgesetzten Auth-, Player-, Comparison- und Research-Navigationsflaechen gezielt bereinigen, auf gemeinsame Systemregeln zurueckziehen und die letzten Inkonsistenzen bei CTA-Platzierung, Download-Intent, Korpustiteln, Typografie und Textfluss beseitigen.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/runbooks/ui-change-workflow.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `app/templates/auth/access_request.html`
- `app/templates/pages/research_player.html`
- `app/templates/pages/research_comparison.html`
- `app/static/css/00_tokens.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/static/js/pages/research-comparison.js`
- `app/src/app/routes/public.py`
- `app/src/app/research_player_runtime.py`
- `app/src/app/research_views.py`
- `app/src/app/research_phenomena_views.py`
- `app/tests/test_auth_phase1.py`
- `app/tests/test_research_sessions.py`
- `app/tests/test_research_phenomena.py`

## Geaenderte Bereiche

- Access-Request-Formular und zugehoerige Auth-Regressionen
- geschuetzte Research-Kontexttitel fuer Player, Speaker-Profile und Phaenomene
- Player- und Comparison-Item-Rendering fuer expliziten Download-Intent und gemeinsame Inhaltstypografie
- gemeinsame Tokens und Komponenten-CSS fuer Checkboxen, Lernlevel-Farben und Textfluss
- aktive Player-Spec fuer die neuen systemischen Regeln

## Wichtige Entscheidungen

- Linguistischer Item-Inhalt wird systemisch von UI-Metadaten getrennt: Inhaltstext nutzt die Buchtypografie, waehrend Zaehlungen, Timings, Toggles und sonstige Steuer- oder Metadaten in der UI-Schrift bleiben.
- Single-item-Playback und Single-item-Download bleiben derselbe geschuetzte Routenstamm, aber mit getrenntem Intent: Inline-URLs fuer Wiedergabe, expliziter Download-Intent fuer Attachment-Downloads.
- Running-Text bleibt ein ruhiger Lesemodus; versteckte Download-Aktionen duerfen den Textfluss deshalb nicht mehr durch reservierte Layoutbreite fragmentieren.
- Die Research-Seitenleiste auf geschuetzten Sprachkontext-Seiten folgt konsequent dem vollen lokalisierten Korpustitel statt der nackten Sprachbezeichnung.

## Abweichungen

- Keine Abweichung von aktiver Spezifikation oder Dev/Prod-Paritaet. Die Run-Aenderungen ziehen bestehende produktive Regeln enger zusammen und dokumentieren sie expliziter in der Player-Spec.

## Verifikation

- Diagnostik auf allen geaenderten Python-, Template-, JS-, CSS- und Testdateien; nach dem letzten CSS-Nachzug ohne relevante neue Fehler
- `Run auth phase tests`: `22 passed`
- `Run research sessions tests`: `147 passed`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py app/tests/test_research_comparison.py -q`: `20 passed`
- lokaler Health-Check gegen `http://127.0.0.1:8000/health`: `200`, Status `healthy`
- Live-Gate-Check gegen `http://127.0.0.1:8000/de/research/spanish/player/ES-L-0001-2026-S01/text?source=recordings` ohne Login: `302` auf `/login?next=...`
- Live-Pruefung der oeffentlichen Access-Request-Seite nach Runtime-Neustart:
	- `de`: `200`, genau ein Login-Link fuer den Return-Target-Kontext, Submit-CTA vorhanden
	- `en`: `200`, genau ein Login-Link fuer den Return-Target-Kontext, Submit-CTA vorhanden
- Live-Pruefung der authentifizierten Realrouten nach Login mit dem Dev-Admin `felix.tacke@uni-marburg.de`:
	- `de/research/spanish/player/.../text?source=recordings`: `200`, `Spanisch-Korpus`, `?download=1` und `download`-Attribut vorhanden
	- `en/research/english/player/.../text?source=recordings`: `200`, `English corpus`, `?download=1` und `download`-Attribut vorhanden
	- `de/research/spanish/phenomena`: `200`, `Spanisch-Korpus` vorhanden
	- `en/research/spanish/phenomena`: `200`, `Spanish corpus` vorhanden
	- `de/research/spanish/comparison`: `200`, `Spanisch-Korpus` vorhanden
- Stale-Runtime-Abgleich gemaess Runbook durchgefuehrt: der zuerst aktive Listener auf Port `8000` lieferte veraltete HTML-Staende; nach gezieltem Kill des alten Prozesses und Neustart ueber `scripts/dev-start.ps1` stimmten Live-HTML und Teststand wieder ueberein

## Offene Punkte

- Es wurden Live-HTML- und Runtime-Pruefungen auf den echten Routen durchgefuehrt, aber in diesem Run keine Browser-Screenshot-Artefakte unter `tmp/ui-qa/` archiviert.

## Naechste sinnvolle Schritte

- Falls fuer diesen UI-Block ein formaler visueller Abnahmestand benoetigt wird, die bereits live geprueften Realrouten noch als Screenshot-Satz unter `tmp/ui-qa/` archivieren