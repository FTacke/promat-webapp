---
tags: promat, research, recordings, speakers
---

# PROMAT Research Pages: Recordings und Speakers

## Zweck

Dieses Dokument beschreibt den aktuell gültigen Stand der PROMAT-Forschungsseiten `recordings`, `speakers`, Profilseite und Player-Stub für den spanischen Dev-Stand. Es ersetzt ältere, widersprüchliche Zwischenstände.

## Aktive Datenquelle

- Die Research-Webapp liest Sessions direkt aus `data/sessions/spanish/{session_id}/metadata.json`.
- Es gibt aktuell keine separate Research-Metadatentabelle als zweite Laufzeitquelle.
- Mehrere Sessions derselben Person werden über `person_id` zusammengeführt.

## Recordings

- `recordings` ist der task-basierte Zugang.
- Die sichtbaren kurzen Task-Namen sind `Wortliste`, `Text` und `Interview`.
- Die längeren Beschreibungstexte sind fest eingefroren:

| Task | Beschreibung |
| --- | --- |
| Wortliste | Isolierte Aussprache über das Vorlesen einer Wortliste. |
| Text | Zusammenhängende Aussprache über das Vorlesen eines Textes oder einer Satzliste. |
| Interview | Reflexion über Aussprache im Interview. |

- Die Ergebnissicht bleibt tabellarisch, kompakt, ruhig und sans-orientiert.
- Die Aktionsspalte ist task-abhängig und benennt direkt die aktuell gewählte Aufzeichnung.
- Verfügbarkeit wird aus den dokumentierten `tasks` der Session abgeleitet.
- Native-Speaker-Sessions bieten keinen Interview-Zugang.

## Speakers und Profilseite

- `speakers` ist der person-basierte Zugang.
- Karten bleiben kompakt und führen entweder ins Profil oder direkt in verfügbare Aufzeichnungen.
- Der Footer-Bereich der Karten heißt `Aufzeichnungen`.

### Profilsemantik

- Die Session-Box heißt `Ausgewählte Session`.
- Das technische Feld `context` bleibt intern, wird aber nicht sichtbar als `baseline` oder `follow_up` ausgegeben.
- `recorded_by` wird sichtbar als `Explorator:in` gezeigt.

### Sprachbiographie für Lernende

Die Lernenden-Profile zeigen in `Sprachbiographie`:

- `Level (Selbsteinschätzung)`
- `L1`
- `L1 der Mutter`
- `L1 des Vaters`
- `Zusätzliche Sprachen`
- `Geschlecht`
- `Geburtsjahr`
- `Aktuelle Region`
- `Region Kindheit`
- `Sprachaufenthalte`

`Sprachaufenthalte` priorisiert detaillierte `exposure_entries`. Sichtbar sind dort pro Eintrag `country`, Dauer, Typ und optionale Notiz. Wenn keine Detaildaten vorliegen, bleibt `stays_in_target_country` die kompakte Fallback-Information.

### Sprachbiographie für Native Speaker

Native-Speaker-Profile zeigen:

- `L1`
- `L1 der Mutter`
- `L1 des Vaters`
- `Zusätzliche Sprachen`
- `Geschlecht`
- `Geburtsjahr`
- `Herkunftsland`
- `Herkunftsregion`
- `Standardvarietät`

## Aktiver Metadatenvertrag

### Person-Ebene

- `person_id`
- `l1`
- `mother_l1`
- `father_l1`
- `additional_languages`
- `gender`
- `birth_year`
- `current_region`
- `childhood_region`
- `origin_country`
- `origin_region`

### Session-Ebene

- `session_id`
- `target_language`
- `speaker_type`
- `level_code`
- `level_self`
- `recording_year`
- `recording_date`
- `context`
- `recorded_by`
- `stays_in_target_country`
- `standard_variety`
- `notes`
- `tasks`
- `files`

### Detaillierte Sprachaufenthalte

- `exposure_entries` ist die strukturierte Session-Liste für Sprachaufenthalte.
- Jeder Eintrag enthält `country`, `duration_months`, `type` und optional `exposure_notes`.
- `stays_in_target_country` bleibt zusätzlich das kompakte Filter- und Summenfeld.

## Sample

- `Sample` bleibt die Proof-Surface für sichtbare Forschungssemantik.
- Änderungen an Task-Texten, Profilbezeichnungen, `Explorator:in` und `Sprachaufenthalte` müssen dort parallel aktualisiert werden.

## Bewusst nicht umgesetzt

- kein echter Player
- kein Doppel-Player
- keine Vergleichslogik
- keine zweite Datenquelle neben den dateibasierten Session-Metadaten
