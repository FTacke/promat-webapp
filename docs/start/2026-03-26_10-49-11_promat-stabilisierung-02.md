# PROMAT Stabilisierungslauf 02

Run-Zeitpunkt: 2026-03-26 10:49:11 +01:00

## 1. Ziel dieses Runs

Ziel war die Stabilisierung des vorhandenen PROMAT-Bootstraps ohne Feature-Ausbau. Der Fokus lag auf Layout- und CSS-Bereinigung, echter lokaler Dev-Validierung mit PostgreSQL und Auth-Migration, Audit der sichtbaren Navigation/UI sowie Dokumentation des aktuellen Zwischenstands.

## 2. Festgestellte Probleme

- Die Shell referenzierte `app/static/css/layout.css`, die in PROMAT nicht vorhanden war.
- Dadurch fehlte die eigentliche Grid-/Shell-Geometrie zwischen Top-Bar, Drawer, Main und Footer.
- Die Startseite setzte `app-shell--drawerless`, aber diese Klasse hatte ohne Shell-CSS keine Wirkung.
- Der Desktop-Drawer lief dadurch effektiv in den normalen Dokumentfluss und konnte den Startseiteninhalt unnatuerlich weit nach unten schieben.
- `app/static/css/app-tokens.css` wurde geladen, war aber ebenfalls nicht vorhanden.
- Das Core-UI-JavaScript verwendete weiterhin den Titel-Suffix `CO.RA.PAN`.
- Das globale Config-Bootstrapping arbeitete noch unter `__CORAPAN__` und war nach dem Base-Cleanup nur eingeschraenkt angeschlossen.
- Mehrere sichtbare Fehlerseiten waren noch spanisch.
- Die sichtbaren Passwort-Reset-Seiten waren teilweise spanisch; die Reset-Seite verwies zudem in eine in PROMAT aktuell nicht aktivierte Altlogik.
- Die Datenschutzerklaerung enthielt noch CO.RA.PAN-spezifische und fuer PROMAT derzeit unzutreffende Aussagen.
- Der lokale PROMAT-Postgres-Port kollidierte zunaechst mit CORAPAN auf `54320`.
- Im Runtime-Trace fehlte anfangs `data/db/public`.

## 3. Konkret umgesetzte Aenderungen

### Layout- und CSS-Bereinigung

- Neue Shell-Datei `app/static/css/layout.css` angelegt.
- Grid-Struktur fuer `body.app-shell` wiederhergestellt.
- Saubere Trennung von `main` und `footer` hergestellt.
- Desktop-Layout mit linker Drawer-Spalte und rechter Content-Spalte wiederhergestellt.
- `app-shell--drawerless` fuer PROMAT-Startseite jetzt technisch wirksam gemacht.
- `md3-content-wrapper` mit nachvollziehbarem vertikalem Offset unter der fixen Top-Bar versehen.
- Startseiten-CSS vereinfacht und beruhigt:
  - klarer Seiten-Stack statt Hack-Kommentare
  - reduzierter Logo-Bereich
  - konsistentere Abstaende zwischen Logo und Karten
  - geringere Logo-Maximalbreite
  - Entfernen der problematischen `min-width`-Sonderregel im Kartencontainer
- Neue `app/static/css/app-tokens.css` angelegt, damit die Shell ohne 404 geladen wird.

### Shell- und Core-Bereinigung

- `base.html` wieder mit stabilem `data-config` versehen.
- Core-Config-JS auf `__PROMAT__` umgestellt, mit Alias auf `__CORAPAN__` fuer Altkompatibilitaet.
- Core-UI-JS auf `PROMAT` als Dokumenttitel-Suffix umgestellt; alte `CO.RA.PAN`-Suffixe werden beim Bereinigen noch toleriert.

### UI- und Seiten-Bereinigung

- Fehlerseiten `400`, `401`, `403`, `404`, `500` auf deutsche UI-Texte umgestellt.
- `password_forgot.html` auf deutsche PROMAT-Platzhalterlogik umgestellt.
- `password_reset.html` vollstaendig durch eine stabile deutsche Platzhalterseite ersetzt, statt eine derzeit nicht verfuegbare Reset-Altlogik anzustoßen.
- `privacy.html` auf den aktuellen PROMAT-Bootstrap angepasst und irrefuehrende Aussagen zu CO.RA.PAN sowie nicht freigeschalteten Account-Selbstbedienungsfunktionen entfernt.

### Laufumgebung / lokale Dev-Haertung

- Lokalen PROMAT-Postgres-Port konsistent von `54320` auf `54321` umgestellt.
- Betroffene Defaults in Compose, Konfiguration, Dev-Skripten und `.env` angepasst.
- Fehlenden Runtime-Ordner `data/db/public` angelegt.

## 4. Betroffene Dateien

- `c:\dev\promat\app\static\css\layout.css`
- `c:\dev\promat\app\static\css\app-tokens.css`
- `c:\dev\promat\app\static\css\md3\components\index.css`
- `c:\dev\promat\app\templates\base.html`
- `c:\dev\promat\app\templates\pages\index.html`
- `c:\dev\promat\app\static\js\modules\core\config.js`
- `c:\dev\promat\app\static\js\modules\core\ui.js`
- `c:\dev\promat\app\templates\errors\400.html`
- `c:\dev\promat\app\templates\errors\401.html`
- `c:\dev\promat\app\templates\errors\403.html`
- `c:\dev\promat\app\templates\errors\404.html`
- `c:\dev\promat\app\templates\errors\500.html`
- `c:\dev\promat\app\templates\auth\password_forgot.html`
- `c:\dev\promat\app\templates\auth\password_reset.html`
- `c:\dev\promat\app\templates\pages\privacy.html`
- `c:\dev\promat\docker-compose.dev-postgres.yml`
- `c:\dev\promat\app\scripts\dev-setup.ps1`
- `c:\dev\promat\app\scripts\dev-start.ps1`
- `c:\dev\promat\app\src\app\config\__init__.py`
- `c:\dev\promat\app\.env.example`
- `c:\dev\promat\.github\workflows\ci.yml`
- `c:\dev\promat\data\db\public`

## 5. Ergebnis der Layout-/CSS-Bereinigung

- Die fehlende Shell-Geometrie ist wieder vorhanden.
- Drawer, Main und Footer greifen wieder systematisch ineinander.
- Die Startseite hat jetzt einen klaren, ruhigeren Vertikalaufbau innerhalb des bestehenden Systems.
- `app-shell--drawerless` funktioniert fuer die Startseite auf Desktop nun wirklich.
- Die Seite hat keinen offensichtlichen toten Shell-Asset-Request mehr.
- Die Startseiten-Assets wurden nach dem Fix erneut geprueft; es blieben keine nicht erreichbaren lokalen Asset-URLs uebrig.

## 6. Ergebnis des realen Postgres-/Auth-Checks

### Reale lokale Dev-Umgebung

- PROMAT-Postgres lokal aktiv auf `127.0.0.1:54321`
- Flask-App lokal aktiv auf `http://127.0.0.1:8000/`

### Durchgefuehrte reale Checks

- `docker compose`-basierter Dev-Postgres geprueft und genutzt
- Auth-Migration gegen PostgreSQL erfolgreich ausgefuehrt
- Analytics-Migration erfolgreich ausgefuehrt
- initialer Admin erfolgreich erstellt bzw. aktualisiert
- `GET /health` erfolgreich
- `GET /` erfolgreich
- geschützte Route vor Login erfolgreich gesperrt (`303`)
- Login mit lokalem Admin erfolgreich
- geschützte Route nach Login erfolgreich (`200`)
- Admin-Platzhalterroute mit Admin-Session erfolgreich (`200`)
- Logout erfolgreich
- geschützte Route nach Logout erneut gesperrt (`303`)
- Runtime-Pfade mit echter Dev-Konfiguration geprueft und nach Anlegen von `data/db/public` vollstaendig auf `OK`

## 7. Navigation-, UI- und Seiten-Audit

### Gepruefte sichtbare Routen

Alle folgenden öffentlichen Routen antworteten erfolgreich mit `200`:

- `/`
- `/projekt/uebersicht`
- `/projekt/design`
- `/projekt/wer-wir-sind`
- `/projekt/zitieren`
- `/projekt/referenzen`
- `/korpus`
- `/korpus/metadaten`
- `/atlas`
- `/impressum`
- `/datenschutz`
- `/login`

### Audit-Ergebnis

- Navigation war im funktionalen Oberflächenpfad ohne offensichtliche HTTP-Brüche.
- UI-Chrome wurde weiter in Richtung konsistentes Deutsch bereinigt.
- Sichtbare Fehlerseiten sind nicht mehr spanisch.
- Die Passwort-Reset-Strecke erzeugt keine sichtbare defekte Altinteraktion mehr, sondern einen klaren Platzhalter.
- Die Startseiten-Shell referenziert keine fehlenden lokalen Assets mehr.

## 8. Verbleibende offene Punkte

- Mehrere übernommene inhaltliche Strukturträgerseiten enthalten weiterhin spanische Inhalte und CO.RA.PAN-Bezüge. Das war für diesen Run akzeptiert, sollte aber später selektiv redaktionell überarbeitet werden.
- Einige nicht sichtbare oder derzeit nicht angebundene Legacy-JS-Dateien und Kommentare enthalten weiterhin CORAPAN-Bezeichnungen.
- Die Reset-/Selbstbedienungsfunktionen sind bewusst noch nicht implementiert; die Oberfläche dafür ist jetzt nur stabilisiert und enttäuscht nicht mehr mit einer defekten Aktion.
- Ein visuelles Browser-Screenshot-/Pixel-Audit wurde in diesem Run nicht automatisiert erzeugt; die Layout-Bereinigung basiert auf Shell-Struktur, Asset-Checks und realem HTTP-/Auth-Lauf.

## 9. Empfohlener naechster Schritt

Im nächsten Run sollte die redaktionelle und fachliche Bereinigung der übernommenen Strukturträgerseiten erfolgen:

- Projekt/Korpus/Datenschutz inhaltlich auf PROMAT umstellen
- verbliebene CORAPAN-Begriffe in sichtbaren Texten reduzieren
- nicht mehr benoetigte Legacy-JS/CSS-Reste systematisch entfernen, soweit sie im PROMAT-Bootstrap nicht mehr referenziert werden

## Zusatz: AGENTS / .github

- In diesem Run wurden `AGENTS.md` und `.github` nicht weiter angepasst.
- Bereits frueher geaenderte `.github`-Dateien wurden nur insofern beruehrt, als der lokale PROMAT-Dev-Port in der CI-Konfiguration auf `54321` konsistent gehalten wurde.
