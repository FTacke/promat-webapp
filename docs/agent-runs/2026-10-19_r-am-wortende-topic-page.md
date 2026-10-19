# Themenseite „Das r am Wortende“ (Slug `r-am-silbenende`, 2026-10-19)

## Ziel

Die bestehende Seite `/{de|en}/teaching/spanish/r-am-silbenende` nach dem Blueprint grundlegend umbauen (Titel, Teaser, Dramaturgie, Audio, Impulse, Vertiefung); URL und Slug bleiben.

## Consulted Sources

Blueprint 2026-10-19, `docs/spec/platform-data-files.md`, `docs/runbooks/teaching-corpus-audio.md`, Run-Logs der Seiten *Weiches Spanisch, hartes Deutsch* und *B oder V?*, digitales Lehrbuch (Kapitel Aussprache, Abschnitt R-Laute, Beispiel *reír*: [re.ˈiɾ] gegenüber [ʁe.ˈɪɐ]).

## Neue Struktur (DE/EN gleichwertig)

Kurzer Einstieg (zwei Sätze) → **Hörvergleich *flor*** (W16, einzige aufklappbare Auflösung) → **Wenn das deutsche r zum Vokal wird** (*sehr* [zeːɐ̯], *Vater*/*Lehrer* mit Vater-Schwa [ɐ], Pointe zu *sehr*; spanisch [ɾ] mit Hinweis auf Variation; kleine IPA-Gegenüberstellung) → **Nicht nur am Wortende** (Silbenendposition) mit **Hörvergleich *enfermo*** (W50) → **Zwei r in einem Wort** (*reír*, Verweis auf *Weiches Spanisch, hartes Deutsch*) mit **Hörvergleich *reír*** (W76) → drei Unterrichtsimpulse → Vertiefung (Lehrbuch Aussprache/R-Laute, *Das spanische r*, *Weiches Spanisch, hartes Deutsch*) → Zitation. Entfallen: „Auf einen Blick“, „Hören und entdecken“, Bullet-Liste, Variationsbox, die Karten *cuidar* und *lavar* (samt 8 MP3 und Registereinträgen; repo-weit nur von dieser Seite referenziert). Titel und Verweise auf anderen Seiten (*Das spanische r*) sowie Tests wurden auf den neuen Titel umgestellt. Autorschaft unverändert (Felix Tacke).

## Ausgewählte Aufnahmen (vorläufig, austauschbar über `audio-slots.yaml`)

| Station | Referenz | Lernende:r | Hinweis |
|---|---|---|---|
| *flor* (W16 = `wl_016`) | ES-N-0002 (Spanien) | ES-L-0006 (B1) | vorläufig |
| *enfermo* (W50 = `wl_050`) | ES-N-0004 (Mexiko) | ES-L-0006 (B1) | vorläufig |
| *reír* (W76 = `wl_076`) | ES-N-0005 (Chile) | ES-L-0019 (A2) | Lernendenaufnahme **gesetzt** (unverändert) |

**W76-Lernendenaufnahme:** Die positiv beurteilte Aufnahme war `p3-reir-learner.mp3` (ES-L-0019, A2, L1 Deutsch, `wl_076`). Sie blieb **byte-identisch** erhalten (SHA-256 `bd7e35613ab7265e…`, auch Quelle der Aufnahme auf *Weiches Spanisch, hartes Deutsch*; ein Test sichert Hash und Sprecher). Die Referenz wechselte von ES-N-0001 auf ES-N-0005 (deutliche Schlagphase am Ende), das MAR.ELE-Beispiel `r_l1`/`r_ele` wurde **nicht** zusätzlich eingebunden: Die Lehrbuch-Lernende zeigt akustisch dasselbe Muster (stimmhafter vokalischer Ausklang ohne Zungenschlag), es hätte einen nahezu identischen Vergleich ergeben.

## Teaching-Freigaben (`--release-report`, Stand 2026-10-19)

| Sprecher-ID | Item | Rolle | Verwendung | Einwilligung (Teaching) | `needs_review` | Sprechertyp | Ergebnis |
|---|---|---|---|---|---|---|---|
| ES-N-0005-2026-S01 | wl_076 | reference | p1-reir · integrated | yes | False | native_speaker | OK |
| ES-L-0019-2026-S01 | wl_076 | learner | p1-reir · integrated | yes | False | learner | OK |
| ES-N-0002-2026-S01 | wl_016 | reference | p3-flor · integrated | yes | False | native_speaker | OK |
| ES-L-0006-2026-S01 | wl_016 | learner | p3-flor · integrated | yes | False | learner | OK |
| ES-N-0004-2026-S01 | wl_050 | reference | p3-enfermo · integrated | yes | False | native_speaker | OK |
| ES-L-0006-2026-S01 | wl_050 | learner | p3-enfermo · integrated | yes | False | learner | OK |
| ES-L-0001-2026-S01 | wl_016 | learner | p3-flor-reserve-0001 · reserve (not integrated) | yes | False | learner | OK |
| ES-L-0019-2026-S01 | wl_016 | learner | p3-flor-reserve-0019 · reserve (not integrated) | yes | False | learner | OK |
| ES-L-0019-2026-S01 | wl_050 | learner | p3-enfermo-reserve-0019 · reserve (not integrated) | yes | False | learner | OK |
| ES-L-0004-2026-S01 | wl_050 | learner | p3-enfermo-reserve-0004 · reserve (not integrated) | yes | False | learner | OK |

Die Paarung für *reír* (ES-N-0005 / ES-L-0019, `wl_076`) ist im Gate-Bericht bereits als Verwendung der Seite *Weiches Spanisch, hartes Deutsch* geführt (gleiche Session-Item-Kombination, jeweils `yes`/`False`, OK). Keine Aufnahme aus Ecuador (ES-N-0003 gesperrt), keine Session mit offener Review, ES-L-0014 gesperrt.

## Akustische Kuratierung (Spektrogramm, Energieverlauf; **nicht abgehört**)

- Alle 21 freigegebenen DE-Lernenden und die Referenzstimmen wurden je Item verglichen (Zeit-Frequenz-Darstellung, Dip-Messung im Hüllkurvenverlauf). Kriterium: Referenz mit klar erkennbarer Schlagphase (kurze Unterbrechung mit anschließender Lösung), Lernende mit durchgehendem vokalischem Auslauf bzw. Formantgleiten ohne Unterbrechung.
- *flor*: Referenzstimmen ES-N-0002/0004/0005 zeigen den Zungenschlag, ES-N-0001 deutlich weniger; ES-L-0006 (B1) endet glatt und vokalisch (keine Unterbrechung, weiterlaufende Formanten), ebenso ES-L-0001, ES-L-0019, ES-L-0020. Auswahl ES-N-0002 + ES-L-0006.
- *enfermo*: Referenz ES-N-0004/0005/0002 mit Schlag zwischen *e* und *m*; ES-L-0006 mit langem Formantgleiten vom *e* zum *m* ohne Unterbrechung (ES-L-0019 ähnlich). Auswahl ES-N-0004 + ES-L-0006.
- *reír*: ES-L-0019 mit schwachem hinteren Reibeanlaut und vokalischem Ausklang ohne Dip; ES-N-0005 mit Anlautschlägen und Schlag am Ende.
- Die Auflösung beim ersten Vergleich beschreibt für die Lernendenaufnahme nur „ohne erkennbaren Zungenkontakt, vokalisch ausklingend“; zu *enfermo* und *reír* behauptet die Seite nichts über die konkreten Aufnahmen.

## Vorläufiges / Hörliste für Ana Goás Pérez

1. *flor*: ES-L-0006 (Lernende) und die Referenz ES-N-0002 anhören; Reserven (Register `reserves`): ES-L-0001 (B2), ES-L-0019 (A2).
2. *enfermo*: ES-L-0006 und Referenz ES-N-0004 anhören (Zungenschlag vs. Vokalisierung vor *m*); Reserven: ES-L-0019 (A2), ES-L-0004 (A1).
3. *reír*: Referenz ES-N-0005 (die Lernendenaufnahme ist gesetzt) und die Beschreibung „hinteres [ʁ] am Anfang, Vokalisierung am Ende“ gegenüber der Aufnahme prüfen.
4. Alle Aussagen der Seite zu diesen Aufnahmen stützen sich auf Spektrogramme; eine Hörabnahme steht aus (Wiedergabe im Browser wurde ausgelöst: alle sechs Player starten, die Chips wechseln auf `playing`).
