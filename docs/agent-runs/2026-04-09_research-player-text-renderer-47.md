# Erster produktiver Text-Renderer im Player

Datum: 2026-04-09

## Ziel

Den technischen Task `text` im bestehenden Research-Player von einem reinen Fallback auf eine erste echte produktive Player-Stufe heben, ohne den `wordlist`-Pfad oder die Player-Grundarchitektur zu brechen.

## Consulted Sources

- `docs/plans/player_comparison_phenomena.md`
- `docs/plans/player_comparison_phenomena_repo_implementation_plan.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `data/config/research_player/spanish/player_config.json`
- `data/config/research_player/spanish/task_catalogs/text.json`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/css/30_components.css`
- `app/tests/test_research_player_set_context.py`
- `docs/spec/research-player.md`

## Wichtige Entscheidungen

- Der erste produktive `text`-Renderer bleibt bewusst auf den belastbaren `sentence_list`-Modus aus `player_config.json` begrenzt.
- Der Renderer liest die sichtbaren Inhalte aus dem kanonischen `text`-Task-Katalog und koppelt sie an session-spezifische `alignment/text.json`-Artefakte statt freie Rekonstruktion zu betreiben.
- `set_id` filtert auch im `text`-Pfad taskgebunden den sichtbaren Ausschnitt; leere `text`-Ausschnitte rendern einen expliziten leeren Zustand.
- `focus_item` hebt im `text`-Pfad jetzt initial die relevante Satzlisten-Zeile hervor und scrollt sie in den sichtbaren Bereich, aber ohne Autoplay.
- Direkter `text`-Compare im Player bleibt in diesem Run bewusst noch nicht produktiv freigeschaltet; der Einzel-Session-Renderer ist echt, Compare für `text` noch nicht.

## Produktiver Stand nach diesem Run

- `text` rendert jetzt als echte Satzliste mit sichtbarer Nummer, `item_id`, Textinhalt und Clip-/Zeit-Metadaten, sofern belastbare Artefakte existieren.
- Task-Audio und itembezogene Clip-Aktionen funktionieren dort, wo `alignment/text.json` plus Split-Clips vorliegen.
- Der `text`-Pfad arbeitet sauber mit `set_id`, `focus_item`, Taskwechseln und dem corpus-spezifischen Label `Satzliste` zusammen.

## Ehrliche Grenzen

- Kein vorgetäuschter Token- oder Wort-Sync innerhalb der Sätze.
- Kein produktiver `running_text`-Renderer in diesem Run.
- Kein produktiver bounded Direct-Compare für `text` in diesem Run.

## Verifikation

- Neue strukturelle Tests für produktiven `text`-Renderpfad, Set-Filterung, leere `text`-Ausschnitte, Fokus-Auswertung, Taskwechsel und Route-Rendering.
- Bestehende Player-/Set-/Phenomena-/Comparison-Regressionen bleiben mitzuprüfen.

## Nächste sinnvolle Schritte

- Optional einen echten `running_text`-Renderer ergänzen, wenn der Satz-/Segmentfluss dafür belastbar modelliert werden kann.
- Danach prüfen, ob bounded Direct-Compare für `text` mit vertretbarer Komplexität und ehrlicher Degradation produktiv ergänzt werden kann.