# Comparison Schritt 1 zu kompaktem Item-und-Set-Block vereinfacht

Datum: 2026-04-10

## Ziel

Den ersten Comparison-Schritt nach der fachlichen Bereinigung noch einmal sichtbar vereinfachen: `Was vergleichen?` durch `Items auswählen` ersetzen, die rechte Material-Nebenfläche zurückbauen, Materialwahl plus Set-Auswahl zu einem kompakten Block zusammenziehen und alle sichtbaren Login-Hinweise innerhalb von `comparison` entfernen.

## Consulted Sources

- `docs/spec/research-access.md`
- `docs/spec/platform-data-files.md`
- `docs/agent-runs/2026-04-10_comparison-truthful-cleanup-55.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`
- `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Schritt 1 liest jetzt parallel zu den anderen Stufen als `Items auswählen` statt `Was vergleichen?`; die sichtbare Struktur bleibt bei genau einer Headline mit Kreisbadge.
- Die frühere rechte Material-Nebenfläche wurde entfernt; Schritt 1 besteht jetzt aus Material-Toggles plus einem benachbarten sekundären Block `Set wählen` mit kleinem Info-Popover.
- Der frühere Handoff-Button nach `phenomena` wurde nicht ersetzt; statt dessen erklärt nur das Info-Popover ruhig, dass Sets unter `phenomena` erstellt und angepasst werden.
- Alle sichtbaren Login-Hinweise innerhalb der Comparison-Fläche wurden entfernt; die Seite verhält sich sichtbar so, als sei der Zugang bereits vorgeschaltet geklärt.
- Die bestehende Set-Logik blieb technisch erhalten und wurde nur anders gelesen: das frühere interne Select rendert jetzt als kompakter Set-Block statt als rechte Nebeninsel oder Preset-Sprache.

## Abweichungen

- Keine Abweichung von Routefamilie, Set-API, Player-Familie oder dem item-centered / speaker-first Modell.
- Die aktuelle Route bleibt technisch weiter öffentlich renderbar; geändert wurde in diesem Run nur die sichtbare Surface-Logik, nicht die vorgeschaltete spätere Login-Sheet-Architektur.

## Verifikation

- VS-Code-Fehlerprüfung für die geänderten Python-, JS-, CSS-, Template-, Test- und Spec-Dateien: ohne neue Fehler.
- Fokussierter Comparison-Testlauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py`
  - Ergebnis: `6 passed`.
- Selenium-Livecheck gegen frische isolierte Instanz auf `http://127.0.0.1:8002/de/research/spanish/comparison`:
  - sichtbare Stufentitel: `1 Items auswählen`, `2 Sprecher:innen auswählen`, `3 Matrix`
  - Materialoptionen `Wortliste`, `Satzliste` vorhanden
  - benachbarter Block `Set wählen` vorhanden
  - Info-Popovertext sichtbar: `Sets lassen sich unter „Phänomene“ individuell erstellen und anpassen.`
  - keine frühere rechte Summary-Insel (`data-comparison-set-summary` fehlt)
  - kein Handoff-Button (`data-comparison-edit-items` fehlt)
  - kein sichtbarer Comparison-interner Login-Hinweis und kein `Anmelden` innerhalb des Comparison-Roots
- Zusätzlicher EN-Payload-Check über `build_comparison_page(...)`:
  - `materialPrompt == "Select items"`
  - `setSelectLabel == "Choose set"`
  - `setSelectInfoText == "Sets can be created and adjusted individually under “Phenomena”."`

## Offene Punkte

- Ein echter vorgeschalteter Login-Sheet-Flow vor `comparison` existiert weiterhin noch nicht; sichtbar ist der Workbench-Zustand jetzt aber bereits darauf vorbereitet.
- Der Set-Select nutzt weiterhin die bestehende Set-/Materiallogik aus `comparison`; eine spätere eigene owner-gebundene Set-Liste aus `phenomena` wurde in diesem Run bewusst nicht neu erfunden.

## Nächste sinnvolle Schritte

- Den vorgeschalteten Login-Sheet-Flow bauen, damit die jetzt entfernten In-Page-Login-Hinweise auch technisch durch echte Vorab-Abfanglogik ersetzt werden.
- Bei Bedarf einen kleinen Owner-Browserflow ergänzen: Set wählen, Sprecher:innen hinzufügen, Matrix-Download auslösen.