# Themenseite „Das spanische r“ (`/de|en/teaching/spanish/r`) neu aufgebaut

Datum: 2026-10-24

## Ziel

Die weitgehend automatisiert entstandene Seite wurde nach dem Blueprint vom 2026-10-19 und dem Qualitätsstandard der drei überarbeiteten Seiten (*Weiches Spanisch, hartes Deutsch*, *Das r am Wortende*, *b, d und g*) vollständig neu strukturiert (DE/EN). Slug, URLs und Autorenschaft (Felix Tacke allein) bleiben unverändert. Die Artikulationsgrafik wurde nachträglich integriert (siehe unten).

## Consulted Sources

- Blueprint `Pronunciation_Matters_Blueprint_Themenseiten_2026-10-19.md`, `docs/spec/platform-data-files.md` (Teaching, Corpus recordings), `docs/runbooks/teaching-corpus-audio.md`, Run-Logs der drei Referenzseiten und von *B oder V?*
- Digitales Lehrbuch: *Aussprache* (`#anders-artikulierte-laute-die-r-laute`, inkl. *claro*-Übung und „Regionale Diversität“), *Herkunftssprachen* (`#gerolltes-r-normal-in-allen-herkunftssprachen`), *Orthographie* (`#se-escribe-casi-como-se-habla`). **Befund:** Das Orthographie-Kapitel behandelt `r`/`rr` nicht ausdrücklich; es ist nur für das allgemeine Buchstaben-Laut-Verhältnis verlinkt. Die Aussage „die Orthographie spiegelt nur den relevanten Unterschied im Wort wider“ steht im Aussprache-Kapitel.
- Lokale Runtime `data/sessions/spanish` (Metadaten, Alignment, Item-MP3), `scripts/teaching_audio_slots.py`.

## Neue redaktionelle Struktur

Kurzer Einstieg (drei Sätze, ohne „Auf einen Blick“ und ohne „Hören und entdecken“) → **Hörvergleich *pero – perro*** (einzige Auflösung, zugeklappt) → *Zwei r-Laute – und die Schrift hilft mit* (Mechanismus, ⟨r⟩/⟨rr⟩, Wortanfang; Platz der Grafik) → *Einfach und mehrfach – auch bei anderen Wörtern* (**caro**, **carro**) → *Wenn das deutsche r ins Spanische übertragen wird* (uvulares [ʁ], regionale vordere r im Deutschen; **reloj**; kurzer Text mit internem Link zu *Das r am Wortende*; **reír**) → *Nicht jedes r klingt gleich* (ohne konkrete Varianten, Verweis aufs Lehrbuch) → Infokasten *Herkunftssprachen als Ressource* → *Impulse für den Unterricht* (drei: Erst den Unterschied hören · Die Artikulationsstelle bewusst machen · Die Schreibung als Hilfe nutzen) → *Vertiefung* (Aussprache, Orthographie, Herkunftssprachen, *Das r am Wortende*; *Weiches Spanisch, hartes Deutsch* bewusst nicht verlinkt, kein eigener Erkenntniswert) → generierte Zitation. Entfallen: Übersicht, alle Lernenden-Vergleiche zu *caro/carro* und *pero/perro*, der Satz D1, die Stellungsbedingungen-Passage (nach /n/, /l/, /s/, Silbenende), die frühere Variationsbox mit konkreten Regionen.

Teaser (verbindlich): „Warum das spanische r nicht wie das deutsche klingt – und wie man [ɾ] und [r] im Unterricht unterscheiden kann.“ EN: „Why the Spanish r does not sound like the German one – and how to tell [ɾ] and [r] apart in the classroom.“

## Audioarchitektur (fünf Hörkästen, 10 Aufnahmen)

| Nr. | Item | Referenz | Lernende:r | Slot-IDs (`audio-slots.yaml`) |
|---|---|---|---|---|
| 1 | W90 `wl_090` *pero – perro* | ES-N-0002 (Spanien) + ES-N-0005 (Chile) | – | `p2-pero` (`ref_a`, `ref_b`) |
| 2 | W85 `wl_085` *caro* | ES-N-0002 + ES-N-0005 | – | `p2-caro` |
| 3 | W57 `wl_057` *carro* | ES-N-0002 + ES-N-0005 (dieselben) | – | `p2-carro` |
| 4 | W2 `wl_002` *reloj* | ES-N-0005 (Chile) | ES-L-0011 (B1, L1 Deutsch) | `p2-reloj` |
| 5 | W76 `wl_076` *reír* | ES-N-0005 (Chile) | ES-L-0019 (A2, L1 Deutsch) | `p2-reir` |

Alle Aufnahmen sind unveränderte Item-MP3 (kein Zuschnitt). Karten 1–3 nennen beide Stimmen `Referenzsprecher:in` / `Reference speaker` (kein Lernenden-Label bei Referenz-Referenz-Paaren); die Untertitel nennen Region und Item (*Spanien · W90*, *Chile · W90*). Lernenden-Labels tragen kein Niveau (wie auf den Schwesterseiten).

**W76 – Bestätigung:** `p2-reir` verwendet exakt dieselbe Session-Item-Kombination wie `p3-reir` (*Das r am Wortende*) und `p1-reir` (*Weiches Spanisch, hartes Deutsch*): Lernende ES-L-0019 `wl_076`, SHA-256 `bd7e35613ab7265e…`, Referenz ES-N-0005 `wl_076`, SHA-256 `d6a4e69ad6fd7cf9…`. Alle drei Seiten tragen byte-identische Dateien (SHA-256 verglichen); es entstand keine neue Datei und kein neuer Lernender wurde gewählt. Ein Test (`test_spanish_r_curation_is_released_traceable_and_reuses_the_reir_recording`) sichert das ab.

## Teaching-Freigaben (`--release-report`)

| session | item | role | use | consent | review | speaker_type | item_text | result |
|---|---|---|---|---|---|---|---|---|
| ES-N-0002-2026-S01 | wl_090 | reference | p2-pero · integrated | yes | False | native_speaker | pero – perro | OK |
| ES-N-0005-2026-S01 | wl_090 | reference | p2-pero · integrated | yes | False | native_speaker | pero – perro | OK |
| ES-N-0002-2026-S01 | wl_085 | reference | p2-caro · integrated | yes | False | native_speaker | caro | OK |
| ES-N-0005-2026-S01 | wl_085 | reference | p2-caro · integrated | yes | False | native_speaker | caro | OK |
| ES-N-0002-2026-S01 | wl_057 | reference | p2-carro · integrated | yes | False | native_speaker | carro | OK |
| ES-N-0005-2026-S01 | wl_057 | reference | p2-carro · integrated | yes | False | native_speaker | carro | OK |
| ES-N-0005-2026-S01 | wl_002 | reference | p2-reloj · integrated | yes | False | native_speaker | reloj | OK |
| ES-L-0011-2026-S01 | wl_002 | learner | p2-reloj · integrated | yes | False | learner | reloj | OK |
| ES-N-0005-2026-S01 | wl_076 | reference | p1-reir / p2-reir · integrated | yes | False | native_speaker | reír | OK |
| ES-L-0019-2026-S01 | wl_076 | learner | p1-reir / p2-reir · integrated | yes | False | learner | reír | OK |
| ES-L-0019-2026-S01 | wl_002 | learner | p2-reloj-reserve-0019 · reserve | yes | False | learner | reloj | OK |
| ES-L-0021-2026-S01 | wl_002 | learner | p2-reloj-reserve-0021 · reserve | yes | False | learner | reloj | OK |
| ES-L-0005-2026-S01 | wl_002 | learner | p2-reloj-reserve-0005 · reserve | yes | False | learner | reloj | OK |

Kein Eintrag aus `EXCLUDED_SESSIONS` ist verwendet (ES-N-0003 ohne Einwilligung bleibt gesperrt). `--check`: `slots OK`.

## Akustische Kuration – **vorläufig, nicht abgehört**

In dieser Umgebung ist kein Abhören möglich. Die Auswahl beruht auf einer Signalprüfung (Intensitätsverlauf, Wellenform, Spektrogramm) und ist **vorläufig**; die Seite behauptet keine konkrete Abweichung einer Lernendenaufnahme.

- **Referenzen *pero – perro*, *caro*, *carro*:** Für alle vier freigegebenen Referenzstimmen wurden Zungenkontakte gezählt (Einbrüche > 8 dB im 80–1500-Hz-Verlauf). *caro*: bei allen genau ein deutlicher Schlag; *carro*: 3–4 Kontakte; *pero – perro*: ES-N-0002 und ES-N-0005 haben je einen sauberen Schlag in *pero* und 4 Kontakte in *perro*, ES-N-0001 ebenfalls, bei ES-N-0004 (Mexiko) fehlt in *pero* ein deutlicher Schlag. Darum **ES-N-0002 (Spanien) + ES-N-0005 (Chile)** für die drei Paarkarten: zwei Varietäten, gleiche Konstellation für *caro* und *carro*, Wörter vollständig, keine abgeschnittenen Ränder.
- **Referenz *reloj*:** Am anlautenden r zeigt ES-N-0005 am deutlichsten mehrere kurze Kontakte vor dem Vokal (Wellenform/Spektrogramm, visuell beurteilt); ES-N-0002/0004/0001 sind dort weniger eindeutig (leise, verhauchte oder glatte Anlaute). Darum ES-N-0005 (Chile, zugleich die etablierte Referenz von *reír*).
- **Lernende *reloj*:** Gesucht wurde ein Anlaut ohne Zungenverschluss und mit Reibung. ES-L-0011 hat keinen Einbruch im Anlaut, nur kurzes Rauschen vor dem Vokal (Rauschanteil 2,5–8 kHz 0,23; bei den übrigen verschlusslosen Kandidaten ≤ 0,02). Das ist das erwartbare Muster eines hinteren Reibelauts, **aber nicht als „uvular“ bestätigt**. Die Hörfrage („Wo wird das *r* artikuliert?“) und der Text bleiben deshalb allgemein; die alte, automatisch gewählte Lernendenaufnahme (ES-L-0012) wurde ersetzt.
- **Reserven (nicht integriert, im Gate geprüft):** ES-L-0019 (dieselbe Person wie bei *reír*, deren hinterer Anlaut dort positiv bewertet wurde), ES-L-0021, ES-L-0005 (alle drei mit hohem Rauschanteil im Anlaut). Austausch: Session in `audio-slots.yaml` ändern, `python scripts/teaching_audio_slots.py --export`.
- **Vorgemerkt zum Abhören:** (1) *reloj*: ES-N-0005 und ES-L-0011 – ist das Lernenden-r wirklich uvular? (2) *pero – perro*/*caro*/*carro*: ES-N-0002 und ES-N-0005 – klingt der Kontrast fair und natürlich? (3) Die Auflösung nach Karte 1 beschreibt für beide Aufnahmen „einmal kurz“ (*pero*) und „mehrfach rasch hintereinander“ (*perro*); das ist signalseitig belegt (1 gegenüber 3–4 Kontakten), akustisch aber nicht abgehört.

## Artikulationsgrafik (nachträglich integriert, 2026-10-24)

Die vom Projektleiter bereitgestellte Grafik „Spanisch [ɾ]/[r] gegenüber Deutsch [ʁ]“ ist integriert; ursprünglich offener Medienpunkt, damit erledigt.

- **Dateien:** Master `content/teaching/spanish/r/media/images/spanish-german-r-articulation.png` (1448 × 1086, 712 KB), Auslieferung `…/spanish-german-r-articulation.webp` (83 KB, Breite 1448, Qualität 92; deklariert in `content/teaching/image-derivatives.yaml`). DE und EN nutzen dieselbe Ressource. **Hinweis zur Herkunft des Masters:** Der Chat lieferte die Grafik nur als WebP; das PNG ist deren verlustfreie Dekodierung (pixelgleich geprüft). Liegt das Original-PNG vor, genügt es, den Master auszutauschen und `python scripts/teaching_images.py --build` auszuführen (der Test prüft den Master-Hash und muss dann mit angepasst werden).
- **Position:** Abschnitt *Zwei r-Laute – und die Schrift hilft mit*, direkt nach dem Absatz zu Artikulation und Gegensatz [ɾ]/[r] (jetzt mit dem Übergangssatz „Im Standarddeutschen wird das r dagegen häufig weiter hinten gebildet, am Zäpfchen.“ / „In Standard German, by contrast, the r is often produced further back, at the uvula.“), vor dem Schreibungsabsatz und vor den Karten *caro* und *carro*. Keine neue Überschrift, kein Infokasten; vorhandener `image`-Block (`size: wide`) mit `alt`, `caption` und `credit`.
- **Texte:** Bildunterschrift DE wörtlich nach Vorgabe, EN gleichwertig; die Unterschrift nennt die gemeinsame Artikulationsstelle von [ɾ] und [r] und keine Zahl von Zungenschlägen. Alt-Text und Nachweis nach Vorgabe (DE/EN).
- **Fachliche Kontrolle:** Links alveolare Artikulation (Zungenspitze am Zahndamm), rechts hinterer Zungenrücken am Zäpfchen; Beschriftung [ɾ] / [r] und [ʁ] (umgedrehtes Kapitäl-R, nicht das aufrechte uvulare [ʀ]); die Darstellung ist schematisch (so beschriftet), kein medizinisches Schnittbild. **Keine gravierende Unstimmigkeit.** Anmerkungen: (1) Die Bewegungslinien links deuten einen Kontakt an, die Zahl der Schläge ergibt sich daraus nicht. (2) Die Beschriftungen im Bild sind deutsch („Spanisch“, „Deutsch“) und stehen damit auch auf der englischen Seite; Alt-Text und Bildunterschrift sind englisch.
- **Browser** (Chromium, :8011): DE/EN, Desktop 1366 px und Mobil 390 px, hell und dunkel; das Bild lädt als WebP (`complete`, natürliche Größe 1448 × 1086), Darstellungsgröße 736 × 552 bzw. 358 × 269 (Seitenverhältnis unverändert), zentriert, kein horizontales Scrollen; im Dunkelmodus liegt die helle Bildfläche gedimmt (vorhandene Figure-Regel, unverändert). Hörkarten und Wortfolge-Chips unverändert.
- **Tests:** `test_spanish_r_articulation_graphic_sits_after_the_explanation_with_exact_texts` (Position, genau eine Figur, Alt/Caption/Credit wörtlich, WebP + PNG-Fallback, Maße, keine Zahl von Schlägen, kein [ʀ]) und `test_spanish_r_graphic_master_is_kept_with_a_declared_webp_derivative`; der frühere Test „keine Platzhaltergrafik“ wurde entsprechend angepasst.

## Sonstige Änderungen

- `audio-slots.yaml`: Einträge `p2-pero/caro/carro/reloj/reir` neu, Reserven, Kopfkommentar. Alte Medien `p2-*-ref/learner.mp3` (8 Dateien, u. a. ES-L-0012) gelöscht; sie bleiben in der Git-Historie des öffentlichen Repos.
- Tests: `test_teaching_spanish_topics.py` um Dramaturgie (DE/EN), Zitation/Teaser und Kuration/W76-Wiederverwendung erweitert, zwei überholte Annahmen angepasst (Lernenden-Niveau-Label, 47 deklarierte Aufnahmen).
- Doku: `docs/spec/platform-data-files.md` (Mehrfach-Referenz-Karten, Wiederverwendung), `docs/runbooks/teaching-corpus-audio.md`.

## Verifikation

- `scripts/teaching_audio_slots.py --check`, `--release-report`, `scripts/validate_teaching_content.py`, `scripts/ci_governance_checks.py`: grün.
- Browser (Chromium, lokale Instanz :8011): `/de` und `/en`, Desktop 1366 px und Mobil 390 px, hell und dunkel, kein horizontales Scrollen. **Wiedergabe:** alle 10 Aufnahmen laden (HTTP 200) und laufen tatsächlich (`play()` → `currentTime` steigt, Dauer 0,98–1,85 s) in beiden Sprachfassungen. Eine akustische Beurteilung war nicht möglich.
- Wortfolge-Chips zeigen den hörbaren Inhalt (*pero – perro*, *caro*, *carro*, *reloj*, *reír*); alle Clips sind ganze Item-Aufnahmen.
- Volltest: `1474 passed, 2 skipped` (vorher `1469 passed`).

## Commit und Deployment

Commit `93a2d94` auf `main` gepusht; CI und „Deploy production“ erfolgreich. Live geprüft (`https://pronunciation-matters.de/{de,en}/teaching/spanish/r`): beide Seiten 200, fünf Hörkarten, kanonische URL unverändert, alle zehn Audiodateien 200 `audio/mpeg`, kein „Auf einen Blick“.
