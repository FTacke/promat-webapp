---
tags: promat, Pronunciation Matters, Datenstruktur, Informanten, Intake
---

# PROMAT: Interview-Pipeline via Amberscript

## 1. Geltungsbereich und Grundentscheidung

| Bereich | Festlegung |
|---|---|
| Ziel des Interview-Transkripts | Das Interview dient primär der **inhaltlichen Erfassung** der Reflexionen der Informant:innen über `wordlist`, `text` und die eigene Aussprache. Nicht die gesprochene Interaktion selbst, sondern der **Inhalt** steht im Vordergrund. |
| Projektstandard | Grundlage ist **Variante 1: Dresing/Pehl, inhaltsorientiert**, ergänzt um genau vier Zusatzphänomene. |
| Zusatzphänomene | 1. **Fülllaute**  2. **Selbstkorrekturen / Abbrüche**  3. **relevante kurze Pausen**  4. **relevantes Lachen / Seufzen** |
| Detaillierungsgrad | **Nicht ultra-fein**. Keine gesprächsanalytische Feinnotation, keine prosodische Feincodierung, keine phonetische Detailtranskription. |
| Langfristige Anschlussfähigkeit | Eine **TEI-Exportoption** kann später als Webapp-Feature ergänzt werden, ist aber **nicht Teil der aktuellen Pipeline**. |

## 2. Grundprinzipien der Transkription

| Thema | Regel |
|---|---|
| Primäres Ziel | Das Transkript soll **gut lesbar**, **konsistent** und **inhaltlich auswertbar** sein. |
| Orthographie | Grundsätzlich **Standardschreibung**, soweit dies für Interviews mit Inhaltsfokus sinnvoll ist. |
| Segmentierung | Automatisch erzeugte Satzgrenzen und Interpunktion werden nicht blind übernommen, sondern an die tatsächliche Äußerungsstruktur angepasst. |
| Fülllaute | Werden **mitgeschrieben**, wenn sie als Zögern, Unsicherheit, Nachdenken oder Gesprächssignal hörbar relevant sind. |
| Hörersignale | Werden nur dann mitgeschrieben, wenn sie einen eigenen Turn bilden oder den Gesprächsverlauf erkennbar mitsteuern. |
| Lachen / Seufzen | Werden nur dann markiert, wenn sie die Äußerung erkennbar färben oder interpretativ relevant sind. |
| Pausen | Es werden nur **relevante kurze Pausen** markiert, nicht jede Mikro-Unterbrechung. |
| Feinzeichen | Keine Jefferson-Notation, keine differenzierte Pausenlänge wie `(0.4)`, keine detaillierte Lautstärke-, Dehnungs- oder Betonungsnotation. |
| Normalisierung | Schreibungen werden auf wenige **kanonische Formen** reduziert, damit die Transkripte konsistent bleiben. |

## 3. Kanonische Schreibweisen: Glossar

| Funktion | Kanonische Form | Verwendung | Normalisiert aus |
|---|---|---|---|
| kurzer Zögerlaut | `äh` | kurzes Zögern, kurzes Suchen | `öh`, `eh`, `uh`, `ähh`, `ööh` |
| längerer Zögerlaut | `ähm` | längeres Zögern, Planungszeit | `öhm`, `ehm`, `uhm`, `ähmm`, `äääähm` |
| nachdenkliches Zögern | `hm` | Nachdenken, Abwägen, suchendes Reagieren | `hmm`, `hmmm`, `mm`, `mhm` sofern nicht bestätigend |
| bestätigendes Hörersignal | `mhm` | Zustimmung, Bestätigung, Mitgehen | `mmh`, `mhmh`, `mhm` |
| Verstehenssignal | `aha` | Einsicht, Verstehen | `ah`, `ahaa` |
| kurzes Lachen | `((lacht kurz))` | kurzes hörbares Lachen mit Relevanz | freie Schreibungen wie `lacht kurz`, `[lacht]`, `*lacht*` |
| Lachen | `((lacht))` | normales Lachen mit Relevanz | freie Varianten |
| Seufzen | `((seufzt))` | hörbares Seufzen mit Relevanz | freie Varianten |

## 4. Notationsregeln für die vier Zusatzphänomene

| Phänomen | Schreibweise | Beispiel | Hinweis |
|---|---|---|---|
| Fülllaut | als normales Wort im Fließtext | `Ja, also ähm, ich glaube ...` | nicht künstlich überdifferenzieren |
| Selbstkorrektur / Abbruch | Gedankenstrich direkt am Abbruch | `Ich ha- ich habe das noch mal gelesen.` | kein Sonderzeichen-Overkill |
| relevante kurze Pause | `(.)` | `Hm, (.) ich weiß es nicht genau.` | nur setzen, wenn relevant |
| relevantes Lachen | `((lacht kurz))` oder `((lacht))` | `Das war, ((lacht kurz)) ehrlich gesagt ungewohnt.` | nur bei interpretativer Relevanz |
| relevantes Seufzen | `((seufzt))` | `((seufzt)) Das war schwierig.` | nur bei interpretativer Relevanz |

## 5. Was ausdrücklich **nicht** gemacht wird

| Nicht vorgesehen | Begründung |
|---|---|
| fein phonologische oder phonetische Transkription | nicht Ziel des Interviewmaterials |
| detaillierte Prosodiemarkierung | für die inhaltliche Auswertung nicht nötig |
| Jefferson-Feinnotation | zu aufwendig, falscher Analysefokus |
| detaillierte Pausenmessung | unnötig für das Projektziel |
| differenzierte Schreibvarianten vieler Fülllaute | verschlechtert Konsistenz |
| erzwungene Mikrogenauigkeit bei allen Wortzeiten | für Interview aktuell nicht erforderlich |

## 6. Amberscript-Workflow

| Schritt | Festlegung |
|---|---|
| 1. Ausgangspunkt | Amberscript-Autotranskript als Rohbasis |
| 2. Editorarbeit | Korrektur im Amberscript-Editor bis zum gewünschten inhaltlichen Zielbild |
| 3. Inhaltliche Korrekturen | Wörter, Fülllaute, Selbstkorrekturen, relevante kurze Pausen sowie relevantes Lachen / Seufzen dürfen direkt im Editor ergänzt oder berichtigt werden |
| 4. Sprecherzuordnung | Falsch erkannte automatische Sprecherzuordnungen werden im Amberscript-Editor manuell korrigiert |
| 5. Interpunktion und Segmentierung | Die automatisch gesetzte Interpunktion wird manuell überarbeitet, da sie oft unpassende oder willkürliche Satzgrenzen setzt; Äußerungen werden so gegliedert, dass sie inhaltlich und prosodisch plausibel bleiben |
| 6. Export | Export als Amberscript-JSON |
| 7. Weiterverarbeitung | Transformation per Script in das kanonische PROMAT-Interview-JSON |
| 8. Rollenverteilung | Amberscript-JSON ist **Rohquelle**, PROMAT-JSON ist **Zielstruktur** |
| 9. Strukturhoheit | **Nicht Amberscript**, sondern **PROMAT** definiert das Zielschema |

### Aktueller Intake-/Working-Bezug

- Der batch-lokale Intake-Eingang bleibt `scripts/research_data_intake/import/{batch_name}/processed/`.
- Das Working-Tree-Ziel für Interview ist aktuell `working/{person_id}/interview/alignment/interview.json` plus `working/{person_id}/interview/source/interview.wav`.
- Für das Working-WAV gilt: zuerst `*_interview_processed.wav`, sonst `*_interview_raw.wav`.
- Für das Amberscript-JSON gilt: zuerst `processed/*_interview_processed.json`, sonst `*_interview_raw.json`.
- Mehrere gleichrangige WAV- oder JSON-Kandidaten sind harte Konflikte; die Pipeline darf diese Zuordnung nicht heuristisch erraten.

## 7. Umgang mit Zeitstempeln nach Editor-Eingriffen

| Thema | Festlegung |
|---|---|
| Beobachtung | Das Einfügen von Füllwörtern im Amberscript-Editor verändert Wortzeiten leicht. |
| Bewertung | Diese leichten Verschiebungen sind **praktisch tolerierbar**. |
| Entscheidung | Es wird **nur eine editierte Exportdatei** verwendet. Ein paralleler Roh-/Edit-Doppel-Export ist **nicht erforderlich**. |
| Konsequenz | Die im Editor leicht modifizierten Zeiten werden **einfach übernommen**. |
| Begründung | Das ist deutlich einfacher und reicht für den aktuellen Interview-Zweck aus. |
| Einschränkung | Die Wortzeiten gelten nicht als phonetisch hochpräzise Feinalignment-Daten, sondern als **arbeitspraktisch ausreichende Tokenzeiten**. |

## 8. Segment- und Wortebene im Zielmodell

| Ebene | Rolle in PROMAT |
|---|---|
| Segmente | Primäre Struktur des Interviews |
| Sprecherwechsel | Müssen sauber erhalten bleiben |
| Wörter / Tokens | Können aus Amberscript übernommen werden, inklusive leicht editierter Zeitstempel |
| Interviewlogik | Das Interview ist **segmentbasiert**, nicht nach dem Muster von `wordlist` oder `text` aufgebaut |
| Navigation | Später primär segmentbasiert, nicht zwingend tokenzentriert |
| Nutzen der Token | Tokens bleiben nützlich für Anzeige, Suche, Hervorhebung und spätere Erweiterungen |

## 9. Praktische Redaktionsregeln für Bearbeiter:innen

| Fall | So transkribieren | Nicht so transkribieren |
|---|---|---|
| kurzer Zögerlaut | `äh` | `öh`, `ähhh`, `öööh` |
| längerer Zögerlaut | `ähm` | `öhm`, `ehm`, `äääähm` |
| nachdenkliches Signal | `hm` | `hmmm`, `hmm` |
| bestätigendes Signal | `mhm` | `mmh`, `mhmh` |
| Pause | `(.)` | `(...)`, `(0.4)` |
| Abbruch | `ich ha- ich habe ...` | `ich ha -- ich habe` |
| Lachen | `((lacht kurz))` | `[lacht]`, `*lacht*` |
| Seufzen | `((seufzt))` | `[seufzt]`, `*seufzt*` |

## 10. Mini-Inventar der erlaubten Sonderformen

| Kategorie | Erlaubte Formen |
|---|---|
| Fülllaute / Signale | `äh`, `ähm`, `hm`, `mhm`, `aha` |
| Pause | `(.)` |
| Abbruch | `Wort-` |
| nonverbal | `((lacht kurz))`, `((lacht))`, `((seufzt))` |

## 11. Beispiele

| Fall | Beispiel |
|---|---|
| Fülllaut | `Ja, also ähm, ich glaube, das war schwierig.` |
| nachdenkliches Zögern | `Hm, ich kann das schwer beschreiben.` |
| Pause | `Hm, (.) ich weiß es nicht genau.` |
| Abbruch | `Ich ha- ich habe es dann noch mal wiederholt.` |
| Lachen | `Das war, ((lacht kurz)) ehrlich gesagt ungewohnt.` |
| Bestätigung | `Mhm, genau das meine ich.` |

## 12. Technische Leitlinie für die Transformationspipeline

| Punkt | Festlegung |
|---|---|
| Quelle | Amberscript-Export-JSON |
| Ziel | kanonisches PROMAT-Interview-JSON |
| Übernahme | Sprecher, Segmente, Token und Zeitstempel werden aus dem editierten Export übernommen |
| Normalisierung | Glossarformen werden in der Transformation auf die kanonischen Schreibweisen vereinheitlicht |
| Bereinigung | Nicht-kanonische Editorformen wie `äääähm` oder `öhhhh` werden zu `ähm` bzw. `äh` normalisiert |
| Struktur | Die Zielstruktur wird so gebaut, dass sie zur PROMAT-Webapp passt, nicht zur Amberscript-Logik |
| TEI | aktuell nicht Teil der Pipeline; später als optionaler Export denkbar |

### Working-Tree-Ziel im aktuellen Intake

- Die erste produktive Zielstufe dieser Transformation ist der batch-lokale Working-Tree, noch nicht `data/sessions/...`.
- Das aktuelle technische Zielartefakt ist `working/{person_id}/interview/alignment/interview.json`.
- Dieses Working-JSON darf `session_id = null` tragen, solange der spätere Produktionsimport die finale Session-Identität noch nicht gesetzt hat.
- `audio.full_mp3` bleibt darin bereits auf den späteren relativen Zielpfad `derived/interview.mp3` normiert.

## 13. Postredaktionelle Referenzannotation bei Materialverweisen

| Punkt | Festlegung |
|---|---|
| Anwendungsfall | Wenn im Interview auf Einheiten des zugrunde liegenden Materials nur indirekt verwiesen wird, etwa durch Angaben wie `Item Nr. 7`, `Nummer 63`, `Satz D5` oder ähnliche Bezeichnungen, kann die konkrete Referenz im Transkript ergänzt werden. |
| Form der Ergänzung | Die Ergänzung erfolgt als **kompakter Marker direkt am referenzierenden Token**. |
| Schreibweise | Standardform ist: `sprechbarer_Anker[item_id]` mit optionaler Schlussinterpunktion am selben Token, zum Beispiel `89[wl_089].`, `D5[d_05]` oder `Nummero [wl_087]`. |
| Beispiele | `... bei Item Nummer 89[wl_089]. ...`  •  `... bei Satz D5[d_05] ...`  •  `... Nummero [wl_087] ...` |
| Zweck | Die Annotation dient der **inhaltlichen Eindeutigkeit** und erleichtert die spätere Auswertung, wenn im Gespräch nur auf Nummern oder Materialpositionen Bezug genommen wird. |
| Grundlage der Annotation | Die Ergänzung erfolgt **manuell** im Editor bzw. in der Postproduktion unter Abgleich mit den **zugrunde liegenden Wortlisten, Satzlisten oder Textmaterialien**; die sichtbare Bezeichnung im PROMAT-JSON wird später ausschließlich aus den kanonischen Task-Katalogen aufgelöst. |
| Status der Annotation | Diese Ergänzungen sind **editorische Annotationen** und nicht Teil der wörtlich gesprochenen Äußerung. |
| Sparsamkeitsprinzip | Solche Annotationen werden nur dort ergänzt, wo die Referenz sonst unklar bliebe oder für das Verständnis bzw. die Auswertung wichtig ist. |
| Konsistenzregel | Für dieselbe Materialeinheit soll projektweit immer dieselbe kanonische Bezeichnung verwendet werden, entsprechend den verbindlichen PROMAT-Materialquellen unter `data/config/research_player/{language}/task_catalogs/`. |

### 13.1 Technische Ausleitung im Working-JSON

- Die kompakten Marker bleiben im Working-JSON nicht als Rohtext erhalten.
- `segment.text` und `tokens[].text` enthalten nur den gesprochenen Ankertext ohne Marker, etwa `89.` statt `89[wl_089].`.
- Die Referenz landet als strukturierte `annotations[]`-Zeile vom Typ `material_ref` mit mindestens `item_id`, `task`, `label`, `item_number`, `canonical_text` und `insert_after_token_id`.
- Wenn der referenzierende Token Schlussinterpunktion trägt, bleibt diese am Tokentext und wird zusätzlich als `trailing_punctuation` markiert, damit spätere UI-Renderer `89 [ahí – allí].` statt `89. [ahí – allí]` bauen können.
- Ungültige Markerformen oder unbekannte `item_id`-Werte sind Fehlerfälle und dürfen nicht als halbaufgelöste Rohannotation in das Working-JSON übernommen werden.

## 14. Kurzfassung der Projektentscheidung

| Bereich | Beschluss |
|---|---|
| Transkriptionsstandard | Dresing/Pehl, **inhaltlich-semantisch**, in projektintern vereinfachter und ergänzter Form |
| Zusätze | Fülllaute, Selbstkorrekturen / Abbrüche, relevante kurze Pausen, relevantes Lachen / Seufzen |
| Glossar | kleines verbindliches Normalisierungsglossar mit kanonischen Schreibweisen |
| Editorpraxis | direkte Bearbeitung im Amberscript-Editor inklusive Korrektur von Sprecherzuordnung, Interpunktion und plausibler Äußerungssegmentierung |
| Postproduktion | bei indirekten Materialverweisen können editorische Kompaktmarker am referenzierenden Token ergänzt werden, z. B. `89[wl_089].` oder `D5[d_05]` |
| Zeitstempel | leicht veränderte Amberscript-Zeiten infolge editorischer Ergänzungen werden akzeptiert |
| Exportpraxis | ein editierter Export genügt |
| Zielmodell | PROMAT-eigenes, kanonisches Interview-JSON |
| TEI | später als Exportoption möglich, aktuell nicht Teil der Pipeline |

## 15. Quellenbezug und projektinterne Modifikation

| Punkt | Festlegung |
|---|---|
| Basissystem | PROMAT orientiert sich für die Interviewtranskription am **Regelsystem für die inhaltlich-semantische Transkription** nach **Dresing/Pehl**. |
| Referenz | **Dresing, Thorsten / Pehl, Thorsten (2024): Praxisbuch Interview, Transkription & Analyse. Anleitungen und Regelsysteme für qualitativ Forschende. 9. Auflage. Marburg.** |
| Stand der referenzierten Regeln | Die auf audiotranskription veröffentlichten **inhaltlich-semantischen Transkriptionsregeln** wurden im November 2022 aktualisiert und in der 9. Auflage des Praxisbuchs veröffentlicht. |
| Projektinterne Modifikation | PROMAT übernimmt den **einfachen, inhaltsorientierten Grundansatz** des Regelsystems, modifiziert ihn aber für die Interview-Pipeline in einem kleinen, verbindlichen Projektschema. |
| Kondensierte Projektmodifikation | Gegenüber dem Basissystem werden in PROMAT **vier Zusatzphänomene systematisch mitgeführt**: **Fülllaute**, **Selbstkorrekturen/Abbrüche**, **relevante kurze Pausen** und **relevantes Lachen/Seufzen**. Diese werden mit wenigen festen, normalisierten Schreibweisen erfasst. |
| Vereinfachungsprinzip | PROMAT verwendet **keine** gesprächsanalytische Feinnotation, **keine** prosodische Feincodierung und **keine** phonetische Detailtranskription. Ziel ist eine **gut lesbare, zuverlässig anwendbare und inhaltlich auswertbare** Interviewtranskription. |
| Technische Umsetzung | Die Bearbeitung erfolgt im **Amberscript-Editor**; die dort edierte Fassung wird als Arbeitsgrundlage exportiert und anschließend per Script in das kanonische PROMAT-Interview-JSON transformiert. |
| Spätere Exportoption | Eine **TEI-Exportierung** kann später ergänzt werden, ist aber **nicht Teil der aktuellen Pipeline**. |

## 16. Metatext für die Webapp

### Kurzfassung (DE)

Die Interviewtranskripte in PROMAT folgen einem **einfachen, inhaltsorientierten Regelsystem in Anlehnung an Dresing/Pehl**. Gegenüber dem Basissystem werden projektintern zusätzlich **Fülllaute**, **Selbstkorrekturen/Abbrüche**, **relevante kurze Pausen** sowie **relevantes Lachen/Seufzen** in standardisierter Form mitgeführt.

### Kurzfassung (EN)

The interview transcripts in PROMAT follow a **simple content-oriented transcription scheme based on Dresing/Pehl**. In addition to the base system, PROMAT systematically retains **filled pauses**, **self-repairs/cut-offs**, **relevant short pauses**, and **relevant laughter/sighing** in a standardized form.

### Vollbeleg für Dokumentation / Impressum / Methodenhinweis

Dresing, Thorsten / Pehl, Thorsten (2024): *Praxisbuch Interview, Transkription & Analyse. Anleitungen und Regelsysteme für qualitativ Forschende.* 9. Auflage. Marburg.

---

# Postproduction zum Ziel-JSON

## 1. Zielprinzip

Das Interview-Ziel-JSON soll **nicht** die Amberscript-Struktur imitieren, sondern sich an den bestehenden PROMAT-JSONs für `wordlist` und `text` orientieren.

Dabei gilt:

- `wordlist` und `text` bleiben **item-basiert**
- `interview` wird **segment-basiert**
- Tokenzeiten aus Amberscript werden, soweit brauchbar, **vereinfacht übernommen**
- editorische Annotationen werden **strukturiert** in das Ziel-JSON überführt
- Amberscript-interne Felder und Unsicherheitswerte werden **nicht** als produktive Webapp-Daten mitgeschleppt

---

## 2. Grundentscheidung zur Zielstruktur

### 2.1 Top-Level

Das Interview-Ziel-JSON soll auf oberster Ebene möglichst nahe an `text.json` und `wordlist.json` bleiben.

**Empfohlenes Top-Level-Minimum:**

- `session_id`
- `person_id`
- `task`
- `audio.full_mp3`
- `segments`

**Optional zusätzlich:**

- `meta`

### 2.2 Task-Wert

Für Interviews ist der technische Task-Wert immer:

- `interview`

### 2.3 Audio-Pfad

Analog zu den anderen Tasks:

- `audio.full_mp3 = "derived/interview.mp3"`

---

## 3. Was aus Amberscript übernommen wird

### 3.1 Amberscript-Quelle

Amberscript liefert im Kern:

- `speakers`
- `segments`
- pro Segment:
  - `speaker`
  - `words`
- pro Wort:
  - `start`
  - `end`
  - `duration`
  - `text`
  - `conf`
  - `pristine`

### 3.2 Relevante Übernahme

Für PROMAT werden davon im Kern nur diese Informationen produktiv gebraucht:

- Sprecherzuordnung
- Segmentreihenfolge
- Wortreihenfolge
- `start`
- `end`
- `text`

---

## 4. Was wegfallen kann

Die folgenden Amberscript-Felder sollen **nicht** in das Ziel-JSON übernommen werden:

| Feld | Grund |
|---|---|
| `id` | Amberscript-interne ID, für PROMAT fachlich nicht relevant |
| `recordId` | Amberscript-intern, keine produktive PROMAT-Bedeutung |
| `filename` | nicht nötig im Alignment-/Player-JSON |
| `startTimeOffset` | aktuell redundant |
| `duration` | aus `start` und `end` ableitbar |
| `conf` | für die Webapp und den produktiven Interview-View nicht relevant |
| `pristine` | nur Amberscript-/Editor-Herkunftsinfo, nicht Teil des Zielcontracts |
| Amberscript-`speakers[].name` | wird durch feste PROMAT-Sprecherrollen ersetzt |

---

## 5. Sprecherlogik im Ziel-JSON

Da im PROMAT-Interview gilt:

- `spk1` = immer **Explorator:in**
- `spk2` = immer **Sprecher:in** / informierende Person

soll die Amberscript-Sprecherlogik im Ziel-JSON **kanonisiert** werden.

### 5.1 Empfehlung

Die Amberscript-Codes `spk1` und `spk2` werden **nicht roh** beibehalten, sondern in stabile PROMAT-Codes umgewandelt:

- `interviewer`
- `participant`

### 5.2 Konsequenz

Eine eigene Amberscript-ähnliche `speakers`-Liste ist im Ziel-JSON **nicht nötig**.

Die Sprecherrolle wird direkt pro Segment über `speaker_code` transportiert.

---

## 6. Segmentstruktur im Ziel-JSON

Jedes editorisch bereinigte Interviewsegment wird ein PROMAT-Segment.

### 6.1 Segment-Minimum

Jedes Segment soll mindestens enthalten:

- `segment_id`
- `segment_number`
- `speaker_code`
- `start_ms`
- `end_ms`

### 6.2 Empfohlene zusätzliche Felder

Zusätzlich sinnvoll:

- `text`
- `tokens`
- `annotations`

### 6.3 Bedeutung der Felder

| Feld | Bedeutung |
|---|---|
| `segment_id` | stabile technische ID, z. B. `seg_001` |
| `segment_number` | sichtbare Reihenfolge, z. B. `1`, `2`, `3` |
| `speaker_code` | `interviewer` oder `participant` |
| `start_ms` | Segmentbeginn in Millisekunden |
| `end_ms` | Segmentende in Millisekunden |
| `text` | editorisch bereinigter Segmenttext für Anzeige und Export |
| `tokens` | optionale Timing-Tokens für Highlighting / Sync |
| `annotations` | editorische Zusatzannotation, z. B. Materialreferenzen |

### 6.4 Segmentgrenze

Ein Segment ist in der Regel:

- ein final editorisch bereinigter Sprecherturn

Nicht Amberscript als Rohsystem, sondern die **editorisch korrigierte Segmentierung** ist maßgeblich.

---

## 7. Tokenstruktur im Ziel-JSON

Die Tokenebene soll vereinfacht, aber beibehalten werden.

### 7.1 Warum Tokens behalten?

Auch wenn das Interview primär segmentbasiert ist, sind Tokens sinnvoll für:

- späteres Wort-Highlighting
- feinere Navigation
- mögliche Such-/Sync-Funktionen
- Einfügepunkte für editorische Annotationen

### 7.2 Token-Minimum

Pro Token genügt:

- `text`
- `start_ms`
- `end_ms`

### 7.3 Empfohlen zusätzlich

Optional, aber sinnvoll:

- `token_id`

### 7.4 Wegfallende Tokenfelder

Nicht übernehmen:

- `duration`
- `conf`
- `pristine`

### 7.5 Beispiel

Aus Amberscript:

```json
{
  "start": 27.23,
  "end": 27.31,
  "duration": 0.07999992,
  "text": "es",
  "conf": 0.91,
  "pristine": true
}
````

wird im Ziel-JSON z. B.:

```json
{
  "token_id": "seg_002_tok_035",
  "text": "es",
  "start_ms": 27230,
  "end_ms": 27310
}
```

---

## 8. Millisekunden statt Sekunden

Für Kohärenz mit `text.json` und `wordlist.json` sollen Interviewzeiten ebenfalls in **Millisekunden** gespeichert werden.

### Regel

* Amberscript `start`/`end` in Sekunden
* im Ziel-JSON: `start_ms` / `end_ms` als Integer in Millisekunden

Beispiel:

* `27.23` → `27230`
* `27.31` → `27310`

---

## 9. Das Feld `text` auf Segmentebene

Das Segment soll nicht nur Tokens tragen, sondern auch einen editorisch bereinigten Volltext.

### Warum?

Denn der finale anzeigbare Interviewtext ergibt sich nicht immer sauber nur aus den Tokens:

* Interpunktion ist editorisch überarbeitet
* Satzgrenzen sind editorisch plausibilisiert
* Fülllaute werden normalisiert
* postredaktionelle Referenzannotationen kommen hinzu

### Regel

Das Feld `text` ist die **maßgebliche editorische Anzeigeform** des Segments.

Die Tokens sind die Timing-Ebene.

---

## 10. Materialreferenzen aus der Postproduktion

Wenn im Interview auf Wortlisten- oder Textmaterial verwiesen wird, sollen diese Referenzen strukturiert ins Ziel-JSON eingehen.

### 10.1 Editor-Syntax

Im Editor wird eine Referenz kodiert als:

```text
[= {label}::{item_id}]
```

Beispiele:

```text
[= juzgar::wl_019]
[= ahí – allí::wl_089]
[= D5::d_05]
[= QY3::qy_03]
```

### 10.2 Warum nicht nur sichtbar im Text belassen?

Weil die Webapp diese Referenzen später:

* sichtbar markieren
* als Link rendern
* zum Item springen lassen
* optional die zugehörige Split-MP3 derselben Session ansteuern lassen

soll.

### 10.3 Ziel-JSON-Regel

Die Editor-Kodierung wird **nicht als rohe Markup-Syntax** ins Ziel-JSON übernommen, sondern in strukturierte Annotationen umgewandelt.

---

## 11. Struktur der Annotationen

### 11.1 Empfehlung

Materialreferenzen sollen auf Segmentebene in einem Feld `annotations` gespeichert werden.

Jede Referenz wird dabei als Objekt abgelegt.

### 11.2 Mindestfelder pro Materialreferenz

* `kind`
* `label`
* `item_id`
* `task`

### 11.3 Sinnvolle Zusatzfelder

* `item_number`
* `canonical_text`
* `insert_after_token_id`

### 11.4 Bedeutung

| Feld                    | Bedeutung                                                             |
| ----------------------- | --------------------------------------------------------------------- |
| `kind`                  | z. B. `material_ref`                                                  |
| `label`                 | sichtbare Form, z. B. `juzgar`                                        |
| `item_id`               | stabile technische ID, z. B. `wl_019`                                 |
| `task`                  | abgeleitet aus dem Präfix der `item_id`, z. B. `wordlist` oder `text` |
| `item_number`           | sichtbare Nummer aus dem Material                                     |
| `canonical_text`        | kanonischer Text aus `wordlist.json` oder `text.json`                 |
| `insert_after_token_id` | Einfügeanker für das Rendering im Segment                             |

### 11.5 Warum `insert_after_token_id`?

Weil editorische Referenzen **nicht gesprochen** sind und daher keine echten Audiotokens sein sollen.

Sie sollen im UI an einer bestimmten Stelle **eingefügt** werden, ohne die Timing-Tokens selbst zu verfälschen.

---

## 12. Ableitung von `task` aus `item_id`

Im Editor genügt:

```text
[= juzgar::wl_019]
```

Die Pipeline leitet `task` dann automatisch ab:

| Präfix | Task       |
| ------ | ---------- |
| `wl_`  | `wordlist` |
| `d_`   | `text`     |
| `qy_`  | `text`     |
| `qw_`  | `text`     |
| `t_`   | `text`     |

Die `task` muss daher **nicht manuell im Editor mitgeschrieben** werden.

---

## 13. Abgleich mit `wordlist.json` und `text.json`

Jede editorische Materialreferenz muss in der Transformation gegen die kanonischen Materialquellen validiert werden.

### 13.1 Zu prüfen

* existiert die `item_id`?
* lässt sich daraus eindeutig die `task` ableiten?
* passt die `item_number`?
* passt der kanonische Text?
* ist das Präfix gültig?

### 13.2 Ergebnis der Anreicherung

Aus der Editor-Kodierung

```text
[= juzgar::wl_019]
```

wird im Ziel-JSON z. B.:

```json
{
  "kind": "material_ref",
  "label": "juzgar",
  "item_id": "wl_019",
  "task": "wordlist",
  "item_number": "19",
  "canonical_text": "juzgar",
  "insert_after_token_id": "seg_014_tok_013"
}
```

---

## 14. Vorschlag für das minimale Ziel-JSON

```json
{
  "session_id": "ES-L-0001-2026-S01",
  "person_id": "ES-L-0001",
  "task": "interview",
  "audio": {
    "full_mp3": "derived/interview.mp3"
  },
  "segments": [
    {
      "segment_id": "seg_001",
      "segment_number": "1",
      "speaker_code": "interviewer",
      "start_ms": 1710,
      "end_ms": 9230,
      "text": "Ich würde jetzt ganz gern zum Abschluss noch mal ein paar Fragen dazu stellen, wie du denn das Vorlesen der spanischen Texte so erlebt hast. Wie ging es dir damit?",
      "tokens": [
        {
          "token_id": "seg_001_tok_001",
          "text": "Ich",
          "start_ms": 1710,
          "end_ms": 1910
        }
      ]
    },
    {
      "segment_id": "seg_002",
      "segment_number": "2",
      "speaker_code": "participant",
      "start_ms": 9830,
      "end_ms": 28870,
      "text": "Ja, also ähm, ich fand jetzt äh nichts irgendwie. Also ich glaube, ich bin nicht so viel ins Stocken geraten bei manchen.",
      "tokens": [
        {
          "token_id": "seg_002_tok_001",
          "text": "Ja,",
          "start_ms": 9830,
          "end_ms": 10230
        }
      ]
    }
  ]
}
```

---

## 15. Empfehlung zur ID-Bildung

### 15.1 Segmente

* `seg_001`
* `seg_002`
* `seg_003`

### 15.2 Tokens

* `seg_001_tok_001`
* `seg_001_tok_002`
* `seg_001_tok_003`

So bleibt die Struktur lesbar und stabil.

---

## 16. Was minimal nötig ist und was optional bleibt

### 16.1 Minimal nötig

**Top-Level**

* `session_id`
* `person_id`
* `task`
* `audio.full_mp3`
* `segments`

**Segment**

* `segment_id`
* `segment_number`
* `speaker_code`
* `start_ms`
* `end_ms`

### 16.2 Für die Praxis klar empfohlen

**Segment zusätzlich**

* `text`
* `tokens`

**Token**

* `text`
* `start_ms`
* `end_ms`
* optional `token_id`

**Optional bei Bedarf**

* `annotations`

### 16.3 Nicht minimal nötig, aber später möglich

* Segment-Split-MP3s
* separate Sprecher-Metadatenliste
* TEI-Export
* zusätzliche Alignment-/Qualitätsflags

---

## 17. Was bei der Implementierung zu beachten ist

| Punkt              | Zu beachten                                                                            |
| ------------------ | -------------------------------------------------------------------------------------- |
| Kohärenz           | Interview soll oben wie die anderen Tasks aussehen, aber intern segmentbasiert bleiben |
| Timing             | Millisekunden als Integer                                                              |
| Sprecherrollen     | Amberscript `spk1`/`spk2` in feste PROMAT-Rollen übersetzen                            |
| Segmenttext        | editorisch bereinigter Anzeige-Text muss separat gespeichert werden                    |
| Tokens             | vereinfachen, aber behalten                                                            |
| Annotationen       | nicht als rohe Editor-Markup-Syntax weiterreichen                                      |
| Referenzen         | gegen `wordlist.json` und `text.json` validieren                                       |
| Redundanz          | Amberscript-Metadaten nur übernehmen, wenn sie im Zielsystem wirklich gebraucht werden |
| Zukunftssicherheit | spätere Link-, Jump- und Clip-Funktionen schon in der Datenstruktur mitdenken          |

---

## 18. Klare Schlussentscheidung

Für PROMAT ist die sinnvollste Zielstruktur:

* **top-level analog zu `wordlist` und `text`**
* **interview intern klar segmentbasiert**
* **Tokens vereinfacht übernehmen**
* **Amberscript-Ballast verwerfen**
* **Materialreferenzen strukturiert anreichern**
* **editorisch bereinigten Segmenttext ausdrücklich mitführen**

Das ist der sauberste Kompromiss aus:

* technischer Kohärenz
* ausreichender Einfachheit
* späterer Webapp-Nutzbarkeit
* Anschlussfähigkeit an Player, Highlighting und Verlinkung

```
```
