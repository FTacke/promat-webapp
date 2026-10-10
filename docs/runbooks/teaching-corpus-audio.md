# Runbook: Korpusaufnahmen auf Teaching-Themenseiten austauschen

## Zugehörige Spezifikation

- `docs/spec/platform-data-files.md` (Teaching-Medien, Abschnitt „Teaching corpus recordings“)
- `docs/spec/intake-workbook.md` (`teaching_consent_signed` ist ein Eignungsflag für die manuelle Auswahl, kein Veröffentlichungsschalter)

## Zweck

Die kuratierten Hörvergleiche der spanischen Phänomen-Themenseiten (`content/teaching/spanish/*/`) sind zentral in `content/teaching/spanish/audio-slots.yaml` deklariert. Dieses Runbook beschreibt, wie einzelne Sprecher-Item-Kombinationen ersetzt werden, ohne Seitentexte oder Layout anzufassen.

## Voraussetzungen

- lokale Runtime mit `data/sessions/spanish/{session_id}/items/{wordlist|text}/{item_id}.mp3` (Items `wl_NNN`, `d_NN`, `qy_NN`, `qw_NN`)
- die Quellsession trägt `teaching_consent_signed: yes` und `needs_review: false` (Eignungsprüfung; die Auswahl selbst bleibt eine manuelle redaktionelle Entscheidung)

## Schritte

1. In `audio-slots.yaml` den Eintrag der Aufnahme suchen (`comparisons[].recordings[]`, Felder `session_id` und `item`) und Session oder Item ändern. `category` bleibt `reference` (Session `ES-N-…`) oder `learner` (Session `ES-L-…`); `file` bleibt unverändert, damit die Seiten nicht angepasst werden müssen.
2. `python scripts/teaching_audio_slots.py --export` ausführen: prüft Einwilligung und Sprechertyp, kopiert die MP3 nach `content/teaching/spanish/{topic}/media/audio/corpus/` und schreibt den neuen `sha256`.
3. Die Aufnahme anhören. Wurde ein Beispiel gezielt wegen einer beobachteten Realisierung gewählt, die Erklärung der Seite (`solution`-Block) entsprechend prüfen: Die Seiten behaupten bewusst keine konkrete Abweichung einzelner Aufnahmen.
4. `python scripts/teaching_audio_slots.py --check`, `python scripts/validate_teaching_content.py` und `pytest app/tests/test_teaching_spanish_topics.py` ausführen.
5. Geänderte MP3 und `audio-slots.yaml` committen.

Neue Vergleiche oder Hörfragen: den Eintrag unter `comparisons` ergänzen (die `question` muss wörtlich im `lead` des Vergleichsblocks der Seite stehen) und den Block in `de.yaml`/`en.yaml` mit den Dateinamen `corpus/…` anlegen.

## Verifikation

- `--check` meldet `slots OK` (Dateien vorhanden, `sha256` stimmt, jede Datei wird von der Seite referenziert, Fragen stehen auf der Seite; mit lokaler Runtime zusätzlich Einwilligung, Sprechertyp und Gleichheit mit der Quelle)
- Seite lokal öffnen: Player startet nicht automatisch, Beschriftung nennt Sprecherkategorie und Item

## Risiken und Rückbau

- Ersetzte oder entfernte Aufnahmen bleiben in der Git-Historie des (öffentlichen) Repositorys. Eine Aufnahme, deren Einwilligung widerrufen wird, muss aus `audio-slots.yaml` und `media/audio/corpus/` entfernt werden; die Historie lässt sich nur durch eine gesonderte Maßnahme bereinigen.
- Die Auswahl der ersten Veröffentlichung erfolgte automatisch (typische Dauer je Item) und wurde phonetisch nicht geprüft.
