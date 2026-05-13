# Teaching Admonition Icon Unification

Datum: 2026-05-13

## Ziel

Die Admonition- und Citation-Icons auf der deutschen Teaching-Topic-Route `which-pronunciation` auf eine gemeinsame schlichte Outline-SVG-Systematik umstellen, ohne die englische Route sichtbar zu verändern.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/static/css/00_tokens.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/templates/base.html`
- `app/templates/pages/teaching_page.html`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `app/static/css/30_components.css`

## Wichtige Entscheidungen

- Die vorhandene tokenbasierte Admonition-Architektur blieb erhalten; darüber liegt jetzt eine deutsche Topic-seitig gescopte Icon-Mapping-Schicht statt einer globalen Ersetzung.
- Die Outline-SVGs werden zentral über CSS-Variablen auf der Route `html[data-ui-lang="de"] .pm-teaching-page--topic` gemappt.
- Die englische Teaching-Route bleibt unverändert, weil die neuen Tokens nur unter dem deutschen UI-Lang-Scope aktiv sind.
- Für den Citation-Copy-State wurde die Badge-/Statusflächenoptik entfernt; der State kommuniziert sich nur noch über Clipboard-zu-Check-Icon plus ARIA-Status.

## Abweichungen

- Keine Spec-Änderung nötig; es handelt sich um eine visuelle Systemangleichung innerhalb bestehender UI-Komponenten.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation"`
- Browser-QA auf `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`
- Live geprüft: Info-Admonition mit konsistentem Outline-Info-Icon
- Live geprüft: Citation-Box mit Outline-Quote- und Clipboard-Icon aus derselben visuellen Familie
- Direkt nach Klick geprüft: `data-copy-state="done"`, `aria-label="Zitat kopiert."`, Check-Icon-Maske aktiv, Hintergrund und Border weiter transparent

## Offene Punkte

- Die deutsche Topic-Route ist vereinheitlicht; weitere deutsche Teaching-Topic-Seiten könnten bei Bedarf denselben Icon-Scope mitnutzen oder separat feinjustiert werden.

## Nächste sinnvolle Schritte

- Falls weitere deutsche Teaching-Themenseiten folgen, dieselbe Route-Scope-Logik wiederverwenden und nur die inhaltlichen Admonition-Varianten gegenprüfen.