# Runbook: Produce Research Wordlist Player Artifacts

## Zweck

Vorbereitung und Referenzablauf für den kommenden Implementierungs-Run, der die `wordlist`-Produktionsartefakte für den Research-Player erzeugt.

## Verbindliche Quellen

- `data/config/research_player/spanish/task_catalogs/wordlist.json`
- `source/wordlist.wav`
- `alignment/wordlist.TextGrid`

## Katalog-Provenienz

- Der kanonische Task-Katalog `data/config/research_player/spanish/task_catalogs/wordlist.json` ist die operative Inhaltsquelle für den Produktions-Run.
- Der Katalog dokumentiert, dass `docs/model_mds/01_Spanisch_Wortliste.pdf` die Referenz für kanonische Reihenfolge und sichtbare Nummerierung `1` bis `92` ist.
- Der Katalog dokumentiert, dass `docs/model_mds/spanish_wordlist.txt` die Referenz für die exakten Item-Texte ist.

## Autoritätsregel

- Wenn ein kanonischer Task-Katalog vorliegt, ist dieser Katalog die verbindliche Inhaltsquelle für Reihenfolge, `item_id`, `item_number` und `text`.
- `alignment/wordlist.TextGrid` liefert die Zeitgrenzen und die Reihenfolge der nicht-silence-Intervalle, aber nicht die maßgeblichen `text`-Werte für JSON und Split-Referenzierung.
- Die Katalogwerte werden unverändert übernommen: keine Orthographienormalisierung, keine Unicode-Vereinfachung, keine Akzentbereinigung, keine automatische Groß-/Kleinschreibungsänderung und keine stillschweigende Änderung von Leerzeichen oder Gedankenstrichen.
- Der kommende Implementierungs-Run darf TextGrid-Labels gegen die kanonischen Katalogtexte validieren, aber erkannte Abweichungen dürfen nicht stillschweigend normalisiert werden.

## Eingaben

- `data/config/research_player/spanish/task_catalogs/wordlist.json` als kanonische Inhaltsquelle
- `source/wordlist.wav` als Audioquelle für das Full-MP3
- `alignment/wordlist.TextGrid` als Quelle der Intervallgrenzen
- `docs/model_mds/spanish_wordlist.txt` und `docs/model_mds/01_Spanisch_Wortliste.pdf` nur als Provenienz- und Audit-Referenzen des Katalogs, nicht als operative Produktionsquelle solange der Katalog vorhanden ist

## Zielartefakte

- `derived/wordlist.mp3`
- `items/wordlist/{item_id}.mp3`
- `alignment/wordlist.json`

## ID- und Nummerierungsvertrag

- `item_number` ist die fachlich sichtbare Nummer der kanonischen spanischen Wortliste und kommt aus dem Task-Katalog.
- Für den aktuellen Produktionspfad muss `item_number` im Katalog genau `1` bis `92` abbilden.
- `item_id` ist die stabile technische ID und kommt aus dem Task-Katalog.
- Für den aktuellen spanischen Produktionspfad wird `item_id` im Katalog deterministisch aus `item_number` abgeleitet: Prefix `wl_`, dreistellige Nullauffüllung, also `wl_001` bis `wl_092`.
- `split_mp3` verweist intern immer auf `items/wordlist/{item_id}.mp3`.

## Fehlerbedingungen

- Wenn der Task-Katalog nicht geladen werden kann oder nicht exakt `92` Items enthält, schlägt der Produktions-Run fehl.
- Wenn die Zahl der nicht-silence-Intervalle in `alignment/wordlist.TextGrid` nicht exakt `92` beträgt, schlägt der Produktions-Run fehl.
- Wenn die Intervallreihenfolge nicht positionsgleich auf den kanonischen Task-Katalog gemappt werden kann, schlägt der Produktions-Run fehl.
- Wenn für ein Intervall keine kanonische Katalogzuordnung hergestellt werden kann, schlägt der Produktions-Run fehl.
- Wenn eine optionale Label-Validierung gegen TextGrid-Labels Abweichungen erkennt, darf der Run nur kontrolliert fehlschlagen oder explizit warnen; stillschweigende Textumschreibung ist unzulässig.

## Ablauf

1. Den kanonischen Task-Katalog `data/config/research_player/spanish/task_catalogs/wordlist.json` laden.
2. Prüfen, dass der Katalog genau `92` Items enthält.
3. `alignment/wordlist.TextGrid` lesen.
4. Führende, zwischenliegende und abschließende Silence-Intervalle verwerfen.
5. Prüfen, dass genau `92` nicht-silence-Intervalle vorliegen.
6. Die Intervallreihenfolge positionsgleich auf die `92` Katalog-Items mappen.
7. Optional die TextGrid-Labels gegen die kanonischen `text`-Werte des Katalogs validieren.
8. Die gelesenen Zeitwerte vor weiterer Ableitung auf vier Nachkommastellen runden.
9. `derived/wordlist.mp3` aus `source/wordlist.wav` mit konstanter Bitrate und Lautheitsstandardisierung erzeugen.
10. `items/wordlist/{item_id}.mp3` aus dem bereits standardisierten Full-MP3 erzeugen.
11. Für jeden Split `250 ms` Vorlauf und `250 ms` Nachlauf anwenden.
12. Die gepaddeten Split-Grenzen an die verfügbare Audiolänge klammern.
13. `alignment/wordlist.json` aus dem kanonischen Task-Katalog plus den kanonischen Zeitgrenzen und den Split-Korrespondenzen erzeugen.

## Kanonische Grenzen vs. Exportgrenzen

- Die Katalogdaten `item_id`, `item_number` und `text` bleiben von session-spezifischen Zeit- und Splitdaten getrennt.
- `start_ms` und `end_ms` in `alignment/wordlist.json` sind die kanonischen Annotationsgrenzen.
- Die aus dem TextGrid gelesenen und auf vier Nachkommastellen gerundeten Werte sind die Grundlage dieser kanonischen JSON-Grenzen.
- Die für Split-MP3s verwendeten gepaddeten Exportgrenzen sind davon getrennt.
- Split-Padding verändert die kanonischen JSON-Grenzen nicht.

## Interner Pfad vs. Download-Dateiname

- Interne Speicherung bleibt `items/wordlist/{item_id}.mp3`.
- Der spätere Download-Dateiname wird erst bei der Auslieferung erzeugt und ändert den internen Speicherpfad nicht.
- Der vorbereitete Download-Vertrag für die aktuelle Wortliste ist `{person_id}_wordlist_{item_id}_{text}.mp3`.
- Die lesbare Textkomponente stammt aus dem kanonischen `text` des Items.
- Eine eventuelle spätere Dateinamen-Escaping-Logik darf nur die Delivery-Benennung betreffen und nicht auf `item_id`, JSON-`text` oder interne Speicherpfade zurückwirken.

## Erwarteter JSON-Kern pro Item

- `item_id`
- `item_number`
- `text`
- `start_ms`
- `end_ms`
- `split_mp3`

## Hinweise

- `wordlist` bleibt item-zentriert; künstliche `tokens` mit identischen Werten werden nicht erzeugt, wenn das Item selbst bereits die timingtragende Einheit ist.
- Der kanonische Task-Katalog kann später auch rohe Materialansichten in der Webapp tragen, ohne dadurch automatisch Audio oder geschützte Korpusdaten freizugeben.
- Split-MP3s werden aus dem bereits lautheitsstandardisierten Full-MP3 erzeugt und nicht pro Item nochmals separat normalisiert.
- Dieser Ablauf beschreibt den wiederholbaren Produktionsschritt, nicht dessen konkrete Implementierung im nächsten Run.