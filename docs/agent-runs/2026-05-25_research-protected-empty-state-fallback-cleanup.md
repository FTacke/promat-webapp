# Research Protected Empty-State Fallback Cleanup

Datum: 2026-05-25

## Ziel

Alte Dummy-/Planungs-Fallbacks auf den geschützten Research-Seiten `speakers`, `comparison` und `phenomena` entfernen und bei leerem `data/sessions` stattdessen die produktiven Flächen mit schlichten Empty States ausliefern.

## Consulted Sources

- `docs/spec/research-capabilities.md`
- `AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/AGENTS.md`
- `app/src/app/routes/public.py`
- `app/src/app/routes/public_content.py`
- `app/src/app/research_capabilities.py`
- `app/src/app/research_views.py`
- `app/src/app/research_phenomena_views.py`
- `app/src/app/i18n.py`

## Geänderte Bereiche

- Research-Capability-Routing für produktive versus Placeholder-Surfaces
- Builder für `speakers`, `comparison` und `phenomena`
- Jinja-Templates für `research_speakers` und `research_phenomena_overview`
- Client-JS für `research-comparison` und `research-phenomena-overview`
- i18n-Katalog für neue No-Data-Texte
- Fokus-Regressionen in `app/tests/`
- aktive Spec in `docs/spec/research-capabilities.md`

## Wichtige Entscheidungen

- `spanish/speakers` und `spanish/comparison` bleiben auch ohne Runtime-Daten auf der produktiven finalen Oberfläche statt auf generischen Placeholder-Seiten.
- No-Data-Zustände und Filter-Empty-Zustände werden getrennt behandelt, damit leere Runtime-Daten nicht als Such- oder Filterproblem erscheinen.
- `phenomena` zeigt ohne Runtime-Sessions keine kuratierten oder privaten Sets mehr an, auch wenn Set-Metadaten vorhanden wären.
- Alte Planungsphrasen wie `Geplante Übersicht`, `Geplante Filter`, `Struktureller Stand` und `Geplante Oberfläche` gehören nicht mehr zum aktiven Verhalten der geschützten Seiten.

## Abweichungen

- Keine Abweichung von der aktualisierten Spec.
- Ein breiterer `speakers`-Regressionlauf trifft weiterhin zwei bestehende Erwartungsfehler außerhalb des bearbeiteten Empty-State-Slices (`Aufenthalte` vs. `Sprachaufenthalte` in Alt-Assertions).

## Verifikation

- Fokussierte Pytest-Checks:
  - `python -m pytest app/tests/test_research_sessions.py -q -k "plain_empty_state_without_runtime_sessions or speakers_route_renders_plain_empty_state_without_runtime_sessions"`
  - `python -m pytest app/tests/test_research_comparison.py -q -k "final_empty_state_without_runtime_sessions or comparison_route_uses_final_empty_state_without_runtime_sessions"`
  - `python -m pytest app/tests/test_research_phenomena.py -q -k "plain_empty_state_without_runtime_sessions or phenomena_overview_route_renders_plain_empty_state_without_runtime_sessions"`
- Breitere Regression:
  - `python -m pytest app/tests/test_research_comparison.py -q` : grün
  - `python -m pytest app/tests/test_research_phenomena.py -q` : grün
  - `python -m pytest app/tests/test_research_sessions.py -q -k "speakers"` : zwei bestehende Alt-Assertions fehlgeschlagen, nicht durch diesen Slice verursacht
- Live-Browser-Abnahme auf:
  - `/de/research/spanish/speakers`
  - `/de/research/spanish/comparison`
  - `/de/research/spanish/phenomena`
  - `/en/research/spanish/speakers`
  - `/en/research/spanish/comparison`
  - `/en/research/spanish/phenomena`
- Sichtprüfung bestätigt auf allen sechs Routen die erwarteten Empty States ohne sichtbare Planungsphrasen.

## Offene Punkte

- Die zwei bestehenden `speakers`-Assertions im breiteren File-Lauf sollten separat gegen die aktuelle produktive Beschriftung bereinigt werden.
- Wenn weitere Korpora auf produktive Empty-State-Surfaces umgestellt werden, sollte dieselbe Capability-Regel explizit in der Spec ergänzt werden.

## Nächste sinnvolle Schritte

- Die verbleibenden alten `speakers`-Assertions auf aktuelle Label-Texte ausrichten.
- Bei der nächsten Research-UI-Bereinigung prüfen, ob weitere generische Fallback-Payloads in `public_content.py` noch Alt-Planungstexte enthalten.
