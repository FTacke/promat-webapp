---
tags: promat, webdesign, planung
---

architecture_plan.md

# Architektur-Konsolidierung und Player-Optimierung

## Status und Zweck

Dieses Dokument ist ein Planungs- und Referenzdokument für die nächste Konsolidierungsphase der PROMAT-Webapp. Es bündelt die aus Audit, aktiver Spec und den letzten produktiven Runs abgeleiteten Architekturentscheidungen und legt eine verbindliche Umsetzungsreihenfolge für die nächsten größeren Eingriffe fest.

Stand 2026-04-13:

- Phase 1 der Access-Konsolidierung ist produktiv umgesetzt und normativ in `docs/spec/platform-data-files.md` und `docs/spec/research-access.md` verankert.
- Phase 2 der zentralen Research-Capability-Schicht ist produktiv umgesetzt; die aktive Source of Truth liegt jetzt in `docs/spec/research-capabilities.md` und im kanonischen Implementierungsspiegel `app/src/app/research_capabilities.py`.
- Phase 3 der Unified-Player-Entschlackung ist produktiv umgesetzt; die interne Runtime-Auflösung für Source, Set, Media, Items und bounded Compare lebt jetzt in `app/src/app/research_player_runtime.py`, während Route-Vertrag und produktive Nutzerlogik stabil bleiben.
- Phase 4 der Set-Modell-Entschlackung ist produktiv umgesetzt; der kanonische Set-Kern und der owner-gebundene Workbench-State sind jetzt serverseitig getrennt, ohne die produktiven Flows in `phenomena`, `comparison` und `player` aufzubrechen.
- Phase 5 der Schattenpfad-Bereinigung ist produktiv umgesetzt; verbliebene Top-Level-Kompatibilitätsprojektionen der Set-API wurden entfernt, sodass workbench-spezifischer Zustand im produktiven JSON-Vertrag nur noch unter `workbench_state` geführt wird.
- Dieses Planungsdokument bleibt für die restliche Reihenfolge relevant, ist aber nicht selbst die aktive Spezifikation.

Es beschreibt nicht nur den Zielzustand des Research-Players, sondern auch die nötige Vorarbeit in Access-Logik, Capability-Modell, Set-Semantik und Routing. Der Player darf nicht isoliert optimiert werden, weil seine aktuelle Komplexität direkt aus mehreren noch nicht sauber genug getrennten Systemschichten entsteht.

## Ausgangslage

PROMAT hat bereits eine brauchbare Basis:

- Runtime, Config, Public und Sessions sind grundsätzlich sauber getrennt.
- Der Research-Player ist bereits als ein gemeinsamer Player für mehrere Materialtypen angelegt.
- Phänomene, Vergleich und Player greifen inzwischen sichtbar auf dieselbe owner-gebundene Set-Basis zu.
- Die Route des Players ist bereits stark genug, um Session, Task, Set-Kontext, Fokus und bounded Compare über einen gemeinsamen Vertrag abzubilden.

Trotzdem ist der jetzige Zustand noch keine ruhige Zielarchitektur.

Die zentralen strukturellen Probleme sind derzeit:

1. Access-Regeln und öffentliche Research-Flächen sind noch nicht konsequent genug als geschützte App-Bereiche modelliert.
2. Task-, View-, Set- und Workbench-Fähigkeiten sind nicht an einer einzigen kanonischen Stelle definiert.
3. Der Player ist in seiner äußeren Form richtig, intern aber noch zu stark als Orchestrierungszentrum gebaut.
4. Interview ist im gemeinsamen Task-Rahmen sichtbar, aber bewusst noch nicht als produktiver Player-Modus ausgebaut.

## Zielbild in einem Satz

PROMAT soll unter `research` eine klar geschützte Forschungs-App mit einem einzigen modularen, source-gesteuerten Unified Player erhalten, dessen Verhalten aus einer zentralen Capability-Schicht und einem schlanken Set-Kern abgeleitet wird.

## Verbindliche Grundentscheidung für Research Access

Für **alle** Korpora gilt künftig dieselbe Regel:

- `/{ui_lang}/research/{corpus}/design` ist öffentlich.
- **Alle anderen** Research-Seiten und Research-Detailrouten sind nur nach erfolgreicher Authentifizierung zugänglich.

Das betrifft insbesondere:

- `speakers`
- `recordings`
- `comparison`
- `phenomena`
- `player`
- `phenomena/presets/{preset_id}`
- `phenomena/sets/{set_id}`
- alle owner-gebundenen Set- und Arbeitsflächen

Diese Regel gilt nicht nur für `spanish`, sondern genauso für `english`, `french` und `german`.

## Begründung für die Access-Entscheidung

Der gesamte Research-Bereich außerhalb von `design` arbeitet mit datenschutzrelevanten Forschungsdaten oder führt direkt in solche Arbeitsflächen hinein. Eine halböffentliche Modellierung einzelner Workbenches erzeugt langfristig mehr Probleme als Nutzen:

- unklare Sicherheitsgrenzen
- inkonsistente Nutzerführung
- Sonderlogik im Routing
- doppelte Zustandsmodelle für öffentliche und geschützte Varianten
- spätere teure Rückbauten

Darum gilt:

> Research außerhalb von `design` ist kein öffentlicher Inhaltsbereich, sondern ein geschützter App-Bereich.

## Access-Regeln für die Umsetzung

### 1. Schutz auf Routing-Ebene, nicht im Workbench-Body

Die Auth-Schranke gehört an die eigentliche Seitengrenze.

Nicht zulässig ist ein Modell, bei dem die Seite selbst öffentlich sichtbar bleibt und dann innerhalb der Seite ein CTA wie „Bitte anmelden“ oder „Sign in to continue“ erscheint. Das ist für diese Flächen die falsche Architektur.

Richtig ist:

- entweder die Route ist zugänglich,
- oder sie ist es nicht und leitet sauber in den Login-Zugang bzw. auf eine vorgeschaltete Zugriffsschranke.

### 2. Keine korpusabhängigen Access-Ausnahmen

Es darf keine harte Sonderlogik wie „Spanisch hat echte Workbenches, andere Sprachen Placeholder“ mehr im Research-Access geben.

Die Frage, ob ein Korpus inhaltlich schon weit ausgebaut ist, ist etwas anderes als die Frage, ob eine Route geschützt ist.

### 3. Design bleibt die einzige öffentliche Research-Unterseite

`design` ist die erklärende und dokumentierende Ausnahme. Alles andere ist geschützter Forschungsraum.

### 4. Diese Regel muss in Code, Spec und Governance gleichlautend stehen

Es reicht nicht, sie nur im Routing umzusetzen. Sie muss zusätzlich:

- in die bindende Research-Access-Spec,
- in die Plattform-/Routing-Spec,
- in relevante Governance-/Instruction-Dateien,
- und in künftige Planungsdokumente

übernommen werden.

Sonst wird die Ausnahme später wieder versehentlich aufgeweicht.

## Primäres Architekturziel nach der Access-Korrektur

Nach der Access-Festlegung ist das nächste Hauptziel eine **zentrale Research-Capability-Schicht**.

Ohne diese Schicht bleibt der Player trotz aller Verbesserungen zu indirekt, zu verteilt und zu driftanfällig.

## Die zentrale Research-Capability-Schicht

## Zweck

Die Capability-Schicht ist der eine kanonische Ort, an dem die fachlich-technischen Fähigkeiten des Research-Bereichs beschrieben werden.

Sie soll verstreute Mehrfachdefinitionen ersetzen und künftig die Basis für Routing, Sichtbarkeit, Player-Verhalten, Compare-Fähigkeit, Set-Fähigkeit und sprachspezifische Unterschiede bilden.

## Die Capability-Schicht muss mindestens definieren

### 1. Aktive Research-Tasks

Kanonische technische Task-Keys:

- `wordlist`
- `text`
- `interview`

Dabei bleibt wichtig:

- technische Keys bleiben stabil,
- sichtbare Labels dürfen korpusspezifisch sein,
- aber sichtbare Labels erzeugen keine zweite Task-Familie.

### 2. Korpus- und sprachspezifische Unterstützung

Pro Korpus bzw. Sprachslug muss definierbar sein:

- welche Research-Seiten verfügbar sind,
- welche Seiten öffentlich oder geschützt sind,
- welche Tasks im Player produktiv unterstützt sind,
- welche Tasks nur sichtbar, aber noch unavailable sind,
- welche text-spezifischen Render-Modi erlaubt sind,
- welche sprachspezifischen Metadaten oder Varietäten gelten.

### 3. Workbench-Fähigkeiten

Pro Task bzw. Source-Klasse muss definierbar sein:

- player-fähig oder nicht,
- compare-fähig oder nicht,
- set-fähig oder nicht,
- focus-fähig oder nicht,
- running-text-fähig oder nicht,
- full-audio-fähig oder nicht.

### 4. Seitentypen und Access-Semantik

Es muss klar modellierbar sein:

- Seite öffentlich oder geschützt,
- Überblicksseite oder Detail-Workbench,
- owner-gebundene Daten nötig oder nicht,
- Auth zwingend oder optional.

### 5. Sichtbare Task-Subsets je Workbench

Nicht jede Workbench braucht jede Task-Familie in voller Form.

Beispiele:

- `player`: `wordlist`, `text`, später `interview`
- `comparison`: nur die dafür sinnvoll unterstützten Tasks
- `phenomena`: kuratierte Tasks, nicht jedes denkbare Material

Diese Unterscheidung darf nicht in mehreren Modulen parallel leben.

## Ziel der Capability-Schicht

Das Ziel ist nicht noch eine weitere Konfigurationslage, sondern die Beseitigung von Mehrdeutigkeiten.

Am Ende soll gelten:

> Keine verstreuten Task- und Workbench-Wahrheiten mehr in mehreren Dateien, sondern ein einziger kanonischer Fähigkeitsvertrag.

## Zielarchitektur des Players

## Leitprinzip

PROMAT hat genau **einen** Research-Player für die Webapp.

Es gibt:

- keinen separaten Wortlisten-Player,
- keinen separaten Satzlisten-Player,
- keinen separaten Text-Player,
- keinen separaten Set-Player,
- keinen zweiten Compare-Player.

Es gibt einen gemeinsamen Player mit einem stabilen Route-Vertrag und intern modularer, source-gesteuerter Architektur.

## Der äußere Player-Vertrag bleibt erhalten

Die bestehende Route-Familie bleibt die kanonische Grundlage:

```text
/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}
```

Ergänzender Query-Kontext bleibt möglich:

- `source`
- `preset_id`
- `set_id`
- `compare_session`
- `compare_mode`
- `focus_item`
- `focus_segment`
- `render_mode`

Wichtig ist:

- Der äußere Route-Vertrag bleibt stabil.
- Neue Varianten dürfen nicht wieder eigene Route-Familien eröffnen.
- Zusätzlicher Kontext verfeinert nur den Zustand, erzeugt aber kein zweites Player-Produkt.

## Interne Player-Module

Der Player soll intern in klar getrennte Bausteine zerlegt werden.

### 1. Source-Resolution

Verantwortung:

- klären, welche Quelle geladen wird,
- Quelle explizit als `wordlist`, `sentence_list`, `text` oder `set` normalisieren,
- keine UI-Heuristiken verwenden.

Regel:

Die Quelle wird **nicht** aus Textlänge, Satzanzahl oder sichtbarer Form erraten. Sie wird datengetrieben bestimmt.

### 2. Item-Normalisierung

Verantwortung:

- aus jeder produktiven Quelle eine gemeinsame geordnete Item-Sequenz ableiten,
- stabile `item_id`, sichtbare Nummerierung, Text, Reihenfolge und optionale Textmetadaten transportieren,
- keine parallelen Item-Systeme aufbauen.

Regel:

Alle produktiven Player-Oberflächen müssen vor dem Rendern dieselbe Grundform besitzen:

- eine normalisierte Source
- eine geordnete Liste normalisierter Items

### 3. Set-Resolution und Set-Filterung

Verantwortung:

- aktives `set_id` owner-gebunden auflösen,
- task-spezifischen Ausschnitt des Sets bestimmen,
- leere Exzerpte sauber als expliziten Empty State rendern.

Regeln:

- Ein Set filtert die sichtbare Sequenz, es baut keinen zweiten Player.
- Ein Set definiert keine neue Task-Familie.
- Ein Set rekonstruiert keinen Fließtext.

### 4. Media-Resolution

Verantwortung:

- Full-Audio und Item-Audio sauber auflösen,
- Verfügbarkeit explizit modellieren,
- fehlende Artefakte sauber degradieren.

Regeln:

- Audio-Fähigkeit folgt der Source- und Task-Logik, nicht der UI-Bequemlichkeit.
- Kein falsches Versprechen von Präzision oder Verfügbarkeit.

### 5. View-Composition

Verantwortung:

- dieselbe normalisierte Sequenz als Liste oder Running Text rendern,
- View-Switch nur anbieten, wenn die Source ihn wirklich erlaubt,
- aktiven Fokus über View-Wechsel stabil halten.

Regeln:

- View ist nur Darstellung, kein zweiter Datenzustand.
- Bei echter Textquelle darf `running_text` möglich sein.
- Bei Set-Ausschnitten ist `text` immer list-only.

### 6. Compare-Extension

Verantwortung:

- eine optionale sekundäre Session im selben Player-Zustand hinzufügen,
- Matching über stabile `item_id` abbilden,
- fehlende sekundäre Treffer sauber degradieren.

Regeln:

- Compare ist Erweiterung desselben Players.
- Compare ist kein eigener Player-Typ.
- Compare gilt nur für kompatible Tasks.

## Strikte Trennung von Task, Source, Set und View

Ein zentrales Ziel der Konsolidierung ist die eindeutige Trennung dieser vier Ebenen.

## 1. Task

Task ist der technische research-task-key:

- `wordlist`
- `text`
- `interview`

Task ist Route- und High-Level-Zustand.

## 2. Source

Source ist die normalisierte Materialklasse:

- `wordlist`
- `sentence_list`
- `text`
- `set`

Source beschreibt die aktuell geladene Materiallogik.

## 3. Set

Set ist eine optionale kuratierte Filter- und Auswahlkontextschicht.

Set ist **kein** eigener Task und **keine** eigene View.

## 4. View

View ist nur die Darstellungsform derselben Sequence.

Beispiele:

- Liste
- Running Text

Diese Ebenen dürfen nicht ineinanderfallen.

## Verbindliche Set-Regeln

## 1. Set ist kuratiertes Arbeitsmaterial, keine zweite Player-Domäne

Ein Set speichert:

- ausgewählte Items,
- ihre explizite Reihenfolge,
- Provenienz,
- Notiz,
- ggf. owner-gebundenen Arbeitsstatus.

Ein Set ist nicht:

- ein eigener Task,
- ein eigener View-Typ,
- ein künstlich rekonstruierter Text,
- eine zweite Compare-Architektur.

## 2. Set-Kern und Workbench-Präferenzen trennen

In den Set-Kern gehören nur semantisch stabile Set-Daten.

In den Set-Kern gehören **nicht**:

- player-spezifische Startpräferenzen,
- comparison-spezifische UI-Filtersemantik,
- Workbench-spezifische Anzeigelogik,
- sonstige abgeleitete UI-Zustände.

Workbench-Zustände dürfen auf ein Set referenzieren, aber sie sollen nicht dessen Kernmodell verunreinigen.

## 3. Sets bleiben im Player immer Listen

Auch wenn ein Set Items aus echter Textquelle enthält, gilt:

- keine Rekonstruktion als Fließtext,
- kein Running-Text-Modus,
- keine künstliche Voll-MP3-Logik auf Set-Ebene.

## 4. Leere task-spezifische Set-Ausschnitte bleiben ehrlich

Wenn ein aktives Set für den aktuellen Task keine Items enthält, dann gilt:

- kein stiller Fallback auf die volle Session,
- kein heimlicher Drop des Sets,
- kein irreführender Normalzustand.

Stattdessen wird ein expliziter taskbezogener Empty State gerendert.

## Zielzustand für `wordlist`

`wordlist` bleibt der stabilste und produktivste Player-Modus.

### Regeln

- list-only
- primär item-audio
- bounded direct compare erlaubt
- stabile sichtbare Nummerierung aus Produktionsdaten
- keine UI-generierte Fantasienummerierung
- item clicks bleiben item checks, kein Sprung in globale Vollaufnahme-Logik

### UI-Folgerung

`wordlist` bleibt die Referenzoberfläche für die ruhige, dichte, gut kontrollierbare Player-Interaktion.

## Zielzustand für `text`

`text` bleibt technisch ein einziger Task-Key, kann aber in zwei produktiven Verhaltensweisen auftreten:

- `sentence_list`
- `running_text`

## Regeln

- welche Form aktiv ist, kommt aus expliziten Source-Metadaten,
- nicht aus UI-Heuristik,
- `running_text` nur bei echter textfähiger Source,
- Compare bleibt auf stabilem sentence-list/item-list-Vertrag,
- Set-Ausschnitte im technischen Task `text` bleiben list-only.

## Konsequenz

`text` ist keine zweite Player-Welt, sondern eine source-gesteuerte Variante auf derselben Item-Basis.

## Zielzustand für `interview`

Interview wird bewusst **nicht** in den jetzigen Unified-Player-Kern hineingezwungen.

## Verbindliche Entscheidung

Interview bleibt vorerst:

- sichtbar als Task,
- aber funktional separat,
- ohne Compare,
- ohne künstliche Zerlegung in Wortlisten-/Satzlisten-Logik,
- mit später eigenem, einfachen, interview-geeigneten Renderer.

## Begründung

Interview ist konzeptionell anders:

- Sprecherwechsel
- segmentbasierte Navigation
- andere Interaktionslogik
- kein sinnvoller bounded direct compare

Darum wird Interview ausdrücklich nicht in dieselbe tiefe Modularisierung wie `wordlist` und `text` gepresst.

## Zielbild für Compare im Player

## Grundsatz

Bounded direct compare bleibt ein Bestandteil desselben Players und kein separates Produkt.

## Regeln

- maximal eine sekundäre Session,
- nur für kompatible Tasks,
- Matching über stabile `item_id`,
- fehlende Treffer degradieren lokal,
- kleinere Viewports fallen auf Single-Session-Ansicht zurück,
- keine zweite Route-Familie,
- keine zweite globale Compare-Architektur im Player.

## UI-Folgerung

Die Compare-Logik bleibt sichtbar als bewusste Erweiterung der primären Player-Oberfläche, nicht als immer offene Konkurrenzstruktur.

## Was aus dem Player entfernt oder bereinigt werden muss

## 1. Orchestrierungsballast in einzelnen Buildern

Der Player darf nicht weiterhin einen übergroßen Builder behalten, der gleichzeitig:

- Herkunftskontext,
- Set-Auflösung,
- Compare-Logik,
- Render-Modi,
- Session-Switching,
- Audio-Verfügbarkeit,
- Leerzustände,
- Client-State

in einer Stelle zusammenzieht.

Das ist nicht robust genug für die nächsten Ausbauphasen.

## 2. Tote oder halbtote Schattenpfade

Alte spezialisierte Builder oder Hilfsfunktionen, die nicht mehr wirklich Teil des aktiven Systems sind, müssen:

- entfernt,
- oder klar als separate Strategie neu eingeordnet werden.

Schattenpfade erzeugen Fehlwahrheiten in der Wartung.

## 3. Ungenutzte oder übermodellierte Konfigurationslagen

Konfigurationsschichten, die real nicht im aktiven Pfad hängen, sollen nicht als scheinbare Zukunftsfähigkeit im System verbleiben.

Regel:

- entweder aktiv und normativ anbinden,
- oder entfernen,
- aber keine dauerhafte Zwischenlage.

## 4. Sprachspezifische Fachlogik im View-Layer

Korpus- oder sprachspezifische Varietäten und Fachzuordnungen gehören nicht hart in den View-Builder.

Sie müssen in domänische Lookup- oder Capability-/Konfigurationsschichten ausgelagert werden.

## Verhältnis von Player, Comparison und Phenomena

## 1. Gemeinsame Set-Basis beibehalten

Die Angleichung der sichtbaren owner-gebundenen Set-Liste über Player, Comparison und Phenomena war richtig und bleibt erhalten.

## 2. Workbenchs bleiben getrennte Produkte

Trotz gemeinsamer Set-Basis gilt:

- `player` bleibt session-zentrierte Detail-Workbench,
- `comparison` bleibt item-zentrierte Vergleichs-Workbench,
- `phenomena` bleibt kuratierende Set-Workbench.

Sie dürfen nicht wieder ineinander kollabieren.

## 3. Gemeinsame Logik nur dort, wo sie wirklich geteilt ist

Gemeinsam bleiben insbesondere:

- Set-Auflösung,
- Item-/Katalog-Normalisierung,
- Media-Logik,
- gewisse Payload-/Serialisierungslogik,
- Translation-/Label-Grundlagen.

Getrennt bleiben:

- UI-Ablauf,
- sichtbarer Arbeitskopf,
- Interaktionsrhythmus,
- Workbench-spezifische Seitensemantik.

## Empfohlene Umsetzungsreihenfolge

## Phase 1: Access-Modell festziehen

Zuerst wird das Research-Access-Modell systemisch korrigiert.

### Ziele

- nur `design` öffentlich,
- alle übrigen Research-Flächen auth-pflichtig,
- konsistente Redirect-/Login-Logik,
- keine Login-CTA innerhalb geschützter Workbench-Bodies,
- Spec und Governance auf denselben Stand bringen.

### Diese Phase hat Vorrang

Ohne diese Phase würden weitere Arbeiten auf einer falschen Grenzziehung aufbauen.

## Phase 2: Zentrale Capability-Schicht einführen

Danach wird die verteilte Logik kanonisiert.

### Ziele

- एक zentraler Vertrag für Tasks, Workbench-Fähigkeiten, Access-Semantik und Sprach-/Korpus-Support,
- Ende der Mehrfachdefinitionen,
- klare Basis für Player, Comparison und Phenomena.

## Phase 3: Player intern modularisieren

Erst auf Basis der Capability-Schicht wird der Player intern umgebaut.

### Ziele

- klare interne Modulgrenzen,
- weniger Orchestrierungsballast,
- source-gesteuerte Entscheidungen,
- saubere Set- und View-Trennung,
- stabilerer Ausbaupfad.

## Phase 4: Set-Modell entschlacken

Danach wird das Set-Modell semantisch bereinigt.

### Ziele

- Set-Kern von Workbench-Zustand trennen,
- persistente Set-Bedeutung klären,
- spätere Teaching-Anbindungen nicht auf verunreinigtem Kern aufbauen.

## Phase 5: Schattenpfade und Altlasten entfernen

### Ziele

- tote Player-Bausteine löschen,
- Scheinkonfigurationen bereinigen,
- Wartungssignale im Code wieder ehrlich machen.

## Phase 6: Interview später separat produktiv machen

### Ziele

- einfacher interview-geeigneter Renderer,
- kein Compare,
- keine unnötige Verflechtung mit dem jetzigen Unified-Player-Kern.

## Was ausdrücklich nicht passieren soll

## 1. Kein weiterer Ausbau auf Basis diffuser Access-Regeln

Es soll keine Zwischenlösung geben, bei der einige Korpora oder Workbenchs halboffen und andere geschlossen sind.

## 2. Keine neuen Sonderrouten oder Spezial-Player

Neue Materialarten oder Kontexte dürfen nicht wieder in eigene Player-Familien ausweichen.

## 3. Keine weitere Vermischung von Set und Workbench-Zustand

Ein Set ist keine versteckte Comparison- oder Player-Session.

## 4. Keine Heuristiken statt expliziter Metadaten

Textfähigkeit, View-Umschaltbarkeit oder Compare-Fähigkeit dürfen nicht aus sichtbaren Oberflächen erraten werden.

## 5. Interview nicht künstlich in falsche Architektur pressen

Interview bleibt vorerst bewusst ein Sonderfall außerhalb des produktiven Unified-Player-Kerns.

## Prüf- und Akzeptanzkriterien für die Konsolidierung

Die Architektur-Konsolidierung ist erst dann gelungen, wenn mindestens folgende Bedingungen erfüllt sind:

## Access

- Für alle Korpora ist unter `research` nur `design` öffentlich.
- Alle anderen Research-Seiten verlangen Auth.
- Geschützte Flächen rendern nicht als pseudoöffentliche Seiten mit Login-CTA im Body.

## Capability-Modell

- Es gibt eine einzige kanonische Stelle für Task-, Access- und Workbench-Fähigkeiten.
- Verstreute Parallelwahrheiten sind entfernt oder auf diese Quelle umgestellt.

## Player

- Der Player behält denselben äußeren Route-Vertrag.
- Intern sind Source, Items, Set, Media, View und Compare modular getrennt.
- `wordlist` und `text` laufen auf derselben Grundarchitektur.
- Set-Ausschnitte bleiben listenbasiert.
- Running-Text erscheint nur bei explizit textfähigen Quellen.

## Sets

- Das Set-Kernmodell enthält keine unnötige Workbench-Anzeigepräferenz.
- Player, Comparison und Phenomena nutzen dieselbe Set-Grundlage, ohne semantisch zu verschmelzen.

## Interview

- Interview bleibt sichtbar, aber nicht falsch als voll produktiver Compare-/Unified-Task verkauft.
- Späterer Ausbau kann separat erfolgen.

## Schlussformel

Die nächste Ausbauphase von PROMAT darf nicht als bloßes UI-Finetuning verstanden werden. Es geht um eine strukturelle Konsolidierung.

Die richtige Reihenfolge ist daher verbindlich:

1. Access korrigieren.
2. Capability-Schicht einziehen.
3. Player intern modularisieren.
4. Set-Kern entschlacken.
5. Altlasten entfernen.
6. Interview später separat ausbauen.

Nur so wird aus dem jetzigen brauchbaren Prototyp unter `research/{corpus}` eine ruhige, belastbare Forschungs-App-Architektur.
