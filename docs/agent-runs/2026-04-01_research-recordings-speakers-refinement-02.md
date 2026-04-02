# Research Recordings Speakers Refinement 02

Datum: 2026-04-01

## Ziel

Die erste Umsetzung von `recordings`, `speakers` und dem Sprecherprofil konzeptionell nachschaerfen: ruhigere `speakers`, klarer task-first fuer `recordings`, ueberarbeitete Profilseite sowie konsistente Einfuehrung von `stays_in_target_country`, `origin_country` und `origin_region` durch Webapp, Seeds, `metadata.json` und Importdokumentation.

## Consulted Sources

* `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
* `AGENTS.md`
* `app/AGENTS.md`
* `docs/AGENTS.md`
* `scripts/AGENTS.md`
* `.github/instructions/repo.instructions.md`
* `app/src/app/runtime_paths.py`
* `app/src/app/config/__init__.py`
* `docker-compose.dev-postgres.yml`
* `app/infra/docker-compose.prod.yml`
* `app/migrations/0002_create_analytics_tables.sql`
* `app/src/app/research_sessions.py`
* `app/src/app/research_views.py`
* `scripts/session_setup/seed_dev_spanish_example_sessions.py`
* `scripts/session_setup/dev_spanish_example_sessions.json`
* `scripts/import/README.md`
* `docs/research_pages/promat_recordings_speakers.md`

## Geaenderte Bereiche

* Research-Reader und View-Modelle unter `app/src/app/`
* Forschungstemplates unter `app/templates/pages/`
* Workbench-spezifische Styles unter `app/static/css/`
* spanische Dev-Seeds unter `scripts/session_setup/` und `data/sessions/spanish/`
* Importdokumentation unter `scripts/import/`
* Referenzdokumentation unter `docs/research_pages/` und `docs/`

## Wichtige Entscheidungen

* `stays_in_target_country` ist jetzt das kanonische boolesche/nullable Feld fuer die bisher zu unklare Exposure-Logik; historische Exposure-Felder werden nur noch als Kompatibilitaetsquelle gelesen.
* Native-Speaker-Daten werden aktiv ueber `standard_variety`, `origin_country` und `origin_region` modelliert; lernendentypische Felder `current_region` und `childhood_region` bleiben fuer Lernendenprofile reserviert.
* `recordings` und `speakers` verwenden auf Desktop keine Sidebar-Filter mehr, sondern denselben ruhigen vertikalen Arbeitsfluss mit Full-Width-Filtercontainern.
* Es wurde bewusst keine neue Research-Datenbankmigration als ungenutzte Parallelstruktur eingefuehrt, weil im aktiven Repo weiterhin keine verdrahtete Research-Metadatentabelle existiert.
* Stattdessen fixiert `scripts/import/session_metadata_xlsx_mapping.md` das kanonische XLSX-/Metadaten-/spaetere-DB-Mapping fuer die naechste Importphase.

## Abweichungen

* Keine Abweichung von Runtime-Grenzen, Session-Struktur oder Dev/Prod-Paritaet eingefuehrt.
* Der Research-Datenbankteil bleibt dokumentiert, aber noch nicht als laufender Importpfad implementiert; das ist bewusst, um keine zweite halbfertige Datenquelle neben `metadata.json` zu schaffen.

## Verifikation

* `seed_dev_spanish_example_sessions.py` mit aktualisiertem Manifest ausgefuehrt; 11 spanische Dev-Sessions wurden erfolgreich neu geschrieben.
* Fehlerpruefung fuer die angepassten Python-, Template- und CSS-Dateien ohne verbleibende Befunde ausgefuehrt.
* Stichproben auf regenerierten `metadata.json`-Dateien fuer Lernenden- und Native-Speaker-Eintraege geprueft.

## Offene Punkte

* Die Research-Webapp liest weiterhin direkt dateibasiert; ein spaeterer DB-Import muss das dokumentierte Mapping noch praktisch umsetzen.
* Die aktuelle Dev-Datenbasis dokumentiert Aufgaben weiterhin nur eingeschraenkt; die Task-Panels bereiten die Zielstruktur vor, ohne schon den Player fachlich auszubauen.
* Die app-weite englische Routenverfuegbarkeit ausserhalb dieses Runs bleibt unveraendert.

## Naechste sinnvolle Schritte

* Einen echten XLSX-Importschritt unter `scripts/import/` bauen, der direkt auf dem neuen Mapping basiert.
* Anschliessend den Player fachlich um Audio-, Transkript- und Task-spezifische Inhalte erweitern.
* Bei Bedarf danach eine echte Research-Metadatentabelle einfuehren, aber nur zusammen mit realem Import- und Laufzeitwiring.