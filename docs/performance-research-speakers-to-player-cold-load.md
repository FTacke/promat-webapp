# Performance-Diagnostik Speakers -> Player Cold Load

## Scope

- Zielpfad: Klick von `/en/research/spanish/speakers` auf eine Player-Route vom Typ `.../player/<session>/wordlist?source=speakers`
- Fokus: erster HTML-Response, serverseitige Renderkosten, DB-Anteil, Template-Anteil, Browser-Asset-Anteil, Link-/Prefetch-Verhalten
- Messungen lokal gegen `http://127.0.0.1:8000` mit authentifiziertem Research-Zugang

## Befund vor dem Fix

### Navigation und Browser

- Speakers nutzt normale Anchor-Navigation; es gibt dort kein Turbo-/PJAX-/JS-Routing für Player-Links.
- Der Klick lädt keine Audio-Ressourcen vorab; auf dem Player bleiben die Audio-Requests vor Interaktion bei `0`.
- Auf dem gemessenen Klickpfad lädt der Browser nach dem Seitenwechsel weiterhin die volle App-Shell-Basis mit `30` Stylesheets plus `1` Request auf `research-player.js`.

### Direkt gemessene Browserzeiten

Auf einem bereits laufenden Dev-Server ohne zusätzlichen Warm-up:

| Fall | DCL | Network idle | `responseStart` |
| --- | ---: | ---: | ---: |
| erster Speakers -> Player-Klick | `734 ms` | `1234 ms` | `603 ms` |
| zweiter Klick auf dieselbe Route | `297 ms` | `828 ms` | `185 ms` |
| neuer Browserkontext mit `no-cache` Headern | `360 ms` | `922 ms` | `199 ms` |

Der große Sprung zwischen erstem und zweitem Klick lag damit nicht primär an Browser-HTTP-Cache für CSS/JS, sondern am serverseitigen ersten Player-Build.

### Opt-in Server-Profiling auf der Player-Route

Für diese Diagnose wurde ein opt-in Profiling für die Player-HTML-Route ergänzt. Es misst:

- Access-Gate-Zeit
- `build_player_page(...)`
- Template-Renderzeit
- DB-Query-Zahl und DB-Gesamtdauer
- Runtime-Teilschritte `set_context`, `task_bundle`, `ready_sessions`, `player_items`

Erster echter Player-Request nach Python-Reload:

| Teil | Dauer |
| --- | ---: |
| Access | `0.068 ms` |
| Build | `6319.608 ms` |
| Render | `39.716 ms` |
| Gesamt-Route | `6359.544 ms` |
| DB gesamt | `107.044 ms` über `8` Queries |
| Runtime `task_bundle` | `449.382 ms` |
| Runtime `ready_sessions` | `5340.655 ms` |
| Runtime `player_items` | `10.677 ms` |

Zweiter Request auf dieselbe Route im selben Prozess:

| Teil | Dauer |
| --- | ---: |
| Build | `47.491 ms` |
| Render | `2.519 ms` |
| Gesamt-Route | `50.133 ms` |
| DB gesamt | `5.996 ms` über weiter `8` Queries |
| Runtime `ready_sessions` | `0.004 ms` |

## Schlussfolgerungen

- Der dominante Kaltstartblock war `load_task_ready_sessions(...)`, nicht Template-Rendering und nicht die DB.
- Die DB zeigt auf diesem Pfad kein N+1-Muster: die Query-Zahl bleibt stabil bei `8`, und der DB-Anteil bleibt selbst im Kaltfall klar unter dem Dateisystem-/Runtime-Anteil.
- Template-Rendern ist mit grob `28-40 ms` kein Hauptproblem.
- Browserseitig bleibt die volle Shell-CSS-Kette relevant, aber der Haupthebel für den kalten Speakers -> Player-Klick lag serverseitig im erstmaligen Ready-Session-Scan.

## Umgesetzte Fixes

### 1. Ready-Session-Resolution pro Sprache/Task cachen

`app/src/app/research_player_runtime.py`

- `load_task_ready_sessions(language_slug, task_key)` nutzt jetzt einen Prozess-Cache.
- Das entspricht dem bestehenden Cache-Modell für Session- und Katalogdaten und verhindert wiederholte Vollscans pro Player-Request.

### 2. Speakers-seitiges Prewarm vor dem eigentlichen Klick

`app/src/app/routes/public.py`

- Die Player-Route akzeptiert jetzt einen internen Header `X-Promat-Player-Prewarm: 1`.
- Der Prewarm-Pfad läuft durch Access-Gate und `build_player_page(...)`, rendert aber kein HTML und antwortet mit `204`.

`app/static/js/pages/research-speakers.js`

- Speakers startet dieses Prewarm gezielt bei `pointerenter`, `focusin` und `touchstart` auf Player-Links aus der Speakers-Ansicht.
- Die Navigation selbst bleibt ein normaler Anchor-Klick.

`app/templates/pages/research_speakers.html`

- lädt das kleine Speakers-Prewarm-Modul nur auf dieser Seite.

## Ergebnis nach dem Fix

Gemessener Hover-Prewarm auf dem Speakers-Link:

| Teil | Dauer |
| --- | ---: |
| Prewarm-Gesamt | `260.834 ms` |
| Prewarm-Build | `260.729 ms` |
| Prewarm-DB | `19.118 ms` über `8` Queries |
| Prewarm `ready_sessions` | `188.700 ms` |

Direkter nachfolgender echter Klick auf denselben Link:

| Teil | Dauer |
| --- | ---: |
| Server Build | `63.273 ms` |
| Server Render | `28.477 ms` |
| Server Gesamt | `91.873 ms` |
| DB gesamt | `8.029 ms` über `8` Queries |
| Runtime `ready_sessions` | `0.003 ms` |
| Browser `responseStart` | `86.5 ms` |
| Browser DCL | `203 ms` |
| Browser network idle | `719 ms` |

Zusätzlich gemessen auf dem echten Klick nach Prewarm:

- `1` Request auf `research-player.js`
- `30` Stylesheet-Requests für die volle Shell-Basis
- `0` Audio-Requests vor Interaktion

## Bewertung

- Der Kernengpass des kalten Speakers -> Player-Klicks war serverseitig und hing am erstmaligen Ready-Session-Scan.
- Der neue Cache beseitigt die Wiederholungskosten innerhalb desselben Prozesses.
- Das Speakers-seitige Prewarm verschiebt den einmaligen Kaltpfad in einen kurzen Vorab-Request bei Hover/Fokus/Touch und macht den eigentlichen Klick deutlich schneller, ohne Routing oder sichtbare UI zu verändern.
- Übrig bleibt vor allem die breite Shell-Basis des Vollseiten-Reloads. Das ist ein separater, globalerer Optimierungshebel.

## Validierung

- Live-Playwright-Messung gegen `http://127.0.0.1:8000`
- Profiling-Header auf der Player-Route (`X-Promat-Player-Profile`, `Server-Timing`)
- `pytest tests/test_research_sessions.py -q -k player_prewarm_request_warms_route_without_rendering_body`
- `pytest tests/test_research_player_set_context.py -q`