# Repo-Implementierungsplan: `player`, `comparison`, `phenomena`, Presets und Sets

Datum: 2026-04-08

## Zweck

Dieses Dokument leitet aus [docs/plans/player_comparison_phenomena.md](c:\dev\promat\docs\plans\player_comparison_phenomena.md) einen repo-konkreten Umsetzungsplan ab. Es beschreibt den tatsächlichen Ist-Zustand des Repos, die Konflikte zu den aktiven Specs, die Zielarchitektur im bestehenden PROMAT-Stack und eine belastbare Phasierung fuer die naechsten Implementierungsruns.

Der Arbeitsbeschluss unter `docs/plans/player_comparison_phenomena.md` bleibt die fachliche Zielreferenz. Die aktiven Produktregeln liegen weiterhin in `docs/spec/`.

## A. Repo-Audit

### 1. Routing und Page-Struktur

- Die Research-Seiten laufen aktuell ueber [app/src/app/routes/public.py](c:\dev\promat\app\src\app\routes\public.py).
- Die kanonische Player-Route `/{ui_lang}/research/{language}/player/{session_id}/{task}` ist implementiert.
- `speakers`, `recordings` und das Profil sind datengetrieben.
- `comparison` und `phenomena` existieren als Research-Seitenroute bereits im IA-Schema, werden aktuell aber nur als Platzhalterinhalt aus [app/src/app/routes/public_content.py](c:\dev\promat\app\src\app\routes\public_content.py) gebaut.
- Es gibt noch keine eigene Vergleichs-Workbench-Route-Logik jenseits der Platzhalterseite.
- Es gibt noch keine datengetriebene Preset-/Phenomena-Seite.

### 2. Aktueller Player-Zuschnitt

- Der Player wird in [app/src/app/research_views.py](c:\dev\promat\app\src\app\research_views.py) durch `build_player_page(...)` aufgebaut.
- Das produktive UI liegt in [app/templates/pages/research_player.html](c:\dev\promat\app\templates\pages\research_player.html).
- Das interaktive Verhalten liegt in [app/static/js/pages/research-player.js](c:\dev\promat\app\static\js\pages\research-player.js).
- Die aktuelle Player-Implementierung ist real nur fuer `wordlist` fertig. `text` und `interview` bleiben im Task-Switch sichtbar, rendern aber bewusst als unavailable/future state.
- Der bestehende Compare-Pfad im Player ist ein gebundener `1 + 1`-Vergleich mit optionalem `compare_session` und optionalem `compare_mode=manual`.
- Die Compare-Logik ist derzeit eng in den Player eingebacken: Datenaufbereitung, Template-Struktur und JS-Interaktion sind nicht als eigenstaendige Mehrfachvergleichs-Workbench abstrahiert.

### 3. Wo steckt heute Compare-Logik?

- Die einzige produktive Compare-Logik steckt aktuell im Player.
- Datenlogik:
  - Laden compare-faehiger Sessions und Bundles in [app/src/app/research_views.py](c:\dev\promat\app\src\app\research_views.py)
  - Query-Kontext nur ueber `compare_session` und `compare_mode`
- Template-Logik:
  - Compare-Panel, Summary-Cards und duale Listen in [app/templates/pages/research_player.html](c:\dev\promat\app\templates\pages\research_player.html)
- Client-Logik:
  - Vergleich oeffnen/schliessen, sequenzielles Item-Abspielen, History-URL-Sync in [app/static/js/pages/research-player.js](c:\dev\promat\app\static\js\pages\research-player.js)
- Es gibt keine eigenstaendige `comparison`-seitige Sessionauswahl, kein wiederbearbeitbares Selection-Tray und keinen item-zentrierten Mehrfachvergleich ausserhalb des Players.

### 4. Forschungsseiten, Loader und Query-State

- Session- und Persondaten werden dateibasiert aus `data/sessions/{language}/{session_id}/metadata.json` geladen.
- Die zentrale Leseschicht dafuer ist [app/src/app/research_sessions.py](c:\dev\promat\app\src\app\research_sessions.py).
- Diese Schicht liefert bereits brauchbare Grundlagen fuer spaetere Workbenches:
  - `SessionRecord` und `PersonRecord`
  - Task-Verfuegbarkeit
  - Session-/Person-Filter
  - Sortierung und Matching
- Es gibt bereits etablierte URL-Query-Muster fuer Research-Kontext (`source`, `compare_session`, `compare_mode`, session focus), aber noch kein `set_id`- oder `preset_id`-Handling im Runtime-Code.
- Es gibt noch keinen gemeinsamen Loader fuer `player_config.json`, `phenomena_presets.json` oder taskuebergreifende Item-Referenzen.

### 5. Vorhandene Konfigurations- und Datenbausteine

- Unter [data/config/research_player/spanish/task_catalogs](c:\dev\promat\data\config\research_player\spanish\task_catalogs) liegen bereits kanonische Task-Kataloge fuer `wordlist` und `text`.
- `wordlist.json` und `text.json` liefern bereits stabile `task + item_id`-Referenzen, die als Fundament fuer Presets und Sets geeignet sind.
- Der Repo-Stand enthaelt derzeit jedoch noch keine eingecheckten Dateien fuer:
  - `data/config/research_player/spanish/player_config.json`
  - `data/config/research_player/spanish/phenomena_presets.json`
- Damit existiert die in den Specs bereits genannte Preset-/Config-Struktur im Repo noch nicht produktiv.

### 6. DB-, User- und Security-Stand

- PostgreSQL ist im Repo bereits fuer die Auth/Core-Datenbank angeschlossen:
  - [docker-compose.dev-postgres.yml](c:\dev\promat\docker-compose.dev-postgres.yml)
  - [app/infra/docker-compose.prod.yml](c:\dev\promat\app\infra\docker-compose.prod.yml)
- Die SQLAlchemy-Engine ist generisch verfuegbar ueber [app/src/app/extensions/sqlalchemy_ext.py](c:\dev\promat\app\src\app\extensions\sqlalchemy_ext.py).
- Vorhandene ORM-Modelle sind aktuell auth-spezifisch in [app/src/app/auth/models.py](c:\dev\promat\app\src\app\auth\models.py): `users`, `refresh_tokens`, `reset_tokens`.
- Vorhandene Migrationen sind aktuell:
  - [app/migrations/0001_create_auth_schema_postgres.sql](c:\dev\promat\app\migrations\0001_create_auth_schema_postgres.sql)
  - [app/migrations/0002_create_analytics_tables.sql](c:\dev\promat\app\migrations\0002_create_analytics_tables.sql)
- Es gibt noch keine Tabellen fuer Research-Sets, Preset-Ableitungen oder vergleichsbezogene User-Zustaende.
- Wichtig fuer die Zielarchitektur: Die Research-Routen selbst sind aktuell nicht per `jwt_required()` geschuetzt. Die Seitenmodelle tragen zwar `access: protected`, die Public-Blueprint-Routen fuer Research und Player erzwingen das aber derzeit nicht.

### 7. Tests und dokumentierter Ist-Stand

- [app/tests/test_research_sessions.py](c:\dev\promat\app\tests\test_research_sessions.py) deckt bereits viel vom aktuellen Research-Iststand ab:
  - dateibasierte Session-/Person-Loader
  - Profil- und Recordings-Zuschnitt
  - produktive `wordlist`-Player-Ansicht
  - bounded compare innerhalb des Players
- Es gibt noch keine Tests fuer:
  - datengetriebene `comparison`-Seite
  - datengetriebene `phenomena`-Seite
  - Preset-Loader
  - Set-API / Set-Persistenz
  - `text` in Comparison

### 8. Bereits teilweise umgesetzt vs. noch komplett offen

Bereits teilweise umgesetzt:

- task-spezifische Player-Route
- bounded Direct-Compare im Player
- dateibasierte Session-/Task-Grundlage
- kanonische `task + item_id`-Kataloge fuer `wordlist` und `text`
- Postgres/Auth-Stack und generische DB-Session-Infrastruktur

Noch komplett offen:

- datengetriebene `comparison`-Workbench
- datengetriebene `phenomena`-Preset-/Auswahlseite
- file-backed `player_config.json`
- file-backed `phenomena_presets.json`
- serverseitiges `set`-Modell in Postgres
- API fuer Drafts/Sets
- `set_id`-/`preset_id`-Uebergabelogik
- persistente, wieder bearbeitbare Comparison-Konfiguration
- auth-erzwungene Ownership fuer Research-Arbeitszustaende

## B. Konfliktanalyse der Specs

### 1. `docs/spec/research-access.md`

Zu eng oder veraltet:

- Die Formulierung, `player` sei die gemeinsame Workbench fuer Playback-, Preset- und Comparison-Kontexte, ist zu breit. Der neue Arbeitsbeschluss trennt `player`, `comparison` und `phenomena` fachlich sauber.
- Die Aussage, `comparison` sei nur spaeterer Player-Kontext, ist ueberholt. `comparison` ist laut Arbeitsbeschluss eine eigenstaendige item-zentrierte Workbench.
- Die Aussage, Comparison sei nur optionale Player-Erweiterung und nie separate Routefamilie, ist fuer die Zielarchitektur zu eng. Der bounded Direct-Compare im Player bleibt, aber die Research-Seite `comparison` bleibt eine eigenstaendige Route mit eigener Verantwortung.

Beibehaltbar:

- `speakers` person-zentriert
- `recordings` session-/task-zentriert
- kanonische Player-Route
- einheitliche Task-Verfuegbarkeit und Profilsemantik

Notwendige Spec-Anpassung:

- `comparison` als first-class Research-Workbench-Seite
- `phenomena` als kuratierte Auswahl- und Launcher-Seite
- `player` nur noch als session-zentrierte Detailansicht mit bounded Direct-Compare

### 2. `docs/spec/research-player.md`

Zu eng oder veraltet:

- Die Formulierung, Comparison sei nur bounded extension des Players, ist nur noch fuer Direct-Compare im Player richtig, nicht fuer die eigenstaendige `comparison`-Seite.
- Die Formulierung, Phenomena-Presets seien bounded extension derselben Player-Base, ist zu eng. `phenomena` ist eine eigene kuratierte Seite und nicht nur Player-Kontext.
- Das optionale Query-Modell kennt `preset_id`, aber noch kein `set_id`.
- Die bisherige Regel, manuelle Preset-Erweiterungen lebten nur im aktiven Player-State, kollidiert mit der neuen Vorgabe serverseitiger, usergebundener Sets in Postgres.
- Die Spec trennt noch nicht sauber zwischen `preset_id` als kuratierter Vorlage und `set_id` als kanonischem User-Arbeitskontext.

Beibehaltbar:

- genau eine kanonische Player-Route
- kein `mixed`-Task im Pfad
- gemeinsamer modularer Player fuer `wordlist`, `text`, `interview`
- bounded `compare_session` im Player
- media delivery unter derselben Player-Familie
- taskuebergreifende Presets duerfen gemischte Items enthalten

Notwendige Spec-Anpassung:

- `set_id` als neuer Player-Kontext
- Prioritaetsregel `set_id` vor `preset_id`
- klare Trennung zwischen standalone `comparison` und bounded Direct-Compare im Player
- klares Set/Preset/Lifecycle-Modell fuer aktive User-Arbeit

### 3. `docs/spec/platform-data-files.md`

Weitgehend kompatibel:

- `comparison` und `phenomena` sind bereits als aktive Research-Pages vorgesehen.
- Die Player-Detailroute bleibt task-spezifisch.
- `mixed` ist bereits nicht als Taskwert vorgesehen.

Noetige Klarstellung:

- `comparison` und `phenomena` bleiben eigenstaendige Research-Page-Routen und werden nicht in alternative Player-Pfade umgebogen.
- gemischte Sets bleiben Zustand/Query/Server-State, nicht Pfadlogik.

### 4. Verbindlich aufzunehmende Begriffe

- `set_id`
- `draft`
- `saved`
- `source_preset_id`
- `preferred_task`
- `comparison` als item-zentrierte Workbench
- `phenomena` als kuratierte Auswahl- und Launcher-Seite
- bounded `direct compare` im Player als getrennte Begrifflichkeit zur standalone `comparison`

## C. Zielarchitektur fuer die Umsetzung im Repo

### 1. Routen

`player`

- Route bleibt unveraendert: `/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}`
- Erlaubte Taskwerte bleiben ausschliesslich `wordlist`, `text`, `interview`.
- Kein `mixed`-Task, keine neue Player-Routefamilie.

`comparison`

- Nutzt die bestehende Research-Page-Route: `/{ui_lang}/research/{corpus_language}/comparison`
- Kanonischer Arbeitskontext ueber Query `set_id`
- Zusaetzliche, UI-bezogene Querys spaeter nur fuer lesbare Ansichtszustaende, z. B. `view_task=all|wordlist|text`

`phenomena`

- Nutzt die bestehende Research-Page-Route: `/{ui_lang}/research/{corpus_language}/phenomena`
- Preset-Auswahl ueber `preset_id`
- Bereits bestehende User-Arbeit optional ueber `set_id`
- Kanonisch bleibt: Preset ansehen oder editieren auf `phenomena`, hoeren auf `player` oder `comparison`

### 2. Handhabung von `set_id`, `preset_id` und `preferred_task`

- `preset_id` identifiziert eine zentrale, file-backed kuratierte Vorlage.
- `set_id` identifiziert die aktive usergebundene Arbeitsmenge in Postgres.
- Sobald von einer Preset-Ansicht in aktive Arbeit gewechselt wird, wird ein Draft-Set erzeugt oder wiederverwendet; ab diesem Punkt ist `set_id` der kanonische Arbeitsbezug.
- Wenn `set_id` und `preset_id` gleichzeitig vorhanden sind, gewinnt `set_id` fuer die konkrete Auswahl; `preset_id` bleibt nur Provenienzkontext.
- `preferred_task` wird am Set gespeichert und von `phenomena` oder `comparison` genutzt, um den initialen Player-Task zu bestimmen.
- `preferred_task` wird nicht zum neuen Player-Pfadsegment und muss nicht als dauerhafter Player-Queryparameter normiert werden.

### 3. Verhalten von `phenomena`

- `phenomena` laedt file-backed Presets.
- Das Oeffnen eines Presets zeigt eine editierbare Itemliste mit taskuebergreifenden Referenzen.
- Entfernen/Hinzufuegen von Items aendert nicht das Preset selbst, sondern das aktive Set.
- `phenomena` bietet zwei Verzweigungen:
  - Oeffnen in `comparison` mit `set_id`
  - Oeffnen in `player` mit `set_id`, `session_id` und taskgebundener Zielroute

### 4. Verhalten von `comparison`

- `comparison` ist item-zentriert und nicht task-first.
- Die Seite arbeitet mit einer aktiven Itemmenge aus dem Set.
- `wordlist` und `text` duerfen im selben Set vorkommen.
- Die UI darf nach Task gruppieren oder filtern, aber nicht die Existenz des Sets vom Task trennen.
- Sessionauswahl und Sessionentfernung bleiben auf derselben Seite bearbeitbar.
- Die persistente Arbeitsgrundlage bleibt `set_id`; die aktuelle Sessionkonfiguration wird mit demselben Set-Aggregat gespeichert.

### 5. Verhalten von `player`

- `player` bleibt session-zentriert.
- `set_id` filtert die sichtbaren Items taskgebunden auf den fuer den aktuellen `task` passenden Ausschnitt.
- Bei gemischten Sets entscheidet `preferred_task` oder eine explizite Launcher-Auswahl ueber den initialen Player-Task.
- Der bestehende `compare_session`-Mechanismus bleibt fuer bounded Direct-Compare erhalten.
- Die standalone `comparison`-Workbench ersetzt den bounded Player-Compare nicht, sondern ergaenzt ihn.

### 6. Persistente, aber wieder bearbeitbare Comparison-Konfiguration

- Die Comparison-Seite braucht keinen separaten Wizard und keinen zweiten Seitentyp.
- Das Set speichert:
  - die aktive Itemmenge
  - die ausgewaehlten Sessions fuer die Comparison-Workbench
  - die bevorzugte Task-Sicht bzw. View-Filterung
- Die Seite laedt beim Oeffnen denselben Zustand wieder und erlaubt sofortige Weiterbearbeitung.
- Sichtbar gibt es nur eine Speicheraktion: `Als neues Set speichern`.

## D. Datenmodell-Vorschlag fuer serverseitige Sets

## Grundsatz

Das passende Repo-Modell ist kein Browser-only State und auch kein getrenntes Temp-vs.-Saved-Doppelsystem. Passend zum bestehenden Stack ist ein Postgres-basiertes Set-Aggregat mit einem gemeinsamen Tabellenmodell fuer `draft` und `saved`.

### 1. Tabellen

`research_sets`

- `set_id` UUID/Text, Primary Key
- `owner_user_id` Text, FK auf `users.user_id`
- `corpus_language` Text, z. B. `spanish`
- `label` Text, bei `saved` verpflichtend, bei `draft` optional
- `state` Text mit Check `draft|saved`
- `source_preset_id` Text nullable
- `preferred_task` Text nullable, Check `wordlist|text`
- `comparison_view_task` Text nullable/default `all`, Check `all|wordlist|text`
- `created_at`
- `updated_at`
- `last_accessed_at`
- `expires_at` nullable

`research_set_items`

- `set_id` FK auf `research_sets`
- `task` Text, Check `wordlist|text`
- `item_id` Text
- `sort_order` Integer
- `segment_id` Text nullable
- `note` Text nullable
- Unique-Key auf `(set_id, task, item_id)`

`research_set_sessions`

- `set_id` FK auf `research_sets`
- `session_id` Text
- `sort_order` Integer
- Unique-Key auf `(set_id, session_id)`

### 2. Warum dieses Modell zum Repo passt

- Es nutzt die vorhandene Postgres-/SQLAlchemy-Infrastruktur, ohne einen zweiten Datenspeicher einzufuehren.
- Es bleibt kompatibel zur bestehenden file-backed Research-Metadatenlogik: Sessions und Player-Artefakte bleiben weiterhin in `data/`, waehrend usergebundene Arbeitszustaende in Postgres liegen.
- Es behandelt `draft` und `saved` als Lifecycle desselben Modells statt als getrennte Technikpfade.
- Es speichert Item-Referenzen explizit als `task + item_id`, passend zu den bereits vorhandenen Task-Katalogen.

### 3. Beziehung zu Usern und Presets

- Jedes Set gehoert genau einem User ueber `owner_user_id`.
- `source_preset_id` verweist optional auf ein file-backed Preset, ist aber kein Fremdschluessel in eine Datenbanktabelle.
- Ein gespeichertes Set kopiert seine explizite Itemliste in `research_set_items` und bleibt dadurch stabil, auch wenn sich das Ursprungs-Preset spaeter aendert.

### 4. `draft` vs. `saved`

- `draft`
  - `state = draft`
  - `expires_at` gesetzt
  - `label` optional
- `saved`
  - `state = saved`
  - `expires_at = null`
  - `label` gesetzt

### 5. TTL-/Cleanup-Strategie

- Drafts erhalten serverseitig `expires_at` und `last_accessed_at`.
- Jeder Zugriff aus `phenomena`, `comparison` oder `player` aktualisiert `last_accessed_at` und verschiebt `expires_at` innerhalb eines definierten Fensters.
- Cleanup erfolgt nicht ueber Browser-Logout, sondern ueber einen serverseitigen Job.
- Repo-passend ist dafuer ein Flask-CLI-Kommando, z. B. `flask research-sets-cleanup`, das spaeter in Dev manuell und in Prod per Scheduler ausgefuehrt wird.

### 6. Minimale Sicherheitsanforderungen / Ownership

- Alle Set-Reads und Set-Writes muessen den JWT-User serverseitig in `owner_user_id` aufloesen.
- Kein API-Endpunkt darf ein clientseitig geliefertes `owner_user_id` akzeptieren.
- Jede Set-Abfrage filtert immer nach `(set_id, owner_user_id)`.
- `session_id`-Eintraege in `research_set_sessions` muessen gegen die existierende dateibasierte Session-Leseschicht validiert werden.
- `task + item_id` aus `research_set_items` muessen gegen die Task-Kataloge validiert werden.
- Row-Level Security ist im aktuellen Repo nicht der erste sinnvolle Schritt, weil die Anwendung mit einer gemeinsamen DB-Verbindung arbeitet. Zunaechst ist app-seitige Ownership-Erzwingung der passende, reale Sicherheitsmechanismus.

## E. Komponenten- und Modul-Schnitt

### 1. Bestehende Komponenten, die weiterverwendet werden sollten

- [app/src/app/research_sessions.py](c:\dev\promat\app\src\app\research_sessions.py) als Session-/Person-Grundmodell
- [app/src/app/research_views.py](c:\dev\promat\app\src\app\research_views.py) fuer shared page-level View-Model-Helfer, Labeling und Speaker-Card-Ableitungen
- [app/src/app/routes/public.py](c:\dev\promat\app\src\app\routes\public.py) fuer die bestehenden HTML-Routefamilien und Player-Media-Delivery
- [app/templates/pages/research_player.html](c:\dev\promat\app\templates\pages\research_player.html) als Referenz fuer Audio-Controls, Meta-Cards und itembasierte Listen
- [app/static/js/pages/research-player.js](c:\dev\promat\app\static\js\pages\research-player.js) als Referenz fuer clipbasiertes Playback und compare-sequencing
- die vorhandenen Task-Kataloge unter [data/config/research_player/spanish/task_catalogs](c:\dev\promat\data\config\research_player\spanish\task_catalogs)

### 2. Was abstrahiert werden sollte

- gemeinsamer Loader fuer taskuebergreifende Item-Referenzen aus Task-Katalogen
- gemeinsamer Preset-Loader fuer `phenomena_presets.json`
- gemeinsamer Config-Loader fuer `player_config.json`
- gemeinsame Normalisierung von `task + item_id`-Referenzen, Segment-Markern und optionalen Gruppen
- Trennung der bounded Player-Compare-Logik von generischem itembasiertem clip playback

### 3. Neue Module / Container, die sinnvoll sind

- `app/src/app/research_presets.py`
  - file-backed Loader fuer `player_config.json`, `phenomena_presets.json`, Task-Kataloge
- `app/src/app/research_sets.py`
  - Persistenz- und Ownership-Schicht fuer Drafts/Sets
- `app/src/app/routes/research_api.py`
  - JSON-Endpunkte fuer Set CRUD, Set-Sessions, Set-Items, Save-as-new-set
- `app/templates/pages/research_comparison.html`
  - eigenstaendige Comparison-Workbench
- `app/templates/pages/research_phenomena.html`
  - datengetriebene Phenomena-/Preset-Seite
- `app/static/js/pages/research-comparison.js`
  - item-zentrierte Mehrfach-Playback-Interaktion
- `app/static/js/pages/research-phenomena.js`
  - Preset-Editierung, Launch-Entscheidungen, Save-as-new-set
- `app/migrations/0003_create_research_sets.sql`
  - Postgres-Schema fuer Sets

### 4. Was bewusst getrennt bleiben soll

- bounded Direct-Compare im Player bleibt Teil des Players
- standalone `comparison` bleibt eigene Workbench und bekommt nicht die komplette session-zentrierte Player-Chrome
- `phenomena` bleibt Preset-/Auswahlseite und wird nicht zur vollen Hoeransicht umgebaut
- zentrale Presets bleiben file-backed Projektkonfiguration und werden nicht als userveraenderbare DB-Objekte modelliert

## F. Phasenplan fuer die Folgeruns

### Phase 1: Specs und Zustandsmodell fixieren

Ziel:

- Widerspruchsfreie aktive Specs fuer Seitenrollen, Query-Kontext und Set-/Preset-Begriffe herstellen.

Betroffene Dateien/Verzeichnisse:

- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- optional `docs/spec/platform-data-files.md`
- `docs/plans/player_comparison_phenomena_repo_implementation_plan.md`

Risiken / Seiteneffekte:

- Zu fruehe Detail-Festlegung kann spaetere UI-Iteration erschweren.
- Ohne klare Begriffsprioritaet laufen Folgephasen sonst gegen Alt-Specs.

Abhaengigkeiten:

- keine

Minimale Akzeptanzkriterien:

- `comparison` und `phenomena` sind in den Specs nicht mehr auf Player-Untermode reduziert.
- `player` bleibt task-spezifisch ohne `mixed`-Route.
- `set_id`/`preset_id`/`preferred_task` sind begrifflich sauber getrennt.

### Phase 2: Kuratierte Config-Grundlage einfuehren

Ziel:

- die bereits spezifizierten, aber im Repo fehlenden Config-Dateien und Loader produktiv anschliessen.

Betroffene Dateien/Verzeichnisse:

- `data/config/research_player/spanish/player_config.json`
- `data/config/research_player/spanish/phenomena_presets.json`
- `app/src/app/research_presets.py`
- Tests fuer Loader und Validierung

Risiken / Seiteneffekte:

- Preset-Item-Referenzen koennen von Task-Katalogen abweichen.
- Ohne Validierungslogik entstehen spaeter fragile Set-Daten.

Abhaengigkeiten:

- Phase 1

Minimale Akzeptanzkriterien:

- Spanish `player_config.json` und `phenomena_presets.json` existieren.
- Loader validiert `task + item_id` gegen Task-Kataloge.
- gemischte `wordlist`/`text`-Preset-Mengen sind technisch lesbar.

### Phase 3: Serverseitiges Set-Modell und Auth-gebundene API einfuehren

Ziel:

- Postgres-Drafts/Sets plus JSON-API fuer usergebundene Arbeitsmengen aufbauen.

Betroffene Dateien/Verzeichnisse:

- `app/migrations/0003_create_research_sets.sql`
- `app/src/app/research_sets.py`
- `app/src/app/routes/research_api.py`
- `app/src/app/routes/__init__.py`
- ggf. `app/src/app/__init__.py` fuer CLI-Cleanup
- API- und Ownership-Tests

Risiken / Seiteneffekte:

- Research-Routen sind aktuell noch nicht auth-enforced.
- Falsche Ownership-Filter waeren eine echte Sicherheitsluecke.

Abhaengigkeiten:

- Phase 1
- Phase 2 fuer Preset->Set-Materialisierung

Minimale Akzeptanzkriterien:

- Authentifizierte User koennen Draft-Sets anlegen, laden, aendern und als neues Set speichern.
- Nicht-Eigentuemer koennen fremde Sets nicht lesen oder veraendern.
- Draft/Saved nutzen dasselbe Datenmodell.

### Phase 4: `phenomena` als editierbare Preset-Seite ausbauen

Ziel:

- die bestehende Platzhalterseite zur kuratierten Preset- und Launcher-Oberflaeche machen.

Betroffene Dateien/Verzeichnisse:

- `app/src/app/routes/public.py`
- `app/src/app/research_views.py` oder neues View-Model-Modul fuer phenomena
- `app/templates/pages/research_phenomena.html`
- `app/static/js/pages/research-phenomena.js`

Risiken / Seiteneffekte:

- Gefahr, `phenomena` zu stark in Richtung Vollplayer zu ziehen.
- Gefahr, Set-Erzeugung zu spaet oder zu frueh zu triggern.

Abhaengigkeiten:

- Phase 2
- Phase 3

Minimale Akzeptanzkriterien:

- Presets werden datengetrieben angezeigt.
- Items koennen hinzugefuegt und entfernt werden.
- Start in `comparison` oder `player` arbeitet ueber ein serverseitiges `set_id`.

### Phase 5: `comparison` als eigenstaendige Mehrfach-Workbench bauen

Ziel:

- die bisherige Placeholder-Seite in eine item-zentrierte Mehrfach-Hoeransicht ueberfuehren.

Betroffene Dateien/Verzeichnisse:

- `app/src/app/routes/public.py`
- neues View-Model fuer comparison
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- gemeinsame Audio-/Item-Helfer, falls ausgegliedert

Risiken / Seiteneffekte:

- UI kippt bei zu enger Kopplung an den bisherigen Player.
- `text` wird leicht vergessen, wenn die erste Iteration nur `wordlist` bedient.

Abhaengigkeiten:

- Phase 2
- Phase 3
- Phase 4 fuer Phenomena->Comparison-Handoff

Minimale Akzeptanzkriterien:

- `comparison` laedt ein `set_id`.
- ausgewaehlte Sessions koennen hinzugefuegt und entfernt werden.
- `wordlist` und `text`-Items koennen im selben Set vorkommen.
- die Workbench bleibt auf derselben Seite editierbar.

### Phase 6: `player` sauber an `set_id` / `preset_id` anbinden

Ziel:

- den bestehenden Player so erweitern, dass er serverseitige Sets taskgebunden nutzen kann, ohne seine Routefamilie zu veraendern.

Betroffene Dateien/Verzeichnisse:

- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- Player-bezogene Tests in `app/tests/test_research_sessions.py` oder neuen Testdateien

Risiken / Seiteneffekte:

- bestehender bounded Player-Compare darf nicht regressieren.
- Misch-Sets duerfen nicht zu inoffiziellen `mixed`-Pfaden fuehren.

Abhaengigkeiten:

- Phase 3
- Phase 4 oder 5 fuer echte Launcher-Handoffs

Minimale Akzeptanzkriterien:

- `player` akzeptiert `set_id`.
- gemischte Sets rendern taskgebunden den passenden Ausschnitt.
- `compare_session` bleibt fuer Direct-Compare erhalten.

### Phase 7: Hardening, Cleanup, Tests und Doku

Ziel:

- Ownership, Cleanup, Regression-Schutz und Abschlussdokumentation vervollstaendigen.

Betroffene Dateien/Verzeichnisse:

- API- und UI-Tests
- CLI-Cleanup fuer Drafts
- Spezifikation und Run-Logs

Risiken / Seiteneffekte:

- Ohne diese Phase bleiben Draft-TTL, Ownership und Text-Support leicht halb fertig.

Abhaengigkeiten:

- Phasen 3 bis 6

Minimale Akzeptanzkriterien:

- Cleanup fuer Drafts existiert.
- Tests decken Phenomena, Comparison, Set-API und Player-Set-Handoff ab.
- Doku und aktive Specs entsprechen dem implementierten Stand.

## G. Konkrete Aenderungsziele pro Phase

### Phase 1

- Aktive Spec-Widersprueche beseitigen.
- Begriffe `set_id`, `preset_id`, `preferred_task`, `draft`, `saved` normativ festziehen.

### Phase 2

- fehlende kuratierte Konfigurationsdateien ins Repo bringen.
- validierten Loader fuer Presets und Player-Config bauen.

### Phase 3

- Postgres-Schema fuer Sets einfuehren.
- API und Ownership-Schicht auf die bestehende Auth-DB aufsetzen.
- Research-Arbeitszustaende von Browser-only-Logik entkoppeln.

### Phase 4

- Presets editierbar machen.
- Handoff in `comparison` und `player` ueber `set_id` implementieren.

### Phase 5

- item-zentrierte Mehrfach-Workbench mit persistentem Set-Kontext umsetzen.
- `text` von Anfang an mittragen.

### Phase 6

- bestehenden Player an Set-Kontext anbinden.
- taskgebundene Filterung und gemischte Sets sauber integrieren.

### Phase 7

- Cleanup, Tests, Doku und Resthaertung abschliessen.

## H. Ergebnisdokumentation und unmittelbare Konsequenz fuer den naechsten Run

Nach diesem Plan sollte der naechste Implementierungsrun nicht direkt mit UI-Bau starten, sondern mit Phase 2 oder Phase 3 beginnen, je nachdem ob zuerst die kuratierte Config-Grundlage oder zuerst das Set-Backend gelegt wird.

Empfohlene Reihenfolge fuer den naechsten konkreten Run:

1. fehlende `player_config.json` und `phenomena_presets.json` plus Loader einziehen
2. direkt danach Postgres-Set-Schema und Set-API einfuehren

Begruendung:

- ohne kanonische Preset-Dateien bleibt `phenomena` fachlich leer
- ohne Set-Backend bleiben `phenomena`, `comparison` und spaeter `player` bei derselben Inkonsistenz zwischen Plan und Laufzeit haengen
