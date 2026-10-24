# Themenseite „Europa klingt auf Spanisch anders“ (Vokale und Diphthonge) neu angelegt

Datum: 2026-10-24

## Ziel

Neue, bewusst kompakte Teaching-Themenseite zu spanischen Vokalen und Diphthongen (DE/EN) nach dem Blueprint vom 2026-10-19: Schrifttransfer bei ⟨eu⟩ (*Europa*, *deuda*) → Qualität einzelner Vokale (*mismo – álbum*) → Silbenstruktur spanischer Diphthonge (*sueño*, *viuda*). Eine Vokalseite existierte noch nicht (ein früherer Test hielt ausdrücklich „planned vowel page: no placeholder“ fest), also wurde eine neue Seite angelegt statt einer bestehenden zu ändern.

## Consulted Sources

- Blueprint, `docs/spec/platform-data-files.md`, `docs/runbooks/teaching-corpus-audio.md`, Run-Logs der Seiten *Das spanische r*, *Das r am Wortende*, *b, d und g*.
- Digitales Lehrbuch: *Orthographie* (`#vokale`: ⟨eu⟩ in *Europa* und *deuda* als Schrifttransfer), *Aussprache* (`#laute-des-spanischen-herausforderungen`: [i]/[ɪ] mit *bieten*/*bitten*, Diphthonge, *fuego*). Für [uː]/[ʊ] gibt das Lehrbuch kein Parallelbeispiel; die Seite stützt sich dafür auf das vertraute deutsche *Album* [ˈalbʊm].
- Lokale Runtime `data/sessions/spanish`, Wortliste (W-Nummern gegen den Katalog bestätigt: W80 *Europa*, W22 *deuda*, W37 *mismo*, W44 *álbum*, W40 *sueño*, W3 *viuda*).

## URLs und redaktionelle Struktur

`/de/teaching/spanish/europe-sounds-different` und `/en/teaching/spanish/europe-sounds-different` (Slug englisch wie die übrigen; im Hub als erstes Thema der Gruppe „Aussprachephänomene entdecken“, Vokale vor Konsonanten; Autor: Felix Tacke allein). Titel EN: „Europe sounds different in Spanish“.

Kurzer Einstieg (3 Sätze) → **Hörvergleich *Europa*** (einzige Auflösung, zugeklappt) → **Hörvergleich *deuda*** + ein Satz → *Fünf Vokale – nicht ganz wie im Deutschen*: kurzer Text, **Hörvergleich *mismo* – *álbum*** (kombiniert), Text zu gespannten/ungespannten Vokalen → *Wenn aus einem Diphthong zwei Silben werden*: Text mit *fuego* (Lehrbuchbeispiel ohne Audio), **Hörvergleich *sueño***, ein Satz, **Hörvergleich *viuda*** → *Impulse für den Unterricht* (drei) → *Vertiefung* (Aussprache, Orthographie, *Weiches Spanisch, hartes Deutsch*) → Zitation. Keine Grafik, keine „Auf einen Blick“-Box, keine generische Rubrik; Wortakzent bleibt der Seite *Ein Akzent verändert alles* vorbehalten.

## Audioarchitektur (fünf Hörkästen, 10 Aufnahmen)

| Karte | Item | Referenz | Lernende:r | Comparison-ID |
|---|---|---|---|---|
| 1 | W80 `wl_080` *Europa* | ES-N-0002 (Spanien) | ES-L-0021 | `p7-europa` |
| 2 | W22 `wl_022` *deuda* | ES-N-0002 | ES-L-0021 | `p7-deuda` |
| 3 | W37 `wl_037` *mismo* + W44 `wl_044` *álbum* (Montage) | ES-N-0005 (Chile) | ES-L-0011 | `p7-mismo-album` |
| 4 | W40 `wl_040` *sueño* | ES-N-0001 (Spanien) | ES-L-0010 | `p7-sueno` |
| 5 | W3 `wl_003` *viuda* | ES-N-0001 | ES-L-0010 | `p7-viuda` |

Alle Aufnahmen stammen aus ProMat (keine MAR.ELE-Aufnahme verwendet). Karten 1, 2, 4, 5 sind unveränderte Item-MP3; Untertitel nennen Region und Item (*Spanien · W80*), Lernenden-Labels tragen kein Niveau.

### Technische Erstellung der Montage *mismo – álbum*

Das Slot-System wurde allgemein um mehrteilige Derivate erweitert (kein Sonderweg für die Seite): ein Eintrag trägt statt `item`/`crop` die Liste `parts` (je `item`, `target_tokens`, `crop`, `source_sha256`) und `join.pause_ms`. `scripts/teaching_audio_slots.py`: `recording_parts`, `derive_montage`, Prüfungen und Freigabebericht laufen je Teil; bestehende Einträge sind unverändert (alle früheren Tests grün, andere Medien bitgleich). Schnittpunkte je Wort nach Energieverlauf (Floor −40 dB), 50 ms Vorlauf, 70 ms Nachlauf, Fades 15/25 ms:

| Slot | Teil | Session | Schnitt (ms) |
|---|---|---|---|
| ref | *mismo* `wl_037` | ES-N-0005 | 250–840 |
| ref | *álbum* `wl_044` | ES-N-0005 | 250–880 |
| learner | *mismo* `wl_037` | ES-L-0011 | 210–970 |
| learner | *álbum* `wl_044` | ES-L-0011 | 255–1010 |

Zwischen den Wörtern liegen 300 ms eingefügte Stille (mit Nach- und Vorlauf ca. 0,42 s wirksame Pause; zuerst 400 ms, auf „kurz“ gekürzt); Dateien 1,52 s (Referenz) und 1,82 s (Lernende:r). Keine Änderung von Tonhöhe oder Tempo, Originale unberührt (Hashes in `audio-slots.yaml`), Export bitgleich reproduzierbar (ffmpeg 8.1). Auf der Seite trägt jede der zwei Player-Karten den Hinweis „Zwei Einzelwörter, hintereinander montiert“ bzw. „Two single words, spliced one after the other“, die Untertitel nennen beide Items (*W37, W44*), und der Chip zeigt `mismo – álbum`. Fortschrittsfüllung des Chips im Browser geprüft.

## Teaching-Freigaben (`--release-report`, Auszug)

| session | item | role | use | consent | review | speaker_type | item_text | result |
|---|---|---|---|---|---|---|---|---|
| ES-N-0002-2026-S01 | wl_080 | reference | p7-europa | yes | False | native_speaker | Europa | OK |
| ES-L-0021-2026-S01 | wl_080 | learner | p7-europa | yes | False | learner | Europa | OK |
| ES-N-0002-2026-S01 | wl_022 | reference | p7-deuda | yes | False | native_speaker | deuda | OK |
| ES-L-0021-2026-S01 | wl_022 | learner | p7-deuda | yes | False | learner | deuda | OK |
| ES-N-0005-2026-S01 | wl_037 | reference | p7-mismo-album (Teil 1) | yes | False | native_speaker | mismo | OK |
| ES-N-0005-2026-S01 | wl_044 | reference | p7-mismo-album (Teil 2) | yes | False | native_speaker | álbum | OK |
| ES-L-0011-2026-S01 | wl_037 | learner | p7-mismo-album (Teil 1) | yes | False | learner | mismo | OK |
| ES-L-0011-2026-S01 | wl_044 | learner | p7-mismo-album (Teil 2) | yes | False | learner | álbum | OK |
| ES-N-0001-2026-S01 | wl_040 | reference | p7-sueno | yes | False | native_speaker | sueño | OK |
| ES-L-0010-2026-S01 | wl_040 | learner | p7-sueno | yes | False | learner | sueño | OK |
| ES-N-0001-2026-S01 | wl_003 | reference | p7-viuda | yes | False | native_speaker | viuda | OK |
| ES-L-0010-2026-S01 | wl_003 | learner | p7-viuda | yes | False | learner | viuda | OK |

Acht Reserven (nicht integriert, ebenfalls im Gate geprüft, alle `OK`): ES-L-0008 (*Europa*, *deuda*), ES-L-0004 und ES-L-0019 (*mismo*, *álbum*), ES-L-0015 (*sueño*), ES-L-0017 (*viuda*). `EXCLUDED_SESSIONS` unberührt.

## Akustische Kuration – **nicht abgehört; Befunde nur signalseitig**

In dieser Umgebung ist kein Abhören möglich. Gemessen wurden Formantverläufe (LPC, F1/F2) und Dauern in den Item-Aufnahmen aller 4 freigegebenen Referenzstimmen und aller 21 freigegebenen Lernenden. **Phonetisch bestätigt im Sinne eines Hörbefunds ist nichts**; die Seitentexte behaupten deshalb nichts über konkrete Realisierungen einer Lernendenaufnahme (keine Auflösung außer bei *Europa*, und diese beschreibt die Regel „kann“).

| Karte | Signalbefund | Einordnung |
|---|---|---|
| *Europa* | Alle vier Referenzen: F2 fällt im ⟨eu⟩ stark (ES-N-0002: ca. 2450 → 850 Hz), also [e] → [u]. Bei 7 von 21 Lernenden steigt F2 dagegen (ES-L-0021: ca. 1100 → 2000 Hz über ca. 180 ms), also die Richtung von [ɔɪ̯] (ʻo → i‘). | **gut belegt (Signal)**: gegenläufiger Diphthong |
| *deuda* | ES-N-0002: ca. 2340 → 1140 Hz (fallend); ES-L-0021: ca. 1200 → 1950 Hz (steigend), dieselbe Gegenrichtung wie bei *Europa*. Der *d*-Anlaut macht den Verlauf verrauschter. | **gut belegt (Signal)**; dieselbe Person wie bei *Europa* |
| *mismo – álbum* | **Nicht überzeugend belegt.** ES-L-0011 hat bei /i/ das höchste F1 aller Lernenden (≈ 430 Hz gegenüber ≈ 300–350 Hz bei den Referenzen) und bei /u/ ein erhöhtes F1 (≈ 420 Hz) bei zentralisiertem F2 (≈ 1400 Hz gegenüber ≈ 750–900 Hz bei den Referenzen), beides mit [ɪ]/[ʊ] vereinbar, aber der Abstand ist gering und die F1-Bereiche von Referenzen und Lernenden überlappen. Die Referenz ES-N-0005 hat eindeutig gespannte [i] (F1 ≈ 340, F2 ≈ 2200) und [u] (F1 ≈ 300, F2 ≈ 750). | **vorläufig, Hörprüfung nötig**; ES-L-0004 (/u/ F1 ≈ 480, F2 ≈ 1050 Hz) und ES-L-0019 als Reserven |
| *sueño* | Referenzen: tiefe-F2-Phase des [u] 45–90 ms, danach schneller V-förmiger Anstieg zum [e]. ES-L-0010: ca. 100–115 ms stabil tiefes F2, danach langsamerer Anstieg. | **schwach belegt (Signal)**: mit zwei Silben vereinbar |
| *viuda* | Referenzen (ES-N-0001/0005): hohe-F2-Phase des [i] nur ca. 70–90 ms, dann gleitender Abfall zum [u]. ES-L-0010 und ES-L-0017: stabile hohe-F2-Phase von 150–200 ms, dann Abfall zu einem eigenständigen [u]. Die Intensitätsgipfel-Zählung war nicht trennscharf. | **schwach belegt (Signal)**: mit einem vollen Silbenkern für *i* vereinbar |

**Nicht belegt / zu hören:** (1) *mismo*: ob die Lernendenaufnahme tatsächlich [ɪ] zeigt; (2) *álbum*: ob [ʊ]; (3) *sueño* und *viuda*: ob wirklich zwei bzw. drei Silben realisiert werden und nicht nur ein langsames Tempo oder eine betonte Aussprache; bei *viuda* wurde der Anlaut-*v* bewusst nicht gewertet. Zur Hörprüfung vorgemerkt: genau die zehn Aufnahmen der Seite plus die Reserven.

### Verworfene bzw. nicht verwendete Kandidaten

- *ciudad*, *cuidado*, *tierra*, *buscó*, *centro*, *pastel*: laut Auftrag ausgeschlossen.
- ES-N-0004 (Mexiko) als Referenz: bei *deuda* kein klarer fallender Verlauf, bei *sueño* keine messbare [u]-Phase, bei *viuda* lange hohe-F2-Phase (200 ms) – für Diphthong-Referenzen ungeeignet. ES-N-0001 bei *deuda*: flacher F2-Verlauf.
- ES-L-0005: *Europa* gegenläufig, *deuda* aber spanisch-ähnlich fallend – nicht konsistent. ES-L-0015 (*sueño*: [u]-Phase 155 ms) nur als Reserve, weil das Gesamttempo sehr langsam ist.
- MAR.ELE (siehe unten): kein Material übernommen.

### Prüfung des MAR.ELE-Altmaterials für *mismo*/*álbum*

Da die ProMat-Befunde bei *mismo* nicht überzeugen, wurde das Rohmaterial von MAR.ELE gesichtet (Projektordner; nur Aufnahmen und Einwilligungsspalte, keine personenbezogenen Daten verarbeitet). Befund: Die Wortlisten-Aufnahmen (`NNN_liste.wav`, 22 L1-Deutsch-Lernende) sind lange Einzeldateien ohne Wortgrenzen; sie wurden an Sprechpausen segmentiert (bei den meisten Personen 125 Segmente, also fester Listenreihenfolge) und *mismo*/*álbum* per MFCC-DTW-Konsens über die Listenposition gesucht (*mismo* ≈ Position 39, *álbum* ≈ 48). Die gemessenen /i/-Werte der MAR.ELE-Lernenden (F1 ≈ 240–440 Hz, F2 ≈ 2100–2650 Hz) liegen im selben Bereich wie bei ProMat, /u/ ließ sich meist nicht zuverlässig messen. Damit zeigte das Altmaterial **keinen klareren Kontrast**; zudem wäre die Zuordnung nur per Gehör verlässlich und für eine Montage aus externen Quellen und die Einwilligungsklärung (in der Informantentabelle bei 20 Personen ein Vermerk, bei drei keiner) neue Arbeit nötig. Es wurde daher nichts davon integriert. Zum Hineinhören liegen die gefundenen Kandidatenstellen als kurze Klips lokal vor (`tmp/ui-qa/2026-10-24-spanish-vowels/marele-candidates/` mit Übersicht `marele-candidates.md`, git-ignoriert, nicht im Repository).

## Verifikation

- `scripts/teaching_audio_slots.py --check` / `--release-report`, `scripts/validate_teaching_content.py`, `scripts/ci_governance_checks.py`: grün.
- Tests: `test_teaching_spanish_topics.py` um Dramaturgie DE/EN, Titel/Teaser/Zitation, Kuration und Montage-Deklaration, Negativtests der Montage-Regeln, reproduzierbaren Export (Dauer = Schnitte + Pause), Release-Bericht je Teil erweitert; bestehende Zählungen (Hub, Übersicht, 57 Aufnahmen) angepasst; Deploy-Smoke kennt die neue Seite.
- Browser (Chromium, lokal :8011): DE/EN, Desktop 1366 px und Mobil 390 px, hell und dunkel, kein horizontales Scrollen; alle 10 Aufnahmen laden und laufen (Dauer 1,10–1,82 s), keine HTTP-Fehler; Chip der Montagekarte reagiert auf die Wiedergabe. Akustisch nicht beurteilt.
- Volltest: siehe Abschnitt *Commit und Deployment*.

## Commit und Deployment

(wird nach dem Lauf ergänzt)
