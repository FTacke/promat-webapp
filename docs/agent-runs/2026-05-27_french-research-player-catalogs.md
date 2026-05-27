# 2026-05-27 French research-player catalogs

Datum: 2026-05-27

## Ziel

Den fehlenden Ordner `data/config/research_player/french/` mit kanonischen `wordlist`- und `text`-Task-Katalogen aus den bereitgestellten TXT-Dateien anlegen und loader-kompatibel machen.

## Consulted Sources

- `data/config/research_player/README.md`
- `data/config/research_player/english/player_config.json`
- `data/config/research_player/english/task_catalogs/wordlist.json`
- `data/config/research_player/english/task_catalogs/text.json`
- `data/config/research_player/spanish/player_config.json`
- `data/config/research_player/spanish/task_catalogs/text.json`
- `app/src/app/research_presets.py`
- `app/tests/test_research_presets.py`
- Root `AGENTS.md`, `docs/AGENTS.md`, `.github/instructions/repo.instructions.md`

## Geänderte Bereiche

- `data/config/research_player/french/player_config.json`
- `data/config/research_player/french/task_catalogs/wordlist.json`
- `data/config/research_player/french/task_catalogs/text.json`
- `app/tests/test_research_presets.py`

## Wichtige Entscheidungen

- Das französische `text`-Material wurde als `connected_text` unter dem technischen Task-Key `text` modelliert, mit laufenden Item-IDs `t_01 ...`, weil der User explizit die englische Nummerierungsform für die Satzitems verlangt hat.
- Die Wordlist-Einträge übernehmen die Reihenfolge und Textformen aus der bereitgestellten TXT-Quelle; sichtbare Rand-Whitespace-Artefakte aus der Attachment-Darstellung wurden nicht als semantischer Inhalt übernommen.
- Für die französische Sprache wurde ein minimales `player_config.json` ergänzt, damit Loader und Player dieselbe Konfigurationsfamilie wie bei Englisch und Spanisch vorfinden.

## Abweichungen

- Keine Abweichung von aktiven Specs oder Repo-Konventionen.

## Verifikation

- Repo-Smoke-Test in `app/tests/test_research_presets.py` für französische Task-Kataloge und `player_config.json` ergänzt.
- Nach dem Patch gezielter Pytest-Lauf für `app/tests/test_research_presets.py` vorgesehen.

## Offene Punkte

- Kein `phenomena_presets.json` für Französisch angelegt, weil der User nur die `task_catalogs` beauftragt hat und die bestehende Runtime dafür keinen zusätzlichen Pflicht-Loader aufruft.

## Nächste sinnvolle Schritte

- Falls für Französisch kuratierte Phänomen-Einstiege gebraucht werden, ein passendes `phenomena_presets.json` mit validen `wordlist`-/`text`-Referenzen ergänzen.