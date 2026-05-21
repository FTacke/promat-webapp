# Teaching Audio Feedback Feature

Datum: 2026-05-21

## Ziel

Gezielter Feature-Run für öffentliche Teaching-Themenseiten: zwei unterschiedliche Wiedergabe-Rückmeldungen auf bereits vorhandenen Audio-Oberflächen.

- kurze `audio_contrast`-Wortfolge-Pillen erhalten einen echten Progress-Fill von links nach rechts
- längere `audio_examples`-Transkriptkästen erhalten während der Wiedergabe einen subtilen Secondary-Accent-Glow und im Pause-Zustand eine statische aktive Hervorhebung

Nicht im Scope: Änderungen an Audioquellen, Textinhalten, allgemeinem Audio-Card-Layout, MFA-/Alignment-Logik oder Wort-/Tokenmarkierung in längeren Transkripten.

## Consulted Sources

- Root- und Scoped-Governance in `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`
- Repo-Anweisungen in `.github/instructions/repo.instructions.md` und `.github/copilot-instructions.md`
- aktive Spec in `docs/spec/platform-data-files.md`
- Teaching-Audio-Markup in `app/templates/partials/_teaching_blocks.html`
- Teaching-Audio-State-Logik in `app/static/js/modules/core/teaching-mini-player.js` und `app/static/js/modules/core/entry.js`
- Teaching-Audio-Tokens und Komponenten-CSS in `app/static/css/00_tokens.css` und `app/static/css/30_components.css`
- fokussierte Regressionen in `app/tests/test_research_sessions.py`

## Betroffene Komponenten

- `render_teaching_mini_player(...)`
- `render_audio_examples_item(...)`
- `render_audio_examples_block(...)`
- `render_audio_contrast_example(...)`
- `audio_examples`-Transkriptkästen (`pm-teaching-audio-example__transcript audio-quote`)
- `audio_contrast`-Wortfolge-Pillen (`pm-teaching-audio-contrast__transcript`)
- gemeinsames Mini-Player-Modul `initTeachingMiniPlayers()`

## Geänderte Dateien

- `app/templates/partials/_teaching_blocks.html`
- `app/static/js/modules/core/teaching-mini-player.js`
- `app/static/css/00_tokens.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`
- `docs/spec/platform-data-files.md`

## Diagnose

- Die Audio-Beispiele auf Themenseiten werden vollständig über `_teaching_blocks.html` gerendert.
- Der bestehende Public-Teaching-Player-Zustand wird zentral im Modul `app/static/js/modules/core/teaching-mini-player.js` gehalten; dort existierten bereits `loadedmetadata`, `durationchange`, `timeupdate`, `play`, `pause` und `ended`.
- Es gab bereits pro Audio einen echten `play`-/`pause`-/`ended`-State und echtes Fortschrittswissen via `currentTime` plus `duration`.
- Für `audio_contrast` existiert eine gemeinsame Wortfolge-Pille pro Vergleichsblock, aber zuvor keine visuelle Kopplung an die laufenden Beispiel-Audios.
- Für `audio_examples` existieren eigene Transkriptkästen pro Audio-Card, aber zuvor keine eigene aktive Wiedergabe-Rückmeldung jenseits des Players.
- `sample` spiegelt diese Audio-Oberflächen aktuell nicht und musste deshalb in diesem Run nicht angepasst werden.

## Umsetzung

### State-Weitergabe

- Es wurde keine parallele Audio-State-Erkennung eingeführt.
- Stattdessen verwendet der Run die vorhandene Mini-Player-State-Maschine weiter und ergänzt nur verlinkte Feedback-Ziele.
- Jeder Teaching-Mini-Player kann jetzt optional `data-audio-feedback-target="..."` tragen.
- Lange Transkriptkästen und Wortfolge-Pillen erhalten stabile Ziel-IDs plus `data-audio-state="idle"`.
- Das Mini-Player-Modul schreibt auf diese Ziele:
  - `data-audio-state="playing" | "paused" | "idle"`
  - `--pm-audio-linked-progress: <percent>%`
- Der Mini-Player selbst erhält ebenfalls `data-audio-state`, damit der sichtbare Play-Button konsistent zur neuen Feedback-Weitergabe bleibt.

### Wortfolge-Pille

- Die Wortfolge-Pille bleibt im Idle optisch wie bisher.
- Beim Abspielen eines Audios im eigenen Vergleichsblock setzt das Modul `--pm-audio-linked-progress` aus echtem `currentTime / duration`.
- Das Fill wird über ein Pseudo-Element innerhalb der bestehenden Pille gerendert; der eigentliche Text liegt in einem inneren `pm-teaching-audio-contrast__transcript-text` Layer darüber.
- Bei Pause bleibt der Fortschritt stehen.
- Beim Start eines anderen Audios im selben Vergleichsblock beginnt die Pille erneut mit dessen Fortschritt.
- Bei `ended` wird der Fortschritt auf `0` zurückgesetzt und der State auf `idle` gesetzt.

### Längere Transkriptkästen

- Die bestehenden `audio-quote`-Transkriptkästen verwenden jetzt `data-audio-state` als Zustandsanker.
- `paused`: statische leichte Tint-/Border-Hervorhebung
- `playing`: dieselbe Tint plus weicher, langsamer Secondary-Accent-Glow
- `idle`: kompletter Rückfall auf den Normalzustand
- Es wurde ausdrücklich keine Wort-/Tokenmarkierung eingeführt.

### Externe Pausen / Blockwechsel

- Das bestehende globale Mini-Player-Verhalten pausiert andere Teaching-Audios beim Start eines neuen Audios.
- Für diese externen Pausen wurde `pauseReason = superseded` eingeführt, damit verknüpfte Pille oder Transkript nicht fälschlich im `paused`-Highlight hängen bleiben, sondern sauber auf `idle` zurückfallen.
- Ein manueller Pause-Klick ohne Blockwechsel bleibt dagegen bewusst im `paused`-State.

## Tokens

Neu ergänzt in `app/static/css/00_tokens.css` für Light und Dark:

- `--pm-teaching-audio-linked-progress-bg`
- `--pm-teaching-audio-linked-progress-bg-strong`
- `--pm-teaching-audio-transcript-active-bg`
- `--pm-teaching-audio-transcript-active-border`
- `--pm-teaching-audio-transcript-active-glow`

Ableitung:

- alle neuen Audio-Feedback-Tokens leiten sich von der bestehenden Secondary-Familie (`promat-secondary`, `promat-secondary-container`, `promat-secondary-rgb`) ab
- keine lokal hardcodierten Akzentfarben in den Komponentenregeln

## Dark Mode

- Für Dark Mode wurden eigene Tokenwerte ergänzt statt Light-Mode-Werte einfach zu übernehmen.
- Der Progress-Fill bleibt sichtbar, aber deutlich gedämpft.
- Der Transcript-Glow nutzt im Dark Mode eine etwas stärkere, aber weiterhin weiche `rgba(var(--promat-secondary-rgb) / ...)`-Ableitung ohne Neonwirkung.
- Textkontrast bleibt über den bestehenden Foreground-Tokens stabil.

## Reduced Motion / Accessibility

- Unter `@media (prefers-reduced-motion: reduce)`:
  - keine Pulse-Animation für aktive Transkriptkästen
  - keine Progress-Transition auf dem Pill-Fill-Pseudo-Element
  - der aktive Zustand bleibt trotzdem über statische Tint-/Border-Hervorhebung erkennbar
- Es wurden keine Layoutgrößen geändert und keine zusätzlichen Progressbars außerhalb der bestehenden Oberflächen eingeführt.
- Fokus- und Player-Bedienung bleiben auf dem vorhandenen Mini-Player-System.

## Verifikation

### Fokussierte Tests

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation"` -> `2 passed, 197 deselected`

### Live-DOM / Browser

Reale Route: `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`

Geprüfte Fälle:

- Idle-Zustand der Wortfolge-Pille: `idle`, Progress `0.000%`
- Play im ersten Vergleichsblock: Pille `playing`, Progress > `0%`
- Pause im ersten Vergleichsblock: Pille `paused`, Progress bleibt stehen
- Wechsel auf das zweite Audio im selben Vergleichsblock: Pille bleibt `playing`, Progress springt auf den neuen Audiofortschritt zurück
- `ended`: Pille fällt auf `idle`, Progress zurück auf `0.000%`
- Langes Beispiel `Mexiko`: zugehöriger Transkriptkasten `playing`, `Chile` bleibt `idle`
- Wechsel auf `Chile`: `Mexiko` fällt auf `idle`, `Chile` wird `playing`
- Dark Mode explizit geprüft: aktive Transcript- und Pill-States bleiben sichtbar
- `prefers-reduced-motion: reduce` explizit geprüft: `animationName = none`, Pill-Transition `0s`

### Screenshots

- Integrierte Browser-Screenshots für Light- und Dark-Mode-Zustände geprüft
- Light-Mode-QA auf Wortfolge-/Vergleichsbereich
- Dark-Mode-QA auf langen Transkriptkästen

## Grenzen / bewusste Nicht-Umsetzung

- Keine MFA-/JSON-Zeitstempel-Logik
- Keine Wort-für-Wort- oder Token-Markierung in längeren Transkripten
- Kein Versuch, längere Transkripte präziser zu highlighten als auf Box-Ebene
- Keine Änderungen an Audioquellen oder Textinhalten
- Keine Änderung am allgemeinen Layout der Audio-Cards
