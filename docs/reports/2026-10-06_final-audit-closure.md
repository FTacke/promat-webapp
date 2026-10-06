# Final Audit Closure – Technische Audit-Serie 2026-10-06

Datum: 2026-10-06. Nicht-normativ; aktive Regeln stehen in `docs/spec/`. Run-Journal: `docs/agent-runs/2026-10-06_final-technical-closure.md`. Grundlage: `docs/audits/promat_technical_integrity_audit_2026-10-06.md` (TI-xx), `docs/audits/promat_data_ux_publication_audit_2026-10-06.md` (übrige Präfixe) und die Berichte von Run 1–4.

**Endstatus: `AUDIT_SERIES_CLOSED_WITH_POLICY_DECISIONS`** – es gibt keinen technisch notwendigen Reparaturpunkt mehr. Offen sind Policy-, Content- und Editorial-Entscheidungen sowie zwei Operator-Schritte.

Alle Statusangaben wurden in diesem Run gegen den Code von `HEAD` (`17cb7d0`, danach `40d37f5`) geprüft, nicht aus alten Berichten übernommen. Spalte „Production verifiziert“: `ja` = auf `https://pronunciation-matters.de` in einem Run beobachtet (nur lesend, anonym), `Test/Browser` = nur lokal, im Linux-Container oder im CI-Browser-Smoke belegt (kein Produktionskonto), `–` = nicht beobachtbar.

## Executive Closure Summary

| Frage | Antwort |
|---|---|
| Production Blocker? | **Nein.** Der einzige P0-Befund (TI-01, Legal-Seiten 500) ist seit Run 1.5 behoben und live verifiziert. |
| Security Blocker? | **Nein.** Alle P1-Sicherheitsbefunde sind geschlossen und deployed; offen sind nur nachrangige Härtungen (siehe „Bewusst deferiert“). |
| Privacy Blocker? | **Nein.** ID3-Tags bereinigt (0 Verstöße, Production-Scan), Client-Payloads ohne interne Felder, Reset-Token nicht in Logs. Offene Punkte sind Redaktions-/Policy-Entscheidungen. |
| Publication Blocker? | **Nein.** Offen sind Lizenz/Rechteinhaber, Korpusversion/Datenstand, Teaching-Verantwortliche (Registry-Werte, keine Technik). |
| Data Integrity Blocker? | **Nein.** Orphan-Prüfung, Vokabular-Konsistenztest und Katalog-Drift-Test schützen die Mehrfachpflege; vier unreferenzierte Teaching-Medien warten auf eine Content-Entscheidung. |
| Nur Policy/Content/Editorial | Lizenz/Rechteinhaber (Text, Audio, Forschungsdaten, Metadaten); Korpusversion/`data_as_of`; Teaching-Verantwortliche FR/DE/EN und Bestätigung ES; ORCID/Affiliationen; Sichtbarkeit `person_notes`/`session_notes`; Darstellung `recorded_by`; Gruppenkonto-Zurechenbarkeit; E-Mail-Double-Opt-in; Aufbewahrungsfrist und Text zu IP/User-Agent der Zugangsanfragen; Drittanbieter-Hinweise im Datenschutztext (CONTENT-03); `[wl_032-]` in ES-L-0014; Französischer Katalog (DATA-06); vier unreferenzierte Teaching-Medien; Legacy-Routen. |
| Extern/Operator | nginx-Kompression für CSS/JS (Runbook `deploy-and-rollback.md`, Punkt 14); Branch Protection `main` (UI). |
| Bewusst als nicht lohnend deferiert | siehe Abschnitt am Ende. |

## 1. Security / Production

| ID / Thema | Schweregrad | Audit | Finalstatus | Run | Production verifiziert | Restentscheidung |
|---|---|---|---|---|---|---|
| TI-01 / PUBL-01 Legal-Seiten 500, Reparatur-Set nicht auf `main` | HIGH | TI | `CLOSED_AND_DEPLOYED` | 1.5 | ja (5 URLs 200) | – |
| TI-02 Profiling-Hook `?_profile=1` | HIGH | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja | – |
| TI-03 Open Redirect | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja (anonym) | – |
| TI-05 Cache-Control geschützter Antworten | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | `/login` ja; geschützt Test/Browser | – |
| TI-06 Zugangsanfrage: Status-Constraint, 500, Token | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja (Constraint) | – |
| TI-07 GoatCounter auf geschützten Seiten | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja (öffentlich) | – |
| TI-08 Rate-Limit-UX, Login-Zählung, Audio-Budget | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 3 | Test/Browser | – |
| TI-09 Set-API-Robustheit | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | Test | – |
| TI-10 Redis-Ausfall legt Seiten lahm | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 / 3 | ja (`/ready` mit Redis-Check) | – |
| TI-11 Config fail-open | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja (Start mit Prüfung) | – |
| TI-12 Backup vor Migration, `--reset` | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja (Deploy-Backup, Cron) | – |
| TI-13 Reset-Token im Log | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja (nginx-Log ohne Query, Test mit Harmlos-Wert) | – |
| TI-14 Dev-DB/Dev-Server auf allen Interfaces | MEDIUM (bedingt) | TI | `CLOSED` (Bindung); Dev-Zugangsdaten in `dev-start.ps1`: `INTENTIONALLY_DEFERRED` | Final | – (nur Dev) | – |
| TI-15 `markdown-it-py` nur transitiv | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja (Image läuft) | – |
| TI-21 Teaching-Media-Route Traversal | LOW | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | Test (nicht geprobt) | – |
| TI-23 `/ready` Informationsleck | LOW | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja | – |
| TI-26 Logout per GET, CSRF | LOW | TI | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja (GET ⇒ 405) | Login-CSRF bleibt SameSite-Cookie-gestützt |
| TI-22 Login-Timing, Lockout-Missbrauch, SMTP synchron | LOW | TI | `CLOSED` (Timing: Dummy-Verifikation bei unbekanntem Namen); Lockout-Reihenfolge und asynchroner Mailversand `INTENTIONALLY_DEFERRED` | Final | Test | – |
| TI-24 Zugangsanfrage: roher `X-Forwarded-For` | LOW | TI | `CLOSED` (Code: `remote_addr`); Aufbewahrungsfrist, Cleanup und Datenschutztext `POLICY_DECISION_REQUIRED` | Final | Test | Frist und Wortlaut |
| TI-28 `ProxyFix` ohne `TRUSTED_HOSTS` | LOW | TI | `INTENTIONALLY_DEFERRED` | – | – | – |
| TI-29 Container als root, `.dockerignore`, Pins, Header | LOW | TI | `INTENTIONALLY_DEFERRED` | – | – | – |
| TI-33 Workflow: Input in `run:`, Pins, `environment:` | LOW | TI | `CLOSED` (Input über `env:`); SHA-Pins/`environment:`: `INTENTIONALLY_DEFERRED`; Branch Protection: `BLOCKED_EXTERNAL` | Final | – | Branch Protection (UI) |
| TI-37 passlib/bcrypt-Pin | LOW | TI | `CLOSED` (`bcrypt<5` mit Begründung) | Final | – | – |

## 2. Auth / Privacy

| ID / Thema | Schweregrad | Audit | Finalstatus | Run | Production verifiziert | Restentscheidung |
|---|---|---|---|---|---|---|
| TI-04 Token überlebt Statuswechsel | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 2 | Test/Browser | – |
| Logout widerruft Token serverseitig | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 2 | ja (Tabelle `revoked_tokens`) | – |
| E-Mail-Wechsel ohne Re-Authentifizierung | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 2 | Test/Browser | Double-Opt-in: `POLICY_DECISION_REQUIRED` |
| TI-25 Admin-Invarianten | LOW | TI | `CLOSED_AND_DEPLOYED` | 2 | Test | – |
| DATA-01 ID3-Tags mit mutmaßlichen Namen | HIGH | DUP | `CLOSED_AND_DEPLOYED` | 2 | ja (Scan 0 von 8324) | – |
| TI-27 interne IDs in Client-Payloads | LOW | TI | `CLOSED_AND_DEPLOYED` | 2 | Test | – |
| TI-27 `person_notes`, `session_notes` | LOW | TI | `EDITORIAL_DECISION_REQUIRED` | 2 | – | Sichtbarkeit für Research-Konten |
| TI-27 `recorded_by` | LOW | TI | `EDITORIAL_DECISION_REQUIRED` | 2 | – | Klarname oder Pseudonym |
| TI-27 Zurechenbarkeit bei Gruppenkonten | LOW | TI | `POLICY_DECISION_REQUIRED` | 2 | – | Protokollierung ja/nein |
| TI-24 Aufbewahrung Zugangsanfragen | LOW | TI | `POLICY_DECISION_REQUIRED` | Final | – | Frist, Text |
| CONTENT-03 Drittanbieter-Einbindungen und Analytics-Cookie im Datenschutztext | MEDIUM | DUP | `POLICY_DECISION_REQUIRED` (juristisch) | – | – | Wortlaut, Einwilligungsschicht |

## 3. Research Data

| ID / Thema | Schweregrad | Audit | Finalstatus | Run | Production verifiziert | Restentscheidung |
|---|---|---|---|---|---|---|
| DATA-03 142 Itemtexte der Design-Seite doppelt | MEDIUM | DUP | `CLOSED` als Drift-Schutz (Test `data`, 142/142 identisch, schlägt bei Abweichung an); Laufzeitauflösung `INTENTIONALLY_DEFERRED` | Final | – | – |
| DATA-05 Korpus-/Task-/Sprachcode-Mehrfachlisten | MEDIUM | DUP | `CLOSED` (Konsistenztest über 7 Projektionen; `TRACKED_CORPORA` und Admin-Tabelle nutzen `ACTIVE_RESEARCH_CORPORA`) | 4 / Final | Test | – |
| DATA-02 Kataloge nicht in Git und CI | MEDIUM | DUP | `INTENTIONALLY_DEFERRED` (Spec: operator-eigen, unversioniert; CI nutzt Fixture-Runtime) | – | – | – |
| DATA-04 Session-Metadaten doppelt, DB-Spiegel ohne Leser | MEDIUM | DUP | `INTENTIONALLY_DEFERRED` | – | – | – |
| DATA-06 Französischer Katalog (Apostroph, Tippfehler) | MEDIUM | DUP | `EDITORIAL_DECISION_REQUIRED` | – | – | Katalogtext |
| DATA-07 11 Sessions nur mit `metadata.json` | MEDIUM | DUP | `CONTENT_DECISION_REQUIRED` | – | – | Datenhalter |
| DATA-08 Herkunftsländer nicht lokalisiert | LOW | DUP | `INTENTIONALLY_DEFERRED` (Freitextwerte brauchen eine Content-Entscheidung) | – | – | – |
| DATA-09 Alignment-Auffälligkeiten | LOW | DUP | `INTENTIONALLY_DEFERRED`; ZWSP in ES-L-0014: `EDITORIAL_DECISION_REQUIRED` | – | – | – |
| TI-34 `[wl_032-]` Rohcode in ES-L-0014 | LOW | TI | `EDITORIAL_DECISION_REQUIRED` | 3 | – | Korpusinhalt |
| German-Korpus geschützte Platzhalter | MEDIUM | DUP/Run 4 | `CLOSED` (schlichter „In Vorbereitung“-Zustand, kein Entwicklertext; Spec bestätigt leere Zustände) | Final | Test/Browser (DE+EN, 1280/390) | – |

## 4. UX / Accessibility

| ID / Thema | Schweregrad | Audit | Finalstatus | Run | Production verifiziert | Restentscheidung |
|---|---|---|---|---|---|---|
| UX-01 Comparison ändert das Set implizit | HIGH | DUP | `CLOSED_AND_DEPLOYED` | 3 | Test/Browser | – |
| UX-02 / UX-03 / UX-04 / ACCESSIBILITY-08 Kontraste | HIGH/MEDIUM | DUP | `CLOSED_AND_DEPLOYED` (axe 0 auf 44 Kombinationen) | 3 | Test/Browser | `label-content-name-mismatch` nur stichprobenartig |
| TI-20 / RESPONSIVE-01 Mobile-Überläufe | MEDIUM | TI/DUP | `CLOSED_AND_DEPLOYED` | 3 | Browser | – |
| ACCESSIBILITY-01…07, -09 | MEDIUM/LOW | DUP | `CLOSED_AND_DEPLOYED` (Fokus, IDs, Namen, Live-Regions, `lang`, Select) | 3 | Browser | Skip-Link: `INTENTIONALLY_DEFERRED` |
| ACCESSIBILITY-04 Snackbar mit deutschem „Schließen“ | LOW | DUP | `INTENTIONALLY_DEFERRED` | – | – | – |
| UX-05 undefinierte CSS-Variablen | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` (`--book-danger`); übrige Namen nicht systematisch geprüft: `INTENTIONALLY_DEFERRED` | 3 | – | – |
| UX-06 Themenumschaltung | LOW | DUP | `NO_LONGER_APPLICABLE` (`theme.js` kennt `auto`) | – | – | – |
| UX-07 Sprechergruppen-Chip verwirft Filter | LOW | DUP | `POLICY_DECISION_REQUIRED` (Produktentscheidung) | – | – | – |
| UX-08, UX-09 Player-Navigation, Hervorhebung | LOW | DUP | `INTENTIONALLY_DEFERRED` | – | – | – |
| AUDIO-03 Fehler-/Ladezustände | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` (Stall-/Netzwerkpfade nur im Code) | 3 | Browser (Stub) | – |
| AUDIO-01 Clip-Ende nur per `timeupdate` | MEDIUM | DUP | `INTENTIONALLY_DEFERRED` (Browser- und Geräteprüfung nötig) | – | – | – |
| AUDIO-02 `play()` nach asynchroner Arbeit (iOS) | MEDIUM | DUP | `INTENTIONALLY_DEFERRED` (nur auf echtem iOS-Gerät prüfbar) | – | – | – |
| AUDIO-04, -05, -06, PERF-06 | LOW | DUP | `INTENTIONALLY_DEFERRED` | – | – | – |
| CONTENT-05 Entwicklersprache im UI | MEDIUM | DUP | `CLOSED` (Player-Hinweise und Platzhalter umformuliert, DE+EN) | Final | Test | – |
| TI-34 „curated/custom/Draft“ in der DE-UI | LOW | TI | `CLOSED_AND_DEPLOYED` | 3 | Test | – |

## 5. Performance

| ID / Thema | Schweregrad | Audit | Finalstatus | Run | Production verifiziert | Restentscheidung |
|---|---|---|---|---|---|---|
| PERF-01 5-MB-Icon-Font | HIGH | DUP | `CLOSED_AND_DEPLOYED` (10,9 KB) | 3 | ja | – |
| PERF-02 Static-Caching/Fingerprinting | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` (App-Header `immutable`) | 3 | ja | – |
| PERF-02 Kompression CSS/JS | MEDIUM | DUP | `BLOCKED_EXTERNAL` (nginx, Operator) | 3 | ja (nicht komprimiert) | nginx-Änderung |
| PERF-03 Landing-Bilder | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` (8,6 MB ⇒ 1,5 MB) | 3 | ja | – |
| PERF-05 Comparison-Katalog ohne Cache | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` | 3 | Test | – |
| PERF-07 totes Gewicht (htmx, jQuery, `/auth/session`) | LOW | DUP | `CLOSED_AND_DEPLOYED` | 3 | ja (kein htmx) | – |
| PERF-04 unsubsettete Webfonts | MEDIUM | DUP | `INTENTIONALLY_DEFERRED` (420 KB größte Datei; kein reproduzierbarer Nutzen belegt) | – | – | – |

## 6. Regression / Tests

| ID / Thema | Schweregrad | Audit | Finalstatus | Run | Production verifiziert | Restentscheidung |
|---|---|---|---|---|---|---|
| TI-16 Frontend-Verhalten ungeschützt | MEDIUM | TI | `CLOSED_AND_DEPLOYED` (CI-Job `browser-smoke`, jetzt 228 Prüfungen) | 3 / Final | CI | – |
| TI-17 Komposition, Routenmatrix, Payloads | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 2 / 3 | CI | – |
| TI-18 SQLite statt Postgres | MEDIUM | TI | `CLOSED_AND_DEPLOYED` | 1 | CI | – |
| TI-19 Realdaten-Drift | MEDIUM | TI | `CLOSED` (Parität i18n/Registry, Konsistenz- und Katalog-Drift-Test); `validate_research_config.py` in CI: `INTENTIONALLY_DEFERRED` (Kataloge nicht im Repo) | 3 / Final | CI | – |
| TI-36 Tests mit geringem Informationswert | LOW | TI | `INTENTIONALLY_DEFERRED` | – | – | – |
| TI-30 ungenutzte Pakete, toter Code | LOW | TI | `INTENTIONALLY_DEFERRED` (JS/Bilder in Run 3 geschlossen; Pakete: nur Imagegröße) | – | – | – |
| TI-31 doppelte Implementierungen | LOW | TI | `CLOSED` für `_safe_next` (Run 1) und Korpus-Registries (Konsistenztest); `_build_access_request_href` `INTENTIONALLY_DEFERRED` | 1 / Final | – | – |
| TI-32 Repo-Hygiene | LOW | TI | `CLOSED` (`.gitattributes` für `*.sh`, `pool_pre_ping`); `console.log`, `.claude/settings.json`, `tmp_obj`: `INTENTIONALLY_DEFERRED` | Final | – | `.claude/settings.json` ist Sache der Maintainer |
| TI-35 Konsistenzabweichungen | LOW | TI | teils `CLOSED` (Drafts, 404); Rest `INTENTIONALLY_DEFERRED` | 3 / 4 | – | – |

## 7. Publication / Metadata

| ID / Thema | Schweregrad | Audit | Finalstatus | Run | Production verifiziert | Restentscheidung |
|---|---|---|---|---|---|---|
| METADATA-01 Client-JS überschreibt `document.title` | HIGH | DUP | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja (Server-Titel) | – |
| CITE-01 Zitat-URL auf Domain-Wurzel | HIGH | DUP | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja | – |
| CONTENT-01 unfertige Teaching-Themen öffentlich | HIGH | DUP | `CLOSED_AND_DEPLOYED` | 1 / 1.5 | ja (302 bzw. ab Run 4 404) | – |
| PUBL-02 Autor:innenschaft doppelt | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` | 4 | ja | Verantwortliche FR/DE/EN: `CONTENT_DECISION_REQUIRED` |
| PUBL-03 Lizenz/Rechteinhaber | MEDIUM | DUP | `POLICY_DECISION_REQUIRED` | 4 | – | Lizenz je Ressourcenart |
| PUBL-04 Version/Datenstand | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` (Infrastruktur) | 4 | ja | Wert: `CONTENT_DECISION_REQUIRED` |
| PUBL-05 Identität am Slug, 302 statt 404 | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` | 4 | ja (404) | – |
| METADATA-02 / -03 / -04 canonical, hreflang, JSON-LD, Description | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` | 4 | ja (13 Seiten) | – |
| CITE-02 / CITE-03 generierte Zitate, vier Ebenen | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` | 4 | ja | – |
| CONTENT-02 Platzhalter-`design` | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` | 4 | ja | – |
| CONTENT-04 Legacy-Stubs sichtbar | MEDIUM | DUP | `CLOSED_AND_DEPLOYED` (Verfügbarkeitsregel Run 1); Abschnittsreihenfolge `r-am-silbenende` `EDITORIAL_DECISION_REQUIRED` | 1 | ja | – |
| CONTENT-06 Hub-Titelmuster, Reihenfolgen | LOW | DUP | `EDITORIAL_DECISION_REQUIRED` | – | – | – |
| ORCID / Affiliationen | – | – | `POLICY_DECISION_REQUIRED` | 4 | – | Personenangaben |

## 8. Data / Content Integrity

| ID / Thema | Schweregrad | Audit | Finalstatus | Run | Production verifiziert | Restentscheidung |
|---|---|---|---|---|---|---|
| DATA-11 Teaching-Validator zu schwach | LOW | DUP | `CLOSED` (Front Matter in Run 4; verwaiste Medien im Final-Run: Fehler für unbekannte Orphans, dokumentierte Ausnahmeliste, Stale-Prüfung, 7 Regressionstests) | 4 / Final | CI | – |
| Vier unreferenzierte Teaching-Medien (`seseo-casa-caza.mp3`, `seseo-word-series.mp3`, `seseo-america.svg`, `seseo-distincion-spain.svg`) | LOW | DUP | `CONTENT_DECISION_REQUIRED` (in `content/teaching/media-exceptions.yaml` dokumentiert; die beiden MP3 sind andere Aufnahmen als die verwendeten und werden von der Media-Route weiterhin öffentlich ausgeliefert) | Final | – | einbinden oder entfernen, ggf. Einwilligung der ersetzten Aufnahme prüfen |
| DATA-10 tote/Legacy-Pfade | LOW | DUP | Logout-GET geschlossen (Run 1); `/datenschutz`, `/auth/change-password`, `example.invalid`, `ensure_curated_test_set`: `INTENTIONALLY_DEFERRED`, Entfernen öffentlicher Legacy-Routen `POLICY_DECISION_REQUIRED` | – | – | Legacy-Routen |

## 9. External / Policy / Editorial

| Thema | Finalstatus | Restentscheidung |
|---|---|---|
| Branch Protection `main` (`protected: false`) | `BLOCKED_EXTERNAL` | UI-Schritte im Run-1.5-Bericht |
| nginx-Kompression CSS/JS/JSON/SVG | `BLOCKED_EXTERNAL` | Operator-Schritt, Runbook Punkt 14 |
| QA-Konto für authentifizierte Production-Smokes | `BLOCKED_EXTERNAL` | Operator stellt ein Konto bereit |
| Lizenz/Rechteinhaber, Metadatenlizenz, Korpusversion, ORCID | `POLICY_DECISION_REQUIRED` / `CONTENT_DECISION_REQUIRED` | siehe Run-4-Bericht, „Policy Handoff“ |
| `person_notes`, `session_notes`, `recorded_by`, Gruppenkonto-Zurechenbarkeit, E-Mail-Double-Opt-in | `EDITORIAL_DECISION_REQUIRED` / `POLICY_DECISION_REQUIRED` | siehe Run-2-Bericht |

## Bewusst deferiert („nicht lohnend“)

Jeweils mit Begründung; keiner ist ein Blocker.

- **DATA-03 Laufzeitauflösung der Design-Itemtexte:** Die Kataloge sind operator-eigene, unversionierte Laufzeitkonfiguration (Spec). Eine Auflösung zur Laufzeit würde die öffentliche, zitierbare Designseite von `data/` abhängig machen und in CI und Image-Smoke (ohne Kataloge) entweder brechen oder eine zweite Quelle als Fallback erzwingen. Stattdessen verhindert der Drift-Test Abweichungen. Er läuft nur dort, wo die Kataloge vorliegen (Marker `data`, nicht in CI).
- **TI-22 Lockout-Reihenfolge:** Würde ein gesperrtes Konto für jedes Passwort als „gesperrt“ melden und damit Konten aufdecken; Abwägung statt mechanischer Fix. Asynchroner Mailversand: eigener Zuverlässigkeits-Workstream.
- **TI-28 `TRUSTED_HOSTS`:** Eine falsche Hostliste würde Produktion mit 400 beantworten; setzt eine geprüfte nginx-Konfiguration voraus (Operator).
- **TI-29 Container-Nutzer, Image-Pins:** Nicht-root verlangt die Prüfung der Schreibrechte auf den Produktions-Volumes; Risiko höher als der Nutzen bei Loopback-Bindung und Host-Härtung.
- **TI-30, TI-36, TI-32 (Rest), TI-31 (Rest):** Imagegröße und Code-Hygiene ohne Sicherheits- oder Integritätswirkung.
- **TI-14 Dev-Zugangsdaten in `dev-start.ps1`:** Nur lokale Entwicklung; Datenbank und Server hören jetzt nur auf Loopback.
- **AUDIO-01, -02, -04…06, PERF-04, PERF-06, UX-08/09, ACCESSIBILITY-04/-09 (Skip-Link):** Brauchen Geräte-/Browserprüfung oder sind Feinschliff ohne belegten Schaden.
- **DATA-02, TI-19 (`validate_research_config.py` in CI):** Kataloge liegen nach Spec nicht im Repo.

## Tests und Deploy dieses Runs

| Prüfung | Ergebnis |
|---|---|
| `pytest` lokal (Windows, ohne Postgres) | 1238 passed, 2 skipped, 9 deselected |
| `pytest` im Linux-Container mit Postgres 15 | 1244 passed, 2 skipped, 9 deselected |
| neu | 31 Tests: Vokabular-Konsistenz 7, Katalog-Drift 2 (`data`, nicht in der Standardsuite), Orphans 7, Deutsch leer 8, Härtung 7; dazu 48 Browser-Smoke-Prüfungen |
| JS / ruff / compileall / Governance / Teaching-Validator | 64/64 / grün / grün / grün / grün (4 Warnungen für die dokumentierten Orphans) |
| CI-Browser-Smoke lokal | 228 Prüfungen, 0 Fehler (Run 4: 180; neu: deutsche Seiten DE+EN bei 1280/390 px) |
| Mutation | Katalog-Drift-Test rot bei verändertem Itemtext |
| Commit | `40d37f5` auf `main` |

## Projektzustand nach der Audit-Serie

| Bereich | Zustand |
|---|---|
| Production | Läuft auf dem Stand der Run-4-/Closure-Commits; Legal-Seiten, Metadaten, Zitate, Cache-Header, 404-Verhalten live verifiziert; tägliches DB-Backup mit Cron, Deploy-Backup vor jeder Migration |
| CI | `release-gate` mit Python (Postgres-Service), JS, Docker-Image-Smoke, Backup/Restore-Rehearsal und `browser-smoke`; Deploy nur per `workflow_run` nach grünem CI |
| Security | Alle P0/P1-Befunde geschlossen und deployed; offen nur nachrangige Härtungen (siehe deferiert) |
| Privacy | MP3-Tags bereinigt und per Validator abgesichert; keine internen IDs im Client; Tokens nicht in Logs; offene Punkte sind Redaktionsentscheidungen |
| Datenintegrität | Konsistenztests für Korpus-/Task-/Sprachcode-Mengen, Katalog-Drift-Test, Orphan-Prüfung der Teaching-Medien, Registry-Validierung |
| UX / A11y | axe 0 Verstöße und 0 Überläufe auf den geprüften Kombinationen; Screenreader-Tests mit echter Hilfstechnik wurden nicht durchgeführt |
| Performance | Landing 8,6 MB ⇒ 1,5 MB; offen nur nginx-Kompression (Operator) und Webfont-Subsetting |
| Publication Metadata | Registry, canonical, hreflang, JSON-LD, generierte Zitate; DOI-fähig, kein DOI vergeben |
| Regression Protection | 1244 Tests im Linux-Lauf, 64 JS-Tests, 228 Browser-Smoke-Prüfungen, Mutationsproben für die kritischen Pfade |

### Noch offene Entscheidungen

Siehe „Executive Closure Summary“ (Zeile „Nur Policy/Content/Editorial“) und Abschnitt 9; keine davon erzeugt eine technische Aufgabe.

### Empfohlene nächste technische Arbeit

> Keine weitere Audit-/Repair-Welle empfohlen.

Neue Produktentwicklung, German Intake, neue Teaching-Inhalte und die Umsetzung der Policy-Entscheidungen sind eigene Vorhaben außerhalb dieser Serie.

## Production

- Code-Commit `40d37f5`: CI (`release-gate` mit allen fünf Jobs) und `Deploy production` grün; `scripts/post_deploy_smoke.py` gegen `https://pronunciation-matters.de` grün. Live read-only: `/ready` 200, `/de/research/german/design` 200, Themenseite 200, geschützte deutsche Seiten leiten anonym auf den Login (302). Die geänderten geschützten Seiten (deutscher „In Vorbereitung“-Zustand, Login-Dummy-Verifikation) sind ohne Produktionskonto nur lokal, im Linux-Container und im CI-Browser-Smoke belegt.
- Die vier unreferenzierten Teaching-Medien werden unverändert ausgeliefert (z. B. `seseo-casa-caza.mp3` ⇒ 200); die Content-Entscheidung steht aus.
- Abschluss-Commit: Dokumentation (dieser Bericht und der Run-Eintrag) folgt als Doku-Commit ohne Code-Änderung.
