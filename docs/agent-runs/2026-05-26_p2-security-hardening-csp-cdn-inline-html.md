# P2 Security Hardening: CSP, CDN, Inline Styles, HTML Sinks

## 1. Scope

Umgesetzt wurde gezielt der priorisierte P2a-Slice aus dem CSP/CDN/Inline/HTML-Audit:

- CSP-Basis in `app/src/app/__init__.py` enger und vollstaendiger gemacht
- tote externe Icon-CDNs aus `app/templates/base.html` entfernt
- Datawrapper-Embeds server- und clientseitig gehaertet
- zwei kleine HTML-Senken in `alert-utils.js` und `admin_users.js` bereinigt
- die zwei produktiven Template-Inline-Style-Blocker risikoarm reduziert
- aktive Teaching-Spec fuer den Datawrapper-Host nachgezogen

Ausdruecklich nicht umgesetzt:

- keine Design-System-Migration
- keine Google-Fonts-Lokalisierung
- keine breite `innerHTML`-Totalbereinigung
- keine Teaching-Content-Aenderungen
- keine P0/P1-Arbeit
- keine pauschale Entfernung legitimer JS-Style-State-Logik

## 2. Änderungen

- `app/src/app/__init__.py`
  - CSP enger gemacht: externe Script-CDNs entfernt, fehlende Basisdirektiven ergaenzt, `frame-src` verengt
- `app/templates/base.html`
  - Font Awesome und Bootstrap Icons CDN-Links entfernt
  - statischen Inline-`<style>`-Block entfernt
- `app/static/css/layout.css`
  - frueherer statischer `base.html`-Head-Style in die zuerst geladene CSS-Datei ueberfuehrt
- `app/static/css/30_components.css`
  - statische Datawrapper-Iframe-Stilanteile in CSS verschoben
- `app/templates/partials/_teaching_blocks.html`
  - Datawrapper-Iframe ohne Inline-`style`, mit `height`-Attribut und Klassen weitergerendert
- `app/src/app/teaching_content.py`
  - serverseitige HTTPS-/Host-/Pfad-Allowlist fuer Datawrapper-`src` eingebaut
- `app/static/js/modules/core/datawrapper.js`
  - `postMessage`-Origin auf `https://datawrapper.dwcdn.net` verengt
- `app/static/js/md3/alert-utils.js`
  - Alert-Titel wird jetzt genauso escaped wie die Message
- `app/static/js/auth/admin_users.js`
  - Config-Lesen auf `textContent` begrenzt; kein `innerHTML`-Fallback mehr
- `app/tests/test_auth_phase1.py`
  - CSP- und entfernte-CDN-Regressionsabdeckung erweitert
- `app/tests/test_teaching_content.py`
  - Datawrapper-URL-Validierung und invalid-source-Pfade abgedeckt
- `app/tests/js/p2_security_hardening.test.mjs`
  - neue kleine JS-Regressionen fuer Alert-Escaping und Datawrapper-Origin
- `docs/spec/platform-data-files.md`
  - aktive Teaching-Embed-Regel auf `https://datawrapper.dwcdn.net/...` eingegrenzt

## 3. CSP

Vorher relevante Direktiven:

- `script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com`
- `style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com`
- `font-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com`
- `frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com https://datawrapper.dwcdn.net`
- keine `object-src`
- keine `base-uri`
- keine `form-action`

Nachher relevante Direktiven:

- `script-src 'self'`
- `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com`
- `font-src 'self' https://fonts.gstatic.com`
- `frame-src 'self' https://www.youtube.com https://datawrapper.dwcdn.net`
- `object-src 'none'`
- `base-uri 'self'`
- `form-action 'self'`

Entfernte externe Hosts:

- `cdnjs.cloudflare.com` aus `script-src`, `style-src`, `font-src`
- `cdn.jsdelivr.net` aus `script-src`, `style-src`, `font-src`
- `youtube-nocookie.com` aus `frame-src`

Neu ergaenzte Direktiven:

- `object-src 'none'`
- `base-uri 'self'`
- `form-action 'self'`

Bewusst beibehaltene Direktiven:

- `style-src 'unsafe-inline'` bleibt vorerst bestehen
  - Grund: der grosse P2a-Blocker in Templates ist beseitigt, aber es existieren weiterhin mehrere legitime JS-CSSOM-/Style-State-Pfade; diese wurden in diesem Run bewusst nicht breit refactort
- `img-src 'self' data: https: blob:` bleibt unveraendert
  - Grund: fuer eine weitere Verengung fehlte in diesem Run ein sicherer Vollbeleg aller produktiven Bildquellen
- Google-Fonts-Hosts bleiben fuer Styles/Fonts erlaubt
  - Grund: Lokalisierung war explizit nicht Teil dieses Runs

`style-src 'unsafe-inline'` konnte in diesem Run nicht entfernt werden.

## 4. Externe Ressourcen

Entfernte CDN-Abhaengigkeiten:

- Font Awesome aus `app/templates/base.html`
- Bootstrap Icons aus `app/templates/base.html`

Bewusst beibehaltene externe Ressourcen:

- Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`)
- YouTube-Embed fuer die Projektseite
- Datawrapper-Embeds fuer Teaching

Google Fonts Status:

- unveraendert extern
- keine Lokalisierung in diesem Run

YouTube/Datawrapper Status:

- YouTube bleibt erlaubt und in `frame-src` enthalten
- `youtube-nocookie.com` wurde entfernt, weil keine produktive Nutzung belegt war
- Datawrapper bleibt erlaubt, aber jetzt mit serverseitiger `src`-Allowlist und clientseitiger Origin-Pruefung

## 5. Datawrapper-Härtung

Serverseitige `src`-Validierung:

- nur `https` erlaubt
- Host muss exakt `datawrapper.dwcdn.net` sein
- keine `http:`, `javascript:`, `data:` oder protocol-relative URLs
- keine Userinfo, kein Port, keine Query-/Fragment-Anhaenge
- nur sinnvolle absolute Pfade werden akzeptiert und normalisiert
- invalide Datawrapper-Quellen werden verworfen und geloggt, statt gerendert

Clientseitige `postMessage`-Origin-Pruefung:

- `app/static/js/modules/core/datawrapper.js` akzeptiert Resize-Messages jetzt nur noch von `https://datawrapper.dwcdn.net`
- der bestehende Payload-Shape- und `contentWindow`-Abgleich bleibt zusaetzlich aktiv

Tests:

- Python-Regressionen fuer gueltige und ungueltige Datawrapper-URLs
- JS-Regression fuer den Origin-Check
- bestehende Research-/Teaching-Render-Tests weiter gruen

## 6. HTML-/Inline-Senken

`alert-utils`-Titel-Escaping:

- Titel wird jetzt genauso escaped wie die Message
- keine API-Aenderung fuer Aufrufer

`admin_users` Config-Leselogik:

- JSON-Template-Config wird nur noch ueber `content.textContent` bzw. `textContent` gelesen
- kein `innerHTML`-Fallback mehr

Template-Inline-Style-Aenderungen:

- der statische Head-Style aus `base.html` wurde in `app/static/css/layout.css` verschoben
- der Datawrapper-Iframe nutzt keine Template-Inline-Styles mehr; statische Teile sitzen in CSS, die Hoehe kommt ueber das validierte `height`-Attribut und spaetere Resize-Updates

Verbleibende `innerHTML`-/Style-Restthemen:

- mehrere legitime `innerHTML`-Renderpfade, vor allem im Research-Comparison-JS, bleiben unveraendert
- mehrere legitime JS-Style-State-Pfade bleiben unveraendert
- diese Themen sind bewusst in einen spaeteren, engeren Folgeblock verschoben worden

## 7. Tests und Checks

Ausgefuehrte Kommandos und Ergebnisse:

- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_teaching_content.py -q -k "security_headers or access_request_page_does_not_load_removed_icon_cdns or admin_users_static_js_uses_semantic_action_button_classes or datawrapper"`
  - `11 passed, 86 deselected`
- `node --test app/tests/js/p2_security_hardening.test.mjs`
  - `2 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q`
  - `65 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -q`
  - `201 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests -q -k "security_headers or csp or teaching or datawrapper or admin_users or alert"`
  - `55 passed, 418 deselected`
- `c:\dev\promat\.venv\Scripts\python.exe -m compileall app`
  - erfolgreich
- `node --test app/tests/js/*.test.mjs`
  - `7 passed`
- `docker compose -f app/infra/docker-compose.prod.yml config`
  - erfolgreich mit Platzhalterwerten fuer die bewusst verpflichtenden Env-Variablen

Optionale Checks:

- `ruff`
  - im lokalen venv nicht vorhanden
- `mypy`
  - im lokalen venv nicht vorhanden

## 8. Nicht umgesetzt

- keine Design-System-Migration
- keine Google-Fonts-Lokalisierung
- keine breite `innerHTML`-Totalbereinigung
- keine Teaching-Content-Aenderungen
- keine P0/P1-Arbeit
- `style-src 'unsafe-inline'` nicht entfernt
  - Grund: Restbestand legitimer JS-Style-State-Logik wurde in diesem Run bewusst nicht breit umgebaut
- `img-src` nicht weiter verengt
  - Grund: fuer einen sicheren Vollbeleg fehlte in diesem Run die noetige Evidenzbasis

## 9. Verbleibende nächste Schritte

- Google Fonts lokalisieren oder bewusst als externe Restabhaengigkeit akzeptieren
- Research-Comparison-Renderer langfristig haerten
- `img-src` weiter verengen, sobald alle produktiven Bildquellen sicher belegt sind
- `style-src 'unsafe-inline'` erst entfernen, wenn der verbleibende JS-Style-Restbestand gezielt geprueft und ohne UI-Bruch umgestellt werden kann
