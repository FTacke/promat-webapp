# Fix: /access-request 500 nach erfolgreichem Submit

**Datum:** 2026-06-22

## Ursache des 500-Fehlers

Der POST-Handler für `/access-request` leitete nach erfolgreichem Mailversand per `flash()` + `redirect()` zurück auf dieselbe Form-URL. Das Template `access_request.html` rief dann `get_flashed_messages()` auf – allerdings hatte `base.html` die Flash-Messages bereits in `data-flash-messages` (für die Snackbar) konsumiert, bevor der Template-Block in `access_request.html` auswertete. Die Bestätigungsnachricht erschien damit nie sauber inline.

In bestimmten Produktionskonfigurationen (Session-State, Rate-Limiter-Backend, SMTP-Timing) konnte der Redirect-Zyklus außerdem mit einem 500 brechen, ohne dass im Test-Setup eine entsprechende Fehlerquelle sichtbar war.

## Gelöster Ansatz

Statt `flash()` + Redirect zur Form-URL → direkter Redirect zu `?submitted=1`. Der GET-Handler erkennt `submitted=1` und rendert einen sauberen Bestätigungs-State direkt im Template – ohne Flash-Abhängigkeit, ohne Session-State, ohne erneutes Formular.

## Geänderte Dateien

| Datei | Änderung |
|---|---|
| `app/src/app/i18n.py` | Neue Keys `auth.access_request.submitted_heading`, `submitted_body`, `submitted_disclaimer`, `submitted_login_hint` (DE + EN) |
| `app/src/app/routes/public.py` | `flash`-Import entfernt; neuer Helper `_build_access_request_submitted_href`; `_render_access_request_page` um `submitted`-Parameter erweitert; GET-Handler liest `?submitted=1`; POST-Handler leitet zu `submitted`-URL, kein `flash()` mehr |
| `app/templates/auth/access_request.html` | `{% if submitted %}` Branch: zeigt Bestätigungsartikel mit 72h-Text; `{% else %}` Branch: zeigt das Formular wie bisher |
| `app/tests/test_auth_phase1.py` | Redirect-Location-Assertion aktualisiert (`?submitted=1`); Erfolgstext-Assertion auf neuen 72h-Text angepasst; 7 neue Tests für Confirmation-State (DE, EN, Login-Link, Form-absent, kein 500, Honeypot-Redirect) |

## Erfolgreicher Submit-Flow (nach Fix)

```
POST /access-request
  → DB-Eintrag anlegen
  → Betreiber-Mail senden
  → redirect 303 → /access-request?next=...&submitted=1

GET /access-request?submitted=1
  → _render_access_request_page(submitted=True)
  → HTTP 200, Bestätigungsseite mit 72h-Text, kein Formular
```

## Checks

- `python -m ruff check .` → All checks passed
- `python -m compileall -q app/src app/scripts` → keine Fehler
- `python -m pytest app/tests/test_auth_phase1.py` → **134/134 passed**
- `python -m pytest app/tests/test_auth_phase1.py -k access_request` → **18/18 passed** (inkl. 7 neue Tests)

Nicht berührt: Fehlschläge in `test_research_sessions.py` waren vor diesem Task bereits vorhanden (Datei im ursprünglichen git-Status als modifiziert markiert, unrelated zu access-request).
