# Player Fix Validation 97

Datum: 2026-04-12

## Ziel

Einen gezielten Korrekturlauf für den produktiven Research Player abschließen: Footer-Aktionsreihenfolge sauber halten, die Materialleiste kompakter und auf Desktop belastbar einzeilig machen, die sichtbare Set-Liste mit Comparison und Phenomena konsistent halten, spürbare Voll-Reloads bei Player-internen Wechseln reduzieren und die reale Dev-Runtime auf `127.0.0.1:8000` mit Browser-QA in `de` und `en` verifizieren.

## Consulted Sources

- `docs/spec/research-player.md`
- `docs/spec/research-access.md`
- `docs/spec/platform-data-files.md`
- `docs/runbooks/ui-change-workflow.md`
- `docs/agent-runs/2026-04-12_material-strip-followup-94.md`
- `docs/agent-runs/2026-04-12_player-set-alignment-96.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- `app/src/app/research_views.py`
- `app/src/app/research_sets.py`
- `app/src/app/research_phenomena_views.py`
- `app/src/app/routes/research_api.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/30_components.css`

## Geänderte Bereiche

- Query-Erhalt für textgebundene Set-Wechsel in `app/src/app/research_views.py`
- In-Place-Navigation und lokales Compare-Close im produktiven Player in `app/static/js/pages/research-player.js`
- Materialleisten- und Pending-State-Polish in `app/static/css/30_components.css`
- Regression für `render_mode`-Erhalt in `app/tests/test_research_player_set_context.py`
- Wiederholbarer Live-QA-Capture samt Artefakten unter `tmp/ui-qa/2026-04-12-player-fix-97/`

## Wichtige Entscheidungen

- Die verbleibende wahrgenommene Trägheit wurde nicht mit zusätzlicher Spezial-API bekämpft, sondern durch in-place HTML-Swaps für Player-interne Navigation auf derselben Route-Familie.
- Compare-Remove bleibt im produktiven Player lokal und löst keinen erzwungenen Shell-Reload mehr aus.
- Der Player-Set-Wechsel für `text` muss den aktiven `render_mode` behalten, damit die View nicht beim Set-Wechsel implizit zurückspringt.
- Die sichtbare Set-Konsistenz bleibt an der bestehenden shared saved-only-Workbench-Logik aus Run 96 gebunden; dieser Lauf ändert die Regel nicht, sondern validiert sie erneut auf der realen Dev-Runtime.
- Maßgeblich für die Runtime-Wahrheit auf Windows blieb der bereinigte Einzellistener auf Port `8000` plus Live-HTML- und Browserprüfung, nicht allein die angezeigte Python-Pfadform in der Prozessliste.

## Abweichungen

- Keine Abweichung von der aktiven Player-, Access- oder Plattform-Spec.
- Für die Browser-QA wurden auf der realen Dev-Datenbank ein gespeichertes QA-Set und ein versteckter Draft angelegt; sie dienten ausschließlich der Live-Verifikation.
- Der QA-Capture unter `tmp/ui-qa/2026-04-12-player-fix-97/` wurde während des Laufs zweimal nachgeschärft, weil erst ein verbliebener echter Compare-Reload und danach ein zu strenges Wait-Kriterium im Skript sichtbar wurden.

## Verifikation

- Editor-Fehlerprüfung der geänderten produktiven Dateien: keine relevanten Fehler.
- Fokussierter Pytest-Lauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_player_set_context.py tests/test_research_sessions.py -q`
  - Ergebnis: `64 passed`
- Laufzeitbereinigung auf `127.0.0.1:8000`:
  - konkurrierende PROMAT-Python-Prozesse identifiziert und beendet
  - Dev-Stack anschließend kanonisch über `scripts/dev-start.ps1` neu gestartet
  - `http://127.0.0.1:8000/health` erfolgreich geprüft
  - Live-HTML auf Player-Route auf aktuelle Marker geprüft
- Headless-Edge-Browser-QA gegen reale Routen in `de` und `en` erfolgreich durchgeführt für:
  - `/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings`
  - `/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings`
  - `/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings&set_id=<saved_set_id>`
  - `/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings&compare_session=ES-L-0003-2027-S02`
  - `/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings&compare_session=ES-L-0003-2027-S02`
  - `/de/research/spanish/comparison`
  - `/en/research/spanish/comparison`
  - `/de/research/spanish/phenomena`
  - `/en/research/spanish/phenomena`
- Die Browser-QA verifiziert explizit:
  - Footer-Reihenfolge im primären Player-Card-Footer: Compare-Add vor Profile
  - gespeichertes QA-Set sichtbar, versteckter Draft unsichtbar
  - Set-Wechsel bleibt im selben Fensterzustand ohne Voll-Reload
  - Compare-Entry bleibt im selben Fensterzustand ohne Voll-Reload
  - Compare-Remove bleibt im selben Fensterzustand ohne Voll-Reload
- Finale Artefakte unter `tmp/ui-qa/2026-04-12-player-fix-97/`:
  - `player_de.png`
  - `player_set_de.png`
  - `player_compare_de.png`
  - `player_en.png`
  - `player_compare_en.png`
  - `comparison_de.png`
  - `comparison_en.png`
  - `phenomena_de.png`
  - `phenomena_en.png`
  - `metrics.json`
- Browserbefund laut `metrics.json`:
  - Player `de/en` listet nur `Alle Items` beziehungsweise `All items` plus `QA Player Fix 97 Saved`
  - Comparison `de/en` listet das Saved Set als `QA Player Fix 97 Saved · custom`
  - Phenomena `de/en` zeigt das Saved Set, den versteckten Draft aber nicht
  - Marker für Set-Wechsel, Compare-Entry und Compare-Remove bleiben jeweils im selben Window-Kontext erhalten

## Offene Punkte

- Die Windows-GPU-Warnung von Edge im Headless-Lauf blieb rein infrastrukturell und hatte keinen sichtbaren Einfluss auf die QA-Ergebnisse.
- Der QA-Capture ist auf die aktuell verwendeten QA-Labels und Login-Credentials zugeschnitten; künftige Läufe sollten eigene QA-Labels verwenden statt diese Artefakte fortzuschreiben.

## Nächste sinnvolle Schritte

- Bei der nächsten substanziellen Player-Interaktionsänderung denselben QA-Capture direkt wieder gegen `127.0.0.1:8000` laufen lassen, damit Voll-Reload-Regressionspfade sofort auffallen.
- Falls weitere Player-interne Wechselpfade dazukommen, sie an dieselbe in-place Navigation binden statt parallel wieder `window.location.assign(...)` einzuführen.