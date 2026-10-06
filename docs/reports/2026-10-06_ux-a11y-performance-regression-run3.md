# UX, Accessibility, Performance & Regression Protection – Run 3: Repair- und Validation-Bericht

Datum: 2026-10-06. Nicht-normativ; aktive Regeln in `docs/spec/`. Run-Journal: `docs/agent-runs/2026-10-06_ux-a11y-performance-regression-run3.md`.

**Endstatus: siehe Abschnitt „Production“ (wird nach Deployment ergänzt).** Messwerte stammen aus einem lokalen Lauf mit Produktionsdaten-Katalog und gedrosselter Verbindung (1,6 Mbit/s, 150 ms RTT, Cold-Cache), nicht aus Produktion.

## A. Befund-Tabelle

`CLOSED_AND_DEPLOYED` wird erst nach dem Deployment vergeben; bis dahin steht in der Spalte Production „offen bis Deploy“.

| Finding | Phase-0-Status | Änderung | Evidenz | Production | Endstatus |
|---|---|---|---|---|---|
| UX-01 Comparison: Sprecher-/Filter-/Material-Wechsel ändern das gewählte Set, Fork per `private-copy` | `STILL_OPEN` | lokaler Zustand statt Draft-Schreibzugriff; Draft/`private-copy` nur bei explizitem Anlegen oder echter Item-Änderung; Set-Select bleibt stabil; Default schreibt kein `set_id` in die URL | Browser-Smoke (DE+EN): Sprecher an/aus ändert Set nicht, kein `private-copy`, keine Schreibzugriffe, auch mit gespeichertem Set; JS-Helper-Test | Deploy | s. u. |
| TI-08 429-UX, Login-Zählung, Audio-Budget, Redis-Latenz | `STILL_OPEN` | lokalisierte 429-Seite/-JSON mit `Retry-After`; Login zählt nur Fehlversuche; Audio-Routen `3000 per hour`; Health-Monitor schaltet den Limiter bei Redis-Ausfall ab (kein In-Memory-Ersatz) | 13 Tests `test_web_performance_and_errors.py` (HTML/JSON, `Retry-After`, erfolgreiche Logins zählen nicht, Monitor-Flag); Screenshots 429 DE/EN, hell/dunkel | Deploy | s. u. |
| AUDIO-03 Fehler-/Ladezustände | `STILL_OPEN` | lokalisierte Status (Laden, Fehler, Stall, Session abgelaufen, 429) mit `aria-live` im Player und Comparison | Browser-Smoke: fehlender Clip ⇒ lokalisierte Meldung, Wiedergabe endet (DE+EN, Stub); Stall-/Netzwerkfehler-Pfade nur im Code, nicht automatisiert getestet | Deploy | s. u. |
| TI-20 Mobile-Überläufe (Player, Comparison, Phenomena/Sets, Speakers) | `STILL_OPEN` (4 von 60 Fällen) | schmale-Viewport-Regeln in `30_components.css`, Wrapping statt Überlauf | `ui_probe` 390/820/1280, DE/EN: 0 Überlauf-Fälle; Smoke prüft 8 Seiten bei 390 px | Deploy | s. u. |
| Kontrast (Primärbutton, Success-Snackbar, muted Nav, Akzenttext, native-Badge, Auswahlzustände, Teaching-Karten-Aktionen, `--book-danger`) | `STILL_OPEN` (28 von 40 Kombinationen) | Token-basiert: `--pm-accent-text-tone`, dunkles `--promat-on-primary`, `--book-danger`, `--pm-state-muted-text`, Status-Tokens | axe: 0 Verstöße auf 44 Kombinationen (DE/EN × hell/dunkel × 11 Seiten) | Deploy | s. u. |
| Fokus sichtbar und konsistent | `PARTIALLY_FIXED` | gemeinsamer `:focus-visible`-Ring (`--book-link`, 2 px) für alle interaktiven Familien | Screenshots; Fokus-Regeln im CSS und Spec; keine vollständige manuelle Tastaturprüfung | Deploy | s. u. |
| Doppelte IDs im Speakers-Filter | `STILL_OPEN` | Filter-Partial mit `id_prefix` (strukturell) | Test „IDs eindeutig“ (DE+EN) | Deploy | s. u. |
| Landmarks/Namen/Live-Regions/`lang`/`aria-current`/`aria-valuetext` | `STILL_OPEN` | `role="banner"` entfernt, Drawer `<nav>` mit Namen, eindeutige Breadcrumb-/Seitenende-Labels (lokalisiert), Matrix-Buttons mit Item/Sprecher, `lang` auf Fremdsprach-Items, `aria-valuetext` für Regler, Fokus nach Re-Render | axe 0 Verstöße; `label-content-name-mismatch` (experimentell) nur stichprobenartig | Deploy | s. u. |
| Select navigiert bei Pfeiltasten | `STILL_OPEN` | `select-commit.js` (Pfeile browsen, Enter/Blur/Zeiger commit) | 4 JS-Tests | Deploy | s. u. |
| PERF-01 5-MB-Icon-Font, unbedingtes `FontFace.load()` | `STILL_OPEN` | Subset 10,9 KB (`build_icon_font.py`), Loader und Fallback entfernt, Preload | Cold-Cache-Transfer, Tabelle C; Test „Subset enthält jedes genutzte Icon“ | Deploy | s. u. |
| PERF-02 Static-Caching/Fingerprinting/Kompression | `STILL_OPEN` | `static_asset()` überall, `immutable` für versionierte Antworten; nginx-Kompression als Operator-Anweisung | Test (Header, jede Referenz versioniert); Produktionsheader vor dem Deploy: CSS ohne `Content-Encoding`, `Cache-Control: no-cache` | Deploy / nginx offen | s. u. |
| PERF-03 Landing-Bilder | `STILL_OPEN` | 1,08 MB-PNG ⇒ JPEG mit Maßen, `decoding="async"` | Landing 8,6 MB ⇒ 1,5 MB | Deploy | s. u. |
| PERF-05 Comparison-Katalog je Request | `STILL_OPEN` | Katalog-Cache mit Kopie je Request | Messung lokal (24 Sessions): Aufbau 540–840 ms je Request ohne Cache, 0,7 ms mit Cache | Deploy | s. u. |
| PERF-07 Totes Gewicht (htmx, jQuery, `/auth/session` je Seite, ungenutzte Bilder) | `STILL_OPEN` | entfernt; `/auth/session` bleibt als Endpoint | Test „bleibt entfernt“; Browser-Smoke ohne Fehler | Deploy | s. u. |
| PERF-04 Webfonts (Inter, Source Serif) | `STILL_OPEN` | nicht verändert (kein Glyph-Inventar, kein reproduzierbarer Nutzen belegt) | größter verbleibender Transfer 420 KB | – | `DEFERRED_TO_RUN_4` (nur als Performance-Restpunkt) |
| Landing-`<title>` doppelt | `STILL_OPEN` | `format_page_title` gibt bei gleichem Label nur den App-Namen aus | Test, Smoke (`document.title` = Server-Titel) | Deploy | s. u. |
| DE-UI „curated/custom/Draft“ | `STILL_OPEN` | „kuratiert“, „eigenes Set“, „Entwurf“, „Entwurf geladen“ | i18n-Test | Deploy | s. u. |
| `[wl_032-]` in ES-L-0014 | `STILL_OPEN` | nicht verändert: Es handelt sich um Korpusinhalt, dessen Interpretation eine redaktionelle Entscheidung braucht | – | – | `EDITORIAL_DECISION_REQUIRED` |
| TI-16 Browser-/Verhaltenstests, Mutationen M13/M14/M21/M22/M24 | `STILL_OPEN` | CI-Job `browser-smoke`, JS-Syntaxtest, Fixture-Runtime | Mutationen rot (M13: 4, M14: 2, M21: 2, M24: 10 Prüfungen; M22 im JS-Helper-Test) | Deploy | s. u. |
| TI-17 Routenmatrix, Registry, i18n-Parität, Golden-Metadaten, FR/EN-Fixtures | `PARTIALLY_FIXED` (Run 2: Payload-Sentinels) | Matrix über `create_app("testing")` mit Allowlist, Parität, Varietäten-Registry, Golden-Format, FR/EN-Sessions im Browser-Smoke | 15 + 9 Tests; M20 (`@jwt_required()` entfernt) wird rot | Deploy | s. u. |
| Branch Protection `main` | `BLOCKED_EXTERNAL` | unverändert | – | – | `BLOCKED_EXTERNAL` |
| `person_notes`/`session_notes`, `recorded_by` | `EDITORIAL_DECISION_REQUIRED` | unverändert | – | – | `EDITORIAL_DECISION_REQUIRED` |
| Gruppenkonto-Zurechenbarkeit, E-Mail-Double-Opt-in | `DEFERRED_POLICY_DECISION` | unverändert | – | – | `DEFERRED_POLICY_DECISION` |

## C. Performance Summary

Cold-Cache, gedrosselt (1,6 Mbit/s, 150 ms RTT), lokal, ein Lauf je Seite (Schwankung der Ladezeiten rund ±10 %; das Teaching-Thema schwankt zusätzlich mit nachgeladenen Audiodateien); Spalten „vorher ⇒ nachher“.

| Seite | Transfer | Anfragen | Fonts | größte Datei | DCL | LCP |
|---|---|---|---|---|---|---|
| Landing | 8643 ⇒ 1498 KB | 43 ⇒ 40 | 5741 ⇒ 777 KB | 4976 ⇒ 420 KB | 6863 ⇒ 5020 ms | 4220 ⇒ 3600 ms |
| Login | 5956 ⇒ 892 KB | 42 ⇒ 39 | 5321 ⇒ 357 KB | 4976 ⇒ 345 KB | 4378 ⇒ 3859 ms | 2868 ⇒ 2692 ms |
| Teaching-Thema | 8630 ⇒ 3565 KB (2975 KB im ersten Lauf) | 106 ⇒ 100 (80) | 6590 ⇒ 1626 KB | 4976 ⇒ 420 KB | 11033 ⇒ 6953 ms | 2940 ⇒ 2824 ms |
| Research-Hub | 6381 ⇒ 1318 KB | 46 ⇒ 43 | 5741 ⇒ 777 KB | 4976 ⇒ 420 KB | 4414 ⇒ 4137 ms | 2840 ⇒ ca. 2700 ms |
| Comparison | 6543 ⇒ 1488 KB | 51 ⇒ 49 | 5741 ⇒ 777 KB | 4976 ⇒ 420 KB | 5966 ⇒ 4927 ms | 5980 ⇒ 4944 ms |
| Player | 6549 ⇒ 1493 KB | 51 ⇒ 49 | 5741 ⇒ 777 KB | 4976 ⇒ 420 KB | 6105 ⇒ 4993 ms | 3688 ⇒ 3544 ms |

- **nginx/Cache/Kompression:** Produktion vor dem Deploy: HTML wird gzip-komprimiert, `30_components.css` (257 KB) und andere Static-Dateien nicht; `Cache-Control: no-cache` auf Static. Die App sendet ab jetzt `immutable` für versionierte URLs. Die gzip-Freigabe für CSS/JS/JSON/SVG ist eine einmalige nginx-Änderung (Runbook `deploy-and-rollback.md`, Punkt 14); ich hatte keinen Zugriff auf den Proxy.
- **Verbleibende Engpässe:** Inter (345 KB) und Source Serif 4 (420 KB) als unsubgesetzte Variable-Fonts; neun render-blockierende Stylesheets, `30_components.css` mit 254 KB unkomprimiert (solange nginx CSS nicht komprimiert); LCP der Comparison (4,9 s bei 1,6 Mbit/s) liegt deutlich über den anderen Seiten (Ursache nicht untersucht).

## D. Accessibility Summary

| Messgröße | vorher | nachher |
|---|---|---|
| axe, Kombinationen mit serious/critical | 28 von 40 | 0 von 44 |
| axe, Verstöße gesamt | `color-contrast` 28, `landmark-*` 108, `aria-allowed-role` 20, `heading-order` 8 | 0 |
| Überlauf-Fälle (390/820/1280, DE/EN) | 4 von 60 | 0 von 66 |
| Fokus | uneinheitlich | gemeinsamer Ring |
| Tastatur | Pfeiltasten im Set-Select navigieren | Commit per Enter/Blur/Zeiger |

Verbleibend und begründet: `label-content-name-mismatch` ist eine experimentelle axe-Regel und nicht aktiv geprüft; Stichproben (Matrix-Buttons, Sprecherzeilen) tragen den sichtbaren Text im Namen. Screenreader-Tests mit echter Hilfstechnik wurden nicht durchgeführt.

## E. Handoff für Run 4

- Offen unverändert: Branch Protection (`BLOCKED_EXTERNAL`), `EDITORIAL_DECISION_REQUIRED` (`person_notes`/`session_notes`, `recorded_by`, `[wl_032-]` in ES-L-0014), `DEFERRED_POLICY_DECISION` (Gruppenkonto-Zurechenbarkeit, E-Mail-Double-Opt-in).
- Publikations-/Metadatenarchitektur (Meta-Description, Zitation, DOI, Lizenz) wie vorgesehen nicht angefasst.
- Neue Beobachtungen: nginx-Kompression offen (Operator); Webfont-Subsetting als mögliche Performance-Arbeit; QA-Konto für authentifizierte Production-Smokes weiterhin nicht vorhanden; M22 ist nur durch den JS-Helper-Test (nicht den Browser-Smoke) abgesichert, weil der Comparison-Default keine Server-Drafts mehr erzeugt.

## Production

Wird nach Merge, CI, Deploy und Post-Deploy-Smoke ergänzt.

## Tests

| Prüfung | Ergebnis |
|---|---|
| `pytest` (mit Postgres 15) | 1155 passed, 1 skipped (Windows/WSL-`bash -n`), 7 deselected (`data`) |
| neu in Run 3 | `test_route_security_matrix.py` 15, `test_i18n_and_registry_integrity.py` 9, `test_web_performance_and_errors.py` 13 |
| JavaScript | 64/64 (inkl. Parse-Test jedes Static-Scripts, Select-Commit) |
| ruff, compileall, Governance, Teaching-Validierung | grün |
| Docker | Image gebaut, Image-Smoke grün |
| Browser-Smoke (Chromium, Fixture-Runtime) | 110 Prüfungen, 0 Fehler |
| Mutationen | M13, M14, M21, M24, M20 rot; M22 im JS-Test rot |
