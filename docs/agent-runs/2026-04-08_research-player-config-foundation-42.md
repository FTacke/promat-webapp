# Research Player Config Foundation

Datum: 2026-04-08

## Ziel

Die fehlende file-backed Konfigurationsgrundlage fuer den Research-Bereich einfuehren: produktive spanische Player-Defaults, produktive spanische Phenomena-Presets, gemeinsamer Loader und Validator sowie Tests fuer die neue Preset- und Config-Basis.

## Consulted Sources

- `docs/plans/player_comparison_phenomena.md`
- `docs/plans/player_comparison_phenomena_repo_implementation_plan.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `data/config/research_player/README.md`
- `data/config/research_player/spanish/task_catalogs/wordlist.json`
- `data/config/research_player/spanish/task_catalogs/text.json`
- `app/src/app/config/data_conventions.py`
- `app/src/app/research_sessions.py`

## Geaenderte Bereiche

- `data/config/research_player/spanish/`
- `app/src/app/`
- `app/tests/`
- `data/config/research_player/README.md`
- `docs/agent-runs/`

## Wichtige Entscheidungen

- `spanish/player_config.json` bleibt minimal und definiert nur die derzeit aktiven, spezifizierten `text`-Defaults.
- Fuer Spanisch wurde `text.default_render_mode = sentence_list` und `text.display_label = Satzliste` gesetzt, weil der aktuelle spanische `text`-Katalog fachlich eine Satzliste ist und bereits denselben sichtbaren Labelwert fuehrt.
- `phenomena_presets.json` wurde bewusst klein, aber produktiv angelegt: mehrere kuratierte Presets mit realen, validierten `wordlist`- und `text`-Referenzen statt Dummy-Daten.
- Doppelte `task + item_id`-Referenzen innerhalb eines Presets gelten als ungueltig, damit die file-backed Presets spaeter direkt in ein Set-Modell ueberfuehrt werden koennen.

## Abweichungen

- Keine DB- oder Set-Implementierung vorgenommen.
- Keine UI-Integration fuer `comparison`, `phenomena` oder `player` vorgenommen.

## Verifikation

- Neuer Loader in `app/src/app/research_presets.py` implementiert.
- Spanische `player_config.json` und `phenomena_presets.json` eingefuehrt.
- Tests fuer gueltige und ungueltige Preset-/Config-Faelle ergaenzt.

## Offene Punkte

- Der naechste Run sollte auf dieser Basis das Postgres-Set-Modell und die Auth-gebundene Ownership-Schicht bauen.
- Optional kann danach eine leichte HTML-Integration fuer `phenomena` und `comparison` folgen, die die neue file-backed Config konsumiert.

## Naechste sinnvolle Schritte

- Postgres-Schema fuer Research-Sets einfuehren.
- Auth-gebundene Set-API mit denselben `task + item_id`-Referenztypen bauen.
- Danach `phenomena` und `comparison` an den neuen Loader anschliessen.
