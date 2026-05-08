# recordings-doc-agent-context-cleanup

Datum: 2026-05-08

## Ziel

Repo-weite Bereinigung aktiver Dokumentations-, Planungs- und Agent-Kontextquellen, damit die entfernte Research-Seite `recordings` nicht später durch alte Architekturtexte, Runbooks, Pläne oder testspezifische Normalfallannahmen wieder eingeführt wird.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/research-player.md`
- root `AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`

## Geänderte Bereiche

- `docs/runbooks/ui-change-workflow.md`
- `docs/decisions/2026-04-02_person-based-research-access-01.md`
- `docs/decisions/2026-04-05_unified-modular-research-player-02.md`
- `docs/plans/architecture_plan.md`
- `docs/plans/project_pages/project_pages_content_german_english.md`
- `docs/agent-runs/2026-05-08_speakers-table-view-phase1.md`
- `docs/agent-runs/2026-05-08_recordings-page-removal-phase2.md` blieb als aktueller historischer Phase-2-Log erhalten
- `app/tests/test_research_sessions.py`
- `app/tests/test_research_player_set_context.py`
- `app/tests/js/research_ui_state_helpers.test.mjs`

## Wichtige Entscheidungen

- Aktive oder agentisch relevante Texte wurden auf den heutigen Sollstand umgestellt; ältere ADRs, Pläne und Run-Logs durften bleiben, mussten aber klar historisch oder superseded markiert werden, statt weiter wie aktuelle Zielarchitektur zu klingen.
- In Tests bleibt `source=recordings` nur noch als gezielter Legacy-Kompatibilitätsfall bestehen; normale Player- und URL-State-Regressionspfade verwenden jetzt `speakers` als aktiven Einstieg.
- Datenbezogene Vorkommen von `Aufnahmen`/`Recordings` wie Korpusstatus, Labeltexte oder Referenzaufnahmen wurden bewusst nicht entfernt, weil sie keine eigenständige Research-Seite beschreiben.

## Abweichungen

- Keine Abweichung von der aktiven Spezifikation.
- Historische, datierte Run-Logs aus April 2026 wurden nicht repo-weit umgeschrieben; sie bleiben als nicht-normative Historie erhalten.

## Verifikation

- Repo-weite Suchläufe nach `recordings`, `Aufnahmen`, `Recordings`, `recording page`, `recordings page`, `recordings workbench` in `docs/**`, `.github/**`, `**/AGENTS.md`, `**/README*.md` und `app/tests/**`
- Zusätzliche Abschluss-Suchen nach `recordings` in Kombination mit `page`, `workbench`, `route`, `navigation`, `capability`, `order`, `public`, `protected`
- `pytest app/tests/test_research_sessions.py -q` -> `180 passed`
- `pytest app/tests/test_research_player_set_context.py -q` -> `28 passed`
- `node --test app/tests/js/research_ui_state_helpers.test.mjs` -> `5 passed`

## Offene Punkte

- Historische Run-Logs vor dem 2026-05-08-Cleanup enthalten weiterhin damalige `recordings`-Architekturstände. Sie sind über Datum/Titel als Historie erkennbar, aber nicht einzeln mit zusätzlichen Statushinweisen versehen.
- Die aktive Spec dokumentiert weiterhin legitime Daten- und UI-Begriffe wie `recordings label`, `Recordings` als Tabellenkopf oder `reference recordings`; diese Treffer sind fachlich korrekt und kein Hinweis auf eine eigene Seite.

## Nächste sinnvolle Schritte

- Bei späteren Player- oder Navigation-Änderungen gezielt darauf achten, dass neue Tests wieder `speakers` als aktiven sessionnahen Einstieg verwenden.
- Falls ältere Historien-Dokumente künftig öfter von Agents zitiert werden, einen schlanken Sammelhinweis in `docs/agent-runs/README.md` ergänzen, dass `recordings` als aktive Research-Seite seit 2026-05-08 entfernt ist.