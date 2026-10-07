# Local Storage Hygiene

Wiederholbarer Ablauf zum Prüfen und Aufräumen des lokalen PROMAT-Speichers. Soll-Zustand und Rollen: `docs/spec/platform-data-files.md` (Abschnitt „Local Storage Roles And Preservation Root“).

## 0. Ein Modell, zwei Sichten

```text
Intake  ->  lokales Archiv (PROMAT_LOCAL_ARCHIVE_ROOT, Arbeitsarchiv)
        ->  verifizierte institutionelle Kopie (PROMAT_PRESERVATION_ROOT)
        ->  Cleanup-Eignung (nur Bericht)
```

- **Speicherrollen** (Spec, Abschnitt „Local Storage Roles And Preservation Root“) klassifizieren *Orte*: `SOURCE/UNIQUE`, `WORKING`, `SPOOL`, `REGENERABLE`, `CACHE`, `PRESERVATION`.
- **Erhaltungszustände** beschreiben den Lebenszyklus je *Archiv-Einheit* (Session-Archiv oder Batch-Archiv) und werden von `scripts/research_data_intake/archive_preservation.py` berechnet: `ACTIVE_LOCAL` → `PRESERVATION_PENDING` → `PRESERVED` → `LOCAL_CLEANUP_ELIGIBLE`. Die Audit-Stufen `ACTIVE`/`INTAKE_COMPLETE` entsprechen `ACTIVE_LOCAL` (kein Fixity vorhanden; `INTAKE_COMPLETE` = Archiv-Manifest + Importbericht liegen vor). Es gibt kein zweites Zustandsmodell.
- `PROMAT_LOCAL_ARCHIVE_ROOT` ist und bleibt die Zielablage des Intake. `PROMAT_PRESERVATION_ROOT` wird **nur** von den Preservation-Werkzeugen und vom Inventar gelesen; der Intake schreibt nie direkt dorthin (ein Test sichert das ab). `PROMAT_LOCAL_ARCHIVE_ROOT` wird **nicht** auf die Preservation-Root umgestellt.
- `PROMAT_BACKUP_ROOT` ist eine dritte, eigene Rolle: die physisch getrennte Backup-Kopie (`archive_preservation.py backup-copy|backup-verify|backup-status`). Ein Backup ist keine Preservation und macht lokale Daten nie aufräumfähig; nur `LOCAL_CLEANUP_ELIGIBLE` aus der Preservation tut das. Alle drei Roots müssen ausdrücklich konfiguriert sein (Umgebung oder `.env` im Repo-Root); es gibt keine Standardpfade.
- Unveränderte Invariante: Keine einzigartigen wissenschaftlichen Daten sind Cleanup-geeignet, bevor eine vollständige institutionelle Kopie eine frische Fixity-Prüfung bestanden hat.

## 1. Inventar (read-only)

```powershell
python scripts/storage_inventory.py
python scripts/storage_inventory.py --preservation-root K:\Pronunciation_Matters
python scripts/storage_inventory.py --cleanup-report tmp\preservation-reports\cleanup-report-<zeit>.json
python scripts/storage_inventory.py --json
```

Das Skript ändert nichts. Es meldet Größen von Repo, Intake-Batches, `working/`, Laufzeit-Sessions, Archiv, Exports, Worktrees, die Erreichbarkeit der Preservation-Root (auch aus `PROMAT_PRESERVATION_ROOT`), die Erhaltungszustände je Einheit (Schnellprüfung ohne Hashing, höchstens `PRESERVED`) und Archivwurzel-Einträge, die die Einheitenkopie **nicht** abdeckt. `LOCAL_CLEANUP_ELIGIBLE` erscheint nur über einen mit `--cleanup-report` übergebenen Bericht von `archive_preservation.py cleanup-report` (Momentaufnahme; vor jeder Aktion neu erzeugen). Es braucht kein eingehängtes `K:`.

## 2. Immer sicher (reproduzierbar, keine Forschungsdaten)

| Kategorie | Voraussetzung | Neuerzeugung |
|---|---|---|
| `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `__pycache__` | keine | automatisch |
| `tmp/` QA-Screenshots, Edge-Profile (`edge-qa-*`, `mobile-audit-*`, `ui-qa`, …) | `git status` sauber | Browser-Pass neu ausführen |
| Worktrees | Branch gemergt, `git status` sauber, keine Intake-Dateien darin | `git worktree add` |

## 3. Nur nach Operator-Entscheidung

| Kategorie | Voraussetzung | Verifikation | Neuerzeugung |
|---|---|---|---|
| Batch-lokales Legacy-`.mfa_cache` | Batch fertig importiert; Sprachcache `shared/{lang}` vorhanden oder Netz verfügbar | Importbericht liegt im Archiv; kein Forschungsdatum, daher nicht vom Erhaltungszustand abhängig | MFA-Modell-Download per Docker |
| `working/{person}/text/mfa_corpus`, `mfa_output` | Batch importiert **und** Archiv-Einheit mindestens `PRESERVED` | Archiv-Manifest enthält Alignment | Intake-Pipeline neu laufen lassen |
| Alte Upload-Pakete in `exports/` | Prod-Publish bestätigt (Health/Ready 200) | `upload_report.md` + Prod-Check | `build_prod_upload_package.py` aus Runtime + Archiv |

## 4. Erst nach verifizierter Preservation

Batch-Quell-WAVs im Drop-in `import/`, Batch-`working/`-Quellkopien und das lokale Archiv selbst. Ablauf (Details und Befehle: `docs/runbooks/archive-preservation.md`):

1. Baseline-Fixity für bestehende Archiv-Einheiten erzeugen (additiv), Kopie im Dry-Run, dann verifizierte Kopie auf die Preservation-Root. Das lokale Archiv bleibt unverändert.
2. Vollständige SHA-256-Prüfung der Kopie (`verify`). Ein Zustand `PRESERVED` aus der Schnellprüfung genügt nicht.
3. `cleanup-report --candidate-dir <Batch-Ordner>` listet nur Einheiten im Zustand `LOCAL_CLEANUP_ELIGIBLE` und Dateien, deren SHA-256 mit verifiziert erhaltenem Inhalt übereinstimmt (`duplicates`). `not_covered`-Dateien (zum Beispiel die Intake-Workbooks der Batches und alles, was nur im Drop-in liegt) sind **nicht** abgedeckt und bleiben, bis sie separat gesichert sind.
4. `PROMAT_LOCAL_ARCHIVE_ROOT` bleibt unverändert; es wird nicht auf die Preservation-Root umgestellt. Nach jedem neuen Batch den Ablauf für die neuen Einheiten wiederholen.
5. Lokale Löschung nur durch explizite Operator-Aktion außerhalb der Werkzeuge, nie automatisiert. Kein Werkzeug im Repository löscht Archiv- oder Quelldaten.

## 5. Nie löschen

Originalaufnahmen, TextGrids, Intake-Workbooks, `secure/`-Material, `data/config/research_player/**` (nur lokal vorhanden, siehe Report), Postgres-Volumes (`data/db/postgres_dev`) und alles, dessen Preservation-Status unbekannt ist.
