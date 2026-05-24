# Teaching-Content-Modell-Diagnose

## 1. Kurzfazit

Der bestehende öffentliche Teaching-Bereich ist bereits klar als dateibasierte, repo-getriebene Public-Surface von Research getrennt. Die guten Grundentscheidungen sind schon da: keine DB, keine Admin-Schreiboberfläche, keine Research-Auth, keine Research-Intake-/Publish-Abhängigkeit, zentrale Loader-Logik in einer Datei, öffentliche Asset-Auslieferung nur aus dem Public-Root und eine für den aktuellen Rohbau ungewöhnlich gute Testabdeckung.

Der größte Wartungsnachteil liegt nicht im Renderer, sondern im Content-Modell:

- Hub- und Card-Daten werden aktuell primär aus `index.yaml` gelesen, nicht aus Topic-Dateien.
- Gruppenreferenzen, Topic-Listen und Topic-Dateien müssen heute mehrfach konsistent gehalten werden.
- Medien werden in YAMLs über harte öffentliche Pfade wie `/teaching/spanish/audio/...` referenziert, nicht topic-nah und nicht über eine auflösbare interne Medienlogik.
- Es gibt keinen dedizierten Teaching-Validator und keinen lokalen Import-/Publish-Schritt für Topic-Inhalte und Medien.

Für einen produktiven Ausbau ist das System trotzdem gut migrierbar, weil fast die gesamte Fachlogik in `app/src/app/teaching_content.py` konzentriert ist. Die künftige Migration auf ein topic-zentriertes Modell ist daher eher eine kontrollierte Umlagerung der Inhaltsquelle als ein Neuaufbau.

## 2. Ist-Zustand

### 2.1 Ist-Struktur

#### Content-Ablage

Aktuell liegt Teaching-Content unter:

- `content/teaching/{teaching_lang}/teaching.yaml`
- `content/teaching/{teaching_lang}/{ui_lang}/index.yaml`
- `content/teaching/{teaching_lang}/{ui_lang}/topics/{topic_slug}.yaml`

Konkrete aktuell vorhandene Content-Dateien:

- `content/teaching/spanish/teaching.yaml`
- `content/teaching/spanish/de/index.yaml`
- `content/teaching/spanish/en/index.yaml`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
- `content/teaching/spanish/de/topics/final-r.yaml`
- `content/teaching/spanish/en/topics/final-r.yaml`
- `content/teaching/spanish/de/topics/r.yaml`
- `content/teaching/spanish/de/topics/soft-spanish-hard-german.yaml`
- `content/teaching/english/teaching.yaml`
- `content/teaching/english/de/index.yaml`
- `content/teaching/english/en/index.yaml`
- `content/teaching/french/teaching.yaml`
- `content/teaching/french/de/index.yaml`
- `content/teaching/french/en/index.yaml`
- `content/teaching/german/teaching.yaml`
- `content/teaching/german/de/index.yaml`
- `content/teaching/german/en/index.yaml`

Nur `spanish` hat derzeit echte Topic-Dateien. `english`, `french` und `german` haben nur leere Hub-Indizes ohne Topics.

#### Medienablage

Aktuell liegen veröffentlichte Teaching-Medien unter:

- `public/teaching/spanish/audio/corapan/*.mp3`
- `public/teaching/spanish/audio/variation/*.mp3`
- `public/teaching/spanish/downloads/asset-smoke.txt`
- `public/teaching/spanish/downloads/final-r-handout.txt`
- `public/teaching/spanish/images/variation/seseo-america.svg`
- `public/teaching/spanish/images/variation/seseo-distincion-spain.svg`
- `public/teaching/spanish/video/.gitkeep`

Aktuell referenzierter Public-Asset-Bestand aus YAML:

- verwendet: die MP3-Dateien unter `audio/corapan/` und `audio/variation/`
- verwendet: `public/teaching/spanish/downloads/asset-smoke.txt`
- nicht im Beispielcontent referenziert: `public/teaching/spanish/downloads/final-r-handout.txt`
- nicht im Beispielcontent referenziert: die beiden SVGs unter `public/teaching/spanish/images/variation/`
- nicht im Beispielcontent referenziert: `public/teaching/spanish/video/`

#### Routen

Implementierte Teaching-Routen:

- `/{ui_lang}/teaching`
- `/{ui_lang}/teaching/{teaching_language}`
- `/{ui_lang}/teaching/{teaching_language}/{topic_slug}`
- `/teaching/{asset_path}`

Implementierende Dateien:

- `app/src/app/routes/public.py`
- `app/src/app/routes/public_content.py`
- `app/src/app/teaching_content.py`

#### Loader und Parser

Zentrale Loader-/Parser-Datei:

- `app/src/app/teaching_content.py`

Dort liegen:

- Root-Ermittlung und Override über `PROMAT_TEACHING_CONTENT_ROOT`
- YAML-Laden über `yaml.safe_load`
- Manifest-, Index- und Topic-Loader
- Edition-Fallbacks
- Topic-Route-Auflösung und Sprachswitch-Auflösung
- Block-Normalisierung und Markdown-Rendering
- Public-Asset-Existenzprüfungen

#### Templates

Die Teaching-Hubs und Topic-Seiten werden primär über diese Templates gerendert:

- `app/templates/pages/teaching_page.html`
- `app/templates/partials/_teaching_blocks.html`
- `app/templates/partials/_corpus_card.html`
- `app/templates/partials/_content_header.html`

Die Teaching-Links im globalen Shell-Navigationssystem sitzen zusätzlich in:

- `app/templates/partials/_top_app_bar.html`
- `app/templates/partials/_navigation_drawer.html`

#### CSS und JS

Teaching-relevante CSS-Dateien:

- `app/static/css/00_tokens.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/static/css/layout.css`

Teaching-relevante JS-Dateien:

- `app/static/js/modules/core/entry.js`
- `app/static/js/modules/core/teaching-mini-player.js`
- `app/static/js/modules/core/teaching-citation-copy.js`
- `app/static/js/modules/core/datawrapper.js`

#### Tests

Teaching wird derzeit vor allem hier getestet:

- `app/tests/test_teaching_content.py`
- `app/tests/test_research_sessions.py`

Indirekte Teaching-Bezüge zusätzlich in:

- `app/tests/test_auth_phase1.py`
- `app/tests/test_analytics.py`

#### Validatoren und Prüfskripte

Es gibt aktuell keinen dedizierten Teaching-Validator und kein dediziertes Teaching-Importskript.

Vorhandene Teaching-nahe Prüfmittel:

- Laufzeitwarnungen in `app/src/app/teaching_content.py`
- Pytest-Tests in `app/tests/test_teaching_content.py`
- Integrations- und HTML-Assertions in `app/tests/test_research_sessions.py`
- QA-Screenshot-Skripte in `scripts/qa/capture_qa.py` und `scripts/qa/capture_qa.ps1`

### 2.2 Aktuelles Content-Modell

#### `teaching.yaml`

Aktuell tatsächlich gelesen:

- `teaching_lang`
- `default_ui_lang`
- `available_ui_langs`

Pflicht heute praktisch:

- `teaching.yaml` als Datei muss existieren, sonst wird die Sprache nicht als Teaching-Sprache erkannt.

Optional bzw. mit Fallback:

- `teaching_lang` ist technisch optional, weil auf den Ordnernamen zurückgefallen wird.
- `default_ui_lang` ist technisch optional, verringert aber die Qualität des Fallbacks.
- `available_ui_langs` ist technisch optional, aber ohne echte Index-Dateien faktisch nutzlos.

Nicht validiert:

- ob `teaching_lang` zum Ordnernamen passt
- ob `default_ui_lang` in `available_ui_langs` enthalten ist
- ob alle `available_ui_langs` wirklich ein `index.yaml` haben

#### `index.yaml`

Aktuell tatsächlich gelesen:

- `title`
- `lead`
- `overview_intro`
- `hub_intro`
- `orientation`
- `groups[].title`
- `groups[].description`
- `groups[].intro`
- `groups[].topics`
- `topics[].slug`
- `topics[].title`
- `topics[].summary`
- `topics[].level`
- `topics[].category`
- `topics[].is_available`
- `topics[].is_public`
- `topics[].published`

Pflicht heute praktisch:

- `index.yaml` als Datei muss existieren, damit eine Edition als vorhanden gilt.
- Für sinnvolle Hubs braucht es mindestens `topics` oder `groups`.

Optional:

- `title` fällt im Hub auf den Sprachslug zurück.
- `lead`, `overview_intro`, `hub_intro`, `orientation`, `groups`, `topics` sind technisch optional.

Wichtiges Ist-Verhalten:

- Hub- und Card-Daten kommen heute primär aus `index.yaml`, nicht aus Topic-Dateien.
- `groups[].topics` referenziert Slugs, aber die Gruppe kann nur Karten bauen, wenn derselbe Topic-Slug zusätzlich in `topics[]` als Mapping existiert.
- Wenn `groups` existieren, verschwinden Topics, die nur in `topics[]`, aber nicht in einer Gruppe stehen.
- Wenn keine `groups` existieren, wird ein flacher Kartenstapel aus `topics[]` gebaut.

#### Topic-YAMLs

Aktuell tatsächlich gelesen:

- Top-Level:
  - `title`
  - `description`
  - `equivalents`
  - `metadata`
  - `authors`
  - `peer_review`
  - `created`
  - `updated`
  - `credits`
  - `citation`
  - `blocks`
- In Blöcken je nach Typ weitere Felder wie `body`, `title`, `lead`, `src`, `alt`, `caption`, `audio`, `examples`, `provider`, `href`, `links`, `embed_url` usw.

Pflicht heute praktisch:

- Die Topic-Datei selbst muss existieren, damit der Topic-Route-Resolver die Seite als vorhanden anerkennt.

Optional:

- `title` ist technisch optional, weil auf den Slug zurückgefallen wird.
- `description`, `equivalents`, `metadata`, `credits`, `citation` und `blocks` sind optional.

#### Tatsächlich gelesene Felder vs. tatsächlich gerenderte Felder

Wichtige Felder, die aktuell gelesen, aber auf der sichtbaren Seite nicht oder nur indirekt genutzt werden:

- `hero.title` wird gelesen, aber auf Topic-Seiten nicht sichtbar gerendert.
- `hero.eyebrow` wird gelesen, aber nicht sichtbar gerendert.
- `hero.lead` wird als Seiten-Intro genutzt, der Hero-Block selbst wird aber unterdrückt.
- `section_heading.lead` wird gelesen, aber im Template nicht gerendert.
- `audio_examples[].segments` wird geladen, aber im Template nicht angezeigt.
- `audio_examples[].speaker_id` wird geladen, aber nicht separat angezeigt.
- `audio_examples[].source` je Beispiel wird geladen, aber nicht angezeigt; sichtbar ist nur `block.source`.

Wichtige Felder, die für die aktuelle Seite sichtbar zentral sind:

- Seiten-Titel: Topic-Datei `title`
- Seiten-Intro: `hero.lead` oder sonst `description`
- Topic-Metadaten: aus `metadata.*` oder als Fallback aus Top-Level-Feldern und `credits.authors`
- Card-Titel und Card-Summary im Hub: aus `index.yaml` `topics[].title` und `topics[].summary`
- Credits-Block: aus Top-Level-`credits`
- Zitationsblock: aus Top-Level-`citation` oder aus einem `citation`-Block

#### Doppelte Pflege

Es gibt heute mehrere doppelte Pflegestellen:

- Hub-Karten brauchen `index.yaml` `topics[].title` und `topics[].summary`, obwohl die Topic-Datei denselben Gegenstand beschreibt.
- Gruppenreferenzen brauchen Slugs in `groups[].topics`, aber zusätzlich vollständige Topic-Einträge in `topics[]`.
- `which-pronunciation` und `final-r` pflegen Titel und Einordnungen sowohl im Hub-Index als auch in Topic-Dateien.
- `equivalents` werden in Topic-Dateien gepflegt, die Hub-Zuordnung aber separat in editionsspezifischen Index-Dateien.

Die heutige Card-Quelle ist damit nicht topic-zentriert, sondern hub-zentriert.

### 2.3 Mehrsprachigkeit und Editionen

#### Aktuelles Modell

- `ui_lang` ist die UI-/Editionsroute und global auf `de` und `en` beschränkt.
- `teaching_lang` ist die unterrichtete Sprache, aktuell `spanish`, `english`, `french`, `german`.
- Eine Teaching-Edition ist heute technisch die Kombination aus `teaching_lang` und `ui_lang`.

Tatsächlich vorhandene Editionen:

- `spanish/de` mit vier Topics im Index, davon zwei echte Topic-Dateien mit tieferem Ausbau und zwei deutsche Rohbau-Topics
- `spanish/en` mit vier Topics im Index, davon zwei echte Topic-Dateien
- `english/de`, `english/en`, `french/de`, `french/en`, `german/de`, `german/en` nur als leere Hubs ohne Topic-Dateien

#### Fallback-Verhalten

Edition-Fallback heute:

- Wenn die angefragte Edition existiert, wird sie genutzt.
- Sonst wird auf `default_ui_lang` aus `teaching.yaml` zurückgefallen.
- Sonst auf die erste vorhandene Edition.

Topic-Fallback heute:

- Wenn die Ziel-Edition existiert und `equivalents[target_ui_lang]` vorhanden ist, wird auf diesen Topic-Slug gewechselt.
- Sonst wird derselbe Topic-Slug in der Ziel-Edition versucht.
- Wenn dort kein Topic existiert, geht der Sprachwechsel auf den Hub der Ziel-Edition zurück.
- Wenn die Edition selbst fehlt, greift die globale UI-Sprachumschaltung und die Route leitet später auf eine funktionierende Edition um.

#### Sichtbarer Sprachswitch

Es gibt zwei Ebenen, die man trennen muss:

- sichtbar aktiv: der globale `DE | EN`-Switch im Shell-System
- vorhanden, aber derzeit nicht gerendert: `teaching_switch_items` und die CSS-Familie `.pm-teaching-locale-switch*`

Das bedeutet:

- Der globale Switch ist route-aware und nutzt `resolve_teaching_switch_path()`.
- Ein page-lokaler Editionsswitch existiert als Datenstruktur und CSS, ist aber im aktuellen Teaching-Template nicht eingebunden.

#### Fehlende Sprachfassungen

Aktuelles Verhalten bei fehlenden Sprachfassungen:

- Fehlende Topic-Seite in vorhandener Ziel-Edition: Rückfall auf Ziel-Hub
- Fehlende Edition: Rückfall auf Default-Edition bzw. Redirect im Routen-Resolver
- Fehlendes Topic insgesamt: Redirect auf Hub
- Fehlende Teaching-Sprache: 404

`equivalents` werden unterstützt, aber nur für Topic-Slug-Auflösung beim Sprachwechsel.

#### Unabhängigkeit der Editionen

Der Code erlaubt heute unterschiedliche Topic-Mengen und unterschiedliche Reihenfolgen pro Edition, weil jedes `index.yaml` editionsspezifisch ist. Das ist positiv.

Die Unabhängigkeit ist aber teuer erkauft, weil dadurch auch Card-Titel, Card-Summary und Gruppierung editionsweise dupliziert werden.

### 2.4 Medienintegration

#### Aktuelle Referenzierung

Audio, Bilder, Downloads und Videos werden heute vor allem so referenziert:

- Audio: harte absolute Public-Pfade wie `/teaching/spanish/audio/variation/distincion-casa-caza.mp3`
- Downloads: harte absolute Public-Pfade wie `/teaching/spanish/downloads/asset-smoke.txt`
- Bilder: `src`-Felder mit direktem Pfad erwartet
- Videos: `src` für öffentliche Datei oder `embed_url` für externes Embed
- Embeds: strukturierte externe Embeds mit `provider: datawrapper`, `src`, `height`, optional `caption`

#### Wo liegen Medien aktuell?

Aktuell global nach Typ und Teaching-Sprache getrennt unter:

- `public/teaching/{teaching_lang}/audio/...`
- `public/teaching/{teaching_lang}/downloads/...`
- `public/teaching/{teaching_lang}/images/...`
- `public/teaching/{teaching_lang}/video/...`

Es gibt derzeit keine topic-nahe Medienablage.

#### Validierung heute

Vorhanden:

- Public-Asset-Existenzprüfung für Audio, Downloads und lokale Videos über das Public-Root
- Path-Traversal-Schutz in der Asset-Route `/teaching/<path:asset_path>`
- Unsupported-Embed-Provider werden verworfen und geloggt
- Fehlendes `alt` bei Bildern erzeugt eine Laufzeitwarnung

Nicht vorhanden:

- keine Teaching-spezifische Prüfung, dass ein Pfad unter `/teaching/...` liegen muss
- keine Prüfung, dass Medien zum aktuellen Topic gehören
- keine systematische Prüfung von Alt-Texten, Captions, Transkripten oder Download-Metadaten
- keine Prüfung von `equivalents`
- keine Prüfung auf verwaiste oder ungenutzte Public-Medien
- keine Prüfung, ob `available_ui_langs`, Index-Dateien und Topic-Dateien konsistent sind

Wichtiges Detail:

- `_public_asset_exists()` prüft auf Existenz unter `PROMAT_PUBLIC_ROOT`, nicht auf Zugehörigkeit zu `public/teaching/`.
- Damit sind Research- oder `data/`-Pfade zwar nicht öffentlich auflösbar, aber das Modell erzwingt technisch noch nicht, dass Teaching-Blöcke nur Teaching-Pfade verwenden.

#### Unterstützte Dateitypen heute

Im bestehenden Beispielcontent und Renderer praktisch genutzt:

- Audio: MP3
- Bilder: frei referenzierbar, Beispielassets aktuell SVG
- Downloads: frei referenzierbar, Beispielassets aktuell TXT
- Video: `<video>` mit Datei oder externes `embed_url`
- Embed: aktuell nur Datawrapper erlaubt

#### Bewertung des aktuellen Medienmodells

Das bestehende Modell mit globalen Pfaden wie

```text
content/teaching/{teaching_lang}/{ui_lang}/topics/{topic_slug}.yaml
public/teaching/{teaching_lang}/audio/...
public/teaching/{teaching_lang}/images/...
```

ist für den ersten Rohbau funktional, aber für wachsenden Content redaktionell unpraktisch:

- Topic und zugehörige Medien liegen nicht beieinander.
- Umbenennungen von Topics haben keine Beziehung zu Medienordnern.
- Medienreferenzen sind manuell verkettete Public-URLs statt auflösbarer Inhaltssourcen.
- Die Trennung nach Typ statt nach Topic erschwert das lokale Ergänzen und Prüfen einzelner Topics.

### 2.5 Renderer und Blockmodell

#### Implementierte Blocktypen

Im Loader implementiert:

- `hero`
- `section_heading`
- `text`
- `rich_text`
- `image`
- `embed`
- `info_box`
- `tip_box`
- `warning_box`
- `topic_meta`
- `audio_example`
- `audio_examples`
- `audio_contrast`
- `download`
- `credits`
- `next_topics`
- `topic_grid`
- `video`
- `further_reading`
- `citation`

Intern werden `info_box`, `tip_box` und `warning_box` zu einem Admonition-Block normalisiert.

#### Im Beispielcontent tatsächlich vorkommende Blocktypen

- `hero`
- `topic_meta`
- `section_heading`
- `text`
- `rich_text`
- `info_box`
- `tip_box`
- `audio_examples`
- `audio_contrast`
- `embed`
- `download`
- `credits`
- `next_topics`
- `topic_grid`

Im Beispielcontent derzeit nicht vorkommend:

- `warning_box`
- `image`
- `video`
- `further_reading`
- expliziter `citation`-Block
- `audio_example` als Einzahl-Alias

#### Unbekannte Blocktypen

Unbekannte Blocktypen werden nicht still geschluckt, sondern geloggt und ignoriert. Das ist gut.

#### Passung des Blockmodells

Stärken:

- Das Blockmodell ist insgesamt generisch genug für narrative Topic-Seiten.
- Markdown-Normalisierung ist zentralisiert und sicher.
- Zwei-Spalten-Layout und Sectioning sind bereits sauber getrennt.
- `topic_meta` wird konsequent in den Header gezogen.

Schwächen bzw. Altlasten:

- `hero` ist faktisch nur noch ein Legacy-Input für das Intro, kein wirklicher Renderblock mehr.
- Einige geladene Audio-Felder (`segments`, `speaker_id`) haben derzeit keine sichtbare Ausgabe.
- Die Renderer erwarten weiterhin harte fertige Asset-URLs statt interne Medienreferenzen.

#### Design-/Token-System

Positiv:

- Teaching nutzt weitgehend bestehende Tokens und gemeinsame UI-Familien.
- Layout- und Komponentenstile hängen an Variablen aus `00_tokens.css`, `20_layout.css` und `30_components.css`.
- Die Audio- und Citation-Komponenten sind sichtbar ins gemeinsame System integriert.

Einschränkungen:

- Die Teaching-Audio-Tokens enthalten in `00_tokens.css` feste Basiskonstanten wie `#fff`, `#fcfcfc`, `#e5e5e5`, `#2f5f8f`, `#777`, `#666`, die erst später thematisiert überschrieben werden. Das ist kein akuter Verstoß, aber kein ganz reines Token-Modell.
- Die CSS-Familie für `.pm-teaching-locale-switch` ist derzeit tote Oberfläche, weil das Template sie nicht rendert.

### 2.6 Hub-/Card-Logik

Aktueller Stand:

- Hub-Karten werden aus `index.yaml` gebaut.
- Topic-Dateien sind für Hub-Karten nicht die Quelle.
- `next_topics` und `topic_grid` auf Topic-Seiten bauen ebenfalls Karten aus `index.yaml`, nicht aus Topic-Dateien.

Konsequenzen:

- Card-Titel und Card-Summary müssen heute separat gepflegt werden.
- Eine Topic-Datei kann existieren, aber unsichtbar bleiben, wenn sie nicht korrekt im Index erfasst ist.
- Eine Gruppe kann einen Topic-Slug nennen, aber ohne separaten `topics[]`-Eintrag wird keine Karte gebaut.

Aktuelles Verhalten in Randfällen:

- Hub referenziert Topic, Topic-Datei fehlt: Pending-Karte ohne Link
- Topic-Datei existiert, Topic fehlt im Hub-Index: Topic bleibt im Hub unsichtbar
- Topic-Datei existiert, Topic fehlt in `index.yaml topics[]`, wird aber in `groups[].topics` referenziert: ebenfalls unsichtbar
- Topic-Datei existiert und Index markiert `is_available: false`: Pending-Karte trotz vorhandener Datei

Reihenfolge heute:

- auf Root-Ebene hart kodiert in `build_corpus_cards_teaching()` als `spanish`, `english`, `french`, `german`
- auf Hub-Ebene aus `groups[]` und deren `topics[]`
- ohne Gruppen aus der Reihenfolge in `topics[]`

Kategorien/Gruppierung heute:

- explizit über `groups[]`
- `category` in `topics[]` wird als Kartenmetadatum gelesen, ist aber nicht die eigentliche Gruppierungslogik

## 3. Gute bestehende Entscheidungen, die erhalten bleiben sollen

- Teaching ist technisch sauber von Research getrennt.
- Teaching bleibt dateibasiert und repo-basiert.
- Es gibt keine DB-Abhängigkeit für Teaching-Inhalte.
- Öffentliche Teaching-Medien werden getrennt vom Content ausgeliefert.
- Die öffentliche Asset-Route schützt gegen Parent-Traversal.
- Die meiste Teaching-Fachlogik sitzt zentral in `app/src/app/teaching_content.py`.
- Markdown-Normalisierung ist zentral und deaktiviert rohes HTML.
- Topic-Metadaten werden bereits an die richtige Stelle im Header gezogen.
- Unknown Blocks und invalid Embeds werden nicht hart gecrasht, sondern defensiv verworfen.
- Die Testabdeckung für den Teaching-Rohbau ist für den aktuellen Stand gut.

## 4. Wartungsprobleme und Risiken

- Doppelte Pflege von Hub-/Card-Daten in `index.yaml` und Topic-Dateien.
- Zusätzliche doppelte Pflege innerhalb von `index.yaml`, weil Gruppen-Slugs und `topics[]` parallel gepflegt werden müssen.
- Topic-Dateien können leicht verwaisen, ohne dass es ein Validator meldet.
- Medien liegen nicht topic-nah und werden über harte Public-URLs referenziert.
- Das Modell erzwingt keine konsistente Beziehung zwischen Topic und Medien.
- Es gibt keinen dedizierten Validator, keine Import-Routine und keinen Bericht über Inkonsistenzen.
- `hero` ist als Legacy-Sonderfall im Modell verblieben und macht Topic-Dateien unnötig unklar.
- Teile der Sprachswitch-Logik sind als tote page-lokale Oberfläche vorhanden, aber derzeit nicht produktiv eingebunden.
- Die Produktivverdrahtung kopiert `content/` in das Image, aber nicht `public/`; `public` wird in Prod als Volume gemountet. Für ein zukünftiges topic-nahes Medienquellmodell braucht es deshalb zwingend eine klare Publish-/Sync-Strategie.

## 5. Spec-vs-Code-Abweichungen

### 5.1 Übereinstimmungen

- Öffentliche Teaching-Routen entsprechen der aktiven Spec.
- Teaching ist eine eigene Public-Surface und nicht an Research-Auth gekoppelt.
- Teaching-Content liegt dateibasiert unter `content/teaching/...`.
- Veröffentlichtes Teaching-Material wird aus `public/teaching/...` ausgeliefert.
- Pending-Karten im Hub werden unterstützt.
- `topic_meta` wird header-lokal und nicht als Body-Block gerendert.
- `citation` wird als eigener Abschlussblock gerendert.
- Datawrapper wird als strukturierter Embed-Provider behandelt.

### 5.2 Relevante Abweichungen oder Spannungen

| Einstufung | Beobachtung | Bewertung |
| --- | --- | --- |
| unkritisch | In CSS und Datenstruktur existiert ein page-lokaler Editionsswitch, der aktuell nicht gerendert wird. | Tote Altfläche, aber kein inhaltlicher Bruch. |
| mittelfristig störend | `hero` ist in produktivem Beispielcontent noch aktiv, obwohl Topic-Seiten heute über Header + Intro laufen. | Legacy-Last im Content-Modell. |
| mittelfristig störend | Einige gelesene Audio-Felder wie `segments` und `speaker_id` haben derzeit keine Ausgabe. | Modell und sichtbare Oberfläche driften leicht auseinander. |
| sollte vor produktivem Ausbau bereinigt werden | Hub-Karten bauen aus `index.yaml` statt aus Topic-Dateien. | Kernproblem für Wartbarkeit und doppelte Pflege. |
| sollte vor produktivem Ausbau bereinigt werden | Gruppen- und Topic-Liste im Hub müssen parallel gepflegt werden. | Hohe Inkonsistenzgefahr bei Wachstum. |
| sollte vor produktivem Ausbau bereinigt werden | Medienreferenzen sind harte Public-URLs statt interne referenzierbare Quellen. | Erschwert topic-nahe Organisation und Validierung. |
| sollte vor produktivem Ausbau bereinigt werden | Es gibt keinen dedizierten Teaching-Validator. | Fehler werden erst spät oder gar nicht sichtbar. |
| blockierend für das vorgeschlagene Zielmodell | Das aktive Runtime-Modell liefert nur aus `PROMAT_PUBLIC_ROOT/teaching`, während das Zielmodell topic-nahe Medien unter `content/teaching/.../media` vorsieht. | Ohne explizite Publish-/Resolver-Strategie ist das Zielmodell nicht deploybar. |

## 6. Bewertung des vorgeschlagenen Zielmodells

Das vorgeschlagene Zielmodell

```text
content/teaching/{teaching_lang}/
  teaching.yaml
  hubs/
    de.yaml
    en.yaml

  {topic_slug}/
    de.yaml
    en.yaml
    media.yaml
    media/
      audio/
      images/
      video/
      downloads/
```

ist für diese App inhaltlich sinnvoll und mit dem bestehenden Loader/Renderer gut migrierbar.

### 6.1 Warum es sinnvoll ist

- Alle Fassungen eines Topics liegen zusammen.
- Topic-Dateien können endlich die kanonische Quelle für Titel, Beschreibung, Card-Daten, Credits und Blocks werden.
- Hub-Dateien können auf Reihenfolge, Gruppierung und Sichtbarkeit reduziert werden.
- Topic-nahe Medien erleichtern lokales Arbeiten und Review.
- Fehlende Sprachfassungen bleiben natürlich möglich.

### 6.2 Welche Codebereiche betroffen wären

- `app/src/app/teaching_content.py`
  - Pfadfunktionen `_manifest_path`, `_index_path`, `_topic_path`
  - Editionserkennung `list_existing_ui_editions()`, `edition_exists()`, `resolve_teaching_edition_ui_lang()`
  - Hub-Kartenbau `_hub_topic_card()`, `_hub_topic_groups()`, `_build_topic_grid_cards()`
  - Topic-Lader `load_teaching_topic()`
  - Switch-Logik `resolve_topic_slug_for_ui_lang()` und `resolve_teaching_switch_path()`
- `app/src/app/routes/public_content.py`
  - Root-Statuszählung über `count_teaching_topics()`
- Tests in `app/tests/test_teaching_content.py` und `app/tests/test_research_sessions.py`
- QA-Skripte, sofern sie feste Beispielrouten oder Dateierwartungen abprüfen

### 6.3 Risiken der Migration

- Das heutige Hub-Modell hängt mehrfach an `index.yaml`; diese Abhängigkeit muss sauber auf Topic-Dateien umgelegt werden.
- `equivalents` müssen konsistent bleiben, wenn Topic-Slugs editionsweise nicht deckungsgleich sind.
- Pending-Karten müssen auch im neuen Modell sauber als redaktionell geplante, aber noch nicht öffentliche Topics beschrieben werden.
- Die Medienfrage ist nicht nur Loader-, sondern auch Deploy- und Runtime-Wiring-Frage.

## 7. Medienstrategie-Empfehlung

### Empfehlung

Für diese App ist die einfachste und robusteste Lösung:

- Topic-nahe Medien als redaktionelle Quelle unter `content/teaching/{teaching_lang}/{topic_slug}/media/...`
- öffentliche Auslieferung weiterhin ausschließlich aus `public/teaching/...`
- ein kleiner lokaler Publish-/Sync-Schritt erzeugt oder aktualisiert die auslieferbare Public-Struktur deterministisch

### Begründung

- Das respektiert die aktive Trennung `content/` versus `public/`.
- YAML-Dateien bleiben sicher außerhalb der Public-Auslieferung.
- Die bestehende Asset-Route kann fast unverändert bleiben.
- Die Produktivverdrahtung ist bereits auf `PROMAT_PUBLIC_ROOT` als Auslieferungsgrenze ausgelegt.

### Kein Direkt-Serving aus `content/teaching/.../media`

Technisch wäre ein dedizierter Asset-Resolver möglich, der nur `media/` aus `content/teaching/...` öffentlich serviert und YAML ausschließt. Für diese App wäre das aber die fragilere Variante, weil es:

- die heutige `content`/`public`-Trennung aufweicht
- zusätzliche Sicherheitslogik braucht
- vom bestehenden Runtime- und Spec-Modell wegführt

### Braucht es einen Asset-Resolver?

Ja, aber eher als Inhalts-Resolver als als Dateiserver:

- Block-YAML sollte später bevorzugt Medien über IDs oder relative Pfade innerhalb des Topics referenzieren.
- Der Loader sollte daraus eine öffentliche URL auf eine veröffentlichte Datei ableiten.

Das ist ein guter Resolver. Ein Direkt-HTTP-Resolver auf `content/` ist für diese App nicht die bevorzugte Lösung.

## 8. Sprach-/Editionsstrategie-Empfehlung

- `ui_lang` und `teaching_lang` sollten konzeptionell getrennt bleiben.
- Fehlende Sprachfassungen eines Topics sollten explizit erlaubt bleiben.
- Der sichtbare Sprachswitch sollte nur Editionen anbieten, die vorhanden oder sinnvoll fallbackbar sind.
- `equivalents` sollten bleiben, aber nur für nicht deckungsgleiche Slugs.
- Topic-Dateien sollten die kanonische Quelle je Edition werden.
- Hub-Dateien sollten nur Reihenfolge, Gruppierung und Sichtbarkeit steuern.

Wichtiger Realismus-Hinweis:

- Aktuell sind öffentliche UI-Routen global auf `de` und `en` beschränkt.
- Wenn langfristig Teaching-only-Editionen außerhalb `de`/`en` gewünscht sind, braucht das später eine explizite Routen- und Shell-Entscheidung.
- Für das hier gewünschte Zielmodell ist das noch nicht blockierend, solange das öffentliche UI bei `de` und `en` bleibt.

## 9. Validator-Empfehlung

Aktuell gibt es keinen dedizierten Teaching-Validator. Das sollte vor dem produktiven Ausbau ergänzt werden.

Ein einfacher späterer Validator sollte mindestens prüfen:

- Manifest-Konsistenz pro Teaching-Sprache
- vorhandene Hub-Dateien pro Edition
- vorhandene Topic-Dateien pro referenziertem Topic
- keine verwaisten Topic-Dateien ohne Hub-Bezug
- keine Gruppenreferenzen ohne Topic-Definition
- `equivalents` nur auf existierende Ziel-Topics
- Pflichtfelder je Topic-Datei
- Pflichtfelder je Blocktyp
- nur erlaubte Blocktypen
- Medienreferenzen auflösbar
- erlaubte Dateitypen
- fehlende Alt-Texte bei Bildern
- fehlende Transkripte bei Audio-Beispielen mindestens als Warnung
- fehlende Captions bei relevanten Bild-/Video-Elementen mindestens als Warnung

Sinnvoller späterer Ablageort:

- `scripts/validate_teaching_content.py`

Das ist einfacher und wartbarer als sofort einen neuen Script-Unterbaum zu eröffnen.

## 10. Import-Workflow-Empfehlung

### Empfohlene Import-Struktur

Von den beiden vorgeschlagenen Varianten ist diese einfacher:

```text
content/teaching_import/{teaching_lang}/{topic_slug}/
  de.yaml
  en.yaml
  media/
    ...
```

Begründung:

- `teaching_lang` ist eine echte Primärachse des Systems.
- Topic-Slugs können zwischen Teaching-Sprachen kollidieren, ohne dass sie inhaltlich dasselbe bedeuten.
- Die Zielstruktur unter `content/teaching/{teaching_lang}/{topic_slug}/...` wird direkt vorbereitet.

### Empfohlenes Verhalten der späteren Routine

- Standardmodus: Dry-Run
- Schreibmodus nur explizit per Flag
- niemals still überschreiben

Die Routine sollte später:

- YAML parsen und validieren
- `teaching_lang` und `topic_slug` normalisieren
- Editionsdateien prüfen
- Medienreferenzen prüfen
- erlaubte Dateitypen prüfen
- Dateinamen normalisieren
- optional Audio nach MP3 konvertieren
- Zielstruktur unter `content/teaching/{teaching_lang}/{topic_slug}/...` erzeugen
- optional `media.yaml` erzeugen oder aktualisieren
- optional Public-Medien deterministisch nach `public/teaching/...` publizieren
- danach den Teaching-Validator laufen lassen
- nichts deployen
- keine Server-Pipeline auslösen

### Konfliktbehandlung

Empfehlung:

- bestehende `de.yaml` und `en.yaml` nie automatisch überschreiben
- bestehende `media.yaml` nur mit explizitem Merge-Modus anfassen
- bestehende veröffentlichte Public-Dateien nur mit explizitem Replace-Modus überschreiben
- `teaching.yaml` und Hub-Dateien nie automatisch überschreiben

### Gewünschte Reports

- Dry-Run-Bericht mit geplantem Zielbaum
- Feld- und Blockvalidierungsbericht
- Medienbericht mit fehlenden, ungenutzten oder umbenannten Dateien
- Konfliktbericht
- finaler Validator-Bericht

## 11. Minimaler Refactoring-Vorschlag in 2–3 Phasen

### Phase 1: Modell entdoppeln

- Hub-Dateien auf Reihenfolge, Gruppierung, Sichtbarkeit und optionale Hub-Texte reduzieren
- Card-Daten aus Topic-Dateien lesen
- Topic-Dateien als kanonische Quelle für `title`, `description`, `card`, `credits`, `blocks`
- Legacy-`hero` als Übergangspfad markieren und später abbauen

### Phase 2: Medien topic-nah organisieren

- Topic-nahe Medienquelle unter `content/teaching/{teaching_lang}/{topic_slug}/media/...`
- internen Medien-Resolver einführen
- deterministischen lokalen Publish-/Sync-Schritt nach `public/teaching/...` ergänzen
- Validator um Medienchecks erweitern

### Phase 3: lokale Redaktion absichern

- Validator als Standard-Lokalcheck
- einfacher Dry-Run-Import für neue Topics und kleine Medien
- fokussierte Regressionstests für fehlende Editionen, fehlende Topics, fehlende Medien und Card-Fallbacks

## 12. Liste betroffener Dateien

### Aktive Spec und historische Planung

- `docs/spec/platform-data-files.md`
- `docs/plans/teaching_section_raw.md`

### Runtime und Routen

- `app/src/app/teaching_content.py`
- `app/src/app/routes/public.py`
- `app/src/app/routes/public_content.py`
- `app/src/app/__init__.py`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`

### Templates

- `app/templates/pages/teaching_page.html`
- `app/templates/partials/_teaching_blocks.html`
- `app/templates/partials/_corpus_card.html`
- `app/templates/partials/_content_header.html`
- `app/templates/partials/_top_app_bar.html`
- `app/templates/partials/_navigation_drawer.html`

### Styles und JS

- `app/static/css/00_tokens.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/static/css/layout.css`
- `app/static/js/modules/core/entry.js`
- `app/static/js/modules/core/teaching-mini-player.js`
- `app/static/js/modules/core/teaching-citation-copy.js`
- `app/static/js/modules/core/datawrapper.js`

### Content

- `content/teaching/spanish/teaching.yaml`
- `content/teaching/spanish/de/index.yaml`
- `content/teaching/spanish/en/index.yaml`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
- `content/teaching/spanish/de/topics/final-r.yaml`
- `content/teaching/spanish/en/topics/final-r.yaml`
- `content/teaching/spanish/de/topics/r.yaml`
- `content/teaching/spanish/de/topics/soft-spanish-hard-german.yaml`
- `content/teaching/english/teaching.yaml`
- `content/teaching/english/de/index.yaml`
- `content/teaching/english/en/index.yaml`
- `content/teaching/french/teaching.yaml`
- `content/teaching/french/de/index.yaml`
- `content/teaching/french/en/index.yaml`
- `content/teaching/german/teaching.yaml`
- `content/teaching/german/de/index.yaml`
- `content/teaching/german/en/index.yaml`

### Public Assets

- `public/teaching/spanish/audio/corapan/MEXb80def27c.mp3`
- `public/teaching/spanish/audio/corapan/CHL8b78ac16b.mp3`
- `public/teaching/spanish/audio/corapan/ARGCBAeca46a987.mp3`
- `public/teaching/spanish/audio/corapan/CRI61d9dc2dc.mp3`
- `public/teaching/spanish/audio/variation/distincion-casa-caza.mp3`
- `public/teaching/spanish/audio/variation/seseo-casa-caza.mp3`
- `public/teaching/spanish/audio/variation/distincion-word-series.mp3`
- `public/teaching/spanish/audio/variation/seseo-word-series.mp3`
- `public/teaching/spanish/downloads/asset-smoke.txt`
- `public/teaching/spanish/downloads/final-r-handout.txt`
- `public/teaching/spanish/images/variation/seseo-america.svg`
- `public/teaching/spanish/images/variation/seseo-distincion-spain.svg`

### Tests und QA

- `app/tests/test_teaching_content.py`
- `app/tests/test_research_sessions.py`
- `app/tests/test_auth_phase1.py`
- `app/tests/test_analytics.py`
- `scripts/qa/capture_qa.py`
- `scripts/qa/capture_qa.ps1`

### Runtime-Wiring für Dev und Prod

- `app/Dockerfile`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## 13. Empfohlene Tests und Checks

- Validator-Test: verwaiste Topic-Datei ohne Hub-Referenz
- Validator-Test: Hub referenziert Topic ohne Topic-Datei
- Validator-Test: Gruppe referenziert Slug ohne `topics[]`-Eintrag
- Validator-Test: `equivalents` zeigt auf nicht vorhandenes Topic
- Validator-Test: Medienreferenz zeigt auf fehlende Datei
- Validator-Test: Bild ohne Alt-Text mindestens Warnung
- Validator-Test: Audio ohne Transcript mindestens Warnung
- Integrationstest: Hub-Karten ziehen Titel und Summary aus Topic-Dateien statt aus Hub-Dateien
- Integrationstest: fehlende Ziel-Edition bietet nur sinnvolle Switch-Ziele an
- Integrationstest: Topic nur in `de` führt beim Switch nach `en` sauber auf den Hub
- Integrationstest: Pending-Topic bleibt ohne Link, obwohl Topic-Ordner schon existiert
- Integrationstest: Public-Asset-Route bleibt auf `public/teaching` begrenzt

## 14. Offene Fragen

- Soll der künftige sichtbare Sprachswitch auf Teaching-Seiten page-lokal zusätzlich zum globalen `DE | EN`-Switch erscheinen oder bleibt nur der globale Switch aktiv?
- Sollen `card.title` und `card.description` als optionale Overrides in Topic-Dateien genügen, mit Fallback auf `title` und `description`?
- Soll `hero` im Zielmodell noch als Legacy-Eingabe unterstützt werden oder vollständig entfallen?
- Sollen Topic-Metadaten künftig nur noch unter `metadata:` gepflegt werden oder bleiben die heutigen Top-Level-Fallbacks bewusst erhalten?
- Soll `media.yaml` wirklich eingeführt werden oder reicht für den Anfang eine reine relative Dateireferenzierung innerhalb des Topic-Ordners?
- Wie genau synchronisiert der bestehende GitHub-Deploy-Lauf derzeit das Repo-`public/` in das produktive Public-Volume? Das ist für jedes künftige Medienmodell entscheidend.
- Soll der spätere Publish-/Sync-Schritt nur lokal durch Redakteur:innen laufen oder zusätzlich in CI prüfbar sein, ohne selbst Artefakte zu schreiben?