# PROMAT Dev Example Seed 01

Datum: 2026-03-31

## Ziel

Lokalen Dev-Testbestand fuer 11 spanische Beispielpersonen aus den vorhandenen `data/example_data`-Fixtures herstellen, ohne eine zweite Dev-Architektur aufzubauen.

## Umgesetzter Stand

- Deterministisches Seed-Manifest fuer 11 fiktive Personen und Sessions unter `scripts/session_setup/dev_spanish_example_sessions.json` angelegt.
- Wiederholbares Python-Skript unter `scripts/session_setup/seed_dev_spanish_example_sessions.py` fuer die Uebernahme nach `data/sessions/spanish/{session_id}/` angelegt.
- `app/scripts/dev-setup.ps1` so korrigiert, dass fuer Auth-Migrationen und Admin-Seed bevorzugt die Workspace-`.venv` genutzt wird.
- Pro Session `metadata.json`, initial `raw/isolated_speech.wav` und `alignment/isolated_speech.TextGrid` erzeugt; die WAV-Zuordnung wurde im Folge-Run fachlich auf `source/isolated_speech.wav` korrigiert.
- Leere Session-Unterordner `source/`, `derived/` und `items/` als strukturelle Vorbereitung angelegt, aber bewusst nicht befuellt.
- Bestehende lokale Dev-DB-Kette bei PostgreSQL belassen; keine SQLite-Struktur oder Fallback-Logik eingefuehrt.

## Bewusst nicht umgesetzt

- Keine MP3-Dateien
- Kein Item-Splitting
- Keine weitergehenden JSON-Derivate
- Kein neuer Webapp-Reader fuer Forschungsdaten

## Verifikation

- Session-ID-Schema und Metadatenfelder gegen die Spezifikation geprueft.
- Vorhandene Beispiel-WAV- und TextGrid-Dateien deterministisch auf 11 Session-Ordner gemappt.
- Dev-Setup- und Compose-Stand fuer PostgreSQL gegen den aktuellen Runtime- und Config-Stand geprueft.