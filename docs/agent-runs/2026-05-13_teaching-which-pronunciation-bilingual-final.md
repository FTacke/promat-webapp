# Bilinguale Finalisierung für which-pronunciation

Datum: 2026-05-13

## Ziel

Die Themenseite `which-pronunciation` zuerst auf Deutsch final bereinigen und danach auf Englisch übertragen: redundanten unteren Vertiefungsblock entfernen, den Seitenabschluss beruhigen, die Icon-Systematik für Citation und Admonitions zentral auf der Topic-Route vereinheitlichen und beide Sprachversionen mit derselben Layout- und Interaktionslogik validieren.

## Consulted Sources

- `AGENTS.md`
- `.github/copilot-instructions.md`
- bereits zuvor konsultierte Teaching-Governance aus `app/AGENTS.md`, `docs/AGENTS.md` und `docs/runbooks/ui-change-workflow.md`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
- `app/templates/pages/teaching_page.html`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- DE-Topic-Content: redundanten unteren Lehrbuchblock entfernt
- EN-Topic-Content: an den bereinigten DE-Abschluss angeglichen, inkl. eigenem Transferblock und Ausblick-Sektion statt altem Weiterlesen-/Hub-Ende
- route-scopte CSS-Systematik für `which-pronunciation` in beiden Sprachen vereinheitlicht
- fokussierte Render-Regressionen für DE und EN erweitert

## Wichtige Entscheidungen

- Die Icon-Vereinheitlichung wurde nicht weiter per Einzelkorrekturen ergänzt, sondern auf eine gemeinsame Topic-Scope-Schicht (`data-topic-slug="which-pronunciation"`) gehoben.
- Neben den Basistoken wurden auch die variantenspezifischen Admonition-Tokens direkt auf dieselbe Outline-Familie gemappt, weil die gerenderten Pseudoelemente sonst weiter alte Root-Icons nutzten.
- Der redundante `further_reading`-Abschlussblock wurde in DE entfernt und in EN nicht durch einen neuen Ersatzblock ersetzt; relevante Lehrbuchlinks bleiben nur noch inhaltlich eingebettet im Ausblick.
- Die EN-Seite wurde erst nach stabiler DE-Umsetzung übertragen und auf dieselbe Abschlusslogik reduziert: Transferblock, Ausblick, Citation, Backlink.

## Abweichungen

- Keine Abweichung von den aktiven Regeln. Die Änderungen bleiben auf die konkrete Topic-Route begrenzt und ändern keine aktiven Plattform- oder Routingregeln.

## Verifikation

- `pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation"` -> 2 bestanden
- Live-Browser-QA im Shared Browser für DE und EN:
  - `further_reading`-Blockcount `0`
  - Copy-State nach gestubbter Clipboard-API in beiden Sprachen: `data-copy-state="done"`, transparente Fläche/Rand, nur Check-Icon
  - Bottom-Backlink vorhanden in beiden Sprachen
- Route-spezifische Icon-Prüfung im Live-DOM:
  - Citation-Quote und Context-Icon laufen auf `fill='none'`, `stroke='currentColor'`, `stroke-width='2'`
  - Citation-Action läuft auf das schlichte Check-/Copy-SVG ohne Badge-Optik
  - gemessene Größen in DE/EN: Quote `22.3958px`, Copy/Check `23.1979px`, Context `21.5938px`
- Echte Desktop-/Mobile-Screenshots via lokalem Playwright unter `tmp/ui-qa/2026-05-13-which-pronunciation-final/`
  - `de_desktop.png`
  - `de_mobile.png`
  - `en_desktop.png`
  - `en_mobile.png`
- Mobile-QA bestätigt den Transferblock als 1-Spalten-Layout; Desktop-QA bestätigt 2×2-Kartenraster.

## Offene Punkte

- `get_errors` meldet in `app/static/css/30_components.css` weiterhin bestehende `color-mix(...)`-Kompatibilitätshinweise außerhalb des bearbeiteten Scopes; daraus ergab sich in diesem Run kein neuer Defekt.

## Nächste sinnvolle Schritte

- Falls gewünscht, dieselbe route-scopte Icon-Härtung auf weitere Teaching-Topic-Seiten übertragen, bevor die globale Admonition-Tokenfamilie repo-weit neu gefasst wird.
