---
tags: promat, Pronunciation Matters, Webdesign
---

# PROMAT: Webdesign "/recordings" und "/speakers"

## 1. Ziel dieses Dokuments

Dieses Dokument bündelt die konzeptionellen Entscheidungen für die Forschungsseiten `recordings` und `speakers` im PROMAT-Kontext. Es dient als fachliche und gestalterische Grundlage für die spätere Umsetzung in der Webapp.

Ausgangspunkt ist die bereits festgelegte Plattformlogik: Das Korpus wird über mehrere gleichwertige Zugänge erschlossen. `recordings` ist der aufgabenbasierte Zugang, `speakers` der personenzentrierte Zugang. Beide Seiten greifen auf denselben Datenbestand zu, sollen aber bewusst unterschiedliche Nutzungslogiken abbilden. `speakers` und `recordings` führen jeweils auf eine Player-Seite mit vollständiger Aufgabe; Inline-Audio gehört dagegen nicht auf diese beiden Seiten. :contentReference[oaicite:0]{index=0}

## 2. Grundprinzip: Warum beide Seiten sinnvoll sind

Die beiden Seiten sind nur dann sinnvoll, wenn sie tatsächlich unterschiedliche Einstiege in denselben Datenraum ermöglichen.

`recordings` beantwortet die Frage:

- Welche Art von Aufnahme möchte ich hören?

`speakers` beantwortet die Frage:

- Welche Art von Sprecher:in möchte ich untersuchen?

Beide Seiten dürfen deshalb nicht dieselbe Oberfläche mit anderer Überschrift sein. Der Unterschied muss schon in der Primärlogik sichtbar werden:

- `recordings`: task-first
- `speakers`: person-first

Genau das entspricht der strukturellen Plattformlogik: `recordings` ist als Zugang über Aufgabentypen konzipiert, `speakers` als Zugang über Personen. :contentReference[oaicite:1]{index=1}

## 3. Gemeinsame Designleitlinien

Für beide Seiten gelten einige übergreifende Gestaltungsprinzipien:

- Die Seiten sind Forschungswerkzeuge, keine Landingpages.
- Die Oberflächen müssen ruhig, dicht und funktional sein.
- Redundante Erklärtexte sollen vermieden werden.
- Kerninformationen müssen schnell scannbar sein.
- Filter und Ergebnisdarstellung müssen auf Desktop effizient und auf Mobile robust funktionieren.
- Große dekorative Cards oder stark visuelle Showcase-Elemente sind hier fehl am Platz.
- Die UI soll immer klar machen, ob gerade nach Aufgaben oder nach Sprecher:innen navigiert wird.

Außerdem gilt für beide Seiten:

- aktive Filter werden als Chips dargestellt
- der gesamte Chip ist anklickbar und entfernt den Filter
- es gibt eine kleine Statuszeile
- Ergebnislisten bleiben kompakt
- die eigentliche Audiowiedergabe findet erst im Player statt

## 4. Seite `recordings`: fachliche Funktion

### 4.1 Zweck

`recordings` ist der aufgabenbasierte Zugang zum Korpus. Hier steht nicht die Person als primäre Einheit im Vordergrund, sondern die jeweilige Aufgabe. Nutzer:innen wählen zunächst den Aufgabentyp und suchen innerhalb dieses Bereichs passende Sprecher:innen bzw. Aufnahmen.

Die Seite dient damit dem schnellen Zugang zu den drei zentralen Aufgabentypen, die intern sprachübergreifend als `isolated_speech`, `connected_speech` und `interview` geführt werden. Die UI verwendet die deutschen Labels. :contentReference[oaicite:2]{index=2}

### 4.2 Aufgabentypen

Im UI werden die drei Aufgaben klar und gleichrangig angeboten:

- Isolierte Aussprache
- Zusammenhängende Aussprache
- Interview

Wichtig ist dabei: Alle Sprecher:innen haben diese Aufgaben grundsätzlich vollständig aufgenommen. Deshalb braucht `recordings` keine Logik, die erst prüft, ob bestimmte Items oder Teilaufnahmen pro Person vorhanden sind. Das vereinfacht die Seite bewusst.

### 4.3 Kernflow

Die Nutzungslogik von `recordings` ist:

1. Aufgabentyp wählen
2. Sprecher:innen bzw. Aufnahmen nach Metadaten filtern
3. passende Aufnahme öffnen
4. auf der Player-Seite die vollständige Aufgabe mit gesamtem Audio und Transkript ansehen und hören

Ein zusätzlicher Wort- oder Item-Filter ist auf dieser Seite nicht notwendig. Er wäre nur dann sinnvoll, wenn man direkt innerhalb der Wortliste auf bestimmte Items vorspringen oder Sprecher:innen bereits nach einem einzelnen Wort einschränken wollte. Für das derzeitige Zielkonzept ist das nicht nötig und würde die Seite unnötig komplex machen.

## 5. Seite `recordings`: Informationsarchitektur und Layout

### 5.1 Kopfbereich

Der obere Bereich der Seite soll klar und knapp aufgebaut sein:

- Breadcrumb
- Seitentitel `Aufnahmen`
- ein kurzer Einleitungssatz, der die Seite als aufgabenbasierten Zugang erklärt

Direkt darunter folgt die Primärnavigation der Seite: die Auswahl des Aufgabentyps.

### 5.2 Task-Switcher

Für `recordings` wird ein Task-Switcher in Form von Tabs vorgesehen. Diese Lösung ist kompakt, sofort verständlich und sowohl auf Desktop als auch auf Mobile gut beherrschbar.

Die Tabs lauten:

- Isolierte Aussprache
- Zusammenhängende Aussprache
- Interview

Unterhalb der Tabs steht eine kurze einzeilige Beschreibung des aktuell ausgewählten Aufgabentyps. Rechts daneben wird die Anzahl der verfügbaren Aufnahmen angezeigt. Dadurch bleibt die Seite informativ, ohne in längere Beschreibungstexte auszuweichen.

Die Tabs sollen klar als Arbeitsnavigation wirken, nicht wie große Navigationskarten. Karten wären für diesen Seitentyp zu groß, zu erklärungsstark und zu nah an einer Landingpage-Logik.

### 5.3 Hauptbereich

Der Hauptbereich ist ein filterbares Arbeitsinterface.

Desktop:

- links oder oben links ein Filterpanel
- rechts die Ergebnisliste

Mobile:

- Filter oberhalb der Ergebnisse
- Ergebnisse darunter
- Tabs bleiben sichtbar und klar bedienbar

Die Seite soll insgesamt eher tabellarisch-kompakt wirken als card-basiert.

## 6. Seite `recordings`: Filterlogik

### 6.1 Vorgesehene Filter

Für `recordings` werden folgende Filter vorgesehen:

- Level
- L1
- speaker_type
- Geschlecht
- vorheriges Exposure (ja/nein)

`standard_variety` wird hier nicht als Filter vorgesehen. Der Grund ist pragmatisch: Diese Information ist im Wesentlichen nur für Native Speaker relevant, und diese Gruppe ist klein. Ein eigener Filter würde hier eher überladen als helfen.

### 6.2 Status- und Filterelemente

Oberhalb der Ergebnisliste erscheint eine kleine Statuszeile mit:

- Anzahl Aufnahmen
- Anzahl aktiver Filter

Aktive Filter werden als Chips angezeigt. Jeder Chip ist als Ganzes klickbar und entfernt den jeweiligen Filter. Es gibt kein separates kleines `x`.

### 6.3 Was bewusst nicht vorgesehen ist

Nicht vorgesehen sind:

- Wort- oder Item-Filter
- Vergleichslogik direkt auf der Seite
- Inline-Player
- matrixartige Gegenüberstellungen
- aufgabeninterne Segmentsuche

Diese Elemente würden die klare Rolle der Seite verwässern. `recordings` bleibt ein task-first-Browser, nicht ein Analyse- oder Vergleichstool.

## 7. Seite `recordings`: Ergebnisdarstellung

Die Ergebnisansicht soll kompakt, funktional und scanbar sein. Große Cards sind hier nicht sinnvoll, weil die Seite kein personenzentrierter Showcase ist, sondern ein aufgabenbezogenes Suchwerkzeug.

Sinnvoll ist eine kompakte Listen- oder Tabellenansicht pro Treffer. Jede Zeile zeigt nur die wesentlichen Identifikations- und Filterinformationen, etwa:

- session_id
- speaker_type
- Level
- L1
- Geschlecht
- Exposure ja/nein

Zusätzlich gibt es eine klare Aktion zum Öffnen der Aufnahme.

### 7.1 Interaktion

Jeder Treffer führt direkt in die Player-Seite der gewählten Aufgabe und Sprecher:in. Dort wird die gesamte Aufgabe mit vollständigem Audio und Transkript gerendert. Diese Trennung entspricht der übergreifenden Audiologik: `recordings` selbst dient der Auswahl, die eigentliche Wiedergabe geschieht auf einer separaten Player-Seite. :contentReference[oaicite:3]{index=3}

## 8. Seite `recordings`: Verhältnis zum Player

Der Player ist bewusst nicht Teil der Übersichtsseite. Die Seite `recordings` endet beim Auswahlakt.

Auf der Player-Seite gelten dann andere Logiken:

- vollständige Aufgabe
- vollständiges Transkript
- Audio-Player
- später ggf. Zusatzfunktionen wie Direktvergleich

Für eine spätere Ausbaustufe ist ein Doppel-Player denkbar, um zwei Sprecher:innen für dieselbe Aufgabe im Direktvergleich anzuzeigen. Diese Funktion gehört aber nicht auf `recordings`, sondern in den Player selbst. Sie soll zunächst nur als Desktop-Funktion gedacht werden, nicht als Standardbestandteil auf Mobile.

## 9. Seite `speakers`: fachliche Funktion

### 9.1 Zweck

`speakers` ist der personenzentrierte Zugang zum Korpus. Hier steht nicht zuerst die Aufgabe im Zentrum, sondern die Sprecher:in als Forschungsobjekt mit ihrem Profil.

Die Seite soll besonders für Suchintentionen geeignet sein wie:

- Zeig mir Sprecher:innen mit einem bestimmten Level
- Zeig mir Sprecher:innen mit bestimmter L1
- Zeig mir Lernende mit oder ohne vorheriges Exposure
- Zeig mir Native Speaker
- Zeig mir bestimmte Sprecherprofile zum direkten Durchgehen

Damit bekommt `speakers` eine eigene, von `recordings` klar unterscheidbare Funktion. Genau dieser Zugang über Personen ist in der Plattformlogik vorgesehen. :contentReference[oaicite:4]{index=4}

### 9.2 Kernflow

Die Nutzungslogik von `speakers` ist:

1. Sprechergruppe oder Sprecherprofil filtern
2. passende Sprecher:in in der Übersicht finden
3. entweder direkt eine Aufgabe öffnen
4. oder auf eine Profilseite der Sprecher:in gehen

Damit kombiniert `speakers` schnellen Zugriff mit vertiefender Personenansicht.

## 10. Seite `speakers`: Informationsarchitektur und Layout

### 10.1 Kopfbereich

Auch `speakers` beginnt mit:

- Breadcrumb
- Seitentitel `Sprecher:innen`
- kurzem Einleitungssatz, der den personenzentrierten Zugang erklärt

### 10.2 Schnellfilter-Ebene

Ganz oben auf der Seite steht eine segmentierte Schnellfilter-Ebene mit:

- Alle
- Lernende
- Native Speaker

`heritage_speaker` wird hier bewusst nicht angezeigt, solange diese Gruppe im Projekt faktisch noch nicht vorkommt. Eine leere oder erklärungsbedürftige zusätzliche Option würde die Oberfläche unnötig verkomplizieren.

Diese Schnellfilter-Ebene ist keine eigene Zwischenseite, sondern ein integrierter Umschalter innerhalb derselben Seite.

### 10.3 Weitere Filter

Unterhalb des Schnellfilters folgen die regulären Filter:

- Level
- L1
- Geschlecht
- vorheriges Exposure (ja/nein)

Der `speaker_type` ist hier bereits teilweise durch den Schnellfilter abgedeckt; die Seite bleibt dadurch fokussiert und verständlich.

### 10.4 Ergebnisdarstellung

Die Ergebnisdarstellung erfolgt hier bewusst card-basiert. Anders als bei `recordings` ist das sinnvoll, weil `speakers` personenzentriert ist und individuelle Sprecherprofile als separate Einheiten sichtbar machen soll.

Allerdings sollen diese Cards kompakt bleiben. Es geht nicht um große visuelle Profilkarten, sondern um dichte, gut scanbare Arbeitskarten.

## 11. Seite `speakers`: Speaker-Cards

### 11.1 Inhalt der Cards

Jede Card zeigt reduzierte Kerninformationen, etwa:

- person_id
- zugeordnete session_id
- speaker_type
- Level
- L1
- Geschlecht
- Exposure ja/nein

Die Information wird bewusst reduziert gehalten, damit die Übersicht schnell bleibt. Vollständige Metadaten gehören nicht auf die Card, sondern auf die Profilseite.

### 11.2 Visuelle Codierung

Die Cards können eine subtile farbliche Top-Border erhalten. Diese dient der schnellen Level-Erkennung.

Empfohlen ist:

- Lernende erhalten je nach Level eine differenzierte Farbcodierung
- Native Speaker erhalten einen eigenen klar unterscheidbaren Farbton
- Farbe dient nur als Zusatzsignal, nicht als alleinige Bedeutungsträgerin
- Level wird immer auch als Text angezeigt

Die Cards sollen dabei nicht vollflächig eingefärbt werden. Vollflächen oder zu bunte Karten würden die Seite unnötig laut machen. Die obere Akzentlinie reicht als visuelle Codierung.

### 11.3 Interaktion der Cards

Die Cards haben zwei Ebenen von Interaktion:

1. Hauptbereich der Card  
   führt auf die Profilseite der Sprecher:in

2. kleine Direktlinks innerhalb der Card  
   führen unmittelbar in die drei Aufgaben

Diese Direktlinks lauten:

- isolierte Aussprache
- zusammenhängende Aussprache
- Interview

Diese Doppelstruktur ist wichtig. Würde jede Interaktion immer zuerst über das Profil führen, würde die Seite im Alltag zu langsam. Würde es umgekehrt gar keine Profilseite geben, wäre der personenzentrierte Mehrwert von `speakers` zu gering. Die Kombination aus Profilzugang und Direktlinks löst das sauber.

## 12. Seite `speakers`: Status und Filterelemente

Wie bei `recordings` gibt es auch hier:

- eine kleine Statuszeile
- Filter-Chips
- klickbare Entfernung des gesamten Chips

Die konkrete Statuszeile kann sich an der Zahl der Treffer orientieren und die aktiven Filter transparent machen.

## 13. Profilseite der Sprecher:in

### 13.1 Warum eine eigene Profilseite nötig ist

Weil die Cards bewusst reduziert bleiben, braucht `speakers` eine echte Detailansicht. Diese soll nicht nur ein kleines Overlay oder ein nebensächlicher Dialog sein, sondern eine genuine Seite.

Gründe dafür:

- sie ist inhaltlich mehr als eine Schnellinfo
- sie ist besser verlinkbar und bookmarkbar
- sie funktioniert robuster auf Desktop und Mobile
- sie ist als Ziel vom Player aus sinnvoll erreichbar
- sie kann später wachsen, ohne in einem Dialog zu eng zu werden

### 13.2 Keine primäre Dialoglösung

Ein Dialog oder Popup wäre hier die falsche Hauptlösung. Das Profil ist kein nebensächliches Interface-Element, sondern eine eigenständige Forschungsperspektive auf die Sprecher:in. Daher wird eine eigenständige Profilseite vorgesehen.

### 13.3 Rolle der Profilseite

Die Profilseite ist die zentrale Detailansicht der Sprecher:in. Sie zeigt vollständigere Metadaten und dient als Hub zwischen Person und ihren verfügbaren Aufgaben.

Von der Profilseite aus führen ebenfalls Links in die drei Player.

### 13.4 Inhalt der Profilseite

Die Profilseite soll mindestens enthalten:

- person_id
- zugeordnete session_id
- speaker_type
- Level
- L1
- Geschlecht
- vorheriges Exposure
- weitere verfügbare Metadaten
- Links zu den drei Aufgaben

Wichtig ist, dass sowohl `person_id` als auch `session_id` sichtbar gemacht werden. Die Datenlogik trennt beides ausdrücklich: `person_id` beschreibt die Person als stabile Einheit, `session_id` die konkrete Aufnahme bzw. Session. :contentReference[oaicite:5]{index=5}

Diese Unterscheidung muss Nutzer:innen nicht didaktisch ausführlich erklärt werden. Es reicht, sie auf der Profilseite knapp und transparent sichtbar zu machen, zum Beispiel mit Bezeichnungen wie:

- Person-ID
- Zugeordnete Aufnahme

Optional kann eine sehr kurze Hilfestellung ergänzt werden, falls das sinnvoll erscheint. Eine lange Erläuterung des Datenmodells ist nicht nötig.

### 13.5 Zugriff vom Player aus

Auch vom Player aus soll die Profilseite erreichbar sein. Wer eine konkrete Aufnahme hört, soll die zugehörige Sprecher:in jederzeit in ihrem Kontextprofil aufrufen können.

## 14. Verhältnis von `speakers`, Profil und Player

Die saubere Rollenverteilung lautet:

- `speakers`: Sprecher:innen finden und vorsortieren
- `speaker profile`: Sprecher:in im Detail verstehen
- `player`: konkrete Aufgabe hören und lesen

So bleibt die Oberfläche logisch stabil:

- `recordings` startet von der Aufgabe aus
- `speakers` startet von der Person aus
- die Profilseite vertieft die Person
- der Player fokussiert die konkrete Aufnahme

## 15. Mobile- und Desktop-Verhalten

### 15.1 `recordings`

Desktop:

- Tabs oben
- darunter Task-Beschreibung und Anzahl Aufnahmen
- links Filter, rechts Ergebnisliste

Mobile:

- Tabs oben
- Beschreibung und Zahl kompakt darunter
- Filter oberhalb der Ergebnisse
- Ergebnisliste untereinander
- keine Vergleichsansicht

### 15.2 `speakers`

Desktop:

- Schnellfilter oben
- weitere Filter darunter
- Grid mit kompakten Speaker-Cards

Mobile:

- Schnellfilter bleibt kompakt bedienbar
- Filter gestapelt
- Speaker-Cards einspaltig untereinander
- Direktlinks zu den drei Aufgaben bleiben sichtbar und leicht tappbar

### 15.3 Doppel-Player

Ein späterer Doppel-Player ist ausschließlich als Desktop-Funktion vorgesehen. Für Mobile wird diese Vergleichsoption zunächst nicht unterstützt. Das hält die Player-Logik klar und vermeidet überladene enge Interfaces.

## 16. Dinge, die bewusst vermieden werden

Für beide Seiten gilt: Folgende Muster sollen vermieden werden, weil sie die Rollen der Seiten verwischen oder die Oberflächen unnötig aufblasen würden:

- große Landingpage-artige Karten ohne Arbeitswert
- Inline-Audio auf Übersichtsseiten
- Vergleichslogik direkt in `recordings`
- vollständige Metadaten in jeder Speaker-Card
- zusätzliche leere Schnellfilter-Kategorien wie `heritage`, solange sie nicht real belegt sind
- zu starke Farblogik oder rein farbbasierte Bedeutungszuweisung
- Popups als Ersatz für eine echte Profilseite

## 17. Zusammenfassung der Zielbilder

### `recordings`

`recordings` ist ein schlanker task-first-Browser mit:

- Tabs für die drei Aufgaben
- einzeiliger Aufgabenbeschreibung
- Anzeige der Anzahl verfügbarer Aufnahmen
- kompakten Filtern
- klickbaren Filter-Chips
- kompakter Ergebnisliste
- direktem Übergang in den Player

Die Seite enthält keine Vergleichslogik und keine Item- oder Wortsuche.

### `speakers`

`speakers` ist ein person-first-Browser mit:

- Schnellfilter für Alle / Lernende / Native Speaker
- zusätzlichen Profilfiltern
- kompakten Speaker-Cards
- Level-orientierter subtiler Farbcodierung
- Hauptklick ins Profil
- Direktlinks zu den drei Aufgaben
- echter Profilseite als Detailansicht
- Verlinkung vom Player zurück zum Profil

## 18. Implementationsleitidee

Die Umsetzung sollte sich bei beiden Seiten nicht an dekorativen Showcase-Seiten orientieren, sondern an klaren, belastbaren Forschungsinterfaces. Die beiden Seiten sind nicht Varianten derselben Ansicht, sondern bewusst unterschiedlich gedachte Einstiege in denselben Korpus. Genau diese Differenz muss die fertige UI sichtbar machen.

Hier ist der Nachtrag für die Doku und darunter der Umsetzungs-Prompt.


## 19. Festgelegte Implementationsentscheidungen für `recordings` und `speakers`

Dieser Nachtrag konkretisiert die bereits festgelegten Konzepte für die Forschungsseiten `recordings` und `speakers` und friert die wichtigsten Implementationsentscheidungen für die erste Umsetzungsphase ein. Er dient als verbindliche Ergänzung zur bisherigen Seitenkonzeption und soll bei späteren Konzeptänderungen mitgepflegt werden.

### 19.1 Routen

Für die personenzentrierte Detailansicht gilt:

```text
/{ui_lang}/research/{language}/speakers/[person_id]
````

Beispiel:

```text
/de/research/spanish/speakers/P-0012
```

Für die Player-Seite gilt:

```text
/{ui_lang}/research/{language}/player/[session_id]/[task]
```

Beispiel:

```text
/de/research/spanish/player/ES-L-DE-B1-26-001/isolated_speech
```

Diese Routenlogik folgt der bereits festgelegten Trennung von `person_id` und `session_id`: `person_id` beschreibt die Person als stabile Einheit, `session_id` die konkrete Aufnahme bzw. Session. 

Ein möglicher späterer Doppel-Player wird in dieser ersten Phase noch nicht konzipiert oder implementiert. Die aktuelle Player-Route bleibt deshalb zunächst auf die Einzelansicht ausgelegt. Eine spätere Erweiterung kann über zusätzliche Parameter oder eine ergänzende Vergleichslogik gelöst werden, ohne die jetzige Grundroute unnötig zu verkomplizieren.

### 19.2 `recordings`: festgelegte UI-Entscheidungen

Die Seite `recordings` bleibt der aufgabenbasierte Zugang zum Korpus. Die Primärnavigation erfolgt über Tabs für die drei Aufgaben:

* Isolierte Aussprache
* Zusammenhängende Aussprache
* Interview

Direkt unter den Tabs steht eine kurze einzeilige Beschreibung des gewählten Aufgabentyps; daneben wird die Anzahl der verfügbaren Aufnahmen angezeigt.

Die Ergebnisdarstellung erfolgt als kompakte Liste bzw. Tabelle, nicht als Card-Grid. Diese Entscheidung unterstreicht die Rolle von `recordings` als funktionales Arbeitsinterface und verhindert eine unnötige Annäherung an die personenzentrierte Seite `speakers`.

Die Standardsortierung erfolgt nach `level`.

Vorgesehene Filter sind:

* Level
* L1
* speaker_type
* Geschlecht
* vorheriges Exposure (ja/nein)

`standard_variety` wird in dieser ersten Fassung nicht als Filter vorgesehen, weil diese Angabe im Projektkontext nur für wenige Native Speaker relevant ist und die Oberfläche unnötig aufblähen würde.

Auf Mobile werden die Filter als einklappbarer Bereich oberhalb der Ergebnisse dargestellt. Diese Lösung ist kompakter und robuster als eine dauerhaft offene Filterspalte.

Die Statuszeile zeigt:

* Anzahl Aufnahmen
* Anzahl aktiver Filter

Aktive Filter werden als Chips angezeigt; der gesamte Chip ist anklickbar und entfernt den jeweiligen Filter.

### 19.3 `speakers`: festgelegte UI-Entscheidungen

Die Seite `speakers` bleibt der personenzentrierte Zugang zum Korpus.

Ganz oben steht ein segmentierter Schnellfilter mit:

* Alle
* Lernende
* Native Speaker

`heritage_speaker` wird hier bewusst nicht angezeigt, solange diese Gruppe im Projekt noch nicht real vertreten ist.

Darunter folgen die regulären Filter:

* Level
* L1
* Geschlecht
* vorheriges Exposure (ja/nein)

Die Ergebnisdarstellung erfolgt als kompakte Speaker-Cards. Diese zeigen eine reduzierte Auswahl zentraler Informationen und unterscheiden sich damit bewusst von der tabellarischen Logik der Seite `recordings`.

Auf den Cards soll mindestens sichtbar sein:

* person_id
* session_id
* speaker_type
* Level
* L1
* Geschlecht
* Exposure ja/nein

Die Task-Links innerhalb der Cards werden kurz benannt als:

* Liste
* Text
* Interview

Die Interaktionslogik der Cards ist zweistufig:

* der Hauptbereich der Card führt auf die Profilseite der Sprecher:in
* die kleinen Task-Links führen direkt in die jeweilige Player-Seite

Die Standardsortierung erfolgt auch hier nach `level`.

### 19.4 Profilseite der Sprecher:in

Die Profilseite ist eine eigenständige Seite und kein Dialog. Sie dient als Detailansicht der Sprecher:in und zeigt alle vorhandenen nicht-sensiblen Metadaten, also alle verfügbaren Forschungsmetadaten außerhalb des Secure-Bereichs.

Die Profilseite nennt ausdrücklich sowohl:

* `person_id`
* zugeordnete `session_id`

Damit bleibt die Trennung zwischen Person und konkreter Aufnahme transparent sichtbar, ohne dass sie auf der Oberfläche breit ausdidaktisiert werden muss. Diese Unterscheidung entspricht der festgelegten Datenarchitektur. 

Von der Profilseite aus führen ebenfalls Links zu den drei Aufgaben.

### 19.5 Visuelle Codierung der Speaker-Cards

Zur schnellen Orientierung erhalten Speaker-Cards eine subtile farbliche Top-Border.

Für Native Speaker wird festgelegt:

```text
--book-accent: #2b4460
```

Für Lernende wird eine abgestufte Farblogik vorgesehen, die sich harmonisch zwischen dem bestehenden Projektfarbton

```text
--promat-wordmark-accent: #a15a95
```

und dem Blau der Native-Speaker-Farbe bewegt. Grundprinzip:

* niedrigere Niveaus liegen näher am magenta-violetten Bereich
* höhere Niveaus liegen näher am blauen Bereich
* Native Speaker verwenden den klar getrennten Ton `#2b4460`

Die genaue Ableitung der Zwischenstufen soll gestalterisch konsistent mit dem bestehenden Designsystem erfolgen. Farbe dient nur als zusätzliches Orientierungssignal; Level muss immer auch als Text sichtbar sein.

### 19.6 Leere Zustände

Für Nulltreffer werden klare, knappe Standardtexte vorgesehen, etwa:

* „Keine passenden Aufnahmen gefunden.“
* „Keine passenden Sprecher:innen gefunden.“

Diese Texte sollen gemeinsam mit einer gut sichtbaren Möglichkeit zum Zurücksetzen der Filter erscheinen.

### 19.7 Rückverlinkung und Navigationslogik

Der Player wird in dieser Phase noch nicht umgesetzt. Für die spätere Navigation wird jedoch bereits festgehalten:

* der Player soll auf die jeweilige Ursprungsliste zurückverlinken (`recordings` oder `speakers`)
* zusätzlich soll es im Player einen expliziten Link zum Profil der Sprecher:in geben

Damit bleibt sowohl die Herkunft der Navigation als auch die personenzentrierte Vertiefung nachvollziehbar.

### 19.8 Dokumentationspflicht bei Umsetzung

Alle Umsetzungsruns zu `recordings`, `speakers`, Sprecherprofilen und angrenzenden Forschungsseiten sollen nach jedem Run in

```text
docs/research_pages/
```

dokumentiert werden.

Diese Run-Dokumentation dient der internen Prüfung und muss insbesondere festhalten:

* welche Dateien geändert wurden
* welche Seiten, Komponenten und Routen angelegt oder angepasst wurden
* welche Entscheidungen direkt umgesetzt wurden
* welche Punkte bewusst noch offen geblieben sind
* welche Abweichungen oder technischen Einschränkungen aufgetreten sind

Dieses Referenzdokument selbst soll bei späteren Konzeptänderungen ebenfalls aktualisiert werden, damit Konzept und Implementationsstand nicht auseinanderlaufen.

