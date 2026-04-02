# PROMAT App Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` für Arbeiten innerhalb von `app/`.

## Scope

- `src/app/` enthält die Flask-Anwendung und deren Runtime-Wiring.
- `templates/` enthält den Single-Shell-Aufbau.
- `static/` enthält das gemeinsame UI-System.
- `migrations/` enthält auth-nahe SQL-Migrationen.

## Routing und Sprache

- Öffentliche Routen bleiben ui-lang-präfixiert und technisch englisch.
- Technische Section-, Language- und Page-Slugs bleiben englisch.
- Sichtbare Labels, Breadcrumbs und Navigationseinträge dürfen deutsch sein, müssen aber von technischen Keys getrennt bleiben.
- In sichtbaren deutschen UI-Texten innerhalb von Templates, Seitentiteln, Buttons, Filtern, Sample-Beispielen und Leerzuständen sind echte Umlaute und `ß` zu verwenden. ASCII-Umschriften wie `ae`, `oe`, `ue` oder `ss` sind dort unzulässig.
- Alte deutsche Routen oder Alias-Slugs werden nicht wieder eingeführt.

## Datenzugriff und Runtime-Grenzen

- Verwende `PROMAT_RUNTIME_ROOT` und `PROMAT_PUBLIC_ROOT` als einzige kanonische Runtime-Grenzen.
- Leite Pfade über `src/app/runtime_paths.py` und `src/app/config/__init__.py` ab, nicht über freie Stringpfade.
- Kein View, Helper oder Script in `app/` greift direkt auf `secure/` zu.
- Öffentliche Inhalte kommen nur aus `public/`, nicht direkt aus `data/`.

## Technische Begriffe

- Verbindliche Task-Keys sind `isolated_speech`, `connected_speech`, `interview`.
- Verbindliche Datenbegriffe sind unter anderem `person_id`, `session_id`, `speaker_type`, `target_language`, `file_role`, `standard_variety`.
- Alte Begriffe wie `wordlist`, `text` oder `reflexion` dürfen nicht als neue technische Standards eingebaut werden.

## Template- und UI-Regeln

- `templates/base.html` bleibt die gemeinsame Shell.
- UI-Labels und Textstruktur dürfen angepasst werden, aber nicht über technische Slugs oder Dateipfade gesteuert werden.
- Badge-, Chip- und Task-Benennungen sollen aus bestehenden UI-Mustern konsolidiert werden, statt parallele Varianten einzuführen.
- Keine verdeckte Vermischung von Forschungszugang, öffentlichem Materialraum und Sample-Logik in denselben Komponenten.

## Refactor-Regeln

- Route-, Helper- oder Config-Refactors müssen Templates, Skripte, Tests und Doku mitziehen.
- Entferne Legacy konsistent oder lasse sie explizit dokumentiert. Keine halbaktiven Aliasse.
- Suche repo-weit nach Referenzen, bevor du technische Namen änderst.

## No-Go

- Keine neuen deutschen technischen Slugs.
- Keine direkten `secure/`- oder `data/`-Dateizugriffe aus Web-Views für öffentliche Auslieferung.
- Keine neue App-Quelle außerhalb von `app/`.
- Keine Reanimation von Search-, BlackLab-, Atlas-, Player- oder Editor-Abhängigkeiten.
- Keine harte Kopplung von UI-Texten an technische Keys.