---
name: Architecture Change
about: Schlage eine strukturelle oder governance-relevante Änderung vor
title: "architecture: "
labels: [architecture]
assignees: []
---

## Ziel

Welche strukturelle Änderung wird vorgeschlagen?

## Motivation

Welches Problem oder welche Drift soll verhindert werden?

## Betroffene Spec-Dateien

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- weitere betroffene Governance- oder Runtime-Dateien

## Auswirkungen

- Architektur
- Dev/Prod-Parität
- Routing, Datenpfade oder öffentliche/geschützte Trennung
- Person-/Session-Modell, Research-Zugangslogik oder Native-Speaker-Sonderfall

## No-Go-Check

- Führt der Vorschlag alte Slugs, alte Pfade oder neue Schattenstruktur ein?
- Bricht der Vorschlag das kanonische ID-Modell `person_id = {CORPUS_CODE}-{SPEAKER_MARKER}-{NNNN}` / `session_id = {person_id}-{YYYY}-S{NN}`?

## Offene Fragen

- Was muss vor einer Umsetzung noch geklärt werden?