# Lokaler Teaching-Importbereich

Diese README ist die verbindliche Anleitung fuer zukuenftige lokale Teaching-Importe durch Repo-Agenten oder kleine Repo-Skripte. `content/teaching_import/` ist ein reiner Staging-Bereich im Repository. Er ist kein Server-Upload, keine DB-Pipeline, keine Admin-Oberflaeche und keine Research-Integration.

## Zweck des Ordners

- Neue Teaching-Themenseiten werden zunaechst gesammelt unter `content/teaching_import/<import-topic-folder>/` abgelegt.
- Jeder Unterordner ist genau ein Importpaket fuer ein Thema.
- Der Unterordnername ist nur ein Arbeitsname. Die verbindliche Zielzuordnung kommt ausschliesslich aus den YAML-Metadaten.
- Nach erfolgreicher Integration schreibt der Agent in das bestehende Teaching-Zielmodell unter `content/teaching/...` und darf den verarbeiteten Import-Unterordner entfernen.

## Erlaubte Importstruktur

```text
content/teaching_import/
  README.md
  .gitkeep

  <import-topic-folder>/
    de.yaml
    en.yaml
    es.yaml
    beliebige-medienfiles...
```

Zusaetzlich sind grob sortierte Medienunterordner im Importpaket erlaubt, zum Beispiel `audio/`, `images/`, `video/` oder `downloads/`. Medien duerfen aber auch flach neben den YAML-Dateien liegen.

Fehlende Sprachfassungen sind erlaubt. Ein Importpaket muss nicht gleichzeitig `de.yaml`, `en.yaml` und `es.yaml` enthalten.

## Pflichtfelder pro YAML

Jede Import-YAML muss mindestens diese Felder enthalten:

```yaml
teaching_lang: spanish
topic_slug: which-pronunciation
ui_lang: de

title: ...
description: ...
status: draft
```

Bedeutung der Pflichtfelder:

- `teaching_lang` bestimmt das Ziel unter `content/teaching/{teaching_lang}/`.
- `topic_slug` bestimmt das Ziel unter `content/teaching/{teaching_lang}/{topic_slug}/`.
- `ui_lang` bestimmt die Zieldatei `{ui_lang}.yaml`.
- `title` ist der fachliche Titel dieser Sprachfassung.
- `description` ist die fachliche Kurzbeschreibung dieser Sprachfassung.
- `status` ist der Import-Status dieser Sprachfassung und wird nur uebernommen, wenn die Abbildung ins produktive Modell eindeutig ist.

Empfohlene optionale Felder:

```yaml
card:
  title: ...
  description: ...

credits:
  authors:
    - name: ...

hub:
  group: Grundlagen
  status: draft

blocks:
  ...
```

Zusaetzliche bereits vorhandene produktive Felder wie `summary`, `equivalents`, `metadata`, `citation` oder weitere gueltige Topic-Keys duerfen enthalten sein und muessen vom Agenten unveraendert uebernommen werden, solange sie technisch valide sind.

## Zielstruktur nach erfolgreichem Import

Das verbindliche Zielmodell bleibt:

```text
content/teaching/{teaching_lang}/
  teaching.yaml
  hubs/
    {ui_lang}.yaml

  {topic_slug}/
    {ui_lang}.yaml
    media/
      audio/
      images/
      video/
      downloads/
```

Importe schreiben in diese Zielstruktur:

- Topic-Dateien nach `content/teaching/{teaching_lang}/{topic_slug}/{ui_lang}.yaml`
- lokale Medien nach `content/teaching/{teaching_lang}/{topic_slug}/media/...`
- Hub-Eintraege nur in `content/teaching/{teaching_lang}/hubs/{ui_lang}.yaml`

Es darf keine alte Public-Teaching-Struktur wieder eingefuehrt werden. Es gibt keine Rueckmigration nach `public/teaching/...` und keine Legacy-Fallbacks.

## Hub-Zuordnung

- `teaching_lang` und `topic_slug` muessen innerhalb eines Importpakets konsistent sein.
- Die Hub-Zuordnung erfolgt ueber die YAML-Metadaten, nicht ueber den Import-Unterordnernamen.
- `hub.group` bestimmt die Rubrik innerhalb der Ziel-Hub-Datei.
- `hub.status` oder ein eindeutig ableitbarer Topic-`status` steuern nur Sichtbarkeit bzw. Status des Hub-Eintrags.
- Hub-Dateien steuern nur Rubrik, Reihenfolge, Sichtbarkeit und Status.
- Card-Titel, Card-Beschreibung und Autor:innen kommen aus der Topic-YAML.
- Card-Texte duerfen nicht in Hub-Dateien dupliziert werden.
- Fehlende Sprachfassungen sind erlaubt; Hub-Dateien werden nur fuer die vorhandenen `ui_lang`-Editionen aktualisiert.

Wenn die passende Hub-Datei oder die gewuenschte Hub-Gruppe nicht eindeutig ist, muss der Agent abbrechen oder die Rueckfrage dokumentieren.

## Medienregeln

Erlaubte Medienformate:

Audio:
- `.mp3`
- `.ogg`
- `.wav`

Bilder:
- `.svg`
- `.png`
- `.jpg`
- `.jpeg`
- `.webp`

Video:
- `.mp4`
- `.webm`

Downloads:
- `.pdf`
- `.txt`

Zielmedienordner:

```text
media/audio/
media/images/
media/video/
media/downloads/
```

Import-Medien duerfen im Paket flach oder grob sortiert liegen. Der Agent normalisiert sie beim Import auf die Zielstruktur.

Medienreferenzen in YAML duerfen im Importpaket einfache Dateinamen oder relative Pfade sein, zum Beispiel:

```yaml
audio: casa-seseo.mp3
src: schema.svg
file: arbeitsblatt.pdf
```

Beim Import werden sie auf Zielpfade umgeschrieben, zum Beispiel:

```yaml
audio: media/audio/casa-seseo.mp3
src: media/images/schema.svg
file: media/downloads/arbeitsblatt.pdf
```

Der Agent ordnet Medien anhand ihrer Dateiendung zu. Wenn mehrere Dateien denselben Zielpfad beanspruchen oder Medien keiner YAML eindeutig zuordenbar sind, muss der Agent abbrechen oder die Kollision dokumentieren.

## Leichte technische Korrekturen, die erlaubt sind

Der Agent darf:

- YAML strukturell validieren
- offensichtliche technische Pfadkorrekturen vornehmen
- Medien anhand ihrer Dateiendung einsortieren
- Dateinamen technisch normalisieren
- relative Medienpfade in YAML auf `media/audio/...`, `media/images/...`, `media/video/...`, `media/downloads/...` umschreiben
- `ui_lang` aus dem Dateinamen ergaenzen, wenn eindeutig
- YAML-Key-Reihenfolge vereinheitlichen
- leere optionale Felder entfernen
- Hub-Status aus Topic-Status uebernehmen, wenn eindeutig
- Hub-Eintraege ergaenzen, wenn die YAML eindeutig ist
- verarbeitete Import-Unterordner nach erfolgreicher Integration entfernen
- alle vorgenommenen leichten Korrekturen im Abschlussbericht auflisten

## Wann der Agent abbrechen oder Rueckfragen dokumentieren muss

Der Agent muss abbrechen oder Rueckfragen dokumentieren, wenn mindestens einer dieser Punkte eintritt:

- `teaching_lang` fehlt
- `topic_slug` fehlt
- `ui_lang` fehlt und ist nicht eindeutig bestimmbar
- `title` fehlt
- `description` fehlt
- `status` fehlt
- Medien werden referenziert, sind aber nicht vorhanden
- Medien sind vorhanden, aber keiner YAML eindeutig zuordenbar
- mehrere YAMLs im selben Importpaket widersprechen sich bei `teaching_lang` oder `topic_slug`
- Zielordner oder Ziel-YAML existiert bereits
- bestehende Zielmedien wuerden still ersetzt
- passende Hub-Datei existiert nicht
- gewuenschte Hub-Gruppe existiert nicht und eine Neuanlage ist nicht eindeutig gewuenscht
- neue `ui_lang` wird vom bestehenden Routing nicht unterstuetzt

Aktuell sind die oeffentlichen Routing-Sprachen `de` und `en`. Weitere Teaching-Editionen duerfen nur dann neu eingefuehrt werden, wenn Routing, Spec und produktive Logik im selben Run bewusst erweitert werden; ansonsten ist der Import zu stoppen und zu dokumentieren.

## Was der Agent ausdruecklich nicht darf

Der Agent darf nicht:

- fachliche Inhalte erfinden
- Texte verlaengern, kuerzen, umformulieren oder ergaenzen, ohne zu fragen
- fehlende Beschreibungen selbst schreiben
- fehlende Autor:innen erfinden
- unklare Hub-Gruppen frei waehlen
- bestehende Ziel-YAMLs still ueberschreiben
- bestehende Medien still ersetzen
- DB, Admin-Oberflaeche oder Research-Pipeline einfuehren
- alte Public-Teaching-Struktur wieder einfuehren
- Legacy-Fallbacks einbauen
- Backups im Repo anlegen

## Checks nach jedem Import

Nach jedem erfolgreichen Import muessen mindestens diese Checks laufen:

1. `python scripts/validate_teaching_content.py`
2. `python -m pytest app/tests/test_teaching_content.py -q`
3. betroffene Teaching-Hub- und Topic-Routen lokal im Dev-Server pruefen
4. Diff pruefen, committen und pushen

Wenn Hub-Ausgabe, Karten oder Topic-Rendering sichtbar betroffen sind, soll zusaetzlich ein fokussierter HTML- oder Integrationstest fuer Teaching mitlaufen.

## Minimalprompt fuer einen Repo-Agenten

```text
Bitte importiere alle neuen Teaching-Themenseiten aus `content/teaching_import/`.
Lies zuerst `content/teaching_import/README.md` und befolge sie verbindlich.
Verarbeite jeden Unterordner als Importpaket.
Validiere YAMLs, ordne Medien zu, schreibe in das Teaching-Zielmodell, aktualisiere Hubs nur fuer Rubrik/Reihenfolge/Status, fuehre Validator und Teaching-Tests aus.
Erfinde keine Inhalte und dokumentiere alle Korrekturen, Konflikte und offenen Fragen.
```