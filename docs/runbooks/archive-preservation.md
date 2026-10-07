# Runbook: Archiv-Fixity und institutionelle Kopie

## Zugehörige Spezifikation

- `docs/spec/platform-data-files.md` (Abschnitte „Archive provenance and fixity“, „Institutional preservation“, „Storage Roots“)

## Zweck

Das lokale Archiv (`PROMAT_LOCAL_ARCHIVE_ROOT`) ist ein Arbeitsarchiv. Dieses Runbook erzeugt Fixity für bestehende Archive, kopiert sie verifiziert auf eine zweite, institutionelle Ablage (Preservation Root) und weist den Erhaltungszustand je Einheit aus. Es löscht nichts.

Der heutige physische Ort der Ablage (beim Betreiber: ein Ordner auf Laufwerk `K:`) ist **aktuelle Konfiguration, keine Architektur-Identität**. Ein späterer Umzug braucht nur: verifizierte Kopie, Integritätsprüfung, Konfigurationsänderung.

## Ausgangslage (Messung `docs/reports/2026-10-05_local-storage-audit.md`, nur zur Orientierung)

- Das lokale Archiv ist bis zur verifizierten Preservation die maßgebliche Kopie der Originalaufnahmen; erstes Migrationsziel ist genau dieses bestehende Archiv. Sein Ort steht nur in der Konfiguration (`PROMAT_LOCAL_ARCHIVE_ROOT`), nicht im Code: Es gibt keinen eingebauten Standardpfad mehr.
- Die Drop-in-Ordner `import/<batch>/` enthalten Duplikate der archivierten Originale. Nach verifizierter Preservation kann dort erheblicher Speicher frei werden (Zahlen stehen nur im Audit-Bericht, nicht im Code).
- Task-Kataloge (`data/config/research_player/**`) liegen nur beim Operator und sind nicht im Git; identische Kopien stecken in den Upload-Paketen. Aktuelle Intake-Workbooks liegen nur in den Batch-Verzeichnissen. **Beides deckt `copy` für historische Batches nicht ab**: Es kopiert nur Archiv-Einheiten (`sessions/`, `batches/`). Neue Imports archivieren Workbook und Katalog-Identität (SHA-256) additiv; historische Bestände werden nicht nachträglich umgeschrieben. Historische Workbooks, Kataloge und Archivwurzel-Ordner wie `praat_pipeline/` oder `informanten_intake_*` müssen separat gesichert werden; die Berichte weisen solche Einträge unter „Archive-root entries not covered by the unit copy“ aus.
- `K:\Corapan` ist ein anderes Projekt und darf nie mit `K:\Pronunciation_Matters` vermischt werden.

## Archivwurzel, Preservation-Root und Backup-Root

Die drei Roots werden über ihre Variable in der Umgebung oder in der git-ignorierten `.env` im Repo-Root gesetzt (Vorlage `.env.example`). Die Umgebung gewinnt immer; es gibt keine Standardpfade.

- `PROMAT_LOCAL_ARCHIVE_ROOT`: Arbeitsarchiv, in das der Intake schreibt. Pflicht für jeden Intake- und Archivbefehl; fehlt der Root, brechen die Werkzeuge mit einer Fehlermeldung ab und legen nichts an. Fluss: Intake → lokales Archiv → verifizierte Kopie.
- `PROMAT_PRESERVATION_ROOT`: zweite, institutionell abgelegte Kopie. Nur `archive_preservation.py` und `storage_inventory.py` lesen sie. Sie macht das Intake-Archiv **nicht** zum direkten Schreibziel, und `PROMAT_LOCAL_ARCHIVE_ROOT` wird nicht dorthin umgestellt.
- `PROMAT_BACKUP_ROOT`: physisch getrennte Backup-Kopie (externer Datenträger). Eigene Rolle mit eigenem Marker `BACKUP_ROOT.json`; ersetzt die Preservation nicht, ist nie Intake-Ziel und nie Datenquelle. Siehe „Physisches Backup“ unten.

## Voraussetzungen

- Ausführung lokal auf dem Betreiberrechner (Windows, PowerShell), nicht in der Cloud-Umgebung; Python 3.12; Repository ausgecheckt
- `PROMAT_LOCAL_ARCHIVE_ROOT` ist gesetzt und zeigt auf das lokale Archiv (oder `--archive-root` wird übergeben)
- Kein Zugriff auf Produktion nötig; keine Geheimnisse
- Alle Befehle: `python scripts\research_data_intake\archive_preservation.py <befehl> ...`. Schreibende Befehle sind ohne `--execute` ein Dry-Run.

## Schritte

Platzhalter `<ZIEL>` = der konkrete Zielordner, z. B. `K:\Pronunciation_Matters`. Der Pfad steht nirgends im Code; er wird nur hier und in der Konfiguration genannt.

1. **Erreichbarkeit prüfen.** `Test-Path K:\` muss `True` liefern. Sonst Laufwerk/Netzwerk klären; nicht fortfahren.
2. **Zielordner anlegen.** `New-Item -ItemType Directory K:\Pronunciation_Matters` (oder den vom Betreiber gewählten Ordner). Schlägt das mit „Zugriff verweigert“ fehl, hat das Konto kein Anlegerecht im Wurzelverzeichnis von `K:`; dann muss der Ordner durch die Dateiablage-Verwaltung angelegt oder das Recht erteilt werden. Nicht auf andere Projektordner (z. B. `K:\Corapan`) ausweichen. Stand 2026-10-05: der Ordner existiert nicht und das Betreiberkonto kann ihn nicht anlegen.
3. **Schreibzugriff prüfen.** Das Kopierwerkzeug legt Marker `PRESERVATION_ROOT.json` an und führt eine Schreib-/Lese-Probe aus (nur mit `--execute`). Schlägt sie fehl, bricht es ab (Exit-Code 2). Zusätzlich manuell: Datei anlegen, lesen, löschen (nur die Probedatei).
4. **Baseline-Fixity erzeugen** (additiv; nur neue Dateien unter `fixity/baseline/`):
   ```powershell
   python scripts\research_data_intake\archive_preservation.py baseline --report-dir tmp\preservation-reports
   python scripts\research_data_intake\archive_preservation.py baseline --execute --report-dir tmp\preservation-reports
   ```
   Der Bericht nennt Einheiten mit `incomplete_unreadable_files` (kein Baseline, erst Dateien klären), `baseline_drift` und `covered_by_unit_manifest`.
5. **Kopie im Dry-Run.**
   ```powershell
   python scripts\research_data_intake\archive_preservation.py copy --preservation-root K:\Pronunciation_Matters --report-dir tmp\preservation-reports
   ```
   Erwartet: alle Einheiten `would_preserve`; keine `failed`. Konflikte (`conflict_destination_mismatch`) werden nie überschrieben: Ursache klären.
6. **Kopie ausführen** (wiederaufnehmbar, bei Abbruch einfach erneut starten):
   ```powershell
   python scripts\research_data_intake\archive_preservation.py copy --preservation-root K:\Pronunciation_Matters --execute --report-dir tmp\preservation-reports
   ```
7. **Alle Dateien verifizieren** (vollständige SHA-256-Prüfung der Ablage):
   ```powershell
   python scripts\research_data_intake\archive_preservation.py verify --preservation-root K:\Pronunciation_Matters --report-dir tmp\preservation-reports
   ```
   Exit-Code 0 erforderlich.
8. **Erhaltungszustand festhalten.** Die Quittungen entstehen bei Schritt 6 automatisch (`PROMAT_LOCAL_ARCHIVE_ROOT\preservation\receipts\` und `<ZIEL>\_preservation\receipts\`); die Berichte aus Schritt 4–7 zusammen mit `status` ablegen:
   ```powershell
   python scripts\research_data_intake\archive_preservation.py status --preservation-root K:\Pronunciation_Matters --report-dir tmp\preservation-reports
   ```
9. **Root konfigurieren.** Dauerhaft `PROMAT_PRESERVATION_ROOT=K:\Pronunciation_Matters` setzen (Benutzer-Umgebungsvariable oder lokale `.env`, nie ins Git). `PROMAT_LOCAL_ARCHIVE_ROOT` bleibt unverändert auf dem lokalen Archiv; es wird nicht auf `K:` umgestellt.
10. **Inventar erneut laufen lassen:** `python scripts\storage_inventory.py` (liest `PROMAT_PRESERVATION_ROOT`, zeigt Zustände je Einheit und nicht abgedeckte Archivwurzel-Einträge). Optional mit dem Bericht aus Schritt 11 (`--cleanup-report`); das Inventar bleibt read-only.
11. **Erst dann Duplikate identifizieren:**
    ```powershell
    python scripts\research_data_intake\archive_preservation.py cleanup-report --preservation-root K:\Pronunciation_Matters --candidate-dir <lokaler-Batch-Ordner> --report-dir tmp\preservation-reports
    ```
    Nur Einheiten im Zustand `LOCAL_CLEANUP_ELIGIBLE` und Dateien unter `duplicates` sind Kandidaten. Der Bericht ist keine Anweisung; Löschen bleibt eine ausdrückliche Betreiberaktion außerhalb dieses Werkzeugs. Quell-Batch-Ordner mit `not_covered`-Dateien nicht löschen.

### Spätere Umzüge der Ablage

`copy --archive-root <alter Root>\archive --preservation-root <neuer Root> --execute`, danach `verify` gegen den neuen Root und `PROMAT_PRESERVATION_ROOT` umstellen. Einheiten gelten für einen neuen Root erst nach dessen verifizierter Kopie wieder als erhalten.

### Optionen

- `--unit "sessions/es/*"` begrenzt auf Einheiten (wiederholbar)
- `--exclude-secure` kopiert ohne `secure/`; solche Einheiten werden **nie** `PRESERVED`
- `--report-dir` schreibt `<befehl>-<zeit>.json` und `.md`

## Verifikation

- `verify` Exit-Code 0; Zusammenfassung zeigt `LOCAL_CLEANUP_ELIGIBLE` = Einheitenzahl
- Dry-Run-Berichte enthalten keine `failed`-Einheiten

## Risiken und Rückbau

- Windows-Langpfade: Dateioperationen nutzen das `\\?\`-Präfix; zusätzlich `LongPathsEnabled` in Windows setzen. Die Pfadumwandlung ist getestet; Baseline, Dry-Run, Kopie, `verify` und `status` liefen am 2026-10-05 lokal auf Windows (Probe auf `C:`, siehe `docs/agent-runs/2026-10-05_preservation-activation-organizer-equivalence.md`). Ein Lauf gegen das Netzlaufwerk `K:` steht noch aus.
- Eine Baseline dokumentiert den **heutigen** Inhalt, nicht historische Korrektheit.
- Rückbau: Baselines/Quittungen/Berichte sind reine Zusatzdateien und können gelöscht werden; Archivinhalt wird nie verändert. Die Ablage selbst wird von keinem Werkzeug gelöscht.

## Physisches Backup

Zusätzliche, physisch getrennte Kopie der Archiv-Einheiten auf einem externen Datenträger. Sie verwendet dieselbe verifizierte Kopie wie die Preservation, ist aber eine eigene Rolle: eigener Marker (`BACKUP_ROOT.json`), eigene Quittungen (`PROMAT_LOCAL_ARCHIVE_ROOT\backup\receipts\`, `<BACKUP>\_backup\receipts\`), eigene Zustände (`BACKUP_PENDING`, `BACKED_UP`). Ein Backup macht keine Einheit `PRESERVED` und nie `LOCAL_CLEANUP_ELIGIBLE`.

`<BACKUP>` = der in `PROMAT_BACKUP_ROOT` konfigurierte Ordner auf dem Backup-Datenträger. Sein übergeordneter Ordner muss existieren; den Backup-Ordner selbst legt `backup-copy --execute` an.

1. **Datenträger anschließen**, Erreichbarkeit prüfen (`Test-Path <übergeordneter Ordner>`).
2. **Dry-Run:** `python scripts\research_data_intake\archive_preservation.py backup-copy --report-dir tmp\preservation-reports` — erwartet: alle Einheiten `would_back_up`, keine `failed`.
3. **Kopie ausführen** (additiv, wiederaufnehmbar): `... backup-copy --execute --report-dir tmp\preservation-reports` — erwartet: alle Einheiten `backed_up`.
4. **Zusatzbestände sichern** (alles Nicht-Regenerierbare außerhalb der Archiv-Einheiten), aus dem Repo-Root:
   ```powershell
   python scripts\research_data_intake\archive_preservation.py backup-supplemental --execute `
     --extra "intake_workbooks=scripts/research_data_intake/import/*/*.xlsx" `
     --extra "research_player_config=data/config/research_player" `
     --report-dir tmp\preservation-reports
   ```
   Ohne `--extra` werden die übrigen Archivwurzel-Ordner (z. B. `praat_pipeline/`, `informanten_intake_*`) und `fixity/` gesichert. Jeder Lauf schreibt unter ein Label (Standard: UTC-Datum) nach `<BACKUP>\supplemental\<label>\`. Hat sich eine Quelle seit diesem Label geändert, meldet der Lauf `conflict_manifest_differs` und ersetzt nichts: dann mit neuem `--label` sichern.
5. **Kalt verifizieren:** `... backup-verify --unbuffered --report-dir tmp\preservation-reports`. Exit-Code 0, `BACKED_UP` = Einheitenzahl und `supplemental_failed=0` erforderlich. `--unbuffered` liest jede Datei am Dateicache des Rechners vorbei direkt vom Datenträger; ein Verify ohne diese Option unmittelbar nach dem Kopieren kann aus dem Arbeitsspeicher bedient werden. Ein Ab- und Wiederanstecken ist dafür nicht nötig.
6. **Nach jedem neuen Batch** Schritte 1–5 wiederholen; `backup-status` zeigt, welche Einheiten `BACKUP_PENDING` sind. Regelmäßig `backup-verify` laufen lassen, auch ohne neue Daten.

Regeln:

- Das Werkzeug löscht und überschreibt auf dem Backup nichts. Weicht eine Zieldatei vom erwarteten Inhalt ab, meldet es `conflict_destination_mismatch` und bricht für diese Einheit ab: Ursache klären (defekter Datenträger oder veränderte Quelle), nicht von Hand „reparieren“.
- Ist der Datenträger nicht angeschlossen, melden `backup-status` und `storage_inventory.py` das als Zustand; App und Intake sind davon nicht betroffen.
- Ein Ordner mit `PRESERVATION_ROOT.json` wird als Backup-Root abgelehnt und umgekehrt; beide Roots dürfen weder gleich noch ineinander verschachtelt sein noch im lokalen Archiv liegen.
- `backup-copy` deckt nur `sessions/` und `batches/` ab. Archivwurzel-Ordner wie `praat_pipeline/`, die Fixity-Baselines, die aktuellen Intake-Workbooks der Batch-Ordner und die Task-Kataloge unter `data/config/research_player/` kommen über `backup-supplemental` (Schritt 4) ins Backup.
- Das Backup enthält personenbezogene Daten im Klartext (`secure/`, Workbooks, Sprachaufnahmen). NTFS-Rechte schützen einen externen Datenträger nicht; Schutz bieten nur Verschlüsselung des Datenträgers (z. B. BitLocker To Go) und persönliche Verwahrung.
- Wiederherstellung ist eine Betreiberaktion: Einheit aus `<BACKUP>\archive\...` zurückkopieren und mit `baseline` bzw. `backup-verify` gegen die Fixity prüfen. Das Backup wird nie als `PROMAT_LOCAL_ARCHIVE_ROOT` eingetragen.
