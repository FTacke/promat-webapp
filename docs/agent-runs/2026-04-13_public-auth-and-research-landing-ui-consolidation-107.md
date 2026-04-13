# Public Auth And Research Landing UI Consolidation 107

Datum: 2026-04-13

## Ziel

Die öffentlichen Auth-Flächen auf `/login` und `/auth/password/*` sowie die neue öffentliche Research-Korpus-Landingpage unter `/{ui_lang}/research/{corpus}` in die aktuelle PROMAT-Formensprache überführen: kein alter MD3- oder CORAPAN-Eindruck mehr, ruhigere Auth-Hierarchie, leichtere Corpus-Orientierungsliste, plain page-name Aktionen, muted/locked Schutzsignale ohne zusätzliche Login-Hinweise und vollständige `de`/`en`-Abnahme auf der kanonischen Dev-Instanz `127.0.0.1:8000`.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md` (geprüft, in diesem Run unverändert belassen)
- `docs/spec/research-capabilities.md` (geprüft, in diesem Run unverändert belassen)
- `docs/spec/intake-workbook.md` (geprüft, in diesem Run unverändert belassen)
- `docs/plans/auth_login_plan.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- Skill geprüft: `c:\Users\Felix Tacke\.vscode\extensions\github.copilot-chat-0.43.0\assets\prompts\skills\agent-customization\SKILL.md`
- Runtime-Wiring geprüft: `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `docker-compose.dev-postgres.yml`, `app/infra/docker-compose.prod.yml`
- Repo-Memory geprüft: `/memories/repo/promat-research-ui-notes.md`, `/memories/repo/promat-doc-system-notes.md`, `/memories/repo/promat-dev-setup-notes.md`
- Produktive Referenzflächen geprüft: `app/templates/pages/research_player.html`, `app/templates/pages/research_speakers.html`, `app/templates/pages/research_recordings.html`, `app/templates/partials/_research_filters.html`, `app/static/css/20_layout.css`, `app/static/css/30_components.css`, `app/static/css/40_cards.css`

## Geänderte Bereiche

- Öffentliche Auth-Shell und Auth-Templates unter `app/templates/_md3_skeletons/auth_login_skeleton.html` und `app/templates/auth/`
- Öffentliche Research-Korpus-Landingpage und Sample-Mirror unter `app/templates/pages/research_language_root.html` und `app/templates/pages/sample_page.html`
- Shared Research-Navigation unter `app/templates/partials/_navigation_drawer.html`
- Public Content Builder und Übersetzungen unter `app/src/app/routes/public_content.py` und `app/src/app/i18n.py`
- Shared Layout- und Komponenten-CSS unter `app/static/css/20_layout.css` und `app/static/css/30_components.css`
- Fokussierte Regressionen unter `app/tests/test_auth_phase1.py` und `app/tests/test_research_sessions.py`
- Aktive UI-Regeln unter `docs/spec/platform-data-files.md`
- Statushinweis im Plan unter `docs/plans/auth_login_plan.md`

## Wichtige Entscheidungen

- Die öffentlichen Auth-Flächen wurden nicht als eigene Mini-Designwelt behandelt, sondern auf bestehende PROMAT-Familien umgestellt: `pm-content-header`, `pm-phenomena-field__input`, `pm-research-inline-action`, `pm-research-button`, die bestehende Sidebar-/Muted-Logik und die ruhige vertikale Rhythmik aus den Research-Seiten.
- Der alte MD3-/CORAPAN-Look wurde auf den öffentlichen Auth-Flächen gezielt zurückgedrängt, indem die MD3-Auth-Stylesheet-Einbindung aus der Auth-Skeleton entfernt und die sichtbaren MD3-Card-, Button- und Textfield-Muster aus Login, Passwort vergessen und Passwort setzen entfernt wurden.
- Die Corpus-Landingpage bleibt eine öffentliche Orientierungsebene, aber bewusst als lineare Liste statt als laute Karten- oder CTA-Fläche. Die sichtbaren Aktionslabels bleiben die schlichten Seitennamen.
- Geschützte Ziele bleiben auf der Landingpage und im Sidebar-Navigationsblock sichtbar, werden für unangemeldete Nutzer:innen jedoch ausschließlich über muted/locked Zustände signalisiert. Der Lock sitzt links vor dem Label; zusätzliche sichtbare `Login erforderlich`-Texte wurden nicht eingeführt.
- Sichtbares Branding auf diesen Flächen bleibt `Pronunciation Matters`.

## Abweichungen

- Keine Abweichung von den aktiven Routing-, Access- oder Runtime-Regeln in der finalen Implementierung.
- Vor der Browser-Abnahme wurde eine lokale Runtime-Abweichung bereinigt: Zwei stale globale Python-312-Prozesse (`-m src.app.main`) belegten `127.0.0.1:8000` und lieferten veraltetes Corpus-Root-HTML aus. Die Prozesse wurden beendet und die kanonische Startstrecke `scripts/dev-start.ps1` wurde erneut auf `8000` gestartet.

## Verifikation

- Editor-Fehlerprüfung für die geänderten Templates, Python-Dateien und CSS-Dateien: ohne verbleibende Fehler nach der Entfernung der inkompatiblen `color-mix(...)`-Border-Deklarationen.
- Fokussierter Python-Testlauf im Workspace-Environment:
  - `tests/test_auth_phase1.py`
  - `tests/test_research_sessions.py`
  - Ergebnis: `151 passed`
- Zusätzliche Laufzeitprüfung per HTTP gegen `http://127.0.0.1:8000/health` und `http://127.0.0.1:8000/de/research/spanish` nach dem Neustart der kanonischen Dev-Instanz.
- Browser-QA mit Headless Edge gegen die laufende Instanz `127.0.0.1:8000` nach Runtime-Bereinigung, inklusive Screenshots für:
  - `/de/research/spanish`
  - `/en/research/spanish`
  - `/de/research/french`
  - `/login?ui_lang=de`
  - `/login?ui_lang=en`
  - `/auth/password/forgot?ui_lang=de`
  - `/auth/password/forgot?ui_lang=en`
  - `/auth/password/reset?token=...&ui_lang=de`
  - `/auth/password/reset?token=...&ui_lang=en`
  - `/de/research/spanish/design` mit muted/locked Sidebar
  - unangemeldeter Klick von `/de/research/spanish` auf den geschützten `speakers`-Link mit Redirect auf `/login?next=/de/research/spanish/speakers`

## Screenshots

- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/research_spanish_de.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/research_spanish_en.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/research_french_de.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/login_de.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/login_en.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/forgot_de.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/forgot_en.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/reset_set_password_de.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/reset_set_password_en.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/design_locked_sidebar_de.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/gate_speakers_from_root_de.png`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/metrics.json`
- `tmp/ui-qa/2026-04-13-public-auth-research-ui-consolidation-107/dev-start-8000.log`

## Offene Punkte

- Die QA-Screenshots bestätigen die gewünschte Richtung und die korrigierte Runtime. Für weitere große Research-UI-Läufe sollte vor Browser-Abnahme weiterhin zuerst geprüft werden, ob alte globale `python.exe -m src.app.main`-Listener auf `8000` laufen.
- Die öffentlichen Auth- und Corpus-Landing-Flächen sind konsolidiert; eine weitergehende globale Ablösung verbliebener MD3-Strukturen außerhalb dieses Scopes war nicht Teil dieses Runs.

## Nächste sinnvolle Schritte

- Falls weitere öffentliche Flächen denselben Alt-Look behalten, denselben PROMAT-Familienabgleich auf die nächsten Public- oder Admin-Surfaces fortsetzen.
- Die Runtime-Hygiene für lokale QA weiter standardisieren, damit die kanonische `8000`-Instanz nicht erneut von globalen Python-Prozessen überlagert wird.
