# Icon Convention + Font Policy

## 1. Scope

Umgesetzt wurde ein enger Folge-Run auf Basis des vorherigen Icon-/Font-Audits:

- aktive Icon-Konvention in der bindenden Spec dokumentiert
- den bestehenden produktiven Dual-Weg explizit geregelt
- einen kleinen, eindeutig toten Icon-Altpfad bereinigt
- externe Google Fonts bewusst als aktuelle Produktentscheidung dokumentiert
- bestehende negative Absicherung fuer entfernte Icon-CDNs beibehalten und erweitert

Nicht im Scope:

- keine Google-Fonts-Lokalisierung
- keine Font-Downloads
- keine Typografie-Neugestaltung
- keine Design-System-Migration
- keine breite Icon-Migration
- keine Farbangleichung
- keine Research-Comparison-Inline-SVG-Migration
- keine pauschale Ersetzung typografischer Pfeile oder `i`-Marker
- keine breite P2-Security-Nacharbeit

## 2. Änderungen

- `docs/spec/platform-data-files.md`
  - aktive Icon-Konvention und externe Google-Fonts-Policy als bindende Plattformregel dokumentiert
- `app/static/js/modules/auth/snackbar.js`
  - entfernt; isolierter Legacy-Auth-Snackbar-Pfad ohne belegte produktive Call-Sites
- `app/static/css/md3/components/snackbar.css`
  - toten `md3-snackbar--auth-expired`-Block entfernt, inklusive `material-symbols-outlined`-Restpfad
- `app/tests/test_auth_phase1.py`
  - HTML-Regressionsabdeckung fuer externe Google Fonts plus lokales Material-Symbol-Stylesheet erweitert
  - neue statische Regression fuer den entfernten Legacy-Snackbar-Pfad hinzugefuegt

## 3. Icon-Konvention

Dokumentierte Regel:

- `Material Symbols Rounded` ist der kanonische Font-Weg fuer inline/textnahe Aktions-, Formular- und Status-Icons sowie andere kleine Interaktionsicons in Buttons, Labels, Cards, Alerts, Snackbars und Messages.
- Auslieferung fuer diesen Weg bleibt lokal/self-hosted.
- Shared-Default-Achsen bleiben die bereits belegten CSS-Basiswerte: `FILL 0`, `wght 300`, `GRAD 0`, `opsz 24`.
- Groesse, Line-Height und Alignment laufen ueber bestehende Tokens und Shared-Klassen, nicht ueber ad hoc Overrides.
- `pm-icon-mask` ist der kanonische Chrome-/Utility-Weg fuer Shell-, Drawer-, Player-, Lock-, Theme-, Admonition- und vergleichbare Oberflaechenicons.
- `pm-icon-mask` bleibt ein zentrales CSS-Mask-System auf Basis gemeinsamer SVG-Data-URI-Tokens; Groesse laeuft ueber die bestehenden `--pm-icon-size-*`-Tokens, Farbe bleibt kontext- bzw. tokenabhaengig.
- Zulässige Sonderfälle bleiben:
  - Inline-SVGs in dynamisch gebauter JS-UI, wenn der kanonische Weg unverhaeltnismaessig waere
  - typografische Pfeile/Symbole, wenn sie bewusst Textelemente statt generischer Icon-Slots sind
  - zentral verwaltete SVG-Masks im `pm-icon-mask`-System
- Nicht gewuenscht bleiben:
  - neue Font-Awesome-Nutzung
  - neue Bootstrap-Icons-Nutzung
  - neue externe Icon-CDNs
  - unbegruendete Material-Symbol-Variantenabweichungen
  - zufaellige page-lokale Inline-SVGs ohne zentralen Grund

## 4. Bereinigte Icon-Reste

Entfernt:

- `app/static/js/modules/auth/snackbar.js`
- der zugehoerige `md3-snackbar--auth-expired`-CSS-Block in `app/static/css/md3/components/snackbar.css`

Warum sicher:

- Suche nach `showAuthExpiredSnackbar|modules/auth/snackbar|material-symbols-outlined` in `app/**` lieferte vor der Bereinigung nur Treffer in genau dieser Legacy-Moduldatei und dem zugehoerigen CSS-Block.
- In `app/static/js/modules/core/entry.js` und den produktiven Template-Pfaden wurde stattdessen nur die aktuelle Core-Snackbar-Initialisierung belegt.
- Es gab keine belegten Template-, JS- oder Test-Call-Sites fuer den Legacy-Auth-Snackbar-Pfad.

Suchbelege:

- `showAuthExpiredSnackbar` vor der Bereinigung: nur `app/static/js/modules/auth/snackbar.js`
- `material-symbols-outlined` vor der Bereinigung: nur `app/static/js/modules/auth/snackbar.js` und `app/static/css/md3/components/snackbar.css`
- Font Awesome / Bootstrap Icons in produktiven App-Pfaden: keine produktive Nutzung belegt; nur negative Regressionen und historische Artefakte

Bewusst beibehalten:

- alte MD3-Material-Symbol-Overrides in `app/static/css/md3/components/top-app-bar.css`
  - Grund: sie wirken zwar nach heutigem Befund wie paralleler oder historischer CSS-Bestand, aber dieser Run hat sie nicht entfernt, weil die Datei global geladen wird und eine breitere CSS-Bereinigung nicht im Scope lag
- dynamische Inline-SVGs in `app/static/js/pages/research-comparison.js`
  - Grund: bewusst geschlossener JS-Sonderfall, keine sichere Altlast
- typografische Pfeile und einzelne Pseudo-Icons
  - Grund: keine pauschale Migration in diesem Run

## 5. Google-Fonts-Policy

- Google Fonts bleiben bewusst extern.
- Produktiv betroffen sind weiterhin:
  - `Inter`
  - `Source Serif 4`
- Zweck:
  - `Inter`: UI, Navigation, Display, Labels, Meta
  - `Source Serif 4`: Lesetext, Karten, Reading-Zonen
- Warum extern bleiben:
  - produktive Nutzung ist real und stabil
  - die aktuelle Typografie ist visuell akzeptiert
  - fruehere lokale Font-Versuche fuehrten laut Projektkontext zu sichtbar abweichender Typografie und schlechterer Wartbarkeit
  - lokales Hosting ist zwar datenschutz- und CSP-seitig sauberer, ist fuer den aktuellen Stand aber keine erzwungene Sofortmassnahme
- CSP-Folge:
  - `fonts.googleapis.com` bleibt fuer das externe Stylesheet noetig
  - `fonts.gstatic.com` bleibt fuer die Fontdateien noetig
- Bedingungen fuer spaetere Lokalisierung:
  - separater kontrollierter Run
  - gleiche oder bewusst dokumentierte Font-Version
  - korrekte Familien und Gewichte
  - Pruefung von Zwischenwerten wie `font-weight: 450`
  - vorher/nachher-Screenshots zentraler produktiver Seiten
  - klare Rollback-Moeglichkeit

## 6. Tests und Checks

Ausgefuehrte Kommandos und Ergebnisse:

- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py -q`
  - `62 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m compileall app`
  - erfolgreich
- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q`
  - `66 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests -q -k "icon or material or snackbar or csp or security_headers or navigation or player"`
  - `113 passed, 361 deselected`

Optionale lokale Checks:

- `ruff check ...`
  - im aktuellen venv nicht verfuegbar
- `mypy ...`
  - im aktuellen venv nicht verfuegbar

## 7. Nicht umgesetzt

- keine Google-Fonts-Lokalisierung
- keine Font-Downloads
- keine Design-System-Migration
- keine breite Icon-Migration
- keine Farbangleichung
- keine Research-Comparison-Inline-SVG-Migration
- keine pauschale typografische Pseudo-Icon-Ersetzung
- keine breite P2-Security-Nacharbeit ausser der reinen Policy-Dokumentation der bewusst externen Google-Fonts-Abhaengigkeit

## 8. Verbleibende nächste Schritte

- optional spaeter: die verbleibenden MD3-Icon-/Top-App-Bar-CSS-Restpfade als eigenen kleinen Totcode- oder Parallelbestand-Run verifizieren
- optional spaeter: Research-Comparison-Inline-SVGs normalisieren, wenn dort ohnehin eine gezielte UI-Politur ansteht
- optional spaeter: typografische Pseudo-Icons nur in einem gezielten Interaktions-Polish-Run vereinheitlichen
- optional spaeter: Google-Fonts-Lokalisierung nur mit kontrollierter Visual-Regression und klarer Rollback-Strategie