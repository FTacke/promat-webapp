# Wordlist Compare Repair and Consolidation

Datum: 2026-04-07

## Ziel

Den bestehenden produktiven `wordlist`-Compare-Player technisch konsolidieren: Freeze beim Moduswechsel beheben, Toolbar und Geschwindigkeitswahl auf eine ruhige Arbeitszeile bringen und die Player-Metakarten wirklich auf dieselbe Kartenfamilie wie die Speaker-Cards zurückführen.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/agent-runs/2026-04-06_research-player-wordlist-compare-layout-31.md`
- `docs/agent-runs/2026-04-07_research-player-wordlist-compare-default-32.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/templates/partials/_research_speaker_card.html`

## Geänderte Bereiche

- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`
- `docs/spec/research-player.md`

## Technische Ursache des Freeze

- Der sichtbare Hänger beim Umschalten zwischen `Einzeln`, `A/B manuell` und `A→B je Item` kam nicht von doppelten Event-Listenern oder Audio-Neuinstanziierung.
- Die eigentliche Ursache war, dass der Moduswechsel noch über normale `href`-Navigation lief und damit jedes Mal die komplette Player-Seite neu lud: Server-Render, DOM-Neuaufbau, neues Audio-Setup und erneute JS-Initialisierung.
- Für den Compare-Use-Case war diese Vollnavigation unnötig, weil die komplette Compare-Oberfläche samt Liste und Audioelementen bereits im DOM vorhanden war.

## Reparatur

- Der Moduswechsel wurde auf einen leichten clientseitigen State-Wechsel umgestellt.
- Die Mode-Buttons bleiben als echte Links im Markup erhalten, damit der Player ohne JS nicht bricht; mit JS werden Klicks jedoch abgefangen, `data-player-mode` wird lokal aktualisiert und die URL nur per `history.replaceState(...)` synchronisiert.
- Dabei wird keine neue Navigation ausgelöst und keine Compare-Liste neu aufgebaut.
- Laufende Sequenzen werden beim Moduswechsel sauber abgebrochen, Audios pausiert und bei `single` oder `sequence` wieder auf den Primärkontext zurückgeführt, damit keine kaputte Zwischenansicht entsteht.

## Toolbar-Konsolidierung

- Die obere Reihe bleibt bei Primärsession, Vergleichssession und Modusgruppe.
- Die untere Reihe wurde auf eine echte Arbeitszeile umgestellt: Play/Pause, Zeit, Seekbar, Lautstärke, Geschwindigkeit.
- Die Geschwindigkeitswahl ist keine große Dropdown-Fläche mehr, sondern eine direkte kompakte Segmentgruppe mit den festen Werten `0.5×`, `0.75×`, `1.0×`, `1.25×`, `1.5×`.
- Lautstärke bleibt Slider und sitzt jetzt ohne zusätzliche Hilfslogik auf derselben Kontrollachse.

## Kartenbasis

- Die Player-Metakarten hängen nicht mehr an `pm-profile-session`, sondern leiten sich jetzt technisch von der Speaker-Card-Familie ab: `pm-speaker-card` plus player-spezifische Meta-Variante.
- Übernommen wurden dieselbe Accent- oder Top-Border-Logik, dieselbe Chip-Sprache und dasselbe zweispaltige Faktenraster-Prinzip.
- Bewusst nicht übernommen wurde die starre Speaker-Card-Proportion; im Player dürfen die Karten die verfügbare Arbeitsbreite vollständig nutzen.
- Im Compare-Modus stehen zwei gleich breite Karten exakt über den beiden Wortlisten-Spalten; im Single-Modus nutzt die Primärkarte die ganze verfügbare Breite.
- Die Profil-Aktion ist jetzt eine klar sekundäre Inline-Aktion `Profil →` im Kartenkopf.

## Abweichungen

- Frühere Run-Logs beschrieben den Compare-Zustand nach den Layout-Runden zu optimistisch: Der produktive Moduswechsel war technisch noch immer ein Vollreload und damit noch keine saubere State-Lösung.
- Dieser Run behandelt deshalb echte Reparatur und Konsolidierung, nicht bloß Polishing.

## Verifikation

- `pytest app/tests/test_research_sessions.py`
- Problems-Check für die geänderten Template-, JS-, CSS- und Test-Dateien.
- Headless-Browser-Prüfung mit Selenium gegen den laufenden lokalen Flask-Server:
  - Initialzustand bei gültiger `compare_session`: `data-player-mode = sequence`, Compare-Liste sichtbar, `92` Compare-Zeilen.
  - Moduswechsel ohne neue Navigation: `performance.getEntriesByType('navigation').length` blieb vor und nach den Wechseln bei `1`.
  - Gemessene Wechselzeiten im Headless-Browser: `manual` ca. `53 ms`, `single` ca. `41 ms`, `sequence` ca. `49 ms`.
  - Kompakte Speed-Direktwahl geprüft: Aktivierung von `1.25×` setzte die aktive Rate-Markierung und beide Audioelemente auf `1.25`.
- Lokale Screenshots des reparierten Zustands:
  - `tmp/ui-qa/player-compare-pass7/desktop-repair.png`
  - `tmp/ui-qa/player-compare-pass7/mobile-repair.png`

## Was weiterhin nur Polishing ist

- Mikrotypografie, letzte Abstände der Toolbar und feinere visuelle Gewichtung einzelner Chips wären weiteres Polishing.
- Die funktionale Reparatur selbst ist abgeschlossen: kein Vollreload mehr beim Moduswechsel, direkte Speed-Wahl, Compare-Sichtbarkeit ab gültiger Vergleichssession und konsolidierte Kartenbasis.

## Nächste sinnvolle Schritte

- Falls der `text`-Compare später produktiv wird, dieselbe clientseitige Moduslogik nur dann übernehmen, wenn die Textoberfläche dieselbe vorgerenderte Compare-Struktur tatsächlich besitzt.