# German batch ingest (german_batch_complete_20261008)

Datum: 2026-10-08

Non-normative run report. Binding rules: `docs/spec/platform-data-files.md`, `docs/spec/intake-workbook.md`, `docs/spec/research-capabilities.md`.

## Ziel

Erster vollständiger Intake des deutschen Korpus (26 Personen: 24 Lernende mit L1 Französisch, Kabylisch, Russisch, Spanisch sowie 2 Muttersprachler:innen) vom Drop-in-Batch bis zur lokalen Runtime, zur Dev-DB, zum lokalen Archiv und zur Produktion.

## Consulted Sources

- `docs/spec/platform-data-files.md` (Intake Batch Working Filesystem, Storage Roots)
- `docs/spec/intake-workbook.md` (`l1_code`)
- `docs/spec/research-capabilities.md` (korpusspezifische Oberflächen)
- `docs/runbooks/research-intake-working-pipeline.md`, `research-prod-upload-and-publish.md`, `local-storage-hygiene.md`
- `scripts/research_data_intake/` (Scanner, Organizer, Importer, MFA-Schritte, Validatoren)

## Befund im Batch

- 228 Dateien in vier L1-Unterordnern plus `Muttersprachler/`; der Scanner klassifizierte alle strikt über den Dateinamen, die Unterordner stören nicht.
- Unsaubere Dateinamen, die der Scanner trotzdem eindeutig erkennt und die deshalb **nicht umbenannt** wurden (Originalnamen bleiben so im Archiv-Manifest erhalten): `de-l-0014_wordlist_raw.wav` (Bindestriche), `DE_L_0003`/`DE_L_0011` `..._interview_processed.wav` (Großbuchstaben), `de_l_0022_Interview_*` (Großbuchstabe), `de_n_0001_wordlist_raw .wav` (Leerzeichen vor der Endung).
- `wordlist.txt` (96 Einträge) und `text.txt` (51 Sätze) liegen als cp1252 vor und waren bisher kein Teil des Katalogs.
- Alle 26 Wortlisten-TextGrids haben 96, alle Text-TextGrids 51 gesprochene Intervalle (nach den Korrekturen unten).

## Geänderte Bereiche

- `data/config/research_player/german/` (lokal, git-ignoriert; geht über das Upload-Paket mit `--include-research-player-config` nach Prod): `task_catalogs/wordlist.json` (96 Items, `wl_001`–`wl_096`), `task_catalogs/text.json` (51 Items, `t_01`–`t_51`, `sentence_list`), `player_config.json`, `phenomena_presets.json` (leer). Texte stammen unverändert aus den `.txt`-Dateien; nur äußere Leerzeichen wurden entfernt (`Morgen\t` in Zeile 82, ein Leerzeichen am Ende von Satz 19).
- `app/src/app/config/data_conventions.py`, `docs/spec/intake-workbook.md`: L1-Vokabular um `KAB` (Kabylisch), `NMG` (Ngumba/Kwasio), `RCF` (Réunion-Kreol), `DUA` (Duala) erweitert (ISO 639-3, Entscheidung der Betreiber:in). Keine globale Alias-Regel `KABYL`/`CREOLE`.
- `scripts/research_data_intake/alignment_export/import_interview_amberscript.py`, `docs/spec/platform-data-files.md`, `app/tests/test_research_working_tree_intake.py`: Pausenrahmen aus getrennten Wörtern (`[ . ]`, `[ ]`, `[. ]`) bleiben als einzelne Token erhalten (bisher Fehler `error_invalid_material_ref_marker`); `[ wl_025 ]` bleibt weiter ein Fehler. Zwei neue Tests.
- `app/src/app/research_player_runtime.py`, `app/src/app/i18n.py`, `app/static/css/30_components.css`, `docs/spec/platform-data-files.md`, `docs/spec/research-player.md`: Speaker-Codes `interviewer_1`/`interviewer_2` (Importer-Rollennamen, Player-Labels de/en, gleiche Badge-Familie wie `interviewer`); zwei neue Importer-Tests.
- `docs/spec/research-capabilities.md`, `app/tests/test_german_research_empty_state.py`: Aussage „German hat keine Runtime-Sessions“ korrigiert.

## Korrekturen an Quelldaten im Batch (reversibel dokumentiert)

Alle Änderungen betreffen nur die Batch-Kopie; die Originale liegen bei der Betreiber:in.

| Datei | Änderung | SHA-256 vorher → nachher |
|---|---|---|
| `DE-L-0017` Wortlisten-TextGrid | Intervall 14: Label `siilent` → `silent` (Tippfehler, wurde als 97. Wort gezählt) | `d70960ae…c4e` → `03a2b762…ab7` |
| `DE-L-0017`/`DE-L-0020` Interview-JSON | `speakers[].name` gesetzt: 0017 `spk1` „Interviewer 1“, `spk3` „Interviewer 2“; 0020 `spk1` „Interviewer 1“, `spk2` „Interviewer 2“, `spk3` „Participant“ | `0f8dfa1d…` → `00b12662…`; `70c16044…` → `5896d669…` |
| `DE-L-0008` Interview-JSON | Ein Wort `]"a"-Umlaut` (83.99–85.23 s) in `]` (83.99–84.10 s) und `"a"-Umlaut` (84.10–85.23 s) geteilt; Zeitaufteilung proportional zur Zeichenzahl | `a573eb60…992` → `56a99ade…033` |
| `promat_intake_german.xlsx` | Zellen in Blatt `Research_Person`: C, E, F (`KABYL` → `KAB`) in den Zeilen 6, 7, 8, 10, 12, 14, 15, 16; D9, E9, F9 (`NGOUMBA` → `NMG`); D13 (`CREOLE` → `RCF`, nur diese Person); D17 (`DOUALA` → `DUA`); Blatt `Vocabularies` C60–C63 auf die vier Codes. Chirurgische XML-Änderung, Rest der Datei byte-gleich (u. a. Kommentare, bedingte Formatierung) | `f2785d73…b43` → `1ef21b61…` |

## Wichtige Entscheidungen

- Kabylisch und die drei übrigen Sprachen bekommen ISO-639-3-Codes im L1-Vokabular (Betreiber:in); `CREOLE` wird ausschließlich personenbezogen für DE-L-0011 zu `RCF`.
- Pausenrahmen werden als getrennte Token belassen (Betreiber:in), weil die anderen Korpora `(.)` als ein Token führen und `( . )` bereits getrennt akzeptiert wurde.
- Interviews DE-L-0017 und DE-L-0020 (je drei Sprecher): Nach Durchsicht der Transkripte ist `spk1` jeweils die deutsche Interviewerin bzw. der deutsche Interviewer, die Übersetzung übernimmt in DE-L-0017 `spk3`, in DE-L-0020 `spk2`; die Informantin bzw. der Informant ist in DE-L-0017 `spk2`, in DE-L-0020 `spk3`. Auf Vorgabe der Betreiber:in werden die Rollen `interviewer_1` (Interview), `interviewer_2` (Übersetzung) und `participant` genannt. Umsetzung: neue Speaker-Codes `interviewer_1`/`interviewer_2` (Labels „Explorator:in 1/2“ bzw. „Interviewer 1/2“), im Importer über explizite Rollennamen in `speakers[]` des Transkripts; bestehende Daten mit `interviewer`/`participant` bleiben unverändert. Beide Interviews sind nachimportiert (Updates der bestehenden Sessions, 0 Konflikte).
- DE-L-0025 steht nur im Workbook (keine Dateien) und wird nicht importiert (`no_delivered_task_data`).

## Abweichungen

- Keine Abweichung von der Spezifikation; Vokabular- und Importerregel sind in `docs/spec/` nachgezogen.
- Docker Desktop musste lokal gestartet werden (Dev-DB, MFA).

## Verifikation

- Scanner: 228 Dateien erkannt, 0 Konflikte; Organizer: 26 Personen, 0 Konflikte, 2 erwartete Fehler (spk3).
- MFA (Docker, `german_mfa`) für 26 Personen; Rückimport 26/26, 0 Fehler. DE-N-0002: für 9 Sätze (24, 30, 34, 35, 39, 40, 43, 44, 46) hat MFA kein TextGrid geliefert (Warnung, kein Abbruch; Satzgrenzen aus dem Segment-TextGrid sind vorhanden).
- Importer: 26 Sessions angelegt, 74 Task-Synchronisierungen (26 Wortliste, 26 Text, 22 Interview), 0 Konflikte. Dev-DB: 26 Sessions `de`, 26 Personen `DE-*`.
- `validate_research_intake.py runtime-tree` 26/26 und `archive-tree` 26/26 grün; `scan_audio_tags.py`: 3896 MP3, 0 Verstöße.
- Tests: `pytest app/tests` 1277 passed, 2 skipped; `scripts/ci_governance_checks.py` grün.
- Browser (`tmp/ui-qa/2026-10-08-german-ingest/`): `/de` und `/en` Research-Routen für Hub, Design, Sprecher:innen, Profil, Vergleich, Phänomene und Player (Wortliste, Text, Interview, Muttersprachler) alle 200; Audio-Endpunkte 200 `audio/mpeg`; anonymer Audio-Zugriff wird umgeleitet.

## Offene Punkte

- **Frage: Sprachbezeichnungen auflösen?** Die Webapp zeigt L1-Werte als ISO-Code (`KAB`, `FR`, `RCF`). Sollte sie diese in verständliche Sprachbezeichnungen auflösen (DE/EN), damit Nutzer:innen sie lesen können? Das betrifft alle Korpora und braucht eine Entscheidung zu Labels und Ort (i18n-Schicht).
- Die öffentliche Design-Seite des Deutsch-Korpus ist weiter der Zustand „in Vorbereitung“; eine Beschreibung fehlt.
- DE-L-0017, Segment 28 („Ah, okay, alles klar. Dann war es das, glaube ich, auch. Das war meine eine Nachfrage …“) ist im Transkript `spk3` (Interviewer 2) zugeordnet, klingt aber nach der deutschen Interviewerin bzw. dem deutschen Interviewer (Interviewer 1); unverändert übernommen, bitte prüfen.
- Satz 6 der Satzliste lautet im Quelltext „Das Mädchen hat hat eine hübsche neue Tasche.“ (doppeltes „hat“); unverändert übernommen, bitte gegen die Vorlage prüfen.
- Bindestrich-Varianten in der Wortliste (`sagen -sägen`, `Weg - weg`) sind unverändert aus der Vorlage übernommen.
- Preservation- und Backup-Kopie des neuen Batch-Archivs stehen aus (`PROMAT_PRESERVATION_ROOT` nicht gesetzt); `archive_preservation.py backup-copy` für die neuen Einheiten ausführen, sobald das Laufwerk verfügbar ist.

## Nächste sinnvolle Schritte

- Produktion: Der Code-Stand (L1-Codes, Importer-Regel, Spec) wurde mit Commit `d585cd9` nach `main` gepusht und läuft durch CI und `Deploy production`. Das Upload-Paket `promat_upload_german_20261008` (26 Sessions, 3896 MP3, `config/research_player/german`, `db/import_payload.json`) ist gebaut und mit `validate_research_intake.py prod-package` grün. **Upload und Publish stehen noch aus**, weil der SSH-Zugriff auf den Produktionsserver in dieser Sitzung nicht freigegeben war. Befehle: `docs/runbooks/research-prod-upload-and-publish.md` (`upload_prod_package.py` nach `incoming/`, danach `publish_prod_release.py --upload-id promat_upload_german_20261008 --apply-db-upsert`, Health, Smoke).
- Quell-Batch erst nach verifizierter Preservation-Kopie aus `import/` entfernen.
