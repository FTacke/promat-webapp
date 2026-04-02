# PROMAT Task- und Intake-Konsistenz

Datum: 2026-04-02

## Ziel

Die aktiven PROMAT-Standards fuer Research-Tasks, Session-Dateibenennung und Intake-Workbook-Struktur repo-weit konsistent nachziehen.

## Geänderte Bereiche

- aktive Task-Keys in Runtime, Seeds, Tests und Governance auf `wordlist`, `text`, `interview` gestellt
- aktive Intake-Mapping-Dateien auf das Workbook-Endmodell mit `Research_Person`, `Research_Session_Intake`, `Exposure` und breitem `Vocabularies`-Blatt umgestellt
- Dev-Session-Metadaten und Session-Dateinamen unter `data/sessions/spanish/` auf die neuen Task-Namen umgezogen
- veralteten Repo-Platzhalterordner mit legacy Session-Pfad entfernt

## Architekturwirkung

- Die technische Task-Semantik ist jetzt deckungsgleich in Code, Seed-Daten, Session-Metadaten und aktiver Doku.
- Intake-Regeln und spaetere Runtime-Projektion sprechen jetzt dieselbe Modellstruktur.
- Der spanische Research-Runtime-Baum enthaelt keinen zweiten aktiven Placeholder mehr mit nicht-kanonischem Session-Ordnernamen.

## Verifikation

- spanischer Dev-Seed erneut ausgefuehrt
- Session-Dateibenennung per Dateisystem-Bereinigung angepasst
- repo-weite Suchlaeufe gegen alte aktive Task-Terme und legacy Placeholder ausgefuehrt

## Offene Punkte

- Historische Logs unter `docs/start/`, `docs/agent-runs/` und dated `docs/research_pages/` bleiben als Historie unveraendert.

## Nächste sinnvolle Schritte

- spaetere Import-Implementierung direkt gegen das jetzt fixierte Intake-Mapping bauen
- historische Dokumente bei Bedarf gesammelt als Legacy-Referenzen kennzeichnen
