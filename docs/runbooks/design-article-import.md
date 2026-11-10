# Runbook: Design-Aufsatz aus dem Autorenmanuskript (DOCX) übernehmen

## Zugehörige Spezifikation

- `docs/spec/platform-data-files.md`, *Routing rules*: „Research design articles“ und „Single-language pages“
- `docs/spec/research-capabilities.md` (Design-Seiten je Korpus)

## Zweck

Ein wissenschaftlicher Design-Aufsatz wird wort- und formatgetreu aus dem DOCX-Manuskript übernommen, ohne Lektorat. Der Ablauf gilt auch für eine neue Fassung desselben Manuskripts. Derzeit sind das der englische Aufsatz von Rolf Kreyer und der deutsche Aufsatz von Theresa Fischer und Kathrin Siebold (mit englischer Fassung).

## Voraussetzungen

- Repo-`.venv`; die Python-Standardbibliothek genügt.
- Das Manuskript als `.docx` ohne Änderungsverfolgung und ohne Kommentare. Der Importer bricht bei nicht unterstützten Strukturen ab, statt zu raten.
- Für die Erhebungsmaterialien die Runtime-Kataloge unter `data/config/research_player/{korpus}/task_catalogs/` (`wordlist.json`, `text.json`).

## Schritte

1. Das Manuskript unverändert unter `docs/author-sources/{korpus}-design/` ablegen, z. B. `kreyer-english-design-original.docx`. Der Ordner ist git-ignoriert: Manuskripte kommen nicht ins öffentliche Repo, die Datei bleibt lokal beim Maintainer und gehört in dessen Sicherung. Den SHA-256 notieren (`sha256sum …`); ein gelieferter Prüfwert muss übereinstimmen und wird als `DOCX_SHA256` in `app/tests/test_english_design_article.py` eingetragen.
   Redaktionelle Auffälligkeiten des Manuskripts gehören nicht in den öffentlichen Run-Bericht, sondern in eine lokale Notiz unter `tmp/author-review/`.
2. Importieren:
   `python scripts/import_design_article_docx.py --docx docs/author-sources/english-design/kreyer-english-design-original.docx --out content/research/english/design.json`
   Deutscher Aufsatz (Struktur über direkte Fettung, Tabellen mit Beschriftung darunter):
   `python scripts/import_design_article_docx.py --profile bold-headings --docx docs/author-sources/german-design/fischer-siebold-german-design-original.docx --corrections docs/author-sources/german-design/fischer-siebold-german-design-corrections.yaml --references-heading Literatur --out content/research/german/design.json`
   Offensichtliche Tippfehler und typografische Versehen, die auf der Seite korrigiert werden dürfen, stehen ausschließlich in der lokalen Korrekturdatei neben dem Manuskript (`source`, `old`, `new`, `kind`); inhaltliche Punkte gehören in die lokale Notiz unter `tmp/author-review/`. Danach den SHA-256 in `app/tests/test_german_design_article.py` (`DOCX_SHA256`) prüfen.
3. Materialien aus den Katalogen kopieren:
   `python scripts/sync_design_article_materials.py --corpus english` bzw. `--corpus german` (Wortliste und Satzliste)
4. Bei einem neuen Korpus:
   - in `app/src/app/routes/public_content.py::RESEARCH_DESIGN_ARTICLES` den Ordner und die Ergänzungen eintragen;
   - die einbettenden Texte der Ergänzungen in `public_page_content_data.py` anlegen (`after_source` = DOCX-Referenz des Absatzes, hinter dem das Material erscheint);
   - in `content/publication/resources.yaml` einen `research_design`-Eintrag mit den Autor:innen anlegen;
   - falls der Aufsatz nur in einer Sprache erscheint, die Seite in `app/src/app/page_languages.py::PAGE_UI_LANGUAGES` eintragen.
   Übersetzte Fassung (Deutsch → Englisch): `content/research/german/design.en.md` von Hand pflegen. Jeder Block beginnt mit dem Marker der Manuskriptstelle (`<!-- p21 -->`); eine Korrektur der Autorinnen ändert nur den Text unter dem betreffenden Marker. Tabellenzellen und Literatur ohne Marker werden unverändert aus dem Original gezeigt. Nach einem Neuimport des Originals meldet der Test fehlende, überzählige oder umsortierte Marker.
5. Tests: `cd app && python -m pytest tests/test_english_design_article.py tests/test_german_design_article.py` und mit Laufzeitdaten `python -m pytest -m data tests/test_design_page_catalog_parity.py`.
6. Browser-Durchgang Desktop/Mobil in Hell und Dunkel (`docs/runbooks/ui-change-workflow.md`), außerdem eine Stichprobe gegen die Word-Darstellung. Die Word-PDF lässt sich lokal per Word-COM-Export (`SaveAs2 … 17`) erzeugen.
7. Inhaltlich nichts korrigieren (nur vereinbarte offensichtliche Tippfehler über die lokale Korrekturdatei, siehe Schritt 2). Abweichungen zwischen Manuskript und Katalogen kommen in den Run-Log, redaktionelle Auffälligkeiten im Text nur in die lokale Notiz (siehe Schritt 1).

## Verifikation

- `python scripts/import_design_article_docx.py … --check` und `python scripts/sync_design_article_materials.py --corpus english --check` melden Übereinstimmung.
- `test_english_design_article.py` ist grün (lokal mit Manuskript; ohne Manuskript, z. B. in CI, laufen nur die Tests, die es nicht brauchen, plus die SHA-256-Prüfung des Imports). Der Test vergleicht jeden Absatz und jede Tabellenzelle der gerenderten Seite Zeichen für Zeichen mit dem DOCX, einschließlich kursiv, fett, unterstrichen und hochgestellt, sowie die automatische Kapitel- und Beispielnummerierung.
- Die deutsche URL einer nur englischen Seite antwortet mit `302` auf die englische URL; im Sprachumschalter ist `DE` deaktiviert.

## Risiken und Rückbau

- Den generierten JSON-Inhalt nie von Hand ändern: Der `--check`-Test schlägt dann fehl. Korrekturen gehören ins Manuskript, danach neu importieren.
- Der Importer kennt nur die Strukturen dieses Manuskripttyps (Titel, Abstract/Keywords, Überschriften 2 und 3, nummerierte Beispiele „(n)“, Tabelle mit Gruppenzeilen, Literaturliste). Neue Strukturen erfordern eine bewusste Erweiterung des Importers, keine Nacharbeit im JSON.
- Rückbau: den Korpus aus `RESEARCH_DESIGN_ARTICLES` und `PAGE_UI_LANGUAGES` entfernen. Die Seite zeigt dann wieder den Zustand „In Vorbereitung“.
