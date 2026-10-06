# Auth, Privacy & Research-Data Hygiene – Run 2: Repair- und Validation-Bericht

Datum: 2026-10-06. Nicht-normativ; aktive Regeln in `docs/spec/`. Run-Journal: `docs/agent-runs/2026-10-06_auth-privacy-hygiene-run2.md`.

**Endstatus: `RUN 2: COMPLETE`** – Code deployed, Research-Audio über die Pipeline neu publiziert, Production-Scan bestätigt den Sollzustand.

## Befund-Tabelle

`CLOSED_AND_DEPLOYED` = auf Produktion wirksam; Beobachtungen, die ein Produktionskonto brauchen, stehen in der Spalte Production.

| Finding | Ausgangsstatus | Änderung | Evidenz/Test | Production-Status | Endstatus |
|---|---|---|---|---|---|
| TI-04 Token überlebt Statuswechsel | `STILL_OPEN` | `token_verification_loader` + `access_token_is_valid`: widerrufene `jti`, unbekannte/inaktive/gelöschte/noch nicht gültige/abgelaufene Subjekte, abweichende Claims (`role`, `account_kind`, `must_reset_password`) ⇒ abgewiesen; ein Prüfpunkt für Seiten und `@jwt_required`-APIs | 36 Tests in `test_session_state.py` (u. a. deaktiviert, gelöscht, abgelaufen, noch nicht gültig, Rollenwechsel beide Richtungen, Kontoart, `must_reset`, unbekannte `sub` mit Admin-Claims, Token ohne Claims, Lockout beendet keine Session); 14 davon werden ohne den Loader rot | deployed (Smoke, Log ohne Fehler); authentifizierter Ablauf nur lokal/Browser: kopiertes Token nach UI-Logout im frischen Browserkontext ⇒ Login-Redirect (DE+EN) | `CLOSED_AND_DEPLOYED` |
| Logout serverseitig wirksam | `PARTIALLY_FIXED` (POST+CSRF aus Run 1) | Logout legt die `jti` in `revoked_tokens` (Migration 0012) ab; nur dieses Token, andere Sessions desselben (Gruppen-)Kontos bleiben | `test_logout_ends_the_copied_token_server_side`, `…keeps_other_sessions…`, Aufräum-Test; Browser-Replay | Tabelle `revoked_tokens` auf Produktion vorhanden (Migration im Deploy, Backup davor) | `CLOSED_AND_DEPLOYED` |
| E-Mail-Wechsel ohne Re-Auth | `STILL_OPEN` | `POST /auth/account`: Adressänderung nur mit korrektem aktuellen Passwort, Formfeld „Aktuelles Passwort“ (DE/EN), Adressformat geprüft; Namensänderung ohne Passwort | 8 Tests (ohne/falsches/richtiges Passwort, Login mit neuer Adresse, ungültige Formen, vergebene Adresse); Screenshots DE+EN | deployed | `CLOSED_AND_DEPLOYED` |
| E-Mail: Bestätigung der neuen Adresse (Double-Opt-in) | – | nicht gebaut (braucht eigenen Token-Flow); in der Spec festgehalten | – | – | `DEFERRED_POLICY_DECISION` |
| TI-25 Admin-Invarianten | `STILL_OPEN` | serverseitig: gelöschtes Konto unveränderlich; Gruppenkonto behält Rolle `user`, keine E-Mail/Namen, kein Reset-Zustand; Persönliche E-Mail wohlgeformt; verantwortliche Person muss aktiver Admin sein; Last-Admin-Schutz bleibt | 10 (teils parametrisierte) Tests in `test_session_state.py` | deployed | `CLOSED_AND_DEPLOYED` |
| DATA-01 ID3-Tags der Runtime-MP3 | `STILL_OPEN` | ffmpeg `-map_metadata -1`; `audio_tags.py`/`scan_audio_tags.py`; Validatoren für Runtime-Baum und Prod-Paket; metadata-only Bereinigung; Re-Publish über Pipeline | 9 Audio-Tests (Reader, Strip byte-genau, kontaminierte Datei abgelehnt ohne Wertausgabe, echte ffmpeg-Konvertierung erbt keine Tags); Production-Scan 0 Verstöße | publiziert (siehe Summary) | `CLOSED_AND_DEPLOYED` |
| TI-27 Client-/API-Payloads | `PARTIALLY_FIXED` | Set-API ohne `created_by_user_id`/`updated_by_user_id`; Negativ-Allowlist-Test mit Sentinels über Speakers, Profil, Player, Comparison, Phenomena (DE+EN) und Set-API | Sentinel-Test (2), Set-API-Test | deployed | `CLOSED_AND_DEPLOYED` |
| TI-27 `person_notes`, `session_notes` | `STILL_OPEN` | klassifiziert: per Spec für geschützte Research-Kontexte vorgesehen; Inhalt nicht angefasst | Spec-Abschnitte `research-access.md` §notes | – | `EDITORIAL_DECISION_REQUIRED` (ob Notizinhalte für alle Research-Konten sichtbar bleiben sollen) |
| TI-27 `recorded_by` | `STILL_OPEN` | per Spec als „Explorator:in“ sichtbar; kein Verstoß | Spec `research-access.md` | – | `EDITORIAL_DECISION_REQUIRED` (Klarnamen von Projektmitarbeitenden vs. Pseudonym) |
| TI-27 Zurechenbarkeit bei Gruppenkonten | `STILL_OPEN` | bewertet: keine Spec-Vorgabe, keine vorgesehenen Download-Logs; kein Tracking eingeführt | – | – | `DEFERRED_POLICY_DECISION` |
| Branch Protection `main` | `BLOCKED_EXTERNAL` | nur verifiziert (`protected: false`) | GitHub-API | unverändert | `BLOCKED_EXTERNAL` |

Zusammenfassung: 6 × `CLOSED_AND_DEPLOYED` (TI-04, Logout, E-Mail-Re-Auth, TI-25, DATA-01, TI-27 Payloads), 2 × `EDITORIAL_DECISION_REQUIRED`, 2 × `DEFERRED_POLICY_DECISION`, 1 × `BLOCKED_EXTERNAL`.

## C. ID3/Privacy Summary

| Punkt | Wert |
|---|---|
| MP3 gesamt (Runtime) | 8324 (english 1385, french 3464, spanish 3475); lokal und Produktion bytegleich vor dem Lauf |
| Vor Repair mit unerlaubten Tags | 5143 (62 %): `TIT2` und `TRCK` je 5143; alle 8324 trugen zusätzlich den Encoder-Frame `TSSE` (zulässig) |
| Nach Repair mit unerlaubten Tags | **0** (lokal und auf Produktion); 3181 Dateien tragen noch `TSSE` (nur Encoder-Name) |
| Betroffene Korpora/Sessions | english 1322 Dateien / 9 Sessions, french 787 / 14, spanish 3034 / 22 ⇒ 45 Sessions |
| Wertmuster (ohne Werte) | zwei Familien: interne Arbeitsnamen der Form `<code>_<nr>_<aufgabe>_raw…` und `<Nachname>_<Liste/Text/Wortliste>_<Sprache>`; keine Namenslisten im Bericht |
| Verfahren | Tag-Bytes (ID3v2/v1) entfernt, MPEG-Frames unverändert (SHA-256 der Audiobytes je Datei vor/nach identisch, kein Re-Encoding, Stichproben-Decode ok); neue Konvertierungen erzeugen mit `-map_metadata -1` keine Quelltags mehr |
| Re-Publish Production | über `build_prod_upload_package` → `upload_prod_package` (Checksum-Gate) → `publish_prod_release` für `english`, `french`, `spanish`; Post-Publish-Scan auf dem Server: 8324 MP3, 0 Verstöße; Hash-Liste identisch zum lokalen Stand; `/ready` 200, Smoke grün |
| Manifest/Checksums | je Paket neu erzeugt (`manifest.json`, `checksums.sha256`); der Publish bildet ein neues Release (`current` + Delta); alte Juni-Releases wurden durch die dokumentierte Retention gelöscht |
| Öffentliche Teaching-MP3 | 10 Dateien, nur `TSSE` ⇒ 0 Verstöße |
| Source-/Archive-Layer unverändert | **ja**: nur `data/sessions` (Derived/Runtime) bereinigt; das Werkzeug verweigert `secure`/`source`/`archive`/`raw`-Wurzeln, der Archiv-Validator wurde nicht verschärft, kein Archivpfad wurde gelesen oder geschrieben |

## Production status

- `main` = Production-Commit der Code-Änderung `b6d4948` (Run-2-Code); Doku-Commit folgt auf `main` (siehe Terminal-Zusammenfassung).
- Migration `0012` angewendet; Backup vor der Migration automatisch durch das Deploy; tägliches Backup-Cron aus Run 1.5 aktiv.
- Smoke grün (`scripts/post_deploy_smoke.py`), keine neuen Fehler in Container- und App-Log.
- Nicht beobachtbar ohne Produktionskonto (und deshalb nicht an realen Konten getestet): Login/Logout-Zyklus, geschützte Antworten mit gültigem Cookie, Profile ohne interne Felder. Lokal/Container/Browser belegt; Nachholen mit `scripts/qa/browser_smoke.py` und einem vom Operator bereitgestellten QA-Konto.

## Tests

| Prüfung | Ergebnis |
|---|---|
| `pytest` (mit Postgres 15) | **1118 passed, 1 skipped (Windows/WSL-`bash -n`), 7 deselected** (`data`) |
| neu in Run 2 | `test_session_state.py` 36, `test_audio_tags.py` 9, Sentinel-Test 2, Set-API-Test 1 |
| JS / ruff / compileall / Governance / Teaching-Validierung | 11/11, grün, grün, 7/7, grün |
| Docker | Image-Smoke grün; Migrationskette inkl. 0012 im Image gegen Postgres 15; produktionsähnlicher Start (Gunicorn, Postgres, Redis) |
| Browser (Chromium, DE+EN) | 48 Smoke-Prüfungen + 8 Auth-Prüfungen, 0 Fehler |

## D. Handoff für Run 3

- **Offen:** Branch Protection (UI, `BLOCKED_EXTERNAL`); `EDITORIAL_DECISION_REQUIRED` für `person_notes`/`session_notes` und `recorded_by`; `DEFERRED_POLICY_DECISION` für Gruppenkonto-Zurechenbarkeit und Double-Opt-in beim E-Mail-Wechsel; Passwortwechsel widerruft andere Sessions nicht (bewusst nicht Teil der Spec); ein QA-Konto für den authentifizierten Production-Smoke.
- **Neu entdeckt:** `publish_prod_release.py`-Retention löscht vorherige Releases älter als 7 Tage, ein Rollback-Puffer besteht nur für den unmittelbar vorherigen Stand; `upload_prod_package.py` verlangt `config/` im Paket (Builder-Flag `--include-research-player-config`); unter Git Bash zerstört MSYS-Pfadumwandlung die Remote-Pfad-Argumente (`MSYS_NO_PATHCONV=1` nötig, Betriebsnotiz für das Runbook).
- **Für Run 3 (UX, Accessibility, Performance, Regression Protection):** aus den Audits unverändert TI-20 (Mobile), TI-16/TI-17 (Browser-/Komposition-Tests, Mutations-Lücken), TI-08 (429-UX, Redis-Ausfall-Latenz ca. 2,5 s je Request), UX-01 (Comparison-Sprecherauswahl) und die Landing-`<title>`-Doppelung; die neuen Session-State-Tests und `scripts/qa/browser_smoke.py` sind Ausgangspunkt für einen CI-Browser-Smoke.
