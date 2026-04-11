---
tags: promat, webdesign, planung
---

# Phänomen-Seite (research/phenomena)

> Statushinweis
> Dieses Dokument ist ein Planungsstand und keine aktive Source of Truth. Die aktuell bindenden Regeln für `phenomena` liegen in `docs/spec/research-access.md` und `docs/spec/platform-data-files.md`. Wenn Plan und Spec auseinanderlaufen, gilt immer die Spec.

Die Seite `research/phenomena` wird als reine Übersichts- und Einstiegsseite gedacht. Sie soll bewusst einfach, ruhig und linear aufgebaut sein. Inhaltliche Bearbeitung, Speichern und Handoff in andere Bereiche gehören nicht auf diese Seite, sondern auf eine separate Unterseite einer konkreten Liste.

## Ziel der Seite

Die Seite hat genau eine Aufgabe: Phänomenlisten sichtbar machen und einen klaren Einstieg bieten.

Nutzer:innen sollen hier:

- eine vorhandene Liste finden
- eine Liste öffnen
- eine kuratierte Liste als Ausgangspunkt modifizieren
- eine neue Liste anlegen
- eigene Listen bei Bedarf löschen können

Mehr nicht.

## Grundprinzip

Die Seite folgt einem schlichten Aufbau von oben nach unten:

1. Seitenkopf
2. Phänomenliste wählen
3. Listenübersicht
4. Listenende mit Pagination / Mehr-laden / Empty State

Es gibt auf dieser Seite keine parallelen Arbeitsbereiche, keine Konfigurationsblöcke und keinen Handoff in Player oder Vergleich.

## Seitenkopf

Titel:

Phänomene

Unterzeile:

Kuratierte Phänomenlisten öffnen oder eine neue Liste anlegen.

Die Unterzeile bleibt knapp. Kein langer Erklärungstext, keine interne Fachsprache, keine Hinweise auf spätere Arbeitsschritte.

## Hauptblock

Überschrift:

1 Phänomenliste wählen

Direkt darunter eine schlanke Steuerzeile mit nur den nötigen Elementen:

- Suchfeld: „Liste suchen“
- Primärbutton rechts: „Neue Liste“

Weitere Filter werden in dieser ersten Version bewusst nicht vorgesehen. Insbesondere wird hier nicht zwischen Wortliste und Satzliste unterschieden. Diese Differenzierung ist für den Einstieg nicht nötig und würde die Seite unnötig verkomplizieren.

## Listenübersicht

Unter der Steuerzeile folgt direkt eine durchgehende, ruhige Listenansicht mit schlanken Karten oder Zeilenkarten.

Es gibt keine getrennten Gruppen für kuratierte und eigene Listen. Die Unterscheidung erfolgt allein über einen klar sichtbaren Status-Badge auf jeder Karte. Das reicht aus und vermeidet leere oder künstlich getrennte Bereiche.

Jede Listenkarte hat genau drei inhaltliche Zeilen plus Aktionen.

### Zeile 1

Titel der Liste

Beispiel:

Frageintonation und Fokus

### Zeile 2

Metazeile mit Anzahl und Status

Beispiel:

6 Items · curated

oder

6 Items · custom

Der Status erscheint als Badge und darf farblich unterschieden sein. Die Farbgebung soll ruhig und systematisch sein, nicht dekorativ.

- `curated` = kuratierte Vorlage
- `custom` = eigene Liste

### Zeile 3

Eine einzelne Vorschauzeile mit ausgewählten Items, geclamppt und sauber abgeschnitten.

Beispiel:

30 usted · 38 vino · 49 ahí · 67 tampoco

Keine mehrzeiligen Mini-Listen, keine langen Beschreibungen, keine Vorschaukästen.

## Aktionen pro Karte

Die Karten haben klare, knappe Aktionen.

### Für curated-Listen

Primäraktionen:

- Öffnen
- Modifizieren

„Modifizieren“ ist bewusst nutzerzentriert formuliert. Gemeint ist: Diese kuratierte Liste als Ausgangspunkt verwenden und in eine eigene bearbeitbare Version überführen. Technisch kann dabei im Hintergrund automatisch eine neue `custom`-Liste erzeugt werden.

Kuratierte Listen sind nicht löschbar.

### Für custom-Listen

Primäraktion:

- Öffnen

Alternativ, falls im Wording konsistenter:

- Bearbeiten

Sekundäraktion über Overflow-Menü:

- Umbenennen
- Löschen

Eigene Listen sollen löschbar sein, aber nicht über einen auffälligen Hauptbutton in jeder Karte. Die Löschfunktion gehört ins sekundäre Menü, damit die Übersicht ruhig bleibt und Fehlklicks vermieden werden.

## Löschen von custom-Listen

Nur `custom`-Listen können gelöscht werden.

Die Aktion liegt im Overflow-Menü der jeweiligen Karte. Nach Auswahl erscheint ein Bestätigungsdialog.

Beispieltext:

Custom-Liste löschen?  
„Meine Fokusauswahl“ wird dauerhaft entfernt.

Buttons:

- Abbrechen
- Löschen

Kuratierte Listen können nicht gelöscht werden.

## Was auf dieser Seite bewusst nicht vorkommt

Folgende Elemente gehören nicht auf `research/phenomena`, weil sie die Einstiegsseite wieder überladen würden:

- keine aktive Auswahl als eigener Block
- keine Materialkonfiguration
- kein Task-Katalog
- keine inhaltliche Bearbeitung von Items
- kein Speichern
- kein Handoff zu Player oder Vergleich
- keine Differenzierung zwischen Wortliste und Satzliste
- keine getrennten Bereiche für curated und custom
- keine langen Beschreibungstexte
- keine großflächigen Kacheln mit viel UI-Text

Diese Seite ist nur der Einstieg. Alles, was inhaltlich mit einer konkreten Liste gearbeitet wird, gehört auf eine separate Bearbeitungs-Unterseite.

## Zustände am Seitenende

Nach der Listenübersicht folgt nur noch das funktionale Seitenende.

Je nach Datenlage braucht die Seite hier:

- „Mehr laden“ oder Pagination, falls viele Listen vorhanden sind
- saubere Empty States bei leerer Suche oder noch fehlenden Ergebnissen

Beispiele:

- „Keine Listen gefunden.“
- „Erstellen Sie eine neue Liste.“

Weitere inhaltliche Blöcke folgen nicht.

## Zielbild

Die Seite soll am Ende so wirken:

- ruhig
- schnell erfassbar
- einspaltig bzw. klar linear
- ohne konkurrierende Einstiege
- ohne konzeptionellen Ballast
- ähnlich schlank wie die Sprecherlisten im Vergleich

Der Einstieg muss sofort verständlich sein: Ich sehe vorhandene Listen, erkenne ihren Status, kann eine öffnen, eine kuratierte Vorlage modifizieren oder eine neue Liste anlegen.

## Bearbeitungs-Unterseite einer konkreten Liste

Die Bearbeitung einer konkreten Liste erfolgt nicht auf `research/phenomena`, sondern auf einer separaten Unterseite der jeweiligen Liste. Diese Seite ist der eigentliche Arbeitsbereich.

Ziel der Unterseite ist es, in maximal klarer Form drei Dinge zu ermöglichen:

- Items auswählen
- Kommentar und Titel pflegen
- Reihenfolge der ausgewählten Items festlegen und speichern

## Grundstruktur der Seite

Die Seite ist klar von oben nach unten aufgebaut:

1. Kopfbereich mit Titel, Status und Hauptaktionen
2. Kommentarfeld
3. Zwei Spalten mit vollständigem Materialbestand
4. Bereich „Ausgewählte Items“ zur Sortierung und Kontrolle
5. destruktive oder verwerfende Aktionen am unteren Ende bzw. im Kopfbereich klar eingeordnet

Die Seite soll optisch stark an den Player erinnern, aber ohne dessen Audio- oder Abspielfunktionen.

## Kopfbereich

Oben steht der Titel des Sets.

Dazu gehören folgende Funktionen:

- Titel anzeigen
- Titel umbenennen
- Speichern

Ein zusätzliches „Speichern als“ ist nicht nötig.

### Automatische Benennung

Für neue freie Sets wird automatisch ein nachvollziehbarer Name vergeben:

- `Neues Set 1`
- `Neues Set 2`
- `Neues Set 3`

fortlaufend, falls bereits vorhanden.

Für die Bearbeitung eines kuratierten Sets wird automatisch ein abgeleiteter Name vergeben:

- `Originaltitel (modifiziert)`

Technisch kann intern weiterhin ein anderer Key oder Slug verwendet werden, aber sichtbar im UI sollte die Benennung lesbar und nicht technisch wirken.

### Status

Im Kopfbereich soll der aktuelle Zustand klar sichtbar sein, nicht nur über kurz eingeblendete Rückmeldungen.

Sinnvolle Zustände sind:

- `neu`
- `ungespeichert`
- `gespeichert`
- `curated`
- `custom`

Eine Snackbar nach erfolgreichem Speichern ist zusätzlich sinnvoll, ersetzt aber nicht den sichtbaren Status.

### Hinweis bei kuratierten Sets

Wenn ein kuratiertes Set bearbeitet wird, erscheint unter Titel und Status ein klarer Hinweis:

Änderungen an dieser kuratierten Vorlage werden als neues eigenes Set gespeichert.

Damit ist eindeutig, dass die Vorlage selbst nicht überschrieben wird.

## Kommentarfeld

Unterhalb des Kopfbereichs und oberhalb der Materiallisten steht ein kleines Freitextfeld für Kommentar oder Notiz.

Label z. B.:

Kommentar

oder

Notiz

Dieses Feld ist Teil des Sets und wird mitgespeichert. Es dient für Arbeitsnotizen und kann später ggf. auch in anderen Bereichen weiterverwendet werden.

## Materialbereich

Darunter folgt der Hauptbereich mit zwei Spalten.

### Linke Spalte

Gesamte Wortliste

### Rechte Spalte

Gesamte Satzliste bzw. alle nummerierten Satz-Items

Beide Spalten zeigen den vollständigen verfügbaren Materialbestand in stabiler, kanonischer Reihenfolge. Diese Reihenfolge bleibt in den Quelllisten unverändert und dient nur der Orientierung und Auswahl.

Die beiden oberen Listen sind keine Sortierflächen.

## Suche

Über jeder Spalte steht ein eigenes Suchfeld.

Die Suche ist als einfache Volltextsuche gedacht und soll Zeichenfolgen direkt im Itemtext auffindbar machen.

Beispiele:

- `rr`
- `ch`
- `ll`
- `gue`

So lassen sich Items auch nach Buchstabenfolgen oder lautbezogenen Mustern schnell finden.

## Auswahlverhalten

Die Auswahl erfolgt direkt in den beiden Materialspalten.

### Bei neuen Listen

Alle Items starten zunächst als nicht ausgewählt und werden visuell muted dargestellt.

Durch Klick auf ein Item oder durch ein klares Auswahl-Element wie Checkbox oder Häkchen wird das Item dem Set hinzugefügt.

Das Item erscheint dann visuell unmuted bzw. hervorgehoben.

Ein erneuter Klick entfernt es wieder aus der Auswahl.

### Bei bestehenden custom-Listen

Bereits enthaltene Items sind beim Laden der Seite schon aktiv und entsprechend unmuted dargestellt.

### Bei bearbeiteten curated-Listen

Die in der Vorlage enthaltenen Items sind beim Laden ebenfalls schon aktiv. Änderungen daran werden aber nicht auf die kuratierte Vorlage selbst geschrieben, sondern in ein neues eigenes Set überführt.

## Zusätzliche Kleinaktionen pro Spalte

Oberhalb oder innerhalb jeder Spalte können kleine Hilfsaktionen vorgesehen werden:

- Alle auswählen
- Alle abwählen

Diese Aktionen sind nützlich, sollen aber nicht visuell dominieren.

## Ausgewählte Items

Unterhalb der beiden Materialspalten folgt ein eigener Bereich mit der Überschrift:

Ausgewählte Items

Dieser Bereich zeigt nur die aktuell im Set enthaltenen Items.

Er erfüllt drei Funktionen zugleich:

- Kontrolle der aktuellen Auswahl
- gemeinsamer Überblick über Wort- und Satz-Items
- Änderung der Reihenfolge

### Gemeinsame Reihenfolge

Die Reihenfolge ist eine gemeinsame Reihenfolge über alle ausgewählten Items hinweg, nicht getrennt nach Wort- und Satzmaterial.

Beispiel:

1. Wort 30
2. Wort 38
3. Satz 101
4. Satz 108

Diese Reihenfolge wird explizit gespeichert und nicht aus den beiden oberen Quellspalten abgeleitet.

### Sortierung

Die Sortierung erfolgt ausschließlich im Bereich „Ausgewählte Items“.

Empfohlen ist eine robuste Drag-and-drop-Lösung mit Drag Handle pro Zeile, sofern technisch stabil und einfach umsetzbar.

Jede Zeile sollte dabei weiterhin klar erkennbar machen:

- Nummer
- Text
- Typ, z. B. `Wort` oder `Satz`
- Drag Handle
- Aktion zum Entfernen aus der Auswahl

Das Entfernen eines Items aus der Auswahl muss auch hier möglich sein, nicht nur oben in den Quelllisten.

### Leerer Zustand

Wenn noch keine Items ausgewählt wurden, zeigt der Bereich eine klare Leermeldung, z. B.:

Noch keine Items ausgewählt.

## Speichern, Verwerfen, Löschen

Die verfügbaren Aktionen hängen vom Status des Sets ab.

### Bei neuem oder noch nicht gespeicherten Set

- Speichern
- Entwurf verwerfen

### Bei bestehendem custom-Set

- Speichern
- Set löschen

### Bei bearbeiteter curated-Vorlage

- Speichern
- Entwurf verwerfen, solange noch keine eigene gespeicherte Version entstanden ist

Die kuratierte Vorlage selbst kann nicht gelöscht und nicht direkt überschrieben werden.

## Löschen eines custom-Sets

Bestehende eigene Sets können gelöscht werden.

Die Löschung erfolgt nicht ohne Bestätigung.

Beispieltext:

Custom-Liste löschen?  
„Meine Fokusauswahl“ wird dauerhaft entfernt.

Buttons:

- Abbrechen
- Löschen

## Warnung bei ungespeicherten Änderungen

Wenn ungespeicherte Änderungen vorliegen und die Seite verlassen, zurück navigiert oder ein anderes Set geöffnet wird, muss eine Warnung erscheinen.

Beispiel:

Ungespeicherte Änderungen verwerfen?

So wird verhindert, dass Arbeit versehentlich verloren geht.

## Was auf dieser Seite bewusst nicht vorkommt

Auch auf der Bearbeitungsseite sollen einige Dinge bewusst nicht auftauchen:

- keine Playerfunktionen
- keine Audioelemente
- kein Handoff zu Vergleich oder Player in dieser ersten Konzeption
- keine Sortierung direkt in den beiden oberen Quelllisten
- kein technisch klingendes Naming im sichtbaren UI
- kein überladener Mehrspalten-Kontrollbereich jenseits der klaren Zweispaltenlogik plus Auswahlbereich unten

## Datenmodell, das dafür mitgedacht werden muss

Für die Datenbank bzw. das Set-Modell muss diese Seite mindestens folgende Informationen sauber ablegen können:

- Titel des Sets
- Status bzw. Typ des Sets, etwa `curated` oder `custom`
- Herkunft eines modifizierten curated-Sets
- Kommentar / Notiz
- ausgewählte Item-IDs
- gemeinsame Reihenfolge der ausgewählten Items

Gerade Kommentar und gemeinsame Reihenfolge müssen explizit mitgedacht und bei Bedarf im Datenmodell ergänzt werden.

## Zielbild

Die Bearbeitungs-Unterseite soll sich am Ende so anfühlen:

- oben klarer Arbeitskopf
- darunter ruhige Materialauswahl in zwei stabilen Quellspalten
- unten ein eigener Bereich für die tatsächlich gewählten Items
- einfache Auswahl durch muted/unmuted-Logik
- nachvollziehbares Speichern
- sichere Behandlung von ungespeicherten Änderungen
- klare Trennung zwischen Materialbestand und Set-Reihenfolge

So bleibt die Seite verständlich und arbeitsfähig, ohne wieder in mehrere konkurrierende Logiken zu zerfallen.