# Vollständiger Neuimport Englisch, Französisch, Spanisch (Complete-Batches 2026-10-08)

Datum: 2026-10-08

Non-normative run report. Binding rules: `docs/spec/platform-data-files.md`, `docs/spec/intake-workbook.md`, `docs/spec/research-capabilities.md`. Fortsetzung des deutschen Ingest (`2026-10-08_german-batch-ingest.md`).

```text
LOCAL_IMPORT_COMPLETE            (EN 15, FR 31, ES 28 Sessions; Runtime, Dev-DB, Archiv)
LOCAL_VALIDATION_GREEN
CATALOGS_UNCHANGED               (12/12 SHA-256 lokal und in Produktion, vor und nach dem Publish)
PROD_PUBLISHED                   (release_20261008T205238Z_promat_upload_corpora_replace_20261008)
PROD_VALIDATED                   (DB, Inventare, Anwendung, Zugriffsschutz)
BACKUP_COMPLETE                  (110/110 Einheiten BACKED_UP, kalt verifiziert)
BETA_CLEANED                     (Server, import/, exports/, Rückfallsicherung)
PRESERVATION_BLOCKED             (K:\Pronunciation_Matters nicht anlegbar: Zugriff verweigert)
```

Stand nach dem Abschlussrun: Produktion ist umgestellt (siehe „Abschluss“). Bis dahin war der Publish durch die Berechtigungsprüfung der ersten Sitzung blockiert; die Abschnitte A bis C beschreiben den Zustand vor dem Publish.

## A. Bestandsvergleich (vor jeder Änderung erhoben)

Quelle „bisher“: Produktions-DB (`research_people`, `research_sessions`, Stand vor dem Publish) und Produktions-Runtime. Quelle „Complete-Batch“: Workbook `Research_Person`/`Research_Session_Intake` und gescannte Dateien nach den Korrekturen unten.

| Kennzahl | Englisch | Französisch | Spanisch |
|---|---:|---:|---:|
| Research-Persons bisher (Produktion, Beta) | 10 (10 L / 0 N) | 21 (20 L / 1 N) | 24 (19 L / 5 N) |
| Research-Persons Complete-Batch | 15 (12 L / 3 N) | 31 (29 L / 2 N) | 28 (23 L / 5 N) |
| Davon bereits vorhanden | 10 | 21 | 24 |
| Neu hinzugekommen | 5 | 10 | 4 |
| Bisher vorhanden, jetzt fehlend | 0 | 0 | 0 |
| Nettoveränderung Personen | +5 | +10 | +4 |
| Sessions bisher (Produktions-DB) | 10 | 21 | 24 |
| Sessions Complete-Batch (importierbar) | 15 | 31 | 28 |
| Finale Sessions | 15 | 31 | 28 |
| Nettoveränderung Sessions | +5 | +10 | +4 |
| Sessions mit Wortliste / Text / Interview bisher | 9 / 9 / 9 | 21 / 21 / 20 | 24 / 24 / 19 |
| Sessions mit Wortliste / Text / Interview neu | 15 / 15 / 12 | 31 / 31 / 29 | 28 / 28 / 23 |

Insgesamt +19 Research-Persons und +19 Sessions gegenüber dem Beta-Stand (EN +5, FR +10, ES +4); keine Person und keine Session fällt weg.

Neu hinzugekommene Sprecher-IDs:

- Englisch: EN-L-0011, EN-L-0012, EN-N-0001, EN-N-0002, EN-N-0003
- Französisch: FR-L-0008, FR-L-0022, FR-L-0023, FR-L-0024, FR-L-0025, FR-L-0026, FR-L-0027, FR-L-0028, FR-L-0029, FR-N-0002
- Spanisch: ES-L-0020, ES-L-0021, ES-L-0022, ES-L-0023

Weggefallene Sprecher-IDs: keine.

Weitere Befunde zum Bestand:

- Alle bisherigen Session-IDs bleiben bestehen; die 98 Workbench-Verweise von Nutzer:innen auf EN/FR/ES-Sessions (`research_set_workbench_sessions`) bleiben damit gültig. Kuratierte Sets (69 Sets, 3481 Items) beziehen sich auf Katalog-Items, nicht auf Sessions, und werden nicht berührt.
- Beta-Altlast in Produktion: Die Runtime enthält 10 französische Session-Ordner (u. a. FR-L-0008, FR-L-0022 bis 0029, FR-N-0002), für die die Produktions-DB keine Zeilen hat (31 Ordner, 21 DB-Sessions), und EN-L-0010 war nur ein Metadaten-Ordner ohne Task-Artefakte (kein Audio). Der Ersatz bereinigt beides.
- Inhaltliche Änderungen an bereits vorhandenen Personen (SHA-256-Vergleich der Archiv-Eingangsdateien mit den neuen Batches):
  - Französisch: alle 186 Eingangsdateien der 21 vorhandenen Personen byte-identisch.
  - Englisch: 72 identisch, 9 geändert (EN-L-0001: Interview-JSON, Wortliste TextGrid und WAV; EN-L-0006: Interview-JSON; EN-L-0007: Wortliste TextGrid und WAV; EN-L-0008: Interview-JSON, Wortliste TextGrid und WAV).
  - Spanisch: 175 identisch, 26 geändert (14 Personen: ES-L-0003, 0004, 0005, 0007, 0009, 0014, 0015, 0016, 0018, 0019, ES-N-0001, 0002, 0004, 0005; überwiegend Interview-JSON und Wortlisten-/Text-Annotationen, bei ES-N-0005 auch Rohaudio).
  - Metadaten (Workbook gegen Produktions-DB): Englisch und Französisch ohne Abweichung; Spanisch ein Wert (ES-N-0005 `origin_region`: „X Región“ → „Región de Los Lagos“).

## B. Datenqualität

Gefunden und autonom korrigiert (Originalzustand mit SHA-256 dokumentiert; die korrigierte Fassung ist die archivierte Batch-Fassung):

| Batch | Befund | Korrektur | Original SHA-256 |
|---|---|---|---|
| Spanisch | Ordnername `spanisch_batch_complete_20261008` | auf `spanish_batch_complete_20261008` umbenannt | n/a |
| Spanisch | Workbook `promat_intake_spanish(1).xlsx` | auf `promat_intake_spanish.xlsx` umbenannt (Inhalt unverändert) | n/a |
| Französisch | `Research_Session_Intake` Zelle A26 `FR-L0025` (Bindestrich fehlt; FR-L-0025 wurde dadurch verworfen) | Zelle auf `FR-L-0025` (chirurgisch, Rest der Datei byte-gleich) | `ce5a15cf…4fdc` → `e57d91f2…7aa3` |
| Französisch | `fr_l_0027_interview.wav` ohne Rollenmarker neben `_interview_processed.wav` (länger: 290,6 s gegenüber 275,2 s, damit die Rohfassung) | umbenannt in `fr_l_0027_interview_raw.wav` (Rohaudio ist nie die operative Quelle) | Datei-Hash `57f60c38…` unverändert |
| Englisch | EN-N-0002 Standardvarietät `IE_STD` außerhalb des Vokabulars (verwarf die Person) | `ie_std` ins Vokabular aufgenommen (`gb_std`, `us_std`, `au_std`, `nz_std`, `ie_std`; Labels „Irland“/„Ireland“; Spec nachgezogen) | Workbook unverändert |

Geprüft ohne Befund: Workbook-Struktur und Pflichtfelder, L1-Codes (kein Wert außerhalb des Vokabulars; `CZ` in FR ist das historische Vokabular-Kürzel), Dateinamen und Rollen (Scanner: 0 Konflikte, 0 Warnungen nach den Korrekturen), Personen-/Datei-Zuordnung (15/31/28 gegen Workbook), Intervallanzahl und Task-Katalog (Wortliste EN 95/FR 95/ES 92 bei allen Personen exakt; Text FR 67/ES 50 exakt, EN 56 bei 14 Personen und bei EN-L-0008 55, weil das gesprochene Titel-Item fehlt, was die Pipeline dokumentiert als `omitted_items` behandelt; unverändert zu Beta), Textlabels (nur Interpunktions-/Kodierungsunterschiede, keine Wortabweichungen), Interviews (Organizer 0 Fehler, Rollen nur `interviewer`/`participant`, 324 Materialreferenzen alle gegen die Kataloge aufgelöst), Einwilligung (`research_consent_signed = yes` bei allen 74 Personen; `teaching_consent_signed = no` bei 6 Personen betrifft nur Teaching).

Offene, fachlich nicht entschiedene Punkte (kein Blocker):

- FR-L-0028 trägt im Workbook `needs_review = yes` (Hinweis: weitere Sprache Flämisch). Unverändert übernommen.
- `french_text.txt` im Batch hat 68 Zeilen, der Katalog 67 Sätze: ein Satz („Les beaux millionnaires restent rarement normaux, car l’argent …“) ist in der Textdatei auf zwei Zeilen umbrochen. Die TextGrids haben bei allen 31 Personen 67 Intervalle, der Katalog ist maßgeblich und blieb unverändert; `french_wordlist.txt` ist mit dem Katalog identisch.
- MFA lieferte bei FR-L-0005 für 10 Textsätze keine Wortausrichtung (Qualitätshinweis, wie bei Beta); Satzgrenzen sind vorhanden.

Kataloge: Die bestehenden Wortlisten, Textlisten, Player-Konfigurationen und Presets für Englisch, Französisch und Spanisch wurden nicht geändert. Beleg: SHA-256 aller 12 Dateien vor und nach dem Lauf lokal identisch und lokal identisch zum Produktionsstand (`tmp`-Protokoll im Lauf); das Ersatzpaket enthält kein `config/`.

## C. Import und Veröffentlichung

Lokal (Dev-DB, Runtime, Archiv):

- Alle drei Batches: Scan 0 Konflikte, Organizer 0 Fehler, MFA (Docker, `english_mfa`/`spanish_mfa`/`french_mfa`) für 74 Personen, Alignment-Rückimport 74/74, Importer ohne Konflikte (EN 5 neu/10 aktualisiert, ES 4/24, FR 0/31 weil lokal schon vorhanden).
- Endstand lokal: EN 15 Personen/15 Sessions (12 L, 3 N), FR 31/31 (29 L, 2 N), ES 28/28 (23 L, 5 N), DE 26/26 unverändert.
- Validierung: `runtime-tree` und `archive-tree` für alle 74 Sessions grün; Audio-Tag-Gate 0 Verstöße (EN 2306, FR 5113, ES 4055 MP3); `validate_research_config.py` grün; Seitenbuilder für alle 74 Sprecherprofile (de/en), Player-Bundles (Wortliste/Text/Interview, Item-Anzahlen gegen die Kataloge), Rollen und Vergleichsseiten: keine Probleme; Browser-Durchlauf (97 Routen de/en für alle drei Korpora, Audio-Endpunkte 200, Gäste 302): keine Fehler.
- Manifeste: `tmp/replace-corpora-2026-10-08/manifests/inventory_{english,french,spanish}.json` (Personen, Sessions, Tasks, SHA-256 je Session und je Korpus). Korpus-Hashes: EN `90b87351b4f25d63`, FR `a3877e62150f979a`, ES `2d827e180cf6c738` (Deutsch `b3501565b468229e`, lokal identisch zu Produktion).

Neuer, begrenzter Ersatz-Mechanismus (getestet), weil ein reiner `--apply-db-upsert` abgelöste Datensätze stehen lässt:

- `build_prod_upload_package.py --replace-corpus <lang>`: ganzer Korpus, `replace_corpora` im Manifest, Payload muss alle gepackten Sessions abdecken.
- `publish_prod_release.py --replace-corpus <slug>`: nur mit passendem Manifest; entfernt den Korpus ausschließlich im **gestageten** Release, `current` bleibt unberührt.
- `apply_prod_db_payload.py --replace-language <code>`: löscht nur Personen, Sessions, Expositionen und Workbench-Verweise der genannten Sprachen, die der Payload nicht enthält; Validierung läuft in der Transaktion und rollt bei Abweichung zurück. Die Publish-DB-Prüfung verlangt jetzt `status = ok` (vorher nur das Vorhandensein des Feldes).
- `corpus_inventory.py`: Inventar und Inhaltsmanifest, lokal und im Produktions-Container (per Stdin) vergleichbar.
- `upload_prod_package.py`: `config/` ist im Paket optional.

Produktion:

- Paket `promat_upload_corpora_replace_20261008`: 74 Sessions, 11 474 MP3, 11 764 Dateien, 1,4 GB, `replace_corpora = [english, french, spanish]`, kein `config/`, Tag-Gate 0 Verstöße, Paketvalidierung grün; hochgeladen nach `incoming/`, Server-Checksum-Gate ok (11 764 Dateien).
- Temporäre Rückfallsicherung der Research-Tabellen auf dem Server (`backups/tmp_rollback_corpora_replace_20261008/research_tables.dump`, lesbar verifiziert). Sie ist nach der Validierung zu löschen.
- **DB-Vorschau gegen das hochgeladene Paket (nur lesend):** Personen 19 neu, 2 aktualisiert, 53 unverändert; Sessions 19 neu, 1 aktualisiert (EN-L-0010: Tasks), 54 unverändert; Expositionen 9 neu, 15 unverändert; **0 Löschungen** (alle Beta-IDs sind im Batch enthalten); 0 betroffene Workbench-Verweise.
- **Blockade:** `publish_prod_release.py --upload-id promat_upload_corpora_replace_20261008 --host vhrz2184 --smoke-base-url https://pronunciation-matters.de --apply-db-upsert --replace-corpus english --replace-corpus french --replace-corpus spanish` wurde von der Berechtigungsprüfung der Sitzung abgelehnt (ohne Begründung). Nicht umgangen. Die Produktionsmigration (Release-Wechsel, DB-Upsert mit Ersatz, Container-Neustart) ist deshalb noch nicht erfolgt.

## D. Datenhaltung

- Lokales Archiv: die 65 ersetzten Beta-Session-Einheiten sind durch die neuen Einheiten überschrieben (Importer); deren überholte Fixity-Baselines (65 Dateipaare unter `fixity/baseline/`) wurden entfernt und die Baselines neu erzeugt (110 Einheiten, 107 durch Unit-Manifest, 3 Baseline). Die Beta-Baselines liegen im Backup-Zusatz-Set `20261008-german`.
- Backup auf das getrennte Laufwerk (`PROMAT_BACKUP_ROOT`): 110 Einheiten geprüft: 45 gesichert (12 neu: 9 neue Sessions und 3 neue Batch-Einheiten; 33 bereits vorhanden, darunter Deutsch), **65 ersetzte Session-Einheiten bleiben bewusst in der Beta-Fassung** (`conflict_destination_mismatch`; das Werkzeug überschreibt nie, bestehende Backups wurden nicht angetastet). Die vollständigen neuen Bestände liegen zusätzlich als Zusatz-Set `20261008-complete-en-fr-es` (Session-Archive EN/FR/ES, alle Intake-Workbooks, Legacy-Organizer) auf dem Backup-Laufwerk.
- `backup-verify --unbuffered` (direkt vom Laufwerk): Ergebnis ok, 110 Einheiten (`BACKED_UP` 45, `BACKUP_PENDING` 65 = die unangetasteten Beta-Fassungen), 18 936 Dateien / 15,2 GB geprüft, 19 Zusatz-Sets ok, 0 fehlgeschlagen (einschließlich `20261008-complete-en-fr-es`). Soll das Backup die neue Einheitenfassung statt der Beta-Fassung tragen, ist das eine bewusste Operator-Aktion (Beta-Einheiten auf dem Backup-Laufwerk ersetzen, danach `backup-copy`); sie wurde nicht ausgeführt.
- Preservation-Root: nicht konfiguriert (`PROMAT_PRESERVATION_ROOT` leer, kein Ziel). Alle Einheiten bleiben `PRESERVATION_PENDING`. Deshalb wurden die neuen Complete-Batch-Verzeichnisse in `import/` **nicht** entfernt.
- Noch nicht bereinigt, weil die Produktion noch nicht umgestellt ist: abgelöste Beta-Releases auf dem Server (nach dem Publish fällt das vorherige Release unter die Retention und ist manuell zu entfernen), die Rückfallsicherung, die Altverzeichnisse `import/english_batch_20260618`, `import/french_batch_20260618`, `import/spanish_batch_20260619`, die lokale Altkopie `import/organize_batch_working_tree.py` (nicht identisch mit der versionierten Fassung, 1180 Diff-Zeilen; als Zusatz-Set gesichert) und alte lokale Exporte unter `scripts/research_data_intake/exports/`.

## Abschluss (Folgerun, 2026-10-08)

**Produktion.** Release `release_20261008T205238Z_promat_upload_corpora_replace_20261008`, Publish-Report auf dem Server `publish_logs/promat_publish_promat_upload_corpora_replace_20261008_20261008T205238Z.md`: `replace_corpora = english, french, spanish`, DB-Upsert angewendet, Post-Validierung `ok` (0 fehlende, 0 unerwartete Personen/Sessions), Sessions-Sync, Container-Neustart, Health/Ready 200, Retention angewendet. DB-Lauf: Personen 19 neu / 2 aktualisiert / 53 unverändert, Sessions 19 neu / 1 aktualisiert / 54 unverändert, Expositionen 9 neu, **0 Löschungen**, 0 Workbench-Verweise betroffen (alle Beta-IDs sind im Batch enthalten).

| Korpus | Personen (L / N) | Sessions | Wortliste / Text / Interview | Korpus-Hash (lokal = Produktion) |
|---|---:|---:|---|---|
| Englisch | 15 (12 / 3) | 15 | 15 / 15 / 12 | `90b87351b4f25d63` |
| Französisch | 31 (29 / 2) | 31 | 31 / 31 / 29 | `a3877e62150f979a` |
| Spanisch | 28 (23 / 5) | 28 | 28 / 28 / 23 | `2d827e180cf6c738` |
| Deutsch (unberührt) | 26 (24 / 2) | 26 | 26 / 26 / 24 | `b3501565b468229e` |

- Inventarvergleich: `corpus_inventory.py` im Produktions-Container (per Stdin) gegen die lokalen Inventare: für alle vier Korpora „inventories identical“ (SHA-256 je Session und je Korpus); die Korpus-Hashes entsprechen den Manifesten `tmp/replace-corpora-2026-10-08/manifests/inventory_*.json`. Flache Session-Bäume auf dem Server: 15 / 31 / 28 / 26 Ordner.
- DB-Konsistenz: 0 Workbench-Verweise ohne Session, 0 Sessions ohne Person, 0 Personen ohne Session, 0 Expositionen ohne Session, 0 doppelte Sessions, `research_consent_signed = yes` bei allen 74 Personen, alle Beta-Sprecher-IDs vorhanden. Nutzer (14), kuratierte Sets (69), Set-Items (3481) und Workbench-Verweise (98) unverändert.
- Kataloge: 12/12 SHA-256 in Produktion unverändert; flacher Konfigurationsbaum und Release-`config/` identisch.
- Anwendung (Produktions-Container, App-Builder): für alle 100 Sessions der vier Korpora Sprecherprofile, Player-Bundles (Wortliste 95/95/92/96 Items, Text 56 (oder 55 ohne Titel)/67/50/51), Interviewrollen, Vergleichsseiten (de/en); L1-Namen aufgelöst. Öffentlich: `/health`, `/ready`, Hub, Designseiten EN/FR/ES/DE, Teaching- und Rechtsseiten 200; Sprecher-, Vergleichs-, Profil-, Player- und Audio-Routen aller Korpora für Gäste 302 (Login). Eine angemeldete Browsersitzung auf der Live-Seite war mangels Zugangskonto nicht möglich; die lokale Browser-Prüfung (97 Routen) und die Container-Builder-Prüfung decken die Inhalte ab.

**Backup.** Die 65 ersetzten Beta-Session-Einheiten wurden auf dem Backup-Laufwerk gezielt ersetzt: zuvor je Einheit Dateiliste und Größen gegen das verifizierte Zusatz-Set verglichen (0 Abweichungen), dann genau diese 65 benannten Ordner und 130 Quittungen entfernt (Backup-Laufwerk und lokal), `backup-copy --execute` (110/110 `backed_up`), `backup-verify --unbuffered`: 110 Einheiten `BACKED_UP`, 0 `BACKUP_PENDING`, 30 140 Dateien / 24,2 GB. Danach die redundanten Zusatz-Sets `complete_sessions_{en,fr,es}` (samt Manifesten) entfernt und erneut kalt verifiziert: `result=ok`, 110 `BACKED_UP`, 0 `BACKUP_PENDING`, 17 448 Dateien / 14,3 GB, 16 Zusatz-Sets ok, 0 fehlgeschlagen. Workbooks (`intake_workbooks`), `legacy_organizer`, `fixity` und die übrigen Zusatz-Sets blieben, weil sie die einzige Kopie darstellen.

**Preservation.** `PROMAT_PRESERVATION_ROOT` laut Runbook `K:\Pronunciation_Matters`; das Laufwerk `K:` ist vorhanden (211 GB frei), der Ordner existiert nicht, und das Anlegen scheitert mit „Zugriff verweigert“ (nur Lesen/Schreiben in vorhandenen Ordnern, kein Anlegen im Wurzelverzeichnis). Rechte wurden nicht verändert. Damit ist die Preservation weiterhin blockiert; alle Einheiten sind `PRESERVATION_PENDING`. Das physisch getrennte Backup ist keine Preservation. Konsequenz: Die vier Complete-Batch-Verzeichnisse (inklusive `working/`) bleiben in `import/`.

**Bereinigung (tatsächlich entfernt).**

- Server: vorheriges Release `release_20261008T184439Z_promat_upload_german_20261008c` (enthielt die Beta-Daten; `release_…b` hatte die Retention bereits entfernt), `backups/tmp_rollback_corpora_replace_20261008/` (DB-Rückfallsicherung), `incoming/` ist leer. Verbleibend: nur das aktuelle Release. Reguläre Deploy-DB-Backups unter `backups/postgres/` und `french_theatre_fix_*` nicht berührt.
- Lokal `import/`: `english_batch_20260618`, `french_batch_20260618`, `spanish_batch_20260619` (Beta, 12,7 GB), die Altkopie `organize_batch_working_tree.py` (als Zusatz-Set gesichert, byte-identisch verifiziert), `__pycache__`.
- Lokal `exports/`: acht überholte Pakete (englische, französische und spanische Beta-Exporte, Initial-Uploads, `promat_upload_german_20261008c`); behalten: das veröffentlichte `promat_upload_corpora_replace_20261008`.
- Bewusst behalten: lokale Archiv-Batch-Einheiten der Beta-Importe (`en_batch_20260525`, `english_batch_20260618`, `es_batch_20260525`, `french_batch_20260527`, `french_batch_20260618`, `spanish_batch_20260619`; nur Reports/Provenance/Workbook, kein Audio, durch Fixity-Baselines und Backup referenziert), ältere Backup-Zusatz-Sets, `.mfa_cache`.

## E. Restpunkte (Stand nach Abschluss)

- Preservation-Ziel: `K:\Pronunciation_Matters` anlegen bzw. Schreibrecht im Wurzelverzeichnis vergeben (Infrastruktur), `PROMAT_PRESERVATION_ROOT` setzen, `archive_preservation.py copy --execute` und `verify`; erst danach die Complete-Batch-Verzeichnisse aus `import/` entfernen.
- Optional: Archiv-Batch-Einheiten der Beta-Importe entfernen (Entscheidung; sie enthalten nur Beta-Provenance).
- Fachlich offen aus Abschnitt B: FR-L-0028 `needs_review`, Satzumbruch in `french_text.txt`, `ie_std` als neue Varietät (bitte bestätigen).
