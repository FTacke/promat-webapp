# Implementation Report: Phenomena Curated/Custom Set Actions

**Datum:** 2026-05-28  
**Branch:** main  
**Basis:** [Diagnosebericht](../agent-runs/phenomena-sets-architecture-diagnosis.md)

---

## Zusammenfassung

Dieser Report dokumentiert die Implementierung der bereinigten Phänomene-Set-Architektur auf Basis der Diagnose vom 2026-05-28.

---

## Was war der diagnostizierte Stand

- `common.status.archived` fehlte als i18n-Key in beiden Sprachen.
- Keine Rollenprüfungstests für Admin-only-Endpunkte.
- Kein Admin-Flow für neues kuratiertes Set aus der UI.
- Kein Endpunkt für Löschung kuratierter Sets (nur Archivieren als Soft-Delete).
- Kein Endpunkt zum Umwandeln eines Custom Sets in ein kuratiertes Set.
- `phenomena_presets.json` irrtümlich als Produktiv-Bedingung in Specs dokumentiert.
- Wording: „Kuratiertes Set archivieren" war sichtbare Aktion statt „Kuratiertes Set löschen".

---

## Was wurde geändert

### Backend (`app/src/app/research_sets.py`)

**Neue Service-Funktionen:**

- `delete_curated_set(*, admin_user_id, set_id)` – Löscht ein kuratiertes Set physisch aus der DB. Prüft, dass das Set tatsächlich `visibility='curated'` hat. Abhängige Tabellen (`research_set_items`, `research_set_workbench_state`, `research_set_workbench_sessions`) werden per CASCADE gelöscht.
- `create_curated_from_custom(*, admin_user_id, source_set_id, label, note)` – Erstellt ein neues kuratiertes Set als Kopie eines bestehenden Custom Sets. Das Quell-Custom-Set bleibt erhalten (Ansatz B: neue curated-Kopie statt Scope-Wechsel). Das neue Set hat `visibility='curated'`, `lifecycle='saved'`, `owner_user_id=NULL`, `published_at=now`.

**Warum Ansatz B (neue curated-Kopie) statt Ansatz A (Scope-Wechsel):**  
Ansatz B ist sicherer: Das Admin-eigene Custom Set bleibt erhalten, kein komplexer Constraint-Dance nötig, keine Gefahr von Datenverlust bei versehentlicher Umwandlung.

### API (`app/src/app/routes/research_api.py`)

**Neue Endpunkte:**

- `DELETE /api/research/admin/curated-sets/<set_id>` – Löscht ein kuratiertes Set. Admin-only (`_require_admin()`). Gibt `{"deleted": true, "set_id": ...}` zurück.
- `POST /api/research/admin/curated-sets/from-custom` – Erstellt ein kuratiertes Set aus einem Custom Set. Payload: `{"source_set_id": "...", "label": "...", "note": "..."}`. Admin-only.

**Bestehende Endpunkte** (archive, reactivate) bleiben als API erhalten für Migration/Kompatibilität, werden aber nicht mehr in der produktiven UI exponiert.

### i18n (`app/src/app/i18n.py`)

**Bug behoben:**
- `common.status.archived` ergänzt in `de` (`"archiviert"`) und `en` (`"archived"`).

**Neue Keys (de):**
- `research.phenomena.editor.delete_curated` → `"Kuratiertes Set löschen"`
- `research.phenomena.editor.delete_curated_title` → `"Kuratiertes Set wirklich löschen?"`
- `research.phenomena.editor.delete_curated_message` → `"Das kuratierte Set „{label}" wird dauerhaft gelöscht. Bestehende eigene Kopien bleiben erhalten."`
- `research.phenomena.editor.delete_curated_success` → `"Kuratiertes Set wurde gelöscht."`
- `research.phenomena.editor.save_as_curated` → `"Als kuratiertes Set speichern"`
- `research.phenomena.editor.save_as_curated_title` → `"Als kuratiertes Set speichern?"`
- `research.phenomena.editor.save_as_curated_message` → `"Das Set wird als neues kuratiertes Set für alle Nutzer:innen veröffentlicht."`
- `research.phenomena.editor.save_as_curated_success` → `"Als kuratiertes Set gespeichert."`
- `research.phenomena.editor.curated_admin_hint` → `"Als Admin bearbeiten oder löschen Sie dieses kuratierte Set direkt."` (Wording von „archivieren" zu „löschen" aktualisiert)

**Neue Keys (en):** analog mit englischen Labels.

### View (`app/src/app/research_phenomena_views.py`)

**Neue URL-Templates im Editor-State:**
- `adminDeleteCuratedSetUrlTemplate` → `DELETE /api/research/admin/curated-sets/__SET_ID__`
- `adminCreateCuratedFromCustomUrl` → `POST /api/research/admin/curated-sets/from-custom`
- `presetEditorHrefTemplate` → URL-Template für den Preset-Editor (für Navigation nach Save-as-Curated)

**Neue Labels im Editor-State:** alle neuen i18n-Keys als `labels.deleteCurated`, `labels.saveAsCurated` etc.

### Template (`app/templates/pages/research_phenomena_editor.html`)

**Geändert:**
- `[data-phenomena-curated-toggle-action]` (archive/reactivate) entfernt
- `[data-phenomena-delete-curated-action]` hinzugefügt – sichtbar nur für ADMINs auf kuratiertem Set
- `[data-phenomena-save-as-curated-action]` hinzugefügt – sichtbar nur für ADMINs auf Custom/Draft-Set

### JavaScript (`app/static/js/pages/research-phenomena-editor.js`)

**Geändert:**
- Referenzen auf `curatedToggleButton` / `curatedToggleLabel` entfernt
- Neue Buttons `deleteCuratedButton` und `saveAsCuratedButton` verdrahtet
- `syncStatus()` aktualisiert: Sichtbarkeit der neuen Buttons per `isCuratedAdminRecord()` und `state.isAdmin && !isCuratedRecord()`
- `toggleCuratedLifecycle()` ersetzt durch:
  - `performDeleteCurated()` – Confirm-Dialog (danger), dann DELETE-Request, dann navigateToOverview
  - `performSaveAsCurated()` – Confirm-Dialog, dann ggf. Items+Patch speichern, dann from-custom POST, dann navigate zu neuem kuratiertem Set im Preset-Editor

---

## Rollenmatrix (aktueller Stand nach Implementierung)

| Aktion | USER | ADMIN |
|---|---|---|
| Kuratiertes Set ansehen | ✓ | ✓ |
| Als eigenes Set bearbeiten | ✓ | ✓ |
| Kuratiertes Set global bearbeiten | ✗ (403) | ✓ |
| Kuratiertes Set löschen | ✗ (403) | ✓ |
| Custom Set anlegen | ✓ | ✓ |
| Custom Set bearbeiten/löschen | eigene Sets | eigene Sets |
| Custom Set als kuratiertes Set speichern | ✗ (403) | ✓ |
| Neues kuratiertes Set direkt anlegen | ✗ (403) | ✓ |

Alle Rollenprüfungen sind serverseitig in `_require_admin()` implementiert.

---

## UI-Flows USER

- Kuratiertes Set → **Ansehen** oder **Als eigenes Set bearbeiten**
- Custom Set → **Bearbeiten** / **Umbenennen** / **Löschen**
- Kein „Kuratiertes Set löschen", kein „Als kuratiertes Set speichern", kein „Kuratiertes Set archivieren"

## UI-Flows ADMIN

- Kuratiertes Set bearbeiten → Editor mit „Kuratiertes Set aktualisieren" (Speichern) + **„Kuratiertes Set löschen"**
- Custom Set bearbeiten → Editor mit normalem Speichern + **„Als kuratiertes Set speichern"**
- Neues Set → immer erst als Custom Set, dann optional „Als kuratiertes Set speichern" im Editor

---

## Was passiert mit privaten Kopien beim Löschen eines kuratierten Sets

- `source_curated_set_id` FK verwendet `ON DELETE SET NULL`
- Private Kopien bleiben vollständig erhalten und verlieren nur die Provenienz-Referenz (`source_curated_set_id = NULL`)
- Kein Datenverlust bei Nutzern

---

## Legacy-Rolle von `phenomena_presets.json`

- Die Dateien unter `data/config/research_player/{language}/phenomena_presets.json` sind Legacy-Artefakte
- Sie werden von keinem produktiven Applikationscode mehr geladen
- `load_phenomena_presets()` und `load_phenomena_preset_map()` in `research_presets.py` existieren noch, werden aber nur in Tests als Fixture genutzt
- Die Specs wurden entsprechend korrigiert

---

## API-Endpunkte nach Implementierung

| Methode | Route | Auth | Rolle |
|---|---|---|---|
| POST | `/api/research/sets` | JWT | user/admin |
| GET | `/api/research/sets` | JWT | user/admin |
| GET | `/api/research/sets/<set_id>` | JWT | user/admin |
| PATCH | `/api/research/sets/<set_id>` | JWT | user/admin |
| DELETE | `/api/research/sets/<set_id>` | JWT | user/admin (nur eigene) |
| PUT | `/api/research/sets/<set_id>/items` | JWT | user/admin |
| PUT | `/api/research/sets/<set_id>/sessions` | JWT | user/admin |
| POST | `/api/research/sets/<set_id>/save-as` | JWT | user/admin |
| POST | `/api/research/sets/<set_id>/private-copy` | JWT | user/admin |
| POST | `/api/research/admin/curated-sets` | JWT | **admin only** |
| PUT | `/api/research/admin/curated-sets/<set_id>` | JWT | **admin only** |
| DELETE | `/api/research/admin/curated-sets/<set_id>` | JWT | **admin only** (neu) |
| POST | `/api/research/admin/curated-sets/from-custom` | JWT | **admin only** (neu) |
| POST | `/api/research/admin/curated-sets/<set_id>/archive` | JWT | **admin only** (deprecated, nicht mehr in UI) |
| POST | `/api/research/admin/curated-sets/<set_id>/reactivate` | JWT | **admin only** (deprecated, nicht mehr in UI) |

---

## DB-/Server-Migration

**Keine DB-Migration nötig.** Das bestehende Schema (`research_sets`-Tabelle mit `visibility`, `lifecycle`, `owner_user_id` etc.) ist korrekt und vollständig. Die neuen Funktionen nutzen die bestehende Tabelle ohne Schemaänderungen.

**Datenmigration:** Falls die Inhalte aus `phenomena_presets.json` in Produktion verfügbar sein sollen, müssen diese einmalig per `POST /api/research/admin/curated-sets` manuell eingetragen werden. Es gibt kein automatisches Import-Skript.

---

## Tests (neu / angepasst)

Neue Tests in `app/tests/test_research_sets.py`:
- `test_user_cannot_create_curated_set` – 403
- `test_user_cannot_update_curated_set` – 403
- `test_user_cannot_delete_curated_set` – 403
- `test_user_cannot_archive_curated_set` – 403
- `test_user_cannot_reactivate_curated_set` – 403
- `test_user_cannot_create_curated_from_custom` – 403
- `test_unauthenticated_cannot_call_admin_endpoints` – 401/422 für alle Admin-Endpunkte
- `test_admin_can_delete_curated_set` – 200, set danach 404
- `test_delete_curated_set_leaves_private_copies_intact` – FK-SET-NULL verifiziert
- `test_delete_curated_set_rejects_private_set` – 400/404
- `test_service_delete_curated_set_removes_items_and_workbench` – CASCADE verifiziert
- `test_admin_can_create_curated_from_custom_set` – 201, curated visibility
- `test_admin_create_curated_from_custom_copies_items` – Items korrekt kopiert
- `test_admin_create_curated_from_custom_preserves_original` – Quell-Custom-Set bleibt erhalten

Angepasst in `app/tests/test_research_phenomena.py`:
- `test_public_preset_editor_route_exposes_admin_curated_actions_for_admins` – neue Button-Data-Attribute verifiziert

---

## Button-Diagnose: USER sieht „Kuratiertes Set archivieren"

Der Diagnose zufolge war der Button (`[data-phenomena-curated-toggle-action]`) korrekt nur für `state.isAdmin === true && record.visibility === 'curated'` sichtbar. Wenn ein Test-User-Account diesen Button sieht, ist die wahrscheinlichste Ursache:

1. **Der Test-User hat role=admin in der DB** – zu prüfen per direktem DB-Query.
2. **Veralteter Browser-Cache** – Hard-Refresh (Ctrl+Shift+R) sollte das klären.
3. Durch diese Implementierung ist der Button `[data-phenomena-curated-toggle-action]` vollständig entfernt; der neue `[data-phenomena-delete-curated-action]` greift dieselbe Bedingung (`isCuratedAdminRecord()`), sodass das Problem in jedem Fall bereinigt ist.
