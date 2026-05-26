# P2 Security Audit: CSP, CDN, Inline Styles, innerHTML

## 1. Scope

Geprueft wurde gezielt die aktuelle P2-Haertungslage fuer:

- globale Content-Security-Policy und zugehoerige Header
- externe Ressourcenabhaengigkeiten in produktiven Templates
- Inline-Styles in Templates und relevante dynamische Style-Schreibpfade in gebundenem JS
- Inline-Scripts und eventuelle Inline-Eventhandler
- `innerHTML`-, `DOMParser`- und verwandte HTML-Senken in gebundenem JS
- Jinja-`safe`-Nutzung und strukturierte HTML-Pipelines
- Teaching-Markdown-Rendering und statische Public-Content-HTML-Pfade
- realistische, risikoarme Folgearbeiten fuer die naechste P2-Phase

Ausdruecklich nicht erneut breit geprueft wurden:

- Reset-/Invite-Secret-Logging
- Gunicorn/WSGI-Prod-Start
- Redis-/Rate-Limit-Themen
- Access-Request-Mailtransport und Spam-Schutz
- allgemeine UI-/Design-System-Migrationen
- Teaching-Inhalte als redaktionelle Qualitaetspruefung

Methodik:

- statische Code- und Template-Suche in `app/src/app`, `app/templates`, `app/static/js`, `app/static/css`, `app/infra`, `docs/spec`
- keine Browser-Mutationen, keine Fixes, keine Runtime-Aenderungen
- keine Shell-Kommandos mit potentiellen Schreibeffekten ausgefuehrt

## 2. Kurzfazit

- CSP-Status: Es gibt bereits eine globale CSP aus der App-Factory, die auf alle Flask-Responses via `after_request` gelegt wird. Sie ist mittelstark, aber nicht auf Prod-Haertung ausgereizt.
- Externe Ressourcen: Produktiv aktiv sind Google Fonts, Font Awesome CDN, Bootstrap Icons CDN, YouTube-Embeds und Datawrapper-Embeds. Material Symbols liegen bereits lokal vor.
- Inline-Style-Lage: Ein echter Inline-`<style>`-Block im Basis-Template und ein produktiver `style="..."`-Iframe bei Datawrapper erzwingen aktuell mindestens eine Lockerung fuer Styles. Dazu kommen mehrere JS-Style-Schreibpfade.
- Inline-Script-Lage: Keine aktiven ausfuehrbaren Inline-Skripte in Templates gefunden. Vorhanden sind nur `type="application/json"`-State-Bloecke und JSON in `data-*`-Attributen.
- `innerHTML`-/HTML-Senken: Mehrere aktive Senken vorhanden, aber die meisten arbeiten mit Escape-Helpern oder statischem Markup. Das groesste Thema ist Haertbarkeit und Konsistenz, nicht ein klarer akuter XSS-Ausbruch.
- Template-/Markdown-Sicherheit: Die Teaching-Pipeline ist vergleichsweise sauber abgesichert mit `yaml.safe_load`, `MarkdownIt(..., {"html": False})` und strukturierten Blöcken. Public-Prose-HTML in `public_page_content_data.py` ist serverkontrolliert, aber nicht ueber dieselbe zentrale Normalisierung gefuehrt.
- Wichtigste Risiken: `style-src 'unsafe-inline'`, ueberbreite oder ungenutzte CSP-Allowlist-Eintraege, tote externe CDN-Lasten in `base.html`, fehlende `object-src`/`base-uri`/`form-action`, und einige grosse `innerHTML`-Renderpfade mit Wartungsrisiko.
- Empfohlene naechste Umsetzung: zuerst CSP ohne externe Script-Hosts und mit fehlenden Basisdirektiven haerten, parallel tote Icon-CDNs belegen und entfernen, danach die wenigen echten Inline-Style-Blocker und die groessten HTML-Senken fokussiert bereinigen.

## 3. CSP-Bestand

Quelle:

- `app/src/app/__init__.py`, Funktion `register_security_headers(...)`

Aktueller Header:

- `default-src 'self'`
- `script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com`
- `style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com`
- `img-src 'self' data: https: blob:`
- `font-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com`
- `connect-src 'self'`
- `frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com https://datawrapper.dwcdn.net`
- `frame-ancestors 'none'`

Bewertung:

- Bereits gut: `default-src 'self'`, `connect-src 'self'`, `frame-ancestors 'none'`, keine Wildcards, kein `unsafe-eval`.
- Schwachstellen:
  - `style-src 'unsafe-inline'` bleibt aktiv.
  - `script-src` erlaubt externe Hosts, obwohl in produktiven Templates keine externen Skripte geladen werden.
  - `img-src https:` ist breit; im produktiven Templatebestand wurde kein externer `img`-Load gefunden.
  - `object-src` fehlt.
  - `base-uri` fehlt.
  - `form-action` fehlt.
  - `media-src` ist nicht explizit gesetzt.
  - `youtube-nocookie.com` ist aktuell nur in CSP/Test belegt, nicht in produktiven Templates.
- Geltungsbereich: die CSP wird zentral ueber `@app.after_request` gesetzt und ist nicht auf einzelne Blueprints verteilt.
- Dev/Prod: keine getrennten CSP-Profile gefunden; nur HSTS wird an `app.debug` gekoppelt.
- Proxy/Deployment: in `app/infra/` keine zweite Header-Schicht oder Proxy-Header-Konfiguration fuer CSP gefunden.
- Doku: in `docs/spec/` keine aktive CSP- oder CDN-Spec gefunden; nur die Teaching-Markdown-Sicherheit ist bereits normativ beschrieben.

Realistisch kurzfristig verschaerfbar:

- `script-src` auf `'self'` reduzieren
- `object-src 'none'` ergaenzen
- `base-uri 'self'` ergaenzen
- `form-action 'self'` ergaenzen
- `frame-src` um ungenutzte Hosts pruefen und `youtube-nocookie.com` ggf. streichen
- `img-src` auf belegte Quellen verengen, wenn keine versteckten externen Bildpfade existieren

Verschaerfungen, die vorher Codeaenderungen brauchen:

- Entfernen von `style-src 'unsafe-inline'`
- Reduktion externer Style-/Font-Hosts, solange `base.html` Google Fonts, Font Awesome und Bootstrap Icons extern laedt
- striktere Embed-Haertung fuer Datawrapper, solange `src` serverseitig nicht host-validiert wird und die Resize-Message keinen Origin-Check nutzt

### CSP-Befunde

- Pfad: `app/src/app/__init__.py`
  Aktuelle Direktive: `style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com`
  Risiko: mittel
  Wahrscheinliche Ursache: Inline-`<style>` in `base.html`, produktiver `style="..."`-Iframe in Teaching-Embeds, externe Fonts/Icon-CSS
  Konkrete Empfehlung: erst produktive Inline-Style-Blocker und tote externe Icon-CDNs abbauen, dann `unsafe-inline` entfernen
  Prioritaet: P2a

- Pfad: `app/src/app/__init__.py`
  Aktuelle Direktive: `script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com`
  Risiko: niedrig bis mittel
  Wahrscheinliche Ursache: historische Allowlist, obwohl produktive Templates keine externen Skripte laden
  Konkrete Empfehlung: Allowlist auf `'self'` reduzieren und als fokussierte Regression absichern
  Prioritaet: P2a

- Pfad: `app/src/app/__init__.py`
  Aktuelle Direktive: `img-src 'self' data: https: blob:`
  Risiko: niedrig
  Wahrscheinliche Ursache: pauschale Freigabe statt evidenzbasierter Quellmenge
  Konkrete Empfehlung: pruefen, ob `https:` fuer Bilder wirklich benoetigt wird; aktueller Templatebestand belegt keine externen `img`-Loads
  Prioritaet: P2b

- Pfad: `app/src/app/__init__.py`
  Aktuelle Direktive: fehlend fuer `object-src`, `base-uri`, `form-action`
  Risiko: mittel
  Wahrscheinliche Ursache: Header wurde zuerst fuer bestehende Ressourcen repariert, nicht vollstaendig gehaertet
  Konkrete Empfehlung: `object-src 'none'; base-uri 'self'; form-action 'self'` als kleine, risikoarme Haertung ergaenzen
  Prioritaet: P2a

- Pfad: `app/src/app/__init__.py`
  Aktuelle Direktive: `frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com https://datawrapper.dwcdn.net`
  Risiko: niedrig
  Wahrscheinliche Ursache: YouTube-Reparatur plus Teaching-Datawrapper
  Konkrete Empfehlung: `youtube-nocookie.com` nur behalten, wenn ein echter Template-Pfad dafuer kommt; sonst Allowlist verengen
  Prioritaet: P2b

## 4. Externe Ressourcen / CDN

| Domain/URL | Zweck | Pfad | Kritisch? | Empfehlung |
|---|---|---|---|---|
| `https://fonts.googleapis.com` | Stylesheet fuer `Inter` und `Source Serif 4` | `app/templates/base.html` | Nein, aber visuell relevant | `lokalisieren`; aktuell nicht lokal vorhanden |
| `https://fonts.gstatic.com` | Font-Dateien fuer Google Fonts | indirekt ueber `app/templates/base.html` / CSP in `app/src/app/__init__.py` | Nein, aber visuell relevant | `lokalisieren`; aktuell nicht lokal vorhanden |
| `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.1/css/all.min.css` | Font Awesome Icon-CSS | `app/templates/base.html` | Nach heutigem Befund nein | `entfernen`; keine produktive Nutzung von `fa-*`-Klassen in Templates/JS gefunden |
| `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.min.css` | Bootstrap Icons CSS | `app/templates/base.html` | Nach heutigem Befund nein | `entfernen`; keine produktive Nutzung von `bi-*`-Klassen in Templates/JS gefunden |
| `https://www.youtube.com/embed/...` | Projektvideo-Embed | `app/templates/pages/promat_page.html` mit Daten aus `app/src/app/routes/public_page_content_data.py` | Optionaler Medienblock, aber gewollt | `behalten`; CSP-Allowlist bleibt erforderlich, spaeter nur enger dokumentieren |
| `https://www.youtube-nocookie.com` | in CSP erlaubt, aktuell kein produktiver Templatebeleg | nur `app/src/app/__init__.py` und Test | Nein | `entfernen` aus CSP, wenn kein geplanter No-Cookie-Embed existiert |
| `https://datawrapper.dwcdn.net/...` | Teaching-Embeds | `app/templates/partials/_teaching_blocks.html`, `app/src/app/teaching_content.py` | Fuer Teaching-Embeds funktional relevant | `behalten`; aber `src` serverseitig auf erlaubte Origin validieren und Message-Origin pruefen |

Zusatzbefunde:

- Lokale Alternative bereits vorhanden: `app/static/fonts/MaterialSymbolsRounded.woff2`.
- Externe Skripte im produktiven Templatebestand: keine gefunden.
- Externe Links wie ORCID, GitHub oder Hispanistica wurden gesehen, sind aber fuer CSP/CDN hier keine geladenen Skript-/Style-/Font-Abhaengigkeiten.

## 5. Inline-Styles

| Pfad | Fund | Grund | CSP-Auswirkung | Empfehlung |
|---|---|---|---|---|
| `app/templates/base.html` | echter Inline-`<style>`-Block im `<head>` | FOUC-/Hydration-/Theme-Load-Schutz | blockiert Entfernung von `style-src 'unsafe-inline'` | in produktive CSS-Datei oder sehr kleinen Nonce-/Hash-Pfad ueberfuehren; P2a |
| `app/templates/partials/_teaching_blocks.html` | `iframe style="width: 0; min-width: 100% !important; border: none; height: {{ block.height }}px;"` | responsiver Datawrapper-Embed | blockiert strengere Style-CSP | feste Klassen fuer statische Teile, `height` ueber CSS-Variable oder JS setzen; P2a |
| `app/static/js/modules/core/datawrapper.js` | `iframe.style.height = ...` | legitime Embed-Resize-Logik | haengt an Style-Attr/CSSOM | wahrscheinlich behalten, aber mit CSP-Zielbild abstimmen; P2b |
| `app/static/js/pages/research-player.js` | `style.setProperty('--pm-player-reference-*', ...)` | positionsabhaengiger Dialog | relevante Style-Attr/CSSOM-Nutzung | wahrscheinlich legitime PE-Logik; spaeter auf Klassen/positioning reviewen; P2b |
| `app/static/js/modules/core/teaching-mini-player.js` | `setProperty('--pm-audio-linked-progress', ...)` | Progress-Visualisierung | relevante Style-Attr/CSSOM-Nutzung | als legitime UI-State-Logik dokumentieren; nur spaeter umstellen wenn `unsafe-inline` wirklich weg soll; P2b |
| `app/static/js/modules/navigation/material-symbols-loader.js` | `test.style.cssText = ...`, `icon.style.display = 'none'` | Font-Test/Fallback | Style-CSP-relevant, aber kein Injektionsbug | spaeter auf Klassen umstellen; P3 |
| `app/static/js/modules/navigation/drawer.js` | `document.documentElement.style.overflow` / `document.body.style.overflow` | Scroll-Lock | Style-CSP-relevant, aber legitimer Zustand | spaeter auf Klassen umstellen; P3 |
| `app/static/js/modules/auth/login.js` | `errorEl.style.display = ...` | Formularfehler anzeigen/ausblenden | Style-CSP-relevant, geringes Risiko | spaeter auf `[hidden]`/Klassen umstellen; P3 |

Einordnung:

- Akut CSP-blockierend sind vor allem die Template-Stellen in `base.html` und `_teaching_blocks.html`.
- Mehrere JS-Style-Schreibpfade sind legitime Zustandslogik und sollten nicht pauschal als Sicherheitsbug behandelt werden.
- Fuer die naechste P2-Phase ist ein enger Fokus auf produktive Template-Inline-Styles sinnvoller als eine Totalbereinigung jeder `.style`-Zuweisung.

## 6. Inline-Scripts

| Pfad | Fund | Risiko | CSP-Auswirkung | Empfehlung |
|---|---|---|---|---|
| `app/templates/pages/research_comparison.html` | `<script type="application/json" id="pm-comparison-state">{{ ... | tojson }}</script>` | niedrig | blockiert strikte Script-CSP nicht wie ein ausfuehrbares Inline-Skript | beibehalten; sichere JSON-State-Einspeisung |
| `app/templates/pages/research_player.html` | `<script type="application/json" id="pm-player-state">{{ ... | tojson }}</script>` | niedrig | wie oben | beibehalten |
| `app/templates/pages/research_phenomena_editor.html` | JSON-State-Skriptblock | niedrig | wie oben | beibehalten |
| `app/templates/pages/research_phenomena_overview.html` | JSON-State-Skriptblock | niedrig | wie oben | beibehalten |
| `app/templates/base.html` | keine ausfuehrbaren Inline-Skripte, nur externe lokale Scripts | niedrig | gute Ausgangslage fuer strikte `script-src` | keine Aktion ausser CSP-Allowlist verengen |
| `app/templates/**` | keine Eventhandler-Attribute wie `onclick=`, `onsubmit=` gefunden | niedrig | erleichtert CSP-Haertung | so beibehalten |

Zusatzbefunde:

- Keine Treffer fuer `eval`, `new Function`, `document.write`, `insertAdjacentHTML`, `createContextualFragment` in gebundenem Produktiv-JS.
- `theme.js` haengt Load-/Error-Listener fuer async geladene Stylesheets sauber programmatisch an, nicht per Inline-Handler.

## 7. innerHTML / HTML-Senken

| Pfad | Funktion/Senke | Datenquelle | Schutz | Risiko | Empfehlung |
|---|---|---|---|---|---|
| `app/static/js/md3/alert-utils.js` | `container.innerHTML = createAlertHTML(...)` | Meldung aus Aufrufern, optional `title` | `message` wird escaped, `title` derzeit nicht | unklar bis latent riskant | Titel ebenfalls escapen; aktuell aktive Aufrufer reichen nur `message` und nutzen Default-Titel |
| `app/static/js/auth/admin_users.js` | mehrere `innerHTML`-Renderer fuer Toast, Tabellenzeilen, Leerzustaende | API-JSON und i18n-Config | zentrale `escapeHtml(...)` fuer Texte/Attribute | wahrscheinlich sicher | mittelfristig DOM-Builder fuer grosse Fragmente; kurzfristig Tests fuer Escaping beibehalten |
| `app/static/js/modules/core/snackbar.js` | `snackbar.innerHTML = ...` | Flash-/UI-Messages | `escapeHtml(message)` | wahrscheinlich sicher | kann bleiben, geringer P2-Druck |
| `app/static/js/modules/auth/snackbar.js` | `snackbar.innerHTML = ...` | statischer Literaltext | statisch | sicher | keine P2-Massnahme noetig |
| `app/static/js/pages/research-comparison.js` | viele `innerHTML`-Zuweisungen fuer Matrix, Filter, Sessionlisten | JSON-State aus `type="application/json"` | zentrales `escapeHtml(...)`, statische `iconSvg(...)` | wahrscheinlich sicher, aber grosse Wartungsflaeche | priorisierte Haertung ueber wenige grosse Renderfunktionen und Regressionen, nicht blind alles gleichzeitig |
| `app/static/js/pages/research-player.js` | `DOMParser().parseFromString(html, 'text/html')` und Node-Import | same-origin HTML-Fetch von Player-Navigation | gleiche App-Templates, keine direkte User-HTML-Einspeisung belegt | unklar, aber derzeit eher architektonisch als akut | keine Sofortmassnahme; bei spaeterer Haertung ggf. auf strukturiertere Partial-Responses umstellen |
| `app/static/js/modules/core/datawrapper.js` | `postMessage`-Resize, keine `innerHTML`-Senke, aber fremde Message-Verarbeitung | Event von eingebettetem Iframe | Payload-Shape und `contentWindow`-Abgleich, aber kein `event.origin`-Check | wahrscheinlich sicher mit Resthaertungsluecke | `event.origin === 'https://datawrapper.dwcdn.net'` oder strikte Allowlist ergaenzen |
| `app/static/js/auth/admin_users.js` | `readConfig()` nutzt `element.innerHTML` als Fallback | Template-JSON aus `<template>` | vorher `textContent`, dann Fallback | niedrig | auf `textContent` beschraenken; Fallback ist unnoetig breit |

Testbedarf:

- Escaping-Regressionsfokus fuer `research-comparison.js`
- kleiner Unit-/DOM-Test fuer `alert-utils.js`, dass `title` nicht roh in HTML landet
- Datawrapper-Message-Test fuer Origin-Allowlist, wenn spaeter gehaertet wird

## 8. Template-/Markdown-Rendering

Abgesicherte Stellen:

- `app/src/app/teaching_content.py` nutzt `yaml.safe_load(...)`.
- `_MARKDOWN_RENDERER = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": False})` deaktiviert rohes HTML in Teaching-Markdown.
- Viele Template-`|safe`-Stellen in `app/templates/partials/_teaching_blocks.html`, `_content_header.html`, `_admonition.html` und `app/templates/pages/teaching_page.html` rendern nicht freie User-Eingaben, sondern strukturierte HTML-Ausgaben aus dieser Pipeline.
- `docs/spec/platform-data-files.md` normiert bereits, dass Teaching-Markdown nur sichere CommonMark-Elemente rendert und raw HTML deaktiviert bleibt.

Wahrscheinlich sichere Stellen:

- JSON-State-Einspeisung in Research-Templates ueber `|tojson`.
- `data-config` und `data-flash-messages` in `app/templates/base.html` ueber `|tojson | e`.

Unklare Stellen:

- `app/src/app/teaching_content.py::_embed_payload(...)` akzeptiert bei `provider == 'datawrapper'` jedes nichtleere `src`, ohne die Host-Origin serverseitig zu validieren. Die CSP blockt Fremdhosts zwar im Browser, aber die Datenvalidierung ist nicht vollstaendig.
- `app/static/js/pages/research-player.js` tauscht HTML-Fragmente ueber `DOMParser` und same-origin Fetch aus. Das ist nicht direkt unsicher belegt, aber eine breitere Sink-Klasse als rein datengetriebene UI.

Riskante Stellen:

- Kein klarer produktiver `|safe`-Pfad mit direkt userkontrolliertem HTML wurde gefunden.
- Der schwaechste aktive Hilfspfad ist nicht Jinja, sondern `md3/alert-utils.js`, weil dort der Titel ungeescaped interpoliert wird, falls spaeter dynamisch genutzt.

Serverkontrollierte Raw-/Safe-HTML-Stellen:

- `app/templates/pages/promat_page.html` rendert `paragraphs_html`, `bullets_html` und `caption_html` mit `|safe`.
- Diese HTML-Fragmente stammen aus `app/src/app/routes/public_page_content_data.py` und sind derzeit hartkodierte, serverkontrollierte Inhaltsdaten mit bewusstem `<em>`-Markup.
- Das ist nach heutigem Befund wahrscheinlich sicher, aber nicht ueber dieselbe zentrale Markdown-Normalisierung abgesichert wie Teaching.

## 9. Priorisierte Befunde

### P2a: vor Prod-Haertung relevant

- ID: `P2A-01`
  Titel: CSP erlaubt unnoetige externe Script-Hosts und es fehlen Basisdirektiven
  Pfad: `app/src/app/__init__.py`
  Evidenz: `script-src` erlaubt `cdn.jsdelivr.net` und `cdnjs.cloudflare.com`, obwohl produktive Templates keine externen Skripte laden; `object-src`, `base-uri`, `form-action` fehlen
  Risiko: unnötig breite Ausfuehrungs- bzw. Navigationsflaeche
  Empfehlung: `script-src 'self'`; `object-src 'none'`; `base-uri 'self'`; `form-action 'self'`

- ID: `P2A-02`
  Titel: `style-src 'unsafe-inline'` ist aktuell technisch erzwungen
  Pfad: `app/templates/base.html`, `app/templates/partials/_teaching_blocks.html`, `app/src/app/__init__.py`
  Evidenz: echter Inline-`<style>`-Block und produktiver Iframe-`style`-Attributpfad
  Risiko: verhindert strengere CSP fuer Styles
  Empfehlung: zuerst nur diese beiden Template-Stellen herausziehen bzw. strukturieren, nicht alle JS-Style-Zuweisungen gleichzeitig

- ID: `P2A-03`
  Titel: Tote externe Icon-CDNs erweitern CSP und Angriffs-/Ausfallflaeche ohne belegten Nutzen
  Pfad: `app/templates/base.html`
  Evidenz: Font Awesome und Bootstrap Icons werden global geladen; keine produktive `fa-*`- oder `bi-*`-Nutzung in Templates/JS gefunden
  Risiko: unnötige externe Abhaengigkeiten und breitere `style-src`/`font-src`-Allowlist
  Empfehlung: zuerst belegbar entfernen, dann CSP entsprechend verengen

- ID: `P2A-04`
  Titel: Datawrapper-Embeds sind funktional erlaubt, aber noch nicht streng genug validiert
  Pfad: `app/src/app/teaching_content.py`, `app/static/js/modules/core/datawrapper.js`
  Evidenz: `src` nicht host-validiert; `postMessage` ohne `event.origin`-Check
  Risiko: kleine, aber reale Resthaertungsluecke an externer Embed-Grenze
  Empfehlung: Datawrapper-Host serverseitig allowlisten und `event.origin` explizit pruefen

### P2b: bald bereinigen

- ID: `P2B-01`
  Titel: `img-src https:` ist breiter als aktuell belegt
  Pfad: `app/src/app/__init__.py`
  Evidenz: keine externen produktiven `img`-Loads in Templates gefunden
  Risiko: unnötige Breite in CSP
  Empfehlung: auf belegte Quellen reduzieren, sofern keine verdeckten Bildpfade existieren

- ID: `P2B-02`
  Titel: Research-Comparison rendert grosse HTML-Fragmente per `innerHTML`
  Pfad: `app/static/js/pages/research-comparison.js`
  Evidenz: viele HTML-String-Renderer, aber mit zentralem `escapeHtml(...)`
  Risiko: aktuell eher Wartungs- und Regressionsrisiko als akute XSS
  Empfehlung: nur die groessten Renderfunktionen spaeter auf DOM-Building oder engere Helper umstellen; Regressionstests vorher/nachher

- ID: `P2B-03`
  Titel: Google Fonts bleiben externe Prod-Abhaengigkeit
  Pfad: `app/templates/base.html`
  Evidenz: `fonts.googleapis.com` und `fonts.gstatic.com` aktiv, keine lokalen Fontdateien fuer `Inter`/`Source Serif 4`
  Risiko: Datenschutz-/Ausfall- und CSP-Breite
  Empfehlung: lokalisieren oder bewusst behalten; nicht im gleichen Schritt wie HTML-Senken mischen

- ID: `P2B-04`
  Titel: `youtube-nocookie.com` ist in der CSP aktuell unbelegt
  Pfad: `app/src/app/__init__.py`
  Evidenz: produktive Templates nutzen `youtube.com`, kein `youtube-nocookie`-Treffer ausser CSP/Test
  Risiko: geringe, aber unnoetige Allowlist-Breite
  Empfehlung: streichen, falls kein naher Umstieg geplant ist

### P3: Wartbarkeit / Design-Schuld

- ID: `P3-01`
  Titel: `alert-utils` escapt den Titel derzeit nicht
  Pfad: `app/static/js/md3/alert-utils.js`
  Evidenz: `displayTitle` wird roh in HTML interpoliert, `message` dagegen escaped
  Risiko: latent; aktive Aufrufer uebergeben derzeit keine dynamischen Titel
  Empfehlung: bei der HTML-Senken-Runde mitziehen, kleiner Test dazu

- ID: `P3-02`
  Titel: `admin_users.js` nutzt `innerHTML`-Fallback beim JSON-Config-Lesen
  Pfad: `app/static/js/auth/admin_users.js`
  Evidenz: `(element.content && element.content.textContent) || element.innerHTML || '{}'`
  Risiko: niedrig, aber unnötig breit
  Empfehlung: auf `textContent` beschraenken

- ID: `P3-03`
  Titel: Mehrere legitime JS-Style-Workarounds erschweren eine sehr strenge Style-CSP
  Pfad: diverse Dateien in `app/static/js/**`
  Evidenz: `drawer.js`, `material-symbols-loader.js`, `research-player.js`, `datawrapper.js`, `teaching-mini-player.js`
  Risiko: eher technische Schuld als Sicherheitsluecke
  Empfehlung: spaeter selektiv auf Klassen oder strukturiertere CSS-Variablenpfade umstellen

## 10. Folgeprompts

1. `Implement CSP Hardening`

   Scope:
   
   - nur CSP-Header und direkt davon blockierte, kleine produktive Vorbedingungen
   - keine Design-System-Migration, keine Teaching-Content-Aenderungen, keine Browser-QA-Ausweitung
   - `script-src` auf belegte Quellen verengen
   - fehlende Basisdirektiven (`object-src`, `base-uri`, `form-action`) ergaenzen
   - `frame-src` auf belegte Hosts pruefen und ungenutzte Hosts entfernen
   - `img-src` nur dann verengen, wenn belegte Quellen klar sind
   - `style-src 'unsafe-inline'` nur dann angreifen, wenn die zwei belegten Template-Blocker mit kleiner Reichweite behoben werden koennen
   
   Anforderungen:
   
   - fokussierte Tests fuer Security-Header anpassen/ergaenzen
   - bestehende Auth-/Research-Tests laufen lassen, wenn betroffen
   - Abschlussbericht als Markdown unter Repo-Konvention `docs/agent-runs/` anlegen
   - zwischen sicher bestaetigten und weiter offenen CSP-Abhaengigkeiten sauber unterscheiden

2. `Localize or Remove External CDN Dependencies`

   Scope:
   
   - nur externe Fonts/Icon-CDNs und zugehoerige Template-/CSP-Verkabelung
   - keine grossen UI-Umbauten
   - tote Abhaengigkeiten zuerst entfernen, bevor lebende Abhaengigkeiten lokalisiert werden
   - `Font Awesome` und `Bootstrap Icons` nur entfernen, wenn die belegte Nutzung weiter leer bleibt
   - Google Fonts getrennt behandeln, inklusive lokaler Dateien oder bewusstem Verbleib
   
   Anforderungen:
   
   - Such-/Regressionsevidenz fuer jede entfernte Domain dokumentieren
   - relevante Template-/CSP-Tests ergaenzen
   - keine sichtbaren UI-Brueche billig in Kauf nehmen
   - Abschlussbericht als Markdown unter Repo-Konvention `docs/agent-runs/` anlegen

3. `Replace Risky Inline HTML/Styles/Scripts`

   Scope:
   
   - nur die belegten produktiven Blocker: `base.html` Inline-Style, Teaching-Datawrapper-`style`, `alert-utils`-Titel-Escaping, `admin_users` JSON-Fallback, optional die groessten `research-comparison`-Renderer
   - keine pauschale Totalbereinigung aller `.style`- und `innerHTML`-Verwendungen
   - legitime UI-State-Logik mit CSS-Variablen nur dann anfassen, wenn sie die neue CSP direkt blockiert
   
   Anforderungen:
   
   - fuer jede angefasste Senke klar dokumentieren: bisheriger Schutz, neuer Schutz, Restrestrisiko
   - DOM-/Unit- oder fokussierte Pytest-/JS-Regressionen verlangen
   - Abschlussbericht als Markdown unter Repo-Konvention `docs/agent-runs/` anlegen
   - sichere Befunde und unklare Befunde getrennt behandeln, nicht zusammen refactoren

## 11. Tests/Checks

Ausgefuehrte Checks:

- statische Workspace-Suchen in produktiven Pfaden (`app/src/app`, `app/templates`, `app/static/js`, `app/static/css`, `app/infra`, `docs/spec`)
- gezielte Datei-Lektuere der aktiven Header-, Template-, JS- und Markdown-Pfade

Nicht als Shell-Kommando ausgefuehrt:

- `pytest --collect-only`
- `python -m compileall app`
- `docker compose -f app/infra/docker-compose.prod.yml config`
- fokussierte `pytest`-Laeufe

Grund:

- fuer diesen engen P2-Audit war die benoetigte Evidenz vollstaendig ueber statische Produktivpfade erreichbar
- zur Wahrung des explizit read-only gehaltenen Audits wurden keine zusaetzlichen Shell-Checks mit moeglichen Nebeneffekten oder Cache-Artefakten mehr ausgefuehrt

## 12. No-Go

Bestaetigt:

- keine Produktivdateien der Anwendung, Konfiguration oder Tests wurden geaendert
- keine Fixes angewendet
- kein kompletter Rundumaudit durchgefuehrt
- keine P0/P1-Themen erneut breit bearbeitet
- keine Design-System-Migration vorgeschoben
- keine echten externen Aktionen ausgefuehrt

Abweichung nur fuer die Dokumentation:

- es wurde ausschliesslich dieser geforderte Auditbericht nach bestehender Repo-Konvention unter `docs/agent-runs/` angelegt, weil `docs/reports/` hier nicht die etablierte Struktur ist
