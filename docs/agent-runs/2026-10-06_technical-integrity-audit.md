# Technical Integrity Audit (Audit-only)

Datum: 2026-10-06

## Ziel

Repo-weiter Audit-only-Run zu Security/Privacy/Access Control, E2E- und Regression-Sicherheit, Aussagekraft der Testsuite sowie Dependency-, Build- und Deployment-Hygiene. Keine Reparaturen.

## Consulted Sources

- `AGENTS.md`, `docs/spec/research-access.md`, `docs/spec/auth-accounts.md`, `docs/spec/research-capabilities.md`, `docs/spec/research-player.md`, `docs/spec/platform-data-files.md`
- `docs/audits/promat_reentry_audit_2026-10-04.md` (Vorgängerbericht, auf HEAD neu verifiziert)
- Code unter `app/src/app/`, `app/templates/`, `app/static/`, `app/tests/`, `.github/workflows/`, `infra/`, `scripts/`

## Geänderte Bereiche

- `docs/audits/promat_technical_integrity_audit_2026-10-06.md` (neu, Bericht)
- `docs/agent-runs/2026-10-06_technical-integrity-audit.md` (dieser Eintrag)
- Kein Anwendungscode, keine Spec, keine Konfiguration, keine Daten geändert.
- Lokal und git-ignoriert: `tmp/ui-qa/2026-10-06-integrity-audit/` (Probe-Skripte, Teilberichte).

## Wichtige Entscheidungen

- Audit-Stand ist HEAD `3c0bb8c`; Produktion (`origin/main` `5512451`) enthält das Reparatur-Set nicht und wurde separat per lesenden GETs geprüft.
- Vier Teilaudits (Security, Testsuite mit Mutationsproben im isolierten Worktree, Hygiene, E2E im Browser) liefen parallel; Widersprüche wurden per Code-Lesen aufgelöst.
- Berichtspfad folgt der Konvention `docs/audits/promat_<thema>_<datum>.md`.

## Abweichungen

- Keine Abweichung von Spec oder Konventionen. Produktion wurde ausschließlich per GET/HEAD auf öffentlichen URLs abgefragt.
- Im Repo existieren zusätzlich die untracked Dateien eines parallelen Audits (`docs/audits/promat_data_ux_publication_audit_2026-10-06.md`, `docs/agent-runs/2026-10-06_data-ux-publication-audit.md`); sie stammen nicht aus diesem Run und wurden nicht angefasst.

## Verifikation

- `pytest tests` 892 passed, 1 failed (Windows-WSL-`bash`), 7 deselected; `node --test` 11/11; `ruff`, `compileall`, Governance, Teaching-Validierung grün.
- 24 Mutationsproben (13 rot, 11 grün), 410 Browser-Prüfungen (383 PASS), Postgres-15-Migrationslauf, Docker-Build und Image-Smoke.
- Abschluss: `git status` ohne Änderungen an getrackten Dateien; temporärer Worktree entfernt.

## Offene Punkte

- Produktions-Blocker: Legal-Seiten liefern auf `origin/main` HTTP 500 (Fix liegt in HEAD, nicht gemergt).
- UNKNOWN (nur auf dem Server prüfbar): nginx-Header-Handling, Produktions-Env-Werte, Postgres-Constraint `ck_access_requests_status`, Backup-Cron, Branch-Protection.

## Nächste sinnvolle Schritte

- Lauf 0 (Operator): Reparatur-Set nach `main` mergen und verifizieren; danach Läufe 1 bis 7 gemäß Abschnitt 7 des Berichts.
