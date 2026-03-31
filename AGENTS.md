# PROMAT Repo Governance

Dieses Dokument operationalisiert die verbindliche PROMAT-Spezifikation. Es ersetzt die Spezifikation nicht, sondern macht sie für Repo-Arbeit, Agent-Runs und kollaborative Änderungen unmittelbar anwendbar.

## Zweck und Prioritäten

- PROMAT ist ein schlanker, strukturell sauberer Bootstrap für Pronunciation Matters.
- Vorrang haben Architekturklarheit, konsistente Begriffe, sichere Datenpfade und minimale Seiteneffekte.
- Änderungen sollen das Repo verständlicher machen, nicht nur kurzfristig lauffähig.

## Verbindliche Quellen

Für Zielarchitektur und Begriffe ist bindend:

1. `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
2. aktive Runtime-Wiring-Dateien: `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `docker-compose.dev-postgres.yml`, `app/infra/docker-compose.prod.yml`
3. dieses `AGENTS.md` und relevante scoped `AGENTS.md`
4. aktive Repo-Dokumentation unter `docs/architecture/`, `docs/conventions/`, `docs/runbooks/`, `docs/decisions/`
5. `README.md` als Kurzüberblick

Historische Run-Logs unter `docs/start/` und `docs/agent-runs/` erklären Entscheidungen, überschreiben aber keine aktive Architektur.

## Architekturprinzipien

- `app/` ist der einzige versionierte Application-Source-Root.
- `data/` ist der geschützte Forschungsdatenraum.
- `public/` ist der ausschließlich explizit freigegebene öffentliche Asset-Raum.
- `secure/` ist Klardatenraum und bleibt außerhalb der Webapp.
- `scripts/` enthält wiederholbare Import-, Export- und Pipeline-Schritte, nicht implizite Laufzeitlogik.
- Das Repo bleibt frei von Search-, BlackLab-, Atlas-, Player- und Editor-Residuen, solange diese nicht bewusst als neuer Architekturstand eingeführt und dokumentiert werden.

## Routing- und Sprachprinzipien

- Öffentliches Routing folgt dem Schema `/{ui_lang}/{section}/{corpus_language}/{page}`.
- Technische Slugs, Keys, Datenfelder und Controlled Vocabularies sind immer Englisch.
- Sichtbare UI-Labels bleiben aktuell Deutsch, müssen aber lokalisierbar bleiben.
- Alte deutsche technische Slugs und Altpfade dürfen nicht wieder eingeführt werden.
- UI-Sprache und technische Routing-Sprache dürfen nicht vermischt werden.

## Daten- und Filesystem-Prinzipien

- `person_id` identifiziert Personen stabil und sprachneutral.
- `session_id` identifiziert konkrete Aufnahmen.
- Session-Daten liegen unter `data/sessions/{language}/{session_id}/`.
- Die Session-Unterstruktur ist `raw/`, `source/`, `alignment/`, `derived/`, `items/` plus `metadata.json`.
- Technische Task-Typen sind `isolated_speech`, `connected_speech`, `interview`.
- Sensible Informationen gehören weder in Dateinamen noch in Pfade, Slugs oder öffentliche Assets.

## Unantastbare Webapp-Grenzen

- Die Webapp greift nie direkt auf `secure/` zu.
- Öffentliche Assets werden nie direkt aus `data/` ausgeliefert.
- `AUTH_DATABASE_URL` ist die einzige gültige Auth/Core-DB-Variable.
- `PROMAT_RUNTIME_ROOT` und `PROMAT_PUBLIC_ROOT` sind die kanonischen Runtime-Grenzen.
- Daten-, Public- und Secure-Logik werden nicht in denselben Pfaden, Helpers oder Views vermischt.

## Dev/Prod-Parität

- Dev und Prod sollen dieselbe Architektur, dieselben Begriffe, dieselben Route-Schemata und dieselbe Datenlogik verwenden.
- Unterschiede zwischen Dev und Prod dürfen nur infrastrukturnah sein, nicht begrifflich oder strukturell.
- Dev-only Sonderstrukturen, Sonderrouten oder Sonderbegriffe sind unzulässig.
- Jede akzeptierte Abweichung muss in `docs/architecture/dev-prod-parity.md` und im jeweiligen Run-Log erklärt werden.
- Provisorische Lösungen müssen als provisorisch markiert werden und eine Abbaurichtung benennen.

## Regeln für Refactors

- Refactors beheben die Ursache, nicht nur Symptome.
- Öffentliche oder repo-interne Namensänderungen erfolgen nicht still; Code, Skripte, Doku und Konfiguration müssen im selben Run nachgezogen werden.
- Legacy wird entweder vollständig entfernt oder explizit als Übergang dokumentiert. Halbe Wiederbelebungen sind unzulässig.
- Vor Strukturänderungen sind Referenzen repo-weit zu prüfen.

## Regeln für Datenpfade

- Pfade werden nicht frei im Code erfunden, sondern aus den kanonischen Runtime- und Config-Dateien abgeleitet.
- Keine neuen Ad-hoc-Ordner außerhalb von `app/`, `data/`, `public/`, `secure/`, `scripts/`, `docs/`, `.github/` ohne dokumentierte Entscheidung.
- `raw`, `source`, `alignment`, `derived` und `items` behalten ihre semantische Trennung.

## Öffentliche vs. geschützte Inhalte

- `public/` enthält nur bewusst freigegebene Inhalte.
- `data/` bleibt geschützt, auch wenn einzelne Inhalte später öffentlich exportiert werden.
- Export nach `public/` ist ein expliziter Prozessschritt, keine implizite Folge eines View- oder Script-Laufs.
- Keine Klardaten, Re-Identifikationsinformationen oder sensiblen Metadaten in öffentliche Dateien oder öffentlich erreichbare Routen.

## Dokumentationspflicht nach jedem Run

- Jeder substanzielle Agent- oder Maintainer-Run erzeugt einen Eintrag unter `docs/agent-runs/` nach Template.
- Bootstrap-, Setup-, Governance- oder Repo-Struktur-Runs aktualisieren zusätzlich `docs/start/`.
- Dauerhafte Architekturentscheidungen kommen nach `docs/decisions/`.
- Wiederholbare Dev/Prod-Abläufe kommen nach `docs/runbooks/`.
- Aktive Regeln werden in `docs/conventions/` oder `docs/architecture/` aktualisiert, nicht als Schattennotiz in irgendeinem Einzeldokument.

## Regeln für Abschlussberichte

- Abschlussberichte nennen mindestens Ziel, geänderte Bereiche, Architekturwirkung, Verifikation, offene Punkte und nächste sinnvolle Schritte.
- Abweichungen von der Spezifikation oder von der Dev/Prod-Parität müssen explizit genannt werden.
- Nicht ausgeführte Prüfungen oder Tests werden offen benannt.

## Regeln für Legacy-Bereinigung

- Gelöschte Legacy-Pfade, Variablen und Slugs werden nicht reaktiviert.
- Neue Logik darf nicht an alte Alias-Pfade oder alte Begriffe gehängt werden.
- Historische Dokumente bleiben als Historie bestehen, dürfen aber nicht als aktive Anleitung behandelt werden.

## Benennungen und technische Sprache

- Ein technisches Konzept hat genau einen bevorzugten Namen.
- Verbindliche technische Standards sind unter anderem `project`, `research`, `teaching`, `sample`, `person_id`, `session_id`, `isolated_speech`, `connected_speech`, `interview`, `raw`, `source`, `alignment`, `derived`, `items`.
- Alte Ausdrücke wie `wordlist`, `text`, `reflexion` sind keine technischen Standards mehr.
- UI-Labels dürfen deutsch sein; technische Keys dürfen es nicht.

## Minimales, sauberes Arbeiten

- Nutze wenige starke Dateien statt verteilter Schattenregeln.
- Ergänze bestehende Strukturen, statt parallele Alternativstrukturen zu bauen.
- Halte Änderungen klein, zusammenhängend und repo-weit konsistent.
- Wenn ein Bereich eine engere Regel braucht, nutze ein scoped `AGENTS.md` statt das Root-Dokument aufzublähen.

## No-Go-Liste

- Keine deutschen technischen Slugs oder Keys neu einführen.
- Keine alten Routen, Pfade oder Variablennamen reaktivieren.
- Keine Webapp-Zugriffe auf `secure/`.
- Keine direkten öffentlichen Auslieferungen aus `data/`.
- Keine stillen Architekturentscheidungen ohne Doku.
- Keine ad-hoc-Ordner oder neue Schattenstruktur außerhalb des definierten Layouts.
- Keine verstreute, sich widersprechende Doppeldokumentation.
- Keine Vermischung von UI-Sprache und technischer Sprache.
- Keine dev-only Notlösungen ohne dokumentierte Begründung und Abbaurichtung.