# Spanische Design-Seite: Titel und Zitiervorschlag

## Ziel

Den sichtbaren Seitentitel der spanischen Research-Design-Seite zweisprachig präzisieren und nach der Literatur einen Zitationskasten im bestehenden Teaching-Citation-Muster ergänzen, ohne Route, Slug oder Navigationslabel zu verändern.

## Konsultierte Grundlagen

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`
- bestehende Teaching-Citation-Partial, Research-Seitenvorlage und Runtime-Wiring

## Änderungen und Entscheidungen

- `SPANISH_DESIGN_PAGE_CONTENT` enthält die neuen deutschen und englischen Seitentitel.
- Das vorhandene Feld `nav_current_label` hält Breadcrumb und Navigation bei `Design`; Routing und Capability-Metadaten bleiben unverändert.
- Der lokalisierte Zitiervorschlag wird über die gemeinsame Admonition-Komponente samt bestehendem Copy-Button gerendert.
- Der Kasten steht nach allen Inhaltsabschnitten und damit nach dem Literaturverzeichnis.
- Keine aktive Spec musste geändert werden, da weder Routing, Access, Capability noch eine Architekturregel verändert wurden.

## Verifikation

- Fokussierte Route- und Rendering-Tests für beide UI-Sprachen.
- Bestehende Research- und Teaching-Regressionen für Navigation und Citation-Komponente.
- Browserprüfung der realen deutschen und englischen Route.

## Abweichungen und offene Punkte

Keine.
