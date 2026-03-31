# PROMAT Bootstrap Run 01

Datum: 2026-03-26

## Ziel

Erster selektiver PROMAT-Bootstrap auf Basis der zuvor analysierten CORAPAN-Struktur, aber ohne Volluebernahme und ohne Rueckgriff auf BlackLab, Search, Player, Editor oder Atlas-Implementierung.

## Umgesetzter Stand

- PROMAT-spezifische App-Fabrik, Konfiguration und Runtime-Pfade aufgebaut.
- Runtime-Namensraum von CORAPAN auf `PROMAT_RUNTIME_ROOT` und `PROMAT_MEDIA_ROOT` umgestellt.
- Minimale Blueprints fuer `public`, `auth` und `admin` angelegt.
- Root- und App-Skripte fuer lokales Setup und Start vorbereitet.
- Root-Compose fuer lokales Postgres sowie App-Compose fuer produktionsnahe Struktur angelegt.
- Root- und App-`AGENTS.md` sowie `.github`-Grundlagen erstellt.
- Uebernommene Shell-Templates auf PROMAT reduziert und auf deutsche UI-Chrome umgestellt.
- Navigation, Top-Bar und Footer auf den schlanken PROMAT-Schnitt angepasst.
- Startseite auf drei Karten reduziert: Projekt, Korpus, Atlas-Platzhalter.
- Platzhalterseiten für Korpus-Metadaten, Atlas, geschützten Bereich und Admin-Dashboard angelegt.
- Einfache PROMAT-SVG-Assets fuer Favicon, Badge und Wordmarks angelegt.
- Index-Logo auf `app/static/img/promat.png` umgestellt und mit Border-Radius versehen.
- Diverse Altlasten aus JS/CSS entfernt, insbesondere fuer Search, Player, Editor, Atlas- und Statistik-Module.
- Startseite auf einen eigenen Landing-Template-Typ umgestellt.
- Die Landing-Startseite rendert ohne Top-Bar und ohne Seitenpanel, aber mit unveraendertem Footer.
- Der Einstieg arbeitet jetzt mit einer zentrierten Wordmark, kurzem Intro und genau zwei Entry-Cards im Bild-oben-Layout fuer Forschung und Unterricht.

## Bewusst nicht enthalten

- Keine BlackLab-Anbindung.
- Keine Suchoberfläche mit CQL, DataTables, Select2 oder HTMX-getriebenem Suchworkflow.
- Kein Player.
- Kein Editor.
- Keine echte Atlas-Funktion.
- Keine Volluebernahme des Admin-Stacks.

## Verifikation

### Statische Pruefung

- VS-Code-Fehlerpruefung fuer `c:\dev\promat\app`: keine Fehler gefunden.

### Laufzeittest

Die App-Fabrik wurde erfolgreich mit einer minimalen Testdatenbank gestartet.

Verwendeter Test:

- Python-Environment: `c:/dev/.venv/Scripts/python.exe`
- Arbeitsverzeichnis: `c:\dev\promat\app`
- Test-DB: temporaere SQLite-Datei unter `c:\dev\promat\tmp\promat-bootstrap-test.sqlite3`
- Vor dem Start wurde eine minimale Tabelle `users` angelegt, da die App den Auth-Schema-Check absichtlich hart voraussetzt.

Ergebnis:

- `create_app('testing')` erfolgreich
- `app.name == 'app'`
- `routes == 25`

Wichtiger Befund:

- Ohne initialisiertes Auth-Schema startet die App absichtlich nicht.
- Das ist korrekt und gewollt.
- Fuer lokalen Realbetrieb muss vor dem Start die Auth-Migration gegen die Ziel-Datenbank ausgefuehrt werden.

### Reeller lokaler Dev-Start

Im Anschluss wurde der lokale Dev-Start gegen eine echte PROMAT-Postgres-Instanz erfolgreich ausgefuehrt.

Wichtige Anpassung:

- Der lokale PROMAT-Dev-Port fuer Postgres wurde von `54320` auf `54321` verschoben, damit PROMAT parallel zu CORAPAN laufen kann.

Erfolgreich durchgefuehrt:

- `docker compose` fuer `promat_auth_db`
- Auth-Migration gegen PostgreSQL
- Anlage des initialen Admin-Benutzers `admin`
- Start des Flask-Dev-Servers
- HTTP-Check auf `http://127.0.0.1:8000/` mit Status `200`

Aktueller lokaler Startzustand:

- Datenbank: `127.0.0.1:54321`
- Webapp: `http://127.0.0.1:8000/`

## Lokaler Startpfad

Geplanter lokaler Start bleibt:

1. Root-Postgres starten ueber `docker-compose.dev-postgres.yml`
2. App-Setup ausfuehren ueber `scripts/dev-setup.ps1`
3. App starten ueber `scripts/dev-start.ps1`

Voraussetzung:

- `AUTH_DATABASE_URL` muss auf die lokale PROMAT-Auth-Datenbank zeigen.
- Die Auth-Migration muss erfolgreich angewendet sein.

Praktisch gilt jetzt standardmaessig:

- `AUTH_DATABASE_URL=postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:54321/promat_auth`

## Offene Naechstpunkte

- Echte Inhalte fuer interne Admin- und Analysepfade spaeter selektiv ergaenzen.
- Passwort-Reset- und weitere Auth-Seiten ggf. ebenfalls sprachlich und funktional auf PROMAT nachziehen.
- Optionales Feintuning der Branding-Texte und der SVG-Assets.
- Reale End-to-End-Pruefung mit lokalem Postgres-Container und Auth-Migration ausfuehren.
