# Publication & Metadata Architecture – Run 4: Architektur- und Repair-Bericht

Datum: 2026-10-06. Nicht-normativ; die aktive Regel steht in `docs/spec/platform-data-files.md`, Abschnitt „Publication Metadata“. Run-Journal: `docs/agent-runs/2026-10-06_publication-metadata-run4.md`.

**Endstatus: siehe Abschnitt „Production“.**

## Resource Model

| Resource Type | ID | Creator | Parent | Version | Citation | DOI-ready |
|---|---|---|---|---|---|---|
| `platform` | `promat` | – (Herausgeber: Felix Tacke) | – | Feld vorhanden, `null` | ja (Projektseite) | ja, `doi: null` |
| `research_corpus` Spanisch | `promat-corpus-es` | Felix Tacke | `promat` | `version`/`data_as_of` vorhanden, `null` | ja | ja |
| `research_corpus` Französisch | `promat-corpus-fr` | Janina Reinhardt | `promat` | `null` | ja | ja |
| `research_corpus` Englisch | `promat-corpus-en` | Rolf Kreyer | `promat` | `null` | ja | ja |
| `research_corpus` Deutsch | `promat-corpus-de` | Kathrin Siebold | `promat` | `null` | nein (`in_preparation`) | Felder vorhanden |
| `research_design` Spanisch | `promat-design-es` | Felix Tacke | `promat-corpus-es` | – | ja | ja |
| `teaching_resource` Spanisch | `promat-teaching-es` | Felix Tacke | `promat` | `null` | ja | ja |
| `teaching_resource` Französisch/Deutsch/Englisch | `promat-teaching-fr`/`-de`/`-en` | nicht hinterlegt | `promat` | `null` | nein (keine veröffentlichten Themen, keine verantwortliche Person) | Felder vorhanden |
| `teaching_topic` „Welche Aussprache unterrichten?“ | `promat-teaching-es-which-pronunciation` (DE und EN) | Felix Tacke | `promat-teaching-es` | `date_modified` 2026-05-13 | ja | ja |

Contributors mit Rolle (aus dem bisherigen Bestand übernommen): Spanisch Materialkonzeption Felix Tacke, Ana Goás Pérez, Durchführung Marlon Merte; Französisch Materialkonzeption Janina Reinhardt, Durchführung Amelie Spieß; Deutsch Materialkonzeption Theresa Fischer, Kathrin Siebold, Durchführung Theresa Fischer; Englisch Materialkonzeption Rolf Kreyer, Durchführung Marlon Merte.

## Findings

| Finding | Phase-0-Status | Entscheidung | Umsetzung | Validation | Endstatus |
|---|---|---|---|---|---|
| PUBL-02 Autor:innenschaft doppelt, Freitext, ohne Rollen | `STILL_OPEN` | Registry mit Personen und Rollen; Creators getrennt vom Plattformherausgeber | `resources.yaml`, `publication.py`; Korpuskarten und Team-Seite generiert; Themen mit `metadata.creators` | Tests „eine Quelle“, „Herausgeber wird nie Autor“, gleiche Personen auf Karten und Team-Seite | s. Production |
| PUBL-03 Lizenz/Rechteinhaber | `POLICY_DECISION_REQUIRED` | nicht entscheiden; Feld `license` vorhanden, `null` | Modell, JSON-LD und Spec tragen eine Lizenz, sobald entschieden | Test „unentschiedene Werte werden nie erfunden“ | `POLICY_DECISION_REQUIRED` |
| PUBL-04 Version/Datenstand der Korpora | `STILL_OPEN` | Infrastruktur, kein künstlicher Wert | `version`, `data_as_of` in Registry, Zitat und JSON-LD | Test mit gesetzten Werten | technisch geschlossen; Wert: `CONTENT_DECISION_REQUIRED` |
| PUBL-05 Identität nur am Slug, 302 statt 404 | `STILL_OPEN` | persistente `resource_id`; 404; explizite `aliases` (301) | Topic-Routing, Validator | Tests 404, Alias, Sprachfallback; Smokes | s. Production |
| METADATA-02 canonical, hreflang, Parametervarianten | `STILL_OPEN` | canonical aus Registry-Origin plus Pfad; hreflang nur bei echtem Äquivalent | `_build_page_meta`, `_page_meta.html` | 14 Seiten parametrisiert, Reziprozität, Parametervarianten, Thema ohne Äquivalent | s. Production |
| METADATA-03 keine maschinenlesbaren Metadaten | `STILL_OPEN` | schema.org JSON-LD als eine primäre Repräsentation; `citation_*` abgeleitet; `<time>` | `publication.json_ld`, Head-Komponente | JSON-LD-Hierarchie, Script-Escape, DOM-Prüfung im Browser-Smoke | s. Production |
| METADATA-04 globale deutsche Description | `STILL_OPEN` | dreistufiger Fallback, lokalisiert | Registry-Beschreibung, `meta.description.*`, Ressourcen-Summary | Test „lokalisiert und ressourcenspezifisch“ | s. Production |
| Landing-`<title>` doppelt | `ALREADY_FIXED` (Run 3) | Titel jetzt zentral aus `page_meta` | zehn Template-Overrides entfernt | Titeltest | `ALREADY_CLOSED` |
| CITE-01 Zitat-URL Domain-Wurzel | `ALREADY_FIXED` (Run 1) | – | – | bestehende Tests angepasst | `ALREADY_CLOSED` |
| CITE-02 Zitat driftet vom Seitentitel | `STILL_OPEN` | Zitat generiert, exakter Seitentitel | getippte Zitate in YAML und Python entfernt | Test gegen YAML-Titel | s. Production |
| CITE-03 kein zentrales Zitierangebot | `STILL_OPEN` | vier Ebenen plus Design-Artikel | Zitatblock auf Projektseite, Korpusseite, Teaching-Hub, Themenseite, Design | Test der vier Ebenen; Copy-Button im Browser | s. Production |
| DATA-05 Personen in mehreren Registries | `STILL_OPEN` | nur der bibliographische Teil | Personen aus `LANGUAGES` und Team-Seite entfernt | Test | s. Production; übrige Korpus-/Vokabular-Literale unverändert (nicht Publication) |
| DATA-11 Validator zu schwach | `STILL_OPEN` | Frontmatter öffentlicher Themen und Registry prüfen | `validate_teaching_content.py` | 16 Validator-Tests | s. Production; verwaiste Medien nicht geprüft |
| DATA-03 142 Itemtexte auf der Design-Seite | `STILL_OPEN` | nicht Teil der Metadatenarchitektur | – | – | unverändert offen (kein Publication-Blocker) |
| CONTENT-02 Platzhalter-`design` | `STILL_OPEN` | ehrlicher „In Vorbereitung“-Zustand, `noindex`, kein Zitat | `build_research_page`, i18n | Test und Browser-Smoke | s. Production; geschützte Platzhalter des deutschen Korpus unverändert |
| Teaching-Verantwortliche Französisch/Deutsch/Englisch | neu | nicht aus dem Repo ableitbar | `creators: []`, nicht zitierbar | Test | `CONTENT_DECISION_REQUIRED` |

## Citation Examples

Tatsächlich generiert (Kopierwert), nur mit hinterlegten Personen:

1. Gesamtplattform (EN): `Tacke, Felix (2026–). Pronunciation Matters: A Multilingual Platform for Learner Pronunciation Research and Teaching. Philipps-Universität Marburg. https://pronunciation-matters.de/en`
2. Research-Korpus Französisch (EN): `Reinhardt, Janina (2026–). Pronunciation Matters: French Learner Pronunciation Corpus. In: Felix Tacke (ed.), Pronunciation Matters: A Multilingual Platform for Learner Pronunciation Research and Teaching. Philipps-Universität Marburg. https://pronunciation-matters.de/en/research/french`
3. Research-Korpus Englisch (EN): `Kreyer, Rolf (2026–). Pronunciation Matters: English Learner Pronunciation Corpus. In: Felix Tacke (ed.), … https://pronunciation-matters.de/en/research/english`
4. Teaching-Sprachbereich Spanisch (DE): `Tacke, Felix (2026–). Pronunciation Matters: Spanish Pronunciation Teaching Resources. In: Felix Tacke (Hrsg.), Pronunciation Matters: A Multilingual Platform for Learner Pronunciation Research and Teaching. Philipps-Universität Marburg. https://pronunciation-matters.de/de/teaching/spanish`
5. Themenseite (DE): `Tacke, Felix (2026). „Welche Aussprache unterrichten?“. In: Felix Tacke (Hrsg.), Pronunciation Matters: A Multilingual Platform for Learner Pronunciation Research and Teaching. Philipps-Universität Marburg. https://pronunciation-matters.de/de/teaching/spanish/which-pronunciation`
6. Themenseite (EN): `Tacke, Felix (2026). “Which pronunciation should you teach?”. In: Felix Tacke (ed.), … https://pronunciation-matters.de/en/teaching/spanish/which-pronunciation`

In der HTML-Fassung sind die Titel der selbständigen Ressourcen und der Plattform kursiv; die URL ist ein Link.

## DOI Readiness

- **Ready:** Plattform, die Korpora Spanisch/Französisch/Englisch, Teaching-Bereich Spanisch, Design-Artikel Spanisch, Themenseite – jeweils mit persistenter `resource_id`, stabiler kanonischer URL, Creators, Publisher, Datum und `isPartOf`. Ein DOI ist ein einzelner Wert (`doi:`) und ersetzt dann im Zitat die URL durch den Resolver-Link.
- **Partially ready:** Korpus Deutsch und die Teaching-Bereiche Französisch/Deutsch/Englisch (Status `in_preparation`; bei den Teaching-Bereichen fehlen Creators).
- **Missing fields für einen Deposit:** Lizenz (überall `null`), Korpusversion bzw. Datenstand, ORCID der Personen, Affiliation außer beim Herausgeber.
- **Keine DOI-Vergabe erfolgt**, kein Deposit, kein DataCite-Export gebaut.

## Policy Handoff

- **Lizenz und Rechteinhaber** (`POLICY_DECISION_REQUIRED`): `app/LICENSE` ist MIT mit „Copyright 2025–2026 Felix Tacke“; der Footer nennt „© 2026 Philipps-Universität Marburg · Hispanistica @ Marburg · Felix Tacke“; das Impressum stellt die Inhalte unter deutsches Urheberrecht mit Zustimmungsvorbehalt; für Teaching-Texte, Teaching-Audio, Forschungsdaten und Metadaten gibt es keine Lizenzangabe. Diese Angaben widersprechen sich teilweise und wurden nicht verändert.
- **Verantwortliche der Teaching-Bereiche** Französisch, Deutsch, Englisch (`CONTENT_DECISION_REQUIRED`): ein Registry-Eintrag je Bereich. Auch die Annahme „Spanisch: Felix Tacke“ bitte bestätigen.
- **Korpusversion/Datenstand** (`CONTENT_DECISION_REQUIRED`): sobald fachlich definiert, `version` oder `data_as_of` setzen.
- **Publikationsstatus** der Korpora Französisch und Englisch: als `published` eingetragen, weil Daten produktiv vorliegen; bei Bedarf auf `in_preparation` setzen.
- **Materialkonzeption Deutsch:** die bisherigen Quellen wichen voneinander ab (DE-Team-Seite und Korpuskarte: Fischer und Siebold; EN-Team-Seite: nur Siebold). Übernommen wurde Fischer und Siebold.
- **ORCID und Affiliationen** der Personen: optional, derzeit leer.
- Technisch offen aus den Audits, aber nicht Publication: DATA-03 (Itemtexte der Design-Seite), übrige Korpus-/Vokabular-Literale (DATA-05), Prüfung verwaister Teaching-Medien (DATA-11), geschützte Platzhalterseiten des deutschen Korpus.

## Production

Wird nach Merge, CI, Deploy und Post-Deploy-Smoke ergänzt.

## Tests

| Prüfung | Ergebnis |
|---|---|
| `pytest` (mit Postgres 15) | 1216 passed, 1 skipped (Windows/WSL), 7 deselected (`data`) |
| neu | `test_publication_metadata.py` 61 Tests; 13 bestehende Tests an generierte Zitate, `datetime` und 404 angepasst |
| JavaScript | 64/64 |
| ruff, compileall, Governance, Content-Validator | grün |
| Docker | Image gebaut, Image-Smoke grün |
| CI-Browser-Smoke (Chromium, Fixture-Runtime) | 180 Prüfungen, 0 Fehler |
| axe / Überlauf (betroffene öffentliche Seiten) | 0 Verstöße auf 52 Kombinationen / 0 von 78 |
| Zotero | nicht getestet (kein Client verfügbar); `citation_*`-Tags im DOM geprüft |
