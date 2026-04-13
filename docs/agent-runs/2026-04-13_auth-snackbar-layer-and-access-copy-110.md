# Auth Snackbar Layer And Access Copy 110

Datum: 2026-04-13

## Ziel

Kleiner Follow-up-Run im Auth-Bereich: Snackbar- und Toast-Meldungen auch bei offenem Dialog und Blur-Backdrop zuverlässig in den Vordergrund holen, den Standardabstand zwischen Icon und Text in der PROMAT-Inline-Action-Familie korrigieren und die gewünschte Access-Request-Copy in Oberfläche und `mailto` aktualisieren.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/runbooks/ui-change-workflow.md`
- Relevante Implementierung in `app/static/js/modules/core/snackbar.js`, `app/static/js/modules/auth/snackbar.js`, `app/static/js/auth/admin_users.js`, `app/static/css/30_components.css`, `app/static/css/md3/components/snackbar.css`, `app/src/app/i18n.py`, `app/tests/test_auth_phase1.py`

## Geänderte Bereiche

- Snackbar-/Toast-Hostlogik unter `app/static/js/modules/core/snackbar.js`, `app/static/js/modules/auth/snackbar.js` und `app/static/js/auth/admin_users.js`
- Shared CTA-/Inline-Action-Abstand unter `app/static/css/30_components.css`
- Globales Snackbar-Layering unter `app/static/css/md3/components/snackbar.css` und `app/static/css/30_components.css`
- Access-Request-Copy unter `app/src/app/i18n.py`
- Fokussierte Auth-Regressionen unter `app/tests/test_auth_phase1.py`

## Wichtige Entscheidungen

- Der Fix wurde nicht nur als höherer `z-index` umgesetzt. Snackbar und Toast werden jetzt an den zuletzt offenen `dialog[open]` angehängt, damit sie im echten Dialog-Top-Layer über dem Blur-Backdrop bleiben.
- Zusätzlich wurde der numerische Layer für globale Snackbars und den Admin-Toast angehoben, damit auch außerhalb offener Dialoge keine konkurrierenden Overlay-Layer dazwischenliegen.
- Der Icon/Text-Abstand wurde auf der gemeinsamen PROMAT-Inline-Action-Familie korrigiert statt nur auf dem einzelnen Access-Request-Link.

## Abweichungen

- Keine Abweichung von den aktiven Specs.
- Keine funktionale Änderung an Access-, Invite- oder Reset-Logik; geändert wurden nur Layer-Verhalten, sichtbare Abstände und Copy.

## Verifikation

- Editor-Fehlerprüfung der geänderten JS-, CSS-, Python- und Testdateien: ohne Fehler.
- Fokussierter Testlauf:
  - `pytest app/tests/test_auth_phase1.py -q`
  - Ergebnis: `12 passed`
- Live-Validierung gegen `http://127.0.0.1:8000/login?ui_lang=de` per Headless Edge:
  - künstlich geöffneten Dialog erzeugt
  - `window.showSnackbar(..., 0)` ausgelöst
  - DOM bestätigt: Snackbar gefunden, Parent-Host `DIALOG`, `hostDialogId='qa-snackbar-host'`

## Offene Punkte

- Keine im Scope dieses Follow-up-Runs.

## Nächste sinnvolle Schritte

- Bei weiteren Auth-/Admin-Dialogen dieselbe Host-Regel für flüchtige Overlays beibehalten: temporäre Meldungen gehören in den aktiven Top-Layer-Host, nicht blind an `body`.