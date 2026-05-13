# 2026-05-12 Teaching Datawrapper Theme Sync

## Scope

Kurzer Follow-up-Fix fuer Datawrapper-Embeds auf Teaching-Topic-Seiten, nachdem der vorherige Neutralitaets-Fix den Mischfall `SiteTheme=light` bei gleichzeitig dunkler Systempraeferenz unleserlich machte.

## Problem

- Der Host wurde korrekt im Light-Mode gerendert.
- Datawrapper orientierte sich im iframe weiter an `prefers-color-scheme: dark`.
- Dadurch entstand im Mischfall `App light + System dark` weisser Karten-Text auf hellem Hintergrund.

## Changes

- updated `app/static/css/30_components.css`
  - Datawrapper-iframe `color-scheme` jetzt an das effektive PROMAT-Theme gekoppelt
  - `light` fuer `data-theme="light"` sowie `auto` mit `data-system-dark="false"`
  - `dark` fuer `data-theme="dark"` sowie `auto` mit `data-system-dark="true"`
- updated `docs/spec/platform-data-files.md`
  - clarified that PROMAT must not force a fixed light-only Datawrapper appearance
  - allowed syncing the iframe `color-scheme` to the effective site theme so both explicit light and dark selections stay legible

## Verification

- browser validation on `/de/teaching/spanish/which-pronunciation`
- verified cases:
  - OS dark + site light -> fixed, iframe `color-scheme` resolves to `light`
  - OS dark + site dark -> still correct, iframe `color-scheme` resolves to `dark`
  - OS light + site light -> still correct, iframe `color-scheme` resolves to `light`
- screenshots saved under `tmp/ui-qa/2026-05-12-datawrapper-theme-sync/`