---
tags: promat, Pronunciation Matters, Implementierung, Teaching
---

# Teaching-Rohbau: Architektur- und Umsetzungsplan

## Status und Zweck

Status: Der erste öffentliche Teaching-Rohbau wurde umgesetzt. Die aktive Soll-Beschreibung liegt jetzt in `docs/spec/platform-data-files.md`; dieses Dokument bleibt als historische Planungsgrundlage erhalten.

Dieses Dokument beschreibt den geplanten Rohbau des öffentlichen Teaching-Bereichs der PROMAT-Webapp.

Der Teaching-Bereich ist ein eigenständiger öffentlicher Inhaltsbereich neben dem geschützten Research-Bereich. Er dient der Bereitstellung von didaktisch aufbereiteten Materialien zur Aussprachevermittlung in verschiedenen Unterrichtssprachen, insbesondere Spanisch, Englisch, Französisch und Deutsch.

Der Fokus dieses Plans liegt auf der Grundarchitektur, nicht auf der finalen inhaltlichen oder gestalterischen Ausarbeitung einzelner Seiten.

Ziel des ersten Umsetzungsschritts ist ein robuster, erweiterbarer Rohbau mit:

- öffentlichen Teaching-Routen,
- dateibasiertem Content-Modell,
- öffentlicher Medienstruktur,
- sprach- und editionsfähigem Routing,
- kontextsensitivem Sprachswitch,
- flexiblem Blockrenderer,
- Card-basierten Sprach-Hubs,
- einfachen Themenseiten,
- Credits-Modell,
- keiner Admin-Schreiboberfläche.

## Grundentscheidung

Teaching wird als vollöffentlicher Bereich der Webapp umgesetzt.

Der Bereich ist unabhängig vom geschützten Research-Bereich. Inhalte können zwar fachlich aus Research-Materialien abgeleitet oder dort ausgewählte Beispiele übernehmen, technisch darf Teaching aber nicht von Research-Sessions, owner-gebundenen Sets, Auth-Logik oder geschützten Datenpfaden abhängen.

Teaching ist kein Research-Unterbereich und keine Ausnahme innerhalb des Research-Access-Modells.

## Abgrenzung zu Research

Für Research gilt weiterhin:

- `/{ui_lang}/research/{corpus}/design` ist öffentlich.
- Alle anderen Research-Flächen sind geschützt.
- Research arbeitet mit geschützten Forschungsdaten, Session-Kontexten, Sets, Player-Routen und ggf. personenbezogenen oder pseudonymisierten Materialien.

Für Teaching gilt dagegen:

- Teaching ist öffentlich.
- Teaching verwendet keine Auth-Schranke.
- Teaching verwendet keine owner-gebundenen Sets.
- Teaching verwendet keine geschützten Research-Datenpfade.
- Teaching verwendet keine produktiven Research-Player-Routen.
- Teaching-Medien liegen öffentlich unter `/public/teaching/...`.
- Teaching-Content liegt dateibasiert im Repository unter `/content/teaching/...`.

## Zielbild in einem Satz

PROMAT erhält unter `/{ui_lang}/teaching/{teaching_lang}` einen öffentlichen, dateibasierten, sprach- und editionsfähigen Teaching-Bereich mit Card-Hubs, flexiblen Themenseiten, öffentlichen Medien und einem schlanken Renderer für didaktische Einzelbeispiele.

## Verbindliche Routing-Struktur

Die kanonische Route-Struktur lautet:

```text
/{ui_lang}/teaching
/{ui_lang}/teaching/{teaching_lang}
/{ui_lang}/teaching/{teaching_lang}/{topic_slug}
````

Beispiele:

```text
/de/teaching
/de/teaching/spanish
/de/teaching/spanish/final-r

/en/teaching/spanish
/en/teaching/spanish/final-r

/es/teaching/spanish
/es/teaching/spanish/r-final-ele
```

Dabei gilt:

* `ui_lang` bezeichnet die Sprache bzw. didaktische Edition der Seite.
* `teaching_lang` bezeichnet die unterrichtete Sprache.
* `topic_slug` bezeichnet eine konkrete Themenseite innerhalb einer Teaching-Edition.

Beispiel:

```text
/de/teaching/spanish/final-r
```

bedeutet:

* deutschsprachige bzw. deutschdidaktische Teaching-Edition,
* zur unterrichteten Sprache Spanisch,
* Themenseite `final-r`.

## Unterstützte Teaching-Sprachen

Der Rohbau soll technisch auf folgende unterrichtete Sprachen vorbereitet werden:

```text
spanish
english
french
german
```

Nicht alle Teaching-Sprachen müssen im ersten Run vollständig befüllt sein.

Die Architektur muss erlauben:

* nur eine befüllte Edition pro Teaching-Sprache,
* mehrere befüllte Editionen pro Teaching-Sprache,
* unterschiedliche Themen je Edition,
* unterschiedliche Reihenfolge je Edition,
* unterschiedliche didaktische Ausgestaltung je Edition,
* fehlende Editionen ohne Fehlerzustand,
* fehlende Themenseiten ohne kaputte Links.

## UI-Sprache vs. Teaching-Sprache

Es wird strikt getrennt zwischen:

```text
ui_lang = Sprache / Edition der Seite
teaching_lang = unterrichtete Sprache
```

Beispiele:

```text
/de/teaching/spanish
```

Deutschsprachige oder deutschdidaktische Materialien zum Spanischunterricht.

```text
/en/teaching/spanish
```

Englischsprachige oder internationalere Materialien zum Spanischunterricht.

```text
/es/teaching/spanish
```

Spanischsprachige bzw. ELE-orientierte Materialien zur spanischen Aussprache.

Diese Versionen sind nicht zwingend reine Übersetzungen derselben Inhalte. Sie können eigenständige didaktische Editionen sein.

## Editionen statt reine Übersetzungen

Teaching-Seiten werden nicht als zwingend deckungsgleiche Übersetzungen modelliert.

Stattdessen gilt:

Eine Kombination aus `teaching_lang` und `ui_lang` ist eine Teaching-Edition.

Beispiel:

```text
spanish/de = deutschsprachige Unterrichtsperspektive
spanish/en = internationale englischsprachige Perspektive
spanish/es = ELE-/spanischsprachige Perspektive
```

Jede Edition kann eigene Themen, eigene Titel, eigene Reihenfolge, eigene Beispiele und eigene didaktische Akzente haben.

Es muss möglich sein, dass eine Themenseite nur in einer Edition existiert.

Beispiel:

```text
/de/teaching/spanish/final-r
```

existiert, aber:

```text
/en/teaching/spanish/final-r
```

existiert nicht.

Ebenso kann eine ELE-Version eigene Themen enthalten, die in der deutschen Edition nicht vorkommen.

## Teaching-Übersicht

Die Route:

```text
/{ui_lang}/teaching
```

ist die allgemeine Teaching-Übersicht.

Sie kann im Rohbau einfach gehalten werden und auf verfügbare Teaching-Sprachen verweisen.

Beispielhafte Cards:

```text
Spanisch
Englisch
Französisch
Deutsch
```

Die Seite soll nur Teaching-Sprachen anzeigen, die in der jeweiligen oder einer sinnvoll fallbackbaren Edition verfügbar sind.

Wenn im ersten Rohbau nur Spanisch befüllt ist, darf die Übersicht entsprechend nur Spanisch prominent anzeigen oder andere Sprachen als geplant, aber noch nicht verfügbar markieren. Für den ersten produktiven Stand ist eine reduzierte Anzeige befüllter Sprachen vorzuziehen.

## Sprach-Hub

Die Route:

```text
/{ui_lang}/teaching/{teaching_lang}
```

ist der Hub einer konkreten Teaching-Edition.

Beispiel:

```text
/de/teaching/spanish
```

Diese Seite dient als thematischer Einstieg.

Der Hub soll nicht wie Research oder Projekt mit einer dauerhaften linken Seitennavigation arbeiten, sondern über ein Card-Grid auf Themenseiten führen.

Beispielhafte Themen für Spanisch:

```text
Welche Aussprache unterrichten?
Weiches Spanisch vs. hartes Deutsch
Das R
Das R im Auslaut
Vokale
Betonung und Rhythmus
```

Die Themenliste wird pro Edition aus dem jeweiligen `index.yaml` gelesen.

## Themenseiten

Die Route:

```text
/{ui_lang}/teaching/{teaching_lang}/{topic_slug}
```

rendert eine einzelne Themenseite.

Themenseiten sollen keine permanente Sidebar-Navigation erzwingen.

Stattdessen sollen sie enthalten können:

* Breadcrumb oder Rücklink zum Sprach-Hub,
* Titelbereich,
* flexible Content-Blöcke,
* optionale Medien,
* optionale Infokästen,
* optionale Audio-Beispiele,
* optionale Downloads,
* Credits,
* optionale Links zu weiteren Themen.

Beispielstruktur:

```text
← Spanisch unterrichten

Das R im Auslaut

[Einführungstext]

[Audiovergleich]

[Infokasten]

[Bild / Artikulationsschema]

[Weitere Themen]
```

## Navigationsprinzip

Teaching folgt dem Prinzip:

```text
Teaching-Übersicht → Sprach-Hub → Themenseite → weitere Themen / zurück zum Hub
```

Es wird bewusst keine dauerhafte Seitennavigation wie in Projekt oder Research vorgeschrieben.

Begründung:

* Teaching ist stärker thematisch und didaktisch.
* Nutzer:innen kommen häufig über kleine Bildschirme, Tablets, Smartphones oder Schulgeräte.
* Einzelne Themen sollen eigenständig konsumierbar sein.
* Kreativere Seitenlayouts sollen möglich bleiben.
* Der Bereich soll weniger nach App-Workbench und mehr nach Lehrmaterialsammlung wirken.

## Responsive Grundregel

Alle Teaching-Seiten müssen mobile-first funktionieren.

Desktop darf stärkere Grid- und Zwei-Spalten-Kompositionen erlauben, aber kein Inhalt darf nur im Nebeneinander verständlich sein.

Grundregel:

```text
mobile: 1 Spalte
tablet: 1–2 Spalten
desktop: 2–3 Spalten, je nach Blocktyp
```

Auf kleinen Bildschirmen müssen alle Layouts in eine klare vertikale Lesestruktur fallen.

Beispiel Desktop:

```text
Intro links | Beispielkarte rechts
Textblock | Audio-Beispiel
Infokasten | Bild
3er-Cardgrid
```

Beispiel Mobile:

```text
Titel
Lead
Text
Audio
Infokasten
Bild
Weitere Beispiele
```

## Content-Ablage

Teaching-Content liegt nicht unter `/public`.

Verbindliche Struktur:

```text
content/teaching/...
```

Beispiel:

```text
content/teaching/spanish/teaching.yaml
content/teaching/spanish/de/index.yaml
content/teaching/spanish/de/topics/final-r.yaml
content/teaching/spanish/en/index.yaml
content/teaching/spanish/en/topics/final-r.yaml
content/teaching/spanish/es/index.yaml
content/teaching/spanish/es/topics/r-final-ele.yaml
```

Der Ordner `content/` liegt im Repository und wird mit Git versioniert.

## Warum Content nicht unter `/public` liegt

`/public` wird direkt statisch ausgeliefert. Alles dort ist roh abrufbar.

Das ist für öffentliche Medien richtig, aber nicht für strukturierte Content-Quellen.

Content-Dateien sollen:

* versioniert werden,
* reviewbar sein,
* im Deployment reproduzierbar sein,
* nicht roh als YAML/Markdown-Quellen öffentlich angeboten werden,
* nicht über eine Admin-Oberfläche verändert werden.

Darum:

```text
content/teaching/... = redaktionelle Quellen und Seitenstruktur
public/teaching/... = öffentliche Medien und Downloads
```

## Public-Media-Struktur

Öffentliche Teaching-Medien liegen unter:

```text
public/teaching/{teaching_lang}/...
```

Pro Teaching-Sprache sollen mindestens folgende Unterordner vorgesehen werden:

```text
public/teaching/{teaching_lang}/audio/
public/teaching/{teaching_lang}/images/
public/teaching/{teaching_lang}/video/
public/teaching/{teaching_lang}/downloads/
```

Beispiel:

```text
public/teaching/spanish/audio/
public/teaching/spanish/images/
public/teaching/spanish/video/
public/teaching/spanish/downloads/
```

Diese Struktur ist besser als:

```text
public/spanish/
```

weil der Namespace eindeutig macht, dass es sich um öffentliche Teaching-Medien handelt.

## Erlaubte öffentliche Medien

Teaching kann folgende öffentliche Assets verwenden:

* Audio-Dateien,
* Abbildungen,
* Illustrationen,
* Artikulationsschemata,
* Videos,
* PDFs,
* Arbeitsblätter,
* Downloadmaterialien.

Alle diese Medien müssen so ausgewählt sein, dass sie öffentlich auslieferbar sind.

Es dürfen keine geschützten Research-Medien versehentlich in `/public/teaching` gespiegelt werden, wenn dafür keine öffentliche Freigabe besteht.

## Content-Manifeste

Jede Teaching-Sprache erhält ein zentrales Manifest:

```text
content/teaching/{teaching_lang}/teaching.yaml
```

Beispiel:

```yaml
teaching_lang: spanish
default_ui_lang: de
available_ui_langs:
  - de
  - en
  - es
```

Dieses Manifest beschreibt die verfügbaren Editionen einer Teaching-Sprache.

Es legt nicht fest, dass alle Editionen dieselben Themen haben.

## Hub-Dateien

Jede Edition erhält ein eigenes Hub-File:

```text
content/teaching/{teaching_lang}/{ui_lang}/index.yaml
```

Beispiel:

```text
content/teaching/spanish/de/index.yaml
content/teaching/spanish/en/index.yaml
content/teaching/spanish/es/index.yaml
```

Darin stehen nur die Themen, die in dieser Edition angeboten werden.

Beispiel deutschsprachige Edition:

```yaml
title: Spanisch unterrichten
lead: Materialien zur spanischen Aussprache im deutschsprachigen Unterricht.
topics:
  - slug: which-pronunciation
    title: Welche Aussprache unterrichten?
    summary: Orientierung zwischen Standard, Variation und Unterrichtspragmatik.
    level: Grundlagen

  - slug: soft-spanish-hard-german
    title: Weiches Spanisch vs. hartes Deutsch
    summary: Warum spanische Aussprache oft weniger gespannt und weniger segmentiert wirkt.
    level: Kontrast

  - slug: r
    title: Das R
    summary: Artikulation, Variation und typische Lernendenschwierigkeiten.
    level: Laut

  - slug: final-r
    title: Das R im Auslaut
    summary: Warum End-r im Spanischen anders behandelt werden muss als im Deutschen.
    level: Beispiel
```

Beispiel ELE-orientierte Edition:

```yaml
title: Pronunciación para ELE
lead: Materiales sobre pronunciación española para contextos internacionales.
topics:
  - slug: variedades
    title: Variedades del español
    summary: Orientación sobre variación y modelos de pronunciación.

  - slug: seseo-yeismo
    title: Seseo y yeísmo
    summary: Fenómenos relevantes para la enseñanza de la pronunciación.

  - slug: r-final-ele
    title: La r final
    summary: Ejemplos y orientaciones para trabajar la r final.
```

Die Listen dürfen unterschiedlich sein.

## Topic-Dateien

Jede Themenseite liegt als eigenes File unter:

```text
content/teaching/{teaching_lang}/{ui_lang}/topics/{topic_slug}.yaml
```

Beispiele:

```text
content/teaching/spanish/de/topics/final-r.yaml
content/teaching/spanish/en/topics/final-r.yaml
content/teaching/spanish/es/topics/r-final-ele.yaml
```

Der gleiche Slug in mehreren Editionen bedeutet standardmäßig: Diese Seiten sind Entsprechungen.

Beispiel:

```text
de/topics/final-r.yaml
en/topics/final-r.yaml
```

können über den Sprachswitch direkt verbunden werden.

Wenn Entsprechungen unterschiedliche Slugs haben, kann optional ein explizites Mapping verwendet werden.

Beispiel:

```yaml
slug: final-r
equivalents:
  en: r-final
  es: r-final-ele
```

## Topic-Datei: Grundstruktur

Eine Themenseite besteht aus Metadaten und einer flexiblen Blockliste.

Beispiel:

```yaml
title: Das R im Auslaut
description: Warum das spanische r am Wortende für deutschsprachige Lernende schwierig ist.

credits:
  coordinator:
    - name: "Max Mustermann"
      affiliation: "Universität Marburg"
      role: "Koordination"
      url: "https://example.org"
      orcid: "0000-0000-0000-0000"
  authors:
    - name: "Erika Beispiel"
    - name: "Juan Pérez"
      affiliation: "Universidad de Salamanca"

blocks:
  - type: hero
    eyebrow: Spanische Aussprache
    title: Das R im Auslaut
    lead: Im Spanischen bleibt r am Wortende hörbar und leicht artikuliert.

  - type: text
    body: |
      Deutschsprachige Lernende neigen dazu, das r im Auslaut zu vokalisieren oder stark zu reduzieren.

  - type: audio_contrast
    title: Hörvergleich
    examples:
      - label: Spanisches Zielbeispiel
        audio: /teaching/spanish/audio/r/final-r-model.mp3
        transcript: "hablar"
        segments:
          - text: "ha"
          - text: "blar"
      - label: Typische deutsche Annäherung
        audio: /teaching/spanish/audio/r/final-r-learner.mp3
        transcript: "hablar"
        segments:
          - text: "ha"
          - text: "bla"

  - type: tip_box
    title: Unterrichtsimpuls
    body: Das r nicht übertreiben, aber auch nicht verschwinden lassen.

  - type: credits

  - type: next_topics
    topics:
      - r
      - soft-spanish-hard-german
```

## Blockmodell

Themenseiten werden nicht als starre Templates umgesetzt.

Stattdessen besteht jede Seite aus einer freien Sequenz erlaubter Blöcke.

Start-Blocktypen für den Rohbau:

```text
hero
text
rich_text
image
info_box
tip_box
warning_box
audio_example
audio_contrast
topic_grid
download
video
credits
next_topics
```

Nicht alle Blocktypen müssen im ersten Run visuell final ausgebaut sein. Sie sollen aber als strukturierte Grundlage vorgesehen werden.

## Blocktyp: hero

Zweck:

* Einstieg in eine Themenseite,
* Titel,
* kurzer Lead,
* optionaler Eyebrow/Kategorietext.

Beispiel:

```yaml
- type: hero
  eyebrow: Spanische Aussprache
  title: Das R im Auslaut
  lead: Im Spanischen bleibt r am Wortende hörbar und leicht artikuliert.
```

## Blocktyp: text

Zweck:

* einfacher Fließtext,
* kurze Absätze,
* unkomplizierte Erläuterungen.

Beispiel:

```yaml
- type: text
  body: |
    Deutschsprachige Lernende neigen dazu, das r im Auslaut zu vokalisieren.
```

## Blocktyp: rich_text

Zweck:

* längere Inhalte mit Markdown-ähnlicher Struktur,
* Zwischenüberschriften,
* Listen,
* Hervorhebungen,
* Links.

Beispiel:

```yaml
- type: rich_text
  body: |
    ## Worauf kommt es an?

    Das spanische r im Auslaut wird nicht wie im Deutschen vokalisiert.
    Wichtig ist eine leichte, aber hörbare Artikulation.
```

## Blocktyp: image

Zweck:

* Abbildungen,
* Illustrationen,
* Artikulationsschemata,
* Fotos,
* erklärende Grafiken.

Beispiel:

```yaml
- type: image
  src: /teaching/spanish/images/r/articulation-r.png
  alt: Artikulationsschema für das spanische r
  caption: Vereinfachte Darstellung der Artikulation.
```

Rendering-Regeln:

* `alt` ist verpflichtend oder wird im Validator als Warnung markiert.
* `caption` ist optional.
* Wenn `caption` fehlt, wird kein leerer Caption-Bereich gerendert.

## Blocktyp: info_box

Zweck:

* neutrale Zusatzinformation,
* Hintergrund,
* fachliche Einordnung.

Beispiel:

```yaml
- type: info_box
  title: Hinweis
  body: Das spanische r kann regional unterschiedlich realisiert werden.
```

## Blocktyp: tip_box

Zweck:

* Unterrichtsimpuls,
* didaktische Empfehlung,
* praktische Handlungsanweisung.

Beispiel:

```yaml
- type: tip_box
  title: Unterrichtsimpuls
  body: Lassen Sie Lernende zunächst zwischen hörbarem und vokalisiertem Auslaut-r unterscheiden.
```

## Blocktyp: warning_box

Zweck:

* Warnung vor typischen Missverständnissen,
* didaktische Vorsicht,
* klare Abgrenzung.

Beispiel:

```yaml
- type: warning_box
  title: Nicht übertreiben
  body: Das r soll hörbar sein, aber nicht künstlich stark gerollt werden.
```

## Blocktyp: audio_example

Zweck:

* einzelnes Audio-Beispiel,
* optional mit Transkript,
* optional mit Segmenten zur Markierung.

Beispiel:

```yaml
- type: audio_example
  title: Beispiel
  label: Zielaussprache
  audio: /teaching/spanish/audio/r/final-r-model.mp3
  transcript: "hablar"
  segments:
    - text: "ha"
    - text: "blar"
```

Rendering-Ziel:

* kompakter öffentlicher Audio-Player,
* keine Research-Session,
* keine Set-Logik,
* keine Auth,
* optional segmentierte Anzeige.

## Blocktyp: audio_contrast

Zweck:

* Vergleich weniger vorausgewählter Audio-Beispiele,
* z. B. Zielbeispiel vs. typische Lernendenannäherung,
* maximal einfache didaktische Kontraste.

Beispiel:

```yaml
- type: audio_contrast
  title: Hörvergleich
  examples:
    - label: Spanisches Zielbeispiel
      audio: /teaching/spanish/audio/r/final-r-model.mp3
      transcript: "hablar"
      segments:
        - text: "ha"
        - text: "blar"

    - label: Typische deutsche Annäherung
      audio: /teaching/spanish/audio/r/final-r-learner.mp3
      transcript: "hablar"
      segments:
        - text: "ha"
        - text: "bla"
```

Optional kann später eine Dropdown- oder Klickauswahl ergänzt werden.

Für den Rohbau reicht:

* mehrere Beispielkarten,
* jeweils eigener Play-Button,
* optional segmentierte Anzeige.

## Blocktyp: topic_grid

Zweck:

* interne thematische Verweise,
* kleine Card-Gruppen innerhalb einer Themenseite.

Beispiel:

```yaml
- type: topic_grid
  title: Verwandte Themen
  topics:
    - r
    - final-r
    - soft-spanish-hard-german
```

Die Topics werden über die aktuelle Edition aufgelöst.

Fehlende Topics dürfen nicht als kaputte Links gerendert werden.

## Blocktyp: download

Zweck:

* PDF,
* Arbeitsblatt,
* Handreichung,
* Zusatzmaterial.

Beispiel:

```yaml
- type: download
  title: Arbeitsblatt
  description: Kurze Übung zum r im Auslaut.
  file: /teaching/spanish/downloads/r/final-r-worksheet.pdf
  label: PDF herunterladen
```

Rendering-Regeln:

* `file` muss auf `/teaching/{teaching_lang}/downloads/...` zeigen.
* `description` ist optional.
* `label` hat einen Default, falls nicht gesetzt.

## Blocktyp: video

Zweck:

* öffentliches Video,
* eingebettetes oder lokal bereitgestelltes Lehrvideo.

Beispiel:

```yaml
- type: video
  title: Artikulation des r
  src: /teaching/spanish/video/r/articulation-r.mp4
  caption: Kurzes Demonstrationsvideo.
```

Video muss im Rohbau noch nicht priorisiert werden. Die Struktur soll aber vorgesehen sein.

## Blocktyp: credits

Zweck:

* Anzeige von Koordination und Autorenschaft.

Credits können entweder als eigenes Blockelement gerendert werden oder aus den Seitenmetadaten stammen.

Empfohlen:

```yaml
credits:
  coordinator:
    - name: "Max Mustermann"
      affiliation: "Universität Marburg"
      role: "Koordination"
      url: "https://example.org"
      orcid: "0000-0000-0000-0000"
  authors:
    - name: "Erika Beispiel"
    - name: "Juan Pérez"
      affiliation: "Universidad de Salamanca"

blocks:
  - type: credits
```

Rendering-Regeln:

* Wenn `coordinator` Personen enthält, wird die Gruppe `Koordinator:in` angezeigt.
* Wenn `authors` Personen enthält, wird die Gruppe `Autor:innen` angezeigt.
* Wenn eine Gruppe leer ist, wird sie nicht angezeigt.
* Wenn beide Gruppen leer sind, wird der gesamte Credits-Block nicht gerendert.
* Nur vorhandene Felder werden dargestellt.
* Fehlende Felder erzeugen keine sichtbaren Leerstellen oder Labels.

Personenfelder:

```yaml
name: "Erika Beispiel"
affiliation: "Universität Marburg"
role: "Autorin"
url: "https://example.org"
orcid: "0000-0000-0000-0000"
```

Pflichtfeld:

```text
name
```

Optionale Felder:

```text
affiliation
role
url
orcid
```

Wenn nur ein Name vorhanden ist, soll die Ausgabe trotzdem vollständig und sauber wirken.

Beispiel minimal:

```yaml
credits:
  authors:
    - name: "Erika Beispiel"
```

Ausgabe:

```text
Autor:innen
Erika Beispiel
```

Keine leeren Zeilen wie `Institution:` oder `ORCID:`.

## Blocktyp: next_topics

Zweck:

* Navigation am Ende einer Themenseite,
* Hinweise auf thematisch anschließende Seiten.

Beispiel:

```yaml
- type: next_topics
  title: Weitere Themen
  topics:
    - r
    - soft-spanish-hard-german
```

Rendering-Regeln:

* Nur Topics rendern, die in der aktuellen Edition existieren.
* Fehlende Topics ignorieren oder als Validator-Warnung melden.
* Kein kaputter Link.

## Teaching-Player / Audio-Renderer

Teaching erhält keinen vollständigen Research-Player.

Stattdessen wird ein schlanker öffentlicher Audio-/Beispielrenderer gebaut.

Dieser darf konzeptionell einzelne Ideen aus dem Research-Textplayer übernehmen, insbesondere:

* segmentierte Anzeige,
* Wort-für-Wort- oder Segment-Markierung,
* Transkriptanzeige,
* einfache Audio-Synchronisierung, falls später verfügbar.

Er darf aber nicht übernehmen:

* Research-Session-Kontext,
* Set-Auflösung,
* Compare-Architektur,
* owner-gebundene Daten,
* Auth-Abhängigkeit,
* geschützte Datenpfade,
* komplexe Player-Routen.

Der Teaching-Renderer ist für statisch ausgewählte Einzelbeispiele gedacht.

Er soll unterstützen:

* einzelnes Beispiel,
* zwei oder drei kontrastierende Beispiele,
* optionale Dropdown- oder Klickauswahl,
* optionale Segmentmarkierung,
* optionales Transkript.

Er muss nicht unterstützen:

* ganze Listen,
* Session-Navigation,
* Sets,
* Research-Compare,
* User-State,
* gespeicherte Auswahl,
* geschützte Audiodaten.

## Segmentmodell für Audio-Beispiele

Für den Rohbau reicht eine einfache Segmentstruktur.

Beispiel:

```yaml
transcript: "hablar"
segments:
  - text: "ha"
  - text: "blar"
```

Optional später erweiterbar:

```yaml
segments:
  - text: "ha"
    start: 0.0
    end: 0.3
  - text: "blar"
    start: 0.3
    end: 0.8
```

Im ersten Rohbau muss keine echte zeitbasierte Synchronisierung umgesetzt werden. Eine visuelle Segmentanzeige reicht.

Wenn später Zeitmarken ergänzt werden, kann der Renderer zur aktiven Hervorhebung ausgebaut werden.

## Sprachswitch

Der allgemeine App-Sprachswitch bleibt außerhalb von Teaching auf die globalen App-Sprachen beschränkt.

Regel außerhalb Teaching:

```text
DE | EN
```

Innerhalb von Teaching wird der Sprachswitch kontextsensitiv erweitert.

Regel innerhalb Teaching:

```text
Zeige alle UI-Sprachen, die für die jeweilige Teaching-Sprache verfügbar sind.
```

Beispiel Manifest:

```yaml
teaching_lang: spanish
default_ui_lang: de
available_ui_langs:
  - de
  - en
  - es
```

Dann zeigt der Sprachswitch innerhalb von:

```text
/de/teaching/spanish
```

die Optionen:

```text
DE | EN | ES
```

Diese zusätzlichen Sprachen sind keine globalen App-Sprachen. Sie gelten nur für diese Teaching-Edition.

## Sprachswitch auf Hub-Seiten

Auf einer Hub-Seite wie:

```text
/de/teaching/spanish
```

prüft der Switch:

```text
Gibt es für spanish eine Edition in der Ziel-UI-Sprache?
```

Wenn ja, verlinkt er auf:

```text
/en/teaching/spanish
/es/teaching/spanish
```

Wenn nein, wird die Option nicht angezeigt oder deaktiviert.

## Sprachswitch auf Themenseiten

Auf einer Themenseite wie:

```text
/de/teaching/spanish/final-r
```

prüft der Switch pro Ziel-UI-Sprache:

1. Gibt es eine explizite Entsprechung über `equivalents`?
2. Gibt es denselben Slug in der Ziel-Edition?
3. Gibt es zumindest den Hub der Ziel-Edition?
4. Gibt es die Ziel-Edition gar nicht?

Daraus folgt:

### Fall A: gleiche Themenseite existiert

```text
/de/teaching/spanish/final-r
```

und:

```text
/en/teaching/spanish/final-r
```

existiert.

Dann verlinkt `EN` direkt auf:

```text
/en/teaching/spanish/final-r
```

### Fall B: explizite Entsprechung existiert

Deutsche Seite:

```yaml
slug: final-r
equivalents:
  es: r-final-ele
```

Dann verlinkt `ES` auf:

```text
/es/teaching/spanish/r-final-ele
```

### Fall C: Ziel-Edition existiert, aber keine Entsprechung der Themenseite

Dann verlinkt der Switch auf den Hub der Ziel-Edition:

```text
/en/teaching/spanish
```

Das bedeutet: Wechsel zur englischen Teaching-Edition, nicht zur identischen Seite.

### Fall D: Ziel-Edition existiert nicht

Dann wird die Sprachoption nicht angezeigt oder deaktiviert.

## Fallback-Regeln

Wenn eine Hub-Route für eine nicht verfügbare UI-Sprache aufgerufen wird:

```text
/en/teaching/french
```

aber nur Deutsch existiert, soll auf die Default-Edition geleitet werden:

```text
/de/teaching/french
```

Wenn eine Themenseite in der Ziel-UI-Sprache nicht existiert, aber derselbe Slug in der Default-Edition existiert, kann auf diese Default-Seite weitergeleitet werden.

Beispiel:

```text
/en/teaching/spanish/final-r
```

existiert nicht, aber:

```text
/de/teaching/spanish/final-r
```

existiert.

Dann ist eine Weiterleitung auf die Default-Seite zulässig.

Wenn der Slug gar nicht existiert, soll keine kaputte Seite gerendert werden. Zulässig sind:

* 404,
* oder Rückleitung auf den Hub der aktuellen bzw. defaultbaren Edition.

Für den Rohbau ist eine klare 404 oder Hub-Rückleitung ausreichend.

## Keine automatische Themenmischung zwischen Editionen

Wenn eine Edition existiert, zeigt ihr Hub nur ihre eigenen Topics.

Beispiel:

```text
/es/teaching/spanish
```

soll nicht automatisch deutsche Themen aus:

```text
/de/teaching/spanish
```

übernehmen.

Grund:

Editionen sind didaktisch eigenständig. Automatisches Mischen würde inkonsistente Hubs erzeugen.

Fallback ist nur für ganze fehlende Editionen oder direkte fehlende Routen sinnvoll, nicht für das automatische Auffüllen einzelner Topic-Listen.

## Card-Hub-Design im Rohbau

Der Sprach-Hub verwendet ein Card-Grid.

Cards sollen mindestens unterstützen:

```yaml
slug: final-r
title: Das R im Auslaut
summary: Warum End-r im Spanischen anders behandelt werden muss als im Deutschen.
level: Beispiel
```

Optionale spätere Felder:

```yaml
category: Laut
image: /teaching/spanish/images/cards/final-r.png
tags:
  - Aussprache
  - R
  - Deutsch-Spanisch
credits:
  authors:
    - name: "Erika Beispiel"
```

Für den Rohbau reichen:

* Titel,
* Summary,
* optional Level oder Kategorie,
* Link zur Themenseite.

Credits auf Cards sind optional. Vollständige Credits gehören primär auf die Themenseite.

## Kein Admin-Editor

Es wird keine Admin-Schreiboberfläche für Teaching-Content gebaut.

Teaching-Content wird dateibasiert gepflegt und über Git versioniert.

Begründung:

* stabiler,
* reviewbar,
* weniger fehleranfällig,
* keine Schreibrechte der App auf Projektdateien nötig,
* keine CMS-Komplexität,
* keine Gefahr beschädigter YAML-Strukturen durch eine Weboberfläche.

Ein späterer Validator oder eine Preview-Ansicht kann sinnvoll sein, aber keine Schreiboberfläche.

## Optional später: Validator oder Preview

Nicht Teil des ersten Rohbaus, aber sinnvoll als spätere Ergänzung:

* Admin-/Dev-Ansicht aller Teaching-Seiten,
* Anzeige der zugrunde liegenden Content-Datei,
* Prüfung unbekannter Blocktypen,
* Warnung bei fehlenden Medien,
* Warnung bei fehlenden Alt-Texten,
* Warnung bei kaputten Topic-Links,
* Warnung bei nicht auflösbaren Sprachswitch-Entsprechungen,
* Warnung bei Credits ohne Namen.

Diese Funktion wäre deutlich risikoärmer als ein Editor.

## Umsetzung im ersten Run

Der erste Run soll den Rohbau liefern, nicht das finale Teaching-Design.

Umfang:

```text
1. Top-Level content/teaching-Struktur anlegen
2. public/teaching-Medienstruktur anlegen
3. Teaching-Routen einführen
4. Content-Loader für Teaching-Manifeste, Hubs und Topics bauen
5. Verfügbarkeitslogik für Editionen bauen
6. Kontextsensitiven Sprachswitch für Teaching einführen
7. Hub-Seite mit Card-Grid bauen
8. Themenseiten-Renderer mit Blockliste bauen
9. Start-Blocktypen implementieren
10. Schlanken Audio-Beispielrenderer bauen
11. Credits-Modell implementieren
12. Beispielcontent für Spanisch/de anlegen
13. Optional eine zweite Edition als Smoke-Test anlegen
14. Keine Admin-Schreiboberfläche bauen
```

## Minimaler Beispielcontent für den Rohbau

Für Spanisch/de sollen initial 3–4 Topics angelegt werden.

Beispiel:

```text
content/teaching/spanish/de/topics/which-pronunciation.yaml
content/teaching/spanish/de/topics/soft-spanish-hard-german.yaml
content/teaching/spanish/de/topics/r.yaml
content/teaching/spanish/de/topics/final-r.yaml
```

Der Hub:

```text
content/teaching/spanish/de/index.yaml
```

verweist auf diese Topics.

Mindestens eine Themenseite soll mehrere Blocktypen testen:

* hero,
* text oder rich_text,
* audio_example oder audio_contrast,
* info_box oder tip_box,
* credits,
* next_topics.

## Optionaler Smoke-Test für zweite Edition

Um den Sprachswitch früh zu testen, kann eine sehr kleine zweite Edition angelegt werden.

Beispiel:

```text
content/teaching/spanish/en/index.yaml
content/teaching/spanish/en/topics/final-r.yaml
```

oder:

```text
content/teaching/spanish/es/index.yaml
content/teaching/spanish/es/topics/r-final-ele.yaml
```

Diese zweite Edition muss nicht inhaltlich final sein. Sie dient nur zur Prüfung:

* kontextsensitiver Sprachswitch,
* direkte Entsprechung,
* Hub-Fallback,
* unterschiedliche Topic-Listen.

## Akzeptanzkriterien

Der Teaching-Rohbau gilt als gelungen, wenn folgende Punkte erfüllt sind:

### Routing

* `/de/teaching` ist öffentlich erreichbar.
* `/de/teaching/spanish` ist öffentlich erreichbar.
* `/de/teaching/spanish/{topic_slug}` ist öffentlich erreichbar.
* Teaching liegt nicht unter Research.
* Teaching nutzt keine Auth-Schranke.

### Content

* Teaching-Content liegt unter `content/teaching/...`.
* Content-Dateien werden aus Git gelesen.
* Medien liegen unter `public/teaching/...`.
* Content-Dateien liegen nicht unter `/public`.

### Hubs

* Sprach-Hubs rendern ein Card-Grid.
* Die Topics stammen aus dem jeweiligen `index.yaml`.
* Unterschiedliche Editionen können unterschiedliche Topic-Listen haben.
* Fehlende Topics erzeugen keine kaputten Links.

### Themenseiten

* Themenseiten rendern flexible Blöcke.
* Es gibt keine erzwungene linke Seitennavigation.
* Seiten funktionieren mobil in einer vertikalen Struktur.
* Desktop darf Grid-Layouts verwenden.
* Blocktypen können pro Seite frei kombiniert werden.

### Credits

* Credits können Koordinator:innen und Autor:innen anzeigen.
* Nur vorhandene Felder werden gerendert.
* Leere Gruppen werden nicht angezeigt.
* Wenn nur Namen vorhanden sind, wirkt die Ausgabe vollständig.
* Wenn keine Credits vorhanden sind, wird kein leerer Credits-Bereich gerendert.

### Sprachswitch

* Außerhalb Teaching bleibt der Switch bei den globalen App-Sprachen.
* Innerhalb Teaching zeigt der Switch die verfügbaren Editionen der jeweiligen Teaching-Sprache.
* Auf Themenseiten führt der Switch nach Möglichkeit zur entsprechenden Themenseite.
* Wenn keine entsprechende Themenseite existiert, kann er zum Hub der Ziel-Edition führen.
* Nicht verfügbare Editionen werden nicht als kaputte Links angeboten.

### Audio

* Teaching verwendet einen schlanken öffentlichen Audio-Renderer.
* Audio-Dateien kommen aus `/public/teaching/{teaching_lang}/audio/...`.
* Einzelbeispiele und einfache Kontraste sind möglich.
* Keine Research-Sessions, Sets oder Auth-Abhängigkeiten werden verwendet.

### Admin

* Es gibt keinen Admin-Editor.
* Keine Schreiblogik auf Content-Dateien wird eingebaut.

## Was ausdrücklich nicht Teil des ersten Rohbaus ist

Nicht im ersten Run umzusetzen:

* vollständiges CMS,
* Admin-Schreibeditor,
* Medien-Upload,
* komplexe Quiz- oder Übungslogik,
* gespeicherte Nutzerstände,
* vollständiges Teaching-Designsystem,
* finale Gestaltung aller Card-Varianten,
* komplexe Audio-Synchronisierung,
* Video-Feinschliff,
* PDF-Verwaltungslogik,
* automatische Übernahme von Research-Daten,
* Research-Player-Integration.

## Spätere Ausbaustufen

Nach dem Rohbau können schrittweise ergänzt werden:

1. Weitere Blocktypen und Layoutvarianten.
2. Erweiterte Audio-Markierung mit Zeitsegmenten.
3. Video-Blöcke mit besserem Layout.
4. Download-Gruppen und Materialsammlungen.
5. Dev-/Admin-Preview ohne Schreibfunktion.
6. Content-Validator.
7. Weitere Teaching-Sprachen.
8. Weitere UI-Editionen pro Teaching-Sprache.
9. Didaktisch ausgearbeitete Themenpakete.
10. Optional kleine interaktive Übungen ohne Nutzerkonto.

## Schlussformel

Der Teaching-Bereich wird als öffentlicher, dateibasierter und editionsfähiger Content-Bereich aufgebaut.

Die jetzt zu treffenden Entscheidungen betreffen die langfristig relevanten Grundlagen:

```text
Routing
Content-Struktur
Public-Media-Struktur
Editionenmodell
Sprachswitch
Blockrenderer
Credits
Audio-Beispielrenderer
Git-basierte Pflege ohne Admin-Editor
```

Gestalterische Details einzelner Cards, Seitenvarianten und didaktischer Module werden später anhand echter Inhalte iterativ ausgearbeitet.

Damit entsteht ein belastbarer Rohbau, der mobil funktioniert, öffentliche Lehrmaterialien sauber ausliefert und zugleich genug Freiheit für kreativ gestaltete Unterrichtsseiten lässt.
