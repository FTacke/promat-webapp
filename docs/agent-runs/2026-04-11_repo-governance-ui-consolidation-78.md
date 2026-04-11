# Repo Governance UI Consolidation

Datum: 2026-04-11

## Ziel

Die wiederkehrenden Erkenntnisse aus den letzten UI-, Research- und Governance-Runs als dauerhafte Regeln an die richtigen Stellen im Repo konsolidieren, damit künftige Agent-Runs stärker auf Wiederverwendung, ruhige UI-Hierarchie, Browserprüfung und klare Doku-Rollen ausgerichtet werden.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `.github/pull_request_template.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/plans/phenomena_plan.md`
- `docs/runbooks/README.md`
- `docs/runbooks/_template.md`
- `docs/agent-runs/2026-04-02_sample-layout-sync-followup-21.md`
- `docs/agent-runs/2026-04-06_research-player-wordlist-compare-layout-31.md`
- `docs/agent-runs/2026-04-10_phenomena-live-repair-and-validation-76.md`
- `docs/agent-runs/2026-04-11_phenomena-ui-polish-77.md`
- `app/templates/pages/sample_page.html`

## Geänderte Bereiche

- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `.github/pull_request_template.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/runbooks/ui-change-workflow.md`
- `docs/plans/phenomena_plan.md`

## Wichtige Entscheidungen

- Operative Agent-Regeln bleiben kurz und handlungsnah in `.github` und `AGENTS.md`; die dauerhaften UI-Systemregeln werden in einer bestehenden Spec verankert statt in neue freie Design-Notizen ausgelagert.
- Die praktische UI-Prüfroutine bekommt genau einen wiederholbaren Prozess-Ort unter `docs/runbooks/`.
- Produktive Referenzseiten werden explizit benannt: `comparison` für Step- und Auswahlmuster, `player` für dichte Arbeitsflächen und Zustandslogik, `speakers`/`recordings`/Profil für Karten- und Zeilenfamilien.
- `docs/plans/phenomena_plan.md` bleibt als Planungshistorie erhalten, wird aber klar als nicht-normativ markiert.

## Abweichungen

- Keine Abweichung von der aktiven Spec-Struktur; der Run stärkt die bestehende Source-of-Truth-Trennung statt eine neue Doku-Schicht einzuführen.

## Verifikation

- bestehende Governance-, Spec-, Plan-, Runbook- und Run-Orte systematisch gegeneinander geprüft
- Änderungen bewusst nur in vorhandene Governance- und Spec-Strukturen plus ein einzelnes neues Runbook eingehängt
- inhaltliche Konsistenz zwischen `.github`, `AGENTS.md`, `docs/spec/` und `docs/runbooks/` manuell gegengeprüft

## Offene Punkte

- Es gibt weiterhin ältere agent-runs mit wertvollen Detailerkenntnissen; nicht jede historische Einzelbeobachtung wurde in diesem Run in dauerhafte Regeln überführt, sondern nur die wiederkehrenden Muster.
- Falls künftig weitere UI-Familien produktiv stabil werden, sollte der Referenzteil im neuen Runbook gezielt mitwachsen statt wieder in Run-Berichten zu zerfallen.

## Nächste sinnvolle Schritte

- Bei den nächsten visuellen Runs das neue `docs/runbooks/ui-change-workflow.md` aktiv gegen den tatsächlichen Arbeitsablauf testen und bei Bedarf nachschärfen.
- Falls sich die UI-Referenzmatrix weiter stabilisiert, die wichtigsten gemeinsamen Partial- oder CSS-Einstiegspunkte später noch expliziter im Runbook verlinken.