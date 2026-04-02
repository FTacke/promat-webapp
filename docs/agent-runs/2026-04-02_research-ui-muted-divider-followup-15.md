# Disabled-Task-Muting und Divider-Abstände nachgezogen

Datum: 2026-04-02

## Ziel

Die Disabled-Typografie in Task-Panels und deaktivierten Profil-Task-Kacheln deutlich stärker zurücknehmen und die Divider-Abstände in Speaker-Cards über wiederverwendbare Before/After-Tokens robuster machen.

## Geänderte Bereiche

- `app/static/css/00_tokens.css`: separate Divider-Tokens für Abstand vor und nach Trennlinien ergänzt, zusätzlich ein starkes Muted-Farbtoken für deutlich hellere Disabled-Texte
- `app/static/css/30_components.css`: Utility-Klasse für stark gemutete Texte ergänzt und per spezifischer Disabled-Overrides auch für Description/State gegen spätere Komponentenselektoren durchgesetzt
- `app/static/css/40_cards.css`: Speaker-Card-Divider auf konsistente Before/After-Abstände umgestellt
- `app/templates/pages/research_recordings.html`: Disabled-Task-Panel nutzt die neue starke Muted-Klasse
- `app/templates/pages/research_speaker_profile.html`: deaktivierte Profil-Task-Kachel nutzt die neue starke Muted-Klasse

## Normative Doku

- Keine Änderung unter `docs/spec/`: nur visuelle Ausführung und Spacing-System nachjustiert, keine aktive Regel geändert.

## Verifikation

- Live-Screenshot der recordings-Task-Panels mit stärker zurückgenommenem Disabled-Zustand geprüft
- zusätzlicher Live-Screenshot bestätigt, dass beim deaktivierten `Interview` jetzt auch der Beschreibungstext gleich stark gemutet ist
- Live-Screenshot der Speaker-Cards mit zusätzlichem Abstand oberhalb der Footer-Divider geprüft
- bestehende fokussierte Research-Tests unverändert weiter lauffähig gehalten

## Offene Punkte

- Keine weiteren sichtbaren Restpunkte an Disabled-Muting oder Divider-Abständen in den angefassten Bereichen gesehen.