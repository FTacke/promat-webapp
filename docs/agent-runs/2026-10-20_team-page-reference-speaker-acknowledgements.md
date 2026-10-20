# Teamseite: Dank an Referenzsprecher:innen

Datum: 2026-10-20

## Ziel

Abschnitt „Dank“ / „Acknowledgements“ auf `/{de|en}/project/team`: neuer Dankestext, elf namentlich genannte und eine anonyme Referenzsprecher:in, gruppiert nach Sprache.

## Status

Umgesetzt, getestet und im Browser geprüft (Desktop 1280 px / mobil 390 px, hell/dunkel, DE/EN).

## Geänderte Dateien

- `app/src/app/routes/public_page_content_data.py`: Dank-Absatz (DE/EN) ersetzt, `<em>tertium comparationis</em>`; alte `bullets` entfernt; vier `meta_cards` mit `credit_items` (Spanisch, Französisch, Deutsch, Englisch), Layout `team-corpus` (2 × 2, mobil einspaltig).
- `app/templates/pages/promat_page.html`: Meta-Karten rendern `credit_items` als semantische Liste (`ul.pm-credit-list`); die Abschnittsüberschrift vor den Karten wird nur noch ausgegeben, wenn der Abschnitt keinen eigenen Textblock hat (sonst stand „Dank“ doppelt).
- `app/static/css/40_cards.css`: `.pm-credit-list*` (Name hervorgehoben, Varietät klein und gedämpft darunter, nur bestehende Tokens, Marker ausgeblendet).
- `app/src/app/routes/public_content.py`: `_fill_team_corpus_cards` überspringt Abschnitte mit handgeschriebenen `meta_cards`. Ohne diese Zeile hätte die Registerbefüllung die Dank-Karten durch Korpuskarten ersetzt (Fehler der ersten Fassung, die nie ausgeführt worden war).
- `app/tests/test_research_sessions.py`: Kartenanzahl 6 → 10, alter „M.A.“-Check ersetzt, neuer Test `test_team_page_acknowledges_reference_speakers_by_group` (Gruppenreihenfolge, Nachnamenssortierung, Varietäten, Kursivsatz, Überschrift genau einmal, keine Ecuador-Angabe).

## Scope-Prüfung

- `git diff` gegen HEAD: Änderungen außerhalb des Dank-Abschnitts nur die neuen gemeinsamen Hilfen (`credit_items`-Block im Template, `.pm-credit-list*`-CSS) und die beiden oben genannten Bedingungen (Template-Überschrift, `_fill_team_corpus_cards`), die für bestehende Abschnitte wirkungslos sind (kein bestehender Abschnitt kombiniert Textblock und Karten oder trägt handgeschriebene `team-corpus`-Karten).
- Nicht angefasst: `content/publication/resources.yaml`, Autorenregister, Teaching-Tests, Autorenreihenfolge-/Zitationstests, Forschungsdaten, Secure-/Intake-Dateien, andere Seiten.
- Bestehende Testanpassungen nur durch den neuen Dank-Abschnitt begründet (Kartenzahl, entfernte „Aoife … M.A.“-/Bullet-Assertions).
- Browser-Vergleich gegen HEAD (Worktree, gleiche Fixture-Runtime): sichtbarer Text oberhalb „Dank“ in DE und EN identisch; Screenshots oberhalb des Dank-Abschnitts pixelgleich (Desktop dunkel/hell, mobil), eine einmalige, 7 px hohe Bandabweichung im Kopfbereich im ersten Desktop-Hell-DE-Screenshot ist ein Einblend-Zeitartefakt und in allen übrigen Läufen nicht vorhanden. Der Abschnitt „Sprachenzentrum“ liegt oberhalb und ist unverändert.

## Entscheidungen

- Reihenfolge der Gruppen wie auf der Plattform: Spanisch, Französisch, Deutsch, Englisch; innerhalb jeder Gruppe nach Nachnamen.
- Anonyme Sprecherin: ohne Länderangabe und ohne weiteren Hinweis („Eine weitere Referenzsprecherin · auf eigenen Wunsch ohne Namensnennung“), um keine indirekte Identifizierbarkeit zu erzeugen. Es wurden keine Intake-Daten in Content übernommen.
- Bestehende Personenlisten (auch Materialkonzeption Spanisch „Felix Tacke, Ana Goás Pérez“) bleiben unverändert; außerhalb des Dank-Abschnitts wurde nichts umsortiert.

## Prüfungen

- `pytest` gesamte Suite (`app/`): 1443 passed, 2 skipped, 11 deselected (nach den Korrekturen erneut gelaufen). Zielgruppe `test_research_sessions.py`, `test_publication_metadata.py`, `test_teaching_spanish_topics.py`: 406 passed.
- `ruff check .`, `scripts/ci_governance_checks.py`, `scripts/validate_teaching_content.py`: ohne Fehler. `node --test app/tests/js/*.test.mjs`: 67 passed. Docker-Build und Shellcheck nicht ausgeführt (vom Dank-Abschnitt unberührt).
- Browser (Playwright/Chromium, eigene In-Process-Instanz auf Fixture-Runtime, keine echten Daten): `/de/project/team`, `/en/project/team` bei 1280 px und 390 px, hell und dunkel. Ergebnis: 2 × 2 auf Desktop, einspaltig mobil; kein horizontaler Überlauf, keine abgeschnittenen Namen (Bucarey-Altamirano bricht am Bindestrich in der Desktop-Spalte, steht mobil in einer Zeile); Name (600, Serif) / Varietät (klein, gedämpft) klar gestaffelt; anonymer Eintrag gleichrangig; keine Konsolenfehler; `<em>tertium comparationis</em>` berechnet `font-style: italic` in allen acht Kombinationen.
- Regression: `/de/research` und `/en/research` (Karten-Familie `pm-meta-card`-fremde Auswahlkarten, gleiche Seitenschale) bei Desktop und mobil pixelgleich zu HEAD.
- Screenshots: `tmp/ui-qa/2026-10-20-team-dank/{base,new}/`, Skript `tmp/ui-qa/2026-10-20-team-dank/capture.py` (tmp ist git-ignoriert; Repo-Wurzel sauber).
