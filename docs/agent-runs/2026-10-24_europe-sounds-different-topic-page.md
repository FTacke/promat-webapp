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
| 3 | *mismo* + *álbum* (Montage aus MAR.ELE-Einzelwörtern, Listenpositionen 40 und 49) | `inf-L1-ES_es` (MAR.ELE-Kontrollsprecher:in, Spanisch) | `inf-019` (MAR.ELE, L1 Deutsch) | `p7-mismo-album` |
| 4 | W40 `wl_040` *sueño* | ES-N-0001 (Spanien) | ES-L-0010 | `p7-sueno` |
| 5 | W3 `wl_003` *viuda* | ES-N-0001 | ES-L-0010 | `p7-viuda` |

Karten 1, 2, 4, 5 sind unveränderte ProMat-Item-MP3; Untertitel nennen Region und Item (*Spanien · W80*), Lernenden-Labels tragen kein Niveau. Karte 3 stammt aus MAR.ELE (Untertitel *MAR.ELE*, wie auf den Seiten *b oder v?* und *b, d und g*). **Erste Fassung (Commit 13d579e, live gewesen):** Montage aus ProMat ES-N-0005 (Chile) und ES-L-0011 (W37/W44); sie war signalseitig schwach (siehe unten) und wurde nach dem Hinweis, dass es zu allen MAR.ELE-Informant:innen Einzel-MP3 je Item gibt, durch die MAR.ELE-Montage ersetzt. Die ProMat-Variante steht in der Git-Historie, ihre Quellen sind weiterhin als Reserven dokumentiert.

### Technische Erstellung der Montage *mismo – álbum*

Das Slot-System wurde allgemein um mehrteilige Derivate erweitert (kein Sonderweg für die Seite): ein Eintrag trägt statt `item`/`crop` die Liste `parts` (je `target_tokens`, `crop`, `source_sha256` und `item` bei ProMat-Sessions bzw. `source_file` bei MAR.ELE) und `join.pause_ms`. `scripts/teaching_audio_slots.py`: `recording_parts`, `derive_montage`, `external_montage_problems`, Prüfungen und Freigabebericht laufen je Teil; MAR.ELE-Montagen tragen `origin.corpus` und werden mit `--export --marele-root <Backup>` (oder `PROMAT_MARELE_ROOT`) gerendert. Bestehende Einträge sind unverändert (andere Medien bitgleich). Quelle: Einzel-MP3 aus dem lokalen MAR.ELE-Webapp-Backup (`items/inf-NNN_<Position>_<Wort>.mp3`; das Backup enthält Zugangsdaten und wurde nicht ins Repository kopiert, nur die Schnitte). Schnittpunkte je Wort nach Energieverlauf und Spektrogramm, Fades 15/25 ms:

| Slot | Teil | Quelldatei | Schnitt (ms) | Quell-SHA-256 (Anfang) |
|---|---|---|---|---|
| ref | *mismo* | `inf-L1-ES_es_040_mismo.mp3` | 550–1240 | `1b2239ed…` |
| ref | *álbum* | `inf-L1-ES_es_049_álbum.mp3` | 480–1135 | `ebccfbb6…` |
| learner | *mismo* | `inf-019_040_mismo.mp3` | 470–1230 | `385d560c…` |
| learner | *álbum* | `inf-019_049_álbum.mp3` | 465–1175 | `b6fbba75…` |

Zwischen den Wörtern liegen 300 ms eingefügte Stille (mit Nach- und Vorlauf der Schnitte gemessen ca. 0,38 s bzw. 0,42 s Pause); Dateien `marele/p7-mismo-album-ref.mp3` 1,645 s und `marele/p7-mismo-album-learner.mp3` 1,770 s. Keine Änderung von Tonhöhe oder Tempo, Originale unberührt (Hashes in `audio-slots.yaml`), Export bitgleich reproduzierbar (ffmpeg 8.1; der Test überspringt sich ohne Backup). Wellenform und Spektrogramm beider Montagen geprüft: beide Wörter vollständig, keine Klicks an den Schnittstellen. Auf der Seite trägt jede der zwei Player-Karten den Hinweis „Zwei Einzelwörter, hintereinander montiert“ bzw. „Two single words, spliced one after the other“, der Chip zeigt `mismo – álbum` als zwei getrennte Einträge.

**Einwilligung (bitte bestätigen):** Das MAR.ELE-Einwilligungsformular erlaubt die Verwendung in „Forschungskontexten wie Vorträgen und didaktischen Kontexten wie Lehrveranstaltungen als Beispiele für die Sensibilisierung für Interferenzphänomene“; Namen und Kontaktdaten werden nicht veröffentlicht. In der Informantentabelle ist die Einwilligung für `inf-019` (und die Alternative `inf-021`) vermerkt. Ob dies auch die Veröffentlichung auf der öffentlichen Teaching-Seite abdeckt, ist nicht automatisch geprüft (anders als bei ProMat gibt es hier kein Gate); die Seite nutzt MAR.ELE-Aufnahmen bereits an anderen Stellen.

## Teaching-Freigaben (`--release-report`, Auszug)

| session | item | role | use | consent | review | speaker_type | item_text | result |
|---|---|---|---|---|---|---|---|---|
| ES-N-0002-2026-S01 | wl_080 | reference | p7-europa | yes | False | native_speaker | Europa | OK |
| ES-L-0021-2026-S01 | wl_080 | learner | p7-europa | yes | False | learner | Europa | OK |
| ES-N-0002-2026-S01 | wl_022 | reference | p7-deuda | yes | False | native_speaker | deuda | OK |
| ES-L-0021-2026-S01 | wl_022 | learner | p7-deuda | yes | False | learner | deuda | OK |
| ES-N-0001-2026-S01 | wl_040 | reference | p7-sueno | yes | False | native_speaker | sueño | OK |
| ES-L-0010-2026-S01 | wl_040 | learner | p7-sueno | yes | False | learner | sueño | OK |
| ES-N-0001-2026-S01 | wl_003 | reference | p7-viuda | yes | False | native_speaker | viuda | OK |
| ES-L-0010-2026-S01 | wl_003 | learner | p7-viuda | yes | False | learner | viuda | OK |

Die MAR.ELE-Montage (`p7-mismo-album`) hat keine ProMat-Session und daher keine Zeile im Freigabebericht (wie die übrigen MAR.ELE-Aufnahmen; Prüfung siehe Einwilligungshinweis oben). Acht Reserven (nicht integriert, ebenfalls im Gate geprüft, alle `OK`): ES-L-0008 (*Europa*, *deuda*), ES-L-0004 und ES-L-0019 (*mismo*, *álbum*), ES-L-0015 (*sueño*), ES-L-0017 (*viuda*). `EXCLUDED_SESSIONS` unberührt.

## Akustische Kuration – **nicht abgehört; Befunde nur signalseitig**

In dieser Umgebung ist kein Abhören möglich. Gemessen wurden Formantverläufe (LPC, F1/F2) und Dauern in den Item-Aufnahmen aller 4 freigegebenen Referenzstimmen und aller 21 freigegebenen Lernenden. **Phonetisch bestätigt im Sinne eines Hörbefunds ist nichts**; die Seitentexte behaupten deshalb nichts über konkrete Realisierungen einer Lernendenaufnahme (keine Auflösung außer bei *Europa*, und diese beschreibt die Regel „kann“).

| Karte | Signalbefund | Einordnung |
|---|---|---|
| *Europa* | Alle vier Referenzen: F2 fällt im ⟨eu⟩ stark (ES-N-0002: ca. 2450 → 850 Hz), also [e] → [u]. Bei 7 von 21 Lernenden steigt F2 dagegen (ES-L-0021: ca. 1100 → 2000 Hz über ca. 180 ms), also die Richtung von [ɔɪ̯] (ʻo → i‘). | **gut belegt (Signal)**: gegenläufiger Diphthong |
| *deuda* | ES-N-0002: ca. 2340 → 1140 Hz (fallend); ES-L-0021: ca. 1200 → 1950 Hz (steigend), dieselbe Gegenrichtung wie bei *Europa*. Der *d*-Anlaut macht den Verlauf verrauschter. | **gut belegt (Signal)**; dieselbe Person wie bei *Europa* |
| *mismo – álbum* (erste Fassung, ProMat, ersetzt) | **Nicht überzeugend belegt.** ES-L-0011 hat bei /i/ das höchste F1 aller Lernenden (≈ 430 Hz gegenüber ≈ 300–350 Hz bei den Referenzen) und bei /u/ ein erhöhtes F1 (≈ 420 Hz) bei zentralisiertem F2 (≈ 1400 Hz gegenüber ≈ 750–900 Hz bei den Referenzen), beides mit [ɪ]/[ʊ] vereinbar, aber der Abstand ist gering und die F1-Bereiche von Referenzen und Lernenden überlappen. Die Referenz ES-N-0005 hat eindeutig gespannte [i] (F1 ≈ 340, F2 ≈ 2200) und [u] (F1 ≈ 300, F2 ≈ 750). | **vorläufig, Hörprüfung nötig**; ES-L-0004 (/u/ F1 ≈ 480, F2 ≈ 1050 Hz) und ES-L-0019 als Reserven; dadurch ersetzt (siehe unten) |
| *sueño* | Referenzen: tiefe-F2-Phase des [u] 45–90 ms, danach schneller V-förmiger Anstieg zum [e]. ES-L-0010: ca. 100–115 ms stabil tiefes F2, danach langsamerer Anstieg. | **schwach belegt (Signal)**: mit zwei Silben vereinbar |
| *viuda* | Referenzen (ES-N-0001/0005): hohe-F2-Phase des [i] nur ca. 70–90 ms, dann gleitender Abfall zum [u]. ES-L-0010 und ES-L-0017: stabile hohe-F2-Phase von 150–200 ms, dann Abfall zu einem eigenständigen [u]. Die Intensitätsgipfel-Zählung war nicht trennscharf. | **schwach belegt (Signal)**: mit einem vollen Silbenkern für *i* vereinbar |

**Nicht belegt / zu hören:** (1) *mismo*: ob die Lernendenaufnahme tatsächlich [ɪ] zeigt; (2) *álbum*: ob [ʊ]; (3) *sueño* und *viuda*: ob wirklich zwei bzw. drei Silben realisiert werden und nicht nur ein langsames Tempo oder eine betonte Aussprache; bei *viuda* wurde der Anlaut-*v* bewusst nicht gewertet. Zur Hörprüfung vorgemerkt: genau die zehn Aufnahmen der Seite plus die Reserven.

### Verworfene bzw. nicht verwendete Kandidaten

- *ciudad*, *cuidado*, *tierra*, *buscó*, *centro*, *pastel*: laut Auftrag ausgeschlossen.
- ES-N-0004 (Mexiko) als Referenz: bei *deuda* kein klarer fallender Verlauf, bei *sueño* keine messbare [u]-Phase, bei *viuda* lange hohe-F2-Phase (200 ms) – für Diphthong-Referenzen ungeeignet. ES-N-0001 bei *deuda*: flacher F2-Verlauf.
- ES-L-0005: *Europa* gegenläufig, *deuda* aber spanisch-ähnlich fallend – nicht konsistent. ES-L-0015 (*sueño*: [u]-Phase 155 ms) nur als Reserve, weil das Gesamttempo sehr langsam ist.
- MAR.ELE: nur für Karte 3 verwendet (siehe unten); andere Kandidaten (u. a. `inf-021`) nicht integriert.

### Die MAR.ELE-Fassung von *mismo – álbum*

Zuerst wurden die langen Wortlisten-Aufnahmen von MAR.ELE per Sprechpausen-Segmentierung und MFCC-DTW-Konsens über die Listenposition durchsucht (*mismo* ≈ Position 39, *álbum* ≈ 48); das war ohne Wortgrenzen nur grob verlässlich und zeigte keinen klareren Kontrast. Der Hinweis, dass es im MAR.ELE-Backup Einzel-MP3 je Item und Informant:in gibt (`items/inf-NNN_040_mismo.mp3`, `…_049_álbum.mp3`; die Positionen 40 und 49 entsprechen der zuvor per Konsens gefundenen Listenposition 39/48, dort nullbasiert gezählt), erlaubte eine direkte Messung aller 23 Informant:innen plus Kontrollsprecher:in `inf-L1-ES_es`:

- Messung je Informant:in (LPC, F1/F2 des /i/ in *mismo*, des /u/ in *álbum*, Verhältnis zum F1 des /a/ in *álbum*): bei den meisten Lernenden liegt F1 des /i/ bei ca. 300–440 Hz und das Verhältnis F1(/i/)/F1(/a/) bei 0,36–0,51; `inf-019` hat mit F1 ≈ 428 Hz und Verhältnis 0,61 (Nukleus 175 ms) den höchsten Wert, ihr /u/ in *álbum* F1 ≈ 426 Hz, F2 ≈ 908 Hz (Verhältnis 0,61). Das ist mit ungespannten [ɪ]/[ʊ] vereinbar (offener als [i]/[u]); der F2 des /i/ (≈ 2380 Hz) ist dabei nicht auffällig zentralisiert.
- `inf-L1-ES_es` (Kontrollsprecher:in): das automatische Verfahren fand für /i/ und /u/ keinen stabilen Kern; die Schnittpunkte wurden daher nach Energieverlauf und Spektrogramm gesetzt, und die Vokalqualität der Kontrolle (ca. F1 250–300 Hz im /i/ nach der früheren Sichtung) ist nur grob signalseitig belegt.
- Alternative: `inf-021` mit fast identischem Wert (F1 ≈ 436 Hz, Verhältnis 0,60; /u/ F1 ≈ 398 Hz, Verhältnis 0,55); nicht integriert, falls die Hörprüfung `inf-019` nicht bestätigt.

**Nicht gehört:** Dass `inf-019` tatsächlich [ɪ] und [ʊ] spricht, ist ein Signalbefund und nicht per Hörprobe bestätigt. Die Seite benennt kein konkretes Ergebnis für die Aufnahme, sondern fragt nach dem Unterschied der Vokale; der erklärende Text beschreibt nur, was „entstehen kann“. Zum Hineinhören liegen die Kandidaten lokal als Klips vor (`tmp/ui-qa/2026-10-24-spanish-vowels/marele-candidates/`, git-ignoriert, nicht im Repository).

## Verifikation

- `scripts/teaching_audio_slots.py --check` / `--release-report`, `scripts/validate_teaching_content.py`, `scripts/ci_governance_checks.py`: grün.
- Tests: `test_teaching_spanish_topics.py` um Dramaturgie DE/EN, Titel/Teaser/Zitation, Kuration und Montage-Deklaration, Negativtests der Montage-Regeln, reproduzierbaren Export (Dauer = Schnitte + Pause), Release-Bericht je Teil erweitert; bestehende Zählungen (Hub, Übersicht, 57 Aufnahmen) angepasst; Deploy-Smoke kennt die neue Seite.
- Browser (Chromium, lokal :8011): DE/EN, Desktop 1366 px und Mobil 390 px, hell und dunkel, kein horizontales Scrollen; alle 10 Aufnahmen laden und laufen (Dauer 1,10–1,82 s), keine HTTP-Fehler; Chip der Montagekarte reagiert auf die Wiedergabe. Akustisch nicht beurteilt.
- Volltest: siehe Abschnitt *Commit und Deployment*.

## Commit und Deployment

Erste Fassung (ProMat-Montage): Commit 13d579e, CI und „Deploy production“ grün. Zweiter Commit dieses Laufs: Umstellung der Karte *mismo – álbum* auf die MAR.ELE-Montage (Slot-Skript mit externen Montagen und `--marele-root`, `audio-slots.yaml`, DE/EN-Seiten, Tests, Spec, Runbook, dieser Bericht). Volltest vor dem Commit: alle Tests grün (Themenseiten-Tests 110 passed; `--check` mit und ohne MAR.ELE-Backup, Governance, Content-Validierung, Bildcheck grün). Browser: DE/EN, Desktop und Mobil, hell und dunkel, kein horizontaler Überlauf, alle 10 Aufnahmen laufen, Chip der Montagekarte reagiert. Der Status des Deployments dieses zweiten Commits wird nach dem Push über die GitHub-Actions-Läufe geprüft und im Abschlussbericht an die Auftraggeberin bzw. den Auftraggeber genannt.
