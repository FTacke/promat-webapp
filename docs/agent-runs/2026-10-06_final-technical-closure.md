# Final Technical Closure Run

Datum: 2026-10-06. Modell: Sonnet 5.5 Medium. Branch `feature/run4-publication-metadata` (Ausgang `origin/main` = `17cb7d0`). Abschlussbericht: `docs/reports/2026-10-06_final-audit-closure.md`.

## Ziel

Die technische Audit-Serie (Run 1–4) mit einem kleinen Closure-Run abschließen: Restbefunde prüfen und, wo eindeutig und klein, schließen; keine fachlichen Entscheidungen erfinden; alle Befunde gegen den aktuellen Stand klassifizieren.

## Consulted Sources

`docs/audits/promat_technical_integrity_audit_2026-10-06.md`, `docs/audits/promat_data_ux_publication_audit_2026-10-06.md`, Berichte und Run-Einträge von Run 1–4, `docs/spec/platform-data-files.md`, `research-capabilities.md`, `research-access.md`; Code für Korpus-Registries, Teaching-Validator, Research-Capabilities, Auth-Login.

## Phase 0

`HEAD` = `origin/main` = `17cb7d0` (Run 4, Production live: canonical der Themenseite geprüft, `/health` 200), Working Tree sauber. Ein Hilfsagent hat die nicht in den Run-Berichten behandelten Befunde (TI-14…37, DATA-02…10, CONTENT-03…06, AUDIO, ACCESSIBILITY, UX) lesend gegen den Code klassifiziert; die Ergebnisse flossen in die Matrix ein und wurden bei den geänderten Punkten durch Tests bestätigt.

## Wichtige Entscheidungen

- **DATA-03:** keine Laufzeitauflösung. Die Kataloge sind unversionierte Operator-Konfiguration; eine Abhängigkeit der öffentlichen, zitierbaren Designseite davon bräche CI und Image-Smoke oder bräuchte einen Fallback als zweite Quelle. Stattdessen Drift-Test (`data`): 142/142 identisch, rot bei Abweichung (Mutation geprüft).
- **DATA-05:** keine Universal-Registry. `TRACKED_CORPORA` und die Admin-Analytics-Tabelle nutzen `ACTIVE_RESEARCH_CORPORA` (bisher ungenutzt); ein Konsistenztest vergleicht sieben parallele Projektionen (öffentliche Sprachen, Analytics, Datenkonventionen, Publikations-Registry, Intake-Profile, Prod-Payload-Fallback, DB-Constraint) sowie die Task-Listen. Level-Vokabular hat nur eine Quelle.
- **DATA-11:** Orphan-Prüfung über alle Strings der YAML-Quellen einer Teaching-Sprache (nicht nur bekannte Medienfelder), damit dynamische Referenzen nicht fälschlich gemeldet werden. Vier Dateien sind unreferenziert (zwei ersetzte Aufnahmen, zwei Pilotgrafiken); es wurde nichts gelöscht, sie stehen mit Begründung in `content/teaching/media-exceptions.yaml` (`content_decision_required`). Die ersetzten MP3 haben andere Bytes als die verwendeten Dateien und werden von der Media-Route weiter ausgeliefert, daher die Notiz zur Einwilligungsprüfung.
- **Deutsche Platzhalter:** Die Spec sieht leere Zustände vor und hat Planungsplatzhalter abgeschafft; die deutschen Seiten zeigten aber noch Entwicklertext („Die Route existiert bereits mit dem finalen technischen Schlüssel“). Ersetzt durch einen schlichten „In Vorbereitung“-Zustand (DE+EN); gleiche Bereinigung für fünf Player-Hinweise mit „in diesem Run“/`dev-start.ps1`.
- **Phase 5:** nur mechanische, policy-freie Punkte: Dummy-Verifikation bei unbekanntem Login (TI-22 Timing), `remote_addr` statt rohem `X-Forwarded-For` (TI-24 Code), Dev-Server und Dev-DB nur auf Loopback (TI-14), `pool_pre_ping`, Workflow-Input über `env:` (TI-33), `bcrypt<5` (TI-37), `.gitattributes` für `*.sh`. Nicht angefasst: Lockout-Reihenfolge (würde Konten aufdecken), `TRUSTED_HOSTS`, Container-Nutzer, Paketbereinigung, Audio-/iOS-Punkte.

## Geänderte Bereiche

`app/src/app/{analytics,main,i18n}.py`, `routes/{admin,auth,public,public_content}.py`, `auth/services.py`, `extensions/sqlalchemy_ext.py`, `scripts/validate_teaching_content.py`, `scripts/qa/ci_browser_smoke.py`, `content/teaching/media-exceptions.yaml`, `docker-compose.dev-postgres.yml`, `.github/workflows/release-candidate-check.yml`, `app/requirements.in`, `.gitattributes`; fünf neue Testdateien. Spec: `platform-data-files.md` (Orphan-Regel und Ausnahmeliste), `research-capabilities.md` (German in preparation, Konsistenz- und Drift-Tests).

## Abweichungen

Keine von den Specs. Die Orphan-Warnungen des Validators erscheinen weiter, bis die Content-Entscheidung gefallen ist.

## Verifikation

- `pytest` lokal 1238 passed; im Linux-Container (`python:3.12-slim`, Postgres 15) 1244 passed, 2 skipped, 9 deselected. JS 64/64, ruff, compileall, Governance, Teaching-Validator grün.
- CI-Browser-Smoke lokal: 228 Prüfungen, 0 Fehler (neu: deutsche Seiten DE+EN, 1280/390 px, Überlauf, Text); Screenshot `tmp/ui-qa/2026-10-06-final-closure/` geprüft (nicht versioniert).
- Windows-Hinweis: lokale Läufe brauchen `PYTHONUTF8=1`, sonst scheitert `test_runtime_packaging` an der Subprozess-Kodierung.
- Hinweis: Docker-Image-Smoke und Post-Deploy-Smoke laufen in CI bzw. im Deploy; Ergebnisse stehen im Bericht.

## Production-Aktionen

Push `17cb7d0..40d37f5` nach `main`; keine Server- oder Datenänderung außerhalb des Deployments.

## Production-Ergebnis

CI und Deploy für `40d37f5` grün, Post-Deploy-Smoke grün, `/ready` 200; Details im Abschlussbericht. Der Doku-Commit danach ändert keinen Code.
