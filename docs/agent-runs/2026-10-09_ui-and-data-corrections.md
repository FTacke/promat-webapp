# UI- und Datenkorrekturrun (neun Punkte)

Datum: 2026-10-09

Non-normative run report. Binding rules: `docs/spec/platform-data-files.md`, `docs/spec/research-access.md`.

## Ziel

Begrenzter Korrekturrun ohne Architekturänderung: fünf UI-Korrekturen (Footer/Matrix, Dropdown-Lesbarkeit, kompakte Niveaukennzeichnung, Sprachaufenthalt ohne „Ja“, Top-Ausrichtung der Metadatenzellen), ISO-Tooltips entfernen, `ie_std` lokalisieren, französische Satzliste bereinigen, `new_FS`-Dokumentationskorrektur.

## Consulted Sources

- `docs/spec/platform-data-files.md` (L1-Darstellung, Standardvarietäten, UI-Regeln), `docs/spec/research-access.md`
- `docs/runbooks/test-and-ci.md`, `docs/runbooks/ui-change-workflow.md`
- `docs/agent-runs/2026-10-08_corpora-replace-en-fr-es.md` (offener Satzumbruch, `ie_std`), `2026-10-08_german-batch-ingest.md` (L1-Info-Indikator)

## Status der neun Punkte

| # | Punkt | Status | Tatsächliche Ursache |
|---|---|---|---|
| 1 | Footer / Vergleichsmatrix | teilweise reproduziert, Ursache behoben, Rest nicht reproduzierbar | Der Footer ist in Chromium geometrisch korrekt (geprüft mit echten Daten: 4 Korpora, DE/EN, hell/dunkel, 360–1920 px, bis zu 8000 px hohe Matrix; Footer beginnt immer nach dem Matrixinhalt). Reproduziert und behoben: die sticky Matrixzellen (`z-index` 4–8) lagen über der Top-App-Bar (`z-index` 4), weil der Matrix-Wrapper keinen eigenen Stacking-Context hatte. Zusätzlich gehärtet: `grid-template-rows` der Shell hatte ein Nullminimum (`minmax(0, 1fr)`), das den Inhalt bei definierter Höhe in die Footer-Zeile laufen lassen kann. Die exakt beschriebene Überlagerung durch den Footer ließ sich nur in Chromium prüfen (kein Firefox/WebKit installiert) und dort nicht auslösen. |
| 2 | Dropdown-Hover unlesbar | behoben | `color-scheme: light dark` auf `html, body` (`layout.css`) ließ native Select-Popups der Betriebssystem-Präferenz folgen, während Select-Farben aus den Theme-Tokens kamen (Standardtheme ist „hell“). Bei Theme ≠ OS entstanden Popup-Hervorhebung und Text in gegensätzlichen Schemata (z. B. weiße Hervorhebungsschrift auf hellem Grund). Die Regel stammt aus dem Mai (`ea39dde`, `ecd10ef`; vorher bereits in der Baseline), ein Oktober-Commit hat sie nicht geändert – eine Eingrenzung auf eine Oktober-Änderung war deshalb nicht möglich; der Fehler tritt nur auf, wenn Theme und OS-Präferenz auseinanderfallen. Fix: `color-scheme` pro Theme in `00_tokens.css`, `option`/`optgroup` zentral aus Tokens. Die eigenen Menüs (Nutzermenü, Segmented Controls) waren nicht betroffen. |
| 3 | Kompakte Niveaukennzeichnung | behoben | Schlüssel `research.comparison.self_placement_prefix`: `Niveau (selbst):` / `Level (self):`. Gilt für Sprecherkarten und den passenden Filter-Chip im Vergleich; `common.labels.level` (`Selbsteinordnung`) und alle anderen Anzeigen bleiben. Zusätzlich: Die Badge-Zeile war `nowrap` + `overflow: hidden`, mit den L1-Sprachnamen (seit 8.10.) wurde L1 trotz kürzerem Label noch abgeschnitten (bis zur Hälfte der Badges bei 1100–1400 px); die Zeile umbricht jetzt. |
| 4 | „Ja ·“ bei Sprachaufenthalt | behoben | `_compact_session_stay_summary` stellte `Ja`/`Yes` vor die Dauer. Jetzt nur die lokalisierte Dauer (`1 Monat`, `3,5 Monate`, `1 month`, `3 months`); ohne Aufenthalt `Keine`/`None`; `Ja`/`Yes` bleibt nur für bestätigten Aufenthalt ohne Dauer. Daten unverändert. |
| 5 | Metadaten oben ausrichten | behoben | `.pm-speaker-card__meta-item` und `.pm-profile-metadata__row` sind Grids mit Standard-`align-content: stretch`; neben einer höheren Zelle wuchsen die Auto-Zeilen, der Wert rutschte nach unten (Messung: 19,5 px → 76 px bzw. 20,8 → 44 px). `align-content: start`. |
| 6 | ISO-Tooltips / Info-Icons | behoben | Entfernt: Inline-Info-Indikator (Commit `a6a1561`) in `l1_display.py`, Template-/JS-Pfade (`title` am Vergleichs-Badge), `info-tooltip.js`-Inline-Logik, CSS (`.pm-l1`, `.pm-info-tip--inline`), i18n-Schlüssel `language.l1.tooltip`/`info_label`. Sprachnamen bleiben; ISO-Zuordnung (`get_l1_iso_reference`) und gespeicherte Codes unverändert. Andere Info-Icons (Set-Auswahl im Player, Vergleich, Profil) unangetastet. |
| 7 | `ie_std` | behoben | Zentrale Labels `research.shared.standard_variety.ie_std`: `Irisches Englisch` / `Irish English` (vorher `Irland`/`Ireland`). Code unverändert, andere Varietäten unverändert. |
| 8 | `french_text.txt` | behoben | Siehe unten. |
| 9 | `new_FS`-Dokumentationskorrektur | **offen** | Im Repository (Dateien, Verlauf, Branches, Commit-Nachrichten, Archivbaum, Run-Logs) kommt `new_FS` nirgends vor, auch keine Variante (`newfs`, `new-fs`). Der Sachverhalt lässt sich nicht rekonstruieren; es wurde bewusst keine unbelegte Änderung vorgenommen. Bitte den gemeinten Sachverhalt benennen. |

## Französische Satzliste (Punkt 8)

- Fehlerstelle: Zeilen 30/31 von `scripts/research_data_intake/import/french_batch_complete_20261008/french_text.txt` („Les beaux millionnaires restent rarement normaux, ⏎ car l’argent et le pouvoir ont une mauvaise influence.“; Umbruch mit Leerzeichen am Zeilenende). Dies war der einzige Umbruch; die Datei hatte 68 Zeilen.
- Korrektur: genau diese zwei Zeilen zu einer verbunden (das Leerzeichen nach dem Komma bleibt das einzige Trennzeichen); sonst byte-gleich. Jetzt 67 Zeilen, Reihenfolge und Wortlaut unverändert.
- Hash der Quelldatei (erwartet, da Dateiinhalt geändert): `fa5e3bba…490d269d` → `1132f299…e7a91b`. Originalzustand: `tmp/ui-qa/2026-10-09-corrections/french_text.before.txt`.
- Validierung: 67 Zeilen = 67 Katalogitems (`t_01`–`t_67`), Zeile für Zeile identisch zum Katalog `data/config/research_player/french/task_catalogs/text.json` (0 Abweichungen), keine leere Zeile.
- Bestandsdaten unverändert: Die Datei ist nur Textquelle (`provided_txt:french_text.txt` im Katalog) und ist weder im Archiv-Batch (`checksums.sha256`: Workbook, Reports, Payload) noch in einer Fixity-Baseline noch in Laufzeitartefakten referenziert; Katalog (`text.json` SHA-256 `0813b425…cab591`, mtime 2026-05-27), `data/` und das Archiv haben keine Dateien, die neuer als der Lauf wären. Kein Reimport, keine Neuausrichtung, keine Änderung an Item-IDs, Aufnahmen, Annotationen (TextGrids hatten bereits 67 Intervalle).
- Die Datei liegt in der git-ignorierten Import-Ablage und ist deshalb nicht Teil des Commits. Neue Tests: `app/tests/test_french_text_source.py` (Marker `data`; skippt ohne Datei).
- Nicht angefasst: die historische Kopie `promat_data_archive/praat_pipeline/catalogs/french_text.txt` (Stand 25.05., 68 Zeilen, derselbe Umbruch an Zeile 30/31, abweichende Apostrophe). Das Archiv ist ein Aufbewahrungsbestand; Entscheidung über Korrektur bleibt offen.

## Geänderte Bereiche

- CSS: `app/static/css/layout.css`, `00_tokens.css`, `20_layout.css`, `30_components.css`, `40_cards.css`
- JS: `app/static/js/modules/core/info-tooltip.js` (Inline-Teil zurückgenommen), `app/static/js/pages/research-comparison.js` (kein `title` am L1-Badge)
- Python: `app/src/app/l1_display.py` (nur noch Namensauflösung), `app/src/app/research_views.py`, `app/src/app/i18n.py`
- Tests: `test_l1_display.py`, `test_research_comparison.py`, `test_research_sessions.py`, `test_i18n_and_registry_integrity.py`, neu `test_theme_and_layout_css.py`, `test_french_text_source.py`; Browser-Smoke `scripts/qa/ci_browser_smoke.py` (ISO-Indikator-Prüfung ersetzt durch Prüfungen der Zielzustände)
- Spec: `docs/spec/platform-data-files.md` (L1-Darstellung ohne ISO-Indikator, `ie_std`-Label, Stays-Anzeige, Niveau-Label, Metadaten-Ausrichtung, Shell/Stacking, Select-Theming)

## Wichtige Entscheidungen

- `self_placement_prefix` gilt für Karten und Filter-Chip gemeinsam (ein Schlüssel, eine kompakte Kennzeichnung im Vergleich).
- Umbrechende Badge-Zeile statt weiterer Kürzung: Die L1-Namen („Kabylisch“, „Réunion-Kreolisch“) passen nie in eine Zeile mit dem Niveau; abschneiden wäre der eigentliche Fehler.
- `get_l1_iso_reference` bleibt als Datenmodell-Referenz erhalten (Test), wird aber nirgends präsentiert.

## Abweichungen

- Keine Abweichung von Spec, Dev/Prod-Parität oder Konventionen. Spec im selben Run nachgezogen.

## Verifikation

- `pytest` (App-Suite): 1319 passed, 2 skipped, 11 deselected vor den letzten Browser-/Smoke-Ergänzungen; ruff, compileall, `ci_governance_checks.py`, `validate_teaching_content.py`, JS-Tests (64) grün; `pytest -m data` für `test_french_text_source.py`: 2 passed.
- CI-Browser-Smoke gegen die Fixture-Runtime: 250 Checks, 0 Fehler (DE/EN: kein ISO-Indikator, Niveau-Badges, Top-Ausrichtung, Footer nach Matrix, Matrix-Isolation, Select-`color-scheme` je Theme bei entgegengesetzter OS-Präferenz, keine geclippten Badge-Zeilen). Mutationsprobe: Gegen den alten CSS-Stand schlagen 6 dieser Checks an.
- Browser mit echten lokalen Daten (`tmp/ui-qa/2026-10-09-corrections/`): Vergleich und Sprecher:innen in DE/EN, hell/dunkel, 390–1920 px; Messung der Badges (0 geclippt bei 1280/1400, 1100 ohne Clipping mit zwei Zeilen), Footer-Geometrie (32 Kombinationen), Metadaten-Offsets vorher/nachher.
- Native Select-Popups liegen außerhalb des Seiten-DOM und sind per Screenshot nicht prüfbar; belegt ist die berechnete Farbschema-/Farbzuordnung.

## Offene Punkte

- Punkt 9 (`new_FS`): Sachverhalt benötigt.
- Punkt 1: Falls der Footer-Effekt in Firefox/Safari oder mit einer bestimmten Matrix auftritt, bitte Browser und Route nennen.
- Archivkopie `praat_pipeline/catalogs/french_text.txt` mit demselben Umbruch: Korrektur ja/nein.
- Aus dem Vorlauf weiterhin offen: FR-L-0028 `needs_review`.
