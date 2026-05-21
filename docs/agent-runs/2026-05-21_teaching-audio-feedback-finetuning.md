# Teaching Audio Feedback Finetuning

Datum: 2026-05-21

## Ziel

Sehr gezielter Finetuning-Run auf der bestehenden Teaching-Audio-Feedback-Implementierung.

- Wortfolge-Pille sichtbar flüssiger machen
- Wortfolge-Pille leicht voreilend wirken lassen, ohne echte Audio- oder MFA-Logik zu fälschen
- längere Transkriptkästen deutlicher, aber weiter ruhig pulsieren lassen
- Audio-Feedback-Farblogik vollständig von `--promat-wordmark-accent` ableiten statt von der Secondary-Familie

Nicht im Scope: Audioquellen, Textinhalte, Layout der Audio-Cards, Player-Bedienlogik, Daueranzeige, Wort-/Token-Sync oder andere Topic-Page-Stile.

## Consulted Sources

- Root- und Scoped-Governance in `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`
- aktive Spec in `docs/spec/platform-data-files.md`
- bestehende Feature-Doku in `docs/agent-runs/2026-05-21_teaching-audio-feedback-feature.md`
- Audio-State-Logik in `app/static/js/modules/core/teaching-mini-player.js`
- Audio-Tokens in `app/static/css/00_tokens.css`
- Audio-Komponentenregeln in `app/static/css/30_components.css`
- fokussierte Teaching-Regressionen in `app/tests/test_research_sessions.py`

## Diagnose

- Die sichtbare Pille wirkte weiterhin leicht ruckelig, weil die verknüpfte Progress-Anzeige faktisch nur über `timeupdate` nachgeführt wurde.
- Die aktive Farbwirkung war noch auf der Secondary-Familie aufgebaut und damit im Ergebnis zu blau.
- Der Glow der längeren Transkriptkästen war funktional vorhanden, aber in Light und Dark noch zu zurückhaltend.
- Die bestehende Mini-Player-State-Maschine war weiterhin der richtige Ownership-Punkt; es war kein zweites Audio-State-System nötig.

## Umsetzung

### JS

- `app/static/js/modules/core/teaching-mini-player.js` behält den vorhandenen Mini-Player als einzige Playback-State-Quelle.
- Für die verknüpfte Feedback-Anzeige wurde ein eigener `requestAnimationFrame`-Loop ergänzt, der nur während aktiver Wiedergabe läuft und bei `pause` oder `ended` sauber stoppt.
- Die eigentliche Player-Bedienung, Daueranzeige und Range-Sync bleiben weiter auf dem bestehenden Event-Modell.
- Für die visuelle Rückmeldung der Wortfolge-Pille wird jetzt ein kleiner Voreil-Faktor von `1.08` auf die reine Progress-Darstellung angewendet; die reale Audio-Zeit selbst bleibt unverändert.
- Unter `prefers-reduced-motion: reduce` startet der RAF-Loop bewusst nicht; dort bleibt die Aktualisierung beim bestehenden eventbasierten Verhalten.

### Tokens

- Die Audio-Feedback-Tokens in `app/static/css/00_tokens.css` wurden vollständig auf `--promat-wordmark-accent` beziehungsweise `--promat-wordmark-accent-rgb` umgestellt.
- Das betrifft:
  - `--pm-teaching-audio-linked-progress-bg`
  - `--pm-teaching-audio-linked-progress-bg-strong`
  - `--pm-teaching-audio-transcript-active-bg`
  - `--pm-teaching-audio-transcript-active-border`
  - `--pm-teaching-audio-transcript-active-glow`
- Für Dark Mode wurden die Mischungen separat nachgezogen, damit die Wirkung dort sichtbar bleibt, ohne neonhaft zu werden.

### CSS

- Die Wortfolge-Pille erhielt eine kürzere Fill-Transition (`80ms`) passend zum RAF-basierten Nachführen.
- Der aktive Pille-Zustand bekam eine etwas stärkere Border-Wirkung.
- Der statische Pause-Zustand der langen Transkriptkästen bekam eine klarere Border- und Glow-Absetzung.
- Der Playing-Pulse der langen Transkriptkästen wurde von `2.8s` auf `2.1s` verdichtet und in den Keyframes sichtbar verstärkt.
- Der aktive Play-Button-Hintergrund folgt jetzt ebenfalls dem Wordmark-Akzent statt der Secondary-Container-Farbe.

## Verifikation

### Fokussierte Tests

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation"` -> `2 passed, 197 deselected`

### Live-DOM / Browser

Reale Route: `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`

Geprüfte Fälle:

- Light Mode, Wortfolge-Pille: Fortschritt lief über mehrere aufeinanderfolgende Animation-Frames weiter (`0.000%`, `21.085%`, `21.673%`, `21.751%`, `22.782%`) statt nur in groben Event-Sprüngen.
- Light Mode, Wortfolge-Pille: Transition-Dauer des Fill-Pseudo-Elements `0.08s, 0.14s`.
- Light Mode, Wortfolge-Pille: `play`, `pause`, `resume` und Reset auf `idle` mit `0.000%` geprüft.
- Wechsel zwischen zwei Audios im selben Vergleichskasten: Pille bleibt im aktiven Blockzustand und springt auf den neuen Audiofortschritt um.
- Lange Transkriptkästen: `play`, `pause`, `resume`, `ended` geprüft; Zustände wechselten `playing -> paused -> playing -> idle` wie erwartet.
- Kein Layout-Shift: Bounding-Box-X-Werte für Wortfolge-Pille und langen Transkriptkasten blieben vor/nach Wiedergabe identisch.
- Reduced Motion: Pill-Transition `0s`, Transcript-Animation `none`.
- Dark Mode: aktive Transcript-Styles und Contrast-Zustände auf realer Route geprüft; sichtbare Audio-Feedback-Tokens bleiben auf dem Wordmark-Akzent.
- Token-Check Light/Dark: `--pm-teaching-audio-linked-progress-bg-strong`, `--pm-teaching-audio-transcript-active-border` und `--pm-teaching-audio-transcript-active-glow` lösen live auf Mischungen mit `#a15a95` bzw. `rgb(161 90 149 / ...)` auf.

### Screenshots

- Browser-Screenshots der realen Route in Light und Dark aufgenommen.
- Die Screenshots wurden für Layoutstabilität und Akzentfarbe verwendet; die aktiven Zustände selbst wurden zusätzlich über DOM- und Computed-Style-Werte abgesichert.

## Ergebnis

- Keine blauen Audio-Feedback-Akzente mehr im neuen Effektpfad.
- Die Wortfolge-Pille wirkt flüssiger und subjektiv etwas schneller, ohne die eigentliche Audio-Zeit oder Bedienlogik zu verändern.
- Die langen Transkriptkästen sind im Playing-Zustand klarer lesbar hervorgehoben, bleiben im Gesamtbild aber ruhig genug für die bestehende Teaching-Oberfläche.
- Die bestehende Audio-Feature-Architektur blieb lokal und unverändert: ein State-Owner, keine Layoutänderung, keine MFA-Illusion.