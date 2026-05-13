# Deutsche Feinkorrektur für which-pronunciation

Datum: 2026-05-13

## Ziel

Die deutsche Themenseite `which-pronunciation` im unteren Abschlussbereich weiter verfeinern: Lehrbuch-Block neu benennen und beruhigen, Icon-Größen nach der vorherigen Vereinheitlichung zurücknehmen, die Änderungen sauber auf diese DE-Topic-Route begrenzen und Englisch unverändert lassen.

## Consulted Sources

- `AGENTS.md`
- `.github/copilot-instructions.md`
- zuvor bereits konsultierte Teaching-Rendering- und UI-Governance aus `app/AGENTS.md`, `docs/AGENTS.md` und `docs/runbooks/ui-change-workflow.md`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `app/templates/pages/teaching_page.html`
- `app/templates/partials/_teaching_blocks.html`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- DE-Content für `which-pronunciation` im YAML
- Topic-Template um `data-topic-slug` für page-spezifische Styles erweitert
- route-scopte CSS-Verfeinerungen für Lehrbuch-Block, Impulsblock und Citation-/Admonition-Icons
- fokussierte Render-Regression für den neuen Lehrbuch-Titel

## Wichtige Entscheidungen

- Die vorherige DE-only Icon-Mapping-Schicht wurde nicht global weiter ausgebaut, sondern auf `data-topic-slug="which-pronunciation"` eingegrenzt.
- Die großen Citation-Icon-Werte in den Shared Cards wurden nicht global zurückgebaut; stattdessen überschreibt die betroffene Topic-Route diese Werte lokal.
- Der bestehende `didactic_close`-Block blieb inhaltlich erhalten und wurde per CSS in ein kompaktes 2x2-Transferkartenraster überführt, statt den Rendering-Pfad erneut umzubauen.

## Abweichungen

- Keine Abweichung von den aktiven Regeln. Die Änderungen bleiben auf die konkrete DE-Topic-Route begrenzt und ändern keine aktive Plattform- oder Routing-Regel.

## Verifikation

- `pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation"` -> 2 bestanden
- Live-HTTP-Check nach Dev-Server-Neustart: neuer Titel `Vertiefung im Lehrbuch` vorhanden, alter Titel nicht mehr vorhanden
- Browser-QA auf `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`
- gemessene Icon-Größen im Browser: Citation-Quote `24px`, Citation-Copy/Check `25.27px`, Context-Header `21.75px`
- Copy-State im Browser mit gestubbter Clipboard-API geprüft: `data-copy-state="done"`, `aria-label="Zitat kopiert."`, transparenter Hintergrund/Rand, Check-Mask aktiv
- English-Guard im Browser auf `http://127.0.0.1:8000/en/teaching/spanish/which-pronunciation`: `data-ui-lang="en"`, keine deutsche Lehrbuch-Umbenennung, keine DE-route-scopten Größenwerte

## Offene Punkte

- Keine funktionalen offenen Punkte im bearbeiteten Scope.

## Nächste sinnvolle Schritte

- Falls gewünscht, die gleiche page-spezifische Verfeinerungsstrategie auf weitere Teaching-Topics übertragen, statt die Shared Admonition-Citation-Werte global zu verschieben.
