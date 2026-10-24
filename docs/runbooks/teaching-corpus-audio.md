# Runbook: Korpusaufnahmen auf Teaching-Themenseiten austauschen

## Zugehörige Spezifikation

- `docs/spec/platform-data-files.md` (Teaching-Medien, Abschnitt „Teaching corpus recordings“)
- `docs/spec/intake-workbook.md` (`teaching_consent_signed` ist ein Eignungsflag für die manuelle Auswahl, kein Veröffentlichungsschalter)

## Zweck

Die kuratierten Hörvergleiche der spanischen Phänomen-Themenseiten (`content/teaching/spanish/*/`) sind zentral in `content/teaching/spanish/audio-slots.yaml` deklariert. Dieses Runbook beschreibt, wie einzelne Sprecher-Item-Kombinationen ersetzt werden, ohne Seitentexte oder Layout anzufassen.

## Voraussetzungen

- lokale Runtime mit `data/sessions/spanish/{session_id}/items/{wordlist|text}/{item_id}.mp3` (Items `wl_NNN`, `d_NN`, `qy_NN`, `qw_NN`)
- die Quellsession trägt `teaching_consent_signed: yes` und `needs_review: false` (Eignungsprüfung; die Auswahl selbst bleibt eine manuelle redaktionelle Entscheidung)

## Freigabe-Gate (verbindlich, vor jedem Export oder Austausch)

`python scripts/teaching_audio_slots.py --release-report` listet jede verwendete (und jede als Reserve geführte) Session-Item-Kombination mit `teaching_consent_signed`, `needs_review`, Sprechertyp, Itemtext und Ergebnis (`OK`/`BLOCKED`). Geprüft wird die Session-`metadata.json` der lokalen Runtime, nicht ein früherer Bericht; Research-Zugang oder vorhandene Audiodateien ersetzen die Teaching-Einwilligung nicht. Sessions in `EXCLUDED_SESSIONS` (z. B. ES-L-0014) sind gesperrt; bei fehlender oder ungeklärter Freigabe wird die Aufnahme nicht eingebunden (kein stiller Sprecherwechsel), der Blocker wird im Run-Bericht dokumentiert. Die Tabelle gehört in den Run-Bericht.

## Schritte

1. In `audio-slots.yaml` den Eintrag der Aufnahme suchen (`comparisons[].recordings[]`, Felder `session_id` und `item`) und Session oder Item ändern. `category` bleibt `reference` (Session `ES-N-…`) oder `learner` (Session `ES-L-…`); `file` bleibt unverändert, damit die Seiten nicht angepasst werden müssen.
2. `python scripts/teaching_audio_slots.py --export` ausführen: prüft Einwilligung und Sprechertyp, kopiert die MP3 nach `content/teaching/spanish/{topic}/media/audio/corpus/` und schreibt den neuen `sha256`.
3. Die Aufnahme anhören. Wurde ein Beispiel gezielt wegen einer beobachteten Realisierung gewählt, die Erklärung der Seite (`solution`-Block) entsprechend prüfen: Die Seiten behaupten bewusst keine konkrete Abweichung einzelner Aufnahmen.
4. `python scripts/teaching_audio_slots.py --check`, `python scripts/validate_teaching_content.py` und `pytest app/tests/test_teaching_spanish_topics.py` ausführen.
5. Geänderte MP3 und `audio-slots.yaml` committen.

MAR.ELE-Aufnahmen (Vorgängerkorpus, nicht in der Runtime): Der Eintrag trägt statt `session_id`/`item` einen `origin` (`corpus`, `source_file`, `transcription`) und die Datei liegt unter `media/audio/marele/`. Sie wird einmal von Hand aus dem Quellrepository kopiert (Quelle bleibt unverändert), `sha256` im Eintrag nachtragen; `--export` überspringt diese Einträge, `--check` prüft Datei, Hash und Seitenverweis. Die Seite nennt die Herkunft als Text `MAR.ELE`, ohne Link.

Ausschnitt statt ganzer Satz: Soll nur die Zielwortfolge hörbar sein, den Eintrag um `crop` ergänzen (`start_ms`, `end_ms` auf der Item-MP3, `fade_in_ms`, `fade_out_ms`, optional `lead_silence_ms`) und im Vergleich `target_tokens` setzen. Die Schnittpunkte nach Spektrogramm und Energieverlauf der tatsächlichen Realisierung bestimmen (Alignment-Wortzeiten sind nur ein Anhaltspunkt und können mehrere 10 ms danebenliegen): Anlaut vollständig, Auslaut und Übergänge nicht abgeschnitten, nichts zwischen den Wörtern einfügen, Vorlaufstille nur am Clip-Anfang. `--export` rendert das Derivat mit ffmpeg (bitgleich reproduzierbar mit derselben Version), schreibt `source_sha256` und `sha256`; der Chip (`transcript`) der Seite nennt genau die gespielte Passage. Das Ergebnis ansehen (Spektrogramm) und anhören.

Zwei Referenzstimmen in einem Vergleich (z. B. `pero – perro` auf `r`): beide Einträge mit `category: reference`, `slot: ref_a`/`ref_b`; die Seite beschriftet beide `Referenzsprecher:in` und unterscheidet sie über die Untertitel. Dieselbe Aufnahme auf mehreren Seiten (z. B. *reír* W76): je Seite ein eigener Vergleich mit derselben Session und demselben Item; `--export` erzeugt bitgleiche Kopien, deren `sha256` übereinstimmen muss.

Montage aus mehreren Einzelwörtern (z. B. *mismo – álbum* auf `europe-sounds-different`): statt `item`/`crop` trägt der Eintrag `parts` (je `item`, `target_tokens`, `crop` mit `start_ms`/`end_ms`/Fades) und `join: {pause_ms}`. Die Schnittpunkte je Wort nach Energieverlauf und Spektrogramm festlegen (Anlaut vollständig, Auslaut inklusive auslautendem Nasal, ca. 50 ms Vorlauf und 70 ms Nachlauf). `--export` rendert alle Teile mit derselben ffmpeg-Kette und fügt nur die deklarierte Stille ein; die wirksame Pause ist `pause_ms` plus Nach- und Vorlauf der Schnitte. Die Seite kennzeichnet die Karte als „Zwei Einzelwörter, hintereinander montiert“, nie als zusammenhängende Äußerung.

Montage aus MAR.ELE-Einzelwörtern: statt `item` tragen die `parts` ein `source_file` (`items/inf-NNN_<Position>_<Wort>.mp3` im MAR.ELE-Webapp-Backup), der Eintrag ein `origin: {corpus: MAR.ELE}` und kein `session_id`. `--export --marele-root <Backup>` (oder `PROMAT_MARELE_ROOT`) rendert aus dem Backup und aktualisiert die Quell-Hashes; `--check --marele-root` prüft zusätzlich, dass die Quellen unverändert sind. Das Backup enthält Zugangsdaten und Schlüssel und wird nie ins Repository kopiert; nur die abgeleiteten Schnitte liegen unter `media/audio/marele/`. Die Einwilligung der MAR.ELE-Personen für die Verwendung auf der Seite ist vor der Veröffentlichung gesondert zu bestätigen.

Kuratorische Reserven (nicht eingebunden) stehen unter `reserves` in `audio-slots.yaml`, ohne Medium; auch sie müssen das Freigabe-Gate bestehen.

Neue Vergleiche oder Hörfragen: den Eintrag unter `comparisons` ergänzen (die `question` muss wörtlich im `lead` des Vergleichsblocks der Seite stehen) und den Block in `de.yaml`/`en.yaml` mit den Dateinamen `corpus/…` anlegen.

## Verifikation

- `--check` meldet `slots OK` (Dateien vorhanden, `sha256` stimmt, jede Datei wird von der Seite referenziert, Fragen stehen auf der Seite; mit lokaler Runtime zusätzlich Einwilligung, Sprechertyp und Gleichheit mit der Quelle)
- Seite lokal öffnen: Player startet nicht automatisch, Beschriftung nennt Sprecherkategorie und Item

## Risiken und Rückbau

- Ersetzte oder entfernte Aufnahmen bleiben in der Git-Historie des (öffentlichen) Repositorys. Eine Aufnahme, deren Einwilligung widerrufen wird, muss aus `audio-slots.yaml` und `media/audio/corpus/` entfernt werden; die Historie lässt sich nur durch eine gesonderte Maßnahme bereinigen.
- Die Auswahl der ersten Veröffentlichung erfolgte automatisch (typische Dauer je Item) und wurde phonetisch nicht geprüft.
