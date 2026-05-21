# EN-Angleichung an finale DE-Fassung (which-pronunciation)

Datum: 2026-05-13

## Ziel

Die englische Topic-Seite `which-pronunciation` strukturell und inhaltlich an die zuletzt überarbeitete deutsche Fassung angleichen, ohne deutsche Texte zu übernehmen.

## Consulted Sources

- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `content/teaching/spanish/en/topics/which-pronunciation.yaml`

## Wichtige Entscheidungen

- Die EN-Struktur wurde an die DE-Blockfolge angeglichen (Listening comparison vor Seseo/Distinción-Kartensektion, anschließend Hörbeispiele, Classroom prompts mit separatem Intro-Textblock plus didactic_close-List).
- Formulierungen wurden idiomatisch englisch gehalten statt direkt aus DE zu kopieren.

## Abweichungen

- Keine Abweichung von aktiven Regeln.

## Verifikation

- `pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation"` -> 2 bestanden

## Offene Punkte

- Der laufende Dev-Server zeigte während der Browser-Inspektion noch alte EN-Heading-Reihenfolge (staler Runtime-Stand); Dateistand und fokussierte Tests entsprechen der aktualisierten Fassung.

## Nächste sinnvolle Schritte

- Bei Bedarf Dev-Server neu starten und die EN-Route im Browser einmal frisch laden, um die aktualisierte Reihenfolge visuell zu bestätigen.
