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
