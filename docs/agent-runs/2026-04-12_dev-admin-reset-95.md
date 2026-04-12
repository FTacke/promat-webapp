# Dev Admin Reset 95

Datum: 2026-04-12

## Ziel

Den lokalen Dev-Zugang wiederherstellen und den Standardstart so erweitern, dass ein fester Dev-Admin bei lokalen Resets und normalen Dev-Starts idempotent auf bekannte Credentials zurueckgesetzt wird.

## Consulted Sources

- `AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/scripts/create_initial_admin.py`
- `app/scripts/dev-start.ps1`
- `app/scripts/dev-setup.ps1`
- `docs/runbooks/local-dev-start.md`
- Repo-Memory: `promat-dev-setup-notes`

## Geaenderte Bereiche

- Standard-Dev-Admin-Seed in `app/scripts/dev-start.ps1`
- Lokale Dev-Doku in `docs/runbooks/local-dev-start.md`

## Wichtige Entscheidungen

- Der normale lokale Start ueber `./scripts/dev-start.ps1` wird zum massgeblichen Rueckfallpfad fuer den Dev-Admin und nicht nur die einmalige `dev-setup`-Route.
- Der Seed bleibt auf lokale Development-Starts gegen die kanonische Dev-PostgreSQL-URL begrenzt, damit keine fremden Datenbanken still zurueckgesetzt werden.
- Die Ruecksetzung nutzt die bereits vorhandene idempotente Logik von `create_initial_admin.py` und fuehrt keine zweite Admin-Implementierung ein.

## Verifikation

- Direktlauf des Admin-Seeds fuer `admin_dev` gegen die lokale Dev-DB
- Datenbankpruefung des Users `admin_dev` auf Rolle `admin`, Aktivstatus und Login-Reset-Felder
- Dokumentation des neuen Rueckfallverhaltens im lokalen Dev-Runbook

## Offene Punkte

- Keine produktionsnahen oder nicht-kanonischen Dev-Datenbanken werden von diesem Rueckfallpfad beruehrt.
- `app/scripts/dev-setup.ps1` behaelt seinen eigenen Start-Admin-Parameter; der neue Standardstart setzt davon unabhaengig den kanonischen lokalen Dev-Account wieder her.