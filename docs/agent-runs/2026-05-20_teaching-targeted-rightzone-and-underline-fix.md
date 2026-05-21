# Teaching Targeted Right-Zone And Underline Fix

Datum: 2026-05-20

## Ziel

Gezielter Fix für zwei enge Teaching-Regressionsbereiche: die rechte Status-/CTA-Zone auf der Unterricht-Sprachauswahlseite sowie die Underline-Scopes auf Spanisch-Hub- und Topic-Seiten.

## Consulted Sources

- Root- und Scoped-Governance in `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`
- Repo-Anweisungen in `.github/instructions/repo.instructions.md`
- produktive Teaching-Templates und CSS in `app/templates/partials/_corpus_card.html`, `app/templates/pages/teaching_page.html`, `app/templates/pages/sample_page.html`, `app/static/css/00_tokens.css`, `app/static/css/30_components.css`
- Git-Historie der betroffenen CSS-Stellen in `app/static/css/00_tokens.css` und `app/static/css/30_components.css`

## Geänderte Bereiche

- `app/templates/partials/_corpus_card.html`
- `app/static/css/00_tokens.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`

## Wichtige Entscheidungen

- Ursache der falschen Underline-Farbe: eine aktuelle uncommitted Shared-Regel koppelte Topic- und Hub-Underlines an den neuen Token `--pm-teaching-section-underline-color`; dadurch verloren normale Topic-Section-Titel ihre committed blaue Farbe und liefen in einen blassen Secondary-Ton.
- Normale Topic-Section-Titel nutzen jetzt wieder die committed Logik über `.pm-teaching-page--topic .pm-teaching-section-heading__title::after` mit `background: var(--book-title-accent-dark)`.
- Didaktische/Impuls-Titel behalten die enge Ausnahme für `which-pronunciation` über `.pm-teaching-page--topic[data-topic-slug="which-pronunciation"] .pm-teaching-topic-section:has(.pm-teaching-rich-text--didactic_close) .pm-teaching-section-heading__title::after` mit `background: var(--promat-wordmark-accent)`.
- Sprachübersichts-Kategorieüberschriften nutzen jetzt dieselbe Underline-Geometrie wie Topic-Section-Titel, aber sauber gescopt über `.pm-teaching-page--hub .pm-teaching-topic-group__title::after`; Farbe und Lage entsprechen damit dem Topic-Vorbild, ohne die Topic-Logik global zu überschreiben.
- Die Sprachkarten-Rechtszone wurde im Markup in eine explizite Aside-Struktur getrennt: Titel links, rechts eine dedizierte `pm-teaching-language-row__aside` für Status und CTA. Desktop nutzt dort ein eigenes Zwei-Spalten-Grid mit größerem Abstand; Mobile bleibt als ruhiger Stack ohne Überlappung.

## Abweichungen

- Keine Spezifikationsänderung erforderlich; der Run repariert regressives UI-Verhalten innerhalb der bestehenden Teaching-Oberflächen.
- Ein breiterer `pytest -k "teaching"` Lauf zeigte zusätzlich eine bereits bestehende Assertion zu exaktem H1-Markup in `test_teaching_overview_keeps_language_selection_label`; diese Abweichung lag außerhalb des gezielten Fix-Scope.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "test_sample_page_reflects_current_landing_and_corpus_cards"` -> bestanden
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching"` -> 1 bestehender Fail, 15 Pass; der Fail betrifft eine separate H1-Markup-Assertion
- Live-DOM-Prüfung auf `http://127.0.0.1:8000/de/teaching`: Status/CTA-Gap der aktiven Karte ca. `46.29px`, vertikale Mittelpunktdifferenz `0px`, Pending-Karten bleiben `article[aria-disabled="true"]` ohne `href`
- Live-Style-Prüfung auf `http://127.0.0.1:8000/de/teaching/spanish`: Hub-Underline für `Grundlagen` rendert als `rgb(47, 111, 179)` mit `opacity 0.24`
- Live-Style-Prüfung auf `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`: normale Section-Titel rendern wieder `rgb(47, 111, 179)` mit `opacity 0.24`; `Impulse für den Unterricht` bleibt `rgb(161, 90, 149)` mit `opacity 0.2`
- Desktop-Screenshot der aktiven Auswahlkarte im integrierten Browser geprüft
- Echter Mobile-Screenshot bei `390x844` via Edge headless geprüft: `tmp/ui-qa/2026-05-20-teaching-targeted-fix/teaching-de-390x844.png`

## Offene Punkte

- Der separate Fail zur exakten Overview-H1-Assertion sollte in einem eigenen, nicht-UI-breiten Follow-up gegen die aktuelle produktive Markup-Ausgabe abgeglichen werden.

## Nächste sinnvolle Schritte

- Optional: den bestehenden H1-Markup-Test gegen die aktuelle produktive Teaching-Overview-Ausgabe nachziehen, falls dafür ein eigener kleiner Testpflege-Run gewünscht ist.