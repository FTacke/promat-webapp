# PROMAT Architecture Audit

Datum: 2026-04-27
Scope: produktive Flask-Webapp, Runtime-Wiring, Research-Zugangsarchitektur, Auth-Flows, i18n- und UI-naher Python-Layer
Artefakttyp: nicht-normativer Auditbericht

## Executive Summary

Der aktuelle Stand ist fuer ein fruehes produktives Forschungswerkzeug technisch tragfaehig, aber nicht in einem Zustand, den ich fuer eine spaetere produktive Verarbeitung geschuetzter Forschungsdaten, personenbezogener Daten und mehrsprachiger Workbench-Nutzung ohne weitere Architekturhaertung freigeben wuerde.

Die staerksten Architekturmerkmale sind die saubere Zentralisierung der Research-Capability-Semantik in `app/src/app/research_capabilities.py`, die klare dateibasierte Runtime fuer Research-Sessions unter `data/sessions/{language}/{session_id}/metadata.json` und die im Kern saubere Trennung zwischen oeffentlichem Bereich, geschuetzter Research-Flaeche und owner-gebundenem Set-API-Modell.

Die groessten Risiken liegen nicht in einem einzelnen Totalausfall, sondern in produktiver Drift zwischen Schichten:

- aktiver Frontend-Bootstrap fuer Token-Refresh ist mit einem Backend ohne `/auth/refresh` verdrahtet
- `app/src/app/__init__.py` enthaelt ueberlappende Alt- und Neudefinitionen fuer Error-Handling und Logging
- die i18n-Strategie ist nicht konsistent zentral, sondern lebt parallel in `translate(...)`, lokalen `if ui_lang == "de"`-Aesten und statischen Zweisprach-Mappings
- mehrere produktive Templates enthalten sichtbar hartcodierte deutsche UI-Texte trotz verbindlicher Regel fuer die gemeinsame Uebersetzungsschicht

Gesamturteil: mittlere bis gute Strukturreife im Research-Kern, aber deutlicher Bereinigungs- und Konsolidierungsbedarf an den Integrationsgrenzen.

## Bewertungsraster

- Architekturtragfaehigkeit: mittel bis gut
- Konsistenz zwischen Schichten: mittel
- Wartbarkeit: mittel
- Governance-Konformitaet der Implementierung: mittel bis schwach
- Produktive Reife fuer spaetere Hochsicherheits- und Langzeitpflege: aktuell nicht ausreichend

## Positive Architekturmerkmale

### 1. Zentrale Research-Capability-Schicht

`app/src/app/research_capabilities.py` bildet sichtbar den staerksten Teil der Gesamtarchitektur.

Positiv:

- page slugs, task subsets, compare-Faehigkeit, set-filter-Faehigkeit und render-mode-Vokabular sind zentral beschrieben
- die zugehoerige Spec unter `docs/spec/research-capabilities.md` ist inhaltlich klar gespiegelt
- die Research-IA ist dadurch prinzipiell erweiterbar, ohne neue Parallelvokabulare zu erzwingen

Bewertung: starker Kern, der gegen weitere Drift aktiv verteidigt werden sollte.

### 2. Klare Research-Runtime-Grenzen

Die Session-Runtime ist dateibasiert und fuer den aktuellen Reifegrad gut nachvollziehbar.

Positiv:

- Sessions kommen aus `data/sessions/{language}/{session_id}/metadata.json`
- Player-/Phenomena-Konfiguration liegt getrennt unter `data/config/research_player/{language}/`
- der Set-/Workbench-Zustand ist als owner-gebundenes Persistenzmodell sauber vom dateibasierten Corpus-Layer getrennt

Bewertung: gute Nachvollziehbarkeit und geringer Magieanteil.

### 3. Public/Protected-Trennung im Routing

Die dokumentierte Regel, dass unter `/{ui_lang}/research/{corpus}` nur `design` oeffentlich bleibt und alle weiteren Research-Seiten vor dem Rendern gated werden, ist architektonisch sinnvoll und im gelesenen Codepfad sichtbar angelegt.

Bewertung: fachlich richtig und fuer spaeteren produktiven Betrieb unverzichtbar.

## Kritische Findings

### A1. Aktiver Auth-Refresh-Drift zwischen Frontend und Backend

Prioritaet: P1

Befund:

- `app/static/js/main.js` initialisiert aktiv `initAuthRefresh()` aus `app/static/js/modules/auth/refresh.js`
- sowohl `app/static/js/modules/auth/refresh.js` als auch `app/static/js/modules/auth/token-refresh.js` rufen `/auth/refresh` auf
- im Python-Routing wurde keine entsprechende Route gefunden

Architekturwirkung:

- der Frontend-Bootstrap geht von einer Token-Lifecycle-Architektur aus, die serverseitig nicht vorhanden ist
- das ist kein totes Experiment am Rand, sondern aktives Runtime-Wiring
- dadurch existiert ein unausgesprochener Betriebszustand, in dem Sessionablauf, 401-Recovery und Nutzerfeedback nicht vertragssicher sind

Risiko:

- unerwartete Logout-/Ablaufzustaende
- inkonsistentes Verhalten zwischen HTML-Navigation, API-Requests und spaeteren JS-Workbenches
- technische Schulden an einer hochkritischen Systemgrenze

Empfehlung:

1. Auth-Strategie explizit entscheiden: echtes Refresh-Token-Modell oder bewusst kein Refresh-Endpoint.
2. Die nicht mehr kanonische Seite vollstaendig entfernen, nicht nur still ignorieren.
3. Die Entscheidung in Spec plus Testabdeckung sichtbar machen.

### A2. `app/src/app/__init__.py` enthaelt konkurrierende Altlogik

Prioritaet: P1

Befund:

- `register_error_handlers` ist einmal als klarer zentraler Block vorhanden
- spaeter im selben File existieren weitere `@app.errorhandler(...)`-Definitionen
- `setup_logging` ist zweimal definiert
- der spaetere Block referenziert weiterhin Legacy-Sprache und Legacy-Produktnamen wie `CO.RA.PAN`

Architekturwirkung:

- das Factory-File traegt nicht nur Setup-Logik, sondern konserviert alte Architekturspuren
- unklarer effektiver Kontrollpfad bei Fehlerbehandlung und Logging
- erhoehtes Risiko, dass Aenderungen an der vermeintlich kanonischen Stelle nicht die tatsaechlich aktive Stelle treffen

Risiko:

- Fehlverhalten in Fehlerseiten oder JSON-Fehlerantworten
- uneinheitliche Logdateinamen und Logformate
- hoehere Eintrittswahrscheinlichkeit fuer Regressionen bei Security- oder Auth-Aenderungen

Empfehlung:

1. `__init__.py` auf einen kanonischen Error-Handling- und Logging-Pfad reduzieren.
2. Tote oder ueberholte Legacy-Blcke entfernen statt nebenher bestehen lassen.
3. Danach gezielte Smoke-Tests fuer HTML- und API-Error-Pfade ergaenzen.

### A3. i18n ist nur teilweise zentralisiert

Prioritaet: P1

Befund:

Es existieren mindestens drei nebeneinander laufende Muster:

- zentrale Uebersetzung ueber `translate(...)` / `translate_many(...)`
- lokale Zweisprach-Mappings im Python-Code, z. B. in `app/src/app/research_views.py`
- direkte Sprachzweige wie `"Geschlecht" if ui_lang == "de" else "Gender"`

Architekturwirkung:

- sichtbare UI-Texte werden nicht konsistent ueber die gemeinsame Uebersetzungsschicht gesteuert
- Pflege und Aenderung von Wortwahl, Terminologie und Bilingualitaet verteilen sich auf mehrere Muster
- Governance-Regeln gegen Hardcodings und lokale de/en-Branches werden dadurch bereits im produktiven Code verletzt

Risiko:

- Terminologiedrift zwischen Oberflaechen
- hoehere Kosten fuer Copy- oder Terminologieaenderungen
- erhoehte Wahrscheinlichkeit, dass `de` und `en` auseinanderlaufen

Empfehlung:

1. `research_views.py` als prioritaeren Konsolidierungskandidaten behandeln.
2. Sichtbare Labels systematisch in die zentrale i18n-Schicht ueberfuehren.
3. Kuenftig lokale `if ui_lang == ...`-Visible-Copy-Pfade als Architekturfehler behandeln.

### A4. Produktive Templates enthalten sichtbare Hardcodings

Prioritaet: P1

Befund:

Mehrere produktive Templates sind nicht zentral uebersetzt, unter anderem:

- `app/templates/errors/401.html`
- `app/templates/errors/404.html`
- `app/templates/partials/footer.html`

Architekturwirkung:

- Finished surfaces shippen nicht sauber in `de` und `en`
- die Implementierung verletzt die eigene Repo-Regel fuer sichtbare UI-Strings in Templates
- Shared-Komponenten wie Footer und Error-Seiten werden dadurch zu Sprach- und Konsistenzlecks fuer die gesamte App

Risiko:

- inkonsistente Bilingualitaet
- spaetere UI-Refactorings muessen sichtbare Copy ueber viele Templates nachziehen
- erschwerte internationale Produktpflege

Empfehlung:

1. Footer und Error-Seiten in die gemeinsame Uebersetzungsschicht ziehen.
2. Shared Partials als erste harte No-Hardcoding-Zone definieren.
3. Sichtbare Template-Hardcodings mit gezielter Suche regelmaessig auditieren.

## Weitere relevante Findings

### A5. Public-Page-Content ist gross, aber strukturiert

Prioritaet: P2

`app/src/app/routes/public_page_content_data.py` enthaelt grosse Mengen zweisprachiger Langform-Inhalte. Das ist als inhaltliche Datenquelle fuer redaktionelle Projektseiten vertretbar, weil es sich um strukturierte Payloads und nicht um UI-Builder-Branches handelt.

Bewertung:

- fachlich akzeptabel
- aber langfristig nur dann wartbar, wenn die Abgrenzung zu translatabler UI-Copy sauber bleibt

### A6. Research-Views sind zu einem Multi-Responsibility-Modul angewachsen

Prioritaet: P2

`app/src/app/research_views.py` kombiniert Label-Mappings, Filter-Builder, Profil-View-Modelle, Vergleichslogik und Teile der Praesentationssemantik.

Risiko:

- hohe kognitive Last
- schwierige Testbarkeit einzelner Teilverantwortungen
- weitere Drift zwischen Capability-, Session- und View-Layer wahrscheinlicher

Empfehlung:

- mittelfristig in klarere Builder-/Formatter-/Label-Module aufteilen
- zuerst die Copy-/Label-Schicht abspalten

### A7. Dateibasierte Session-Runtime ist robust, aber nicht beliebig skalierbar

Prioritaet: P2

Der dateibasierte Runtime-Ansatz ist fuer die aktuelle Projektphase sinnvoll. Fuer spaetere groeßere Mengen, feinere Zugriffsauswertung und detaillierte Auditability kann diese Struktur jedoch an Grenzen kommen, wenn sie ohne zusaetzliche Index- oder Cache-Strategien weiterwaechst.

Bewertung:

- aktuell angemessen
- spaetere Skalierung und Admin-/Audit-Anforderungen fruehzeitig mitdenken

## Architektur-Risiko fuer Produktionsreife

Vor einem harten produktiven Sicherheits- oder Datenschutz-Deployment wuerde ich mindestens folgende Punkte als Blocker behandeln:

1. Auth-Refresh-Architektur entscheiden und konsolidieren.
2. `__init__.py` auf einen einzigen aktiven Setup-/Error-/Logging-Pfad bereinigen.
3. sichtbare UI-Copy auf die zentrale Uebersetzungsschicht zurueckholen.
4. Shared-Templates und Error-Seiten bilingual und governance-konform machen.

## Empfohlene Reihenfolge

### Phase 1: Integrationsgrenzen stabilisieren

- Auth-Refresh-Entscheidung treffen
- aktives Frontend/Backend-Wiring angleichen
- Error-/Logging-Duplikate in `__init__.py` entfernen

### Phase 2: i18n und Shared UI haerten

- Error-Seiten, Footer, Shared Partials und zentrale Builder von Hardcodings befreien
- lokale Sprachzweige in `research_views.py` abbauen

### Phase 3: Modulgrenzen nachziehen

- `research_views.py` in kleinere Verantwortungen zerlegen
- groessere View-Modelle staerker an Capability- und Session-Kern anbinden

## Audit-Fazit

PROMAT hat keinen chaotischen Kern. Der Research- und Routing-Unterbau ist sichtbar von aktiven Specs gepraegt und in wichtigen Teilen sauberer als viele Projekte dieser Reifephase. Die produktive Reife wird derzeit vor allem durch Altlasten, Integrationsdrift und inkonsistente i18n-/UI-Disziplin begrenzt, nicht durch einen falschen Grundansatz.

Wenn die genannten P1-Bloecke bereinigt werden, ist die bestehende Architektur gut genug, um darauf kontrolliert weiter zu haerten. Ohne diese Bereinigung bleibt der spaetere Produktivbetrieb unnoetig fragil.