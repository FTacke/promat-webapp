# Data, UX & Publication Audit (Audit-only)

Datum: 2026-10-06

## Ziel

Read-only Audit von Daten-/Content-Integrität, UX/Accessibility/Responsive, Performance/Audio-Auslieferung und Publikations-/Zitier-Readiness der Plattform. Keine Reparaturen.

## Consulted Sources

- `AGENTS.md`, `docs/spec/platform-data-files.md`, `docs/spec/research-access.md`, `docs/spec/research-capabilities.md`
- `docs/audits/promat_reentry_audit_2026-10-04.md`, `docs/performance-*.md`
- Code unter `app/src/app/`, `app/templates/`, `app/static/`, `content/teaching/`, `scripts/research_data_intake/`; lokale Laufzeitdaten unter `data/`

## Geänderte Bereiche

- `docs/audits/promat_data_ux_publication_audit_2026-10-06.md` (neu, Bericht)
- `docs/agent-runs/2026-10-06_data-ux-publication-audit.md` (dieser Eintrag)
- Kein Anwendungscode, keine Spec, keine Daten, keine Konfiguration im Repo geändert.

## Wichtige Entscheidungen

- Berichtspfad folgt der Konvention `docs/audits/promat_<thema>_<datum>.md`.
- Befunde der Teil-Audits wurden vor Übernahme im Browser gegengeprüft; ein Teilbefund (Reichweite der Muted-Navigation) wurde korrigiert.
- Production nur per GET/HEAD und Browser-Smoke auf öffentlichen Seiten.

## Abweichungen

- Lokale Dev-DB: Die UI-Läufe haben 8 private Draft-Sets in `research_sets` und einen `last_login_at` für `admin_dev` erzeugt (gitignorierte Laufzeitdaten). Eine Bereinigung wurde nicht durchgeführt (Aktion wurde in der Sitzung abgelehnt); die Drafts laufen per `expires_at` ab.
- `pytest` lief mit SQLite-URL im Scratchpad statt gegen die Dev-DB; 892 passed, 1 failed (Windows-WSL-`bash`-Stub, umgebungsbedingt).

## Verifikation

- Playwright-Crawl lokal (anonym + eingeloggt) und Production-Smoke, axe-core, CDP-Throttling, Netzwerkprüfung, Kontrastberechnung, Datenskripte; Details im Bericht §2.
