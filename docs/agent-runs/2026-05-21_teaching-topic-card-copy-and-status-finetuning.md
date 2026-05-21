# Teaching Topic-Card Copy and Status Finetuning

Datum: 2026-05-21

## Ziel

Sehr gezielter Finetuning-Run nur für die Topic-Cards auf `/{ui_lang}/teaching/spanish`.

Im Scope:

- neue Beschreibung für die einzige verfügbare Karte `Welche Aussprache unterrichten?`
- Dummy-Beschreibungen der drei nicht verfügbaren Karten durch `Beschreibung folgt.` ersetzen
- Pending-Karten textlich und visuell ruhiger machen
- CTA bzw. Status in den Hub-Karten konsistent am unteren Kartenrand halten
- Kartenhöhe ohne unnötige Leerflächen kompakt halten

Nicht im Scope:

- H1, Intro, Kopfbereich
- Sprachkarten der Sprachauswahl
- Back-Buttons und Breadcrumbs
- Kategorieüberschriften inklusive Underlines
- eigentliche Themenseiteninhalte

## Consulted Sources

- Root- und Scoped-Governance in `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`
- bestehende Topic-Card-Struktur in `app/templates/partials/_teaching_blocks.html`
- Hub-Rendering in `app/templates/pages/teaching_page.html`
- Sample-Spiegelung in `app/templates/pages/sample_page.html`
- Teaching-Hub-Daten und Inline-Markdown-Pfad in `app/src/app/teaching_content.py`
- Hub-Daten in `content/teaching/spanish/de/index.yaml`
- Hub-Card-CSS in `app/static/css/30_components.css`
- fokussierte Route-Regressionen in `app/tests/test_research_sessions.py`

## Geänderte Dateien

- `content/teaching/spanish/de/index.yaml`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`

## Datenquelle der Topic-Cards

- Die sichtbaren Hub-Card-Daten für `Spanisch: Themenseiten` kommen direkt aus `content/teaching/spanish/de/index.yaml` unter `topics`.
- Die eigentlichen Karten werden über `_hub_topic_card(...)` in `app/src/app/teaching_content.py` aufgebaut.
- Die Sample-Seite spiegelt diese Card-Familie weiterhin über `sample_teaching_topic_groups`, die aus dem aktuellen Teaching-Hub-Payload gespeist werden; deshalb war keine separate Sample-Datenanpassung nötig.

## Inline-Markup für `seseo` / `distinción`

- Inline-Markup war möglich.
- `_hub_topic_card(...)` reicht `title` und `summary` durch `_set_inline_markdown_fields(..., "title", "summary")`.
- Dadurch konnte die neue Beschreibung in `content/teaching/spanish/de/index.yaml` sauber mit Inline-Markdown geschrieben werden:
  - `*seseo*`
  - `*distinción*`
- Es war kein HTML-Hack nötig; gerendert wurde reguläres Inline-Markdown mit `<em>` im finalen HTML.

## Umsetzung

### Copy

- `Welche Aussprache unterrichten?` erhielt die neue Langbeschreibung:
  - `Orientierung zu Aussprachmodellen und Variation im Spanischunterricht: Warum *seseo* und *distinción* gleichberechtigte Aussprachenormen sind und was das für den Unterricht bedeutet.`
- Die drei derzeit nicht verfügbaren Karten erhielten jeweils nur noch:
  - `Beschreibung folgt.`

### CTA-/Status-Positionierung

- Die gemeinsame Hub-Card-Variante `pm-teaching-topic-card--compact` erhielt für `pm-teaching-topic-card__body` eine echte vertikale Spaltenstruktur über `display: flex` und `flex-direction: column`.
- `pm-teaching-topic-card__action` behält grundsätzlich `margin-top: auto`.
- Die kompakte Variant übersteuert dieses Verhalten jetzt nicht mehr mit kleinem festen `margin-top`, sondern ebenfalls mit `margin-top: auto`.
- Die relevanten Regeln liegen in `app/static/css/30_components.css` auf diesen Selektoren:
  - `.pm-teaching-topic-card--compact .pm-teaching-topic-card__body`
  - `.pm-teaching-topic-card--compact .pm-card__action`
  - `.pm-teaching-topic-card--compact .pm-teaching-topic-card__action`
  - `.pm-teaching-topic-card--compact .pm-card__body > .pm-card__action`
  - `.pm-teaching-topic-card--compact .pm-card__body > .pm-teaching-topic-card__action`

### Muted Pending-Zustand

- Pending-Karten bleiben `article[aria-disabled="true"]` ohne Linkziel.
- Der Pending-Beschreibungstext wurde in der kompakten Variante noch etwas ruhiger gezogen als der verfügbare Beschreibungstext.
- Das Statuslabel `In Vorbereitung` bleibt ein ruhiges Textlabel ohne Button- oder Hover-Anmutung.
- Der Pending-Titel bleibt sichtbar, aber leicht gedämpft gegenüber einer aktiven Karte.

## Verfügbare vs. nicht verfügbare Cards

- verfügbar:
  - nur `Welche Aussprache unterrichten?`
  - rendert als Link-Karte
  - bleibt klickbar
  - zeigt `Öffnen →`
  - Hover/Fokus bleibt aktiv
- nicht verfügbar:
  - `Weiches Spanisch, hartes Deutsch`
  - `Das spanische r`
  - `Finales r`
  - rendern weiter als `article` statt Link
  - zeigen `In Vorbereitung`
  - kein `href`, keine Link-Fokussierbarkeit, kein Pointer-Cursor, kein aktiver Hover-Eindruck

## Verifikation

### Fokussierte Tests

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_language_root_uses_shared_topbar_and_mobile_drawer or teaching_pilot_topic_renders_canonical_two_column_storytelling"` -> `2 passed, 197 deselected`

### Desktop-QA auf realer Route

Route: `http://127.0.0.1:8000/de/teaching/spanish`

Geprüft:

- aktive Karte zeigt die neue Beschreibung mit kursivem `seseo` und `distinción`
- drei Pending-Karten zeigen nur `Beschreibung folgt.`
- verfügbare Karte: `cursor: pointer`, Aktion `Öffnen →`
- Pending-Karten: `cursor: default`, Status `In Vorbereitung`
- unterer Abstand Aktion/Status zum Kartenrand war auf allen vier Karten konsistent (`20.67px`)
- Kartenhöhen wirkten kompakt:
  - verfügbare Kartenreihe: `246.4px`
  - Pending-Karten der zweiten Reihe: `130.23px`

### Mobile-QA

- Die integrierte Browser-Session dieser Umgebung übernahm einen schmalen Viewport nicht zuverlässig; deshalb wurde die Mobile-Prüfung separat headless mit Playwright bei ca. `390x844` nachgezogen.
- Ergebnis:
  - vier Topic-Cards korrekt vorhanden
  - nur die verfügbare Karte mit der langen Beschreibung
  - drei Pending-Karten mit `Beschreibung folgt.` und `In Vorbereitung`
  - Pending-Karten blieben nicht interaktiv
  - kein horizontaler Overflow
  - keine Mobile-only-Regressions beobachtet
  - gemessene mobile Höhen: `201.5px` für die verfügbare Karte, `85.3px` für die drei Pending-Karten

### Regression Checks

- `sample` spiegelt dieselbe Topic-Card-Familie weiterhin korrekt:
  - neue Langbeschreibung nur auf `Welche Aussprache unterrichten?`
  - `Beschreibung folgt.` auf den drei Pending-Karten
  - Statuswerte `Öffnen →` versus `In Vorbereitung` korrekt erhalten
- echte Themenseite `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation` lädt unverändert weiter; Audio-Beispiele und Topic-Header blieben vorhanden, Hub-Cards wurden dort nicht versehentlich eingeführt.

## Abweichungen

- Keine Spec-Änderung erforderlich; der Run blieb ein lokales Finetuning bestehender Teaching-Hub-Karten.