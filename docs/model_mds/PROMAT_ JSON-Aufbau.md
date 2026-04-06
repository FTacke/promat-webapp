---
tags: promat, Pronunciation Matters, Datenstruktur, Informanten, Intake
---

# PROMAT: JSON-Aufbau

## Festlegung zur Zeitannotation, Audio-Ableitung und JSON-Codierung für Player-Daten

### Ziel

Für den Research-Player werden Audio- und Strukturdaten so aufbereitet, dass

- die grobe Navigation über stabile Einheiten wie Wortlisten-Items, Satz-Items oder Interviewsegmente erfolgt,
- die laufende Synchronisierung im Player auf timingtragenden Einheiten basiert,
- die Produktionspipeline weitgehend automatisiert bleibt,
- unnötige Datenredundanz vermieden wird,
- Web-Derivate konsistent und vergleichbar abspielbar sind.

Die JSON-Struktur soll deshalb zwischen führenden Containern und feineren timingtragenden Einheiten unterscheiden. Zugleich müssen die Audio-Derivate so erzeugt werden, dass sie für Player, Vergleichsansichten und Downloads robust nutzbar sind.

---

## 1. Grundprinzip

### 1.1 Führende Container-Ebene

Je nach Task gibt es eine führende Ebene für Navigation, Nummerierung und UI-Darstellung:

- `wordlist`: `items`
- `text`: `items`
- `interview`: `segments`

Diese Ebene ist die fachlich sichtbare Grundstruktur im Player.

### 1.2 Timingtragende Einheiten

Die laufende Synchronisierung basiert auf timingtragenden Render-Einheiten.

Diese können je nach Task unterschiedlich ausfallen:

- bei `wordlist` meist direkt das Item selbst
- bei `text` in der Regel untergeordnete `tokens`
- bei `interview` optional `tokens`, sonst Fallback auf Segmentebene

Dadurch bleibt die Architektur einheitlich, ohne dass alle Tasks künstlich dieselbe Rohdatenstruktur erzwingen müssen.

---

## 2. Festlegung zur automatischen Zeitannotation

### 2.1 Satzlisten- und Textdaten

Bei `text`-Daten werden die Satz-Items zunächst über die standardisiert eingefügten Pausen segmentiert. Die bereits vorgesehenen 0,5-Sekunden-Pausen dienen dabei ausschließlich der robusten Abgrenzung von Satz-Items.

Sie dienen nicht der wortweisen Feinalignment-Logik.

Die Wortzeiten innerhalb eines Satz-Items werden anschließend automatisch erzeugt:

1. Satz-Items anhand der standardisierten Pausen schneiden
2. Jedem Satz-Item den kanonischen Soll-Text zuordnen
3. Für jedes Satz-Item ein wortweises forced alignment durchführen
4. Die resultierenden Wortzeiten als `tokens[]` in das jeweilige `text`-Item schreiben

### 2.2 Primärverfahren

Das verbindliche Primärverfahren für die automatische Wortzeitannotation in `text` ist:

- Montreal Forced Aligner (`MFA`)

MFA wird für kontrollierte Lesedaten mit bekanntem Soll-Text als Standardverfahren verwendet.

### 2.3 Fallback

Wenn MFA in einem konkreten Verarbeitungsschritt kein belastbares Ergebnis liefert oder technisch nicht sinnvoll eingesetzt werden kann, ist als Fallback zulässig:

- WhisperX

WhisperX ist kein Primärstandard, sondern ein technischer Ersatzpfad für automatische Tokenzeiten.

### 2.4 Manuelle Nacharbeit

Vollständige händische Wortannotation in Praat ist nicht der Standardprozess.

Manuelle Nacharbeit ist auf Ausnahmefälle zu beschränken. Dazu werden problematische Fälle automatisiert markiert, zum Beispiel:

- fehlende Tokenzeiten
- unplausible Dauern
- nicht monotone Zeitreihen
- abgebrochene Alignments
- deutliche Abweichung zwischen Soll-Text und Alignment-Ergebnis

Nur diese Ausnahmefälle werden gezielt geprüft und bei Bedarf nachkorrigiert.

---

## 3. Festlegung zu Zeitwerten und Rundung

### 3.1 Kanonische Annotationsgrenzen

Die kanonischen Zeitgrenzen eines Items, Tokens oder Segments werden aus den zugrunde liegenden Annotationen übernommen.

Für `wordlist` sind dies die eigentlichen Item-Grenzen aus dem TextGrid. Diese Grenzen bleiben die fachlich gültigen Werte für Player-Synchronisierung, Hervorhebung und interne Logik.

Sie werden nicht durch Export-Komfortregeln für Split-Dateien verändert.

### 3.2 Rundung von TextGrid-Zeitwerten

TextGrid-Dateien können sehr viele Nachkommastellen enthalten. Für die weitere Verarbeitung gilt:

- Zeitwerte aus dem TextGrid werden vor der JSON-Erzeugung auf vier Nachkommastellen gerundet
- weitergehende Nachkommastellen werden regulär weggerundet
- die gerundeten Werte sind die Grundlage für die JSON-Zeitfelder und für die Split-Produktion

Die Rundung dient der technischen Konsistenz und verändert nicht die fachliche Rolle der annotierten Grenzen.

---

## 4. Festlegung zu Audio-Derivaten

### 4.1 Grundregel

`raw/` und `source/` bleiben unverändert.

Audio-Anpassungen für Web-Nutzung und Player-Komfort erfolgen ausschließlich auf den Derivaten:

- `derived/{task}.mp3`
- daraus abgeleitete `items/{task}/{item_id}.mp3`

### 4.2 Full-MP3 als Primärartefakt

Für jeden Task ist das primäre Web-Audio:

- `derived/{task}.mp3`

Dieses Full-MP3 ist die grundlegende Playback-Datei für den Player.

### 4.3 Konstante Bitrate

Für text-audio-synchrones Verhalten und reproduzierbare Player-Nutzung werden die Web-Derivate mit konstanter Bitrate erzeugt.

Das gilt für:

- `derived/{task}.mp3`
- `items/{task}/{item_id}.mp3`

### 4.4 Lautheitsstandardisierung

Für Vergleichbarkeit und angenehme Web-Wiedergabe wird das Full-MP3 auf Derivat-Ebene lautheitsstandardisiert.

Dafür gilt:

- Lautheitsstandardisierung erfolgt nur auf `derived/{task}.mp3`
- `raw/` und `source/` bleiben unangetastet
- Split-MP3s werden aus dem bereits standardisierten Full-MP3 erzeugt
- Einzelne Split-MP3s werden nicht nochmals separat pro Item normalisiert

Damit bleiben die Relationen der Items innerhalb einer Aufnahme konsistent.

### 4.5 Split-MP3 mit Komfort-Padding

Wenn Split-MP3s erzeugt werden, erhalten sie standardmäßig Komfort-Padding:

- `250 ms` vor der kanonischen Startgrenze
- `250 ms` nach der kanonischen Endgrenze

Das dient ausschließlich dem robusten Standalone-Abspielen und Download-Komfort.

Dabei gilt:

- die kanonischen `start_ms`- und `end_ms`-Werte im JSON bleiben unverändert
- das Padding verändert nicht die eigentlichen Annotationsgrenzen
- Split-Grenzen werden an die Dateigrenzen geklammert, also nie kleiner als `0` und nie größer als die Audiolänge

---

## 5. Gemeinsame Hüllstruktur von `alignment/{task}.json`

Jede Player-/Alignment-JSON verwendet denselben gemeinsamen Top-Level-Rahmen.

### 5.1 Verbindliche Top-Level-Felder

```json
{
  "session_id": "ES-L-0001-2027-S02",
  "person_id": "ES-L-0001",
  "task": "text",
  "audio": {
    "full_mp3": "derived/text.mp3"
  }
}
````

### 5.2 Pflichtfelder auf Top-Level

Verbindlich vorhanden sein müssen mindestens:

* `session_id`
* `person_id`
* `task`
* `audio.full_mp3`

### 5.3 Task-spezifische Mindeststruktur

Zusätzlich gilt:

* `wordlist` muss `items` enthalten
* `text` muss `items` enthalten
* `interview` muss `segments` enthalten

Es ist nicht erforderlich, dass jede JSON-Datei zugleich immer `items` und `segments` trägt.

Leere Platzhalterstrukturen nur der formalen Gleichförmigkeit halber sollen nicht erzeugt werden.

---

## 6. JSON-Vertrag für `wordlist`

### 6.1 Führende Struktur

`wordlist` ist item-zentriert.

Ein Item ist ein fachlicher Wortlisten-Eintrag mit stabiler Nummerierung und stabiler `item_id`.

### 6.2 Nummerierung der Wortliste

Die Wortlisten-Nummerierung ist Produktionsdatenlogik.

Für den aktuellen Fall gilt:

* `item_number` wird aus der Reihenfolge der nicht-silence-Intervalle im `wordlist.TextGrid` abgeleitet
* führende, zwischenliegende und abschließende Stilleintervalle sind keine Items
* die verbleibenden gesprochenen Intervalle werden in ihrer Reihenfolge nummeriert

Wenn die Wortliste korrekt im TextGrid vorliegt, ist dafür keine zusätzliche separate Nummerierungsliste erforderlich.

### 6.3 Mindestfelder pro Item

```json
{
  "item_id": "wl_002",
  "item_number": "2",
  "text": "reloj",
  "start_ms": 3100,
  "end_ms": 4020,
  "split_mp3": "items/wordlist/wl_002.mp3"
}
```

Verbindliche Mindestfelder:

* `item_id`
* `item_number`
* `text`
* `start_ms`
* `end_ms`
* `split_mp3`

Optionale Felder:

* `label`
* `tokens`
* `split_padding_ms_before`
* `split_padding_ms_after`

### 6.4 Korrespondenz zu Split-MP3

Für `wordlist` wird die JSON grundsätzlich mit expliziter Korrespondenz zur Split-Datei erzeugt.

Das heißt:

* jedes Wortlisten-Item trägt einen `split_mp3`-Pfad
* der Pfad verweist auf die aus genau diesem Item erzeugte Split-Datei
* das Split-MP3 ist ein sekundäres Arbeits- und Download-Artefakt auf Basis desselben Items

### 6.5 Keine redundanten Dubletten erzwingen

Wenn ein Wortlisten-Item genau einer timingtragenden Einheit entspricht, müssen keine zusätzlichen `tokens` mit identischen Werten gespeichert werden.

Das heißt:

* kein doppeltes `text`
* kein doppeltes `start_ms`
* kein doppeltes `end_ms`

nur um formal eine zweite Ebene zu erzeugen.

### 6.6 Player-interne Ableitung

Wenn ein Wortlisten-Item keine `tokens` besitzt, darf der Player intern aus dem Item selbst eine timingtragende Render-Einheit ableiten.

### 6.7 Beispiel

```json
{
  "session_id": "ES-L-0001-2027-S02",
  "person_id": "ES-L-0001",
  "task": "wordlist",
  "audio": {
    "full_mp3": "derived/wordlist.mp3"
  },
  "items": [
    {
      "item_id": "wl_001",
      "item_number": "1",
      "text": "mesa",
      "start_ms": 0,
      "end_ms": 820,
      "split_mp3": "items/wordlist/wl_001.mp3",
      "split_padding_ms_before": 250,
      "split_padding_ms_after": 250
    },
    {
      "item_id": "wl_002",
      "item_number": "2",
      "text": "reloj",
      "start_ms": 1400,
      "end_ms": 2320,
      "split_mp3": "items/wordlist/wl_002.mp3",
      "split_padding_ms_before": 250,
      "split_padding_ms_after": 250
    }
  ]
}
```

---

## 7. JSON-Vertrag für `text`

### 7.1 Führende Struktur

`text` bleibt technisch immer der Task-Key `text`.

Die führende Container-Ebene sind `items`.

Ein `item` ist ein Satz oder eine andere definierte Texteinheit.

Diese Struktur gilt sowohl für Satzlisten-Ansicht als auch für Fließtext-Ansicht.

### 7.2 Ziel der Struktur

`text` muss zugleich ermöglichen:

* stabile Satz- oder Einheiten-Nummerierung
* ruhige Listen- oder Fließtextdarstellung
* wortgenaue Synchronisierung im Player

Deshalb werden Satz-Items mit untergeordneten `tokens[]` kombiniert.

### 7.3 Mindestfelder pro `text`-Item

```json
{
  "item_id": "d1",
  "item_number": "D1",
  "text": "Hoy miro el reloj con calma antes de salir.",
  "start_ms": 0,
  "end_ms": 4200,
  "tokens": []
}
```

Verbindliche Mindestfelder:

* `item_id`
* `item_number`
* `text`
* `start_ms`
* `end_ms`

`tokens` sollen bei vorhandenem Wortalignment ergänzt werden und sind für die bevorzugte Player-Synchronisierung vorgesehen.

### 7.4 Mindestfelder pro Token

```json
{
  "token_id": "d1_t4",
  "text": "reloj",
  "start_ms": 930,
  "end_ms": 1480
}
```

Verbindliche Mindestfelder pro Token:

* `token_id`
* `text`
* `start_ms`
* `end_ms`

Optionale Felder:

* `wordlist_item_ref`
* `label`
* weitere linguistische Zusatzfelder, falls später benötigt

### 7.5 Verknüpfung zur Wortliste

Tokens in `text` können optional `wordlist_item_ref` tragen.

Dieses Feld verweist auf eine kanonische `item_id` aus der Wortliste.

Beispiel:

```json
{
  "token_id": "d1_t4",
  "text": "reloj",
  "start_ms": 930,
  "end_ms": 1480,
  "wordlist_item_ref": "wl_002"
}
```

Damit können Wortvorkommen in Satzliste oder Fließtext gezielt mit korrespondierenden Wortlisten-Items verknüpft werden.

Diese Referenz ist optional. Nicht jedes Token muss sie tragen.

### 7.6 Beispiel

```json
{
  "session_id": "ES-L-0001-2027-S02",
  "person_id": "ES-L-0001",
  "task": "text",
  "audio": {
    "full_mp3": "derived/text.mp3"
  },
  "items": [
    {
      "item_id": "d1",
      "item_number": "D1",
      "text": "Hoy miro el reloj con calma antes de salir.",
      "start_ms": 0,
      "end_ms": 4200,
      "tokens": [
        {
          "token_id": "d1_t1",
          "text": "Hoy",
          "start_ms": 0,
          "end_ms": 250
        },
        {
          "token_id": "d1_t2",
          "text": "miro",
          "start_ms": 310,
          "end_ms": 760
        },
        {
          "token_id": "d1_t3",
          "text": "el",
          "start_ms": 800,
          "end_ms": 900
        },
        {
          "token_id": "d1_t4",
          "text": "reloj",
          "start_ms": 930,
          "end_ms": 1480,
          "wordlist_item_ref": "wl_002"
        },
        {
          "token_id": "d1_t5",
          "text": "con",
          "start_ms": 1540,
          "end_ms": 1760
        }
      ]
    }
  ]
}
```

---

## 8. JSON-Vertrag für `interview`

### 8.1 Führende Struktur

`interview` ist segment-zentriert.

Ein `segment` ist ein Sprecherturn oder ein anderer definierter Interviewabschnitt.

### 8.2 Mindestfelder pro Segment

```json
{
  "segment_id": "seg_001",
  "segment_number": "1",
  "speaker_code": "A",
  "text": "Bueno, primero estudié español en la escuela.",
  "start_ms": 0,
  "end_ms": 3100
}
```

Verbindliche Mindestfelder:

* `segment_id`
* `segment_number`
* `speaker_code`
* `text`
* `start_ms`
* `end_ms`

Optionale Felder:

* `tokens`
* `label`

### 8.3 Tokens im Interview

Wenn gutes Wortalignment vorliegt, können Segmente untergeordnete `tokens[]` tragen.

Wenn keine belastbaren Tokenzeiten vorliegen, bleibt segmentbasiertes Verhalten zulässig.

### 8.4 Beispiel

```json
{
  "session_id": "ES-L-0001-2027-S02",
  "person_id": "ES-L-0001",
  "task": "interview",
  "audio": {
    "full_mp3": "derived/interview.mp3"
  },
  "segments": [
    {
      "segment_id": "seg_001",
      "segment_number": "1",
      "speaker_code": "A",
      "text": "Bueno, primero estudié español en la escuela.",
      "start_ms": 0,
      "end_ms": 3100,
      "tokens": [
        {
          "token_id": "seg_001_t1",
          "text": "Bueno",
          "start_ms": 0,
          "end_ms": 420
        },
        {
          "token_id": "seg_001_t2",
          "text": "primero",
          "start_ms": 560,
          "end_ms": 1120
        }
      ]
    }
  ]
}
```

---

## 9. Player-interne Normalisierung

Die Produktionsdaten dürfen unterschiedlich fein sein.

Der Player darf und soll diese Daten intern auf eine gemeinsame Render- und Sync-Logik normalisieren.

### 9.1 Zulässige Normalisierung

* `wordlist` ohne `tokens`:

  * das Item selbst wird intern zur timingtragenden Einheit
* `text` mit `tokens`:

  * die Tokens werden timingtragende Einheiten
* `interview` ohne `tokens`:

  * Segment-Fallback bleibt gültig

### 9.2 Ziel

Diese Normalisierung dient dazu,

* die JSON-Dateien schlank zu halten,
* unnötige Redundanz zu vermeiden,
* trotzdem eine einheitliche Player-Architektur zu ermöglichen.

---

## 10. Nummerierung

Nummerierungen sind Produktionsdaten.

Das gilt insbesondere für:

* `item_number` in `wordlist`
* `item_number` in `text`
* `segment_number` in `interview`

Diese Nummerierungen werden aus den Quelldaten oder der Produktionspipeline übernommen.

Sie werden nicht frei im Web-UI synthetisiert.

Auch in der Fließtext-Ansicht dürfen Satz- oder Segmentnummern sichtbar bleiben, jedoch ruhig und zurückhaltend.

---

## 11. Verhältnis von Voll-MP3 und Split-MP3

Für alle Tasks gilt:

* primäre Playback-Grundlage ist das Vollaudio unter `derived/{task}.mp3`
* Split-Dateien unter `items/{task}/{item_id}.mp3` sind sekundäre Arbeits- und Download-Artefakte

Der Player muss mit Voll-MP3 plus Alignment-JSON funktionsfähig bleiben, auch wenn Split-MP3s noch nicht vollständig vorliegen.

Wenn Split-MP3s vorhanden sind, dürfen sie für Einzeldownloads und punktuelle Einzelwiedergabe genutzt werden.

Wenn Split-Dateien produziert werden, soll die JSON eine explizite Korrespondenz zu diesen Artefakten tragen.

---

## 12. Zusammenfassung der Festlegung

Für PROMAT gilt damit:

* `wordlist` ist item-zentriert und braucht keine redundanten Tokens, wenn das Item selbst bereits die timingtragende Einheit ist
* `text` ist ebenfalls item-zentriert, enthält aber idealerweise untergeordnete Tokens für wortgenaue Synchronisierung
* `interview` ist segment-zentriert und kann optional Tokens tragen
* die automatische Wortzeitannotation in `text` erfolgt primär mit MFA
* WhisperX ist ein zulässiger Fallback
* manuelle Nacharbeit bleibt auf problematische Ausnahmefälle beschränkt
* `wordlist_item_ref` erlaubt optionale Verknüpfungen zwischen Tokens in `text` und kanonischen Wortlisten-Items
* der Player darf unterschiedlich feine Eingangsdaten intern in eine gemeinsame Sync-Struktur normalisieren
* die annotierten `start_ms`- und `end_ms`-Werte bleiben die kanonischen fachlichen Grenzen
* Komfort-Padding für Split-MP3s verändert diese Grenzen nicht
* Web-Derivate werden mit konstanter Bitrate erzeugt
* Lautheitsstandardisierung erfolgt nur auf Derivat-Ebene und nicht auf `raw/` oder `source/`
