# Teaching Public Two-Column Topic Alignment

Datum: 2026-05-12

## Ziel

Den öffentlichen Teaching-Bereich konzeptionell verbindlich auf eine ruhige Root-Auswahl, zentrierte Hub-Gruppen und vertikal erzählte zweispaltige Topic-Seiten bringen, inklusive kanonischem Blocktypenkatalog für `topic_meta`, `audio_examples`, `audio_contrast`, `further_reading` und `citation`, ohne Routing oder Auth-/Research-Architektur zu ändern.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `app/src/app/teaching_content.py`
- `app/templates/pages/teaching_page.html`
- `app/templates/partials/_teaching_blocks.html`
- `app/templates/partials/_corpus_card.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_teaching_content.py`
- `app/tests/test_research_sessions.py`
- `app/src/app/routes/public_content.py`
- `app/src/app/content_navigation.py`
- `content/teaching/spanish/de/index.yaml`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `content/teaching/spanish/en/index.yaml`
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
- `public/teaching/spanish/images/variation/seseo-america.svg`
- `public/teaching/spanish/images/variation/seseo-distincion-spain.svg`
- `tmp/ui-qa/2026-05-12-teaching-two-column-topic/capture_teaching_public.py`

## Geänderte Bereiche

- Teaching-Topic-Normalisierung und Page-Payload in `app/src/app/teaching_content.py`
- neue Teaching-i18n-Labels in `app/src/app/i18n.py`
- Teaching-Root-, Hub- und Topic-Templates in `app/templates/pages/teaching_page.html`, `app/templates/partials/_teaching_blocks.html`, `app/templates/partials/_corpus_card.html`
- Sample-Mirror für Teaching-Hub-Gruppen in `app/templates/pages/sample_page.html`
- Teaching-Layout- und Komponentenregeln in `app/static/css/20_layout.css` und `app/static/css/30_components.css`
- Builder- und Route-Regressionen in `app/tests/test_teaching_content.py` und `app/tests/test_research_sessions.py`
- reales Content-Refresh für `content/teaching/spanish/de/topics/final-r.yaml`, `content/teaching/spanish/de/topics/which-pronunciation.yaml` und die englischen Gegenstücke im Spanisch-Hub
- neue öffentliche Pilotgrafiken unter `public/teaching/spanish/images/variation/`
- aktive Teaching-Spezifikation in `docs/spec/platform-data-files.md`
- QA-Hilfsskript und Artefakte unter `tmp/ui-qa/2026-05-12-teaching-two-column-topic/`

## Wichtige Entscheidungen

- Die frühere Topic-`hero`-Blockdarstellung bleibt nur als Content-Eingabemuster bestehen; die sichtbare Seiteneinführung läuft jetzt über den gemeinsamen Content-Header, damit Topic-Seiten kein doppeltes Titel-/Lead-System mehr erzeugen.
- Das aktive Topic-Layout ist wieder ein Zweispaltenmodell. Nur `layout.span: 1 | 2` ist aktiv; alte `3`-Werte werden bewusst als Legacy auf `2` normalisiert.
- Hub-Karten bleiben eine einheitliche Kartenfamilie. Wenn eine Gruppe nur ein oder zwei Karten enthält, wird nicht gestreckt, sondern eine kompaktere zentrierte Kartenbreite verwendet.
- `which-pronunciation` ist jetzt der kanonische Pilotfall für den öffentlichen Spanish-Teaching-Hub und nutzt die neuen Blocktypen `section_heading`, `audio_examples`, `audio_contrast`, `further_reading` und `citation` mit Metadaten unter dem Lead.
- Audio-Beispiele ohne reale öffentliche Datei rendern keine kaputten Player und keine öffentlichen Pending-Texte; der Block bleibt als Text-/Belegsammlung lesbar.
- Inline-Code in Teaching-Markdown wird bewusst als sprachdidaktische Markierung statt als technischer Code behandelt.

## Abweichungen

- Keine Abweichung von Routing-, Auth- oder Research-Grenzen.
- Die integrierte Browser-Seitenöffnung des Agent-Tools schlug lokal mit `browserContext.newPage: Cannot read properties of undefined (reading '_page')` fehl. Für die verpflichtende Browser-QA wurde deshalb stattdessen ein lokales Selenium/Edge-Capture unter `tmp/ui-qa/2026-05-12-teaching-two-column-topic/` verwendet.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q` -> `14 passed`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching or sample_page_reflects_current_landing_and_corpus_cards"` -> `16 passed`
- Browser-QA mit `c:/dev/promat/.venv/Scripts/python.exe tmp/ui-qa/2026-05-12-teaching-two-column-topic/capture_teaching_public.py`
- Erzeugte Artefakte jetzt für Desktop und mobile Linearitätscheck auf:
  - `/de/teaching`
  - `/en/teaching`
  - `/de/teaching/spanish`
  - `/de/teaching/spanish/which-pronunciation`
  - `/de/teaching/spanish/final-r`
  - `/en/teaching/spanish`
  - `/de/sample`
  - zusätzlich mobile Captures für `/de/teaching` und `/de/teaching/spanish/which-pronunciation`
- Visuell geprüft in den erzeugten PNGs:
  - Root-Zeilen bilden rechts einen kompakten Status/CTA-Block.
  - Hub-Gruppen sitzen mit zentriertem Gruppenheader ruhig über den Karten; Zweiergruppen wirken nicht links abgebrochen.
  - `which-pronunciation` zeigt ruhige Metadaten unter dem Lead, zweispaltigen Storytelling-Fluss, Vergleichsblock und Belegsammlung getrennt, Inline-Code als didaktische Markierung, sowie Vollbreiten-Zitation am Seitenende.
  - Mobile Topic-Capture fällt linear untereinander, ohne dritte Spalte oder Aside-Wirkung.
- Konsolenwarnungen im Browser-Capture waren nur wiederholte Tracking-Prevention-Hinweise auf das Bootstrap-Icons-CDN; keine blockierenden App-Fehler.

## Offene Punkte

- Kein blockierender Punkt in diesem Slice.
- Die englische Pilotseite ist funktional vollständig, nutzt aber dieselben derzeit textbasierten Hörbelege ohne reale öffentliche Audiodateien; sobald kuratierte öffentliche Audios vorliegen, können sie ohne Layoutänderung ergänzt werden.

## Nächste sinnvolle Schritte

- Bei weiteren Spanish-Teaching-Themen direkt das neue Muster `metadata` oder `topic_meta` plus `section_heading`, `audio_examples` oder `audio_contrast`, `next_topics` und `citation` mitverwenden.
- Sobald reale öffentliche Audioquellen kuratiert sind, können die Platzhalter-freien Hörblöcke des Piloten ohne Strukturumbau mit echten Medienpfaden ergänzt werden.
