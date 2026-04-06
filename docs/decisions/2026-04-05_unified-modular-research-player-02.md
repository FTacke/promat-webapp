# ADR: Unified Modular Research Player

Status: accepted

Datum: 2026-04-05

## Kontext

Die Research-IA von PROMAT kennt bereits `speakers`, `recordings`, `comparison` und `phenomena`, und eine kanonische Player-Detailroute ist strukturell vorbereitet. Ohne eine verbindliche Zielarchitektur würde der spätere Ausbau leicht in getrennte Wortlisten-, Text- oder Interview-Player zerfallen. Gleichzeitig braucht PROMAT eine saubere Erweiterbarkeit für Vergleich, Presets und korpusspezifische Renderarten, ohne dieselbe Audio-, Sync- und State-Logik mehrfach zu pflegen.

## Entscheidung

PROMAT verwendet für den Research-Bereich verbindlich einen einheitlichen modularen Player mit diesen Regeln:

- Es gibt genau einen gemeinsamen Research-Player für die ganze Webapp.
- `wordlist`, `text` und `interview` bleiben technische Task-Modi derselben Player-Basis.
- Unterschiede zwischen Aufgaben und Korpora werden über Render- und Kontextkonfiguration gelöst, nicht über getrennte Player-Produkte.
- Vergleich bleibt eine begrenzte Erweiterung derselben Player-Basis und ist kein zweiter Player.
- Phenomena startet denselben Player mit Preset-Kontext statt eines Spezial-Players.
- Gemeinsame Audio-, Sync-, Rendering- und Highlighting-Bausteine werden nur einmal definiert und später in allen Task-Modi wiederverwendet.

## Auswirkungen

- Zukünftige Code-Runs müssen den Player als gemeinsame Basisarchitektur implementieren und dürfen keine task-spezifischen Parallel-Frontends aufbauen.
- Routing, Zustandsmodell, Datenvertrag und Preset-Konfiguration bleiben auf eine einzige Player-Familie ausgerichtet.
- Korpusunterschiede wie Satzlisten- oder Textdarstellung werden zu Konfigurationsfragen statt zu Architekturverzweigungen.
- Vergleich und Phenomena können später auf derselben Player-Basis aufsetzen, ohne die Kernlogik erneut zu implementieren.

## Alternativen

- Separater Player pro Task: verworfen, weil dieselbe Audio-, Sync- und State-Logik mehrfach gepflegt werden müsste.
- Separater Vergleichs-Player: verworfen, weil Vergleich nur eine begrenzte Erweiterung derselben task-kompatiblen Basis sein soll.
- Phenomena-spezifischer Mini-Player: verworfen, weil kuratierte Sets als Kontext derselben Player-Architektur modelliert werden können.

## Referenzen

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/agent-runs/2026-04-05_research-player-target-architecture-23.md`