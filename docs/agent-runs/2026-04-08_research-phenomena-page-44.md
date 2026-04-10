# Research Phenomena Page

Datum: 2026-04-08

## Ziel

Die Platzhalterseite `/{ui_lang}/research/{language}/phenomena` als echte, preset- und draft-basierte Forschungsoberfläche umsetzen, ohne bereits den vollen Vergleichs-Workbench oder eine große Player-Integration vorwegzunehmen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `docs/spec/research-player.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `app/src/app/routes/public.py`
- `app/src/app/routes/public_content.py`
- `app/src/app/research_views.py`
- `app/src/app/research_presets.py`
- `app/src/app/research_sets.py`

## Geänderte Bereiche

- dedizierter `phenomena`-View-Builder in `app/src/app/research_views.py`
- Research-Route-Sonderbehandlung in `app/src/app/routes/public.py`
- neue Template-Datei `app/templates/pages/research_phenomena.html`
- neue Seitenlogik `app/static/js/pages/research-phenomena.js`
- neue Layout-/Komponentenstile in `app/static/css/20_layout.css` und `app/static/css/30_components.css`
- neue Tests in `app/tests/test_research_phenomena.py`
- Spec-Updates in `docs/spec/research-access.md` und `docs/spec/research-player.md`

## Wichtige Entscheidungen

- Die `phenomena`-HTML-Seite bleibt oeffentlich renderbar, damit Preset-Katalog und Launcherstruktur in der Research-IA sichtbar bleiben.
- Draft-Erzeugung, `set_id`-Laden und Bearbeitung laufen ausschliesslich owner-gebunden ueber `/api/research/sets`.
- Presets werden erst beim expliziten Oeffnen materialisiert; ein `preset_id` in der URL dient als Oeffnungsabsicht fuer die Seitenlogik und erzeugt keinen serverseitigen Draft beim HTML-Rendern.
- Der Player-Handoff bleibt absichtlich klein: `phenomena` liefert task- und sessionbasierte Start-URLs mit `set_id`/`preset_id`, ohne den bestehenden Player groesser umzubauen.

## Abweichungen

- Keine Abweichung von der aktiven Routing-, Datenraum- oder Owner-Set-Spezifikation.

## Verifikation

- statische Fehlerpruefung der geaenderten Python-, Template-, JS- und CSS-Dateien
- neue gezielte Tests fuer Builder und Route-Rendering in `app/tests/test_research_phenomena.py`

## Offene Punkte

- Die Vergleichsseite ist weiterhin nur Launcher-Ziel und noch keine vollwertige set-basierte Workbench.
- Der Player nimmt `set_id` und `focus_item` derzeit nur als Hand-off-Kontext mit; die inhaltliche Nutzung dieses Kontexts bleibt Anschlussarbeit.

## Nächste sinnvolle Schritte

- die `comparison`-Seite auf denselben Set-Kontext umstellen
- `set_id`- und `focus_item`-Kontext im Player produktiv auswerten
- optional ein Speichern-unter fuer Drafts direkt auf der `phenomena`-Seite anbinden