# PROMAT Technical Integrity Audit (2026-10-06)

Status: nicht-normativer Audit-Bericht. Aktive Regeln stehen weiterhin in `docs/spec/`. Dieser Bericht hält Befunde und Empfehlungen fest und ändert keine Spec. Audit-only-Run: kein Produktcode, keine Spec, keine Konfiguration wurde verändert.

Geprüfter Stand: Branch `local/preservation-activation`, HEAD `3c0bb8c`. Produktion = `origin/main` `5512451` (Deploy per `push`). **HEAD enthält ein Reparatur-Set (Commits `54a5f2c` bis `b454802`), das nicht auf `origin/main` liegt** (siehe TI-01). Alle Aussagen gelten für HEAD, sofern nicht ausdrücklich „Produktion“ steht.

Dateiname folgt der Konvention `promat_<topic>_<YYYY-MM-DD>.md`. Vorgängerbericht: `docs/audits/promat_reentry_audit_2026-10-04.md` (Stand `28c63d1`); dessen Befunde wurden auf HEAD einzeln neu geprüft.

Ergänzendes Material (nur lokal, git-ignoriert): `tmp/ui-qa/2026-10-06-integrity-audit/` mit den vier Teilberichten (`sec/`, `tests/`, `hyg/`, `e2e/`), allen Probe-Skripten (`p*.py`, `t_*.py`, Mutationsprotokoll) und `pytest_baseline.txt`.

---

## 1. Executive Summary

**Gesamturteil:** Der Anwendungskern ist solide. Die Zugriffsgrenzen halten in allen geprüften Pfaden: Research-Gate vor Lookup, Owner-Bindung bei Sets, Audio nur über Session-Lookup, kein XSS, kein Roh-SQL, keine Secrets im Repo. Die Schwächen liegen (a) im Abstand zwischen Produktion und Repo-Stand, (b) in wenigen konkreten Code-Defekten und (c) in einer Testsuite, die Frontend-Invarianten und die produktive Komposition nicht schützt.

| Schweregrad | Anzahl |
|---|---:|
| CRITICAL | 0 |
| HIGH | 2 |
| MEDIUM | 18 |
| LOW | 17 |

**Production Blocker: JA – für den aktuellen Produktionsstand (`origin/main`).** `/impressum`, `/en/impressum`, `/de/privacy`, `/en/privacy` liefern live HTTP 500 (am 2026-10-06 per `curl` verifiziert). Der Fix liegt in HEAD, ist aber nicht deployt. Gleichzeitig fehlen auf `main` die Korrekturen für Reset-Link-Host-Poisoning, Set-Label-HTML-Injection und die Sichtbarkeit von Einwilligungsdaten im Speaker-Profil. Der Deploy läuft dort ohne CI-Gate.
**Für HEAD als Merge-Kandidat: NEIN**, mit der Auflage, TI-02 (unauthentifizierter Listener-Leak) im ersten Reparatur-Lauf zu entfernen.

**Wichtigste Risiken**
1. Produktion läuft ohne das Reparatur-Set (TI-01).
2. Unauthentifizierter, persistenter Ressourcen-Leak über `?_profile=1` auf der Player-Route (TI-02).
3. Zustandslose Tokens: Logout, Deaktivierung und Zugangsende wirken bis zu 60 Minuten nicht; E-Mail-Wechsel ohne Re-Authentifizierung (TI-04).
4. Open Redirect `next=////host` für angemeldete Nutzer (TI-03).
5. Zugangsanfrage: Statuswerte verletzen den Postgres-CHECK, in SQLite-Tests unsichtbar (TI-06, TI-18).
6. Die Testsuite lässt 11 von 24 Mutationsproben überleben, darunter Stop-Logik, „Alle Items“-Selektion, Syntaxfehler im Player-JS und Consent-Felder im Client-JSON (TI-16 bis TI-19).

---

## 2. Ausgangszustand

| Punkt | Wert |
|---|---|
| Branch / Commit | `local/preservation-activation` / `3c0bb8c` (origin: 1 Commit weiter, `87114a6`) |
| `origin/main` | `5512451`; enthält **keinen** der Commits `54a5f2c`, `7feaade`, `d308632`, `84c4cf0`, `a785733`, `b454802` (per `git merge-base --is-ancestor` geprüft) |
| Umgebung | Windows 11, Python 3.12.10 (lokale `.venv`, **älter als der Lock**: Flask 3.1.2, Werkzeug 3.1.3, PyJWT 2.10.1), Node vorhanden, Docker Desktop zeitweise aus |
| Tests | `pytest tests` (CI-Env, Scratch-Runtime): **892 passed, 1 failed, 7 deselected** (`data`-Marker), 87 s. Der Fehlschlag ist Windows-spezifisch: `bash -n` startet WSL ohne Distro (`test_deploy_and_backup_scripts.py`). Mit exakt gelockten Versionen (Scratch-venv) identisches Ergebnis, plus ein zweiter Windows-Mojibake-Fehler in `test_runtime_packaging.py` in einem frischen Worktree |
| JS | `node --test app/tests/js/*.test.mjs`: 11/11 |
| Statische Checks | `ruff check .` pass; `compileall` pass; `scripts/ci_governance_checks.py` 7/7; `validate_teaching_content.py` pass; `shellcheck` sauber (auf LF-Inhalt des Index) |
| `mypy src` | 73 Fehler in 11 Dateien (überwiegend Typrauschen), läuft nicht in CI |
| `pip-audit` (Lock) | 1 Advisory (werkzeug, nur Windows/NTFS `safe_join`; Produktion ist Linux; nicht relevant). Die 49 Advisories des Vor-Audits sind im Lock behoben |
| Build | `git archive HEAD \| docker build -f app/Dockerfile` baut (444 MB), `ci_image_smoke.py` im Image besteht; Migrationen 0001–0010 laufen zweimal fehlerfrei auf Postgres 15, Modelle = Schema |
| Browser | Chromium headless gegen die laufende App (SQLite, echte lokale Daten als Scratch-Kopie): 410 Einzelprüfungen, 383 PASS, die 27 FAIL sind unten als Befunde oder Testartefakte erklärt |
| Mutationsproben | 24 Mutationen im isolierten Worktree: 13 rot, 11 grün (überlebt) |

### 2.1 Production-Smoke (nur lesende GETs auf `https://pronunciation-matters.de`)

| URL | Ergebnis | Bewertung |
|---|---|---|
| `/impressum`, `/de/impressum`, `/en/impressum`, `/de/privacy`, `/en/privacy` | **500** | Befund TI-01 (Legal-Quelle nicht im Image) |
| `/health`, `/ready` | 200; `/ready` öffentlich, JSON mit Check-Details | TI-23 |
| `/de`, `/de/teaching`, `/de/research/spanish`, `/de/research/spanish/design` | 200 | ok |
| `/de/research/spanish/speakers`, `/speakers/x` | 302 `/login?next=<exakter Pfad>` | Gate ok |
| Login-Link auf `/de/research/spanish` | `next=/de/research/spanish` (nicht `/speakers`) | Spec-Abweichung, in HEAD nur noch Topbar (TI-35) |
| Security-Header | HSTS, nosniff, XFO DENY, Referrer-Policy, CSP vorhanden; kein `Cache-Control` auf Seiten; `/static/...` mit `Cache-Control: no-cache` | TI-05 |
| `Server: nginx/1.18.0 (Ubuntu)` | Versionsangabe sichtbar | informativ |

Es wurden keine POSTs, keine Logins und keine Lastproben gegen Produktion ausgeführt.

---

## 3. Findings

Legende: Quelle = Teilaudit (S Security, T Tests, H Hygiene, E E2E) mit interner ID. „Prod“ = betrifft auch den Stand auf `origin/main`.

### HIGH

#### TI-01 – HIGH – Produktion läuft ohne das Reparatur-Set; Legal-Seiten liefern 500
- **Bereich:** Deployment / Betrieb / Datenschutz
- **Beschreibung:** `origin/main` (`5512451`) enthält die Reparatur-Commits nicht. Folgen auf Produktion: (1) Impressum und Datenschutz liefern 500, weil `routes/public_content.py` die Quelle in `docs/plans/` sucht, die das Image nicht enthält (Fix `7feaade`: `content/legal/`). (2) `deploy.yml` startet auf `push` ohne CI-Abhängigkeit (Fix `d308632`). (3) Reset-Link wird aus dem Request-Host gebaut (Fix `84c4cf0`). (4) Set-Labels werden mit `|safe` gerendert (Fix `84c4cf0`). (5) Das Speaker-Profil zeigt Einwilligungsangaben (`research_views.py:1056–1060` auf `main`) jedem angemeldeten Nutzer (Fix `84c4cf0`). (6) Lock mit 49 Advisories (Fix `a785733`).
- **Evidenz:** `curl` auf die vier Legal-URLs → 500 (2026-10-06). `git merge-base --is-ancestor <commit> origin/main` → NEIN für alle genannten Commits. `git show origin/main:.github/workflows/deploy.yml`: `on: push: branches: [main]`. `git show origin/main:app/src/app/research_views.py` Zeilen 1056–1060: `research_consent_signed`, `teaching_consent_signed`, `consent_date` werden als Profilzeilen ausgegeben. Punkte 3–6 sind aus dem Code von `origin/main` abgeleitet, nicht live ausgeführt.
- **Betroffen:** Produktion, `/impressum`, `/<lang>/privacy`, Deploy-Pipeline, Speaker-Profil, Passwort-Reset-Mails.
- **Repro:** `curl -s -o /dev/null -w '%{http_code}' https://pronunciation-matters.de/impressum`.
- **Ursache:** Reparatur-Branch noch nicht gemergt. Der Merge hat Vorbedingungen (Runbook, Commit `ed2d11f`: `JWT_SECRET_KEY` und `PROMAT_PUBLIC_BASE_URL` auf dem Server prüfen, weil HEAD beides beim Start validiert).
- **Auswirkung:** Pflichtseiten (Impressum, Datenschutz) fehlen öffentlich. Einwilligungsdaten pseudonymisierter Sprecher sind für alle Konten sichtbar. Ein nicht grüner Commit würde ungeprüft deployt.
- **Reparaturrichtung:** Operator-Schritt, kein Code: Pre-Merge-Checks aus dem Runbook ausführen, HEAD (inkl. Preservation-Tooling) nach `main` mergen, nach dem Deploy die Legal-URLs und eine Profilseite prüfen. Danach Branch-Protection mit `release-gate` aktivieren (laut Runbook noch offen).
- **Validierung:** Alle fünf Legal-URLs 200; Login-Link auf der Korpus-Landing; Profilseite ohne Einwilligungszeilen; GitHub: Deploy-Run startet nur per `workflow_run` nach grünem CI.

#### TI-02 – HIGH – Unauthentifizierter, persistenter Ressourcen-Leak über `?_profile=1` / `X-Promat-Profile: 1` (Prod)
- **Bereich:** Verfügbarkeit / Debug-Hook vor Auth
- **Beschreibung:** `research_player()` (`routes/public.py:1135–1165`) registriert bei `_profile=1` oder dem Header zwei SQLAlchemy-Listener auf der prozessweiten Engine, bevor UI-Sprache, Korpus und Auth geprüft werden. `_require_ui_lang()` (Zeile 1165, `abort(404)`) und jede spätere Exception entfernen sie nicht; es gibt kein `try/finally`. Die Listener bleiben bis zum Worker-Neustart.
- **Evidenz:** Selbst gelesen (Zeilen 363–364, 1150–1165). Probe `sec/p18.py` (CONFIRMED, auch mit gepinnten Versionen): 1100 anonyme Requests auf `/xx/research/spanish/player/…?_profile=1` → 1100 Listener-Paare; 2000 `SELECT 1` brauchen danach 0,759 s statt 0,100 s (×7,6). Der Hook ist auch auf `origin/main` vorhanden. Der Hygiene-Teilbericht nennt ihn „entfernt“; das ist falsch (Hook per Code-Lesen in HEAD bestätigt).
- **Betroffen:** nur die Player-Route, aber der Listener wirkt auf alle DB-Zugriffe des Workers.
- **Repro:** `for i in $(seq 1000); do curl -s -o /dev/null -H 'X-Promat-Profile: 1' "$BASE/xx/research/spanish/player/a/b"; done` gegen eine lokale Instanz. Nicht gegen Produktion ausführen.
- **Ursache:** Diagnose-Hook (Performance-Arbeit 2026) ohne Auth-Bindung und ohne Aufräumpfad in den produktiven Code geraten.
- **Auswirkung:** Jeder Besucher kann Query-Latenz und Speicher der Worker dauerhaft verschlechtern (Login, Sets, Auth-Lookups). Das Limit `200/h` je IP bremst nur pro IP; ein Worker-Neustart behebt es vorübergehend.
- **Reparaturrichtung:** Hook aus der Produktions-Route entfernen (oder nur für Admins hinter Config-Flag, request-lokal, mit `try/finally`).
- **Validierung:** `sec/p18.py` zeigt `(0, 0)`; Regressionstest: nach 100 `?_profile=1`-Requests ist die Listener-Zahl der Engine unverändert.

### MEDIUM

#### TI-03 – MEDIUM – Open Redirect `next=////host` (Prod)
- **Bereich:** Return-Targets
- **Beschreibung:** `_safe_next` (`routes/auth.py:66–77`) und `_safe_next_value` (`routes/public.py:103–114`) dekodieren, parsen mit `urlparse` und geben `path[?query]` zurück. `////evil.com` ergibt `netloc=''`, `path='//evil.com'`; der Rückgabewert ist protokollrelativ.
- **Evidenz:** Selbst reproduziert (`urlparse(unquote('////evil.com'))` → `netloc ''`, `path '//evil.com'`). Teilaudit S und E: `GET /login?next=////evil.example/pwn` (angemeldet), `GET /access-request?next=…`, `POST /auth/login` (Form/Query) und Passwortwechsel liefern `303 Location: //evil.example/pwn`; Chromium navigiert tatsächlich dorthin. Sicher dagegen: `//host`, `https://host`, `javascript:`, `\\host`, `/\host`, `%5C`, CRLF, Tab-Varianten. Der unangemeldete Zweistufenweg ist zufällig sicher, weil die Login-Seite den Wert vor dem Rendern normalisiert.
- **Betroffen:** beide Funktionen, vier Aufrufpfade.
- **Ursache:** Keine Allowlist; zwei nahezu identische Implementierungen (TI-31).
- **Auswirkung:** Phishing über die echte Domain für bereits angemeldete Nutzer. Kein Datenabfluss.
- **Reparaturrichtung:** Eine zentrale Funktion: Ergebnis muss mit genau einem `/` beginnen, darf weder `//` am Anfang noch `\` oder Steuerzeichen enthalten, sonst Default-Ziel.
- **Validierung:** Payload-Matrix `sec/p5b.py`, `e2e/t_open_redirect_http.py`; Regressionstest mit `////evil.com`, `/%2F%2F%2Fevil.com`, `/%2F/evil.com`.

#### TI-04 – MEDIUM – Zustandslose Access-Tokens; E-Mail-Wechsel ohne Re-Authentifizierung (Prod)
- **Bereich:** Authentifizierung / Autorisierung
- **Beschreibung:** Weder `_set_auth_context` noch `jwt_required` prüfen nach der Ausstellung Benutzerstatus, Rolle, `access_expires_at` oder `must_reset_password` gegen die DB. Logout löscht nur das Cookie. Zusätzlich setzt `POST /auth/account` die E-Mail (Login-Kennung und Reset-Ziel) ohne aktuelles Passwort und ohne Bestätigung.
- **Evidenz:** `sec/p4.py`, `p22.py`, `e2e/t_logout_replay.py`, `t_revocation.py` (CONFIRMED): Token nach Logout weiter gültig (Seite 200, Audio 200); deaktivierter, soft-gelöschter und herabgestufter Nutzer behält Zugriff (inkl. `POST /api/research/sets` 201 und `/admin/users` 200); Token mit unbekannter `sub` und `role=admin` wird akzeptiert; vor `must_reset_password` ausgestellte Tokens umgehen den Zwang; E-Mail-Änderung `bob@… → attacker@evil.example` mit gültigem Cookie+CSRF.
- **Betroffen:** `app/src/app/__init__.py:_set_auth_context`, `auth/decorators.py`, `routes/auth.py` (logout, account), alle geschützten Routen.
- **Ursache:** Stateless JWT; die Refresh-Token-Infrastruktur existiert, wird aber nicht genutzt (TI-30).
- **Auswirkung:** Zugangsentzug wirkt bis zu 60 Minuten verzögert (Default `ACCESS_TOKEN_EXP=3600`). Mit gestohlenem Cookie wird daraus über E-Mail-Wechsel plus „Passwort vergessen“ eine dauerhafte Übernahme. Autorisierung hängt allein am Signaturschlüssel (TI-11).
- **Reparaturrichtung:** Pro geschütztem Request billiger DB-Lookup (`is_active`, `deleted_at`, `access_expires_at`, `must_reset_password`, Rolle; ggf. 30 s gecacht) oder `token_version` pro Nutzer; E-Mail-Wechsel nur mit aktuellem Passwort und Bestätigungsmail an die neue Adresse.
- **Validierung:** `t_revocation.py` und `p4.py`/`p22.py` müssen nach Logout, Deaktivierung, Rollenwechsel sofort 302/401 liefern.

#### TI-05 – MEDIUM – Keine `Cache-Control`-Direktiven auf geschützten Antworten (Prod)
- **Bereich:** Cache-Verhalten geschützter Inhalte
- **Beschreibung:** `set_security_headers` setzt `no-store, private, Vary: Cookie` nur auf `/auth/*` und `/login`. Research-HTML, `/api/research/sets*`, `/admin/*` (JSON mit E-Mail-Adressen) haben keine Direktive; Audio hat `no-cache` ohne `private`.
- **Evidenz:** `sec/p21.py`, `p12.py`, `e2e/t_headers.py`; Browser-Test: Player öffnen, Logout, „Zurück“ → der geschützte Player (Metadaten, Itemliste) erscheint aus dem Cache; erst Reload leitet auf Login. Produktion zeigt dasselbe Header-Bild (`curl`, siehe 2.1).
- **Ursache:** Header-Logik nur für Auth-Pfade.
- **Auswirkung:** Geschützte Inhalte bleiben auf geteilten Rechnern sichtbar; zwischengeschaltete Caches (nginx-Konfiguration unbekannt) nicht ausgeschlossen.
- **Reparaturrichtung:** `after_request`: für alle nicht öffentlichen Antworten `Cache-Control: private, no-store` (Medien `private, no-cache`) plus `Vary: Cookie`.
- **Validierung:** `e2e/t_headers.py` und Back-Button-Test.

#### TI-06 – MEDIUM – Zugangsanfrage: Status verletzt Postgres-CHECK; Konfigurationsfehler → 500 nach Commit; Token wiederverwendbar (Prod)
- **Bereich:** Formulare / Fehlersicherheit
- **Beschreibung:** (a) Migration `0008_create_access_requests.sql` erlaubt `submitted/reviewed/resolved`; der Code schreibt `notified` und `notification_failed` (`services/access_request_notifications.py:150,162`). Bei erfolgreichem Versand scheitert das Status-Update mit `IntegrityError`, der `except` meldet „notification failed“, die Zeile bleibt `submitted`. (b) `build_access_request_notification_message` läuft **vor** dem `try` (Zeile ~140): fehlt `AUTH_ACCESS_REQUEST_FROM_EMAIL` oder ist die Empfängeradresse ein Platzhalter (`__SET_OPERATOR_EMAIL__`), folgt HTTP 500 nach dem DB-Commit. (c) Das Formular-Token ist wiederverwendbar (zwei Zeilen bei Replay).
- **Evidenz:** Code und Migration selbst gelesen. Constraint-Emulation in SQLite (`sec/p7.py`, `e2e/t_forms_access.py`): beide Statuswerte werden abgelehnt; mit lokalem SMTP-Sink kam die Mail an, das Log meldete trotzdem `IntegrityError`. Der Nutzer sieht korrekt die Danke-Seite. Gegen echtes Postgres nicht ausgeführt (UNKNOWN: tatsächlich angewandter Constraint auf dem Server).
- **Ursache:** SQLite-Migration und `create_all()` kennen den CHECK nicht (TI-18); Statusmodell und Migration auseinandergelaufen.
- **Auswirkung:** Betrieb sieht falsche Zustellfehler und kann echte nicht unterscheiden; bei Fehlkonfiguration Fehlerseite trotz gespeicherter Anfrage und Mehrfach-Einsendungen. Kein Datenleck. Dies ist exakt die historische Fehlerklasse „Backend-Aktion erfolgreich, Anzeige/Zustand irreführend“, hier im Log statt in der UI.
- **Reparaturrichtung:** Idempotente Migration, die den CHECK um die beiden Werte erweitert (oder Code auf erlaubte Werte); Nachrichtenbau in den `try`; Platzhalter-/Format-Validierung der Mail-Variablen beim Start; Token einmalig verwendbar.
- **Validierung:** Test gegen Postgres (Service-Container) mit `deliver_access_request_notification`; `p7.py` Fälle 8/9 → 303 statt 500.

#### TI-07 – MEDIUM – GoatCounter-Drittskript auf geschützten Forschungsseiten (Prod)
- **Bereich:** Datenschutz / Supply Chain
- **Beschreibung:** `base.html:37–40` bindet `https://gc.zgo.at/count.js` (ohne SRI) auf Profil, Player, Comparison und Phenomena ein; ausgenommen sind nur `/admin`, `/auth`, `/login`. Der Pfad enthält pseudonyme Speaker-/Session-IDs. CSP erlaubt `gc.zgo.at` und `connect-src …goatcounter.com` auf allen Seiten.
- **Evidenz:** `sec/p13.py` (Produktionskonfiguration mit `VITE_GOATCOUNTER_URL`). Produktions-CSP enthält `https://gc.zgo.at` (siehe 2.1).
- **Auswirkung:** Pseudonyme IDs gelangen an einen Dritten; ein kompromittiertes Skript läuft im App-Origin neben dem lesbaren `csrf_access_token`-Cookie und könnte authentifizierte API-Aufrufe ausführen.
- **Reparaturrichtung:** Positivliste: Skript nur auf öffentlichen Seiten (project, teaching, design); alternativ vorhandene serverseitige Zählung (`analytics.py`) nutzen. CSP nur dort lockern.
- **Validierung:** `p13.py` erwartet `False` für alle Research-Pfade außer `design`.

#### TI-08 – MEDIUM – Rate-Limiting: Login zählt Erfolge, rohe 429-Seite, Audio unter globalem Limit
- **Bereich:** Verfügbarkeit / UX
- **Beschreibung:** `POST /auth/login` ist `5/min` je IP und zählt erfolgreiche Logins (Gruppenkonten hinter einer NAT sperren sich gegenseitig). Das Default-Limit `200/h` gilt je Endpoint und IP, auch für Audio und `/auth/session`; Request 201 liefert die rohe englische Werkzeug-Seite „Too Many Requests“ ohne `Retry-After`, in der Vergleichsmatrix erscheint „TOO MANY REQUESTS“. Eine Zeile mit drei Sprechern kostet HEAD+GET je Clip (6 Requests). Der Limiter-Schlüssel hängt am rechtesten `X-Forwarded-For`-Eintrag; ob nginx diesen anhängt, ist unbekannt.
- **Evidenz:** `e2e/t_login_throttle.py`, `t_audio_429.py`, `t_ratelimit.py` (Prod-like-Modus); `sec/p8.py`.
- **Auswirkung:** Seminar-Gruppenaccounts und Campus-NAT werden bei normaler Nutzung gedrosselt; Fehlermeldung unverständlich und sprachlich falsch.
- **Reparaturrichtung:** Login nur Fehlversuche zählen (Konto+IP); Medien und `/auth/session` vom Default ausnehmen oder je Nutzer limitieren; lokalisierter 429-Handler (HTML+JSON) mit `Retry-After`; JS übersetzt 429; nginx-Header-Verhalten verifizieren.
- **Validierung:** `t_login_throttle.py`, `t_audio_429.py`, `t_ratelimit.py`.

#### TI-09 – MEDIUM – Set-API: unbekannter `task` → HTTP 500; fehlender Body leert Items; keine Größenlimits (Prod)
- **Bereich:** Fehlersicherheit / Datenintegrität
- **Beschreibung:** `PUT /api/research/sets/{id}/items` mit `{"items":[{"task":"bogus",…}]}` → 500, weil `ResearchConfigError` (`research_presets.py:321`, aufgerufen in `research_sets.py:586`) in `routes/research_api.py:236` nicht auf 400 abgebildet wird. Ein Body ohne JSON oder `{}` liefert 200 und **leert die Items** (`payload.get("items", [])`). Label/Note ohne Längenlimit (200 kB / 1 MB gespeichert); `MAX_CONTENT_LENGTH=None`, ein Formular >500 kB löst einen unbehandelten 413 (nackte 500 mit Doppel-Exception im `after_request`/500-Handler); 30-MB-JSON wird akzeptiert.
- **Evidenz:** `e2e/` F-07; `sec/p19.py`, `p10.py`, `p23.py`.
- **Auswirkung:** Fehlerhafte Clients zerstören Set-Inhalte still; Log-Flut und Speicherdruck durch große Bodies.
- **Reparaturrichtung:** `ResearchConfigError` → 400; `items` verpflichtend, `request.is_json` prüfen; Längen validieren; `MAX_CONTENT_LENGTH` plus 413-Handler ohne Request-Parsing.
- **Validierung:** Probes aus `p19.py` und F-07 → 400/413 statt 500/stilles Leeren.

#### TI-10 – MEDIUM – Redis-Ausfall legt alle Seiten lahm; `/ready` erkennt es nicht
- **Bereich:** Betrieb
- **Evidenz:** Reproduziert (Hygiene `D-03`): `RATELIMIT_STORAGE_URI=redis://127.0.0.1:1/0` → jede Route HTTP 500. `/health` und `/ready` sind `limiter.exempt`; `/ready` prüft für `rate_limit_backend` nur den URI-String (`routes/public.py:851–855`), der Docker-Healthcheck nutzt `/health`.
- **Auswirkung:** Redis-Neustart oder -OOM macht auch öffentliche Seiten 500, während Docker und `/ready` „healthy“ melden.
- **Reparaturrichtung:** Bewusste Entscheidung für `RATELIMIT_SWALLOW_ERRORS=true` (fail-open mit Log; ein In-Memory-Fallback wäre nach AGENTS.md ein verbotener Fallback-Speicher); `/ready` mit echtem `PING`.
- **Validierung:** Test mit abgeschaltetem Redis: Seiten antworten, `/ready` meldet `not_ready`.

#### TI-11 – MEDIUM – Konfiguration fail-open: Env-Auflösung in `main.py`, schwache Secrets zulässig
- **Bereich:** Dev-vs.-Prod-Konfiguration
- **Beschreibung:** `main.py:_resolve_env()` liest nur `FLASK_ENV`, fällt auf `development` zurück und übergibt das explizit an `create_app`; `PROMAT_ENV` wird ignoriert (nachgestellt: nur `PROMAT_ENV=production` → `DEBUG=True`, JWT-CSRF aus, Cookies ohne `Secure`). `load_config` selbst ist fail-closed, aber die Prioritäten weichen ab. Produktion akzeptiert 1-Zeichen-Secrets und `JWT_SECRET_KEY == FLASK_SECRET_KEY`; nur Platzhalter und leere Werte werden abgelehnt. In der Dev-Konfiguration wurde ein mit `__CHANGE_ME__` signierter Admin-Token akzeptiert.
- **Evidenz:** `hyg/` D-04, D-11; `sec/p14.py`, `p24.py`. Produktiv abgefangen nur durch `ENV FLASK_ENV=production` im Dockerfile und das Compose-Mapping.
- **Auswirkung:** Eine Änderung an Dockerfile oder Compose kann unbemerkt eine Debug-Instanz mit abgeschalteter CSRF-Prüfung erzeugen; das Deploy-Preflight prüft die andere Auflösung. Schwaches HS256-Secret erlaubt Admin-Token-Fälschung (verstärkt TI-04).
- **Reparaturrichtung:** Eine Auflösungsfunktion für `config`, `runtime_paths`, `main`; `main.py` fail-closed; Mindestlänge ≥ 32 und Verschiedenheit der Secrets in `load_config`.
- **Validierung:** Unit-Tests in `test_runtime_config.py` für beide Fälle.

#### TI-12 – MEDIUM – Deploy migriert ohne automatisches Backup; Migrationsrunner ohne Versionstabelle; `--reset` ungeschützt
- **Bereich:** Deployment / Migrationen
- **Evidenz:** `scripts/deploy_prod.sh` ruft `apply_auth_migration.py --engine postgres` ohne Aufruf von `scripts/backup_prod_db.sh` (Runbook verlangt ein manuelles Backup). Der Runner führt bei jedem Deploy alle Dateien aus (keine `schema_migrations`; doppelte Präfixe `0006_*`, `0008_*`, `0009_*`); Idempotenz nur per Konvention. `--reset` (DROP TABLE users CASCADE …) ist im Produktionsimage ohne Schutz aufrufbar, anders als `restore_db_dump.sh`.
- **Auswirkung:** Latent: eine künftige nicht-additive Migration läuft automatisch, die Sicherung hängt am Gedächtnis des Operators. Heute sind alle 10 Migrationen additiv und idempotent (zweimal auf Postgres 15 verifiziert).
- **Reparaturrichtung:** Backup vor Migration im Deploy (Skript existiert und wird in CI geprobt); `schema_migrations`; `--reset` unter Produktion sperren.
- **Validierung:** CI-Rehearsal: zweiter Lauf wendet nichts an; `--reset` bricht unter `production` ab.

#### TI-13 – MEDIUM – Passwort-Reset-Token im Access-Log, 14 Tage gültig (Prod)
- **Evidenz:** `app/Dockerfile` startet Gunicorn mit `--access-logfile -` (Standardformat enthält die Query); der Reset-Link ist `GET /auth/password/reset?token=…`; `AUTH_RESET_TOKEN_EXP_DAYS` Default 14; Compose setzt keine Log-Rotation.
- **Auswirkung:** Gültige Einmal-Token liegen bis zu 14 Tage im Container-Log (und in nginx-Logs, Format unbekannt). Wer Logzugriff hat, kann Konten übernehmen, solange das Token ungenutzt ist.
- **Reparaturrichtung:** `--access-logformat` ohne Query, Token per POST/Fragment, Log-Rotation, Reset-Gültigkeit kürzen (z. B. 1 h; Einladungen länger).
- **Validierung:** Request mit `?token=x` ausführen, Log prüfen.

#### TI-14 – MEDIUM (bedingt) – Entwicklungsumgebung lauscht auf allen Interfaces mit Repo-Zugangsdaten und echten Daten
- **Evidenz:** `docker-compose.dev-postgres.yml` publiziert `54321:5432` ohne `127.0.0.1` (live verifiziert: `0.0.0.0:54321`), Zugangsdaten `promat_auth/promat_auth`; `main.py` startet `run_simple("0.0.0.0", 8000, use_debugger=True)`; `dev-start.ps1` legt `admin_dev` / `Admin0000!` an; Dev-Secrets stehen im Repo. Die Workstation enthält die echten Sessions (`data/sessions`, ~1 GB).
- **Auswirkung:** Im selben Netz (offene Windows-Firewall unbekannt, daher bedingt) sind DB, Dev-App mit Debugger und Admin-Login erreichbar. Produktion nicht betroffen.
- **Reparaturrichtung:** Bindung an `127.0.0.1`; Dev-Secrets und Admin-Passwort pro Maschine zufällig; Postgres-Port nur an Loopback.
- **Validierung:** `docker port`, `netstat -an`.

#### TI-15 – MEDIUM – `requirements.in` unvollständig: `markdown-it-py` nur transitiv gelockt
- **Evidenz:** `public_content.py:10` und `teaching_content.py:17` importieren `markdown_it`; `requirements.in` listet es nicht. Im Lock steht es nur „via rich“ ← „via flask-limiter“. Eine frische `uv pip compile` (flask-limiter 4.1.1) entfernt `rich` und damit `markdown-it-py` (reproduziert).
- **Auswirkung:** Eine Lock-Regenerierung (z. B. Dependabot) bricht Legal- und Teaching-Seiten beim Import. Das CI-Gate würde es abfangen (Deploy blockiert, kein Produktionsausfall), die Ursache wäre schwer zu deuten.
- **Reparaturrichtung:** `markdown-it-py` in `requirements.in`; Lock mit dem dokumentierten Werkzeug erzeugen; alle Import-Roots gegen `requirements.in` prüfen.
- **Validierung:** Frische Kompilation ohne Paketdifferenz; `import app.routes.public_content` in leerem venv.

#### TI-16 – MEDIUM – Testsuite schützt das Frontend-Verhalten nicht (Stop, „Alle Items“, JS lädt)
- **Bereich:** Testqualität / Regression-Sicherheit
- **Beschreibung:** 7 JS-Tests in 4 Dateien prüfen nur reine Hilfsfunktionen. `research-player.js` (1348 Z.), `research-comparison.js` (1747 Z.), der Phänomene-Editor und `admin_users.js` (~10 000 Zeilen JS gesamt) haben keinen Verhaltenstest. Es gibt keinen Browser-Test (Marker `e2e`/`live` hat 0 Nutzer); `responsive_smoke.py` endet immer mit Exit 0 und „Skipping“ ohne Secrets ist grün.
- **Evidenz (Mutationsproben, im Worktree ausgeführt und zurückgesetzt):** M13/M14 (Stop-Logik und Stop-Icon der Vergleichsmatrix entfernt) → pytest und node grün; M21 (Player: „Alle Items“ nie `current`) → grün; M22 (Vergleichs-JS gibt immer `set_id` in die URL) → grün; M24 (Syntaxfehler in `research-player.js`) → grün. `test_research_comparison.py:481` prüft sogar die **Abwesenheit** von `data-comparison-stop` im Server-HTML. ~29 Phänomene-Editor-Tests sind Substring-Greps auf JS-Quelltext.
- **Reales Verhalten:** Im Browser-Audit sind alle diese Invarianten **erfüllt** (60/60 Comparison, 90/90 Player, Stop mitten in der Sequenz, 0 überlappende Audios). Sie sind heute korrekt, aber nicht abgesichert.
- **Reparaturrichtung:** Ein Playwright-Smoke in CI (Playwright liegt im venv) gegen eine Fixture-Runtime: Login-`next`-Roundtrip, Stop sichtbar und wirksam (Audio gestubbt), „Alle Items“ bleibt beim Wechsel Player↔Vergleich, Seite lädt ohne Konsolenfehler; alternativ JSDOM-Tests der Module.
- **Validierung:** Die vier überlebenden Mutationen (M13, M14, M21/M22, M24) müssen den Smoke rot färben.

#### TI-17 – MEDIUM – Testsuite prüft die produktive Komposition, JSON-API-Gates und Client-Payloads nicht
- **Beschreibung:** `create_app()`/`register_blueprints()` wird von keinem Test aufgerufen; alle Test-Apps sind handgebaut. Die Gate-Matrix der Detailrouten läuft mit Auth-Stub (`g.user_id` aus Config); echter JWT-Pfad nur für 3 Seiten und Spanisch. Für `/api/research/sets*` existiert nur ein Admin-Unauth-Test.
- **Evidenz:** M20 (`@jwt_required()` von `GET /api/research/sets/<id>` entfernt) → grün. M17 (Consent, `researchConsent`, `secureNotes` in `sessionCatalog` serialisiert) → grün; es gibt keine Negativ-Allowlist für HTML-`data-*`, Client-State-JSON und API-JSON. Set-Isolation ist nur für GET+PATCH getestet (M11/M12 hängen an einem einzigen Test), Gruppenaccounts gar nicht.
- **Reales Verhalten:** Ad-hoc geprüft korrekt (echtes `create_app("production")`: alle Research-Detail-/Medienrouten, alle `/api/research/*`, `/admin*` ohne Login 302/303/401; alle sieben Set-Verben für Fremdnutzer, Gruppe und Admin 404; keine Consent-Marker in HTML oder JSON).
- **Reparaturrichtung:** Routen-Matrix über `create_app("testing")` mit Allowlist für öffentliche Routen und Fail bei unklassifizierter Route; Negativ-Allowlist mit Sentinel-Werten für HTML, `data-*` und JSON; Set-Isolation parametrisiert über alle Verben als Fremdnutzer **und** Gruppenaccount.
- **Validierung:** M17 und M20 müssen rot werden.

#### TI-18 – MEDIUM – Tests laufen auf SQLite mit `create_all()`, Produktion auf Postgres mit SQL-Migrationen
- **Evidenz:** Alle App-Tests nutzen SQLite; Modell↔Migration-Gleichheit wird nicht getestet (`test_research_sets.py:255` greppt nur Migrationstext). Postgres sieht CI nur im Backup/Restore-Rehearsal. Dadurch blieb TI-06 unentdeckt. `RATE_LIMIT_STORAGE_URI=redis://…` in der CI-Env ist wirkungslos (alle Tests nutzen `memory://`; verifiziert: identisches Ergebnis). Der Produktionspfad (`ProductionConfig`, HSTS, Secure-Cookies, JWT-CSRF) wird nie als laufende App getestet; `TestingConfig` schaltet CSRF und Secure aus.
- **Reparaturrichtung:** Postgres-Service im `python`-Job für Auth/Sets/AccessRequest (oder `pytest -m postgres`) plus ein Schema-Paritätstest; ein Smoke mit `ProductionConfig` und CSRF.
- **Validierung:** Der CHECK-Konflikt aus TI-06 macht den neuen Test rot, bevor die Migration existiert.

#### TI-19 – MEDIUM – Realdaten-Drift: Fixtures, `data`-Tests außerhalb von CI, Registry und i18n ohne Vollständigkeitstest
- **Evidenz:** Fixtures lassen `files[]`, `derived_file`, `needs_review` weg und enthalten `consent_file`/`questionnaire_file`/`secure_notes`, die real nicht im Runtime-JSON stehen (65 reale `metadata.json`; nur Feldnamen verglichen); nur `target_language=es` und `es_std`. Die 7 `data`-Tests und `validate_research_config.py` laufen weder in CI noch im Deploy. M15 (`fr_std` aus der Varietäten-Registry entfernt, obwohl in echten Daten vorhanden) → grün; M16 (en-i18n-Key entfernt) → volle Suite grün; `test_research_sessions.py:3709` kodiert „Unknown Var“ für unbekannte Codes als Soll. M10 (numerischer `sequence`-Sortierschlüssel entfernt) → grün. Authentifizierte Workbench-Tests existieren nur für Spanisch (31 französische, 10 englische reale Sessions).
- **Reales Verhalten:** Alle Registry-Codes, i18n-Schlüssel (907/907), kanonische Item-Labels (36/36 über Katalog, Player, Editor, Matrix) und die Sortierung sind heute korrekt.
- **Reparaturrichtung:** Registry-Vollständigkeits- und i18n-Paritätstest; Golden-`metadata.json` im Realformat statt fünf kopierter `_learner_payload`; je eine französische und englische Fixture-Session in den Workbench-Tests; `validate_research_config.py` als Deploy-Vorprüfung.
- **Validierung:** M10, M15, M16 werden rot.

#### TI-20 – MEDIUM – Mobile 390 px: Set-Auswahl im Player außerhalb des Viewports, Überläufe, Speakers-Tabelle nicht gestapelt
- **Evidenz:** Browser, de und en (`e2e/shots/top_mob_en_*.png`): Player (wordlist/text/compare) `scrollWidth 463 > 390`, das `select` „Set wählen“ liegt bei x≈463; Comparison 11 px Überlauf; Speakers-Tabelle 873 px breit statt Stapelkarten (Spec `research-access.md`, Abschnitt speakers). Desktop 1280: kein Überlauf.
- **Reparaturrichtung:** Material-Strip auf Mobile umbrechen, Tabelle unter Breakpoint stapeln; UI-Regeln aus AGENTS.md (Browser-Pass beider Sprachen) einhalten.
- **Validierung:** Screenshots 390 px in de/en auf Player, Comparison, Speakers.

### LOW

| ID | Titel | Evidenz (Kurz) | Auswirkung | Fix-Richtung | Validierung |
|---|---|---|---|---|---|
| TI-21 | Teaching-Media-Route: `teaching_lang`/`topic_slug` nicht validiert, Entwurfsstatus ignoriert | `sec/p11.py`: `GET /teaching-media/../private/audio/x.mp3` lieferte eine Datei aus einem Geschwisterverzeichnis (`teaching_content.py:377–407`); im Produktionslayout derzeit keine Ziele außerhalb | Verletzt Spec-Regel „nur topic-lokaler Media-Root“; praktisch begrenzt | Sprache gegen Liste, Slug gegen `[a-z0-9-]+`, `relative_to(root)` erzwingen | `p11.py` → 404 |
| TI-22 | Login-Timing-Enumeration, Lockout-Missbrauch, synchroner SMTP-Versand | `sec/p6.py`, `p8.py`: unbekannter Nutzer 1–6 ms, bekannter ~50 ms; Forgot 2–4 s vs. 0,01 s (`e2e`); Lockout pro Konto, `verify_password` läuft während der Sperre weiter; Zugangsanfrage blockiert einen Worker bis 10 s | Konto-Enumeration per Timing; Worker-Blockade bei hängendem SMTP | Dummy-Argon2 bei unbekanntem Nutzer, Lockout vor Passwortprüfung, Mailversand asynchron | `p6.py`, `t_forms_forgot.py` |
| TI-23 | `/ready` öffentlich, ungedrosselt, mit Exception-Text und Schreibprobe | Live: `/ready` liefert JSON mit Checks; `sec/p20.py`: DB-Fehlertext inkl. Hostname; schreibt bei jedem Aufruf `.promat-ready-probe` | Informationsleck, billige Last | Extern nur Status, Details ins Log, Schreibprobe entfernen | `p20.py` |
| TI-24 | Zugangsanfragen: roher `X-Forwarded-For`, User-Agent, keine Aufbewahrungsfrist; Datenschutztext nennt beides nicht | `routes/public.py:769`; `content/legal/impressum_datenschutz.md` Abschnitt 5 | Datenschutz | IP aus `remote_addr`, Frist plus Cleanup-CLI, Text ergänzen | `p7.py` |
| TI-25 | Admin-PATCH verletzt Kontoinvarianten (Gruppenkonto → Admin, E-Mail setzbar) | `sec/p15.py`; Spec `auth-accounts.md` | Spec-Verletzung durch Admin-Aktion | Serverseitige Invariantenprüfung | `p15.py` |
| TI-26 | Logout per GET ohne CSRF; Login ohne CSRF-Token | `/auth/logout[_any]` akzeptiert GET | Fremdes `<img>` meldet Nutzer ab; Login-CSRF | Nur POST+CSRF (Frontend nutzt bereits POST-fetch) | Test |
| TI-27 | Datenschutz-Beobachtungen: `person_notes`, `session_notes`, `recorded_by` (Klarnamen), Interviewtranskripte für alle Konten (laut Spec); Set-API gibt `created_by_user_id`/`updated_by_user_id` (Admin-UUIDs) aus; keine Zurechenbarkeit von Audio-Downloads bei Gruppenkonten | `research_sets.py:233–262`; 11 reale Notizfelder gefüllt, ohne E-Mail/Telefon/URL-Muster | Kein Spec-Verstoß; Fachentscheidung nötig | Redaktionsregel für Notizen; interne IDs aus der Set-API entfernen | Sentinel-Test (TI-17) |
| TI-28 | `ProxyFix(x_host=1, x_prefix=1)` ohne `TRUSTED_HOSTS` | `__init__.py:185`; Werkzeug-Redirects und `url_for` nutzen Client-Header | Cache-Poisoning nur bei Cache davor (nginx unbekannt) | `TRUSTED_HOSTS`, `x_prefix=0`, nginx überschreibt `Host`/`X-Forwarded-*` | Test mit gefälschtem Host |
| TI-29 | Container/Image: Root-Prozess, kein `.dockerignore`, Tests und `.vscode` im Image, Basisimage und pip ungepinnt, `compose build` ohne `--pull`, Redis/Postgres schwebende Tags, veralteter `X-XSS-Protection`, kein `Permissions-Policy` | `docker run … id` → uid 0; `COPY app/ ./` | Root im Container; CI-getestetes Image kann vom Prod-Image abweichen | `.dockerignore`, `USER`, `--pull`, Digest-Pin | `ci_image_smoke.py` |
| TI-30 | Ungenutzte Pakete, toter Code, tote Statics | `imageio-ffmpeg` = 77 MB von 92 MB site-packages (ungenutzt, enthält ffmpeg-Binary), `pydub`, `httpx`, `requests`, `python-dotenv`, `Flask-Caching` (initialisiert, nie genutzt), `openpyxl` nur Intake; Module `auth/loader.py`, `auth/jwt.py`, Refresh-Token-System ohne Aufrufer, 36 ungenutzte Funktionen in `research_views.py` (~283 Zeilen), 14 von 25 Branding-Keys (vier verweisen auf fehlende Dateien), jQuery 3.7.1 ungenutzt, htmx 1.9.10 auf jeder Seite geladen ohne ein `hx-`-Attribut, 8 verwaiste JS-Dateien, 5 verwaiste Bilder | Angriffsfläche, Image-Größe, Verwirrung bei Audits | Entfernen in separatem Commit (Tabellen nicht ohne Migration anfassen) | vulture, Tests, Browser-Pass |
| TI-31 | Doppelte Implementierungen | `_safe_next` vs. `_safe_next_value` (Ursache von TI-03), `_resolve_request_ui_language` doppelt, `_build_access_request_href` doppelt, Korpus-Registry mindestens sechsfach (`LANGUAGES`, `analytics.TRACKED_CORPORA`, ungenutzte `ACTIVE_RESEARCH_CORPORA`, `admin.py:573`, `data_conventions.py`, DB-CHECK), zweite hartkodierte Sprachtabelle in `apply_prod_db_payload.py` (Dockerfile kopiert `language_config.py` nicht); Legacy-Pfade `/datenschutz`, `/auth/konto`, `LEGACY_ROLE_ALIASES` ohne Spec-Grundlage (AGENTS.md verbietet alte Slugs) | Drift-Risiko; eine fünfte Sprache braucht ~6 Edits | Gemeinsame Module, eine Registry, Legacy-Routen per Entscheidung entfernen oder in die Spec aufnehmen | Test „Korpusmengen identisch“ |
| TI-32 | Repo-Hygiene | Kein `.gitattributes` (`core.autocrlf=true`, Arbeitsbaum CRLF in allen `scripts/*.sh`); 248 MB `tmp_obj` in `.git/objects`; `.claude/worktrees/` untracked und nicht ignoriert; getracktes `.claude/settings.json` erlaubt `Bash(python -c ' *)` ohne Rückfrage; `console.log` in 4 produktiven JS-Dateien; `create_engine` ohne `pool_pre_ping`; keine Commit-SHA zur Laufzeit sichtbar; `tmp/` mit losen Skripten statt `tmp/ui-qa/<datum>-<thema>/` | Shell-Skripte mit CRLF im Deploy möglich; versehentliches `git add .` | `.gitattributes` (`*.sh text eol=lf`), `git gc`, Ignore-Eintrag, `settings.json` prüfen | `git ls-files --eol`, `git count-objects -vH` |
| TI-33 | Workflow-Details | `release-candidate-check.yml:54` interpoliert einen `workflow_dispatch`-Input direkt in `run:`; `deploy.yml` per `workflow_dispatch` führt die Workflow-Datei des gewählten Refs auf dem selbst gehosteten Runner aus; Actions per Tag, nicht SHA | Skript-Injektion durch Personen mit Schreibrecht; ohne Branch-Protection nicht durchgesetzt | Input über `env:`, `environment: production` mit Branch-Einschränkung, Branch-Schutz | `actionlint` |
| TI-34 | Daten-/Inhaltsdefekte | Roher Code `[wl_032-]` im Interview ES-L-0014 (de+en; Datenfehler im Alignment, einziger Treffer in allen Sessions); „curated“/„custom“/„Draft“ englisch in der deutschen UI (`i18n.py:564,567`); deutsche `<meta description>` auf `/en/…`-Seiten | Sichtbare Sprachmischung, unaufgelöster Code | Intake-/Annotationsregel für Abbruchmarker; i18n-Werte und Meta-Description lokalisieren | `e2e/t_data_raw_codes.py`, `t_crawl.py` |
| TI-35 | Konsistenzabweichungen | Jeder Comparison-Besuch mit Sprecherauswahl legt einen Draft an (Cleanup nur per CLI); leer gespeicherte Sets erlaubt; Topbar-Login auf Korpus-Landing → Korpus-Root statt `/speakers` (Spec `research-access.md:49`); Matrix-Spaltenreihenfolge = Klickreihenfolge; unbekanntes Teaching-Topic → 302 statt 404; 401-JSON mit Bibliothekstext; Login-Seite verlinkt sich selbst; kein dokumentierter Dev-Start ohne Docker | Kleine Spec-/UX-Abweichungen | Je Punkt Entscheidung (Spec oder Code) | `e2e/t_login_targets.py` |
| TI-36 | Tests mit geringem Informationswert / OS-fragil | 1 Fehlschlag unter Windows (WSL-`bash`), `subprocess` ohne `encoding`; Test-Name widerspricht Assertion (`research_ui_state_helpers.test.mjs:114`); `test_upload_prod_package.py:37` ohne Assertion; Fixture-Tautologie `test_research_config_fixtures.py:82`; CSS-Token-Snapshot (`test_research_sessions.py:2359`); ~29 Source-Grep-Tests | Falsche Sicherheit, Wartungskosten, Suite auf der Maintainer-Maschine nicht grün | Windows-Skips, Verhaltenstests statt Greps, Namen korrigieren | Lauf unter Windows und Linux |
| TI-37 | `passlib 1.7.4` trägt auf dem Pin `bcrypt==4.1.3` | Mit `bcrypt==5.0.0` wirft `passlib.hash.bcrypt.hash` `ValueError`; Fallbacks in `auth/services.py:50–120` fangen es ab | Dependabot könnte den Pin still brechen | Kommentar/Obergrenze `bcrypt<5` mit Begründung; passlib-Ablösung erst vor Python 3.13 | Lock-Regeneration + Auth-Tests |

---

## 4. Test-Gap-Matrix

Verdikte: **getestet** / **teilweise** / **nicht getestet** / **Scheinsicherheit** (ein Test suggeriert Schutz, deckt die Invariante aber nicht ab). „Reales Verhalten“ = im Audit ausgeführt (HEAD), unabhängig von den Tests.

| # | Invariante | Reales Verhalten | Testabsicherung | Verdikt / Beleg |
|---|---|---|---|---|
| 1 | Geschützte HTML-Seiten ohne Login unerreichbar, 4 Korpora × de/en | korrekt | Parametrisierte Gate-Matrix (Auth-Stub) plus echter Auth-Kontext nur Spanisch/3 Seiten | getestet (M1–M5 rot) |
| 2 | Detail-/Audio-Routen vor Lookup gegated, kein Existenz-Orakel | korrekt | `test_research_sessions.py:3020` | getestet (M1, M2, M4 rot) |
| 3 | `/api/research/*` ohne Login 401 | korrekt (alle 15 Routen) | nur Admin-Endpunkte | teilweise (M20 grün) |
| 4 | Echte Komposition (`create_app`) enthält alle Gates/Header | korrekt | kein Test ruft `create_app` | nicht getestet |
| 5 | Geschützte Daten unabhängig vom Zugriffsweg (Audio, JSON, HTML, Statics) | korrekt | HTML/Audio teilweise, JSON/Payload nicht | teilweise |
| 6 | Login erhält das gewählte Ziel (Speakers, Vergleich, Phänomene, Korpus→`/speakers`, Query/`source`) | korrekt in 68 Fällen, beide Sprachen | DE-Roundtrip getestet, EN nur Rendering | getestet (DE) / teilweise (EN) |
| 7 | Open-Redirect-Abwehr | **verletzt** (`////host`) | `https://` und `//` getestet | Scheinsicherheit (M7 äquivalenter Mutant; `////` nie getestet) |
| 8 | Logout → Wiederzugriff verweigert, Token ungültig | **verletzt** (Token gültig, Back-Button zeigt Seite) | nur Cookie-Löschung | Scheinsicherheit |
| 9 | Owner-gebundene Sets, Gruppenaccounts | korrekt (alle 7 Verben, Nutzer/Gruppe/Admin) | nur GET+PATCH, ein Test | teilweise / Gruppenaccount nicht getestet |
| 10 | Interne Metadaten (Consent, Freigaben, Notizen, IDs) nicht an Nutzer serialisiert | korrekt in HEAD (Profil, Player, Comparison-Katalog, API); `created_by_user_id` in Set-API sichtbar | Profil-HTML getestet (M18 rot) | teilweise (M17 grün: JSON/`data-*` nicht abgedeckt) |
| 11 | „Alle Items“ bleibt gewählt, Filter mutieren keine Daten | korrekt (60/60, 90/90) | Tests prüfen Label und Position, nicht die Selektion | Scheinsicherheit (M21, M22 grün) |
| 12 | Sequenzwiedergabe hat Stop, Audio stoppt bei Navigation | korrekt | keine; ein Test prüft die Abwesenheit des Hooks | Scheinsicherheit (M13, M14 grün) |
| 13 | Player-JS lädt und läuft | korrekt | keine | nicht getestet (M24 grün) |
| 14 | Sortierung Lernende vor Natives | korrekt (44 Listen) | Grundordnung getestet | teilweise (M10: numerischer Schlüssel ungeprüft) |
| 15 | Standardvarietäten-Codes immer als Label | korrekt für alle realen Codes | 14 Fälle, Registry nicht iteriert, „Unknown Var“ als Soll | teilweise (M15 grün) |
| 16 | Kanonische Item-Labels aus einer Quelle, inkl. `théâtre` | korrekt (36/36) | Fixture-Tautologie; echter Test nur `data` | Scheinsicherheit |
| 17 | i18n-Parität, keine ungelösten Keys | korrekt (907/907) | keine | nicht getestet (M16 grün) |
| 18 | Zugangsanfrage: Backend ok + Notify-Fehler → Erfolg ohne 500 | korrekt in der UI | Fehlerpfade getestet (M19 rot) | getestet; Postgres-Status siehe 19 |
| 19 | Zugangsanfrage-Status konsistent mit DB-Schema | **verletzt** (CHECK) | SQLite ohne CHECK | Scheinsicherheit |
| 20 | Doppeltes Absenden, Token-Replay | zwei Zeilen bei Replay, Doppelklick eine Zeile | nein | nicht getestet |
| 21 | Fehler im Backend → konsistenter Frontend-Zustand (Sets) | **verletzt** (500 bei unbekanntem `task`, stilles Leeren) | nein | nicht getestet |
| 22 | Sprachbereiche strukturell konsistent (es, fr, en, de) | korrekt | Gate/Landing/Design für alle vier, authentifizierte Workbench nur Spanisch | teilweise |
| 23 | Leere und Fehlzustände (leere Sets, unbekannte IDs, 404-Seiten) | korrekt, lokalisiert | leere Zustände getestet, unbekannte Speaker/Session/Set nicht | teilweise |
| 24 | Postgres-Verhalten, Migrationen ↔ Modelle | Modelle = Schema (manuell geprüft) | SQLite + `create_all` | Scheinsicherheit |
| 25 | Produktionskonfiguration als laufende App | nicht im Test, Verhalten korrekt in Prod-like-Lauf | nur `load_config`-Unit-Tests | teilweise |
| 26 | Release-Gate: nur grüner CI-Lauf wird deployt | in HEAD korrekt, auf `main` nicht | Meta-Tests `test_ci_workflows.py` | getestet (nur HEAD) |

---

## 5. Priorisierung

### P0 – vor weiterer Production-Nutzung beheben
- **TI-01:** Reparatur-Set nach `main` bringen (Operator-Schritt mit Vorprüfung) und Legal-Seiten, Profil und Deploy-Gate verifizieren. Das ist der einzige tatsächliche Produktions-Blocker.
- **TI-02:** `_profile`-Hook entfernen. Sehr kleiner Eingriff, höchste Wirkung; gehört in den Merge-Kandidaten, bevor er produktiv wird, da er derzeit schon auf `main` liegt.

### P1 – zeitnah beheben
- TI-03 (Open Redirect), TI-04 (Token-/Statusprüfung, E-Mail-Wechsel), TI-05 (Cache-Control), TI-06 (Access-Request-Status/500), TI-07 (GoatCounter), TI-08 (Rate-Limit-UX), TI-09 (Set-API-Robustheit), TI-10 (Redis-Ausfall), TI-11 (Config fail-open), TI-12 (Backup vor Migration), TI-13 (Token im Access-Log).
- Test-Lücken mit realem Regressionsrisiko: TI-16, TI-17, TI-18.

### P2 – sinnvoll, aber nicht dringend
- TI-14 (bedingt, aber trivial zu beheben), TI-15, TI-19, TI-20 (Mobile-UI-Run) sowie alle LOW-Befunde TI-21 bis TI-37.

### Kein Handlungsbedarf (geprüft und belastbar in Ordnung)
- **Gate vor Lookup**, kein 404/401-Orakel, auch bei HEAD und Pfadvarianten (`/DE`, `//`, `;`, `%00`); nur `design` je Korpus öffentlich (4 Korpora × de/en).
- **Owner-Bindung und IDOR bei Sets** (Nutzer, Gruppe, Admin, anonym; alle sieben Verben; Mass-Assignment ignoriert); `include_archived_curated` nur Admin.
- **JWT-Verifikation:** falsches Secret, `alg=none`, Refresh-Typ, abgelaufen, manipuliert, leeres Cookie werden abgelehnt; Cookie `HttpOnly; Secure; SameSite=Lax`; CSRF-Double-Submit im Prod-Modus aktiv.
- **XSS:** serverseitig (Reflexion, Stored, Anzeigenamen, Set-Labels), `|safe`-Fallback escaped, `innerHTML`-Stellen escapen, JSON-in-Script via `tojson`; CSP ohne `unsafe-eval` und ohne `unsafe-inline` für Skripte. Kein Roh-SQL, keine Mail-Header-Injection, `yaml.safe_load`.
- **Audio-Auslieferung:** Pfade nur aus Session-ID-Lookup mit `relative_to(session_root)`; kein Zugriff auf `data/`, `public/`, `secure/`; Range 206/416; Traversal 404. `data/sessions` enthält nur `.mp3`/`.json`.
- **S1 (Reset-Link-Poisoning), S2 (Label-Injection), S7 (Consent im Profil)** in HEAD behoben und mit gefälschten Headern bzw. Sentinel-Werten ausgeführt; **Dependency-Lock** (nur 1 irrelevantes Advisory); **keine Secrets oder Binärdaten im Repo und in der Git-Historie**; Prod-Compose bindet nur `127.0.0.1:8000`, DB/Redis ohne Host-Port, Daten `:ro`.
- **Deploy-Skript, Backup-/Restore-Skripte, CI-Gate** in HEAD (Vollsuite, JS, Docker-Build, Image-Smoke, Postgres-Rehearsal, `release-gate`, `workflow_run`, Meta-Tests); Migrationen auf Postgres 15 idempotent.
- **Historische Regressionsklassen im Browser** (siehe Abschnitt 6): alle bis auf die in TI-03/TI-34 genannten Einzelfälle bestanden.
- **Teaching öffentlich** (152 Seiten, 8 MP3, Range 206, 0 kaputte Links), Fehlerseiten lokalisiert ohne Stacktrace (24 Fälle × 2 Sprachen), DE↔EN-Wechsel erhält Zustand, Python-3.12-Konsistenz, ruff, compileall, Governance, Teaching-Validierung.

### Cross-cutting Invarianten

| Invariante | Ergebnis |
|---|---|
| Geschützte Daten unabhängig vom Zugriffsweg geschützt | erfüllt (HTML, JSON, Audio, Statics); Einschränkung: gültiges Token nach Logout (TI-04), Browser-Cache (TI-05) |
| Login verändert das gewählte Ziel nicht | erfüllt in 68 Fällen; Ausnahme Open Redirect (TI-03) |
| Sprachbereiche strukturell konsistent | erfüllt für es/fr/en; german konsistent Platzhalter |
| UI-Filter verändern Daten nicht | erfüllt (Comparison unverändert nach Interaktion), aber ungetestet (TI-16) |
| Audiozustand konsistent nach Navigation/Wechsel | erfüllt, ungetestet (TI-16) |
| Interne Metadaten werden nicht serialisiert | erfüllt in HEAD; **nicht auf Produktion** (TI-01); Client-Payloads ungetestet (TI-17) |
| Kanonische Bezeichnungen haben eine Quelle | erfüllt (36/36); Korpus-Registry in ≥ 6 Kopien (TI-31) |
| Backend-Fehler führen nicht zu irreführendem Frontend-Zustand | überwiegend erfüllt; Ausnahmen TI-06 (Status), TI-08 (rohe 429), TI-09 (stilles Leeren) |
| Zugriffsentzug wirkt sofort | **nicht erfüllt** (TI-04) |
| Prod-Konfiguration kann nicht versehentlich Dev werden | **nicht erfüllt** (TI-11) |

---

## 6. Historische Regressionsklassen (Browser-Evidenz)

| Klasse | Ergebnis | Evidenz |
|---|---|---|
| Wechsel „Alle Items“ → Set | PASS | Comparison 60/60, Player 90/90 über alle Einstiegsquellen; gespeicherte Sets bleiben unverändert |
| Fehlender Stop bei Sequenzwiedergabe | PASS | Zeilenbutton wird „Stoppen/Stop“, Stop mitten in der Sequenz → 0 weitere `play`-Events, nie mehr als ein Audio, Navigation stoppt |
| Reihenfolge Learners/Natives | PASS | 44 Listen (Karten, Tabelle, Filter), Lernende zuerst, ID aufsteigend; Matrix-Spalten folgen der Klickreihenfolge (TI-35) |
| Unaufgelöste Codes/Slugs | PASS bis auf 1 Datenfall | `[wl_032-]` in ES-L-0014 (TI-34); keine Translation-Keys, kein `undefined`/`{{` im Crawl (~730 Seiten) |
| Inkonsistente kanonische Item-Labels | PASS | 36/36 über Katalog, Player, Phänomene-Editor, Matrix |
| Falsche Login-Return-Targets | PASS (68 Fälle), 1 Open-Redirect-Variante | TI-03 |
| Backend erfolgreich, UI zeigt Fehler | kein Fall gefunden | Set speichern/umbenennen/löschen, Zugangsanfrage mit SMTP down, Forgot-Password, CSRF-Flows; verwandt: TI-08 (429), TI-06 (Log) |
| Inkonsistenz zwischen Sprachbereichen | PASS | identisches Verhalten es/fr/en; german konsistent „im Aufbau“ |

---

## 7. Repair Plan

Wenige abgegrenzte Läufe. Kein Fund hinterlässt eine offene Architektur- oder Ursachenfrage, daher wird Opus nicht empfohlen. Jeder Lauf schreibt einen Eintrag unter `docs/agent-runs/` und aktualisiert die betroffene Spec in `docs/spec/` (AGENTS.md).

### Lauf 0 – Operator: Reparatur-Set nach `main` (kein Modell, ca. 30 Minuten)
- **Scope:** TI-01.
- **Änderung:** Runbook-Vorprüfung (`JWT_SECRET_KEY`, `PROMAT_PUBLIC_BASE_URL`, Backup), Merge von HEAD nach `main`, Branch-Protection mit `release-gate`.
- **Validierung:** `/impressum`, `/de/privacy` → 200; Profilseite ohne Einwilligungszeilen; Deploy-Run startet nur nach grünem CI.
- **Modell:** keines; ein Verifikations-Lauf mit Sonnet 5.5 Low ist optional.
- Empfohlene Reihenfolge: Lauf 1 vor dem Merge, damit TI-02 nicht noch einmal produktiv geht.

### Lauf 1 – Web-Härtung klein und mechanisch
- **Scope:** TI-02, TI-03 (zusammen mit der Zusammenführung der zwei `_safe_next`, TI-31 Teil), TI-05, TI-07, TI-09, TI-21, TI-26.
- **Änderung:** Profil-Hook entfernen; eine zentrale Redirect-Funktion; `Cache-Control` im `after_request`; GoatCounter nur auf öffentlichen Seiten; Fehlerabbildung in der Set-API plus `MAX_CONTENT_LENGTH` und 413-Handler; Validierung in der Teaching-Media-Route; Logout nur per POST.
- **Validierung:** `sec/p18.py`, `p5b.py`, `p21.py`, `p19.py`, `p11.py`, `p13.py`; je ein fokussierter Regressionstest.
- **Modell:** Sonnet 5.5 Medium.

### Lauf 2 – Zugangsprozess und Datenbank-Parität
- **Scope:** TI-06, TI-18, Teile von TI-12.
- **Änderung:** Migration 0011 (CHECK erweitern), Nachrichtenbau in den `try`, Start-Validierung der Mail-Variablen, einmaliges Token; Postgres-Service im CI `python`-Job und ein Schema-Paritätstest; Backup-Aufruf vor der Migration im Deploy; `--reset` unter Produktion sperren.
- **Validierung:** Der neue Postgres-Test ist vor der Migration rot und danach grün; CI-Rehearsal; `p7.py`.
- **Modell:** Sonnet 5.5 Medium.

### Lauf 3 – Token-/Statusprüfung
- **Scope:** TI-04 (inkl. E-Mail-Wechsel mit Re-Authentifizierung), TI-25.
- **Änderung:** Pro geschütztem Request DB-Lookup mit kurzem Cache (oder `token_version`), Bestätigungsfluss für E-Mail-Wechsel, Invariantenprüfung im Admin-PATCH; Spec `auth-accounts.md` aktualisieren.
- **Validierung:** `t_revocation.py`, `p4.py`, `p22.py`, `p15.py`; Browser-Pass beider Sprachen für den Account-Flow.
- **Modell:** Sonnet 5.5 High (groß, aber vollständig verstanden; die Optionen sind im Befund beschrieben).

### Lauf 4 – Konfiguration, Betrieb, Logs
- **Scope:** TI-08, TI-10, TI-11, TI-13, TI-14, TI-15, TI-23.
- **Änderung:** Eine Env-Auflösung und Secret-Mindestlänge, Limiter-Strategie und lokalisierter 429-Handler, Redis-Entscheidung und echter `/ready`-Check, Access-Log-Format und Log-Rotation, Dev-Bindings an Loopback, `markdown-it-py` in `requirements.in`.
- **Validierung:** `test_runtime_config.py` erweitert, `t_login_throttle.py`, `t_audio_429.py`, Test mit abgeschaltetem Redis, frische Lock-Kompilation.
- **Modell:** Sonnet 5.5 Medium.

### Lauf 5 – Testsuite: Invarianten statt Mengen
- **Scope:** TI-16, TI-17, TI-19 (nur die P0/P1-Invarianten aus Abschnitt 4), TI-36.
- **Änderung:** (1) Routen-Matrix über `create_app("testing")`, (2) Negativ-Allowlist für HTML/`data-*`/JSON, (3) Set-Isolation für alle Verben inkl. Gruppenaccount, (4) ein Playwright-Smoke in CI, (5) Registry-/i18n-Paritätstest, (6) Golden-`metadata.json`. Keine Massen-Tests.
- **Validierung:** Mutationen M13, M14, M17, M20, M21/M22, M24, M15, M16 werden rot; die Suite ist unter Windows und Linux grün.
- **Modell:** Sonnet 5.5 High.

### Lauf 6 – Mobile-UI (separat wegen Browser-Pass-Pflicht)
- **Scope:** TI-20, TI-34 (Labels, Meta-Description).
- **Validierung:** Screenshots 390 px und 1280 px in de und en auf den realen Routen, inklusive einer unberührten Seite derselben Komponentenfamilie.
- **Modell:** Sonnet 5.5 Medium.

### Lauf 7 – Mechanische Hygiene (nachrangig)
- **Scope:** TI-29, TI-30, TI-32, TI-33, TI-37 und die LOW-Punkte ohne Entscheidungsbedarf.
- **Änderung:** `.gitattributes`, `.dockerignore`, `USER`, ungenutzte Pakete und tote Statics entfernen, `git gc`, Ignore-Einträge, Workflow-Input über `env:`.
- **Validierung:** `ci_image_smoke.py`, vulture, `git ls-files --eol`, Browser-Pass für entfernte Assets.
- **Modell:** Sonnet 5.5 Low.

Entscheidungen, die vor den Läufen beim Operator liegen und nicht aus dem Repo ableitbar sind: Fail-open des Limiters bei Redis-Ausfall (TI-10); Beibehaltung von Legacy-Routen `/datenschutz` und `/auth/konto` (TI-31); Redaktionsregel für Notizfelder und Pseudonymisierung der Aufnehmenden (TI-27); Quelle der Wahrheit für den Ort der Teaching-Medien (`AGENTS.md` nennt `public/teaching/…`, Spec und Code liefern aus `content/teaching/…`).

---

## 8. Nicht prüfbar (UNKNOWN) und Grenzen

| Punkt | Warum relevant | Wie klären (Operator) |
|---|---|---|
| nginx: Überschreiben von `Host`, `X-Forwarded-For` (anhängen), `X-Forwarded-Host/-Prefix`; `client_max_body_size`; `proxy_cache`; Access-Log-Format; Normalisierung von `..`; ob `/ready` extern erreichbar bleibt (live: ja) | TI-08, TI-13, TI-21, TI-23, TI-28 | `nginx -T` auf dem Server |
| Echte Produktions-Env (`JWT_SECRET_KEY` Länge, Mail-Adressen, `POSTGRES_PASSWORD` nicht Platzhalter) | TI-11, TI-06 | Länge prüfen, nicht ausgeben |
| Tatsächlicher Postgres-Constraint `ck_access_requests_status` | TI-06 | `\d+ access_requests` |
| Existenz des Backup-Cron auf dem Server, Branch-Protection auf `main` | TI-01, TI-12 | `crontab -l`, GitHub-Einstellungen |
| Firewall der Dev-Workstation | TI-14 | `netstat -an`, Firewall-Regeln |
| Postgres im E2E-Lauf (Docker war aus), echter SMTP mit TLS, Reset-Link-Folgeaufruf, gunicorn/HTTPS/Redis, Browser außer Chromium, Audioqualität | Grenzen der lokalen Prüfung | Staging oder Operator-Gegenprobe |
| Produktions-Login-Flows und authentifizierte Seiten | Kein Login gegen Produktion durchgeführt; Aussagen zu Produktion beruhen auf unauthentifizierten GETs und dem Code von `origin/main` | – |

Methodische Hinweise: Die Teilaudits liefen parallel; Widersprüche wurden aufgelöst (der Hygiene-Teilbericht nannte den `_profile`-Hook „entfernt“, der Testteil hielt Open-Redirect-Varianten für harmlos; beides wurde per Code-Lesen und Reproduktion korrigiert). Mutationsproben sind Stichproben: „grün“ heißt, diese konkrete Mutation überlebt. Alle temporären Artefakte (Scratch-Runtimes mit Datenkopien, SQLite-DBs, Scratch-venvs, Worktree) liegen außerhalb des Repos und wurden bzw. werden entfernt; im Repo wurde weder Produkt- noch Spec-Code geändert.
