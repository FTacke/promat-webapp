# Local Storage Hygiene

Wiederholbarer Ablauf zum Prüfen und Aufräumen des lokalen PROMAT-Speichers. Soll-Zustand und Rollen: `docs/spec/platform-data-files.md` (Abschnitt „Local Storage Roles And Preservation Root“).

## 1. Inventar (read-only)

```powershell
python scripts/storage_inventory.py
python scripts/storage_inventory.py --preservation-root K:\Pronunciation_Matters
python scripts/storage_inventory.py --json
```

Das Skript ändert nichts. Es meldet Größen von Repo, Intake-Batches, `working/`, Laufzeit-Sessions, Archiv, Exports, Worktrees und die Erreichbarkeit der Preservation-Root.

## 2. Immer sicher (reproduzierbar, keine Forschungsdaten)

| Kategorie | Voraussetzung | Neuerzeugung |
|---|---|---|
| `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `__pycache__` | keine | automatisch |
| `tmp/` QA-Screenshots, Edge-Profile (`edge-qa-*`, `mobile-audit-*`, `ui-qa`, …) | `git status` sauber | Browser-Pass neu ausführen |
| Worktrees | Branch gemergt, `git status` sauber, keine Intake-Dateien darin | `git worktree add` |

## 3. Nur nach Operator-Entscheidung

| Kategorie | Voraussetzung | Verifikation | Neuerzeugung |
|---|---|---|---|
| Batch-lokales Legacy-`.mfa_cache` | Batch fertig importiert; Sprachcache `shared/{lang}` vorhanden oder Netz verfügbar | Importbericht liegt im Archiv | MFA-Modell-Download per Docker |
| `working/{person}/text/mfa_corpus`, `mfa_output` | Batch importiert **und** Archiv verifiziert | Archiv-Manifest enthält Alignment | Intake-Pipeline neu laufen lassen |
| Alte Upload-Pakete in `exports/` | Prod-Publish bestätigt (Health/Ready 200) | `upload_report.md` + Prod-Check | `build_prod_upload_package.py` aus Runtime + Archiv |

## 4. Erst nach verifizierter Preservation

Batch-Quell-WAVs im Drop-in `import/`, Batch-`working/`-Quellkopien und das lokale Archiv selbst. Voraussetzungen:

1. Kopie ohne Löschen auf die Preservation-Root (`PROMAT_LOCAL_ARCHIVE_ROOT` bleibt unverändert).
2. SHA-256 je Datei auf beiden Seiten vergleichen; Dateizahl und Größen vergleichen.
3. `metadata/archive_manifest.json` je Session prüfen.
4. Erst danach `PROMAT_LOCAL_ARCHIVE_ROOT` auf die Preservation-Root umstellen und lesend validieren.
5. Lokale Löschung nur durch explizite Operator-Aktion, nie automatisiert.

## 5. Nie löschen

Originalaufnahmen, TextGrids, Intake-Workbooks, `secure/`-Material, `data/config/research_player/**` (nur lokal vorhanden, siehe Report), Postgres-Volumes (`data/db/postgres_dev`) und alles, dessen Preservation-Status unbekannt ist.
