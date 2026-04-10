# Comparison als erste Arbeitsseite geschärft

Datum: 2026-04-09

## Ziel

`comparison` als ruhige erste Arbeitsseite verdichten: drei dominante Schritte `Material wählen`, `Sprecher:innen auswählen`, `Matrix`, weniger sichtbare Set-/Draft-Sprache, kompaktere Aktionen, harte Prüfung des Audio-Fehlers und ehrliche lokale Verifikation.

## Consulted Sources

- `docs/plans/player_comparison_phenomena.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/spec/platform-data-files.md`
- `AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/routes/public.py`
- `app/src/app/research_views.py`
- `app/static/js/modules/auth/refresh.js`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`
- `docs/agent-runs/2026-04-09_research-comparison-workbench-45.md`
- `docs/agent-runs/2026-04-09_research-player-set-context-46.md`
- `docs/agent-runs/2026-04-09_research-player-text-renderer-47.md`
- `docs/agent-runs/2026-04-09_research-player-text-compare-48.md`
- `docs/agent-runs/2026-04-09_research-set-save-workflow-49.md`
- `docs/agent-runs/2026-04-09_local-research-set-bootstrap-50.md`
- `docs/agent-runs/2026-04-09_comparison-simplification-51.md`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`
- `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Die sichtbare `comparison`-Fläche wird noch konsequenter als Drei-Schritt-Flow gelesen: Material oben, Sprecher:innen-Auswahl in zwei leisen Spalten, Matrix als dominante Arbeitsfläche.
- Die Materialsteuerung bleibt kompakt: `Wortliste` als Standard, `Satzliste` sekundär, `In Phänomene konfigurieren` als bewusster Handoff statt zweitem Editor auf `comparison`.
- Matrix-Aktionen bleiben icon-basiert und klein; Text-CTAs wurden nicht wieder aufgeblasen.
- Horizontales Matrix-Scrolling bleibt auf die Matrixfläche begrenzt; Stub-Spalte und Session-Header bleiben sticky.
- Die Audio-Ursache wurde nicht als Browser-Problem behandelt, sondern als Daten-/Eligibility-Problem: unbrauchbare Split-Clips, insbesondere 0-Byte-Dateien, dürfen nicht als abspielbar exponiert werden.
- Die Umlaut-Regel blieb bindend über die bestehenden Repo-/`.github`-Instruktionen; sichtbare neue deutsche Labels wurden daran ausgerichtet, ein weiterer Governance-Patch war in diesem Run nicht nötig.

## Entfernt oder reduziert

- Prominente Draft-/Set-Zustandssprache wurde weiter zurückgenommen.
- Die zweite Hauptstufe liest nun sichtbar als `Sprecher:innen auswählen` statt als architekturförmige Session-Verwaltung.
- Gruppenüberschriften wurden auf `Verfügbar` und `Ausgewählt` verkürzt.
- Die Matrix liest nun sichtbar nur noch als `Matrix` statt als schwerere Arbeitsblock-Benennung.

## Audio-Bug: Ursache und Fix

- Im Workspace existierten reale ungültige Split-Artefakte, darunter 0-Byte-MP3-Dateien.
- Die Workbench darf Dateiexistenz allein deshalb nicht als Abspielbarkeit interpretieren.
- Die serverseitige Vergleichs-/Bundle-Auflösung filtert unbrauchbare Split-Artefakte jetzt aus der sichtbaren Verfügbarkeit heraus.
- Die Client-Wiedergabe prüft Audioantworten härter und behandelt leere oder nicht-audiofähige Antworten nicht mehr als normale Clips.
- Eine Regression deckt jetzt explizit ab, dass ein 0-Byte-Split-Clip weder in `comparison` als verfügbar auftaucht noch über die Item-MP3-Route ausgeliefert wird.

## Abweichungen

- Keine Abweichung von Routefamilie, Set-Modell oder Storage-Architektur.
- Browserseitige Live-Klickpfade für Session-Hinzufügen/Entfernen und Materialwechsel konnten in diesem Run nicht vollautomatisiert geprüft werden, weil im Chat keine Browser-Automation mit DOM-Interaktion verfügbar war.

## Verifikation

- VS-Code-Fehlerprüfung für die geänderten Python-, HTML-, JS-, CSS-, Test- und Spec-Dateien: ohne neue Fehler.
- Gezielter Research-Regressionslauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py tests/test_research_phenomena.py tests/test_research_sets.py tests/test_research_player_set_context.py`
  - Ergebnis: `44 passed`.
- Nach der finalen sichtbaren Headline-Korrektur zusätzlicher Regressionstest:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py`
  - Ergebnis: `5 passed`.
- Lokale Live-Prüfung mit laufender App auf `http://127.0.0.1:8000`:
  - HTML-Response `200`.
  - ausgelieferte Comparison-HTML enthält `data-comparison-material-controls`, `data-comparison-matrix-wrap` und sichtbar die drei Schritte `Material wählen`, `Sprecher:innen auswählen`, `Matrix`.
  - reale Clip-Route `/{ui_lang}/research/spanish/player/ES-L-0003-2027-S02/wordlist/items/wl_001.mp3` antwortet mit `200`, `audio/mpeg`, `Content-Length: 27927`.
- Ehrliche Grenze:
  - horizontales Matrix-Scrolling wurde strukturell über Markup/CSS und die echte ausgelieferte Matrix-Wrapper-Struktur geprüft, aber nicht per gesteuerter Browser-Geste.
  - Session-Hinzufügen/Entfernen und Materialwechsel wurden über Codepfad und Regression abgesichert, nicht als vollständiger live-geklickter DOM-Flow.

## Offene Punkte

- Die unauthentische Erstansicht ist jetzt klarer, bleibt aber naturgemäß eingeschränkt; der echte Owner-Flow sollte später einmal browserseitig mit Login und DOM-Interaktion end-to-end geprüft werden.
- `phenomena` kann als nächster Schritt noch stärker auf kompakte Material-Kuration verdichtet werden, damit der Handoff nach `comparison` genauso ruhig wirkt wie die jetzige Vergleichsseite.

## Nächste sinnvolle Schritte

- `phenomena` als reine Material-Kurationsfläche weiter verdichten: weniger generische Workspace-Sprache, schnellere Preset-Einstiege, klarere aktive Auswahl.
- Später einen echten browsergesteuerten Owner-E2E-Check für `comparison` nachziehen: Login, Session hinzufügen/entfernen, Material umschalten, Save-as, Matrix-Scroll.