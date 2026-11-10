# Deutsches Erhebungsdesign (Theresa Fischer, Kathrin Siebold): zweisprachige Design-Seite (2026-11-10)

`/de/research/german/design` zeigt jetzt den Aufsatz „Die Aussprache von Deutschlernenden erfassen: Das Erhebungsdesign des deutschen Korpus von *Pronunciation Matters*“. `/en/research/german/design` zeigt die englische Fassung „Capturing the Pronunciation of Learners of German: Data Collection Design for the German Corpus of *Pronunciation Matters*“. Der bisherige Zustand „In Vorbereitung“ entfällt.

## 1. Architektur und Komponenten

- Die Seite gehört zur selben Architektur wie der englische Aufsatz von Rolf Kreyer (`RESEARCH_DESIGN_ARTICLES`). Die deutsche Fassung kommt aus `content/research/german/design.json`, die englische aus `content/research/german/design.en.md`; die Korpusmaterialien stehen in `content/research/german/design_materials.json`.
- **Importer** `scripts/import_design_article_docx.py` mit neuem Profil `bold-headings`:
  - Das Manuskript ist durchgehend in „Standard“ gesetzt. Titel, Abstract-Label, Abschnittsüberschriften („1. …“), Tabellenbeschriftungen („Tab. n: …“, unter der Tabelle) und „Literatur“ sind nur direkt fett ausgezeichnet.
  - Tabellen werden zu `expandable_table`-Blöcken: zwei Spalten, eine Zelle kann mehrere Absätze haben.
  - Unbekannte Strukturen brechen den Import ab. Das bisherige Profil bleibt unverändert; der englische Import ist bitgleich.
- **Englische Fassung**: `app/src/app/design_translation.py` legt die Markdown-Übersetzung zur Laufzeit über eine Kopie der deutschen Struktur.
  - Jeder übersetzte Block beginnt mit dem Marker der Manuskriptstelle, etwa `<!-- p21 -->`.
  - Alle Prosaelemente sind Pflicht und müssen in Manuskriptreihenfolge stehen: Titel, Abstract, Überschriften, Absätze und Tabellenbeschriftungen.
  - Tabellenzellen ohne Marker und die Literatur werden sprachneutral übernommen: IPA, deutsche Beispielwörter mit Itemnummer, bibliographische Angaben.
- **Tabellen** in der vorhandenen Komponente `pm-expandable`:
  - Die Beschriftung ist sichtbarer Titel; die Tabelle ist standardmäßig zu und lässt sich über den vorhandenen Button öffnen.
  - Im Inneren steht eine semantische `<table>` mit Zeilenköpfen und Spaltenköpfen für Screenreader.
  - Unter 720 px werden die Zeilen gestapelt, mit dem CSS der gruppierten Artikeltabelle.
  - Ergänzt wurden nur eine kleine Tabellen-Variante (`pm-expandable--table`, `pm-article-row-table`) und Titel-Umbruch für lange Überschriften. Neue Designfamilien gibt es nicht.
- **Materialien**: `scripts/sync_design_article_materials.py --corpus german` kopiert Wortliste und Satzliste aus den Aufgabenkatalogen. Beide erscheinen als Plattformergänzung mit `data-supplement`, ohne `data-source`, und mit dem Hinweis „Ergänzt aus dem Aufgabenkatalog des Korpus“.
- **Registry**: `research_design` für `german` (`promat-design-de`), Autorinnen in der Reihenfolge Theresa Fischer, Kathrin Siebold, Erscheinungsjahr 2026. Die Institution ist Philipps-Universität Marburg (über den Herausgeber). DOI, Lizenz und ORCID sind `null`.
- Seite zweisprachig, nicht in `PAGE_UI_LANGUAGES`: Canonical je Fassung, `hreflang` de/en, die Sprachumschaltung wechselt direkt.

## 2. Speicherorte

- Original-DOCX (lokal, git-ignoriert): `docs/author-sources/german-design/fischer-siebold-german-design-original.docx`, SHA-256 `108d722ea80d12775fa3eabe7edf3549c72c09c17e1edefe84ebd06e0d67d213`.
- Korrekturliste (lokal, git-ignoriert, neben dem Manuskript): `fischer-siebold-german-design-corrections.yaml`. `design.json` vermerkt nur ihren SHA-256 und die Zahl der Einträge.
- Englische Übersetzungsquelle (versioniert): `content/research/german/design.en.md`.
- Review-Fassung für die Autorinnen (lokal): `fischer-siebold_german-design_EN_review.docx`. Sie enthält den vollständigen englischen Text mit Tabellen und Stellenmarkern sowie die Kataloglisten als Anhang.
- Prüfpunkte für die Autorinnen (lokal): `tmp/author-review/2026-11-10_german-design-pruefpunkte.md`.

## 3. Vollständiger Import

Übernommen sind:
- Titel und Abstract;
- vier nummerierte Abschnitte mit 13 Absätzen;
- drei Tabellen: Tab. 1 mit 19 Zeilen, Tab. 2 mit 22 Zeilen, Tab. 3 mit 2 Zeilen; mehrteilige Zellen bleiben erhalten;
- sieben Literaturangaben.

`app/tests/test_german_design_article.py` liest das DOCX mit dem unabhängigen Reader des englischen Tests. Lokal vergleicht der Test jedes Element der gerenderten Seite Zeichen für Zeichen, nach Anwendung der vereinbarten Korrekturen. Er prüft auch Reihenfolge und Zeichenformatierung sowie einen frischen Import. In CI ist das Manuskript nicht vorhanden; dort laufen nur der SHA-256-Abgleich und die übrigen Tests.

## 4. Tabellen

| Tabelle | Inhalt | Darstellung |
|---|---|---|
| Tab. 1 | 16 Monophthong- und 3 Diphthongzeilen | Desktop zweispaltig (IPA 24 %, Items 76 %) |
| Tab. 2 | 22 Konsonantenzeilen; Zusätze wie „im Cluster“, „Auslautverhärtung“ als eigene Absätze | dito |
| Tab. 3 | Anlaut- und Auslautcluster | dito |

- Mobil sind die Zeilen gestapelt: IPA-Kopf über der vollständigen Itemliste.
- Nichts wird abgeschnitten, keine Zeile ist gekürzt.

## 5. Materialien

- Wortliste: 96 Items, davon 85 Einzelwörter und 11 Minimalpaare. Sie steht nach dem Absatz zur Wortliste.
- Satzliste: 51 Sätze (T1–T51). Sie steht nach dem Absatz zur Satzliste.
- Das Interview ist nur im Fließtext beschrieben.
- Ein Wortlistenitem gilt jetzt als Minimalpaar, wenn ein Bindestrich an einem Leerzeichen steht; der Katalog schreibt „sagen -sägen“. Das englische Ergebnis bleibt unverändert.

## 6. Vollständigkeit DE/EN

- Beide Fassungen haben dieselben Elemente in derselben Reihenfolge.
- In jedem Element sind dieselben IPA-Zeichen und Jahreszahlen enthalten. Die Tabellen haben dieselben Beispielwörter mit Itemnummern, die Literatur ist identisch.
- Die englische Übersetzung ist eine **KI-gestützte Erstfassung (10.11.2026), die die Autorinnen noch prüfen können**. Sachliche Auffälligkeiten des Originals gibt sie unverändert wieder, z. B. „50 sentences: 31 … 10 … 10“.

## 7. Schreibkorrekturen

40 Einträge in der lokalen Korrekturliste:

| Art | Anzahl |
|---|---|
| Tipp-, Grammatik- und Zeichensetzungsfehler, darunter doppelte Wörter, ein fehlendes Wort und eine fehlende Klammer | 13 |
| Typografie (Halbgeviertstriche, „z. B.“/„u. a.“, Leerzeichen, Abkürzungspunkt) | 18 |
| Kursivierung in vier Zellen von Tab. 1, wie im Rest der Tabelle | 4 |
| unsichtbare Wortverbinder, damit Auslautcluster wie „-lf“ nicht nach dem Bindestrich umbrechen | 5 |

Die Einzelliste steht in der lokalen Prüfnotiz (Abschnitt A). Inhalt, Lautinventare, Beispielwörter und Itemnummern sind unverändert.

## 8. Prüfpunkte für die Autorinnen

Die Prüfpunkte liegen separat und lokal vor: `tmp/author-review/2026-11-10_german-design-pruefpunkte.md`, Abschnitt B, 9 Punkte. Es geht um Satzzahl gegenüber Katalog, Itemnummern in den Tabellen, IPA-Notation, den WALS-Vergleich, die Vokalzählung, Wortformen in den Sätzen, einen unklaren Satz, die Zitierweise und zwei Auffälligkeiten im Korpuskatalog. Nichts davon wurde auf der Seite geändert.

## 9. Tests und Browser

- `test_german_design_article.py` neu.
- Angepasst: `test_design_page_catalog_parity.py` (jetzt auch Deutsch, Wortliste und Satzliste), `test_research_sessions.py`, `test_publication_metadata.py` und `test_german_research_empty_state.py`. Diese drei setzten noch die „In Vorbereitung“-Seite voraus.
- Image-Smoke um beide Design-URLs erweitert.
- Ergebnisse:
  - 1624 Python-Tests, dazu die Katalogparität (Marker `data`);
  - ruff und Governance grün;
  - JS 69/69;
  - Browser-Smoke 277/277.
- Browser lokal: DE/EN × Desktop/Mobil × Hell/Dunkel.
  - Alle 5 Expandables starten geschlossen und lassen sich vollständig öffnen.
  - Nichts wird abgeschnitten, kein Overflow, keine Konsolenfehler.
  - Mobil drückte der lange Tabellentitel zunächst den Button 10 px aus dem Panel; behoben über den Titelumbruch.
- Regression: spanische Design-Seite DE/EN und englische Design-Seite unverändert funktionsfähig.

## 10. Veröffentlichung

Siehe Nachtrag.
