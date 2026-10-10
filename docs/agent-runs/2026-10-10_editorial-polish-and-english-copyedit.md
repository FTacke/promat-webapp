# Editorial Polish: Metadatenzeilen, Tabelle, Themenübersicht-Abstände, englisches Fachlektorat

Datum: 2026-10-10

## Quellen der Texte

Die publizierten Aufsatztexte werden ausschließlich in `app/src/app/routes/public_page_content_data.py` (`SPANISH_DESIGN_PAGE_CONTENT`, je `de`/`en`) gepflegt; der Titel, Zitierblock, `<title>`, `citation_*` und JSON-LD leiten sich daraus bzw. aus `content/publication/resources.yaml` ab. Die Markdown-Vorlage existiert nicht mehr im Repository. Es gibt keine weitere Kopie der Texte; Wort-/Satzlisten, Daten und Registry-Verträge blieben unberührt (Wort- und Satzliste weiterhin 92 / 50 Items, identisch zur Vorfassung).

## Layout

- **Metadaten** (`partials/_article_meta.html`, `routes/public_content.py::_article_header`): drei Zeilen – Autor (Name etwas stärker), Institution, Publikationsjahr und „Zuletzt aktualisiert“ nebeneinander, bei Platzmangel sauber umbrechend; Label gedämpft, Wert normal; keine Fläche, keine Trennlinien, Schriftgröße unverändert `--pm-type-nav-size`. Mehrere Autor:innen werden zusammengefasst, lange Institutionen umbrechen. Abstand Titel→Metadaten von 12 auf 16 px (`--pm-space-sm`), zum Abstract weiterhin der Seitenabschnittsabstand.
- **Schlagwörter** (`partials/_article_abstract.html`): Label `SCHLAGWÖRTER`/`KEYWORDS` auf eigener Zeile (`<h3>`, gleiche Typografie wie die Abstract-Überschrift), Schlagwörter darunter als Textfolge; Abstract bleibt ohne Box.
- **Tabelle** (`promat_page.html`, `30_components.css`, Tokens `--pm-content-table-col-1/2/3` = 30/27/43 %): `colgroup`, oben ausgerichtete, umbrechende Zellen, keine Abschneidung (Prüfung: alle Zellen `scrollWidth ≤ clientWidth`). Ursache des Abschneidens war ein Spezifitätsfehler: `min-width: 54rem` der Basistabelle überschrieb `40rem` der Inhaltstabelle. Jetzt `min-width: 34rem` nur für Inhaltstabellen; Desktop ohne Scrollen, 390 px mit fokussierbarem Scrollbereich im Tabellenrahmen (kein Seiten-Überlauf).
- **Themenübersicht** (Tokens `--pm-teaching-overview-gap`, `-group-stack-gap`, `-group-gap`, `-citation-gap`): etwas mehr Abstand Einleitung→erster Abschnitt, Beschreibung→Karten, zwischen Abschnitten und deutlich mehr vor dem Zitierkasten. Karten, Raster, Farben und Texte unverändert.

## Englisches Fachlektorat (Gegenprüfung am deutschen Text)

- Titel: *Capturing the Pronunciation of Learners of Spanish: Data Collection Design for the Spanish Corpus of Pronunciation Matters* (sichtbar, `<title>`, `citation_title`, Zitierblock und Kopiertext; Open-Graph-Tags gibt es im Projekt nicht; URL unverändert).
- Wesentliche Korrekturen: *Spanish learners* → *learners of Spanish*; *sentence-bound* → *in sentence contexts*; *first-language target norms* → *native-speaker target norms*; *prerequisites* → *needs and proficiency levels*; *heavily adopted* → *largely borrowed*; *material design that makes sense for learners* → *learner-appropriate materials*; *conspicuous realisations* → *unexpected realisations* / *noticeable features* je nach Kontext; *vibrants* → *taps and trills*; *global reading pronunciation* → *overall pronunciation in reading aloud*; *consonantism* → *consonantal phenomena*; der misslungene Satz „Such words can mean that the elicitation no longer…“ neu gebaut („Such words risk shifting the task away from pronunciation: what is elicited then is vocabulary knowledge or reading confidence …“); weitere Germanismen geglättet (z. B. *arise in a vacuum*, *departs from the ideal*, *stress triplet*, *nested sentences*).
- Terminologie: *intelligibility* und *comprehensibility* bleiben getrennt; *wordlist*, *sentence list*, *reading passage*, *elicitation (protocol)*, *pronunciation patterns* einheitlich; ELE wird beim ersten Auftreten eingeführt (*Spanish as a foreign language (español como lengua extranjera, ELE)*); durchgehend British English.
- Literatur (EN): `Hg.` → `eds.`, `o. J.` → `n.d.`, `2., überarb. Aufl.` → `2nd rev. ed.`; Titel, Seiten, Verlage, DOIs unverändert.
- Inhaltstreue: Zahlen (22, 58, 31, 92, 86, 6, 381, 8–14 Wörter, A1–B1), Tabelleninhalt, Fußnoten 1–5, Literatur, Listen und IDs unverändert; ein Strukturtest (Abschnitte, Tabelle, Listen, Literatur, Fußnoten) sichert den Gleichstand DE/EN.

## Redaktionelle Präzisierungen (beide Sprachen)

- Satzliste: „etwa 50 Sätze“ → „Die Liste umfasst 50 Sätze: 30 Aussagesätze, 10 Entscheidungsfragen und 10 W-Fragen.“ / „The list comprises 50 sentences: 30 declarative sentences, 10 yes/no questions and 10 wh-questions.“ Weitere Zahlenfehler wurden nicht gefunden (58 + 31 Wortformen entsprechen den Fußnotenlisten).
- Deutsche Zitierangabe: stimmt mit dem publizierten Titel überein (generiert aus dem Seitentitel; die verkürzte Titelfassung des Manuskripts wurde bereits in `e49b30f` ersetzt).

## Tests und Prüfungen

- `app/tests`: 1351 grün; 1 bekannter, bereits vorher roter Windows-Test (`test_legal_pages_render_in_image_layout…`). Neue Regressionen: Metadatenzeilen und Schlagwortzeile, Tabellenspalten, englisches Lektorat (veraltete Formulierungen fehlen, Titel konsistent, ELE-Einführung), exakte Satzzahl.
- `ci_browser_smoke.py` 263 Checks ohne Fehler, `ci_governance_checks.py` und `validate_teaching_content.py` grün.
- Browser (Screenshots unter `tmp/ui-qa/2026-10-10-design-correction/`): Forschungsdesign DE/EN, hell/dunkel, 1280/390 px, Themenübersicht, Zitierbereiche; kein Seiten-Überlauf.
