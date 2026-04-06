# Research Player Target Architecture 23

Datum: 2026-04-05

## Ziel

Die bisher nur vorbereitete Research-Player-Route fachlich und technisch als verbindliche modulare Zielarchitektur spezifizieren, ohne in diesem Run Produktcode zu implementieren.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `docs/model_mds/speech_text_sync.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- bestehende Player-Stub-Einbindung in `app/src/app/routes/public.py` und `app/src/app/research_views.py`

## Ist-Zustand

- Der Research-Player existiert aktuell nur als vorbereitete Detailroute unter `/research/{language}/player/{session_id}/{task}`.
- `speakers`, `recordings` und das Profil führen bereits auf diese Route, aber die Seite ist fachlich noch Stub.
- Die bestehende Spec kennt bereits die kanonischen Task-Keys und verbietet doppelte Player-Logik, beschreibt aber die Zielarchitektur noch nicht ausformuliert.
- `docs/model_mds/speech_text_sync.md` liefert ein belastbares technisches Referenzmuster für Audio-, Sync- und Highlighting-Modularität, ist in PROMAT aber bisher nicht normative Spezifikation.

## Geänderte Bereiche

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/agent-runs/2026-04-05_research-player-target-architecture-23.md`

## Nachgezogene Präzisierungen

- Die Preset-Regel wurde verschärft: Im Preset-Kontext muss der Player manuelle Item-Erweiterungen erlauben; diese wirken nur im aktiven Zustand und niemals zurück in die Preset-Dateien.
- Die sichtbare Benennung des technischen Tasks `text` wurde als corpus-spezifische Konfiguration geschärft; sichtbare Labels wie `Satzliste` ändern keinen Task-Key.
- Der JSON-Vertrag wurde von einer zu groben Gleichförmigkeit auf gemeinsame Hüllstruktur plus task-spezifische Container und timingtragende Einheiten umgestellt.
- Für `wordlist` wurde explizit festgehalten, dass keine redundanten Token-Dubletten mit identischen Zeit- und Textwerten verlangt werden.
- Für `text` wurde die optionale Token-Referenz `wordlist_item_ref` als eindeutige Verknüpfung zum kanonischen Wortlisten-`item_id` festgelegt.
- Die interne Player-Normalisierung unterschiedlich feiner Eingangsdaten in eine gemeinsame Render-/Sync-Struktur wurde als Architekturregel ergänzt.

## Wichtige Entscheidungen

- Der Research-Player wird als eine einzige modulare Player-Basis spezifiziert.
- Vergleich bleibt eine Desktop-Erweiterung derselben Basis und wird nicht als eigener Player konzipiert.
- Phenomena-Presets werden als separate Konfigurationsschicht modelliert und nicht in Audio- oder Alignment-Daten eingebettet.
- `text` bleibt der technische Task-Key; Satzlisten- oder Textdarstellung wird als Render-Konfiguration definiert.

## Abweichungen

- Keine Abweichung von der Docs-Governance.
- Die neuen Soll-Regeln liegen ausschließlich in `docs/spec/`; ADR und Run-Log dokumentieren nur Entscheidung und Umsetzungspfad.

## Verifikation

- Pflichtquellen und Runtime-Wiring gelesen.
- Vorhandene Player-, Comparison- und Phenomena-Bezüge im Repo per Suche geprüft.
- Bestehende Spec-Aussagen auf Widersprüche zur neuen Player-Zielarchitektur geprüft und gezielt vereinheitlicht.
- Präzisierungen in `research-player.md`, `research-access.md` und `platform-data-files.md` auf Benennungs-, Routing- und Datenvertragskonsistenz gegengeprüft.

## Offene Punkte

- Die Spezifikation legt die Zielarchitektur fest, aber noch keine konkrete Frontend-Dateistruktur oder API-Schnittstellen im Anwendungscode.
- Die Produktionspipeline für `alignment/{task}.json`, `derived/{task}.mp3` und Split-MP3s ist weiter zu konkretisieren, sobald der zugehörige Code-Run beginnt.
- Die genaue minimale Token-Feldmenge für einzelne Korpora bleibt bewusst offen, solange sie den gemeinsamen Timing- und Referenzvertrag nicht verletzt.

## Nächste sinnvolle Schritte

1. Die neue Spec im nächsten Architektur-Run gegen die reale Flask- und Template-Struktur abgleichen und offene Benennungsdetails im Code festziehen.
2. Den kanonischen Page-Entry für den echten Player an Stelle des Stubs vorbereiten, ohne bereits task-spezifische UI-Komplexität zu bauen.
3. Die gemeinsame Basisarchitektur für Player-State, Audio-Steuerung, Datenladen, Sync und Highlighting implementieren.
4. Den Wortlistenmodus auf dieser Basis mit stabiler Nummerierung, direktem Item-Playback und Split-MP3-Download-Zielvertrag umsetzen.
5. Den technischen Task `text` auf derselben Basis mit konfigurierbarer Standarddarstellung für Satzliste oder Fließtext umsetzen.
6. Den gemeinsamen Task-Switch innerhalb derselben Player-Basis für alle session-verfügbaren Tasks herstellen.
7. Die corpus-spezifische Player-Konfiguration unter `data/config/research_player/{language}/` und die Phenomena-Preset-Verträge implementieren.
8. Die Desktop-Vergleichsansicht für `wordlist` und `text` als begrenzte Erweiterung derselben Player-Basis ergänzen.
9. Die interviewangemessene Darstellung als eigener Renderer innerhalb derselben Basis nachziehen.
10. Die Produktionsskripte und Datenpipelines für Alignment-JSON, Voll-MP3 und Split-MP3-Downloads an den normativen Vertrag anbinden.