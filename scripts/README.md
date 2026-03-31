# scripts

Root-Skripte bündeln Entwicklungs-Entrypoints und die vorbereitete Verarbeitungspipeline.

- `dev-setup.ps1` und `dev-start.ps1` delegieren an die App-Implementierung unter `app/scripts/`.
- `import/` ist für Datenimport vorgesehen.
- `session_setup/` ist für Session-Anlage und Metadatenvorbereitung vorgesehen.
- `audio_conversion/` ist für Audio-Konvertierung vorgesehen.
- `item_split/` ist für Item-Splitting vorgesehen.
- `export_to_public/` ist für gezielte Exporte nach `public/` vorgesehen.
