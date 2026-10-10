# Sechs spanische Themenseiten mit Korpus-Hörvergleichen

Datum: 2026-10-10

## Ziel

Die sechs Themenseiten *Weiches Spanisch, hartes Deutsch*, *Das spanische r*, *R am Silbenende*, *B oder V?*, *Weiche Konsonanten: b, d und g* und *Ein Akzent verändert alles* redaktionell fertig ausarbeiten, in DE und EN, mit realen Korpusaufnahmen (Referenz und Lernende) und austauschbaren Audio-Slots.

## Consulted Sources

- `docs/spec/platform-data-files.md` (Teaching-Contract, Medien, Zitation), `docs/spec/intake-workbook.md` / `research-access.md` (`teaching_consent_signed`)
- bestehende Seite `which-pronunciation`, `app/src/app/teaching_content.py`, `scripts/validate_teaching_content.py`
- kuratierte Spanisch-Sets (Export vom selben Tag), `linguistik.hispanistica.com` (Kapitel Aussprache, Fehlerlinguistik, Orthographie)

## URLs

`/{de|en}/teaching/spanish/{slug}` mit den Slugs `soft-spanish-hard-german`, `r`, `r-am-silbenende` (vorhanden, jetzt veröffentlicht) sowie neu `b-or-v`, `soft-consonants-b-d-g`, `accent-changes-everything`. Die Übersicht ist `/{ui_lang}/teaching/spanish`.

## Abweichungen vom Auftrag (Repository-Stand hat Vorrang)

- Die genannte Übersicht `/teaching/spanish/topics` gibt es nicht; die Themenseiten-Übersicht ist der Edition-Hub `/teaching/spanish`.
- Item-IDs im Korpus lauten `wl_NNN`, `d_NN`, `qy_NN`, `qw_NN` (Auftrag: W88, D7, QW8); die Zuordnung wurde gegen Wort- und Satzliste geprüft und stimmt (W87 = *número – numero – numeró*, W88 = *caro – carro*, W90, W92 usw.).
- *de vino* steht nicht in QW3, sondern in QY1 (*¿El vaso está lleno de vino ahora?*); QW3 enthält nur *el vino*. Für *vino* im Satz wird QY1 verwendet.
- Das Lehrbuch (linguistik.hispanistica.com/aussprache) sagt zum Knacklaut „im Spanischen jedoch nie“; die Seite 1 formuliert vorsichtiger (in verbundener Rede nicht charakteristisch, kontextabhängige Glottalisierung möglich). Das Beispiel *o hay* ist dort tatsächlich behandelt (Audio aus MAR.ELE, Ziel [o.ˈai], Lernende [ʔo.ʔai]). Eine Vokalisierung des spanischen r behandelt das Lehrbuch nicht; es nennt dafür das Beispiel *reír* ([re.ˈiɾ] gegenüber [ʁe.ˈɪɐ]).
- Wortakzent behandelt das Lehrbuch im Kapitel *Orthographie* (`#wortakzent`, `#die-tilde-der-orthographische-akzent`), nicht in *Aussprache*; dorthin wird verlinkt.
- Die fachlichen Texte wurden an einigen Stellen präzisiert: /b/ ist nach /l/ approximantisch, /d/ dagegen nach /l/ ein Verschlusslaut; die Realisierung von /g/ nach /l/ (*algo*) ist approximantisch; für *vino* wird der Wechsel [b] (nach Pause) – [β] (*de vino*) beschrieben; die Opposition /ɾ/ – /r/ besteht nur intervokalisch (Neutralisierung am Wortanfang und nach n/l/s).

## Geänderte Bereiche

- `content/teaching/spanish/{slug}/{de,en}.yaml` (12 Dateien, bisherige Scaffolds ersetzt), `hubs/{de,en}.yaml` (Reihenfolge Grundlagen: 2, Laute und Artikulation: 5)
- `content/teaching/spanish/audio-slots.yaml` (zentrale Deklaration), `…/media/audio/corpus/*.mp3` (58 Dateien, 2,9 MB)
- `scripts/teaching_audio_slots.py` (`--export`, `--check`), `docs/runbooks/teaching-corpus-audio.md`
- neuer Block `solution` (aufklappbare Auflösung, natives `<details>`): `teaching_content.py`, `_teaching_blocks.html`, `teaching_page.html`, i18n, CSS (`pm-teaching-solution*`, nur bestehende Tokens)
- `scripts/post_deploy_smoke.py` (alle sieben Themenseiten), Spezifikation (`solution`, Korpusaufnahmen, Kartenbeschreibung)
- Tests: neu `test_teaching_spanish_topics.py` (40 Tests); angepasst `test_research_sessions.py`, `test_publication_metadata.py` (Seiten sind nicht mehr Entwürfe; das Scaffold-Beispiel für Blocktypen ist jetzt `french/liaison`)

## Audio

58 Aufnahmen in 26 Vergleichen (3–5 Items je Seite, jeweils Referenz und Lernende, bei Kontextvergleichen Einzelwort und Satz). Quelle: finale Item-MP3s der lokalen Runtime; geprüft wird `teaching_consent_signed: yes`, `needs_review: false` und der Sprechertyp.

| Seite | Referenz | Lernende |
|---|---|---|
| Weiches Spanisch | ES-N-0004 (Mexiko) | ES-L-0007 (B1) |
| Das spanische r | ES-N-0002 (Spanien) | ES-L-0012 (B1) |
| R am Silbenende | ES-N-0001 (Spanien) | ES-L-0019 (A2) |
| B oder V? | ES-N-0004 (Mexiko) | ES-L-0017 (A2) |
| Weiche Konsonanten | ES-N-0001 (Spanien) | ES-L-0013 (B1) |
| Ein Akzent | ES-N-0005 (Chile) | ES-L-0005 (B1) |

Ausgeschlossen: ES-L-0014 und ES-N-0003 (`teaching_consent_signed: no`), ES-L-0023 (Erstsprache Portugiesisch). Die Lernendenaufnahme je Seite wurde automatisch gewählt (typische Dauer je Item, keine Ausreißer). **Keine Aufnahme wurde phonetisch geprüft**; die Seiten behaupten deshalb nirgends eine konkrete Abweichung einer Lernendenaufnahme, sondern geben Hörfragen und eine neutrale Auflösung.

Manuelle Kuratierung nötig: alle 26 Vergleiche, besonders die Lernendenaufnahmen der Hörblöcke (*tiene hambre*, *caro – carro*, *reír*, *bienes – vienes*, *labio*, W87), da dort die Auflösung nur beschreibt, worauf zu hören ist. Austausch: `audio-slots.yaml` ändern, `--export`, Runbook.

## Wichtige Entscheidungen

- Ein Aufnahme-Slot ist ein stabiler Dateiname (`corpus/{vergleich}-{ref|learner}[-{isoliert|satz}].mp3`); Seiten nennen nur Dateinamen, die Herkunft steht ausschließlich in `audio-slots.yaml` (mit `sha256`, Prüfung in Test und `--check`).
- Hörblöcke ohne Schriftbild (*caro – carro*, *bienes – vienes*, W87, *reloj*) blenden die „Wortfolge“ aus; die Auflösung steht im einklappbaren `solution`-Block, nicht in Notizen.
- Die englischen Fassungen sind vollständige, fachlich gleiche Fassungen (gleiche Blockfolge, gleiche Audiodateien); ein Test sichert den strukturellen Gleichstand.

## Nachtrag: keine Zitierkästen auf Teaching-Übersichtsseiten

Der Hub-Builder (`teaching_content.build_teaching_hub_page`) liefert für jede Sprache und Edition `citation: None`; damit zeigen alle Sprach-Übersichten (auch künftig angelegte) keinen Zitierkasten. Die Publikationsressource des Hubs bleibt für Canonical und JSON-LD erhalten, die Registry unverändert. Einzelne Themenseiten (die sechs neuen und *Welche Aussprache unterrichten?*) behalten ihre generierte Zitation mit Autorschaft, Titel und URL (Test: `test_generated_citations_follow_the_four_levels`, Browser-Smoke). Angepasst: Spezifikation (Zitierorte), `post_deploy_smoke.py`, `ci_browser_smoke.py`, der tote Abstands-Token `--pm-teaching-citation-gap` entfiel.

## Verifikation

- `ruff`, `compileall`, `ci_governance_checks`, `validate_teaching_content`, `teaching_audio_slots --check` grün; `app/tests`: alle grün außer dem bereits vorher roten Windows-Test `test_legal_pages_render_in_image_layout…`; Browser-Smoke 263 Checks ohne Fehler.
- Browser (`tmp/ui-qa/2026-10-10-six-topics/`): alle zwölf Seiten ohne JS-/Konsolenfehler, ohne 4xx-Antworten (Audio), ohne Überlauf auf 1280 und 390 px; Stichproben in Hell/Dunkel (Hörblock, Auflösung, Boxen, Vertiefung, Zitat).
