# Preservation activation (blocked at K:) and organizer equivalence

Datum: 2026-10-05

Branch: `local/preservation-activation` = `origin/claude/storage-preservation-consolidated` (`ce3340c`) plus this run. Nicht nach `main` gemergt. Keine Produktion, kein SSH, kein Deployment, kein deutscher Intake. Es wurden keine wissenschaftlichen Daten gelöscht. Sizes in GiB.

## Ergebnis in einem Satz

Teil B (Organizer) ist abgeschlossen: **EQUIVALENT WITH DOCUMENTED INTERFACE DIFFERENCES** (Erfolgspfad byte-identisch, Randfälle dokumentiert). Teil A (Preservation) ist **an `K:` blockiert**: `K:\Pronunciation_Matters` konnte nicht angelegt werden (Zugriff verweigert). Baseline und Dry-Run sind erledigt, die echte Kopie und Verifikation stehen aus. Nichts gilt als `PRESERVED`.

## Preservation activation

- **Ausgangsstand:** `main` enthielt das Preservation-Werkzeug nicht; Option 2 (lokaler Arbeitsbranch auf dem konsolidierten Stand) wurde vom Operator gewählt. Working tree sauber, `origin` abgerufen.
- **Invariante geprüft:** `PROMAT_PRESERVATION_ROOT` wird nur in `preservation.py`, `archive_preservation.py` und `storage_inventory.py` gelesen; `get_local_archive_root()` kennt nur `PROMAT_LOCAL_ARCHIVE_ROOT`. Intake schreibt weiter ins lokale Archiv.
- **K: (nur lesend):** erreichbar (NTFS, Netzlaufwerk, 178 GiB frei), `K:\Corapan` und `K:\romanistik` existieren (nicht inspiziert), `K:\Pronunciation_Matters` existiert nicht. `PROMAT_PRESERVATION_ROOT` und `PROMAT_LOCAL_ARCHIVE_ROOT` sind in Benutzer- und Prozess-Umgebung nicht gesetzt.
- **Anlegen fehlgeschlagen:** `New-Item K:\Pronunciation_Matters` → „Zugriff verweigert“. Die ACL des `K:`-Wurzelverzeichnisses nennt nur Administratoren/System/Ersteller-Besitzer mit Vollzugriff und einige Gruppen-SIDs mit Lese- bzw. einmal Schreibrecht; keine davon ließ sich dem Betreiberkonto zuordnen. Es wurde nichts umgangen (kein Ausweichen auf andere Pfade) und nichts verändert. Das Schreib-/Lese-/Lösch-Probe-Ergebnis ist daher: **nicht durchführbar**, kein Probeschreibzugriff.
- **Lokales Archiv (inventarisiert):** `C:\dev\promat_data_archive` (Code-Standard), 71 Einheiten (65 Sessions, 6 Batches), 9,237 Dateien vor der Baseline; nicht von Einheiten abgedeckt: `informanten_intake_20260525`, `praat_pipeline`.
- **Baseline:** `archive_preservation.py baseline` (Dry-Run, dann `--execute`): 71 Einheiten, 9,237 Dateien, `baseline_written=68`, `covered_by_unit_manifest=3`, keine unlesbaren Dateien. Additiv: 136 neue Dateien unter `fixity/baseline/`, nichts Vorhandenes umgeschrieben.
- **Copy-Dry-Run** gegen `K:\Pronunciation_Matters`: 71/71 `would_preserve`, 0 Probleme, Scope `complete` (inkl. `secure/`), keine Verweise auf `Corapan`, keine Lösch-/Verschiebeoperationen im Plan.
- **Echte Kopie / `verify` / Konfiguration von `PROMAT_PRESERVATION_ROOT`:** nicht ausgeführt (Blocker oben). `PROMAT_PRESERVATION_ROOT` wurde nicht gesetzt; `PROMAT_LOCAL_ARCHIVE_ROOT` blieb unverändert.
- **Windows-Probe des Werkzeugs auf `C:` (Scratchpad, ohne Quittungen im echten Archiv):** Klon mit 2 Einheiten (1 Session, 1 Batch): `copy` Dry-Run ok, `copy --execute` `preserved=2`, `verify` Exit 0 mit `LOCAL_CLEANUP_ELIGIBLE=2`, `status` `PRESERVED=2`. Das belegt den Windows-Pfad des Werkzeugs, **nicht** das Verhalten auf `K:` (Netzlaufwerk, Rechte, Durchsatz).
- **Inventar nach der Baseline** (`storage_inventory.py --preservation-root K:\Pronunciation_Matters`): Preservation-Root „NOT reachable“ (Ordner fehlt), Einheitenzustände `PRESERVATION_PENDING=71`, `PRESERVED=0`, `LOCAL_CLEANUP_ELIGIBLE=0`, nicht abgedeckt: `informanten_intake_20260525`, `praat_pipeline`. Gegenüber dem Audit: Archiv jetzt 9,386 Dateien (+149 Baseline-Dateien), sonst unverändert.

## Gefundener und behobener Defekt (Windows)

`cleanup-report --candidate-dir` brach auf dem echten Datenbestand mit `OSError: [WinError 1920]` ab, weil die Kandidaten-Traversierung (`fixity.list_unit_files`) bei Kaldi-`.ark`-Dateien unter `.mfa_cache` am `is_file()`-Aufruf scheiterte, bevor die vorhandene Pro-Datei-Fehlerbehandlung griff (derselbe Windows-Fallstrick ist im Run vom 2026-05-25 dokumentiert). Fix (eng begrenzt): `preservation._candidate_files()` meldet solche Dateien als `unreadable` statt abzubrechen; `list_unit_files` bleibt unverändert streng (Baseline/Copy sollen bei unlesbaren Archivdateien laut scheitern). Regressionstest `test_cleanup_report_survives_unstatable_candidate_file`. Danach lief der Bericht: englischer Batch 27 unlesbare Dateien (alle `.ark`), französisch/spanisch 0.

## Uncovered preservation material (aktueller Stand)

| Klasse | Lokaler Pfad | Einzigartig? | Andere Kopie | Vom Einheiten-Copy abgedeckt? | Blockiert deutschen Intake? |
|---|---|---|---|---|---|
| `praat_pipeline/` (Praat.exe, Skripte, Textkataloge) | Archivwurzel | ja | nein | nein | nein |
| Erste Workbook-Generation `informanten_intake_20260525/` | Archivwurzel | ja | nein | nein | nein |
| Aktuelle Intake-Workbooks (3, je Batch) | `import/<batch>/` | ja | nein | nein (`not_covered`) | nein (neuer Import archiviert Workbook-Hash) |
| Task-Kataloge `data/config/research_player/**` | Repo (ungetrackt) | nein | identische Kopien in allen 7 Upload-Paketen | nein | nein für DE; für Weiterbetrieb vor Paket-Cleanup sichern |
| Historischer Organizer | `import/organize_batch_working_tree.py` | ja (nur lokal) | nein | nein | nein (kanonische Wahl siehe unten); SHA-256 ist unten festgehalten |
| Dev-Postgres-Volume | `data/db/postgres_dev` | ja | nein | nein | nein |

Nichts davon wurde manuell kopiert.

## Organizer comparison

- **Pfade/Hashes:** historisch `scripts/research_data_intake/import/organize_batch_working_tree.py` (746 Zeilen, ignoriert/ungetrackt) SHA-256 `539973a1b575b8268cd7abdcc63758d3e8c0cb2900c86318c39d279055446fc0`; rekonstruiert `scripts/research_data_intake/organize_batch_working_tree.py` auf diesem Branch (587 Zeilen) SHA-256 `b31781eb367cdd418755fcc206fb25bc0b9690c9cd87712d93e0e89d948c48a6` (gegenüber der Vorversion `2274ba44…` geändert; Branch-Stand ist maßgeblich). Keine Datei wurde verändert.
- **Pinned Tests:** `app/tests/test_research_working_tree_intake.py` 37/37 mit der rekonstruierten Version und 37/37 mit der historischen Datei (Wegwerf-Worktree, entfernt). Zusätzlich 163 Intake/Archiv/Storage/Runtime-Config-Tests auf dem Branch grün.
- **Statische Unterschiede:**

| Aspekt | Historisch | Rekonstruiert | Klasse |
|---|---|---|---|
| Struktur/Helper (`collect_batch_files`, `file_snapshot` vs `scan_import_batch`, `choose_unique_candidate`) | – | – | NON-FUNCTIONAL (gleiche Snapshot-Felder `path,size,mtime_ns,hash`) |
| CLI | `--copy/--move/--symlink`, `--report-json`, `--person-id` einmalig | `--transfer-mode`, `--json`, `--person-id` wiederholbar | Interface-Unterschied (importer nutzt API) |
| Dry-Run-Status | `rebuilt` | `planned_rebuild` | Report-Label, nicht downstream-relevant |
| Berichtsschlüssel | `mode` | `dry_run`; Summary um `planned_rebuild/missing/conflicts/not_expected` erweitert | Report-Label; `person_ids`/`summary.errors` in beiden vorhanden |
| State: `recognized_sources`, Eintrag für `not_expected…`-Tasks | geschrieben | nicht geschrieben | POTENTIALLY BEHAVIOURAL (von keinem Code gelesen; nur Organizer liest State) |
| `--person-id`: State der übrigen Personen | **wird verworfen** (State nur noch für gewählte Person) | bleibt erhalten | CONFIRMED BEHAVIOURAL DIFFERENCE (historischer Defekt) |
| Defektes Interview-JSON | `error_build_failed`; **bisheriger guter Interview-Baum wird vorher gelöscht** | `error_interview_transform`; guter Baum bleibt | CONFIRMED BEHAVIOURAL DIFFERENCE (historischer Defekt) |
| Unbekannte `--person-id` | Fehler, Exit 1 | Exit 0, Tasks `missing_*`, kein Fehler | CONFIRMED BEHAVIOURAL DIFFERENCE (Rekonstruktion toleranter) |
| Bestehender Task-Baum ohne State, abweichender Inhalt, anderes Managed-Output fehlt | überschreibt still (`rebuilt`) | `conflict_existing_working_tree` | CONFIRMED BEHAVIOURAL DIFFERENCE (Rekonstruktion strenger) |
| Nur geänderte mtime, Inhalt gleich (Wordlist/Text) | `unchanged` (Content-Abgleich) | `rebuilt` (idempotent) | POTENTIALLY BEHAVIOURAL (kosmetisch) |
| Exit-Codes | 1 bei `errors` | 1 bei `errors` | gleich |

- **Realer A/B-Lauf** (unveränderte Snapshots aus drei vorhandenen historischen Batches, jeweils eigener Sandbox-Baum unter einem Wegwerf-Worktree; Quellen unangetastet; beide Original-CLIs, Flags nur übersetzt): Englisch komplett (9 Personen, 27 Tasks), Französisch (3 Personen inkl. zwei Sonderbenennungen + 1 Native), Spanisch (2 Personen + 1 Native).
  - Frischer Schreiblauf: Statusverteilung identisch (`rebuilt` 27 / 11 + 1 native / 8 + 1 native); Arbeitsbäume **dateiweise identisch** (54/54, 22/22, 16/16 Dateien, gleiche SHA-256). Dry-Run schreibt in beiden nichts.
  - Wiederholung: beide `unchanged`; Cross-Lauf (jede Version auf dem Baum der anderen): `unchanged`.
  - **Realer bestehender Batch** (englischer Batch mit echtem `working/` und vom historischen Werkzeug geschriebenem State, 1,599 Dateien): beide 27/27 `unchanged`, Baum unverändert (Dry-Run und Schreiblauf).
  - Stray-Baum ohne State: siehe Tabelle; nach `--replace-existing` identische Bäume.
- **Downstream:** Der Importer-Dry-Run (`import_batch_to_production.py --run-working --dry-run`) konnte nicht laufen, weil er die Dev-Postgres braucht (Docker-Engine aus, Port 54321 verweigert) und der Fehler vor der Organizer-Stufe liegt. Ersatz: beide Module wurden exakt wie vom Importer aufgerufen (`transfer_mode=copy`, `replace_existing=True`, `force_tasks=set()`, `person_ids={…}`, Dry-Run und Schreiblauf); beide liefern `person_ids` und `summary.errors`, den einzigen konsumierten Ergebnisvertrag, und erzeugen identische Bäume. Der State wird außerhalb des Organizers nur in `_cleanup_working_people` toleranter gelesen. **Nicht verifiziert:** der vollständige Importer-Lauf gegen eine laufende DB.
- **Klassifikation: EQUIVALENT WITH DOCUMENTED INTERFACE DIFFERENCES.** Die Erfolgspfad-Ergebnisse (Dateien, Layout, Inhalte, State-Kompatibilität in beide Richtungen, Verhalten auf dem realen Altbestand) sind identisch. Unterschiede liegen in CLI/Labels und in Fehler-/Randfällen; zwei davon sind Defekte der historischen Version, die nicht erhalten werden sollten.
- **Empfehlung:** Die rekonstruierte Version wird kanonisch (sicherer, gleiches Ergebnis), mit einem kleinen Follow-up vor dem deutschen Intake: unbekannte `--person-id` sollte wie historisch als Fehler enden (nicht umgesetzt, da hier keine Organizer-Änderung vorgenommen wird). Die historische Datei darf nicht gelöscht oder überschrieben werden; ihr Hash steht oben. Der Operator sollte sie bei Gelegenheit in die Preservation-Root-Konfiguration/Archivwurzel (nicht ins Git) sichern.

## German-readiness status

- Preservation root: **NOT READY** (`K:\Pronunciation_Matters` nicht anlegbar; kein Blocker für den deutschen Intake selbst)
- Organizer: **READY** (äquivalent mit dokumentierten Unterschieden; Follow-up für unbekannte Person-ID empfohlen)
- German task catalogs: **NOT READY** (keine vorhanden; nicht erzeugt)
- German source data: **NOT PRESENT LOCALLY**
- German single-speaker dry-run: **BLOCKED** (Katalog, Quelldaten und Workbook fehlen; außerdem Docker/Postgres für den Importer-Dry-Run)

## Cleanup candidates (kein Löschen)

`cleanup-report` für die drei Batch-Ordner (englisch, französisch, spanisch; Stand ohne Preservation): 0 Duplikate, da keine Einheit `LOCAL_CLEANUP_ELIGIBLE`; `not_covered` 11,031 / 4,609 / 4,034 Dateien (4.29 / 4.60 / 3.59 GiB), unlesbar 27 / 0 / 0 (nur `.ark`). Projektion aus dem früheren SHA-256-Vergleich (**keine Eignungsaussage**): nach verifizierter Preservation wären rund 6.3 GB Quell-WAV/TextGrid der Batches und rund 2.7 GB `working/`-WAVs technisch Duplikate; `working/…/mfa_corpus` (≈1.0 GB, regenerierbar), Workbooks, Legacy-`.mfa_cache` und `.lab`/`.json`-Dateien bleiben `not_covered` oder regenerierbar. Ganze Batch-Ordner dürfen erst gelöscht werden, wenn jede wissenschaftlich relevante Dateiklasse abgedeckt ist (insbesondere Workbooks).

## Cloud continuation facts (verifiziert am 2026-10-05)

- `K:\Pronunciation_Matters` existiert nicht; das Betreiberkonto hat kein Anlegerecht im `K:`-Wurzelverzeichnis. Erforderlich außerhalb von Cloud: Ordner anlegen lassen oder Recht erteilen, dann Runbook-Schritte 3–10 ausführen.
- Das lokale Archiv ist inventarisiert und hat eine vollständige additive Fixity-Baseline (71 Einheiten, 9,237 Dateien); das Copy-Dry-Run-Ergebnis ist sauber. Das Werkzeug läuft nachweislich auf Windows (Probe auf `C:`); `K:`-Verhalten ungetestet.
- Der Windows-Defekt in `cleanup-report` ist behoben und getestet.
- Organizer-Äquivalenz: festgestellt mit Einschränkungen (siehe Tabelle); der importer-seitige DB-gestützte Dry-Run steht aus.
- Weiterhin nur lokal vorhanden: Originalaufnahmen/TextGrids (Archiv), Workbooks, Task-Kataloge (+ Pakete), historischer Organizer, Dev-DB.
- Nicht verifiziert: Docker/Postgres-Zustand, Produktionszustand, `K:`-Durchsatz.
- Branch `local/preservation-activation`: Der Run ist nicht vollständig abgeschlossen (Kopie/Verify auf `K:` offen); der Branch gilt daher noch **nicht** als PR-Kandidat für `main`. Die `K:`-Blockade ist ein Rechteproblem, kein Codeproblem.
