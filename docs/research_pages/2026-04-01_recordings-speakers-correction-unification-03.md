# Recordings Speakers Correction Unification 03

Datum: 2026-04-01

## Ziel

Gezielte Korrektur und Vereinheitlichung der bestehenden Research-Seiten fuer `recordings`, `speakers`, Profil und `Sample`, ohne neue Basisarchitektur einzufuehren.

## Schwerpunkt dieses Runs

* ruhigere und klarer getrennte Aufgabenlinks auf Speaker-Cards
* staerkere visuelle Hierarchie auf Speaker-Cards ueber Top-Border und Footer-Trennung
* vertikale Profil-Logik mit einem starken Hauptcontainer und Aufgabenbereich darunter
* Vereinfachung der `recordings`-Task-Zone durch integrierte Counts statt separater Summary-Box
* Ergaenzung von Dummy-Beispielen auf `Sample` fuer alle geschaerften Research-Komponenten

## Geaenderte Bereiche

* `app/templates/pages/research_recordings.html`
* `app/templates/pages/research_speakers.html`
* `app/templates/pages/research_speaker_profile.html`
* `app/templates/pages/sample_page.html`
* `app/static/css/20_layout.css`
* `app/static/css/30_components.css`
* `app/static/css/40_cards.css`
* `app/src/app/research_views.py`
* `docs/research_pages/promat_recordings_speakers.md`

## Umgesetzte Entscheidungen

* `recordings` fuehrt Task-Beschreibung und Count direkt im Task-Panel zusammen
* die Ergebniszone liest sich in `recordings` und `speakers` jetzt als Chip-Zone vor der Infozeile
* die Tabellenaktion in `recordings` wurde auf `Aufnahme` verkuerzt
* Speaker-Cards haben jetzt einen deutlicher gegliederten Aufgabenfuss statt gleich lauter Pill-Buttons
* das Profil ist als vertikale Lesefolge organisiert; Aufgaben stehen danach in einem separaten Container
* `Sample` dient jetzt auch als visuelle Referenz fuer Research-Workbench-Komponenten

## Offen bewusst nicht umgesetzt

* kein echter Player-Ausbau
* keine neue Datenquelle oder Datenbankanbindung fuer Research-Seiten
* keine Aenderung an den kanonischen Metadatenfeldern aus dem zweiten Verfeinerungsrun
