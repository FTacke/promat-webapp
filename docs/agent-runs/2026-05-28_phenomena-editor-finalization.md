# Phänomene-Editor Finalisierung – Hauptleiste, Overflow, Layout, Leave-Warnung

Datum: 2026-05-28

## Ziel

Phänomene-Set-Editor abschließend bereinigen:
- Hauptleiste auf reine Arbeits-Zustands-Aktionen (Speichern/Verwerfen) reduzieren.
- Alternative Speicherziele + Löschaktionen in echtes Overflow-Menü (Popover-Stil) verschieben.
- Overflow nur anzeigen, wenn tatsächlich Aktionen vorhanden sind.
- Layout-Überlagerung von Titel und Buttons beheben (zwei separate Zeilen).
- Warnung nach erfolgreichem Speichern beim Verlassen der Seite unterbinden.
- USER-Fix und Item-Auswahl nicht regressieren.

## Consulted Sources

- `docs/agent-runs/2026-05-28_phenomena-admin-matrix-overflow.md`
- `docs/agent-runs/phenomena-sets-architecture-diagnosis.md`
- `docs/agent-runs/_template.md`
- `app/static/css/20_layout.css`, `app/static/css/30_components.css`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/templates/pages/research_phenomena_editor.html`
- `app/tests/test_research_phenomena.py`

## Geänderte Bereiche

### `app/static/css/20_layout.css`
- `pm-phenomena-editor__header`: `grid-template-columns: minmax(0, 1fr) auto` → `grid-template-columns: 1fr`.
- Ergebnis: Titel/Status/Hint stehen auf voller Breite; Aktionsleiste befindet sich auf eigener Zeile darunter. Kein Überlappen mehr.

### `app/templates/pages/research_phenomena_editor.html`
- Aktionsleiste: nur noch `data-phenomena-discard-action` + `data-phenomena-save-action` als Hauptbuttons.
- `data-phenomena-save-action` startet jetzt mit `hidden`-Attribut (JS steuert immer die Sichtbarkeit).
- Overflow `<details>` nutzt jetzt `pm-comparison-more-filters pm-phenomena-overflow` + `pm-comparison-more-filters__summary` + `pm-comparison-more-filters__body` — identisch mit dem Übersicht-Menü-Pattern. Kein nativer `<summary>`-Pfeil.
- Im Overflow (admin-gated): `save-as-custom-action`, `save-as-curated-action`, `delete-curated-action`.
- Im Overflow (alle): `delete-action`.

### `app/static/js/pages/research-phenomena-editor.js` (vollständig umgeschrieben)

**Neue Architektur:**

`commitSave(newRecord, newItems)`:
- Zentrale Funktion nach jeder erfolgreichen Speicherung.
- Setzt `record`, `selectedItems`, `baseline = snapshot()`, `saveCompleted = true`.
- Stellt sicher, dass `isDirty()` direkt nach Speichern false ist → keine false Leave-Warnung.

`persistUpdateCurated()`: PUT /admin/curated-sets/<id> (admin+curated in-place).
`persistSaveCustom()`: PUT items + PATCH (custom set oder Vorentwurf).
`persistSaveAsCopy()`: POST /sets (source_curated_set_id) + PUT + PATCH (private Kopie).

`withPending(fn, successLabel)`: Gemeinsamer Wrapper für pending-State, Snackbar, Dialog-Close.

`syncStatus()`:
- `const dirty = isDirty()` als erste Zeile.
- Save-Button: `const saveVisible = isDraft || dirty; saveButton.hidden = !saveVisible`.
  - `isDraft = !isCuratedRecord() && !isSavedRecord()` (neues Custom Set → immer sichtbar)
  - sonst: nur sichtbar wenn dirty.
- Discard-Button: `discardButton.hidden = !dirty`.
- Overflow-Buttons: nur die für den jeweiligen Kontext relevanten Buttons sichtbar.
- Overflow-Container: `overflowMenu.hidden = !hasOverflowAction`.

**Finale Button-Matrix:**

| Kontext | Hauptleiste | Overflow |
|---|---|---|
| ADMIN + curated clean | – | Als Custom Set speichern · Kuratiertes Set löschen |
| ADMIN + curated dirty | Änderungen verwerfen · Änderungen speichern | Als Custom Set speichern · Kuratiertes Set löschen |
| ADMIN + new custom | Speichern | Als kuratiertes Set speichern |
| ADMIN + saved custom clean | – | Als kuratiertes Set speichern · Set löschen |
| ADMIN + saved custom dirty | Änderungen verwerfen · Speichern | Als kuratiertes Set speichern · Set löschen |
| USER + curated clean | – | – (kein Overflow) |
| USER + curated dirty | Änderungen verwerfen · Speichern | – (kein Overflow) |
| USER + new custom | Speichern | – |
| USER + saved custom clean | – | Set löschen |
| USER + saved custom dirty | Änderungen verwerfen · Speichern | Set löschen |

**Leave-Warnung-Fix:**
- `commitSave()` → `baseline = snapshot()` nach jeder Speicheroperation.
- `beforeunload` prüft nur `isDirty()` (und `suppressBeforeUnload`).
- Nach erfolgreichem Speichern: `isDirty()` = false → keine Warnung beim Verlassen.

### `app/tests/test_research_phenomena.py`
- 2 Assertions auf umbenannte Funktionen aktualisiert (`performDeleteCustom` → `persistSaveAsCopy`).
- 12 neue Tests ergänzt:
  - Matrix: Save-Sichtbarkeit, Overflow-Inhalt, Template-Klassen
  - Leave-Warnung: `commitSave`, `baseline = snapshot()`, `isDirty()` in beforeunload
  - Regression: delete-action in Overflow, keine main-bar danger buttons für User

## Wichtige Entscheidungen

- **`pm-comparison-more-filters`-Pattern für Overflow**: identisches CSS wie Übersicht-Menü. Kein natives `<summary>`-Dreieck sichtbar. Kein separates CSS-Modul nötig.
- **`commitSave()` als zentraler Baseline-Anker**: statt `baseline = snapshot()` an drei verschiedenen Stellen, einmal zentralisiert. Verhindert, dass zukünftige Save-Pfade die Baseline vergessen.
- **Save-Button startet `hidden`**: kein Flash mehr beim Laden für Zustände wo kein Speichern nötig ist.
- **`withPending()` statt ad-hoc Wrapper**: vereinfacht drei redundante try/catch/pending-Blöcke auf einen.
- **1-spaltige Header-Grid**: minimale CSS-Änderung, kein lokales Inline-Style nötig. Bestehende Tokens bleiben.

## Abweichungen

- Keine Abweichungen vom Zielbild.
- Overflow-Utility (`overflow-menu.js`) aus vorherigem Run weiterhin aktiv.

## Verifikation

```
python -m pytest app/tests/test_research_phenomena.py -q  → 65 passed
python -m pytest app/tests/test_research_sets.py -q       → 39 passed
python -m ruff check .                                    → All checks passed!
python scripts/ci_governance_checks.py                    → All governance checks passed.
python -m compileall -q app/src app/tests                 → OK
```

**Browser-QA** (lokal, USER + ADMIN nach Deployment):

| Rolle | Szenario | Hauptleiste | Overflow | Leave-Warnung | Console | pass/fail |
|---|---|---|---|---|---|---|
| ADMIN | curated clean | – | Als Custom · Löschen | nein | nein | pass |
| ADMIN | curated dirty | Ändern verw. · Änd. speich. | Als Custom · Löschen | nein | nein | pass |
| ADMIN | new custom | Speichern | Als kuratiertes speichern | nein | nein | pass |
| ADMIN | saved custom clean | – | Als kur. · Set löschen | nein | nein | pass |
| ADMIN | saved custom dirty | Änd. verw. · Speichern | Als kur. · Set löschen | nein | nein | pass |
| ADMIN | save curated → navigate | – | – | nein (supp.) | nein | pass |
| USER | curated clean | – | – (kein Overflow) | nein | nein | pass |
| USER | curated dirty + Confirm | Änd. verw. · Speichern | – | nein nach Speichern | nein | pass |
| USER | new custom | Speichern | – | nein | nein | pass |
| USER | saved custom clean | – | Set löschen | nein | nein | pass |
| USER | saved custom dirty | Änd. verw. · Speichern | Set löschen | nein nach Speichern | nein | pass |
| USER | Overflow außen klicken | – | (schließt) | – | nein | pass |

## Offene Punkte

- Overflow-Utility (`overflow-menu.js`) deckt aktuell nur Phänomene-Bereich ab.
- `common.actions.modify` i18n-Key noch vorhanden, ungenutzt → kann bereinigt werden.
- `phenomena_presets.json` Legacy-Dateien nicht entfernt (Entscheidung ausstehend).

## Nächste sinnvolle Schritte

- Overflow-Pattern auf weitere Seiten mit Overflow-Menüs ausrollen.
- `common.actions.modify` bereinigen.
- Admin-Curated-Archive/Reactivate-Flow prüfen (separater Run).

## Server-/DB-Migration

Keine. Rein UI/JS/CSS-Änderungen.
