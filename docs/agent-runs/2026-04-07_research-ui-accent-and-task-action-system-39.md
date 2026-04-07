# Research UI Accent And Task Action System

Datum: 2026-04-07

## Ziel

Die Research-UI systematisch vereinheitlichen: Native-Speaker farblich klar vom Learner-Niveausystem trennen, Akzentkanten über die relevanten Kartenfamilien auf `0.5rem` vereinheitlichen und taskbezogene Kleinaktionen als echte Aktionen statt badge-artige Pills lesbar machen.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/spec/intake-workbook.md`
- `app/static/css/00_tokens.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/templates/partials/_research_speaker_card.html`
- `app/templates/pages/research_recordings.html`
- `app/templates/pages/research_player.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/templates/pages/sample_page.html`
- `app/src/app/routes/public.py`
- `app/src/app/research_views.py`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `app/static/css/00_tokens.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/templates/partials/_research_speaker_card.html`
- `app/templates/pages/research_recordings.html`
- `app/templates/pages/sample_page.html`
- `app/tests/test_research_sessions.py`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`

## Wichtige Entscheidungen

- Native-Speaker nutzen jetzt einen dedizierten Accent `#18677A` statt weiter implizit im Learner- beziehungsweise Standard-Akzentbereich zu landen.
- Die sichtbare Top-Akzentkante der relevanten Research-Kartenfamilien wurde auf einen gemeinsamen Token `0.5rem` gezogen: Speaker-Cards, Profile-Session-Container, Player-Metakarten über ihre Speaker-Card-Basis sowie Research- und Sprach-Korpus-Karten.
- Für kleine taskbezogene Einstiege wird keine neue Button-Sprache eingeführt. Stattdessen erweitert ein Modifier `pm-research-inline-action--task` die bestehende Inline-Action-Familie.
- Diese Task-Aktionen tragen denselben kompakten Action-Typ in Speaker-Card-Footern und in der Recordings-Tabelle und bleiben damit klar von Chips und Badges getrennt.
- Die größeren Profil-Task-Tiles bleiben bewusst eine eigene Kategorie und wurden nicht auf die Kleinaktionssprache zusammengestaucht.

## Sample-Sync

- Sample dokumentiert jetzt Chips, Badges und kleine Task-Actions als drei getrennte Kategorien.
- Die Recordings-Dummy-Tabelle verwendet denselben Task-Action-Modifier wie die produktive Recordings-Seite.
- Die Speaker-Card-Dummys übernehmen die neue Kleinaktionssprache automatisch über das geteilte Partial.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py`
- Tests erweitert für:
  - Sample-Markup mit `pm-research-inline-action--task`
  - fehlendes altes Speaker-Task-Link-Markup im gerenderten HTML
  - produktive Recordings-Route mit derselben Task-Action-Familie

## Offene Punkte

- Kein zusätzlicher Browser-Screenshot-Pass in diesem Run; die Absicherung erfolgt hier über den systematischen CSS-/Template-Abgleich plus die erweiterten Render-Tests.

## Nächste sinnvolle Schritte

- Falls weitere kleine Task-Einstiege außerhalb von Research dazukommen, denselben `pm-research-inline-action--task`-Modifier wiederverwenden statt erneut badge-nahe Minikomponenten einzuführen.