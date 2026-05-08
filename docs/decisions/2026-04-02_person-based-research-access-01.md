# ADR: Personbasierter Research-Zugang und kanonische Research-IDs

Status: accepted, partially superseded on 2026-05-08

Datum: 2026-04-02

## Kontext

Die bisherige Dev- und Doku-Lage mischte eine personbasierte Aggregationsidee mit älteren IDs, in denen Level, L1 oder Standardvarietät direkt in `session_id` und teils implizit auch in Personenbeispiele codiert waren. Historisch war daneben noch eine eigenständige session- und taskbasierte `recordings`-Seite vorgesehen; diese Seite wurde am 2026-05-08 aus der aktiven IA entfernt. Für Native Speaker sollten Vergleichsprofile außerdem keine lernendenähnliche Multi-Session-Biographie bilden.

## Entscheidung

PROMAT verwendet für den aktiven Research-Zugang verbindlich diese Regeln:

- `person_id = {CORPUS_CODE}-{SPEAKER_MARKER}-{NNNN}`
- `session_id = {person_id}-{YYYY}-S{NN}`
- `speakers` aggregiert strikt pro `person_id` und zeigt genau eine Personenseite pro Person.
- Auf der Personenseite bleiben alle Sessions sichtbar; eine Session kann optional per Query-Parameter fokussiert werden.
- Der session- und tasknahe Zugriff erfolgt über kanonische Player-Links aus `speakers` und dem Profil; eine eigenständige `recordings`-Seite gehört nicht mehr zur aktiven IA.
- Native-Speaker-Vergleichsprofile bleiben ein Sonderfall mit genau einer Session pro nativer `person_id` und ohne Interview-Task.
- Laufzeitquelle bleibt ausschließlich die dateibasierte Session-Metadatenstruktur unter `data/sessions/{language}/{session_id}/metadata.json`.

## Auswirkungen

- Person- und Session-Begriffe sind repo-weit klar getrennt.
- Seed-, Import- und Doku-Beispiele müssen die neuen ID-Formate und die Person-/Session-Kopplung einhalten.
- Runtime-Validierung wird strenger, weil Session-Verzeichnis, `session_id`, `person_id`, `recording_year` und Sprecherstatus konsistent sein müssen.
- Dev-Beispieldaten müssen echte Mehrfach-Sessions für Lernenden-Personen enthalten, damit das personbasierte UI realistisch prüfbar bleibt.

## Alternativen

- Altes Session-Format mit Level, L1 oder Standardvarietät in der ID beibehalten: verworfen, weil Person- und Session-Semantik unklar bleiben.
- Zweite Runtime-Datenquelle für Personenprofile einführen: verworfen, weil der aktive Architekturstand dateibasierte Session-Metadaten als einzige Research-Laufzeitquelle vorsieht.
- Separate Session-Profilseiten zusätzlich zur Personenseite beibehalten: verworfen, weil der Research-Zugang explizit personbasiert sein soll.

## Referenzen

- `docs/agent-runs/2026-04-02_person-based-research-access-09.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`

## Statushinweis 2026-05-08

Die ID- und Person-/Session-Regeln dieser ADR bleiben gültig. Nicht mehr gültig ist die frühere Annahme einer eigenständigen aktiven `recordings`-Research-Seite; der aktuelle Sollstand steht in `docs/spec/research-access.md` und `docs/spec/research-capabilities.md`.