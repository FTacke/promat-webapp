# Sample an aktuelle Layout-Elemente angeglichen

Datum: 2026-04-02

## Ziel

Die Sample-Seite systematisch vom veralteten Altstand auf die aktuell produktiv verwendeten Layout-Elemente der Webapp nachziehen, ohne Sample selbst als gestalterische Quelle zu behandeln. Zusätzlich sollten Karten in Landing-, Korpus- und Auswahl-Grids immer begrenzte Maximalbreiten behalten.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/templates/pages/sample_page.html`
- `app/templates/pages/landing.html`
- `app/templates/pages/promat_page.html`
- `app/templates/pages/research_speakers.html`
- `app/templates/pages/research_recordings.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/src/app/routes/public.py`
- `app/src/app/routes/public_content.py`
- `app/static/css/00_tokens.css`
- `app/static/css/20_layout.css`
- `app/static/css/40_cards.css`

## Geänderte Bereiche

- `app/src/app/routes/public.py`: Sample erhält echte Builder-Daten für Landing-, Research-, Teaching- und Auswahlkarten; Demo-Speaker-Cards werden in derselben Datenform wie die produktive Sprecher:innen-Seite bereitgestellt
- `app/templates/partials/_research_speaker_card.html`: gemeinsamer Speaker-Card-Partial für produktive Research-Seite und Sample eingeführt
- `app/templates/pages/research_speakers.html`: auf den gemeinsamen Speaker-Card-Partial umgestellt
- `app/templates/pages/sample_page.html`: alte Varianten- und Altstands-Dummys entfernt; Sample nun auf aktuelle Landing-Cards, Korpus-Karten, Auswahlkarten, Speaker-Cards, Recordings-Tabelle und Profil-Container ausgerichtet
- `app/static/css/00_tokens.css` und `app/static/css/20_layout.css`: systemische Maximalbreiten für Card-Grids ergänzt, sodass einzelne Karten im Grid nicht auf volle Breite aufziehen
- `docs/spec/platform-data-files.md`: aktive Regel ergänzt, dass `sample` nur aktuelle reale Layout-Elemente spiegelt
- `AGENTS.md`, `app/AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/repo.instructions.md`: Repo-Regel ergänzt, Sample bei Änderungen an repräsentierten Layout-Elementen im selben Run nachzuziehen
- `app/tests/test_research_sessions.py`: Render-Regressionen für die aktualisierte Sample-Seite ergänzt

## Wichtige Entscheidungen

- Landing- und Korpus-Karten in Sample werden nicht mehr doppelt gepflegt, sondern direkt aus den echten Public-Page-Buildern gespeist.
- Die Speaker-Card ist nicht mehr nur visuell angenähert, sondern wird zwischen Research und Sample über dasselbe Template-Makro gerendert.
- Die Maximalbreiten-Regel wurde nur auf Card-Grids gelegt; Profilcontainer und andere Nicht-Card-Container bleiben in ihrer bisherigen Breite unverändert.

## Normative Doku

- `docs/spec/platform-data-files.md` definiert jetzt explizit, dass `sample` der Spiegel aktueller Layout-Elemente ist und bei Änderungen an repräsentierten Elementen im selben Run mitgezogen werden muss.

## Verifikation

- Render-Regressionen in `app/tests/test_research_sessions.py`
- vollständiger Testlauf: `pytest tests/test_research_sessions.py`

## Offene Punkte

- Weitere künftig hinzukommende reale Layout-Bausteine sollten nur dann in Sample ergänzt werden, wenn sie bereits auf produktiven Seiten stabil verwendet werden.