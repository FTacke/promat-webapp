# ADR: Teaching-Inhaltsfassungen unabhängig von der UI-Sprache

Status: accepted

Datum: 2026-10-26

## Kontext

Die Plattform ist global zweisprachig (`de`, `en`); die Teaching-Editionen hängen bisher an der UI-Sprache (`de.yaml`, `en.yaml`, Präfix `/{ui_lang}/`, `?lang=`). Die spanischen Themenseiten sollen zusätzlich auf Spanisch erscheinen, später die französischen auf Französisch. Eine dritte globale UI-Sprache ist ausdrücklich nicht gewollt: Die DE/EN-Pille bleibt, die spanische Fassung muss auch mit deutscher oder englischer Navigation funktionieren, und `?lang=es` darf nicht zum Umschalter der Inhaltssprache werden.

## Entscheidung

- UI-Sprache und Inhaltssprache sind getrennte Dimensionen. Eine Unterrichtssprache deklariert zusätzliche Inhaltssprachen in `teaching.yaml` (`content_editions: [es]`).
- Die Inhaltssprache ist ein stabiles Pfadsegment unter der unveränderten UI-Präfix-Struktur: `/{ui_lang}/teaching/{teaching_language}/{content_lang}[/{topic_slug}]`. Der DE/EN-Schalter tauscht nur das Präfix; der Inhalt bleibt.
- Dateien liegen neben den bestehenden (`hubs/es.yaml`, `{topic}/es.yaml`), mit gleichem Slug, gleicher `resource_id` und gleichen Creators; Medien werden geteilt.
- Sichtbar und erreichbar ist eine Fassung erst, wenn sie veröffentlicht ist (normale Verfügbarkeitsregel plus veröffentlichte DE/EN-Ausgangsseite). Vorher: 404, kein Link, kein `hreflang`.
- Ein kleiner Textlink mit Eigenbezeichnung der Sprache (`En español`) steht gegenüber dem Zurück-Link; die Fassung führt mit `Auf Deutsch`/`In English` zurück. Die Herkunft wird als `?from=de|en` geführt und nur gegen die vorhandenen UI-Editionen geprüft (kein URL-Rücksprungziel, kein offener Redirect); ohne gültigen Wert gilt die aktuelle UI-Sprache.
- Eine Fassung hat genau einen Canonical (Präfix der Standard-UI-Edition, z. B. `/de/teaching/spanish/es/...`), unabhängig von der Navigationssprache; `hreflang` verknüpft nur veröffentlichte Fassungen; Zitation und JSON-LD behalten Ressourcen-ID und Autorenschaft, `inLanguage` ist die Inhaltssprache.

## Auswirkungen

- Keine sichtbare Änderung, solange keine Fassung veröffentlicht ist; DE/EN-Routen, Canonicals und der Schalter bleiben unverändert.
- Derselbe Mechanismus trägt Französisch (`content_editions: [fr]`) ohne Sonderlogik.
- Inhaltscodes sind reservierte Pfadsegmente: Kein Themen-Slug und kein Alias darf `es`/`fr` heißen (Validator).
- Bis zur Aktivierung offen: Spanische Beschriftungen für Block-Labels (Sprecherrollen, Wortfolge-Chip, Auflösung) und spanische Zitationskonventionen; bis dahin erscheinen diese in der UI-Sprache bzw. in englischer Zitierform.
- Betroffen: `app/src/app/teaching_content.py`, `routes/public.py`, `publication.py`, `partials/_content_header.html`, `app-bar.js`, `scripts/validate_teaching_content.py`.

## Alternativen

- Dritte globale UI-Sprache `es`: verworfen (Pille und gesamte Plattform müssten spanisch werden).
- `?lang=es` oder ein flüchtiger Query-Parameter für die Inhaltssprache: verworfen (bricht die Bedeutung von `lang`, keine stabilen Ressourcenpfade, kein sauberer Canonical).
- Suffix `/{topic_slug}/es`: verworfen (uneinheitlich zwischen Hub und Themenseite).
- Herkunft im Cookie: verworfen (unsichtbarer Zustand, mehrere Tabs widersprechen sich); der validierte Query-Wert ist nachvollziehbar und zustandslos.

## Referenzen

- `docs/agent-runs/2026-10-26_master-revision-and-content-editions.md`
- `docs/spec/platform-data-files.md` (Routing, *Teaching content editions*, *URL identity*, *Citations*)
- `docs/runbooks/teaching-content-editions.md`
