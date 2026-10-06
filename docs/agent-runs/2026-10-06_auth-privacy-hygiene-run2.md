# Auth, Privacy & Research-Data Hygiene – Run 2

Datum: 2026-10-06. Modell: Sonnet 5.5 High. Branch `repair/run2-auth-privacy` (aus `origin/main` = `e626e3e`). Detailbericht: `docs/reports/2026-10-06_auth-privacy-hygiene-run2.md`.

## Ziel

TI-04 (Token-/Statuswirkung, Logout), TI-25 (Admin-Invarianten), E-Mail-Wechsel mit Re-Authentifizierung, DATA-01 (ID3-Tags der Runtime-MP3s) und die technisch entscheidbaren Teile von TI-27.

## Consulted Sources

`docs/spec/auth-accounts.md`, `platform-data-files.md`, `research-access.md`, `intake-workbook.md`; Run-1/1.5-Einträge; Runbook `research-prod-upload-and-publish.md`, `backup-and-restore.md`, `deploy-and-rollback.md`.

## Phase 0

- `main` = Production = `e626e3e` (Run 1.5), Working Tree sauber, Branch Protection weiterhin aus (`BLOCKED_EXTERNAL`, nur verifiziert, kein Blocker). Kein QA-Konto auf Produktion angelegt.
- Ausgangsstatus: TI-04, TI-25, E-Mail-Wechsel, DATA-01 `STILL_OPEN`; TI-27 `PARTIALLY_FIXED` (Consent-/Secure-Felder waren schon aus HTML/JSON heraus, Set-API gab Account-IDs aus). Run-1-Bereiche nicht erneut angefasst.

## Wichtige Entscheidungen

- **Architektur:** Option A plus ein Widerruf je Token, keine `token_version`. Grund: Gruppenkonten sind ein geteilter Zugang; eine Versionsnummer je Nutzer würde beim Logout eines Mitglieds alle anderen abmelden. Statt dessen prüft ein einziger `token_verification_loader` jede Token-Auswertung gegen den Kontostand (aktiv/gelöscht/gültig/abgelaufen, Rolle, Kontoart, `must_reset_password`), und Logout legt die `jti` in `revoked_tokens` (Migration `0012`). Rollen-/Statusänderungen wirken sofort; ein Rollenwechsel erfordert Neuanmeldung für die neuen Claims. Kein Cache (Entzug sofort). Die ungenutzte Refresh-Token-Infrastruktur bleibt unberührt.
- **E-Mail-Wechsel:** nur Re-Authentifizierung mit aktuellem Passwort. Double-Opt-in-Bestätigung der neuen Adresse nicht gebaut (braucht einen eigenen Token-Flow); in der Spec vermerkt.
- **ID3-Politik:** keine ID3v1/APEv2, ID3v2 nur Encoder-Frames `TSSE`/`TENC`; ffmpeg mit `-map_metadata -1`. Bereinigung ist metadata-only (Tag-Bytes entfernen, MPEG-Frames unverändert, pro Datei per Hash der Audiobytes geprüft) statt Re-Encoding. Der Archiv-Layer wird von Validator und Werkzeug nicht angefasst (`validate_archive_tree` prüft Tags bewusst nicht; das Werkzeug verweigert `secure`/`source`/`archive`-Wurzeln).
- **TI-27:** Set-API serialisiert `created_by_user_id`/`updated_by_user_id` nicht mehr (der Client nutzt sie nicht). `person_notes`/`session_notes` und `recorded_by` sind per Spec für geschützte Research-Kontexte vorgesehen (`recorded_by` als „Explorator:in“): kein Spec-Verstoß, Inhaltsfrage als `EDITORIAL_DECISION_REQUIRED` dokumentiert, nichts gelöscht. Gruppenkonto-Zurechenbarkeit: `DEFERRED_POLICY_DECISION` (keine Spec-Vorgabe, kein neues Tracking).

## Geänderte Bereiche

Auth: `auth/models.py`, `auth/services.py`, `extensions/__init__.py`, `routes/auth.py`, `routes/admin.py`, `i18n.py`, `templates/pages/account.html`, Migration `0012_create_revoked_tokens.sql`. Privacy: `research_sets.py`. Audio: `scripts/research_data_intake/{audio_tags,scan_audio_tags}.py` (neu), `audio_conversion/ffmpeg_audio.py`, `intake_storage.py`. Tests: `test_session_state.py` (36), `test_audio_tags.py` (9), Sentinel-Test in `test_research_sessions.py`, Set-API-Test in `test_web_hardening.py`. Specs: `auth-accounts.md` (Session State, Admin Invariants, Logout, E-Mail), `platform-data-files.md` (Tag-Politik, Set-API), Runbook `research-prod-upload-and-publish.md` (Tag-Gate).

## Production-Aktionen

- Code per `main` deployed (CI grün, Deploy grün, Migration 0012 angewendet, Backup vor der Migration durch das Deploy, Post-Deploy-Smoke grün).
- **Research-Audio-Re-Publish über die vorgesehene Pipeline:** vor dem Bau wurde belegt, dass die lokale Runtime (8324 MP3) bytegleich zur Produktion war und `current` bytegleich zum flachen Baum (8545 Dateien, 0 Differenz). Danach lokal bereinigt, drei Pakete (`run2_tagclean_{english,french,spanish}`, 45 Sessions, mit `--include-research-player-config`, identisch zur Produktions-Config) gebaut, hochgeladen (Checksum-Gate ok) und mit `publish_prod_release.py` publiziert (Container-Neustart nur beim letzten). Die Retention des Publish-Skripts hat die zwei alten Juni-Releases gelöscht (älter als 7 Tage); das ist die dokumentierte Policy, der Rollback-Puffer für diesen Stand ist das vorherige Release (`…_french`).
- Post-Publish-Scan auf dem Server: 8324 MP3, 0 Verstöße, Hash-Liste identisch zur lokal bereinigten.

## Abweichungen

Keine von den Specs. Das Publish-Skript lief mit `--no-restart-container` für die ersten zwei Korpora (Dateien werden ohne Neustart von der Platte gelesen); der letzte Lauf hat neu gestartet.

## Verifikation

pytest 1118 passed, 1 skipped (Windows/WSL), 7 deselected, inkl. 7 Postgres-Tests (Migrationskette mit 0012, Schema-Parität); ruff, compileall, Governance, Teaching-Validierung, JS 11/11; Docker-Image-Smoke, Migration im Image, produktionsähnlicher Containerstart; Browser DE+EN: 48 Smoke-Prüfungen plus 8 Auth-Prüfungen (Konto-Seite mit neuem Feld, Fehlermeldung ohne Passwort, kopiertes Token nach UI-Logout in frischem Browserkontext abgewiesen). Die neuen Auth-Tests werden ohne den Verifikations-Loader rot (14 Fehlschläge geprüft). Production: Smoke, `revoked_tokens` vorhanden, keine neuen Fehler im Log. Authentifizierte Production-Probes entfallen (kein QA-Konto).

## Offene Punkte

Siehe Bericht „Handoff für Run 3“. Branch Protection weiterhin `BLOCKED_EXTERNAL`.
