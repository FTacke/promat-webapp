# Arbeitsbeschluss: Abgrenzung und Zielarchitektur für `player`, `comparison`, `phenomena` sowie Presets/Sets

## Status und Zweck

Dieses Dokument fasst den aktuellen fachlichen und technischen Arbeitsstand für den Research-Bereich zusammen. Es präzisiert die Rollen von `player`, `comparison` und `phenomena`, legt den Umgang mit kuratierten Presets und nutzerspezifischen Sets fest und beschreibt die daraus folgende Zustands- und Routenlogik.

Ausgangspunkt ist die bestehende PROMAT-Architektur:

* `comparison` und `phenomena` sind als aktive Research-Seiten vorgesehen.
* Der bestehende Research-Player ist als einheitlicher modularer Player mit task-spezifischer Route angelegt.
* Die aktuelle Spezifikation sieht bislang Vergleich vor allem als begrenzte Player-Erweiterung vor; dieser Arbeitsbeschluss erweitert das Konzept für `comparison` bewusst in Richtung einer eigenständigen Mehrfachvergleichs-Workbench.  

---

## 1. Grundsätzliche Seitenabgrenzung

### `player`

`player` bleibt die **session-zentrierte Detailansicht**.

Er ist zuständig für:

* das Hören einer konkreten Session,
* das Umschalten zwischen den für diese Session verfügbaren Tasks,
* die Anzeige der kompakten sessionbezogenen Metadaten,
* einen optionalen Direktvergleich mit genau **einer** zweiten Session.

Der Player bleibt damit ein Arbeitsraum für:

* **1 Primärsession**
* plus optional **1 Vergleichssession**

Er ist **nicht** die Mehrfachvergleichs-Workbench.

Das bleibt konsistent mit der bestehenden Zielarchitektur: Der Player hat genau eine primäre `session_id`, optional eine `compare_session`, und die Route bleibt task-spezifisch unter `/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}`. Als Task-Werte sind nur `wordlist`, `text` und `interview` zulässig.  

---

### `comparison`

`comparison` wird als **eigenständige item-zentrierte Mehrfach-Höransicht** definiert.

Sie ist zuständig für:

* das Vergleichen **derselben Items** über mehrere Sessions hinweg,
* das gezielte Hören von Split-MP3s,
* den Aufbau von Vergleichskonstellationen über Filter, Suche und Auswahl,
* den Umgang mit kuratierten oder nutzerdefinierten Itemmengen,
* das Arbeiten mit mehreren Sprecher:innen nebeneinander.

`comparison` beantwortet fachlich nicht die Frage
„Wie klingt diese Session?“
sondern die Frage
„Wie wird dasselbe Material von mehreren Sprecher:innen realisiert?“

Damit ist `comparison` **keine bloße Variante des Players**, sondern UI-seitig eine eigene Workbench. Unter der Haube soll sie jedoch möglichst viel wiederverwenden:

* dieselben Datenquellen,
* dieselbe Item-Logik,
* dieselben geschützten Media-Routen,
* dieselben Designsemantiken für Metadaten und Karten.

---

### `phenomena`

`phenomena` wird als **kuratierte Auswahl- und Einstiegsebene** definiert.

Sie ist zuständig für:

* das Anzeigen und Erklären fachlicher Presets,
* das Sichtbarmachen der in einem Preset enthaltenen Items,
* das Hervorheben relevanter Segmente innerhalb dieser Items,
* das Editieren einer kuratierten Vorauswahl vor dem Öffnen einer Höransicht,
* das Starten in entweder `player` oder `comparison`.

`phenomena` ist damit **keine primäre Hörseite**, sondern ein fachlicher Launcher:

* für fokussiertes Arbeiten mit einer Session im Player,
* oder für Mehrfachvergleich derselben kuratierten Itemmenge in `comparison`.

Das ist anschlussfähig an die bestehende Preset-Architektur: Presets sind Konfiguration und nicht Teil der Audioartefakte; sie sollen den Player mit kuratiertem Fokus starten können, wobei manuelle Ergänzungen möglich bleiben.

---

## 2. Fachliche Kernrollen der drei Seiten

### Player

**Detailhören einer konkreten Session**

* konkrete Session hören
* zwischen `wordlist`, `text`, `interview` wechseln
* optional eine zweite Session als Direktvergleich hinzunehmen
* innerhalb der Session fokussiert und taskbezogen arbeiten

### Comparison

**Mehrfachvergleich identischer Einheiten**

* mehrere Sessions nebeneinander
* dieselben Items über mehrere Sprecher:innen hören
* Split-MP3-basierte Vergleichsfläche
* eher rasterartig, forschungsorientiert, desktop-first

### Phenomena

#### Kuratiertes, phänomenbasiertes Arbeiten

* Presets ansehen
* kuratierte Itemmengen prüfen und editieren
* dann wahlweise in Player oder Comparison öffnen

---

## 3. Vergleichslogik: was wohin gehört

### Direktvergleich im Player

Der Direktvergleich im Player bleibt bewusst begrenzt:

* genau eine Primärsession
* optional genau eine zweite Session
* keine n-fache Mehrfachansicht
* voller taskbezogener Kontext bleibt erhalten

Das ist der richtige Ort für enges, fokussiertes Arbeiten an einer Session mit einer Referenz.

---

### Mehrfachvergleich in `comparison`

Die Mehrfachansicht gehört in `comparison`.

Dort sollen möglich sein:

* mehrere Sessions nebeneinander,
* Vergleich derselben Items über mehrere Sprecher:innen,
* Nutzung der Split-MP3-Artefakte pro Item,
* Sessionauswahl und Sessionentfernung innerhalb derselben Arbeitsansicht.

Das ist fachlich ein anderer Zugriff als im Player und rechtfertigt die eigene Seite.

---

## 4. Tasks und Items

### Grundsatz

Für `comparison` ist **nicht** eine vorgeschaltete Task-Wahl der zentrale Einstieg.
Die Seite ist **item-zentriert**.

Das bedeutet:

* Eine aktuelle Arbeitsmenge kann `wordlist`-Items enthalten.
* Dieselbe Arbeitsmenge kann auch `text`-Items enthalten.
* Gemischte Mengen sind erlaubt.
* `interview` gehört nicht in `comparison`.

Die bestehende Spezifikation erlaubt bereits gemischte Preset-Selektionen über mehrere Tasks hinweg. Im Player werden diese taskbezogen auf die jeweils aktive Sicht gefiltert. `comparison` baut darauf auf, aber ohne erzwungene Vorab-Taskwahl.

---

### Konsequenz für `comparison`

`comparison` arbeitet nicht primär mit einem gewählten Task, sondern mit einer **aktuellen Itemmenge**.

Jedes Item muss intern immer eindeutig als **Task-Item-Referenz** modelliert sein, also sinngemäß:

* `task`
* `item_id`

Die UI kann dann:

* alle Items gemeinsam anzeigen,
* oder nach Task gruppieren bzw. filtern,
* etwa über Ansichten wie „Alle“, „Wortliste“, „Text“.

Das ist eine Darstellungsentscheidung, keine Einstiegsbedingung.

---

### Konsequenz für `player`

Der Player bleibt trotz gemischter Sets **task-spezifisch**.

Die Route bleibt:

* `/player/{session_id}/wordlist`
* `/player/{session_id}/text`
* `/player/{session_id}/interview`

Es wird **keine** zusätzliche Route wie `mixed` eingeführt.

Begründung:

* `mixed` ist kein Task, sondern ein Auswahlzustand.
* Die bestehende Player-Architektur ist ausdrücklich task-spezifisch.  

Wenn ein Set sowohl `wordlist`- als auch `text`-Items enthält, öffnet der Player trotzdem immer in **einem initialen Task** und zeigt dort nur den passenden Ausschnitt desselben Sets.

---

## 5. Verhalten bei gemischten Sets im Player

### Regel

Ein gemischtes Set darf in den Player geladen werden, aber der Player öffnet immer taskgebunden.

### Öffnungslogik

* Enthält das Set nur `wordlist`-Items, öffnet der Player in `wordlist`.
* Enthält das Set nur `text`-Items, öffnet der Player in `text`.
* Enthält das Set beides, wird ein initialer Task bestimmt.

### Zulässige Bestimmung des initialen Tasks

Vorzugsweise:

1. `preferred_task` des Sets, falls vorhanden
2. sonst explizite User-Auswahl beim Öffnen
3. sonst ein definierter Fallback

Es wird **nicht** festgelegt, dass gemischte Sets automatisch immer als `text` geöffnet werden.

---

## 6. Vereinheitlichung unter der Haube

Obwohl der Player task-spezifisch bleibt, soll die Implementierung intern möglichst stark vereinheitlicht werden.

### Ziel

Ein gemeinsamer interner Renderer- bzw. Unit-Typ für `wordlist` und `text`, soweit semantisch möglich.

Beispielhafte gemeinsame Basiselemente:

* `task`
* `item_id`
* `item_number`
* `text`
* optional `split_mp3`
* optionale Timing-Informationen
* optionale Tokens

Das entspricht der Grundidee der bestehenden Player-Spezifikation:
Es gibt **einen modularen Player**, keine voneinander getrennten Produkte für `wordlist`, `text` und `interview`; Unterschiede werden über Task-Renderer und Render-Modi beschrieben.

### Wichtig

Diese interne Vereinheitlichung ändert **nicht** die äußere Fachlogik:

* `wordlist` bleibt `wordlist`
* `text` bleibt `text`
* `interview` bleibt `interview`

---

## 7. Presets, Working Sets und Saved Sets

### Grundmodell

Es gibt drei logisch zu unterscheidende Ebenen:

#### A. Curated Presets

Zentral gepflegte, redaktionelle Presets.

* sprach-/projektweit gültig
* unabhängig von einzelnen Usern
* durch das Projekt kontrolliert und änderbar

Diese Logik ist bereits in der bestehenden Preset-Architektur unter `phenomena_presets` angelegt.

#### B. Working Set

Die aktuell bearbeitete Auswahl eines Users.

* kann aus einem kuratierten Preset hervorgehen
* kann manuell ergänzt werden
* kann auch reduziert werden
* ist zunächst eine Arbeitsmenge

#### C. Saved Set

Ein benanntes, nutzerspezifisch gespeichertes Set.

* accountgebunden
* wiederaufrufbar
* reproduzierbar
* von späteren Änderungen des Ursprungs-Presets unabhängig

---

## 8. Presets sind editierbare Startzustände

### Festlegung

Ein Preset in `phenomena` ist **nicht starr**.

Der User darf:

* zusätzliche Items hinzufügen
* einzelne vorausgewählte Items wieder entfernen
* also die kuratierte Menge aktiv verändern

Diese Bearbeitung ist **kein Editieren des zentralen Presets**, sondern das Erzeugen bzw. Verändern einer userseitigen Arbeitsmenge.

### UI-Konsequenz

In `phenomena` muss die Presetliste daher als **editierbare Itemliste** verstanden werden:

* mit sichtbaren Gruppen,
* mit markierten relevanten Segmenten,
* mit Entfernen-Funktion pro Item, z. B. per `X`,
* mit Möglichkeit, weitere Items hinzuzufügen.

---

## 9. Speicherung: nur eine technische User-Set-Lösung

### Festlegung

Temporäre und gespeicherte User-Sets sollen **technisch gleich** behandelt werden.

Es sollen **nicht** parallel fünf verschiedene Speichermodelle entstehen, etwa:

* zentrale Presets,
* Browser-`sessionStorage`,
* unsaved local state,
* saved DB state,
* weitere Sonderfälle.

Die elegante Lösung ist:

* zentrale Presets separat,
* **alle userseitigen Arbeitsmengen serverseitig in Postgres**.

### Warum nicht `sessionStorage` als Hauptlösung?

Browser-`sessionStorage` ist nur für die aktuelle Tab-/Fenster-Sitzung gedacht und endet beim Schließen des Tabs oder Fensters. Für accountgebundene, wiederaufrufbare Arbeitsstände ist das als Hauptspeicher zu schwach.

### Warum serverseitig?

Für einen eingeloggten Research-Bereich ist es sinnvoller, den Arbeitsstand usergebunden auf dem Server zu halten:

* wiederverwendbar über Sitzungen hinweg,
* unabhängig von einem einzelnen Browser-Tab,
* konsistent zwischen `phenomena`, `comparison` und `player`.

---

## 10. Einheitliches Datenmodell für User-Sets

### Vereinfachung

Nach außen soll es für userseitige Arbeitsmengen nur **eine** Referenz geben:

* `set_id`

Nicht getrennt:

* `saved_set_id`
* plus anderer Mechanismus für temporäre Mengen

### Logik

Ein Set in Postgres kann intern unterschiedliche Zustände haben, etwa:

* `draft`
* `saved`

Damit gilt:

* **temporär** und **gespeichert** sind keine unterschiedlichen technischen Modelle,
* sondern nur unterschiedliche Lifecycle-Zustände desselben Modells.

---

## 11. Lebenszyklus temporärer Sets

### Temporäre Sets

Temporäre Sets werden als serverseitige Drafts geführt, zum Beispiel mit:

* `state = draft`
* `expires_at`
* `last_accessed_at`

### Gespeicherte Sets

Gespeicherte Sets haben z. B.:

* `state = saved`
* `expires_at = null`

### Ablauf

Temporäre Sets dürfen automatisch verfallen, z. B.:

* nach definierter Zeit ohne Nutzung,
* mit Verlängerung bei Zugriff.

### Technische Begründung

PostgreSQL hat keine eingebaute automatische Row-TTL im Sinne von „dieser Datensatz verschwindet von selbst nach X Tagen“. Sauber ist daher ein serverseitiges Ablaufdatum `expires_at` plus periodisches Cleanup, etwa über einen geplanten Job. Für einen geschützten, accountgebundenen Bereich ist das die robuste Lösung.

### Logout

Ein Logout kann optional Zusatzlogik auslösen, ist aber **nicht** die verlässliche Kernmechanik für das Aufräumen. Die maßgebliche Lebensdauer soll serverseitig geregelt werden.

---

## 12. Sicherheits- und Account-Modell

User-Sets sind nutzergebunden.

Daraus folgt:

* jedes Set gehört genau einem User,
* der Zugriff muss über Accountbindung gesichert sein,
* serverseitige Durchsetzung ist erforderlich.

Für PostgreSQL ist dafür ein Modell mit `owner_user_id` und abgesicherter Zugriffspolitik sinnvoll; PostgreSQL unterstützt dafür Row-Level Security.

---

## 13. Namensgebung und Speichern im UI

### Speichern

Es gibt nur eine sichtbare Speicheraktion:

**„Als neues Set speichern“**

Es wird **nicht** zwischen

* „Aus kuratiertem Preset ableiten“
* und „Als neues Set speichern“
  im UI getrennt.

### Begründung

Das ist transparenter und vermeidet unnötige Doppelbegriffe.

### Namensvorschlag

Wenn ein Set auf einem kuratierten Preset basiert, darf der UI-Vorschlag automatisch in Richtung gehen wie:

* `preset_XY_modified`
* `intonation_qw_modified`
* `preset_akzentuierung_modified`

Aber sichtbar bleibt nur die eine Aktion:
**„Als neues Set speichern“**

---

## 14. Persistenz der Herkunft

Auch wenn ein Saved Set stabil und unabhängig vom Ursprungs-Preset gespeichert wird, soll die Herkunft nachvollziehbar bleiben.

Daher sollte ein Set optional Felder wie diese tragen:

* `source_preset_id`
* `label`
* `preferred_task`
* `created_at`
* `updated_at`
* `last_accessed_at`
* `expires_at`
* `state`

Wichtig dabei:

* Ein Saved Set speichert **seine eigene explizite Itemliste**.
* Es ist **kein bloßer dynamischer Verweis** auf ein zentrales Preset plus Delta.
* Änderungen an einem zentralen Preset dürfen ein bereits gespeichertes User-Set nicht still verändern.

---

## 15. Parameter und Referenzen

### Zentrale Presets

Für kuratierte Vorlagen bleibt:

* `preset_id`

### User-Sets

Für laufende oder gespeicherte userseitige Arbeitsmengen:

* `set_id`

### Konsequenz

Sobald ein User mit einer Auswahl wirklich arbeitet, also sie in `comparison` oder `player` überführt, soll aus einer bloßen Presetansicht praktisch ein konkretes User-Set werden.

Leitidee:

* Presets sind Vorlagen.
* Laufende Arbeit ist ein Set.

---

## 16. `phenomena`: Zielverhalten

`phenomena` soll folgende Struktur haben:

### Preset-Ebene

* fachliche Presets anzeigen
* Beschreibung und Ziel des Presets zeigen
* enthaltene Items sichtbar machen
* relevante Segmente innerhalb der Items markieren

### Editierbare Arbeitsmenge

* einzelne Preset-Items entfernen
* weitere Items hinzufügen
* aktuelle Auswahl als Arbeitsmenge halten
* optional als neues Set speichern

### Öffnungsoptionen

Nach der Bearbeitung soll der User entscheiden können:

* **Im Player öffnen**
* **In Comparison öffnen**

`phenomena` selbst bleibt also kuratierte Einstiegsebene und delegiert das eigentliche Hören an die Zielansicht.

---

## 17. `comparison`: Zielverhalten

`comparison` ist die Mehrfachvergleichs-Workbench.

### Einstieg

Kein harter vorgeschalteter Wizard, sondern eine Hauptseite mit integrierter, wiederöffnbarer Konfiguration.

### Konfigurationspanel / Selection Tray

Darin:

* Session-Suche
* Session-Filter
* aktive Sessions
* Sessions hinzufügen
* Sessions entfernen
* Suche nach Labels wie Niveau, L1, Sprechergruppe, Standardvarietät
* aktuelle Herkunft der Itemmenge:

  * aus Preset
  * aus Set
  * manuell
* Bearbeiten der aktuellen Itemmenge

### Wichtige Klarstellung

Es gibt **kein Pflichtfeld „Task“** am Anfang.
`comparison` arbeitet mit einer Itemmenge, nicht primär mit einer Taskwahl.

### Darstellungssteuerung

Optional soll die Darstellung nach Task gefiltert oder gruppiert werden können:

* alle Items
* nur `wordlist`
* nur `text`

---

## 18. Sessionauswahl in `comparison`

### Festlegung

Sessions müssen direkt auf `comparison` wieder entfernbar und ergänzbar sein.

Es soll **keine starre Vorseite** geben, auf der man alles konfiguriert und danach in eine zweite, unflexible Arbeitsansicht geht.

Stattdessen:

* dieselbe Seite ist Arbeitsfläche und Konfigurationsraum zugleich,
* die Konfiguration ist sichtbar oder aufklappbar,
* „Auswahl modifizieren“ bedeutet nur, das Panel erneut zu öffnen,
* der Zustand bleibt erhalten.

---

## 19. Session-/Speaker-Auswahl: guided first, manual second

### Grundsatz

Die Auswahl auf `comparison` und `phenomena` soll **nicht primär dropdown-first** sein.

Stattdessen:

* geführte Auswahl als Standard,
* direkte Suche und präzise manuelle Filterung als Expert:innenmodus.

### Sinnvolle guided Logik

Beispielhaft:

* Vergleiche mit Referenzaussprache
* Zeige passende Sprecher:innen nach Niveau
* Filtere nach L1
* Filtere nach Standardvarietät
* arbeite mit einer vorgegebenen oder gespeicherten Itemmenge

### Bewusst zunächst weggelassen

Ein eigener Modus „Verlauf derselben Person“ wird vorerst **nicht** als primärer Guided Path umgesetzt, weil aktuell noch keine reale Mehrfachsession-Lage pro Person produktiv relevant ist.

---

## 20. `comparison`: Hörlogik und Controls

`comparison` ist eine Höransicht, aber **nicht** der volle Player.

### Deshalb braucht `comparison`

* globale Wiedergabegeschwindigkeit
* globale Lautstärke
* pro Item klare Play-Aktionen
* optional sequentielles Abspielen eines Items über mehrere Sessions

### Deshalb braucht `comparison` nicht zwingend

* einen vollen sessionbezogenen Transportbereich wie im Player
* einen großen Fortschrittsbalken für 1–2-Sekunden-Clips

### Bewusste Reduktion

Zu Beginn:

* **eine globale Geschwindigkeit**
* **eine globale Lautstärke**
* optional später leichte Session-spezifische Mute/Solo-Schalter

Kein fein granuliertes Mischpult pro Session.

---

## 21. Anzahl Sessions in `comparison`

### Zielverhalten

Die Anzahl sichtbarer Sessions soll sich an Nutzbarkeit und Breite orientieren, nicht an theoretischer Beliebigkeit.

### Festlegung

* bis ca. 4 Sessions: normale Mehrspaltenansicht
* ab mehr Sessions: horizontal scrollbarer Rasterbereich
* linke Item-Spalte bleibt sticky
* Session-Header bleiben sticky
* horizontales Scrollen betrifft nur die Vergleichsfläche, nicht die ganze Seite

### Obergrenze

Es soll eine harte Obergrenze geben, damit die Oberfläche nicht kippt.
Als Planungsrahmen gilt:

* sinnvoll nutzbar: etwa 3 bis 5 Sessions
* harte Grenze: etwa 6 Sessions

### Grundrichtung

`comparison` bleibt damit klar desktop-orientiert. Das passt zur bestehenden Spezifikation, in der Compare-Kontexte ohnehin nicht als mobile Vollansicht gedacht sind.

---

## 22. `text` in `comparison`

### Festlegung

`text` wird für `comparison` ausdrücklich mitgedacht.

Begründung:

* `text` ist in der bestehenden Spezifikation bereits item-basiert modelliert,
* nicht als unstrukturierter Fließtext,
* sondern mit `item_id`, `item_number`, `text` und perspektivisch geeigneten Einheiten für Vergleich und Synchronisierung.

### Konsequenz

`comparison` ist nicht nur Wortlistenvergleich.
Es soll so gebaut werden, dass auch `text`-Items sauber abbildbar sind.

---

## 23. Routen- und Zustandsgrundsatz

### Player

Bleibt task-spezifische Route:

* `/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}`

### Vergleichs- und Preset-Kontext

Werden **nicht** als neue Task-Routen modelliert, sondern als Zusatzkontext bzw. über referenzierte Sets.

### Kein `mixed`-Task

Es wird keine Player-Route mit `mixed` geben.

Leitsatz:
**Mixed gehört in den Zustand, nicht in den Pfad.**

---

## 24. Zusammenfassung der verbindlichen Beschlüsse

### Verbindlich festgelegt

1. `player`, `comparison` und `phenomena` sind drei fachlich klar getrennte Seitenrollen.
2. `player` bleibt session-zentriert und unterstützt nur 1 plus optional 1.
3. `comparison` wird als eigenständige Mehrfach-Höransicht für itembasierten Vergleich konzipiert.
4. `phenomena` ist die kuratierte Preset- und Auswahlseite, nicht die eigentliche Hörseite.
5. Presets sind editierbare Startzustände; Items dürfen hinzugefügt und entfernt werden.
6. Es gibt nur eine sichtbare Speicheraktion: **„Als neues Set speichern“**.
7. User-Arbeitsmengen werden serverseitig in Postgres gespeichert; temporär und dauerhaft sind nur unterschiedliche Zustände desselben Set-Modells.
8. `comparison` arbeitet itemzentriert, nicht task-first.
9. Gemischte Mengen aus `wordlist` und `text` sind erlaubt.
10. Der Player bleibt taskgebunden; es gibt keine `mixed`-Route.
11. `wordlist` und `text` sollen intern möglichst über gemeinsame Bausteine gerendert werden, ohne ihre Fachlogik zu verwischen.
12. Sessionauswahl auf `comparison` ist integrierter, jederzeit modifizierbarer Teil derselben Hauptseite.

---

## 25. Konsequenz für die Repo-Umsetzung

Für die Umsetzung mit dem Repo-Agenten bedeutet dieser Beschluss voraussichtlich:

* Anpassung der Spezifikationen zu `comparison` und `phenomena`
* Präzisierung der Player- und Set-Logik
* Einführung eines klaren Postgres-Modells für usergebundene Sets
* Konzeption und spätere Implementierung einer eigenständigen `comparison`-Workbench
* Ausbau von `phenomena` zur editierbaren Preset-Seite
* Beibehaltung der task-spezifischen Player-Route ohne `mixed`
