# PROMAT Research Data Intake Scripts Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` und `scripts/AGENTS.md` für Arbeiten unter `scripts/research_data_intake/`.

## Regeln

- Dieser Bereich enthält nur Intake- und Ableitungsschritte für forschungsbezogene Session-Daten.
- Inputs, Outputs und Seiteneffekte müssen pro Skript klar erkennbar bleiben.
- Änderungen an Dateipfaden, Artefakten, IDs, Task-Semantik oder Ableitungsverträgen erfordern im selben Run die passende Aktualisierung unter `docs/spec/`.
- Wiederholbare Arbeitsabläufe werden unter `docs/runbooks/` dokumentiert, nicht als zweite Soll-Ebene in diesem Ordner.
- Batch-Eingänge bleiben Drop-in-basiert; Skripte dürfen keine manuelle Pflichtstruktur mit `processed/`, `raw/` oder `intake_data/` voraussetzen.
- `data/sessions/` ist Runtime-only und darf nur finale JSON/MP3-Artefakte enthalten.
- Langzeitarchivierung liegt unter `PROMAT_LOCAL_ARCHIVE_ROOT` außerhalb des Repo-Workspaces und ist session-zentriert.
- Upload-Pakete sind explizite Allowlist-Exporte aus validierten Runtime-Artefakten und optionalen DB-Payloads.
- Research-Intake-Runs dürfen `content/`, Teaching-Inhalte und Teaching-Media nicht verändern, außer der Scope verlangt es ausdrücklich.
- Dateiklassifikation für Person, Task und Rolle bleibt explizit dateinamengetrieben; bei Konflikten wird reportet oder fehlgeschlagen, nicht geraten.

## No-Go

- Keine allgemeinen Dev- oder Bootstrap-Skripte in diesem Bereich mischen.
- Keine Public-Export-Schritte in diesem Bereich, wenn sie nicht Teil des expliziten allowlist-basierten Upload-Pakets sind.
- Keine konkurrierenden aktiven Verträge in lokalen Notizen oder Ad-hoc-Markdown-Dateien aufbauen.
- Keine WAV-, TextGrid-, XLSX- oder `secure/`-Artefakte in Runtime-Session-Bäume kopieren.