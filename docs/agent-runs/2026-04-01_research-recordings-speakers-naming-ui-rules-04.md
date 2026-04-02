# Research Recordings Speakers Naming UI Rules 04

Datum: 2026-04-01

## Ziel

Bestehende Research-Seiten, die `Sample`-Prüffläche und die zugehörigen Repo-Regeln für Task-Namen, sichtbare deutsche UI-Texte, Chip-/Badge-Systematik und Filterlayout konsistent schärfen.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `.github/copilot-instructions.md`
- `app/src/app/research_sessions.py`
- `app/src/app/research_views.py`
- `app/templates/pages/research_recordings.html`
- `app/templates/pages/research_speakers.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/templates/pages/sample_page.html`
- `docs/research_pages/promat_recordings_speakers.md`

## Geänderte Bereiche

- zentrale Task-Definitionen und Research-View-Logik
- Research-Templates für `recordings`, `speakers` und Profil
- globale UI-Regeln für Filter-Chips, Badges und Filter-Grid
- `Sample` als Prüffläche für Chips, Badges, Speaker-Cards, Profilkopf und Task-Panels
- Repo-Regeln in Root-, App-, Docs- und `.github`-Instruktionen
- Referenzdokumentation und neue Run-Dokumentation unter `docs/research_pages/`

## Wichtige Entscheidungen

- Die sichtbaren kurzen Task-Namen sind nun verbindlich `Wortliste`, `Text` und `Interview`
- Die längeren erklärenden Formen werden konsistent aus derselben Task-Definition gespeist
- Sichtbare deutsche UI-Texte verwenden ab jetzt verbindlich echte Umlaute und `ß`
- Filter-Chips und Badges werden systematisch getrennt: Chips für aktive Filter, Badges für Status und Kategorien
- Der Zurück-Link auf Profilseiten ist Navigation und bleibt daher außerhalb des Aufgabencontainers

## Abweichungen

- Keine neue Datenarchitektur, keine neue DB-Struktur und keine Abweichung von den bestehenden Runtime-Grenzen

## Verifikation

- statische Fehlerprüfung der geänderten Python-, Template- und CSS-Dateien folgt nach dem Patch
- Route-Rendering der betroffenen Seiten wird nach dem Patch mit dem Flask-Testclient geprüft

## Offene Punkte

- Historische ältere Run-Dokumente wurden nicht rückwirkend komplett sprachlich normalisiert
- task-spezifische Counts in `recordings` bleiben bis zu einer feineren Datenbasis an die aktuelle gefilterte Ergebnismenge gebunden

## Nächste sinnvolle Schritte

- geänderte Seiten und Texte gegen den Testclient prüfen
- verbleibende user-visible ASCII-Umschriften in angrenzenden Research-Dokumenten bei Folgeruns abbauen