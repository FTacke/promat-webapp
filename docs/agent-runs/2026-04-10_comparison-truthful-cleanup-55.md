# Comparison fachlich bereinigt und Top-Bar-Menü entklebt

Datum: 2026-04-10

## Ziel

Die nach dem letzten Comparison-Feinschliff noch irreführenden sichtbaren Set-/Preset-Signale entfernen, die Oberfläche fachlich wahr und ruhiger machen, die Matrixsemantik schärfen und den sticky-open Fehler des angemeldeten Top-Bar-Kontomenüs robust beheben.

## Consulted Sources

- `docs/spec/research-access.md`
- `docs/spec/platform-data-files.md`
- `docs/agent-runs/2026-04-10_comparison-speaker-centered-refinement-53.md`
- `docs/agent-runs/2026-04-10_comparison-final-sharpening-54.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_comparison.html`
- `app/templates/partials/_top_app_bar.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/js/modules/navigation/app-bar.js`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/js/modules/navigation/app-bar.js`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`
- `docs/spec/research-access.md`
- `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- `comparison` zeigt keine sichtbare Save-as-Aktion mehr und tut auch nicht mehr so, als würde Material-/Preset-Konfiguration dort selbst stattfinden; dafür bleibt nur die ehrliche Materialzusammenfassung plus leiser Handoff nach `phenomena`.
- Die Materialzusammenfassung liest jetzt `Alle Items` oder `Ganzer Text` statt vorheriger Set-/Preset-Sprache; kuratierte Materialien bleiben intern erhalten, lesen aber sichtbar als `Auswahl aus Phänomene` statt als lokal konfigurierbarer Preset-State.
- Die Levelchips sind jetzt fachlich auf die sichtbare Auswahl reduziert: `A1`, `A2`, `B1`, `B2`, `Native`; `C1` verschwindet aus der Standardfilterzeile.
- Native-Standardvarietäten werden nicht mehr roh oder intern abgekürzt exponiert, sondern über ein zentrales Mapping in sprechende deutsche/englische Labels übersetzt.
- In der Matrix ist die Sekundäraktion jetzt ein direkter MP3-Download statt eines Player-/Open-Icons, weil die zugrunde liegende Route eine Download-Route ist.
- Das Top-Bar-Kontomenü verwendet jetzt eine einzige robuste State-Synchronisation für `hidden`, `data-open` und `aria-expanded`, schließt beim Init explizit und räumt auf bei Outside-Click, `Escape`, Re-Click und Navigation.

## Abweichungen

- Keine Abweichung von Routefamilie, Set-Architektur, Datenräumen oder dem item-centered / speaker-first Modell.
- Der signed-in Top-Bar-Menüzweig konnte lokal nicht mit echtem Login browserseitig durchgeklickt werden, weil in diesem Run keine verlässlichen lokalen Zugangsdaten vorlagen; die Korrektur wurde deshalb über Root-Cause-Codefix plus anonymen Live-Lauf des frischen Servers abgesichert.

## Verifikation

- VS-Code-Fehlerprüfung für die geänderten Python-, JS-, CSS-, Template-, Test- und Spec-Dateien: ohne neue Fehler.
- Research-Regressionslauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py tests/test_research_phenomena.py tests/test_research_sets.py tests/test_research_player_set_context.py`
  - Ergebnis: `45 passed`.
- Anonymer Selenium-Livecheck gegen frische isolierte App-Instanz auf `http://127.0.0.1:8001/de/research/spanish/comparison`:
  - Step-Badges `1`, `2`, `3` vorhanden
  - `Native`-Chip vorhanden
  - `C1`-Chip nicht vorhanden
  - erste `L1`-Option liest `L1 wählen`
  - Materialzusammenfassung liest `Alle Items`
  - kein `data-comparison-material-preset-select`
  - kein sichtbarer Text `Als neues Set speichern`
  - sichtbarer Handoff `In Phänomene anpassen`
- Zusätzlicher Payload-Check gegen dieselbe frische Instanz:
  - `labels.itemsTitle == "Item"`
  - `labels.downloadClip == "MP3 laden"`
  - Native-Testeintrag liest `speakerTypeLabel == "Native"`
  - Native-Standardvarietät wird aus Realwert `es_std` zu `Spanien` übersetzt

## Offene Punkte

- Für eine echte Browser-End-to-End-Bestätigung des signed-in Top-Bar-Menüs fehlt noch ein reproduzierbarer lokaler Login-Flow oder dokumentierte Dev-Credentials.
- Die badge-basierte Matrixkopf- und Download-Semantik ist code- und payloadseitig umgestellt, aber mangels Owner-Login noch nicht mit ausgewählten Sprecher:innen live im Browser durchgeklickt.

## Nächste sinnvolle Schritte

- Einen kleinen Selenium-Owner-Flow ergänzen: Login, Kontomenü öffnen/schließen, `comparison` mit Sprecher:in-Auswahl, Matrix-Download anklicken.
- Falls weitere reale Standardvarietätscodes in die Daten kommen, das neue Mapping in `research_views.py` gezielt erweitern statt Rohkürzel durchzureichen.