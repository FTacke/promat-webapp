# Comparison final präzisiert und Audio gehärtet

Datum: 2026-04-10

## Ziel

Die nach dem sprecherzentrierten Umbau noch offenen sichtbaren und funktionalen Restpunkte der `comparison`-Seite konsequent fertigschärfen: keine doppelten Stufentitel, fachlich korrekter Materialkontext, sauberere Sprecher:innen-Metadaten, klar gruppierte Filter, dichtere Matrixaktionen und real verifizierte Audiofunktion.

## Consulted Sources

- `docs/spec/research-access.md`
- `docs/agent-runs/2026-04-09_comparison-first-workflow-52.md`
- `docs/agent-runs/2026-04-10_comparison-speaker-centered-refinement-53.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`
- `app/tests/test_research_player_set_context.py`
- `app/src/app/routes/research_api.py`
- `app/src/app/routes/public.py`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`
- `app/tests/test_research_player_set_context.py`
- `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Alle drei Comparison-Stufen lesen nun sichtbar mit genau einer Hauptüberschrift: `1 Was vergleichen?`, `2 Sprecher:innen auswählen`, `3 Matrix`.
- Der Materialbereich trennt jetzt sauber zwischen aktueller Materialform (`Vollständige Liste` / `Vollständiger Text`), sekundärer Preset-Auswahl direkt in `comparison` und leisem Handoff `Phänomene konfigurieren`.
- Die sichtbare Public-CTA wurde reduziert: `Anmelden` erscheint nur noch als kleine Sekundäraktion neben dem ruhigen Hinweistext `Zum Vergleichen anmelden.`.
- Sprecher:innen-Zeilen bleiben speaker-first, aber Metadaten wurden semantisch nachgeschärft: Lernende mit `L1: DE`, Native mit eigenem Native-Badge und zusätzlicher Standardvarietät, ohne Vermischung mit Learner-Level-Badges.
- Die Filterzeile wurde räumlich in drei Zonen geschärft: Suche links, Niveau in der Mitte, `L1` plus `Weitere Filter` rechts.
- Matrix-Zellen und Stub-Spalte wurden verdichtet, Primäraktion Audio bleibt visuell zuerst, die Player-Handoff-Aktion ist klar sekundär.
- Der Audio-Fix wurde auf Server- und Client-Seite gehärtet: nicht mehr bloß `Datei > 0`, sondern strukturelle MP3-Prüfung über ID3-/Frame-Sync-Signaturen; zusätzlich prüft der Client `Content-Type`, `Content-Length`, Blob-Typ und MP3-Signatur vor der Wiedergabe.

## Technische Ursache und Fix des Audio-Problems

- Der vorherige Vergleichspfad behandelte Split-Audio als abspielbar, sobald eine Datei existierte und nicht leer war.
- Das war zu schwach: HTML-/Fehldateien oder sonstige ungeeignete Inhalte mit `.mp3`-Pfad konnten dadurch weiterhin als normal spielbar exponiert werden und im Browser zu `The media resource ... was not suitable` führen.
- Serverseitig nutzt `_is_playable_audio_artifact(...)` jetzt eine strukturelle MP3-Prüfung auf ID3-/MPEG-Frame-Signaturen statt nur `st_size > 0`.
- Clientseitig lehnt `fetchClipUrl(...)` jetzt Antworten ohne Audio-MIME, mit `Content-Length: 0`, mit nicht-audiofähigem Blob-Typ oder ohne MP3-Signatur ab und entfernt fehlerhafte Audio-URLs wieder aus dem Cache.
- Neue Regressionen decken jetzt sowohl 0-Byte-Dateien als auch nicht-audiofähige `.mp3`-Inhalte explizit ab.

## Abweichungen

- Keine Abweichung von Routefamilie, Set-Architektur, Sticky-Matrix-Grundlogik oder dem item-centered / speaker-first Access-Modell.
- Die echte Matrix mit ausgewählten Sprecher:innen konnte lokal nicht als vollautomatisierter Browser-Owner-Flow mit Login und Klickinteraktion verifiziert werden; die Matrix-Nachschärfung wurde deshalb über JS/CSS-Vertrag, Regressionen und die laufende Seite im Public-Startzustand abgesichert.

## Verifikation

- VS-Code-Fehlerprüfung für die geänderten Python-, JS-, CSS-, Template-, Test- und Spec-Dateien: ohne neue Fehler.
- Gezielter Research-Regressionslauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py tests/test_research_phenomena.py tests/test_research_sets.py tests/test_research_player_set_context.py`
  - Ergebnis: `45 passed`.
- Sichtbar verifizierte Comparison-Änderungen im Screenshot der laufenden App:
  - `c:/dev/promat/tmp/comparison-final-pass.png`
  - keine doppelten Überschriften mehr in Material- und Sprecher:innen-Stufe
  - Materialkontext mit `Vollständige Liste`, `Vordefiniertes Set`, leisem `Phänomene konfigurieren`-Handoff und kleiner `Anmelden`-Aktion
  - sauber gruppierte Filterzeile mit Suche links, Niveaus in der Mitte, `L1` und `Weitere Filter` rechts
  - dichtere Sprecher:innen-Zeilen mit gebundener `L1: DE`-Darstellung
- Live-Audio-Prüfung gegen die laufende App auf `http://127.0.0.1:8000`:
  - Route: `/de/research/spanish/player/ES-L-0003-2027-S02/wordlist/items/wl_001.mp3`
  - Ergebnis: `200`, `Content-Type: audio/mpeg`, `Content-Length: 27927`
  - gespeicherte Datei: `c:/dev/promat/tmp/comparison-audio-check.mp3`
  - führende Bytes: `49 44 33 ...` (`ID3`)
  - zusätzlicher echter Decode-Check via `pydub`: erfolgreich, `duration_ms=1392`, `channels=1`, `frame_rate=48000`

## Offene Punkte

- Für eine echte End-to-End-Bestätigung der finalen Matrix-Zellen mit aktiver Sprecher:innen-Auswahl fehlt weiterhin ein automatisierter Browser-Owner-Flow mit Login.
- Die Preset-Auswahl direkt in `comparison` deckt den geforderten ruhigen Materialkontext ab; eine vollständige Auswahl aller owner-eigenen gespeicherten Sets existiert in der aktuellen Architektur weiterhin nicht als Listen-API und wurde deshalb nicht neu erfunden.

## Nächste sinnvolle Schritte

- Einen browsergesteuerten Owner-E2E-Test ergänzen: Login, Preset wählen, Sprecher:in hinzufügen, Matrix-Playback, Save-as.
- `phenomena` auf denselben Materialkontext zuspitzen, damit der Wechsel zwischen `comparison` und `phenomena` nicht nur fachlich, sondern auch atmosphärisch noch konsistenter wird.