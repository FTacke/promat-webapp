# Teaching in vier Sprachen: Übersichtstitel, „Alle Themen“ und 15 angekündigte Themenseiten (2026-10-27)

## Übersichten

| Sprache | DE | EN |
|---|---|---|
| Spanisch | Spanische Aussprache verstehen | Understanding Spanish Pronunciation |
| Englisch | Englische Aussprache verstehen | Understanding English Pronunciation |
| Französisch | Französische Aussprache verstehen | Understanding French Pronunciation |
| Deutsch | Deutsche Aussprache verstehen | Understanding German Pronunciation |

Spanische Inhaltsedition: „Comprender la pronunciación del español“. URLs unverändert. Englisch, Französisch und Deutsch haben jetzt das Zweispalten-Layout der Spanisch-Übersicht mit „Zum Einstieg“ / „Getting started“ und „Aussprachephänomene entdecken“ / „Exploring pronunciation features“ und eine kurze Einleitung, die die Reihe ankündigt („entstehen derzeit“), ohne Hörbeispiele zu versprechen. Die Sprachauswahl zeigt vier aktive Sprachen mit 7 / 5 / 6 / 4 Themenseiten (aus dem Content-Index gezählt).

## Zurück-Link

Auf allen Themenseiten „Alle Themen“ / „All topics“ (`teaching.action.back_to_language_hub`, gemeinsame Komponente). In der spanischen Inhaltsedition gehört der Link zur Navigation und folgt der UI-Sprache; er führt zur spanischen Übersicht (kein „Todos los temas“, da kein Inhaltslabel).

## Angekündigte Themenseiten (`status: placeholder`)

| Sprache | Slug | DE-Titel | EN-Titel |
|---|---|---|---|
| Englisch | `which-english-pronunciation` | Welches Englisch unterrichten? | Which English to teach? |
| Englisch | `ship-or-sheep` | Ship oder sheep? Wenn Vokale Wörter verändern | Ship or sheep? When vowels change words |
| Englisch | `english-th` | Das englische th: zwei Laute, viele Varianten | The English th: two sounds, many variants |
| Englisch | `weak-forms-and-schwa` | Warum kleine Wörter plötzlich anders klingen | Why small words suddenly sound different |
| Englisch | `english-stress` | Englisch betont anders | Stress works differently in English |
| Französisch | `nasal-vowels` | Was die Nase mit französischen Vokalen zu tun hat | What the nose has to do with French vowels |
| Französisch | `u-or-ou` | u oder ou? Zwei Schreibungen, zwei Vokale | u or ou? Two spellings, two vowels |
| Französisch | `liaison` | Liaison: Wenn stumme Konsonanten hörbar werden | Liaison: when silent consonants become audible |
| Französisch | `schwa` | Das flüchtige e: Wo bleibt das Schwa? | The fleeting e: where does the schwa go? |
| Französisch | `spelling-and-pronunciation` | Französisch klingt anders, als es geschrieben wird | French sounds different from how it is spelled |
| Französisch | `french-stress` | Wo liegt die Betonung im Französischen? | Where does the stress fall in French? |
| Deutsch | `miete-or-mitte` | Miete oder Mitte? Wenn Vokale Wörter unterscheiden | Miete or Mitte? When vowels tell words apart |
| Deutsch | `ich-or-ach` | Ich oder ach? Zwei Laute für ch | Ich or ach? Two sounds for ch |
| Deutsch | `final-devoicing` | Rad oder Rat? Am Wortende wird es stimmlos | Rad or Rat? Voiceless at the end of the word |
| Deutsch | `german-stress` | Was die Betonung im Deutschen verändert | What stress changes in German |

URLs: `/{de|en}/teaching/{english|french|german}/{slug}`; alle Slugs wie vorgeschlagen. Teaser DE wörtlich aus dem Auftrag, EN idiomatisch übertragen (Dateien `content/teaching/{lang}/{slug}/{de,en}.yaml`).

Darstellung: Kopf mit „Alle Themen“, Titel, Teaser und „Autor:innen: tba“ / „Authors: tba“; keine Blöcke, keine Datumsangaben, keine leeren Container, kein unterer Zurück-Link, keine Zitation, kein JSON-LD, `noindex` ohne Canonical/hreflang. Die Karten sind reguläre, anklickbare Themenkarten. Der Validator verlangt für Platzhalter Titel, Teaser und `resource_id` und verbietet Autor:innen, Datumsangaben und Inhaltsblöcke. Die alten französischen Gerüste (`nasalvokale`, `gleitlaute` mit deutschen Slugs und Fülltext, `liaison`) sind ersetzt; das Liaison-Gerüst bleibt nur als Test-Fixture für das Rendering aller Blocktypen (`app/tests/fixtures/teaching_scaffold/`).

## Bestandsschutz

Die sieben spanischen Themenseiten (`de.yaml`, `en.yaml`, `es.yaml`), Audio-Slots, Medien und Illustrationen sind unverändert (Diff: nur die drei Titelzeilen der spanischen Übersichten); Zitation, Sprachlinks „En español“ und die Inhaltsedition funktionieren weiter.

## Prüfungen

- Neue Tests `app/tests/test_teaching_four_languages.py` (Sprachauswahl 7/5/6/4, vier Übersichtstitel und -strukturen in DE/EN, alle 15 Seiten in DE/EN mit Titel, Teaser, „tba“, ohne Blöcke/Zitation/JSON-LD, `noindex`, Rücklinks, „Alle Themen“ auf allen spanischen Seiten und in der Inhaltsedition, alte französische Slugs 404, Validator-Regeln); bestehende Tests auf den neuen Stand gebracht.
- 1585 Tests, ruff, Governance, Teaching-Validator, Slot-/Bild-Check, JS-Tests, Browser-Smoke grün.
- Browser (lokal, echte Inhalte): Sprachauswahl, alle vier Übersichten, je eine Platzhalterseite pro Sprache, eine spanische Themenseite und deren Inhaltsedition, DE/EN × Desktop/Mobil × Hell/Dunkel: 80 Aufrufe mit 200, kein Overflow, keine Konsolenfehler, keine fehlenden Ressourcen.

## Offen

- Der allgemeine Einleitungssatz der Sprachauswahl („Themenseiten mit fachlicher Orientierung, Hörbeispielen und Unterrichtsimpulsen“) gilt bisher nur für Spanisch vollständig; nicht geändert, da die Sprachauswahl nicht umgestaltet werden sollte.

## Nachtrag: Einheitliche Einleitung, kursive Erwähnungen

- Alle Übersichten tragen die Einleitung der Spanisch-Übersicht, mit dem jeweiligen Fach (Spanisch-, Englisch-, Französisch-, Deutschunterricht / Spanish, English, French, German lessons); die „entstehen derzeit“-Texte sind entfernt.
- Metasprachliche Erwähnungen in Titeln und Teasern kursiv, in DE, EN und der spanischen Inhaltsedition: *Europa*/*Europe*, *B*/*V*, *b*, *d*, *g*, *r* (auch *r*-Laute), *th*, *Ship*/*sheep*, *u*/*ou*, *e*, *Miete*/*Mitte*, *Ich*/*ach*, *ch*, *Rad*/*Rat*, *n*, *z*-Laut; ebenso dort, wo Seitentitel zitiert werden (Vertiefungstitel, Linktexte). Fachtermini (Schwa, Liaison, erres) bleiben aufrecht. `<title>`, Meta-Beschreibung, JSON-LD und Zitation zeigen Klartext.
- Der Post-Deploy-Smoke vergleicht den `<title>` jetzt mit dem Klartext des Seitentitels (vorher wäre er an den Sternchen gescheitert).
