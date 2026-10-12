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
