# prep_server v0.7 production doc update

Datum: 2026-05-26

## Ziel

`docs/plans/prep_prod/prep_server.md` auf Basis der read-only Reports für den ersten ProMat / Pronunciation Matters v0.7-Produktionsdeploy aktualisieren, ohne Runtime-Änderungen auszuführen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- Nutzeranforderung mit den Fakten aus `promat_v07_preflight_readonly_20260526_191204.md`
- Nutzeranforderung mit den Fakten aus `promat_runner_deploy_pattern_readonly_20260526_191925.md`
- App-Konfiguration für Formular-Env-Keys in `app/src/app/config/__init__.py`, `app/infra/docker-compose.prod.yml`, `app/passwords.env.template`

## Geänderte Bereiche

- `docs/plans/prep_prod/prep_server.md`
- `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- Server- und Runtime-Namensraum wird konsistent auf `promat` festgezogen; der öffentliche Produktname bleibt Pronunciation Matters.
- Initiale öffentliche Produktionsdomain ist `pronunciation-matters.de`; `www` ist nur ein Redirect-Ziel, `promat.hispanistica.com` nur ein später möglicher Alias.
- Upload-Promotion wird als `incoming -> releases -> current` mit atomarem Symlink-Switch dokumentiert und nicht als direktes Schreiben in einen Live-Pfad.
- Die Produktionsformular-Sektion dokumentiert nur nicht-geheime Env-Key-Namen und verweist Secret-Werte ausschließlich in Server-Config.
- Runner- und Deploy-Dokumentation ist jetzt auf genau einen ProMat-Runner, `runs-on: [self-hosted, promat-prod]`, Reset auf `GITHUB_SHA` und genau ein Deploy-Script `scripts/deploy_prod.sh` verdichtet.

## Abweichungen

- Die benannten read-only Reports lagen unter den angegebenen absoluten Pfaden in diesem Windows-Workspace nicht lokal vor; die vom Nutzer vorgegebenen Report-Fakten wurden daher direkt aus der Anforderung übernommen.
- Keine Runtime-Abweichung, weil dieser Run ausschließlich Repo-Dokumentation geändert hat.

## Verifikation

- Ziel-Datei und einschlägige Governance-Dateien gelesen.
- Aktive Upload-Package-Spec auf Konflikte geprüft und im selben Run angepasst.
- Formular-Env-Key-Namen per Repo-Suche gegen die tatsächliche App-Konfiguration verifiziert.
- Fehlende Runner-/Compose-/Monitoring-Details in `prep_server.md` gezielt nachgeprüft und nachgetragen.
- `git diff` für die geänderten Doku-Dateien vorgesehen nach Abschluss des Patches.

## Offene Punkte

- Alle in `prep_server.md` beschriebenen Serveraktionen bleiben freigabepflichtige Runtime-Arbeit.
- Der optionale Alias `promat.hispanistica.com` bleibt bis zu separater DNS-/TLS-Freigabe außerhalb des Initial-Deploys.

## Nächste sinnvolle Schritte

- Diff prüfen und freigeben.
- Danach die Runtime-Phasen C bis M nur schrittweise und mit expliziter Serverfreigabe ausführen.
