# MD3-Visual-Audit — `.sr-only` nachgeführt

**Datum:** 2026-05-31  
**Branch:** main  
**Typ:** Bugfix, kein Commit (Arbeitsbaum offen)

## Befund

Nach der MD3-Bereinigung (2026-05-30) fehlte `.sr-only` in allen App-CSS-Dateien.  
Die Klasse war ursprünglich in den gelöschten MD3-Dateien definiert und wurde beim Cleanup nicht in die App-CSS überführt.

## Auswirkung

`.sr-only` wurde in mindestens 11 Template-Stellen verwendet:
- Login-Button und Account-Button in der Topbar (`_top_app_bar.html`)
- Copy-Button in Admonition/Citation-Boxen (`_admonition.html`)
- Screen-Reader-Statustexte in Research-Filtern und Phenomena-Editor
- Invite-Status in Admin-Users-Seite

Ohne `.sr-only` waren alle diese Texte visuell sichtbar — Icon-Buttons zeigten ihr Label, Copy-Buttons zeigten ihren Aria-Label-Text.

## Geänderte Datei

| Datei | Änderung |
|---|---|
| `app/static/css/layout.css` | `.sr-only` als globale Accessibility-Utility ergänzt |

## Bewusst nicht geändert

| Aspekt | Begründung |
|---|---|
| H2-Größen (`--pm-type-reading-h2-size`) | `clamp(1.52rem … 1.84rem)` passt zur MD3-Systematik; Templates verwenden `.promat-content-block__title` mit diesem Token korrekt |
| Topbar-Padding der Utility-Buttons | `padding: 0 0.7rem` + `min-width: 44px` ergibt 44px breite Icon-Buttons — geplantes Verhalten |
| Content-Breiten (`--promat-content-width: 60rem`) | Token war bereits vor dem MD3-Cleanup definiert; keine Regression |
| Button-Größen und Rundungen | Kein Änderungsbedarf nach `.sr-only`-Fix |
| `pm-button--success` Copy-Success-State | Bereits korrekt in 30_components.css |

## Testergebnisse

667 passed, 0 failed | Ruff: clean
