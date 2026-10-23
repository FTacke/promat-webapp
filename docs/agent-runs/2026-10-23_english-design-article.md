# Englische Design-Seite (Rolf Kreyer) originalgetreu integriert, seitenbezogene Einsprachigkeit

Datum: 2026-10-23

## Ziel

Rolf Kreyers Beitrag „Capturing the Pronunciation of Learners of English as a Foreign Language: Data Collection Design for the English Corpus of *Pronunciation Matters*“ wurde wort- und formatgetreu als Design-Seite des englischen Korpus übernommen, in der Seitenfamilie der spanischen Design-Seite. Dazu kam eine allgemeine, deklarative Unterstützung für einsprachige Seiten, die bisher nur `/en/research/english/design` nutzt. Kein Lektorat: Am Text wurde nichts korrigiert.

## Consulted Sources

- `AGENTS.md`, `scripts/AGENTS.md`, `docs/spec/platform-data-files.md`, `docs/spec/research-access.md`, `docs/spec/research-capabilities.md`
- Spanische Design-Seite: `routes/public_page_content_data.py::SPANISH_DESIGN_PAGE_CONTENT`, `routes/public_content.py`, `templates/pages/promat_page.html` und die Partials, `test_design_page_catalog_parity.py`
- Manuskript `docs/author-sources/english-design/kreyer-english-design-original.docx`, SHA-256 `af31cc6e…5a6d` (stimmt mit dem gelieferten Wert überein; nur lokal, git-ignoriert), OOXML: `document.xml`, `styles.xml`, `numbering.xml`
- Runtime-Kataloge `data/config/research_player/english/task_catalogs/{wordlist,text}.json`

## Geänderte Bereiche

- **Import:** `scripts/import_design_article_docx.py` (DOCX → `content/research/english/design.json`) und `scripts/sync_design_article_materials.py` (Kataloge → `content/research/english/design_materials.json`), beide mit `--check`.
- **Seite:** `routes/public_content.py` (`RESEARCH_DESIGN_ARTICLES`, Loader, Einfügen der Ergänzungen), `routes/public_page_content_data.py` (`ENGLISH_DESIGN_SUPPLEMENTS`: nur die einbettenden Plattformtexte), `content/publication/resources.yaml` (`research_design` für `english`: Rolf Kreyer, 2026, keine DOI/Lizenz).
- **Templates:** `promat_page.html` mit nummerierten Kapitelüberschriften, Blocktypen `subheading`, `example` und `grouped_table`, Literatur mit Quellbezug; `_reading_expandable.html` mit Überzeile, Supplement-Modifier, Einspaltigkeit und `data-item-id`; `_article_abstract.html` und `_content_header.html` mit optionalem `data-source`.
- **Einsprachigkeit:** neues Modul `app/src/app/page_languages.py`. In `routes/public.py` die `before_request`-Weiterleitung, `hreflang` nur für vorhandene Fassungen und direkte Links in Sidebar und Feature-Cards. In `__init__.py` setzt der Kontextprozessor die Umschalter-URL auf `None`, wenn eine Fassung fehlt; `_ui_lang_switch.html` zeigt dann einen deaktivierten Eintrag.
- **CSS** (`30_components.css`, Erweiterung bestehender Familien): `.pm-expandable--supplement`, `__eyebrow`, `--single-column`; `.pm-article-example`, `.pm-article-subheading`, `.pm-article-heading__number`; `.pm-article-grouped-table` (auf `pm-research-table`, stapelt unter 720 px); `.promat-topbar__language-link.is-unavailable`.
- **i18n (de/en):** `shell.topbar.language_unavailable`, `research.design.table.phenomenon`/`.evidence` (nur für Screenreader), `research.design.supplement.eyebrow`. Der Pending-Text nennt jetzt Spanisch und Englisch als fertig.
- **Doku:** Specs (`platform-data-files.md`: *Single-language pages*, *Research design articles*, Sprachumschalter; `research-access.md`; `research-capabilities.md`), Runbook `docs/runbooks/design-article-import.md`, ADR `docs/decisions/2026-10-23_single-language-pages-05.md`.
- **Tests:** neu `app/tests/test_english_design_article.py` (20 Tests); `test_design_page_catalog_parity.py` um Englisch erweitert (Marker `data`).

## Wichtige Entscheidungen

- **DOCX direkt lesen:** Absätze werden nicht als `paragraph.text` übernommen. Gelesen werden die Runs mit Formatierung (kursiv, fett, unterstrichen, hoch-/tiefgestellt, Zeichenformatvorlagen). Benachbarte Runs mit gleichem Format werden zusammengeführt, Tags konsistent verschachtelt. Die automatische Word-Nummerierung (Kapitel 1.–5., Beispiele (1)/(2)) wird aus `numbering.xml` berechnet; die Erkennung läuft über Stilnamen (`heading 2`), nicht über lokalisierte IDs (`berschrift2`). Bei unbekannten Strukturen bricht der Importer ab. Die DOCX enthält keine Änderungsverfolgung, keine Felder und keine Symbolschriften.
- **Generiertes JSON statt Python-Dict:** Der Artikel ist ein reproduzierbares Importprodukt. `--check` und ein Test verhindern Handänderungen. `content/` wird ins Image kopiert, `docs/` nicht.
- **Materialien als Kopie mit Drift-Test:** Das entspricht der spanischen Konvention. Die Seite muss ohne die betreiberseitigen Kataloge rendern (CI, Image-Smoke).
- **Leere Tabellenzeilen 10 und 15:** Das sind reine Abstandszeilen in Word ohne Text. Sie stehen in `skipped_empty_rows` und werden vom Test abgesichert. Gruppenzeilen werden als `th colspan=2` dargestellt. Spaltenköpfe sind nur für Screenreader vorhanden; sichtbar bleibt ausschließlich Text aus dem Manuskript.
- **Label „Abstract“:** In Word ist es mit der Formatvorlage „Book Title“ fett-kursiv gesetzt, die Seite zeigt es im Plattform-Label-Stil. Das ist die einzige dokumentierte Formatausnahme (`FORMAT_EXCEPTIONS` im Test).
- **Einsprachigkeit pfadbasiert und zentral:** Begründung in der ADR. 302-Weiterleitung wie bei Teaching-Editionen.
- **Erscheinungsjahr 2026:** Das ist das Jahr der Veröffentlichung auf der Plattform (wie beim spanischen Eintrag). Weitere bibliographische Angaben wurden nicht ergänzt. Bitte bestätigen.

## Verifikation

- Integritätstest: Die gerenderte Seite stimmt Zeichen für Zeichen mit dem DOCX überein, ebenso die Formatierung pro Zeichen und die Reihenfolge aller 72 Manuskriptteile (Absätze und Tabellenzellen). Normalisiert wird nur Whitespace. Gegenprobe mit drei absichtlichen Verfälschungen (stillschweigende Tippfehlerkorrektur, entfernte Kursivierung, Gedankenstrich als Bindestrich): Alle drei werden erkannt.
- Sichtprüfung gegen Word: Die DOCX wurde per Word-COM als PDF exportiert und mit den Screenshots verglichen (Nummerierung, Beispiele, Tabelle, Literatur). Dateien liegen unter `tmp/ui-qa/2026-10-23-english-design/`.
- Browser (eigene Instanz auf :8011, Chromium): Desktop 1366 px und Mobil 390 px, hell und dunkel; zum Vergleich die spanische Design-Seite (de/en), `/de/research/english` und `/de/research/french/design`. Auf keiner Ansicht scrollt die Seite horizontal. Zwei Befunde im ersten Durchgang behoben: Die Phänomen-Spalte war zu klein und die Tabelle auf dem Handy abgeschnitten (beides Spezifität gegenüber `min-width: 34rem`), und Beispiel (1) stand in der UI-Schrift.
- `/de/research/english/design` → 302 → `/en/…` (Query ohne `lang`); der Umschalter zeigt `DE` deaktiviert; kein `hreflang`; Canonical ist die englische URL; Zitation und JSON-LD nennen „Kreyer, Rolf“ als Autor, Felix Tacke als Herausgeber der Plattform.
- Testsuite: `1467 passed, 2 skipped` (vorher `1447 passed`). Mit Marker `data` laufen die Paritätstests für Spanisch und Englisch grün. `scripts/ci_governance_checks.py` besteht ohne Befund. Angepasst wurden vier bestehende Tests, die Englisch noch als Korpus ohne Aufsatz bzw. mit zweisprachiger Design-URL annahmen; sie prüfen jetzt die Weiterleitung bzw. den direkten Link auf die englische Fassung. Post-Deploy- und Image-Smoke prüfen zusätzlich `/en/research/english/design` und die 302-Weiterleitung von der deutschen URL.

## Abgleich Manuskript ↔ Runtime-Kataloge (nicht angeglichen)

- **Wortliste:** Laut Manuskript „85 single words and 11 minimal pairs“ und „The minimal pairs 85 to 95“. Der Katalog hat 95 Items: 84 Einzelwörter (1–84) und 11 Paare (85–95). „full“ steht doppelt (68 und 82), es sind also 83 verschiedene Einzelwörter.
- Item 15 „racing“ kommt weder in Text (2) noch im Katalog-Lesetext vor (dort stehen „raced“ und „Raising“), obwohl die Wortliste laut Manuskript „extracted from the text“ ist.
- Paar 95 „Annie - Kenny“ ist mit Bindestrich geschrieben, alle anderen Paare mit Halbgeviertstrich. Es ist außerdem kein Minimalpaar im engeren Sinn.
- Paare: Laut Manuskript sind *love – laugh* und *of – off* Beispiele für Wörter, die nicht im Text stehen. Tatsächlich steht *love* in Text (2) („He did not love his job“) und *of* ebenfalls; *laugh* steht nur im Katalog-Lesetext (T28), *off* in keinem der beiden Texte. In keinem Text stehen außerdem *bat* (Paar 91) und *race* (Paar 92).
- **Lesetext:** Text (2) im Manuskript und der Katalogtext (T1–T56) weichen voneinander ab. Der Katalog hat zusätzlich „in **his** bed“, „he thought **to himself ‘Let someone else do it!’ He devised** a good plan“ statt „he thought **up** a good plan“, „‘Wolf, Wolf**!**’“ statt „‘Wolf, Wolf**.**’“, „that **he had to laugh, and** a few days later“, „full of **hunger and rage**“ statt „**rage and hunger**“ und „‘**Where is it? Show us. We can’t see it!** Go away …“. Die Einschübe sind im Katalog mit Geviertstrich (—) gesetzt, im Manuskript mit Halbgeviertstrich (–).
- **Wortzahl:** Das Manuskript nennt 342 Wörter für Text (2). Nach Leerzeichen gezählt sind es 338 Wörter Fließtext (343 mit Titel), im Katalog-Lesetext 361. Die Stella-Angabe „69-words“ stimmt (69).
- **Tabelle:** Alle Belegwörter der Phänomentabelle kommen in Text (2) vor.
- Auf der Seite sind die Katalogmaterialien als „Supplementary corpus material“ gekennzeichnet, und der Lesetext trägt den Hinweis, dass er nicht an Text (2) angeglichen ist.

## Redaktionelle und fachliche Prüfpunkte für einen späteren Durchgang

Die Liste der Fundstellen (Tippfehler, IPA-Zeichen, Literaturangaben) liegt bewusst nicht im öffentlichen Repo, sondern lokal beim Maintainer unter `tmp/author-review/2026-10-23_english-design-pruefpunkte.md`. Ebenso liegt das Manuskript nur lokal (`docs/author-sources/` ist git-ignoriert). Am Text wurde nichts geändert.

## Nachtrag: Erhebungsmaterialien an die spanische Seite angeglichen

- Die englische Wordlist ist jetzt dieselbe Komponente wie die spanische (`pm-expandable`): Titel „Wordlist“, Satz „The English wordlist comprises 95 task items: 84 individual words and 11 minimal pairs.“ (Zahlen aus dem Katalog berechnet), alle 95 Items mit Katalognummern und -schreibweisen. Entfallen sind die Überzeile „Supplementary corpus material“, die Tönung und die zugehörigen CSS-Regeln und i18n-Schlüssel. Die Herkunft steht nur noch unsichtbar in `data-supplement`.
- Der Block „Reading text as used in the recordings“ (T1–T56) ist entfernt; `design_materials.json` enthält nur noch die Wordlist. Der Text „The Boy who Cried Wolf“ erscheint ausschließlich als Rolfs Beispiel (2). Runtime-Kataloge unter `data/` sind unverändert (geprüft per Prüfsumme vor und nach der Änderung).
- Die Abweichungen zwischen Beispiel (2) und dem aufgenommenen Katalogtext stehen weiterhin oben im Abschnitt *Abgleich Manuskript ↔ Runtime-Kataloge*.
- Tests: `test_english_design_article.py` prüft jetzt die Wordlist-Items, Titel und Satz wörtlich, die Markup-Gleichheit mit der spanischen Wordlist (Tag- und Klassenfolge) und dass kein Lesetext-Block und kein Supplement-Label mehr auf der Seite stehen. Der Manuskript-Integritätstest ist unverändert grün, `design.json` ist unverändert (`--check`).
- Browser: Wordlists Englisch/Spanisch zugeklappt und aufgeklappt, Desktop/Mobil, hell/dunkel nebeneinander verglichen; gleiche Breite (724 px / 358 px), kein horizontales Scrollen.

## Offene Punkte

- Erscheinungsjahr 2026 im Register bestätigen. Datum der letzten Aktualisierung ist bewusst leer.
- Nach Freigabe der Prüfpunkte durch Rolf Kreyer: Manuskript korrigieren und nach dem Runbook neu importieren.
- Production-Deployment nur über das reguläre Verfahren (Push auf `main`).
