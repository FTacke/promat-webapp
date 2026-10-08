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

## L1-Sprachbezeichnungen (Nachtrag, Folgelauf)

- Zentrale Auflösung `app/src/app/l1_display.py` mit Namen in der i18n-Schicht (`language.l1.<CODE>`, de/en, alle 61 Vokabular-Codes plus `unknown`) und ISO-Zuordnung in `app/src/app/config/data_conventions.py` (`get_l1_iso_reference`: ISO 639-1 für die meisten Codes, ISO 639-3 für `KAB`, `NMG`, `RCF`, `DUA`; das historische Vokabular-Kürzel `CZ` wird als ISO 639-1 `cs` ausgewiesen).
- Anzeige: Sprachname mit unauffälligem Info-Indikator (`pm-info-tip--inline`; Hover, Tastaturfokus, Klick/Tap, Escape schließt), Text z. B. „ISO 639-3: rcf“. Kein permanent sichtbarer Code. Unbekannte Werte bleiben unverändert sichtbar ohne Tooltip. Gespeicherte Werte, URL-Parameter (`?l1=KAB`) und Filterlogik sind unverändert.
- Betroffen: Sprecherkarten, Tabelle, Profil (L1, Weitere L1, Mutter, Vater), Badges in Player und Profil, Filter-Dropdown und Filter-Chip der Sprecherseite, Vergleich (Filter, Chip, Badge mit `title`).
- Offen/bewusst: In Vergleichszeilen (selbst interaktiv) steht der ISO-Verweis als `title` statt als eigener Indikator; `CZ` ist kein ISO-639-1-Code des Vokabulars, der Tooltip nennt `cs`.
- Verifikation: 10 neue Unit-Tests (`app/tests/test_l1_display.py`), angepasste Erwartungen in zwei Test-Dateien, neue Browser-Prüfungen in `scripts/qa/ci_browser_smoke.py` (Hover, Fokus, Escape, Klick, Touch 390 px, hell/dunkel, kein Überlauf; de/en). Gesamt: 1287 pytest, 64 JS-Tests, Ruff, Governance, Teaching-Validierung, Browser-Smoke grün.

## Produktion (Folgelauf, 2026-10-08)

- Deployment: `a6a1561` (L1-Anzeige) lief über CI und `Deploy production` erfolgreich; das Web-Image enthielt `l1_display.py` und die Codes `KAB`/`NMG`/`RCF`/`DUA`.
- Publish 1 (`promat_upload_german_20261008b`): Runtime, Release-Wechsel, Container-Neustart, Health/Ready 200. Der DB-Upsert fügte nur 2 Personen/Sessions ein, weil mein Zweipersonen-Nachimport (DE-L-0017/0020) die `import_payload.json` des Batch-Archivs überschrieben hatte. Die Runtime-Daten (26 Sessions) waren korrekt, die DB nicht.
- Korrektur: Payload mit einem vollständigen Lauf `--update-metadata` neu erzeugt (26 Personen, 26 Sessions, 20 Expositionen), Paket `promat_upload_german_20261008c` gebaut, validiert, hochgeladen und publiziert: DB-Upsert angewendet (24 Personen, 24 Sessions, 18 Expositionen eingefügt, 2 unverändert), Post-Validierung ok, Health/Ready 200. Prod-DB danach: `de` 26 Sessions, 26 Personen (24 Lernende, 2 Muttersprachler:innen), 20 Expositionen; `en` 10, `es` 24, `fr` 21 unverändert.
- Zweite Lücke: Die deutschen Task-Kataloge lagen nur im Release, nicht im flachen Baum `data/config/research_player/`, den die App liest (Publish kopiert `config/` nicht, siehe Spec). `diff -rq` zeigte als einzigen Unterschied das neue Verzeichnis `german`; es wurde additiv kopiert (`cp -a`, Ziel existierte nicht), danach sind beide Bäume identisch. Web-Container neu gestartet.
- Gegenmaßnahmen: `build_prod_upload_package.py` bricht ab, wenn der DB-Payload eine gepackte Session nicht abdeckt (neuer Test); Runbook `research-prod-upload-and-publish.md` um „DB-Payload prüfen“ und „flachen Konfigurationsbaum abgleichen“ ergänzt.
- Release-Retention (Standardpolicy `keep_current_plus_1_previous_max_7_days`) hat beim Publish die alten Releases vom 2026-10-06 (Französisch, Spanisch) entfernt; die flachen Session-Bäume der anderen Korpora sind unverändert (`spanish` 24, `french` 31, `english` 10, `german` 26 Ordner). Rollback-Referenz: Release `…20261008T183938Z…b` bleibt erhalten, aktuell ist `…20261008T184439Z…c`.
- Verifikation Produktion: `/health`, `/ready`, `/de|en/research/german/design` 200; anonyme Aufrufe von Sprecherseite und Audio werden nach `/login` umgeleitet (302). Im Produktions-Container über die App-Loader geprüft: 26 deutsche Sessions, Kataloge 96/51 Items, jede Session Wortliste 96 und Text 51 Items, Interviews in 24 Sessions, Rollen DE-L-0017 `interviewer_1` 7 / `interviewer_2` 13 / `participant` 9, DE-L-0020 19 / 26 / 19, `L1`-Namen und Tooltips (`KAB` „Kabylisch“/„Kabyle“, `RCF` „Réunion-Kreolisch“/„Réunion Creole“, `NMG`, `DUA`), DE-L-0011 `l1_additional = RCF`; Seitenbuilder für Sprecher und Vergleich liefern 26 Sessions mit Namen statt Codes.
- Nicht möglich: Eine angemeldete Browsersitzung auf der Live-Seite (kein Zugangskonto für die Sitzung); Hover/Tap-Verhalten der Tooltips wurde lokal und im CI-Browser-Smoke geprüft, nicht live.

## Aufräumen und Preservation

- Überholtes Paket `promat_upload_german_20261008` aus `incoming/` entfernt (exakt benanntes Verzeichnis, nach Prüfung des `manifest.json`); die Pakete `…b` und `…c` hat der Publish selbst aus `incoming/` entfernt, `incoming/` ist leer. Lokal die Exporte `…20261008` und `…b` gelöscht; `…c` (das veröffentlichte Paket) bleibt als Nachweis.
- Backup auf das separate Laufwerk (`PROMAT_BACKUP_ROOT`): Baseline-Fixity ergänzt (additiv), `backup-copy` 98/98 Einheiten (26 deutsche Sessions plus Batch), `backup-supplemental` (Label `20261008-german`: Intake-Workbooks, Task-Kataloge inkl. `german`, Fixity), `backup-verify --unbuffered`: 98 Einheiten `BACKED_UP`, 13 915 Dateien, 0 Fehler.
- Preservation-Kopie (`PROMAT_PRESERVATION_ROOT`): nicht konfiguriert, kein Ziel verfügbar; alle Einheiten bleiben `PRESERVATION_PENDING`. Ein Backup macht nichts löschbar. Der Quell-Batch unter `import/` und das lokale Archiv bleiben unverändert erhalten.

## Offene Punkte

- Erledigt im Folgelauf: L1-Codes werden als Sprachnamen aufgelöst (siehe oben).
- Die öffentliche Design-Seite des Deutsch-Korpus ist weiter der Zustand „in Vorbereitung“; eine Beschreibung fehlt.
- DE-L-0017, Segment 28 („Ah, okay, alles klar. Dann war es das, glaube ich, auch. Das war meine eine Nachfrage …“) ist im Transkript `spk3` (Interviewer 2) zugeordnet, klingt aber nach der deutschen Interviewerin bzw. dem deutschen Interviewer (Interviewer 1); unverändert übernommen, bitte prüfen.
- Satz 6 der Satzliste lautet im Quelltext „Das Mädchen hat hat eine hübsche neue Tasche.“ (doppeltes „hat“); unverändert übernommen, bitte gegen die Vorlage prüfen.
- Bindestrich-Varianten in der Wortliste (`sagen -sägen`, `Weg - weg`) sind unverändert aus der Vorlage übernommen.
- Preservation-Kopie des neuen Batch-Archivs steht aus (`PROMAT_PRESERVATION_ROOT` nicht gesetzt); danach `archive_preservation.py copy`/`verify` und erst dann Quell-Batch aus `import/` entfernen. Backup ist erledigt.

## Nächste sinnvolle Schritte

- Produktion: erledigt, siehe Abschnitt „Produktion“.
- Quell-Batch erst nach verifizierter Preservation-Kopie aus `import/` entfernen.
