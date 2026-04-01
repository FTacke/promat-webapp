# Session Storage Logic Alignment 02

Datum: 2026-04-01

## Ziel

Die bereits eingefuehrte Audio-/Alignment-/Items-Logik an den noch zu impliziten Stellen nachschaerfen, insbesondere in `data/`, in der Seed-Doku und in den Dev-Session-Metadaten.

## Consulted Sources

- `data/README.md`
- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `docs/conventions/README.md`
- `scripts/session_setup/README.md`
- `scripts/session_setup/seed_dev_spanish_example_sessions.py`
- bestehende `metadata.json` unter `data/sessions/spanish/`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`

## Geaenderte Bereiche

- `data/README.md`
- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `docs/conventions/README.md`
- `scripts/session_setup/README.md`
- `scripts/session_setup/seed_dev_spanish_example_sessions.py`
- bestehende spanische Dev-Session-Metadaten unter `data/sessions/spanish/`

## Wichtige Entscheidungen

- Die Audio-Ebenen `raw`, `source` und `derived` sind nun auch direkt in `data/README.md` normativ beschrieben.
- Die spanischen Dev-Beispiel-WAVs werden nun nicht nur strukturell, sondern auch in den Session-Notizen explizit als `source` ohne vorhandene `raw`-Master beschrieben.
- Die Alignment-JSON-Logik bleibt verbindlich unter `alignment/{task}.json`; `items/` ist weiterhin nur fuer Split-MP3s vorgesehen.
- Die bestehende `.github`-Governance deckt diese Architekturregeln bereits ausreichend ab und wurde in diesem Nachschaerfungslauf daher nicht erneut erweitert.

## Abweichungen

- Keine Architekturabweichung eingefuehrt.

## Verifikation

- Seed-Skript erneut ausgefuehrt, damit die geschärften `notes`-Felder in die 11 spanischen Dev-Sessions geschrieben werden.
- Dokumentation auf konsistente Beispiele fuer interne Item-Dateinamen und die Alignment-JSON-Pipeline geprueft.
- `.github` gegen die verlangten Architekturregeln abgeglichen und bewusst unveraendert gelassen, weil die benoetigten Normsätze bereits vorhanden sind.

## Offene Punkte

- Alignment-JSON-Erzeugung, Gesamt-MP3-Erzeugung und Item-Splitting sind weiterhin nicht implementiert.

## Naechste sinnvolle Schritte

- `TextGrid -> alignment/{task}.json` als kanonischen naechsten Pipeline-Schritt implementieren.
- Danach Gesamt-MP3 aus `source/{task}.wav` und anschliessend Item-Splitting anhand der Alignment-JSON ergänzen.