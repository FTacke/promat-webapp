# Comparison sprecherzentriert verdichtet

Datum: 2026-04-10

## Ziel

`comparison` sichtbarer von interner Set-/Session-Logik lösen und als ruhige, platzsparende, sprecherzentrierte Drei-Schritt-Arbeitsfläche schärfen: `Material wählen`, `Sprecher:innen auswählen`, `Matrix`.

## Consulted Sources

- `docs/spec/research-access.md`
- `docs/agent-runs/2026-04-09_comparison-first-workflow-52.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`
- `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Die sichtbare zweite Stufe der Workbench wird jetzt konsequent als Sprecher:innen-Auswahl gelesen, obwohl intern weiter Sessions gespeichert und mutiert werden.
- Die verfügbare Auswahl rendert als dichte Sprecher:innen-Zeilen mit `person_id` als Primärzeile; `speaker group`, Niveau und `L1` bleiben als ruhige Badges sekundär.
- Der sichtbare Filterstandard wurde auf `Suche`, direkte Niveau-Chips und `L1` reduziert; `Geschlecht` und `Sprachaufenthalt` wandern in `Weitere Filter`.
- Die Materialstufe bleibt kompakt und zeigt nur Materialwahl, materialabhängige Kurz-Zusammenfassung und den sekundären Handoff `Phänomene wählen`.
- Nach Screenshot-Prüfung wurden die Sprecher:innen-Zeilen weiter verdichtet, die leere rechte Auswahlspalte nicht mehr unnötig in die Höhe gestreckt und `Zurücksetzen` ohne aktive Filter hart ausgeblendet.

## Abweichungen

- Keine Abweichung von Routefamilie, Set-Architektur oder Sticky-Matrix-Grundlogik.
- Die Live-Prüfung erfolgte als echter gerenderter Browser-Screenshot, aber nicht als vollautomatisierte DOM-Klicksequenz mit Login und Session-Auswahl.

## Verifikation

- VS-Code-Fehlerprüfung für die geänderten JS-, CSS-, Template-, Python- und Spec-Dateien: ohne neue Fehler.
- Research-Regressionslauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py tests/test_research_phenomena.py tests/test_research_sets.py tests/test_research_player_set_context.py`
  - Ergebnis: `44 passed`.
- Finaler fokussierter Vergleichstest nach den screenshot-getriebenen CSS-/JS-Nachzügen:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py`
  - Ergebnis: `5 passed`.
- Lokale Live-Prüfung mit explizit gestarteter App auf `http://127.0.0.1:8000` über `c:/dev/promat/.venv/Scripts/python.exe -m src.app.main`.
- Headless-Browser-Screenshots erstellt und geprüft:
  - `c:/dev/promat/tmp/comparison-speaker-ui.png`
  - `c:/dev/promat/tmp/comparison-speaker-ui-v2.png`
- Sichtbar verifiziert:
  - `Was vergleichen?`
  - kompakte Filterzeile mit `Suche`, Niveau-Chips, `L1`, `Weitere Filter`
  - dichte Sprecher:innen-Reihen statt großer Session-Karten
  - `Verfügbar` / `Ausgewählt`
  - `Matrix` als dritte Hauptstufe

## Offene Punkte

- Die unauthentische Erstansicht bleibt bewusst ein eingeschränkter Startzustand; die eigentliche Auswahlinteraktion sollte später mit echtem Owner-Login browserseitig end-to-end geprüft werden.
- Die Sprecher:innen-Liste ist jetzt deutlich dichter, kann aber bei sehr großen Katalogen später noch um serverseitige oder virtuelle Ergebnisbegrenzung ergänzt werden, falls Performance oder Scrollgefühl das verlangen.

## Nächste sinnvolle Schritte

- Einen echten browsergesteuerten Owner-E2E-Check für `comparison` ergänzen: Login, Sprecher:in hinzufügen/entfernen, Filter setzen, Material wechseln, Save-as.
- `phenomena` weiter auf denselben ruhigen Materialfluss verdichten, damit der Handoff zwischen beiden Flächen noch konsistenter wird.