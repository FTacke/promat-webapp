# Lernenden-Aufnahme *vida* auf der Seite b/d/g ersetzt

Datum: 2026-11-08

## Ziel

Auf der Themenseite `soft-consonants-b-d-g` die Lernenden-Aufnahme von *vida* durch ES-L-0020-2026-S01 (`wordlist` `wl_045`) ersetzen, sofern die Session für Teaching freigegeben ist.

## Consulted Sources

- `scripts/teaching_audio_slots.py` (Release-Gate), `content/teaching/spanish/audio-slots.yaml`
- `docs/spec/intake-workbook.md` (`teaching_consent_signed` als Eignungsmerkmal)

## Geänderte Bereiche

- `content/teaching/spanish/audio-slots.yaml`: Lernenden-Slot von `p5-vida` auf ES-L-0020, neuer SHA-256; die nun integrierte Reserve `p5-vida-reserve-0020` entfernt
- `content/teaching/spanish/soft-consonants-b-d-g/media/audio/corpus/p5-vida-learner.mp3` per `--export` neu geschrieben
- `app/tests/test_teaching_spanish_topics.py`: erwartete Auswahl angepasst

## Wichtige Entscheidungen

- ES-L-0020 hat `teaching_consent_signed: yes`; `--release-report` meldet OK. Dateiname und Seitentexte bleiben unverändert.

## Abweichungen

- Keine.

## Verifikation

- `--release-report`, `--export`, `--check` ("slots OK"); Tests in `test_teaching_spanish_topics.py`

## Offene Punkte

- Die frühere Aufnahme (ES-L-0007) ist nicht mehr als Reserve eingetragen.

## Nächste sinnvolle Schritte

- Neue Aufnahme einmal anhören.
