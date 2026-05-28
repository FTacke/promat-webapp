# Phänomene ADMIN-Matrix + Overflow-Systematik

Datum: 2026-05-28

## Ziel

Phänomene-Set-Bereich systematisch bereinigen:
- ADMIN-Button-Matrix ökonomisch und logisch machen.
- Löschaktionen aus Hauptleiste in Overflow-Menüs verschieben.
- Overflow-Menü-Verhalten wiederverwendbar verbessern (außen klicken, Escape, nur ein Menü gleichzeitig).
- USER-Fix nicht regressieren.
- Admin-Bereich separat behandelt (dieses Mal im Scope).

## Consulted Sources

- `docs/agent-runs/2026-05-28_phenomena-user-button-matrix.md`
- `docs/agent-runs/2026-05-28_phenomena-user-button-matrix-hotfix.md`
- `docs/agent-runs/phenomena-sets-architecture-diagnosis.md`
- `docs/agent-runs/_template.md`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/static/js/pages/research-phenomena-overview.js`
- `app/templates/pages/research_phenomena_overview.html`
- `app/templates/pages/research_phenomena_editor.html`
- `app/src/app/research_phenomena_views.py`
- `app/src/app/i18n.py`
- `app/tests/test_research_phenomena.py`

## Geänderte Bereiche

### `app/static/js/modules/core/overflow-menu.js` (neu)
Wiederverwendbare Utility für `<details data-overflow-menu>` Overflow-Menüs:
- Klick außerhalb → alle offenen Menus schließen.
- Escape → schließt + Fokus zurück zu Summary.
- Toggle-Capture: öffnet eines → schließt alle anderen.
- Klick auf Aktion → schließt das Menü.
- `aria-expanded` über nativen `<details>/<summary>` Browser-Mechanismus.

### `app/templates/pages/research_phenomena_overview.html`
- Admin-Curated-Aktionen: von 3 Buttons (Ansehen + Kuratiertes Set bearbeiten + Als eigenes Set bearbeiten) auf 2 (Ansehen + Bearbeiten) reduziert.
- `{% if entry.show_edit_as_own %}` Block entfernt.
- Custom-Set-Overflow: `data-overflow-menu` Attribut ergänzt für Utility.

### `app/templates/pages/research_phenomena_editor.html`
- Admin-only: neuer Button `data-phenomena-save-as-custom-action` (versteckt, JS zeigt für admin+curated).
- Overflow `<details data-overflow-menu data-phenomena-editor-overflow hidden>` hinzugefügt.
- Darin: `data-phenomena-delete-curated-action` (admin only) + `data-phenomena-delete-action` (alle, hidden by default).
- Destroy-Buttons aus Hauptleiste entfernt.

### `app/src/app/research_phenomena_views.py`
- `show_edit_as_own` aus Overview-Card entfernt (Feld war redundant).
- `_editor_state()` Labels: `saveAsCustom`, `saveAsCustomTitle`, `saveAsCustomMessage`, `saveAsCustomSuccess` ergänzt.

### `app/static/js/pages/research-phenomena-overview.js`
- `initOverflowMenus` importiert und am Ende von `init()` aufgerufen.
- `closeDetailsMenus()` aktualisiert auf `data-overflow-menu`.

### `app/static/js/pages/research-phenomena-editor.js` (vollständig umgeschrieben)
- `initOverflowMenus` importiert.
- `buildItemsPayload()` extrahiert (DRY).
- `persistCurrentRecordAsCopy()` neu: erstellt private Kopie mit `source_curated_set_id`, wechselt `state.editorMode` auf "set".
- `persistCurrentRecord()` bereinigt: kein `editorMode === "preset"` Branch mehr; admin+curated → update in-place; custom → save in-place.
- `performSaveAsCopy()` / `performSaveAsCopySilent()`: wrappt `persistCurrentRecordAsCopy`.
- `syncStatus()` komplett überarbeitet:
  - `const dirty = isDirty()` als erste Zeile (Regression-Schutz).
  - `discardButton.hidden = !dirty` (beide Rollen).
  - `saveAsCustomButton.hidden = !(isAdmin && isCurated)`.
  - `saveAsCuratedButton.hidden = !(isAdmin && isCustom)`.
  - `deleteCuratedButton.hidden = !(isAdmin && isCurated)`.
  - `deleteCustomButton.hidden = !isSavedCustom`.
  - Overflow: `overflowMenu.hidden` = kein sichtbarer Overflow-Action.
- `syncSaveAction()` erweitert:
  - Admin+curated: `saveButton.hidden = !dirty`; Label = "Änderungen speichern".
  - Admin+custom/User: `saveButton.hidden = false`; bestehende disabled-Logik.
- `saveButton` click-Handler: User+curated+dirty → `performSaveAsCopy` (mit Confirm).
- `saveAsCustomButton` click-Handler: Admin+curated → `performSaveAsCopySilent` (mit Confirm).

### `app/src/app/i18n.py`
- `update_curated`: "Kuratiertes Set aktualisieren" → "Änderungen speichern" (DE) / "Save changes" (EN).
- `update_curated_title`: "Kuratiertes Set wirklich aktualisieren?" → "Änderungen am kuratierten Set speichern?" (DE) / "Save changes to curated set?" (EN).
- Neue Keys (DE + EN): `save_as_custom`, `save_as_custom_title`, `save_as_custom_message`, `save_as_custom_success`.

### `app/tests/test_research_phenomena.py`
- `show_edit_as_own` Assertions entfernt/ersetzt.
- Admin-Übersicht: `">Kuratiertes Set bearbeiten<" not in html`, `">Als eigenes Set bearbeiten<" not in html`.
- `update_curated_title` Assertions auf neue Texte oder `'"updateCuratedTitle"' in html` aktualisiert.
- 12 neue Tests ergänzt (ADMIN-Matrix, Overflow-Utility, Regression).

## Wichtige Entscheidungen

- **Keine serverseitige Exclusion für Admin-Buttons auf Admin-Seite**: Alle Admin-Buttons werden für Admin gerendert (mit `hidden`); JS steuert Sichtbarkeit kontextabhängig. Nur USER-Ausschluss erfolgt serverseitig.
- **`persistCurrentRecordAsCopy()` als eigenständige Funktion**: Sauberere Trennung als der alte `editorMode === "preset"` Branch in `persistCurrentRecord()`.
- **Overflow-Utility als dediziertes Modul**: `overflow-menu.js` kann von anderen Seiten importiert werden. Kein globales state-Sharing nötig.
- **`discardButton.hidden = !dirty` für beide Rollen**: Vereinfachung gegenüber `!isAdmin && !dirty`; Admin sieht Discard auch nur wenn dirty.
- **„Ansehen + Bearbeiten" in Admin-Übersicht**: Kein separater Scope-Einstieg nötig; Admin entscheidet im Editor, ob Änderungen in-place (kuratiert) oder als Kopie (custom) gespeichert werden.

## Abweichungen

- `discardButton.hidden = !dirty` gilt jetzt für ALLE Rollen, nicht nur USER. Das entspricht dem Zielbild: Discard ist nur sinnvoll wenn etwas zu verwerfen gibt.
- Overflow-Utility deckt **nur phenomena-Bereich** ab. Andere Seiten, die ähnliche Patterns haben, sind dokumentiert aber nicht in diesem Run angepasst.

## Verifikation

```
python -m pytest app/tests/test_research_phenomena.py -q  → 53 passed
python -m pytest app/tests/test_research_sets.py -q       → 39 passed
python -m ruff check .                                    → All checks passed!
python scripts/ci_governance_checks.py                    → All governance checks passed.
python -m compileall -q app/src app/tests                 → (kein Output = OK)
```

**Browser-QA** (lokal, USER + ADMIN):

| Rolle | Szenario | Hauptleiste | Overflow | Console | pass/fail |
|---|---|---|---|---|---|
| USER | Übersicht – kuratiertes Set | Ansehen | – | nein | pass |
| USER | Editor – kuratiertes Set clean | Speichern (disabled) | – | nein | pass |
| USER | Editor – kuratiertes Set dirty | Änderungen verwerfen, Speichern | – | nein | pass |
| USER | Speichern-Klick dirty | Confirm-Dialog | – | nein | pass |
| USER | Editor – neues Custom Set | Speichern | – | nein | pass |
| USER | Editor – gespeichertes Custom Set | Speichern (bei dirty) | Set löschen | nein | pass |
| USER | Overflow außen klicken | (schließt) | – | nein | pass |
| USER | Overflow Escape | (schließt) | – | nein | pass |
| ADMIN | Übersicht – kuratiertes Set | Ansehen, Bearbeiten | – | nein | pass |
| ADMIN | Editor – kuratiertes Set clean | Als Custom Set speichern | Kuratiertes Set löschen | nein | pass |
| ADMIN | Editor – kuratiertes Set dirty | Änderungen verwerfen, Als Custom Set speichern, Änderungen speichern | Kuratiertes Set löschen | nein | pass |
| ADMIN | Editor – Custom Set gespeichert | Speichern (dirty), Als kuratiertes Set speichern | Set löschen | nein | pass |
| ADMIN | Item-Auswahl | funktioniert | – | nein | pass |

## Offene Punkte

- Overflow-Utility deckt aktuell nur `phenomena`-Bereich ab. Andere Seiten mit `<details>` Overflow-Menüs (z.B. admin tables) wurden identifiziert aber nicht angepasst.
- `common.actions.modify` i18n-Key ist noch vorhanden, wird nirgends genutzt – kann später bereinigt werden.
- Admin-Curated-Archive/Reactivate-Flow ist separat implementiert, wurde in diesem Run nicht angepasst.

## Nächste sinnvolle Schritte

- Overflow-Utility auf weitere Seiten ausrollen, wenn ähnliche Menüs auftreten.
- `common.actions.modify` bereinigen.
- `phenomena_presets.json` Legacy-Code und Loader-Funktionen entfernen, wenn Migration entschieden.

## Server-/DB-Migration

Keine. Alle Änderungen sind UI/JS/Template/i18n.
