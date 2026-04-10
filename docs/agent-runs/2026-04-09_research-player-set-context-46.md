# Player Set-Kontext produktiv ausgewertet

Datum: 2026-04-09

## Ziel

Phase 6 des Repo-Plans umsetzen: Der bestehende Player soll `set_id` und `focus_item` nicht nur in der URL tragen, sondern im produktiven Player-Zustand taskgebunden auswerten.

## Consulted Sources

- `docs/plans/player_comparison_phenomena.md`
- `docs/plans/player_comparison_phenomena_repo_implementation_plan.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/src/app/research_views.py`
- `app/src/app/research_sets.py`
- `app/src/app/routes/public.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- bestehende Tests unter `app/tests/`

## Geänderte Bereiche

- `app/src/app/__init__.py`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/30_components.css`
- `app/tests/test_research_player_set_context.py`
- `docs/spec/research-player.md`

## Wichtige Entscheidungen

- Owner-gebundene Set-Auflösung im Player läuft über die bestehende Set-Schicht und nicht über ad-hoc-DB-Zugriffe im View-Builder.
- Wenn `set_id` ohne passenden Owner-Kontext ankommt, bleibt die HTML-Seite sichtbar, aber der Player degradiert auf die reguläre Session-Ansicht mit generischem Set-Hinweis ohne Leckage owner-gebundener Daten.
- Bei gültigem `set_id` filtert der Player die sichtbare Itemmenge taskgebunden; im bounded Direct-Compare gilt dieselbe Filtermenge für beide Seiten.
- `focus_item` wird im produktiven `wordlist`-Pfad als initiale Reveal-/Highlight-Logik umgesetzt, aber ohne Autoplay.
- `text` und `interview` bleiben ehrliche Fallbacks; sie berücksichtigen jetzt den Set-Kontext, ohne einen nicht vorhandenen Renderer vorzutäuschen.

## Verifikation

- Neue strukturelle Tests für Set-Filterung, leere Task-Ausschnitte, Focus-Auswertung, Compare-Zusammenspiel, Handoff-Rendering und Degradation ohne Owner-Kontext.
- Bestehende Player-/Research-Regressionssuite bleibt als Anschlussprüfung vorgesehen.

## Offene Punkte

- Der Player begrenzt Session-Switching noch nicht aktiv auf die in einem Set gespeicherten Comparison-Sessions.
- Für `text` gibt es weiterhin keinen produktiven Player-Renderer; der Fortschritt dieses Runs bleibt bewusst auf setbewusste, ehrliche Fallbacks begrenzt.
- `focus_item` steuert noch keinen taskübergreifenden Render-Fokus außerhalb des produktiven `wordlist`-Pfads.

## Nächste sinnvolle Schritte

- `text` als echten Player-Renderer an die bestehende Set- und Fokuslogik anbinden.
- Prüfen, ob Session-Switcher im Player bei `comparison`-Handoffs optional auf die im Set gespeicherten Sessions eingegrenzt werden sollen.
- Falls nötig, den sichtbaren Set-Kontext im Player noch um kompakte Saved-vs.-Draft-Informationen ergänzen, ohne eine zweite Toolbar zu bauen.