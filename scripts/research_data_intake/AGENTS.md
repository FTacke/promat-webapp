# PROMAT Research Data Intake Scripts Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` und `scripts/AGENTS.md` für Arbeiten unter `scripts/research_data_intake/`.

## Regeln

- Dieser Bereich enthält nur Intake- und Ableitungsschritte für forschungsbezogene Session-Daten.
- Inputs, Outputs und Seiteneffekte müssen pro Skript klar erkennbar bleiben.
- Änderungen an Dateipfaden, Artefakten, IDs, Task-Semantik oder Ableitungsverträgen erfordern im selben Run die passende Aktualisierung unter `docs/spec/`.
- Wiederholbare Arbeitsabläufe werden unter `docs/runbooks/` dokumentiert, nicht als zweite Soll-Ebene in diesem Ordner.

## No-Go

- Keine allgemeinen Dev- oder Bootstrap-Skripte in diesem Bereich mischen.
- Keine Public-Export-Schritte in diesem Bereich, wenn sie nicht Teil der geschützten Intake- oder Ableitungspipeline sind.
- Keine konkurrierenden aktiven Verträge in lokalen Notizen oder Ad-hoc-Markdown-Dateien aufbauen.