# Finales Nachschärfen von which-pronunciation

Datum: 2026-05-13

## Ziel

Die Themenseite `which-pronunciation` final beruhigen: den unteren Abschluss klar in Ausblick, Citation-Section und Rücknavigation staffeln, den Transferblock mit nummerierten Impulskarten präzisieren, die route-spezifische Icon-Systematik für Citation und Admonitions konsolidieren und das Ergebnis anschließend auf die englische Route angleichen und visuell prüfen.

## Consulted Sources

- `AGENTS.md`
- `.github/copilot-instructions.md`
- bereits zuvor konsultierte Teaching-Governance aus `app/AGENTS.md`, `docs/AGENTS.md` und `docs/runbooks/ui-change-workflow.md`
- `app/templates/pages/teaching_page.html`
- `app/templates/partials/_teaching_blocks.html`
- `app/static/css/30_components.css`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- explizite Citation-Section- und Bottom-Nav-Klassen im Topic-Template
- route-scopte `which-pronunciation`-Styles für Citation-Spacing, Transferblock und nummerierte Impulskarten
- fokussierte Render-Regressionen für DE/EN aktualisiert
- Root-Hygiene: temporäres QA-Hilfsskript wieder entfernt

## Wichtige Entscheidungen

- Die Citation-Box wurde nicht als neuer Blocktyp eingeführt; stattdessen nutzt die bestehende `citation`-Section jetzt eine explizite Wrapper-Klasse (`pm-teaching-topic-section--topic-citation`) und eine eigene Grid-Klasse für saubere Abschlussabstände.
- Die Impulsnummern werden route-scoped per CSS-Counter erzeugt, sodass der bestehende Rich-Text-/Markdown-Pfad intakt bleibt und keine zusätzliche Parser- oder Template-Sonderlogik nötig ist.
- Die vereinheitlichte Icon-Familie bleibt zentral in der `which-pronunciation`-Topic-Scope definiert; zusätzlich werden die variantenspezifischen Admonition-Tokens dort direkt auf dieselben Outline-SVGs gemappt.
- Die EN-Route wurde nicht blind kopiert, sondern nur auf dieselbe Struktur- und Komponentenlogik gebracht; Texte und Rücknavigation bleiben englisch formuliert.

## Abweichungen

- Keine Abweichung von aktiven Regeln. Die Änderungen bleiben auf die konkrete Topic-Route und ihre visuelle Struktur begrenzt.

## Verifikation

- `pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation"` -> 2 bestanden
- Live-DOM-QA im integrierten Browser für DE:
  - `further_reading`-Blockcount `0`
  - Citation-Section-Klasse vorhanden
  - Bottom-Backlink `← Zurück zur Themenübersicht`
  - Abstände: Ausblick -> Citation `54px`, Citation -> Backlink `45px`
  - Impulsblock ohne linke Gesamtborder (`0px`), mit sichtbarer ruhiger Abschnittsfläche
  - Impulskarten nummeriert und als 4 Karten vorhanden
  - Copy-State via gestubbter Clipboard-API: `data-copy-state="done"`, `aria-label="Zitat kopiert."`, transparenter Hintergrund/Rand
- Live-DOM-QA im integrierten Browser für EN:
  - keine deutschen Resttexte
  - Citation-Section-Klasse vorhanden
  - Bottom-Backlink `← Back to topic overview`
  - Copy-State: `data-copy-state="done"`, `aria-label="Citation copied."`, transparenter Hintergrund/Rand
- Icon-Systematik live geprüft:
  - Citation-Quote, Context-Icon und Action-/Check-Icon nutzen `fill='none'`, `stroke='currentColor'`, `viewBox='0 0 24 24'`
  - Größen in DE/EN: Quote `22.3958px`, Copy/Check `23.1979px`, Context `21.5938px`
- Frische Desktop-/Mobile-Screenshots unter `tmp/ui-qa/2026-05-13-which-pronunciation-final-refresh/`
  - `de_desktop.png`
  - `de_mobile.png`
  - `en_desktop.png`
  - `en_mobile.png`
- Headless-QA bestätigt für beide Sprachen:
  - Transferblock Desktop 2×2, Mobile 1 Spalte
  - Kartenhöhen nicht mehr künstlich gleichgezogen
  - kein unterer Vertiefungsblock

## Offene Punkte

- `get_errors` meldet weiterhin ältere `color-mix(...)`-Kompatibilitätshinweise in `app/static/css/30_components.css` außerhalb des bearbeiteten Scopes; daraus ergab sich in diesem Run kein neuer Defekt.

## Nächste sinnvolle Schritte

- Falls gewünscht, dieselbe `topic-citation-section`-/Bottom-Nav-Systematik auch auf weitere Teaching-Topics übertragen, damit der Seitenabschluss nicht nur auf `which-pronunciation` konsistent ist.
