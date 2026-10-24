# Redaktionelle Harmonisierung der spanischen Themenseiten

Datum: 2026-10-24

## Ziel

Gezielte redaktionelle Vereinheitlichung der sieben bestehenden spanischen Themenseiten (DE/EN): Teaser, Titel, Beobachtungsfragen bzw. erläuternde Sätze der Hörkarten, Adressierung an Lehrkräfte, Entdoppelung. Keine inhaltliche Generalüberholung, keine Audioänderung.

Hinweis zum Auftrag: Im Auftrag stehen die Slugs `europa-sounds-different`, `r` und `r-am-silbenende`; die tatsächlichen Slugs im Repository sind `europe-sounds-different`, `r` und `r-am-silbenende`. URLs bleiben unverändert. Die achte Seite `accent-changes-everything` gehörte nicht zum Auftrag und wurde nicht angefasst (ihre Hörfragen sind bereits sachlich formuliert).

## Geändert

**Teaser (`summary` und gleichlautende `description`)**

| Seite | DE | EN |
|---|---|---|
| Europa klingt auf Spanisch anders | Wie vertraute Schreibungen und Lautmuster die spanische Aussprache beeinflussen. | How familiar spellings and sound patterns influence pronunciation in Spanish. |
| Das spanische r | Zwei spanische r-Laute – und warum das deutsche r anders klingt. | Two Spanish r sounds – and why the German r sounds different. |
| Das r am Wortende | Warum das deutsche r häufig zum Vokal wird, das spanische aber konsonantisch bleibt. | Why the German r often turns into a vowel while the Spanish r stays consonantal. |

Titel unverändert; daher bleiben Seitentitel und die aus dem Titel erzeugte Zitation gleich. Die Beschreibung (`description`) wurde mit dem Teaser angeglichen und erscheint in den Seitenmetadaten.

**Hörkarten** (Kartentitel durchgehend `Hörvergleich: …` / `Listening comparison: …`)

- *Welche Aussprache unterrichten?*: Titel `casa – caza` und `gracias – ciudad – paz – ración` statt „Mit und ohne Unterscheidung“ bzw. „Anders, aber genauso korrekt“. Erste Karte: Frage „Wie werden die beiden Wörter in den Aufnahmen ausgesprochen?“; zweite Karte: erläuternder Satz (Typ B). Einleitungstext: die vorweggenommene Frage „Wie klingt der Unterschied?“ entfernt (Doppelung mit der Kartenfrage). Regionaler Audioblock: Lead nur noch „Die Beispiele stammen aus verschiedenen hispanoamerikanischen Varietäten.“ (die Aussage zur Normalität des *seseo* steht bereits im Text davor). Die Aussagen zu *seseo*, *distinción* und Variation sind vollständig erhalten.
- *Europa klingt auf Spanisch anders*: *Europa* „Wie klingt die Buchstabenfolge *eu* in den beiden Aufnahmen?“; *deuda* „Wie wird die Vokalverbindung *eu* in *deuda* ausgesprochen?“. *mismo – álbum*, *sueño*, *viuda* unverändert.
- *B oder V?*: Karte 1 „Was fällt bei den Anlauten von *bienes* und *vienes* auf?“; Karte 2 „Unterscheidet sich der Anlaut der beiden Wörter in den Aufnahmen?“; Karte 3 trug den Titel „Hörvergleich: *vienes*“, während Chip und Audio *bienes – vienes* enthalten (Korpusitem W92 enthält beide Wörter, laut Freigabebericht „bienes – vienes“). Maßgeblich ist das hörbare Audio, deshalb wurde der Titel auf `bienes – vienes` angeglichen (Chip und Audioquelle unverändert). Karte 1 und 3 haben damit denselben Titel; sie unterscheiden sich durch Sprecher:innen und Frage.
- *b, d und g*: *el bebedor* von der Frage zur erklärenden Form: „Die Wortfolge zeigt drei approximantische Realisierungen: [β] nach /l/ und zwischen Vokalen sowie [ð] zwischen Vokalen.“ Der Text nach der Karte listet die drei Positionen nicht mehr auf; der Einleitungstext vor der Karte wurde gekürzt, damit er die Karte nicht wiederholt. Zwischenüberschrift und Infokasten unverändert. *vida*, *lavar*, *con agua* unverändert.
- *Das spanische r*: „Achte auf …“ ersetzt: *caro* „Wie klingt das einfache *r* bei den beiden Referenzsprecher:innen?“, *carro* „… mehrfache *r* …“, *reloj* „Wie unterscheidet sich das *r* am Wortanfang in den beiden Aufnahmen?“, *reír* „Wie klingt das *r* am Wortanfang in den beiden Aufnahmen?“ (der Transfergedanke steht im Text davor; der Querverweis auf *Das r am Wortende* ist erhalten). *pero – perro* unverändert. Referenz-Referenz-Vergleiche bleiben Referenz-Referenz.
- *Das r am Wortende*: *flor* „Wie klingt das *r* am Wortende in den beiden Aufnahmen?“, *lavar* „Wie wird das auslautende *r* in den beiden Aufnahmen realisiert?“, *enfermo* „Wie klingt das *r* vor *m* in den beiden Aufnahmen?“, *reír* „Wie klingen das *r* am Wortanfang und das *r* am Wortende in den beiden Aufnahmen?“. Hinweis: Der Auftrag nennt für die zweite Frage das Wort *llevar*; auf der Seite steht an dieser Stelle *lavar* (Item W9), die Frage wurde dort eingesetzt.

Die EN-Fassungen sind idiomatisch formuliert (z. B. „How does the tapped *r* sound for the two reference speakers?“, „What stands out about the initial sounds of *bienes* and *vienes*?“), mit gleicher Funktion und gleichen Audioquellen.

**`audio-slots.yaml`**: Die dort geführten `question`-Texte werden vom Check wörtlich auf der Seite erwartet und wurden deshalb mit angepasst (12 Fragen). Für *el bebedor* entfällt `question`, weil die Karte nun einen erläuternden Satz trägt (Frage ist laut Skript optional). Keine Änderung an Sprecher:innen, Items, Dateien, Schnitten oder Hashes.

## Bewusst unverändert

- *Weiches Spanisch, hartes Deutsch*: gesamte Seite unverändert (Referenzseite, Fragen funktionieren).
- Titel und Teaser von *Welche Aussprache unterrichten?*, *Weiches Spanisch, hartes Deutsch*, *B oder V?*, *b, d und g*.
- *mismo – álbum* (MAR.ELE-Montage) mit Kennzeichnung und Provenienz.
- Regionale Untertitel mit Kurzhinweis (`note`) auf den *casa – caza*-Karten von *Welche Aussprache unterrichten?*: Sie benennen die Varietät und nehmen das Ergebnis teilweise vorweg; das gehört zur regionalen Gegenüberstellung dieser Seite und wurde nicht angetastet (offener redaktioneller Punkt, falls diese Hinweise künftig entfallen sollen).
- Alle Wortfolge-Chips, Audioquellen, Freigaben, Bilder und Bildnachweise, Autorenschaft, URLs.

## Blueprint

Der Blueprint `Pronunciation_Matters_Blueprint_Themenseiten_2026-10-19.md` liegt nicht im Repository (nur lokal, `Downloads`); dort wurde Abschnitt 4 „Regeln für Hörvergleichskarten“ neu gefasst und die Abnahme-Checkliste angepasst (Kopie der vorherigen Fassung nur lokal im Temp-Verzeichnis). Neue Regeln: eine Karte trägt entweder eine offene Beobachtungsfrage (entdeckend) oder einen kurzen erläuternden Satz (veranschaulichend), keine obligatorische Frage; keine Imperative und Schülerarbeitsaufträge; neutrale Kartentitel; Chips bleiben und müssen zum Audio passen; keine künstlichen Unterschiede zwischen gleichwertigen Referenzaufnahmen; keine Wiederholung zwischen Karte, Auflösung und Erklärung; Teaser-Regel. Das verbindliche Kernprinzip steht außerdem in `docs/spec/platform-data-files.md` (Teaching, Listening cards); Runbook `docs/runbooks/teaching-corpus-audio.md` unterscheidet Karten mit und ohne `question`.

## Tests und Prüfung

- Tests angepasst (Fragen, Titel, Teaser) und ergänzt: `test_listening_cards_follow_the_shared_editorial_standard` (neutrale Titel = Chip-Wörter, keine Imperative, kein Ergebnis im Titel; **keine** Pflicht, dass jede Karte eine Frage hat), `test_listening_cards_have_identical_function_and_audio_in_both_languages` (Parität DE/EN: gleiche Chips, gleiche Audiodateien, Frage/Erklärung auf beiden Seiten), `test_spanish_topic_teasers_are_single_sentences_that_do_not_repeat_the_title`.
- `scripts/teaching_audio_slots.py --check` (auch mit MAR.ELE-Backup), `--release-report` ohne Sperre; Audio-Hashes unverändert (Check grün, nur Textfelder geändert).
- Browser (Chromium, lokal :8011): alle sieben Seiten in DE und EN, Desktop 1366 px (hell) und Mobil 390 px (dunkel): kein horizontaler Überlauf, keine HTTP-Fehler, alle Audioelemente laufen, Kartentitel/Leads/Chips wie festgelegt.

## Commit und Deployment

Volltest vor dem Commit: 1497 passed, 2 skipped; Governance-, Content- und Slot-Checks grün, Freigabebericht ohne Sperre. Push auf `main` löst CI und „Deploy production“ aus; deren Ergebnis wird nach dem Push über die GitHub-Actions-Läufe geprüft und im Abschlussbericht an die Auftraggeberin bzw. den Auftraggeber genannt.
