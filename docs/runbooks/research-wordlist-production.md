# Runbook: Produce Research Wordlist Player Artifacts

## Zweck

Wiederholbarer Implementierungs- und Betriebsablauf für die Erzeugung der `wordlist`-Player-Artefakte aus expliziten operativen Eingaben.

Dieses Runbook beschreibt den Task-Vertrag der Ableitung. Der reguläre Einstieg für Batch-Importe bleibt `scripts/research_data_intake/import_batch_to_production.py`; `produce_wordlist_artifacts.py` ist der fokussierte Ableitungshelfer für den `wordlist`-Task.

## Operative Eingaben

- `data/config/research_player/spanish/task_catalogs/wordlist.json`
- eine explizite `wordlist`-Source-WAV als operative Ableitungsbasis
- eine explizite `wordlist`-TextGrid-Datei als Alignment-Quelle

Im Batch-Kontext stammen diese operativen Eingaben typischerweise aus:

- `working/{person_id}/wordlist/source/wordlist.wav`
- `working/{person_id}/wordlist/alignment/wordlist.TextGrid`

Im Runtime-Kontext werden nur die Zielartefakte gespeichert, nicht diese Ableitungsquellen.

## CLI-Einstieg

- Einzelne Session validieren, ohne Schreibzugriff:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/produce_wordlist_artifacts.py --session-id ES-L-0001-2026-S01 --dry-run`
- Einzelne Session produzieren:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/produce_wordlist_artifacts.py --session-id ES-L-0001-2026-S01`
- Alle aktuell geeigneten spanischen Sessions produzieren:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/produce_wordlist_artifacts.py --all-suitable-sessions`
- Optionale Label-Prüfung mit Warnungen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/produce_wordlist_artifacts.py --all-suitable-sessions --validate-labels warn`

## Katalog-Provenienz

- Der kanonische Task-Katalog `data/config/research_player/spanish/task_catalogs/wordlist.json` ist die operative Inhaltsquelle für den Produktions-Run.
- Der Katalog dokumentiert, dass `docs/model_mds/01_Spanisch_Wortliste.pdf` die Referenz für kanonische Reihenfolge und sichtbare Nummerierung `1` bis `92` ist.
- Der Katalog dokumentiert, dass `docs/model_mds/spanish_wordlist.txt` die Referenz für die exakten Item-Texte ist.

## Autoritätsregel

- Wenn ein kanonischer Task-Katalog vorliegt, ist dieser Katalog die verbindliche Inhaltsquelle für Reihenfolge, `item_id`, `item_number` und `text`.
- Die TextGrid-Datei liefert die Zeitgrenzen und die Reihenfolge der nicht-silence-Intervalle, aber nicht die maßgeblichen `text`-Werte für JSON und Split-Referenzierung.
- Die Katalogwerte werden unverändert übernommen: keine Orthographienormalisierung, keine Unicode-Vereinfachung, keine Akzentbereinigung, keine automatische Groß-/Kleinschreibungsänderung und keine stillschweigende Änderung von Leerzeichen oder Gedankenstrichen.
- Der Run darf TextGrid-Labels gegen die kanonischen Katalogtexte validieren, aber erkannte Abweichungen dürfen nicht stillschweigend normalisiert werden.

## Zielartefakte

- `derived/wordlist.mp3`
- `items/wordlist/{item_id}.mp3`
- `alignment/wordlist.json`

Diese Zielartefakte sind runtime-tauglich. Die operative Source-WAV und das TextGrid gehören nicht in `data/sessions/`.

## ID- und Nummerierungsvertrag

- `item_number` ist die fachlich sichtbare Nummer der kanonischen spanischen Wortliste und kommt aus dem Task-Katalog.
- Für den aktuellen Produktionspfad muss `item_number` im Katalog genau `1` bis `92` abbilden.
- `item_id` ist die stabile technische ID und kommt aus dem Task-Katalog.
- Für den aktuellen spanischen Produktionspfad wird `item_id` im Katalog deterministisch aus `item_number` abgeleitet: Prefix `wl_`, dreistellige Nullauffüllung, also `wl_001` bis `wl_092`.
- `split_mp3` verweist intern immer auf `items/wordlist/{item_id}.mp3`.

## Fehlerbedingungen

- Wenn der Task-Katalog nicht geladen werden kann oder nicht exakt `92` Items enthält, schlägt der Produktions-Run fehl.
- Wenn die Zahl der nicht-silence-Intervalle in der `wordlist`-TextGrid-Datei nicht exakt `92` beträgt, schlägt der Produktions-Run fehl.
- Wenn die Intervallreihenfolge nicht positionsgleich auf die `92` Katalog-Items gemappt werden kann, schlägt der Produktions-Run fehl.
- Wenn für ein Intervall keine kanonische Katalogzuordnung hergestellt werden kann, schlägt der Produktions-Run fehl.
- Wenn die kanonischen `wordlist`-Grenzen über die verfügbare Dauer der Source-WAV hinausreichen, ist die Session für diesen Produktionspfad nicht verarbeitbar.
- Wenn eine optionale Label-Validierung Abweichungen erkennt, darf der Run nur kontrolliert fehlschlagen oder explizit warnen; stillschweigende Textumschreibung ist unzulässig.

## Ablauf

1. Den kanonischen Task-Katalog `data/config/research_player/spanish/task_catalogs/wordlist.json` laden.
2. Prüfen, dass der Katalog genau `92` Items enthält.
3. Die operative `wordlist`-TextGrid-Datei lesen.
4. Führende, zwischenliegende und abschließende Silence-Intervalle verwerfen.
5. Prüfen, dass genau `92` nicht-silence-Intervalle vorliegen.
6. Die Intervallreihenfolge positionsgleich auf die `92` Katalog-Items mappen.
7. Optional die TextGrid-Labels gegen die kanonischen `text`-Werte des Katalogs validieren.
8. Die gelesenen Zeitwerte vor weiterer Ableitung auf vier Nachkommastellen runden.
9. Die gerundeten kanonischen Zeitgrenzen einmalig als ganzzahlige `start_ms`- und `end_ms`-Werte serialisieren.
10. `derived/wordlist.mp3` aus der operativen `wordlist`-Source-WAV mit Lautheitsstandardisierung sowie MP3 in mono mit `160 kbps` CBR erzeugen.
11. `items/wordlist/{item_id}.mp3` aus dem bereits standardisierten Full-MP3 mit denselben Web-Parametern erzeugen.
12. Für jeden Split `250 ms` Vorlauf und `250 ms` Nachlauf anwenden.
13. Die gepaddeten Split-Grenzen an die verfügbare Audiolänge klammern.
14. `alignment/wordlist.json` aus dem kanonischen Task-Katalog plus den kanonischen Zeitgrenzen und den Split-Korrespondenzen erzeugen.

## Kanonische Grenzen vs. Exportgrenzen

- Die Katalogdaten `item_id`, `item_number` und `text` bleiben von session-spezifischen Zeit- und Splitdaten getrennt.
- `start_ms` und `end_ms` in `alignment/wordlist.json` sind die kanonischen Annotationsgrenzen und werden als ganzzahlige Millisekundenwerte gespeichert.
- Die aus dem TextGrid gelesenen und auf vier Nachkommastellen gerundeten Werte sind die Grundlage dieser kanonischen JSON-Grenzen.
- Die für Split-MP3s verwendeten gepaddeten Exportgrenzen sind davon getrennt.
- Split-Padding verändert die kanonischen JSON-Grenzen nicht.

## Audio-Parameter

- Web-Derivate für den aktuellen `wordlist`-Pfad werden als MP3 in mono mit `160 kbps` CBR erzeugt.
- Diese Parameter gelten einheitlich für `derived/wordlist.mp3` und `items/wordlist/{item_id}.mp3`.
- Die operative Source-WAV bleibt die maßgebliche Analyse- und Ableitungsgrundlage; MP3-Derivate sind Web-, Player-, Vergleichs- und Download-Artefakte.

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
- Die Implementierung verwendet `ffmpeg` und `ffprobe` für Erzeugung und Verifikation.