# Research Card Color And Selection Semantics

Datum: 2026-04-07

## Ziel

Die Research-Kartenfamilie farblich und semantisch schärfen: Learner-Level deutlicher spreizen, Native Speaker als eigene Kategorie bei `#18677A` belassen und den Auswahlzustand von Profil-Session-Karten vollständig an dieselbe Session-Farbe koppeln.

## Consulted Sources

- `AGENTS.md`
- `docs/AGENTS.md`
- `app/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/spec/intake-workbook.md`
- `app/static/css/00_tokens.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/templates/partials/_research_speaker_card.html`
- `app/templates/pages/research_player.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/templates/pages/sample_page.html`
- `app/src/app/research_views.py`
- `app/src/app/routes/public.py`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `app/static/css/00_tokens.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/src/app/routes/public.py`
- `app/templates/pages/sample_page.html`
- `app/tests/test_research_sessions.py`
- `docs/spec/research-access.md`

## Farbentscheidungen

- Learner-Level wurden als explizite violette Token gespreizt:
  - `A1`: `#C77BD9`
  - `A2`: `#A85BCC`
  - `B1`: `#7A46B8`
  - `B2`: `#5A348F`
  - `C1`: `#45276F`
  - `C2`: `#311A4F`
- Native Speaker bleiben bei `#18677A` und damit bewusst außerhalb der violetten Learner-Achse.
- Die starke Top-Akzentkante bleibt systematisch bei `0.5rem`.

## Wichtige Entscheidungen

- Es wurde keine neue konkurrierende Kartenlogik eingeführt; die bestehende Research-Kartenfamilie bleibt erhalten und nutzt weiter dieselben `accent_modifier`-Klassen.
- Die Profil-Session-Selektion verwendet keine losgelöste Highlight-Farbe mehr. Auswahlrahmen, Auswahlbadge und optionale minimale Flächentönung werden jetzt direkt aus `--pm-profile-session-accent` abgeleitet.
- Dadurch bleibt die Farblogik sessiongebunden statt personenbezogen: unterschiedliche Sessions derselben Person können unterschiedliche Level-Farben tragen, und die ausgewählte Karte übernimmt exakt die Farbe ihrer konkreten Session.
- Speaker-Cards und davon abgeleitete Player-Metakarten übernehmen die neue Spreizung automatisch über die gemeinsamen Level-Tokens in der bestehenden Kartenfamilie.

## Sample-Sync

- Der Speaker-Card-Bereich zeigt jetzt A1, A2, B1, B2 und Native als eigene Accent-Fälle.
- Der Profilbereich erklärt explizit, dass Auswahlrahmen und Auswahlbadge dieselbe Session-Farbe wie die Karte verwenden.
- Das Desktop-Grid im Sample wurde für die größere Kartenanzahl auf drei Spalten verbreitert.

## Konsistenzprüfung

- Geprüft und mitgeführt wurden:
  - Speaker-Cards
  - daraus abgeleitete Player-Metakarten über die gemeinsame `pm-speaker-card`-Accentlogik
  - Profil-Session-Karten
  - Sample-Darstellung dieser Kartenfamilie
- Keine unnötige globale Umbauorgie außerhalb der betroffenen Research-Kartenfamilie.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sessions.py -q` aus `app/`
- Tests ergänzt für:
  - sessiongebundene `accent_modifier`- und `is_selected`-Logik im Profil-Builder
  - Sample-Markup mit A1, A2, B1, B2 und Native
  - sichtbare ausgewählte Profil-Session-Fälle im Sample-Markup

## Offene Punkte

- Kein separater Browser-Screenshot-Pass in diesem Run; die Verifikation stützt sich auf die neue Tokenlogik, die systematische CSS-Kopplung und die erweiterten Render-Tests.