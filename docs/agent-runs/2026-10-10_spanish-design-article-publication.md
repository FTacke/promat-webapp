# Spanisches Erhebungsdesign: finale Aufsatzfassung und Navigationsbezeichnung

Datum: 2026-10-10

## Ziel

Die freigegebene Neufassung des Aufsatzes „Die Aussprache von Spanischlernenden erfassen: Das Erhebungsdesign des spanischen Korpus von *Pronunciation Matters*“ verlustfrei auf `/de/research/spanish/design` übernehmen, Aufsatzkopf mit Metadaten und Abstract ergänzen und die Navigationsbezeichnung `Design` in allen vier Korpora auf `Erhebungsdesign` / `Data Collection Design` ändern.

## Consulted Sources

- `docs/spec/platform-data-files.md` (Publication Metadata, Head metadata, Citations, Corpus landing page)
- `docs/spec/research-capabilities.md`, `docs/spec/research-access.md`
- `content/publication/resources.yaml`, `app/src/app/publication.py`

## Geänderte Bereiche

- `app/src/app/routes/public_page_content_data.py`: deutsche Werte von `SPANISH_DESIGN_PAGE_CONTENT` (Titel, Abschnitte, Tabelle, Fußnoten 1–5, Literatur, Listenzusammenfassungen) direkt aus der Markdown-Vorlage erzeugt und eingesetzt; englische Werte unverändert. Neu: `title_html`, `article_header` (Abstract, Schlagwörter), Abschnittsfeld `blocks` für die geordnete Folge Absatz → Tabelle → Absatz → Liste.
- `app/src/app/routes/public_content.py`: `_article_header` (Autor, Institution, Jahr, Änderungsdatum aus der Registry); ein explizites `None` in einem `{de, en}`-Wert bedeutet „diese Ausgabe hat das Element nicht“ und fällt nicht mehr auf Deutsch zurück.
- `app/src/app/routes/public.py`: `title_html` des Seitenkopfs (kursiver Projektname im H1).
- `app/src/app/publication.py`, `content/publication/resources.yaml`: `display_date`; `date_modified: "2026-10-10"` für `research_design` spanisch (`date_published` bleibt `2026`).
- `app/src/app/i18n.py`: `research.design` → `Erhebungsdesign` / `Data Collection Design`, ebenso der Titel der „in Vorbereitung“-Seiten; neue Schlüssel `research.design.article.*`.
- `app/templates/pages/promat_page.html`, neu `partials/_article_header.html`: Tabellen-Macro (HTML-Zellen, fokussierbarer Scrollbereich), geordnete `blocks`.
- `app/static/css/00_tokens.css`, `30_components.css`, `20_layout.css`: Abstract-Tokens und -Klassen (`pm-article-abstract*`, auf bestehenden Tokens aufgebaut, Hell/Dunkel ohne Sonderregeln); Spaltenregel `minmax(0, 1fr)` für `.promat-page__sections` und `.promat-content-section`, damit breite Tabellen im eigenen Rahmen scrollen.
- Tests: `test_research_sessions.py`, `test_publication_metadata.py` angepasst, neue Regressionen für Aufsatzkopf, Abschnittsfolge, Tabelle, 92/50 Items, Navigationsbezeichnung in allen Korpora, `None`-Semantik.
- Spezifikation: `platform-data-files.md` (Aufsatzkopf, Pillen-Bezeichnung), `research-capabilities.md` (Bezeichnung).

## Wichtige Entscheidungen

- Zitierblock, Kopier-Text, `<title>`, `citation_title` und JSON-LD kommen weiter aus der Registry-/Seitenlogik und tragen jetzt automatisch den neuen Titel; der alte Zitierblock der Vorlage wurde nicht übernommen.
- Links der Vorlage auf `https://pronunciation-matters.de/de/project…` wurden zu internen kanonischen Pfaden (`/de/project/about`, `/structure`, `/data-methods`, `/team`); die Linktexte sind unverändert.
- Fußnote 5 nennt „Pronunciation Matters“ in der Vorlage ohne Kursivierung; wortgleich übernommen, der Hausstil-Test nimmt genau diese Stelle aus.
- Die englische Ausgabe wurde nicht angefasst (keine eigenständige Übersetzung): sie zeigt weiter den alten Text mit 4 Fußnoten, ohne Abstract-Kopf; nur die Navigationsbezeichnung ist `Data Collection Design`.

## Abweichungen

- Die Regel „finished surfaces in de und en gemeinsam“ ist für den Aufsatztext bewusst nicht erfüllt (Auftrag: keine Übersetzung). Der Testvergleich der Fußnotenanzahl DE = EN entfällt deshalb.
- `test_runtime_packaging.py::test_legal_pages_render_in_image_layout…` schlägt auch auf unverändertem HEAD fehl und ist nicht Teil dieses Runs.

## Verifikation

- Vollständiger Testlauf `app/tests`: bis auf den oben genannten, bereits vorher roten Test grün.
- `scripts/qa/ci_browser_smoke.py`: 263 Checks, 0 Fehler; `scripts/ci_governance_checks.py` grün.
- Browserprüfung (Screenshots unter `tmp/ui-qa/2026-10-10-design-article/`): DE/EN, hell/dunkel, 1280 und 390 px, Tabelle scrollt auf schmalem Display, Wortliste aufklappbar, Sprung zu Fußnote 5, kein horizontaler Überlauf; Regression `/de/project/team` und die „in Vorbereitung“-Seiten.
- Abgleich der gerenderten Seite mit der Markdown-Vorlage: alle 232 Textzeilen gefunden; nur Byline und Schlagwortzeile sind absichtlich in Kopfkomponenten aufgeteilt.
- Wort- und Satzliste identisch zur bisherigen Seite (92 / 50 Items, gleiche Reihenfolge).
