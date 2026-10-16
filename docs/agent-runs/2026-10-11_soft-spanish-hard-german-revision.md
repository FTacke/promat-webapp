# Themenseite „Weiches Spanisch, hartes Deutsch“ überarbeitet

Datum: 2026-10-11

## Ziel

Die Seite `/{de|en}/teaching/spanish/soft-spanish-hard-german` nach dem Konzept „Weniger erklären, früher hören“ neu aufbauen: kurzer Einstieg, *o hay* (MAR.ELE), Erklärung des Knacklauts, *tiene hambre* (D27), *sus amigos* (D24, Resilbifizierung), Unterrichtsimpuls, Vertiefung.

## Consulted Sources

- `docs/spec/platform-data-files.md` (Teaching-Medien, Korpusaufnahmen), `docs/runbooks/teaching-corpus-audio.md`, `docs/agent-runs/2026-10-10_six-spanish-topic-pages.md`
- `linguistik.hispanistica/docs/aussprache.md` (Quelltext der MAR.ELE-Beispiele), lokale Runtime (Items `d_24`, `d_27`)

## Entscheidungen

- **MAR.ELE-Zuordnung** (Quelltext des Lehrbuchs, Abschnitt „Vokale am Wortanfang“): `glottis_l1.mp3` = Zielaussprache `[o.ˈai]` → Referenz; `glottis_ele.mp3` = Lernendenaussprache `[ʔo.ʔai]` → Lernende. Gegenprobe an den Audios (RMS-Hüllkurve): `l1` 0,42 s Sprache ohne Einbruch, `ele` 0,60 s mit deutlichem Einbruch nach dem *o*. Beide enthalten nur *o hay* (kein Satz). Kopie unverändert nach `media/audio/marele/o-hay-{ref,learner}.mp3`.
- **Herkunft** im Slot-Register über `origin` statt Session/Item; auf der Seite als Text `MAR.ELE` an beiden Karten, **ohne Link** und nicht im Seitenuntertitel (die MAR.ELE-Seite wird abgeschaltet).
- **Austauschbarkeit**: Karten nennen nur Kategorie und Quelle (`Pronunciation Matters · D27`), keine Region, kein Niveau, keine Session; Hörfragen neutral („Wie schließt *hambre* an *tiene* an?“); Auflösungen behaupten keine Realisierung einer konkreten Lernendenaufnahme.
- **D24** lautet „Con su familia es un ángel y con sus amigos un diablo.“; hervorgehoben ist *sus amigos*.
- Entfallen: „Auf einen Blick“, Infobox „Was dieser Vergleich nicht behauptet“, vier Zusatzvergleiche (*se oye*, *la euforia*, *puedo oír*, *que obtiene*; 8 MP3 samt Registereinträgen).
- Vertiefung verlinkt `…/aussprache/#laute-des-spanischen-herausforderungen` (Anker im Live-Lehrbuch vorhanden) und behält den Querverweis auf *Welche Aussprache unterrichten?*.
- Auflösung: bestehender `solution`-Block, Zusammenfassung `Auflösung: Was ist zu hören?` / `Solution: What can be heard?`.
- Gemeinsame CSS-Korrektur (`30_components.css`): Absätze desselben Textblocks hatten 0 px Abstand (jeder Absatz ist ein eigenes `pm-teaching-copy-block`); neue Regel `.pm-teaching-copy-block + .pm-teaching-copy-block` mit `--pm-reading-paragraph-gap`. Wirkt auf alle Themenseiten mit mehrabsätzigen Textblöcken.
- Nicht-trennbare Bindestriche in *su‑sa‑mi‑gos* (kein Umbruch mitten in der Silbenfolge).

## Geänderte Bereiche

`content/teaching/spanish/soft-spanish-hard-german/{de,en}.yaml`, `…/media/audio/{marele,corpus}/`, `content/teaching/spanish/audio-slots.yaml`, `scripts/teaching_audio_slots.py` (externe Aufnahmen), `app/static/css/30_components.css`, `app/tests/test_teaching_spanish_topics.py`, Spezifikation, Runbook.

## Aufnahmen

- *o hay*: MAR.ELE `glottis_l1` (Referenz), `glottis_ele` (Lernende).
- *tiene hambre*: `d_27`, Referenz `ES-N-0004-2026-S01`, Lernende `ES-L-0007-2026-S01` (unverändert).
- *sus amigos*: `d_24`, Referenz `ES-N-0004-2026-S01`, Lernende `ES-L-0007-2026-S01` (neu, automatisch gewählt, nicht phonetisch geprüft).

## Offen für die manuelle Kuratierung

Beste Referenz-/Lernendenaufnahme für D27 und D24 (Austausch: `audio-slots.yaml`, `--export`); anschließend prüfen, ob die neutralen Auflösungen konkretisiert werden können. Klären, ob die MAR.ELE-Aufnahmen (öffentlich im Lehrbuch unter CC BY-SA) weiterhin so geführt werden, sobald MAR.ELE abgeschaltet ist.

## Verifikation

Siehe Abschlussbericht im Chat; Browser-Pass in `tmp/ui-qa/2026-10-11-soft-spanish/` (DE/EN × 1280/390 px × hell/dunkel, keine Konsolenfehler, keine 4xx, kein Überlauf, Auflösungen öffnen/schließen; Regressionscheck der übrigen sechs Themenseiten).

## Nachtrag: Feinschliff der Hörvergleichskästen

- Alle drei `audio_contrast`-Blöcke tragen jetzt einen Titel (damit Audio-Icon und Titelhierarchie wie im Vergleichsmodul von *Welche Aussprache unterrichten?*): `Mit und ohne Knacklaut: *o hay*`, `Ohne zusätzlichen Neueinsatz: *tiene hambre*`, `Resilbifizierung: *sus amigos*` (EN gleichwertig). Keine neue Komponente, kein CSS.
- Abschnittsüberschriften entdoppelt (`Hören und entdecken`, `Noch ein Beispiel: *tiene hambre*`, `Wenn Silben die Wortgrenze überschreiten`); Hörfragen kurz und neutral (Registerfeld `question` in `audio-slots.yaml` angepasst, Aufnahmen und Sprecherzuordnung unverändert).
- Zielwortfolge in den Satz-Chips (D27, D24) fett-kursiv hervorgehoben; Auflösung zu *sus amigos* um die Doppeldefinition gekürzt.

## Nachtrag: Unterrichtsimpulse vereinheitlicht

- Alle sechs neuen spanischen Themenseiten (DE/EN) nutzen für den Unterrichtsteil den bestehenden Block `teaching_impulses` unter der Überschrift `Impulse für den Unterricht` / `Classroom prompts` (wie *Welche Aussprache unterrichten?*, unverändert); die bisherigen `tip_box`-Kurzaufgaben und die zweite Überschrift `Für den Unterricht` entfielen. Kein CSS, keine neue Komponente.
- Bestehende Aufgaben wurden 1:1 in nummerierte Impulse übertragen (nur kurze Impulstitel ergänzt; Leitfrage von *R am Silbenende* im zweiten Impuls, Kontrollhinweis von *Weiche Konsonanten* als vierter Impuls).
- *Weiches Spanisch, hartes Deutsch*: drei neue Impulse (Erst hören, dann erklären / Aussprache bewusst erproben / Sprachen vergleichen) mit kurzem Einleitungssatz; der Sammelsatz zu den drei Hörbeispielen entfiel. Der Sprachvergleich bleibt bewusst offen formuliert.

## Nachtrag: Glottis-Illustration

- `glottis.png` (Repository-Root, unverändert übernommen, 1448 × 1086, 1,8 MB) liegt jetzt unter `content/teaching/spanish/soft-spanish-hard-german/media/images/glottal-stop-larynx-hand.png`; die Arbeitskopie im Root ist entfernt. Eine Datei für DE und EN.
- Eingebunden mit dem vorhandenen `image`-Block hinter dem Abschnitt „Warum klingt das unterschiedlich?“ (vor „Noch ein Beispiel“). Der Block wurde zentral um das optionale Feld `credit` (Bildnachweis) erweitert und ruhiger gestaltet (zentriert, max. 30 rem, kein Rahmen/Schatten; im Dark Mode abgerundete, leicht abgedunkelte Platte). Der Block war bisher auf keiner Seite im Einsatz.
- Der Nachweis steht im Feld `credit` der Themenquelle; die Architektur hat keinen Medienmetadaten-Speicher, die PNG-Datei selbst wurde nicht verändert.
- Offen: Die Datei ist mit 1,8 MB groß (lazy geladen). Eine verlustfreie bzw. WebP-Variante wäre möglich, wurde wegen „genau diese Datei“ nicht gemacht.

## Nachtrag: WebP-Derivat der Illustration

- Bestandsaufnahme: im Teaching-Bereich gibt es genau eine Rasterillustration (`glottal-stop-larynx-hand.png`, 1,8 MB, auf 480 px dargestellt); die zwei SVGs der Seite *Welche Aussprache unterrichten?* sind Vektoren (und nicht referenziert), `promat.png`, Favicon und Landing-Karten gehören nicht zum Teaching-Bereich.
- Derivat: `glottal-stop-larynx-hand.webp`, 960 × 720 px (2 × 480), Qualität 92 nach Vergleich der Stufen 70–95 (PSNR 44,5 dB; bei 2-facher Vergrößerung an Haaren, Handlinien und Lavendelverläufen nicht vom Master zu unterscheiden; Farbstich < 0,3/255). Master unverändert (SHA-256 `46b2d048…062a6`).
- Auslieferung über den gemeinsamen Block `image` (`<picture>`, Master als Fallback, `width`/`height`, lazy); Route liefert `.webp` mit festem Mimetype. Deklaration `content/teaching/image-derivatives.yaml`, Werkzeug `scripts/teaching_images.py`, Runbook `docs/runbooks/teaching-illustrations.md`.

## Nachtrag: einheitliche Sprecherbezeichnungen im Teaching-Bereich

- Zentral: i18n-Schlüssel `teaching.speaker.reference` (`Referenzsprecher:in` / `Reference speaker`) und `teaching.speaker.learner` (`Lernende:r` / `Learner`); Audiobeispiele in den Themenquellen nennen nur noch `role: reference|learner` (optional `level: B1`), die Beschriftung entsteht in `teaching_content._speaker_role_label`. Ein explizites `label` hat weiterhin Vorrang (Varietäten wie *Distinción*/*Seseo*).
- Alle sieben spanischen Seiten (DE/EN) umgestellt; die Einleitungssätze der Korpusvergleiche sprechen von „einer Referenzsprecher:in und einer lernenden Person“ / „a reference speaker and a learner“. Niveauangaben (A2/B1) und Regions-/L1-Untertitel blieben unverändert.
- Unverändert: Korpusdaten, Sprecher-IDs, interne Kategorien (`reference`/`learner`, `speaker_type`), Audio-Slots, Research-Oberfläche (dort bleibt z. B. `Native speakers` als Forschungskategorie), Projektseiten.

## Nachtrag: redaktionelle Endfassung (2026-10-12)

- Seitenanfang: neuer Orientierungstext; Zwischenüberschrift „Hören und entdecken“ und der Satz zu den beiden Aufnahmen entfielen, der erste Hörvergleich (*o hay*, Kastentitel `Hörvergleich: *o hay*`) folgt direkt.
- Abschnitte: `Wie entsteht der Knacklaut?` (ein Absatz, Illustration mit verkürzter Bildunterschrift) → `Wo können Knacklaute bei Lernenden auftreten?` (Transferkontexte, *reír* nur als Textbeispiel) → Hörvergleich *tiene hambre* → `Wenn Wortgrenzen verschwimmen` (Resilbifizierung als reguläres spanisches Muster, Lernende „mitunter“ stärker an Wortgrenzen orientiert) → Hörvergleich *sus amigos* → Impulse (unverändert).
- Nur *o hay* behält die aufklappbare Auflösung (neuer Text mit beiden IPA-Transkriptionen, ohne separate Transkriptionszeile); die Auflösungen zu D27 und D24 entfielen. Wortfolge-Chips bleiben in allen drei Kästen (im Browser geprüft: idle → playing → paused).
- Abweichung vom Wortlaut: In der Auflösung steht „der Referenzsprecher:in“ / „der lernenden Person“ statt „des Referenzsprechers“ / „des Lernenden“ (kein Geschlecht der Sprecher:innen belegt; einheitlich mit den Bezeichnungen der Hörkästen).
- Hörfragen von D27 und D24 im Register `audio-slots.yaml` nachgezogen (`question`); Aufnahmen und Slots unverändert.

## Nachtrag: finale Audio-Kuratierung, Freigaben, Mitautorschaft (2026-10-16)

### Freigabeprüfung (verbindliches Gate, `teaching_audio_slots.py --release-report`, Stand 2026-10-16, Runtime-Metadaten)

| Sprecher-ID | Item | Rolle | Verwendung | `teaching_consent_signed` | `needs_review` | Sprechertyp | Ergebnis |
|---|---|---|---|---|---|---|---|
| ES-N-0004-2026-S01 | d_27 | reference | p1-hambre · integrated | yes | False | native_speaker | OK |
| ES-L-0006-2026-S01 | d_27 | learner | p1-hambre · integrated | yes | False | learner | OK |
| ES-N-0005-2026-S01 | wl_076 | reference | p1-reir · integrated | yes | False | native_speaker | OK |
| ES-L-0019-2026-S01 | wl_076 | learner | p1-reir · integrated | yes | False | learner | OK |
| ES-N-0002-2026-S01 | qy_05 | reference | p1-losotros · integrated | yes | False | native_speaker | OK |
| ES-L-0007-2026-S01 | qy_05 | learner | p1-losotros · integrated | yes | False | learner | OK |
| ES-N-0004-2026-S01 | d_24 | reference | p1-amigos · reserve (not integrated) | yes | False | native_speaker | OK |
| ES-L-0001-2026-S01 | d_24 | learner | p1-amigos · reserve (not integrated) | yes | False | learner | OK |
| ES-L-0014-2026-S01 | – | learner | ausgeschlossen (`EXCLUDED_SESSIONS`) | no | False | learner | BLOCKED: keine Teaching-Freigabe nachweisbar, nicht verwendet |

Geprüft wurde jeweils die `metadata.json` der Session (Flags, Sprechertyp), das Vorhandensein der Item-MP3 und der Alignment-Eintrag des Items samt Zielwortfolge (`tiene hambre`, `reír`, `los otros`, `sus amigos`). Eine aufnahmespezifische Einschränkung existiert im Datenmodell nicht (die Flags gelten je Session); Freigaben aus früheren Berichten wurden nicht übernommen. ES-L-0014 bleibt ausgeschlossen, ebenso ES-N-0003 und ES-L-0023 (`EXCLUDED_SESSIONS`).

### Kanonische Items

D27 = `d_27` („Cuando el chico tiene hambre, pierde el control.“), Wortliste 76 = `wl_076` („reír“), QY5 = `qy_05` („¿Tampoco los otros quieren venir?“), D24 = `d_24` (nur noch Reserve).

### Audioausschnitte (Cut-outs; Korpusaufnahmen unverändert)

| Ziel | Quelle | Schnitt auf der Item-MP3 | Vorlaufstille | Fades ein/aus | SHA-256 Quelle → Derivat |
|---|---|---|---|---|---|
| tiene hambre | ES-N-0004-2026-S01 / d_27 | 968–1672 ms (Länge 704 ms) | 35 ms | 10 / 20 ms | `300dbc98bde4…` → `02a5527c2cc1…` |
| tiene hambre | ES-L-0006-2026-S01 / d_27 | 1612–2650 ms (Länge 1038 ms) | 0 ms | 10 / 25 ms | `45bf91eb05fb…` → `5a5fb08e1383…` |
| los otros | ES-N-0002-2026-S01 / qy_05 | 698–1249 ms (Länge 551 ms) | 40 ms | 10 / 20 ms | `95175d97e1ed…` → `37ccb37cf39f…` |
| los otros | ES-L-0007-2026-S01 / qy_05 | 740–1440 ms (Länge 700 ms) | 40 ms | 10 / 20 ms | `68cbbcdb5819…` → `640bcd62abbb…` |

Schnittpunkte nach Spektrogramm und Energieverlauf der tatsächlichen Realisierung festgelegt, nicht nach den Alignment-Wortzeiten (diese lagen z. B. bei *chico | tiene* in ES-N-0004 um ca. 60 ms im vorangehenden Vokal). Der Beginn liegt in der Verschlussphase des /t/ bzw. am Übergang zum /l/ (Alignment-Grenze ca. 8–20 ms vorgezogen, damit der Anlaut vollständig ist); das Ende liegt hinter dem Auslaut des letzten Worts (Stille bzw. Frikativende) mit kurzem Fade. Zwischen den Wörtern wurde nichts eingefügt oder verändert. Vorlaufstille nur am Clip-Anfang, damit der Einsatz nicht abrupt wirkt (bei den Lernendenaufnahmen von *tiene hambre* liegt der natürliche Verschluss von ca. 60 ms vor). ffmpeg 8.1, MP3 160 kbit/s mono 48 kHz wie die Quelle; die Ableitung ist bitgleich reproduzierbar (Test). *reír* (ES-N-0005, ES-L-0019, `wl_076`) ist bereits isoliert und wird unverändert kopiert. Die Schnitte wurden akustisch (Spektrogramm) geprüft, nicht abgehört: eine Hörkontrolle durch Ana Goás Pérez bleibt sinnvoll.

### Weitere Änderungen

- Seite: vier Hörvergleiche (*o hay*, *tiene hambre*, *reír*, *los otros*), Einleitung „Vier Hörvergleiche“, Resilbifizierungstext mit *sus amigos* und *los otros*; *sus amigos* (D24) ohne Audiokasten, die Medien (`p1-amigos-*`) entfielen; Reserve ES-N-0004 / ES-L-0001 in `audio-slots.yaml` unter `reserves` dokumentiert (kein Medium, Freigabe nach Gate geprüft).
- Chips zeigen jetzt exakt die gespielte Passage (*o hay*, *tiene hambre*, *reír*, *los otros*).
- Autorschaft: `metadata.creators: [felix-tacke, ana-goas-perez]` in DE und EN (Registry-Person vorhanden); sichtbare Zeile „Felix Tacke, Ana Goás Pérez“ (gemeinsame Konvention: Namen mit Komma), generierte Zitation „Tacke, Felix & Goás Pérez, Ana (2026)“, JSON-LD mit beiden Autor:innen; Herausgeber der Plattform und Bildnachweis unverändert bei Felix Tacke; andere Seiten unverändert.
- Spanische Teaching-Übersicht: neues optionales Hub-Feld `overview_note` (zweite, leisere Zeile im Orientierungsbereich) mit dem A1-Grundsatz „Aussprache von Anfang an“ / „Pronunciation from the start“; nur dort, nicht auf Themenseiten.
