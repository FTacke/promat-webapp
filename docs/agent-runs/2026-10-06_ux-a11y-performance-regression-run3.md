# UX, Accessibility, Performance & Regression Protection – Run 3

Datum: 2026-10-06. Modell: Sonnet 5.5 High. Branch `repair/run3-ux-a11y-perf` (aus `origin/main` = `4eb2838`). Detailbericht: `docs/reports/2026-10-06_ux-a11y-performance-regression-run3.md`.

## Ziel

Funktionale UX (UX-01 Comparison-Set-Stabilität, TI-08 Rate-Limit-UX, AUDIO-03 Audio-Zustände), Accessibility (Kontrast, Fokus, Namen, IDs, Landmarks, Live-Regions), Mobile-Überläufe (TI-20), Performance der Weboberfläche (PERF-01…07) und gezielter Regressionsschutz (TI-16, TI-17). Repair-Run ohne Redesign.

## Consulted Sources

`docs/spec/platform-data-files.md`, `research-access.md`, `research-capabilities.md`, `intake-workbook.md`; Audits `promat_technical_integrity_audit_2026-10-06.md` und `promat_data_ux_publication_audit_2026-10-06.md`; Run-1/1.5/2-Einträge; Runbooks `deploy-and-rollback.md`, `test-and-ci.md`.

## Phase 0

- `main` = Production = `4eb2838` (Run 2). Run-2-Bereiche (Token-/Statuswirkung, Logout, ID3, Payload-Hygiene) nicht erneut angefasst; offene Policy-Punkte unverändert klassifiziert (Branch Protection `BLOCKED_EXTERNAL`; `person_notes`/`session_notes`, `recorded_by` `EDITORIAL_DECISION_REQUIRED`; Gruppenkonto-Zurechenbarkeit und E-Mail-Double-Opt-in `DEFERRED_POLICY_DECISION`).
- Baseline gegen den Ist-Code: TI-20 (4 Überlauf-Fälle von 60), TI-16, TI-08, UX-01, doppelter Landing-`<title>`, PERF-01…07, axe: 28 von 40 Seite/Sprache/Theme-Kombinationen mit serious/critical (Kontrast), dazu Landmark- und Heading-Befunde. Messwerte in `tmp/ui-qa/2026-10-06-run3-ux-a11y-perf/` (lokal, nicht im Repo); Zusammenfassung im Bericht.

## Wichtige Entscheidungen

- **Icon-Font:** Subset statt Voll-Font (5 MB ⇒ ca. 11 KB), reproduzierbar über `scripts/build_icon_font.py`; Achsen fest auf die im CSS genutzten Werte, nur im Quelltext als Icon geschriebene Namen. Das GSUB-Closure-Problem (Subsetter zog alle Glyphen mit passenden Buchstaben mit) ist durch Entfernen nicht benötigter Ligaturregeln vor dem Subsetten gelöst. Der unbedingte `FontFace.load()`-Loader und das Fallback-Verstecken sind entfernt, das Font-File wird per Preload geladen.
- **Static-Caching:** alle `/static`-Verweise über `static_asset()` (`?v=mtime`); Antworten mit `v` bekommen `immutable`. Kompression ist nginx-Sache; ich habe keinen Zugriff auf den Proxy (SSH wurde vom Berechtigungsprüfer verweigert) und daher nur Runbook-Anweisung und Messung der Produktionsheader geliefert (`BLOCKED_EXTERNAL`/Operator-Schritt).
- **Comparison (UX-01):** Sprecher-, Filter-, View-Task- und Materialwechsel ändern nur lokalen Zustand; Server-Draft/`private-copy` nur bei explizitem Anlegen oder echter Item-Änderung. Set-Select mit eigenem Commit-Helfer, damit Pfeiltasten nicht navigieren (WCAG 3.2.2).
- **Rate-Limit (TI-08):** lokalisierter 429 (HTML+JSON, `Retry-After`); Login zählt nur Fehlversuche (`deduct_when`); Audio-Routen mit Medienbudget `3000 per hour`; Health-Monitor-Thread schaltet den Limiter bei Redis-Ausfall ab, ohne In-Memory-Ersatz.
- **Regressionsschutz:** CI-Job `browser-smoke` (echte App-Factory, synthetische Fixture-Runtime, gestubbtes Audio) im `release-gate`; JS-Test, der jedes Static-Script parst; Routenmatrix mit expliziter Public-Allowlist; i18n-/Registry-/Golden-Metadaten-Tests.
- **Nicht entschieden/nicht gebaut:** Webfont-Subsetting (Inter/Source Serif; größter verbleibender Transfer, kein reproduzierbarer Nutzen ohne Glyph-Inventar), Meta-Description/Zitation (Run 4), `label-content-name-mismatch` (experimentelle axe-Regel, manuell stichprobenartig geprüft).

## Geänderte Bereiche

App: `__init__.py` (429-Handler, Static-Cache), `extensions/__init__.py` (Limiter, Health-Monitor), `config/__init__.py`, `routes/auth.py`, `routes/public.py`, `routes/public_content.py`, `branding.py`, `i18n.py`, `research_views.py` (Katalog-Cache, Client-State), `teaching_content.py`. Templates: `base.html`, `errors/429.html`, Landing, Comparison, Player, Speakers, Phenomena, Navigation, Content-Header, Admonition, Teaching-Blöcke, Filter-Partial. Statisch: `00_tokens.css`, `10_typography.css`, `30_components.css`, `material-symbols.css`, `typefaces.css`, `research-comparison.js`, `research-player.js`, `select-commit.js`, `auth-setup.js`, Navigation-JS; entfernt: htmx, jQuery, Font-Loader, ungenutzte Bilder. Skripte: `build_icon_font.py`, `qa/ui_probe.py`, `qa/fixture_runtime.py`, `qa/ci_browser_smoke.py`. Tests: `test_route_security_matrix.py`, `test_i18n_and_registry_integrity.py`, `test_web_performance_and_errors.py`, `static_scripts.test.mjs`, `select_commit.test.mjs`, Anpassungen in `test_auth_phase1.py`, `test_research_sessions.py`, `test_research_comparison.py`, `test_ci_workflows.py`. CI: `ci.yml` (Job `browser-smoke`, `fonttools` für den Icon-Font-Test). Specs/Runbooks: `platform-data-files.md`, `test-and-ci.md`, `deploy-and-rollback.md`.

## Verifikation

- `pytest` mit Postgres 15: 1155 passed, 1 skipped (Windows/WSL), 7 deselected. JS: 64/64. ruff, compileall, Governance, Teaching-Validierung grün. Docker-Image gebaut, Image-Smoke grün.
- Browser-Smoke lokal: 110 Prüfungen, 0 Fehler. Mutationen rot: M13, M14 (Stop-Logik/-Icon), M21 („Alle Items“ nie aktuell), M24 (Syntaxfehler im Player-JS), M22 (Set-ID-Exposition, im JS-Helper-Test), M20 (`@jwt_required()` entfernt, Routenmatrix).
- axe: 0 Verstöße (alle Impact-Stufen) auf allen 44 Kombinationen; Überlauf 0 von 66 Fällen (390/820/1280, DE/EN).
- Screenshot-Matrix (DE/EN × Light/Dark × 390/820/1280) für Landing, Research-Hub, Speakers, Comparison, Player, Phenomena (Übersicht und Set), Teaching-Hub, Teaching-Thema, Login, Access-Request, plus 429-Seite; stichprobenartig gesichtet (Comparison und Player mobil, Phänomene-Set, Research-Hub, Teaching-Hub dunkel, 429).

## Abweichungen

Keine von den Specs; die Spec-Aussage zu Google Fonts war veraltet (Fonts sind selbst gehostet, CSP `font-src 'self'`) und wurde korrigiert.
