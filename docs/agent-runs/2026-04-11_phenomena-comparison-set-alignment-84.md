# Phenomena Comparison Set Alignment 84

Datum: 2026-04-11

## Ziel

Die erneute systemische Überarbeitung von `phenomena` mit der noch offenen Comparison-Anbindung abschließen: letzte Overview-Reste entfernen, Overflow stärker an bestehende UI-Familien anbinden, saved custom sets in `comparison` auswählbar machen und den sichtbaren Setzustand im Comparison-Select schon aus dem angefragten `set_id` korrekt vorbelegen.

## Consulted Sources

- `docs/spec/research-access.md`
- `docs/runbooks/ui-change-workflow.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_views.py`
- `app/static/js/pages/research-comparison.js`
- `app/templates/pages/research_phenomena_overview.html`
- `app/static/js/pages/research-phenomena-overview.js`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`
- `app/tests/test_research_phenomena.py`

## Geänderte Bereiche

- Comparison-Setquelle und Vergleichs-Select-Logik
- Phenomena-Overview-Filter und Overflow-Wiederverwendung
- aktive Research-Spec für sichtbare Comparison-Setoptionen
- fokussierte Comparison-/Phenomena-Regressionen

## Wichtige Entscheidungen

- Der sichtbare Comparison-Select bleibt ein kompakter Text-Select statt einer neuen badgeartigen Sonderkomponente; kuratiert vs. custom wird deshalb über klare Optionslabels wie `Starter · curated` und `Mein Fokusset · custom` ausgewiesen.
- Saved custom sets werden serverseitig direkt in dieselbe `materialPresets`-Quelle eingespeist wie kuratierte Sets; es gibt keinen zweiten parallelen Custom-Optionspfad.
- Wenn `comparison` bereits mit einem owner-bound `set_id` geöffnet wird, spiegelt der Select diese Setwahl sofort aus `requestedSetId`, statt erst auf den späteren API-Fetch zu warten.
- Das Custom-Overflow in der Phenomena-Overview verwendet jetzt die bestehende `pm-comparison-more-filters`-Familie statt einer rein featurelokalen Menüpräsentation.

## Abweichungen

- Keine Abweichung von der aktiven Spec.
- Die isolierte Browser-QA für `comparison` lief weiterhin ohne echte owner-bound JWT-API-Session; dadurch erscheint im Screenshot ein `UNAUTHORIZED`-Hinweis im Arbeitsblock, obwohl der Select korrekt `Mein Fokusset · custom` vorbelegt und damit die neue Setoption visuell prüfbar bleibt.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py tests/test_research_phenomena.py`
  - Ergebnis: `15 passed`
- Isolierte Headless-Edge-Browser-QA mit Mini-Research-App und Screenshots unter `tmp/ui-qa/phenomena-comparison-alignment-84/`
- Sichtprüfung der Screenshots auf:
  - ruhige Overview ohne Preview-Zeile
  - Comparison-nahe Overflow-Präsentation für Custom-Sets
  - Editor-Workhead und Saved-State unverändert ruhig
  - sichtbare Vorbelegung `Mein Fokusset · custom` im Comparison-Select

## Screenshots

- `tmp/ui-qa/phenomena-comparison-alignment-84/overview-auth-list.png`
- `tmp/ui-qa/phenomena-comparison-alignment-84/overview-auth-custom-actions.png`
- `tmp/ui-qa/phenomena-comparison-alignment-84/editor-saved-state.png`
- `tmp/ui-qa/phenomena-comparison-alignment-84/comparison-custom-set-selected.png`

## Offene Punkte

- Die sichtbaren Statuswörter `curated` und `custom` bleiben weiterhin bewusst technische Kurzlabels; wenn dafür produktive deutsche Copy gewünscht ist, sollte das als eigener zentraler Copy-Pass erfolgen.
- Für eine voll realistische Comparison-Liveprüfung mit ausbleibendem `UNAUTHORIZED`-Hinweis wäre zusätzlich eine echte owner-bound JWT-Session im Browser-Setup nötig.

## Nächste sinnvolle Schritte

- Falls gewünscht, im nächsten Pass nur noch die sichtbare Badge-Copy `curated` / `custom` zentral auf endgültige deutsche Arbeitsbegriffe umstellen.