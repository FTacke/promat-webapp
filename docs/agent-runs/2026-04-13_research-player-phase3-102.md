# Research Player Phase 3

Datum: 2026-04-13

## Ziel

Phase 3 aus dem Architekturplan umsetzen: den Unified Research Player intern modularisieren, ohne den kanonischen Player-Route-Vertrag, die Capability-Quelle oder produktives Verhalten zu ändern.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/research-player.md`
- `docs/spec/intake-workbook.md`
- `docs/plans/architecture_plan.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- `app/src/app/research_player_runtime.py`
- `app/src/app/research_views.py`
- `app/tests/test_research_player_set_context.py`
- `docs/spec/research-player.md`
- `docs/plans/architecture_plan.md`

## Wichtige Entscheidungen

- Die interne Player-Runtime wurde in ein eigenes Modul gezogen, das Source-Resolution, Set-Context-Resolution, Media-Resolution, Item-Normalisierung und bounded Compare-State bündelt.
- `build_player_page(...)` bleibt die öffentliche Assembly-Stelle, bezieht ihren produktiven Player-State aber jetzt aus der dedizierten Runtime-Schicht statt aus verteilten Helfern im View-Modul.
- Bestehende öffentliche Resolver wie `resolve_player_audio_artifact(...)` und `resolve_player_item_download(...)` bleiben stabil und delegieren intern an die Runtime-Schicht.
- Die View-Schicht bleibt bewusst für Navigation, Summary-Cards, Control-Bars und Template-Payload zuständig; sie wird nicht zur zweiten Capability- oder Source-Truth zurückgebaut.

## Abweichungen

- Keine Abweichung von aktiver Spezifikation, Dev/Prod-Parität oder dem kanonischen Player-Route-Vertrag.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_player_set_context.py app/tests/test_research_sessions.py -q`
- Zusätzliche Runtime-Regressionen direkt gegen `resolve_player_runtime_state(...)` für set-gebundenes `text` und ungültige Compare-Requests.
- Live-QA auf `http://127.0.0.1:8000` mit laufendem `./scripts/dev-start.ps1`:
  - unauthenticated player route redirects to `/login?next=...`
  - authenticated `wordlist` player returns `200`
  - authenticated `text` player returns `200`
  - authenticated set-context player route returns `200` and keeps the selected set excerpt visible
  - authenticated compare-context player route returns `200`
  - authenticated secondary-corpus route `/en/research/english/comparison` returns `200`

## Offene Punkte

- Die View-Komposition liegt weiterhin in `app/src/app/research_views.py`; ein späterer Folgeschritt kann bei Bedarf die rein präsentationsbezogenen Player-Bausteine weiter bündeln, ohne die Runtime-Schicht erneut zu vermischen.

## Nächste sinnvolle Schritte

- Bei einer nächsten Player-Phase die verbleibenden reinen View-Kompositionshelfer gezielt strukturieren, falls weitere produktive Player-Modi dazukommen.
- Falls künftig ein produktiver Interview-Renderer entsteht, ihn bewusst als segmentorientierte Runtime aufbauen statt in die item-basierte productive path hineinzuziehen.