# import

Import-Artefakte fuer die Ueberfuehrung externer Forschungsdaten in die kanonische PROMAT-Session-Struktur.

- Die aktuell aktive Research-Webapp liest Sessions direkt aus `data/sessions/{language}/{session_id}/metadata.json`.
- Ein eigener Research-DB-Importpfad ist im Repo derzeit noch nicht verdrahtet; spaetere Datenbankarbeit soll sich deshalb an denselben kanonischen Feldnamen orientieren.
- Das verbindliche XLSX-/Metadaten-/DB-Mapping fuer den aktuellen Feldstand liegt in `session_metadata_xlsx_mapping.md` und `session_metadata_xlsx_mapping.json` in diesem Ordner.
