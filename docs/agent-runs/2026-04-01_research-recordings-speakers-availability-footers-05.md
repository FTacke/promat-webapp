# Research Recordings Speakers Availability Footers 05

Datum: 2026-04-01

## Ziel

Bestehende Research-Seiten, Profilseiten und die `Sample`-Prüffläche für fachlich korrekte Aufzeichnungsverfügbarkeit, konsistente Benennung aus Forschendenperspektive und stabilere Card-/Profil-Details nachschärfen.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_sessions.py`
- `app/src/app/research_views.py`
- `app/templates/pages/research_recordings.html`
- `app/templates/pages/research_speakers.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `docs/research_pages/promat_recordings_speakers.md`

## Geänderte Bereiche

- Verfügbarkeitslogik in Reader- und View-Modellen
- Speaker-Cards, Profilseite und `Sample`
- Footer- und Badge-Regeln im bestehenden CSS-System
- spanische Dev-Seed-Generierung für Native-Speaker-Aufzeichnungen
- Referenzdokumentation und neue Run-Dokumentation

## Wichtige Entscheidungen

- Native Speaker bieten in PROMAT keine Interview-Aufzeichnungen an
- fachliche Verfügbarkeit wird pro Session an dokumentierten Task-Typen ausgerichtet; nicht vorhandene Aufzeichnungen werden weder in der UI verlinkt noch im Player-Stub angenommen
- der Bereichstitel `Aufgaben` wird auf Speaker-Cards und Profilseiten durch `Aufzeichnungen` ersetzt; task-spezifische Tabellenaktionen werden in einem späteren Run weiter verfeinert
- Speaker-Card-Links werden als ruhige Textlinks mit Pfeil geführt und am unteren Rand der Card verankert
- der Zurück-Link der Profilseite bleibt Navigation und steht deshalb nach dem Aufzeichnungsblock am Ende der Seite

## Abweichungen

- Keine neue Grundarchitektur, keine neue DB-Struktur und keine Abweichung von den bestehenden Runtime-Grenzen

## Verifikation

- statische Fehlerprüfung der geänderten Python-, Template-, CSS- und Doku-Dateien ohne Befunde
- spanische Dev-Sessions nach der Native-Speaker-Korrektur neu generiert
- Routenvalidierung erfolgreich für `recordings`, `speakers`, Profil und `Sample`
- Native-Speaker-Verfügbarkeit erfolgreich geprüft: kein Interview-Link auf Cards oder Profilen, kein Interview-Task-Panel bei Native-Filter in `recordings`, Native-Interview-Playerroute liefert `404`

## Offene Punkte

- Der Dev-Datensatz bleibt außerhalb dieses Korrekturlaufs weiterhin minimal und bildet nicht für alle Lernenden alle drei Aufzeichnungstypen ab.
- Historische ältere Run-Dokumente wurden nicht rückwirkend normalisiert.