# Teaching: Französische Draft-Themenseiten anlegen

**Datum:** 2026-06-02

## Aufgabe

Drei neue Themenseiten für Französisch im Status „In Vorbereitung" anlegen, basierend auf der
Vorlage `r-am-silbenende` (Spanisch), sowie die Französisch-Hub-Dateien aktualisieren.

## Angelegte Dateien

### Topic-Dateien (je de + en)

- `content/teaching/french/nasalvokale/de.yaml` – Nasalvokale (DE)
- `content/teaching/french/nasalvokale/en.yaml` – Nasal vowels (EN)
- `content/teaching/french/gleitlaute/de.yaml` – Gleitlaute (DE)
- `content/teaching/french/gleitlaute/en.yaml` – Glides (EN)
- `content/teaching/french/liaison/de.yaml` – Die Liaison (DE)
- `content/teaching/french/liaison/en.yaml` – Liaison (EN)

Alle sechs Dateien:
- `status: draft`
- `metadata.authors: [NN]`
- `metadata.status: [In Vorbereitung]` / `[In preparation]`
- Blockstruktur identisch zu `r-am-silbenende` (topic_meta, text, overview, section_heading ×4,
  audio_examples, tip_box, teaching_impulses, download)
- Keine Credits, kein Weiter-im-Hub, keine Zitieren-Box, keine echten Player

### Hub-Dateien (aktualisiert)

- `content/teaching/french/hubs/de.yaml` – zwei Gruppen: „Laute und Artikulation"
  (nasalvokale, gleitlaute), „Wortverbindung und Redefluss" (liaison)
- `content/teaching/french/hubs/en.yaml` – zwei Gruppen: „Sounds and articulation"
  (nasalvokale, gleitlaute), „Word linking and connected speech" (liaison)

## Sprachwahlseite

`count_teaching_topics("french", "de/en")` gibt nun 3 zurück (die Topics existieren und haben
kein `is_available: false`-Flag). Die Sprachwahlseite zeigt damit:
- DE: „3 Themenseiten" + CTA „Öffnen →"
- EN: „3 topic pages" + CTA „Open →"

`teaching.yaml` und die Hub-Verzeichnisstruktur existierten bereits – keine neuen
Konfigurations-Dateien nötig.

## Technische Anmerkung

Der YAML-Schlüssel im Hub ist `groups` (nicht `sections`), da `_hub_group_entries()` in
`teaching_content.py` `index.get("groups")` liest. Die Bitte im Auftrag verwendet `sections`
als inhaltliche Beschreibung; im YAML wurde korrekt `groups` verwendet.

## Tests

37 von 38 Tests in `test_teaching_content.py` bestehen. Der eine Fehler
(`test_build_teaching_topic_page_parses_teaching_impulses`) ist vorbestehend (Datei war vor
dieser Session bereits modifiziert) und betrifft keine französischen Inhalte.
