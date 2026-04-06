# Spanish Text Task Catalog 29

Datum: 2026-04-06

## Ziel

Den kanonischen spanischen `text`-Task-Katalog als maschinenlesbare Inhalts-Source-of-Truth anlegen und die Repo-Spezifikation dafür normativ festziehen, ohne bereits Produktionslogik für `alignment/text.json`, `derived/text.mp3` oder Token-Ableitung zu bauen.

## Consulted Sources

- `AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/spec/research-access.md`
- `docs/runbooks/research-wordlist-production.md`
- `docs/agent-runs/2026-04-06_task-catalog-foundation-26.md`
- `data/config/research_player/spanish/task_catalogs/wordlist.json`
- erwartete Referenz: `docs/model_mds/02_Spanisch_Satzliste.pdf`
- user-provided canonical sentence-list text from chat message dated 2026-04-06

## Geänderte Bereiche

- `data/config/research_player/spanish/task_catalogs/text.json`
- `data/config/research_player/README.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/agent-runs/2026-04-06_spanish-text-task-catalog-29.md`

## Wichtige Entscheidungen

- `data/config/research_player/spanish/task_catalogs/text.json` ist jetzt der kanonische spanische `text`-Katalog und damit die operative Inhalts-Source-of-Truth für die Satzliste.
- Die aktuelle spanische `text`-Ausprägung wird als Satzliste modelliert, aber der technische Task-Key bleibt `text`.
- Der Katalog speichert drei maschinenlesbare Gruppen `D`, `QY` und `QW` mit neutralen `group_type`-Werten statt einer Vermischung mit Interview-`segments`.
- Sichtbare `item_number`-Werte bleiben `D1` bis `QW10`, während stabile technische IDs getrennt als `d_01` bis `qw_10` modelliert sind.
- Token-Logik und `wordlist_item_ref` bleiben bewusst aus dem Katalog heraus und sind für spätere session-spezifische `alignment/text.json`-Dateien vorgesehen.

## Abweichungen

- Die als Arbeitsquelle genannte Referenzdatei `docs/model_mds/02_Spanisch_Satzliste.pdf` war im aktuellen Workspace nicht vorhanden.
- Der Run dokumentiert diese PDF daher nur als beabsichtigte Provenienz- und Ordnungsreferenz im Katalog, während die exakten `text`-Werte vollständig aus dem user-provided kanonischen Text aufgebaut wurden.

## Verifikation

- `text.json` wurde vollständig mit `50` Items aufgebaut: `D1` bis `D30`, `QY1` bis `QY10`, `QW1` bis `QW10`.
- Die drei Gruppen `D`, `QY` und `QW` wurden als top-level `groups` mit neutralen `group_type`-Werten modelliert.
- Die Specs wurden so angepasst, dass `text.json` jetzt normativ als kanonische Inhaltsquelle für künftige `text`-Ableitungen geregelt ist.
- Token- und `wordlist_item_ref`-Logik wurden ausdrücklich auf spätere session-spezifische Alignment-Dateien begrenzt.

## Offene Punkte

- Produktionslogik für `alignment/text.json`, `derived/text.mp3`, Split-Audio und Token-Ableitung ist in diesem Run bewusst nicht umgesetzt.
- Wenn die Referenz-PDF später ins Repo zurückkehrt oder ergänzt wird, sollte ihre Pfadreferenz im Katalog gegen den tatsächlichen Workspace-Stand gegengeprüft werden.

## Nächste sinnvolle Schritte

- Einen reinen Produktionsvorbereitungs- oder Implementierungs-Run für den spanischen `text`-Pfad planen.
- Dabei `alignment/text.json` als session-spezifische Ableitung aus `text.json`, TextGrid und Audio aufbauen.
- Erst im folgenden Alignment-Run Token-Ebene und optionale `wordlist_item_ref`-Referenzen ergänzen.