# Agent Run: Repo Hardening After French Promote (No New Prod Upload)

## Scope

- Ziel: Repo nach erfolgreichem French-Promote für zukünftige Research-Intake-, Package- und Upload-Läufe härten.
- Harte Grenzen: kein Server-Promote in diesem Run, kein neuer English/Spanish-Prod-Upload, keine Server-Deletes.

## Umgesetzte Änderungen

1. MFA-Backend-Default und Auflösung vereinheitlicht.
- CLI `--mfa-executable` hat Priorität.
- Danach `PROMAT_MFA_EXECUTABLE`.
- Ohne beides: Default `docker`.
- Docker-Fehlertext präzisiert (`Docker-MFA requested but docker is not available/running`).

2. Text-Task-Statusmeldungen geschärft.
- Bei `needs_preparation` und aktivem `--sync-tasks` enthält die Meldung jetzt einen expliziten Re-Run-Hinweis (`--run-working --run-mfa`).
- Signaturvergleich normalisiert Pfade zusätzlich auf Slash-Form (`\\` -> `/`) plus lower-case.

3. Upload-Helfer robust gemacht.
- Neuer Methoden-Schalter: `--method auto|rsync|tar-ssh`.
- `auto` nutzt rsync nur wenn lokal und remote verfügbar.
- Harte Remote-Dir-Guards gegen `current`, `releases`, `production`.
- Remote-Prüfungen nach Upload immer aktiv:
  - Root-Sanity
  - File-Count
  - `sha256sum -c checksums.sha256`
  - Reject code-ähnlicher Session-Ordner unter `sessions/` (z. B. `fr`, `en`).

4. Dokumentation aktualisiert.
- Spec ergänzt: Datei-Publish darf ohne DB-Payload weiterlaufen; DB-Upsert ist separater Schritt.
- Spec ergänzt: `/app/data` + `current`-Marker als aktiver Produktionszeiger.
- Upload/Publish-Runbook auf French-Promote-Stand aktualisiert.
- Neues Runbook für DB-Upsert aus `db/import_payload.json` erstellt.
- Intake-README auf MFA-Defaultvertrag und Upload-Methode aktualisiert.

## Test- und Verifikationsstand

- Neue/angepasste Tests für MFA-Auflösung und Upload-Methodik ergänzt.
- Bestehende Importer-Tests für neue `needs_preparation`-Meldung und Slash-Normalisierung angepasst.
- Kein Serverzugriff, kein neuer Upload, kein Promote in diesem Run.

## Offene Folgepunkte

- Optionaler dry-run des Upload-Helfers gegen Testhost (nur Verbindungs-/Commandpfad, ohne Promote).
- Nächster produktiver English/Spanish-Run nutzt diese Härtungen als Basis, bleibt aber eigener freigegebener Run.
