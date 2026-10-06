# Publication & Metadata Architecture – Run 4

Datum: 2026-10-06. Modell: Opus 5.5 Medium. Branch `feature/run4-publication-metadata` (aus `origin/main` = `6423dc8`). Detailbericht: `docs/reports/2026-10-06_publication-metadata-run4.md`.

## Ziel

Eine kleine, konsistente Publikations- und Metadatenarchitektur: Ressourcenhierarchie Plattform > Sprachkorpus/Teaching-Bereich > Einzelressource, Autor:innen- vs. Herausgeberrolle, kanonische URLs, eine Head-Komponente, schema.org JSON-LD, generierte Zitate, DOI-/Versions-/Lizenzfelder ohne erfundene Werte.

## Consulted Sources

`docs/audits/promat_data_ux_publication_audit_2026-10-06.md` (PUBL-02…05, METADATA-02…04, CITE-02/03, DATA-03/05/11, CONTENT-02), Technical-Integrity-Audit, Run-1–3-Berichte, `docs/spec/platform-data-files.md`, `research-capabilities.md`; Code: `routes/public.py`, `routes/public_content.py`, `routes/public_page_content_data.py`, `teaching_content.py`, `branding.py`, `base.html`, `content/teaching/**`, `scripts/validate_teaching_content.py`.

## Phase 0

- `HEAD` = `origin/main` = Production = `6423dc8` (CI und Deploy grün, Icon-Font 10,9 KB und `immutable`-Header live): Run 3 ist produktiv wirksam. Working Tree sauber. Run-3-Bereiche nicht angefasst.
- Alle Publication-Findings waren `STILL_OPEN`, außer dem doppelten Landing-Titel (Run 3) und der Zitat-URL (Run 1). Lizenz/Rechteinhaber: `POLICY_DECISION_REQUIRED`.

## Wichtige Entscheidungen

- **Eine Registry** `content/publication/resources.yaml` (im Image, neben `content/legal`) als einzige bibliographische Quelle; ein eigenständiges Modul `app/src/app/publication.py` (ohne Flask-Abhängigkeit, damit der Validator es direkt lädt). Spec als Abschnitt „Publication Metadata“ in `platform-data-files.md` statt neuer Spec-Datei (Repo-Regel).
- **Fünf Ressourcentypen**, nicht mehr: `platform`, `research_corpus`, `teaching_resource`, `research_design`, `teaching_topic`. Speaker, Session, Audio, Set sind keine Publikationsressourcen.
- **Creators aus dem Bestand abgeleitet:** Korpus-Creators sind die bisher als „Korpusverantwortung“/„Projektleitung“ gepflegten Personen (Spanisch Tacke, Französisch Reinhardt, Deutsch Siebold, Englisch Kreyer); Materialkonzeption und Durchführung sind Contributors mit Rolle. Für Teaching-Bereiche ist im Repo nirgends eine verantwortliche Person hinterlegt. Ich habe nur für Spanisch Felix Tacke eingetragen (alleiniger Autor aller spanischen Teaching-Inhalte); Französisch, Deutsch, Englisch bleiben `creators: []`, `in_preparation` und damit nicht zitierbar, bis die Verantwortung benannt ist.
- **Korpusstatus:** Spanisch, Französisch, Englisch `published` (Daten produktiv vorhanden), Deutsch `in_preparation` (keine Sessions).
- **Sprachfassungen sind eine Ressource:** DE und EN einer Themenseite teilen eine `resource_id`; jede Fassung hat ihre eigene kanonische URL und zitiert sich selbst.
- **404 statt Redirect** für unbekannte und unveröffentlichte Themen (bisher 302 auf den Hub); Redirects nur noch für fehlende UI-Sprachfassung (302) und explizite `aliases` (301). Alle Smokes prüften schon „nicht 200“ und bleiben gültig; der manuelle Browser-Smoke wurde angepasst.
- **`citation_*`-Tags** zusätzlich zu JSON-LD: abgeleitet aus demselben Modell, weil Browser-Referenzmanager JSON-LD kaum auswerten. JSON-LD bleibt die primäre Repräsentation; kein Dublin Core, kein DataCite-Laufzeitmodell.
- **CONTENT-02:** Die Entwickler-Platzhalter der `design`-Seite (Französisch/Deutsch/Englisch) sind durch einen schlichten „In Vorbereitung“-Zustand ersetzt, `noindex`, ohne Zitat. Die geschützten Platzhalterseiten des deutschen Korpus sind nicht Teil dieses Runs.
- **Design-Artikel Spanisch:** keine YAML-Migration des Inhalts (für die Architektur nicht nötig); nur die bibliographischen Daten liegen in der Registry, das getippte Zitat ist entfernt.
- **Nicht erfunden:** Lizenz, DOI, Korpusversion, Datenstand, ORCID bleiben `null`.

## Geänderte Bereiche

Neu: `content/publication/resources.yaml`, `app/src/app/publication.py`, `templates/partials/_page_meta.html`, `_page_citation.html`, `tests/test_publication_metadata.py` (61 Tests). Geändert: `routes/public.py` (`_build_page_meta`, Indexierbarkeit je Route, Topic-Routing), `routes/public_content.py` (Personen aus Registry, Ressourcen/Zitate, Design-Zustand), `public_page_content_data.py` (getippte Team-Korpuskarten und Design-Zitat entfernt), `teaching_content.py` (Creators, generiertes Zitat, `<time>`, Alternates, Aliase, 404), `branding.py`, `__init__.py`, `i18n.py`, `base.html` und zehn Seitentemplates (Titel zentral), `content/teaching/spanish/which-pronunciation/{de,en}.yaml` (`resource_id`, `metadata.creators`, Zitat entfernt), `scripts/validate_teaching_content.py`, `scripts/post_deploy_smoke.py`, `scripts/qa/ci_browser_smoke.py`, `scripts/qa/browser_smoke.py`; bestehende Tests angepasst. Spec: `platform-data-files.md` (Abschnitt „Publication Metadata“, drei überholte Aussagen), `research-capabilities.md`. ADR `docs/decisions/2026-10-06_publication-metadata-registry-03.md`.

## Verifikation

- `pytest` mit Postgres 15: 1216 passed, 1 skipped, 7 deselected. JS 64/64. ruff, compileall, Governance, Content-Validator grün. Docker-Image gebaut, Image-Smoke grün.
- CI-Browser-Smoke lokal: 180 Prüfungen, 0 Fehler (neu: canonical, reziprokes hreflang, JSON-LD und Zitat im finalen DOM, Copy-Button schreibt das Zitat in die Zwischenablage, 404, `noindex`).
- Run-3-Baseline: axe 0 Verstöße auf 52 Kombinationen der betroffenen öffentlichen Seiten (eine neue `heading-order`-Meldung auf der Korpusseite gefunden und behoben), Überlauf 0 von 78; keine neuen Scripts oder Abhängigkeiten.
- Zotero: kein Zotero-Client/CLI verfügbar, kein echter Import durchgeführt. Geprüft ist nur, dass die von Referenzmanagern gelesenen `citation_*`-Tags, `meta author`, Titel und canonical im finalen DOM stehen.

## Production-Aktionen

Push `6423dc8..66723d1` nach einem vollständigen Linux-Container-Lauf der Suite; CI grün, Deploy grün, Post-Deploy-Smoke grün; Live-Prüfung von 13 Seiten (Titel, Description, canonical, hreflang, JSON-LD, Zitat) plus 404- und Parameterfälle. Keine Server- oder Datenänderung außerhalb des Deployments.

## Abweichungen

Keine von den Specs. Die Spec-Regel „nicht öffentliches Thema leitet auf den Hub um“ wurde bewusst auf 404 geändert.
