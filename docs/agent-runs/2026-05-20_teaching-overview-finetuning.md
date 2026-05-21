# Teaching-Finetuning für Root, Spanisch-Hub und Lesetypografie

Datum: 2026-05-20

## Ziel

Gezielter Finetuning-Run für die öffentlichen Teaching-Übersichtsseiten: präziser Root-Titel, konsequent zentrierte Header auf Root und Spanisch-Hub, ruhigere Introtypografie, reparierte Reading-Font auf Themenseiten sowie klare Available-vs-Pending-Semantik für Sprach- und Topic-Karten.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- Teaching-Builder und Root-Titel in `app/src/app/teaching_content.py` und `app/src/app/routes/public_content.py`
- Root-Card-Rendering in `app/templates/partials/_corpus_card.html`
- Teaching-Layout und Typografie in `app/static/css/20_layout.css` und `app/static/css/30_components.css`
- Spanisch-Hub-Indexe in `content/teaching/spanish/de/index.yaml` und `content/teaching/spanish/en/index.yaml`
- fokussierte Regressionen in `app/tests/test_teaching_content.py` und `app/tests/test_research_sessions.py`
- aktive Teaching-Regeln in `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- Der Root-Titel verwendet jetzt den bestehenden Landing-Titel `Aussprache unterrichten` / `Teach pronunciation`, während die Bereichs-Eyebrow `Unterricht` / `Teaching` bleibt.
- Root-Sprachen ohne freigegebene öffentliche Themenseite bleiben sichtbar, rendern aber als nicht klickbare Pending-Zeilen ohne CTA.
- Hub-Themen orientieren sich nicht mehr nur an Dateiexistenz: ein explizites `is_available: false` im Index übersteuert eine vorhandene Topic-Datei und hält die Karte bewusst im Pending-Zustand.
- Die blockierte Reading-Font auf Themenseiten wurde an der Ursache repariert: spezifische Teaching-Regeln in `30_components.css` hatten `font-family`, `font-size` und `line-height` für `.promat-content-block__text` und `.pm-teaching-rich-text__body` wieder auf UI-Typografie gesetzt und damit die Lesetext-Regeln aus `10_typography.css` praktisch neutralisiert.
- Hover wurde für verfügbare Sprach- und Topic-Karten auf denselben ruhigeren Charakter reduziert: leichtere Accent-Tönung, stärkeres Accent-Top-Border, nur minimaler Lift, kein schwebender Shadow-Effekt.

## Abweichungen

- Keine Abweichung von Routing-, Shell-, Research-Access- oder Runtime-Regeln.
- Repo-Instructions wurden nicht angepasst; die bestehenden Governance-Regeln waren für diesen Run ausreichend.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q -k "build_teaching_hub_page"` -> 5 bestanden
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_overview_keeps_language_selection_label or teaching_language_root_uses_shared_topbar_and_mobile_drawer or teaching_english_hub_stays_within_english_edition_topics"` -> 3 bestanden
- Desktop-Live-Prüfung auf `http://127.0.0.1:8010` via Browser-Tools für:
  - `/de/teaching`
  - `/de/teaching/spanish`
  - `/de/teaching/spanish/which-pronunciation`
- Desktop-DOM/Style-Checks bestätigt:
  - Root- und Hub-Header zentriert
  - Overview- und Hub-Orientierungstexte in Reading-Font
  - Themenseiten-Blocktext und Rich-Text wieder in Reading-Font
  - Pending-Root-Zeilen ohne Link- oder Fokusziele
- Reale 390px-Headless-Edge-Screenshots geprüft für:
  - `tmp/ui-qa/2026-05-20-teaching-overviews/de-teaching-mobile-edge.png`
  - `tmp/ui-qa/2026-05-20-teaching-overviews/de-teaching-spanish-mobile-edge.png`
  - `tmp/ui-qa/2026-05-20-teaching-overviews/de-teaching-which-pronunciation-mobile-edge.png`

## Offene Punkte

- Die Hover-Abnahme auf Desktop wurde visuell und über Live-DOM-Semantik geprüft, aber nicht als separater Screenshot-Artefaktensatz dokumentiert.
- Direkte Aufrufe der noch nicht freigegebenen Spanisch-Topic-Routen wurden in diesem Run nicht gesperrt; die Deaktivierung betrifft bewusst die öffentliche Karten- und Root-Navigation.

## Nächste sinnvolle Schritte

- Wenn weitere Teaching-Themen redaktionell vorbereitet, aber noch nicht öffentlich sein sollen, denselben Index-Schalter `is_available: false` weiterverwenden.
- Falls später auch direkte Dummy-Routen geblockt werden sollen, die Hub-/Topic-Router auf denselben Public-Availability-Schalter ausrichten statt einen zweiten Statuspfad einzuführen.
