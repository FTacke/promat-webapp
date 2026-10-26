# Master-Redaktion der Spanisch-Themenseiten und Vorbereitung zusätzlicher Inhaltsfassungen (2026-10-26)

## Redaktion (Teil A, DE verbindlich, EN synchronisiert)

- *Welche Aussprache unterrichten?*: Abschnitt *Seseo und distinción* („zwei regional verbreitete Aussprachemuster“), Infokasten („vor allem in Zentral- und Nordspanien üblich“).
- *Weiches Spanisch, hartes Deutsch*: letzter Einleitungssatz („… wie sie den spanischen Redefluss beeinflussen“). Progression und Mitautorenschaft unverändert.
- *Europa klingt auf Spanisch anders*: Teaser, Einleitung, Vertiefungstext zum Querverweis *Weiches Spanisch, hartes Deutsch* (Link unverändert). *mismo – álbum* unverändert.
- *B oder V? Wenn die Schrift mitredet*: Teaser, Einleitung (Phonem /b/, Übertragung der deutschen Unterscheidung).
- *b, d und g: Zu hart ausgesprochen?*: Einleitung, Schlusssatz *Verschluss oder Annäherung?* („häufig als ‚weicher‘ wahrgenommen“), hervorgehobener Satz im Infokasten („Als erste Orientierung gilt …“).
- *Das spanische r*: letzter Satz im Abschnitt *Nicht jedes r klingt gleich* entfernt.
- *Das r am Wortende*: Satz „Der erste Hörvergleich zeigt …“ entfernt; neuer Einstieg in *Wenn das deutsche r zum Vokal wird*, danach geglättet („Dabei sind zwei Fälle zu unterscheiden …“), Unterscheidung R-Vokalisierung nach Vokal vs. Vater-Schwa erhalten; redundanter *sehr*-Satz entfernt.
- Teaser = Beschreibung (Metadaten) bei *Europa* und *B oder V?* gleich gesetzt. Keine weiteren Textänderungen; Audio-Slots, Hashes, Medien und Bildnachweise unverändert (`--check`, Bild-Check).

## Inhaltsfassungen (Teil C)

- Architektur, URL-Schema und Regeln: Spec *Teaching content editions*, ADR `2026-10-26_teaching-content-editions-06.md`, Runbook `teaching-content-editions.md`.
- `spanish/teaching.yaml` deklariert `content_editions: [es]`; es gibt noch keine `es.yaml`: Keine Seite, kein Link, kein `hreflang` ist öffentlich sichtbar (Test gegen das echte Repository).
- Komponenten: `edition_links` im gemeinsamen Content-Header (Textlink mit Globus-Icon gegenüber dem Zurück-Link; ohne Fassung unverändertes Markup), Routen `/{ui_lang}/teaching/{lang}/{code}[/{slug}]`, validierte Herkunft `?from=`, DE/EN-Schalter serverseitig (`teaching_switch_query`) und clientseitig (`promat-ui-switch-params`) inhaltserhaltend, Canonical/`hreflang`/JSON-LD/Zitation je Fassung, Validator-Regeln (Code-Format, Kollision mit Slugs/Aliassen, undeklarierte Sprachdateien, gleiche `resource_id`/Creators).
- Browser-Pass mit einer lokalen, nicht committeten `[QA]`-Platzhalterfassung (`tmp/ui-qa/2026-10-26-content-editions/`): DE/EN-Seite und Übersicht zeigen `En español` rechts gegenüber dem Zurück-Link, die Fassung zeigt `Auf Deutsch`/`In English` je nach Herkunft, Schalter behält den Inhalt; Desktop/Mobil, Hell/Dunkel, kein Overflow, keine Konsolenfehler. Erste Fassung der Zeile war auf dem Desktop zentriert (Zeile schrumpfte auf Inhaltsbreite) und wurde auf volle Breite korrigiert. Echte Seiten (DE/EN-Themenseiten, Übersicht, Research-Design) unverändert.
- Offen bis zur ersten Aktivierung: spanische Block-Labels (Sprecherrollen, Wortfolge-Chip, Auflösung, Vertiefung) und spanische Zitationskonventionen; interne Links in Fassungstexten.

## Prüfungen

- ruff, Governance, Teaching-Validator, Slot-Check, Bild-Check, Browser-Smoke, JS-Tests, volle pytest-Suite grün. Neue Tests: `app/tests/test_teaching_content_editions.py` (Sichtbarkeit, Routing, Herkunft, Schalter, Canonical/`hreflang`, Zitation, Französisch, Validator), JS-Tests für den Schalter, Redaktionsregression `test_master_revision_wording_is_in_place_in_german_and_english`; Route in der Sicherheitsmatrix als öffentlich klassifiziert.

## Export (Teil D)

- `spanish_themenseiten_de_master_review_v2.md` im Downloads-Ordner des Projektverantwortlichen (außerhalb des Repositorys), aus den finalen `de.yaml` generiert; Vollständigkeitsprüfung gegen alle Textfelder der Quelle.
