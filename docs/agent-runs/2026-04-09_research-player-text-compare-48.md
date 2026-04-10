# Produktiver bounded Text-Compare im Player

Datum: 2026-04-09

## Ziel

Den bestehenden bounded Direct-Compare des Research-Players so erweitern, dass `text` im bestehenden session-zentrierten Player produktiv als `1+1`-Vergleich nutzbar wird, ohne neue Routefamilien, ohne `mixed`-Task und ohne Regression des produktiven `wordlist`-Compare.

## Consulted Sources

- `docs/plans/player_comparison_phenomena.md`
- `docs/plans/player_comparison_phenomena_repo_implementation_plan.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/js/pages/research-comparison.js`

## Umgesetzter Stand

- `text` nutzt jetzt im bestehenden Player denselben bounded Compare-Rahmen wie `wordlist`, weiterhin über dieselbe Player-Route und optionales `compare_session`.
- Der produktive `text`-Compare bleibt auf den stabilen `sentence_list`-Pfad begrenzt.
- Compare-Matching erfolgt ausschließlich über stabile `item_id`-Werte, nicht über Textgleichheit oder Wort-/Token-Sync.
- Ein aktives `set_id` filtert im `text`-Compare beide Seiten auf denselben taskgebundenen Satzlisten-Ausschnitt.
- `focus_item` markiert und revealt die relevante Compare-Zeile, ohne Autoplay, auch wenn die Sekundärseite dort fehlt.

## Audio- und Clip-Logik

- Der Compare-Modus übernimmt die bestehende bounded Player-Philosophie: keine chaotische Doppelwiedergabe, sondern geordnete Item-Prüfung.
- `Beide abspielen` bleibt der Default und spielt im Compare-Fall Primär- und Sekundärseite nacheinander auf Satz-/Item-Ebene ab.
- `compare_mode=manual` bleibt die minimale manuelle Alternative für per-side Item-Prüfung.
- Fehlende Split-MP3s entfernen nur die Download-/Split-Signale; sie schalten keine vorgetäuschte feinere Präzision frei und brechen die Compare-Ansicht nicht.

## Graceful Degradation

- Fehlt die Vergleichssession oder ihr `alignment/text.json`, degradiert der Player sauber auf den produktiven Single-Session-`text`-Renderer mit explizitem Hinweis.
- Fehlen einzelne Vergleichsitems, bleiben Primärzeilen nutzbar und die Sekundärseite markiert die Lücken sichtbar pro Zeile.
- Fehlt Owner-Kontext für `set_id`, bleibt die Seite erreichbar und leak-frei; Set-Inhalte werden nicht serverseitig offengelegt.
- Kleine Viewports bleiben bei der bestehenden ehrlichen Client-Degradation auf Single-Session.

## Handoffs

- Direkte Player-URLs aus `comparison` mit `task=text`, `set_id`, `focus_item` und optionalem `compare_session` landen jetzt produktiv im `text`-Compare.
- `comparison` ergänzt Player-Handoffs clientseitig minimal um eine passende zweite Session, wenn eine weitere task-kompatible Session bereits aktiv ausgewählt ist.
- `phenomena` bleibt beim textbezogenen Single-Session-Handoff und trägt weiterhin `set_id`, Provenienz und `focus_item` sauber weiter.

## Verifikation

- Neue strukturelle Tests decken produktiven `text`-Compare, `item_id`-Matching, Set-Filterung, partielle Compare-Abdeckung, fehlende Split-Downloads, Fokusverhalten und Route-Handoffs ab.
- Bestehende Regressionen für `wordlist`-Compare, `text`-Einzelrenderer sowie `set_id`-/`focus_item`-Grundlogik bleiben Teil der gezielten Testläufe.

## Ehrliche Grenzen

- Kein Token- oder Wortsync.
- Kein produktiver `running_text`-Compare.
- Kein n-facher Compare im Player; `comparison` bleibt die Mehrfach-Workbench.

## Nächste sinnvolle Schritte

- Prüfen, ob für `text` zusätzlich eine dezente Compare-spezifische Sessionwahl in der `comparison`-Workbench fachlich sinnvoll ist, ohne den bounded Player zu einer zweiten Workbench aufzublähen.
- Danach nur bei belastbarer Datenlage einen produktiven `running_text`-Renderer inklusive Compare-Semantik prüfen.