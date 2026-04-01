# Dev Example Spanish Seed 01

Datum: 2026-03-31

## Ziel

Einen rein lokalen Dev-Testdatensatz fuer 11 vollstaendig fiktive spanische Sessions aus den vorhandenen Beispiel-WAV- und TextGrid-Dateien anlegen, ohne SQLite oder eine parallele Dev-Struktur einzufuehren.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `app/src/app/config/data_conventions.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- `app/scripts/dev-setup.ps1`
- `app/migrations/0001_create_auth_schema_postgres.sql`
- `app/migrations/0002_create_analytics_tables.sql`

## Geaenderte Bereiche

- `app/scripts/dev-setup.ps1` fuer die kanonische Nutzung der Workspace-`.venv` bei Postgres-Migrationen
- `scripts/session_setup/` fuer den wiederholbaren Dev-Seed von Beispiel-Sessions
- lokale Session-Daten unter `data/sessions/spanish/`
- Run-Dokumentation unter `docs/agent-runs/`
- historische Start-Chronik unter `docs/start/`

## Wichtige Entscheidungen

- Die 11 Dev-Beispielsessions werden dateibasiert unter `data/sessions/spanish/{session_id}/` angelegt, weil im aktuellen Repo-Stand keine separate Forschungsdaten-DB fuer Sessions vorhanden ist.
- Die bestehende lokale Postgres-Kette bleibt unveraendert die einzige Dev-DB fuer Auth/Core-nahe Logik; es wurde keine SQLite-Fallback- oder Parallelstruktur eingefuehrt.
- `app/scripts/dev-setup.ps1` wurde an `app/scripts/dev-start.ps1` angeglichen und nutzt nun bevorzugt die Workspace-`.venv`, damit die lokale Postgres-Migration nicht an einer falschen Python-Installation scheitert.
- `metadata.json` bleibt minimal auf den aktuellen Projektstand zugeschnitten: Kernmetadaten plus genau ein `isolated_speech`-Task und nur die tatsaechlich vorhandenen Dateien.
- `source/`, `derived/` und `items/` werden als Session-Unterordner vorbereitet, aber bewusst nicht mit kuenstlichen Derivaten befuellt.

## Abweichungen

- Keine Architekturabweichung eingefuehrt.
- Die bereits im Repo verfolgte Platzhalter-Session `ES-L-DE-B2-24-001` bleibt lokal unangetastet und ist nicht Teil des neuen 11er-Dev-Seeds.

## Verifikation

- Runtime-, Config- und Compose-Dateien wurden gegen die Spezifikation und Dev/Prod-Paritaet geprueft.
- Das Seed-Manifest wurde gegen Sprecherstatus, Session-ID-Praefix, `recording_year=2026` und `standard_variety` validiert.
- Der Seed wurde lokal ausgefuehrt und die Zielstruktur unter `data/sessions/spanish/` fuer alle 11 Beispielpersonen erzeugt.
- Die bestehende lokale Dev-Setup-Kette mit Postgres-Migrationen wurde verifiziert; Auth/Core bleibt auf PostgreSQL.

## Offene Punkte

- Im aktuellen Webapp-Stand existiert noch kein Session-Reader fuer Forschungsdaten; die Daten liegen im kanonischen Format bereit, werden aber noch nicht ueber UI-Routen aufgeloest.
- Fuer spaetere Pipeline-Stufen fehlen bewusst weiterhin MP3-Konvertierung, Item-Splitting und JSON-Derivate.

## Naechste sinnvolle Schritte

- MP3-Konvertierung fuer `source/isolated_speech.wav` nach `derived/isolated_speech.mp3` als expliziten Folgeschritt unter `scripts/audio_conversion/` ergaenzen.
- Danach Item-Splitting fuer `isolated_speech` unter `scripts/item_split/` implementieren.
- Anschliessend ein kleines dateibasiertes Session-Listing in der Webapp einfuehren, das `metadata.json` unter `data/sessions/{language}/` ausliest.