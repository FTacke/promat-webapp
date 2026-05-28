# Phenomena Curated Set Architecture Diagnosis

**Datum:** 2026-05-28  
**Status:** Diagnose – ursprünglicher Stand; aktualisiert 2026-05-28 (USER-Aktionsmatrix implementiert)

---

## 1. Kurzfazit

Die Phänomene-Sets-Architektur ist insgesamt funktional und gut strukturiert. Die Migration von dateibasierten Presets nach PostgreSQL-backed Sets ist vollständig durchgeführt. Die DB-Schicht mit `research_sets`, `research_set_items`, `research_set_workbench_state` und `research_set_workbench_sessions` ist korrekt modelliert, mit robusten Check-Constraints.

Zentrale gefundene Schwachstellen:

1. **Fehlender i18n-Key**: `common.status.archived` existiert nicht in `i18n.py` (weder `de` noch `en`). Der Code referenziert ihn, der Fallback zeigt den Raw-Key `archived`.
2. **Keine Rollenprüfungstests für Admin-Endpunkte**: Es gibt keine Tests, die sicherstellen, dass ein normaler USER die Admin-Endpunkte (`POST /api/research/admin/curated-sets`, `PUT /api/research/admin/curated-sets/<id>`, `POST /api/research/admin/curated-sets/<id>/archive`, `/reactivate`) mit HTTP 403 abgelehnt wird. Die serverseitige Prüfung existiert (`_require_admin()`), ist aber ungetestet.
3. **Kein Scope-Wechsel private→global**: Es gibt keinen API-Endpunkt und keinen UI-Flow, der einem ADMIN erlaubt, ein bestehendes privates Set in ein kuratiertes Set umzuwandeln. Das Anlegen kuratierter Sets ist nur über `POST /api/research/admin/curated-sets` möglich – nicht über den UI-Flow „Neues Set".
4. **`phenomena_presets.json` ist produktiv toter Code**: Die Dateien in `data/config/research_player/{language}/phenomena_presets.json` werden vom Laufzeitsystem nicht mehr geladen. `load_phenomena_presets()` und `load_phenomena_preset_map()` sind nur noch in Tests und intern in `research_presets.py` referenziert.
5. **UI-Button-Logik für „Kuratiertes Set archivieren"**: Der Button erscheint im Editor nur, wenn `state.isAdmin && record.visibility === "curated"` gilt. Das ist korrekt serverseitig. Es gibt keinen bekannten Fall, dass der Button für normale USER erscheint – aber die Diagnose unter D ist unten genau erklärt.

---

## 2. Aktueller Architekturstand

### Schichten

```
config-Dateien (nur Lesen):
  data/config/research_player/{language}/task_catalogs/{task}.json  → Itemkatalog (aktiv)
  data/config/research_player/{language}/phenomena_presets.json     → LEGACY, nicht produktiv

PostgreSQL (read + write):
  research_sets                   → Haupt-Set-Tabelle (private + curated)
  research_set_items              → Item-Referenzen mit sort_order
  research_set_workbench_state    → Workbench-Zustand pro Set
  research_set_workbench_sessions → Session-Verknüpfungen pro Set

Backend (app/src/app/):
  research_sets.py                → Service-Layer (alle CRUD-Operationen)
  research_phenomena_views.py     → View-Model-Builder (overview + editor)
  routes/research_api.py          → JSON-API Blueprint
  research_presets.py             → Nur noch Katalog-Loader + Legacy-Preset-Loader
  research_capabilities.py        → Capability-Matrix, phenomena_productive-Erkennung

Frontend:
  templates/pages/research_phenomena_overview.html
  templates/pages/research_phenomena_editor.html
  static/js/pages/research-phenomena-overview.js
  static/js/pages/research-phenomena-editor.js
```

### Migrations-Chain

```
0003_create_research_sets.sql          → Initiale private-only Tabellen (state-Spalte, owner NOT NULL)
0004_extend_research_sets_for_phenomena_editor.sql → note-Spalte hinzugefügt
0005_split_research_set_workbench_state.sql → Workbench-State ausgelagert
0006_unify_research_sets_for_curated_db_model.sql → visibility + lifecycle + curated-Constraints
```

---

## 3. Aktuelle Datenquellen

### PostgreSQL-Tabellen (produktiv)

- `research_sets` – alle Sets (private und curated), einzige produktive Quelle
- `research_set_items` – Item-Referenzen (task + item_id + sort_order)
- `research_set_workbench_state` – preferred_task, comparison_view_task
- `research_set_workbench_sessions` – Session-Verknüpfungen

### JSON/Config-Dateien

- `data/config/research_player/{language}/task_catalogs/{task}.json` – **aktiv, Pflicht** für phenomena productive-Erkennung und Item-Validierung
- `data/config/research_player/{language}/phenomena_presets.json` – **LEGACY, nicht mehr produktiv geladen**. Die Funktionen `load_phenomena_presets()` und `load_phenomena_preset_map()` in `research_presets.py` existieren noch, werden aber von keinem produktiven Code importiert oder aufgerufen. Nur in Tests als Fixture-Hilfsmittel und intern in `research_presets.py` selbst referenziert.
- `data/config/research_player/{language}/player_config.json` – aktiv für Player-Konfiguration

### Seed-Logik

- `ensure_curated_test_set()` in `research_sets.py` wird von `app/scripts/create_initial_admin.py` mit dem Flag `--ensure-curated-test-set` aufgerufen. Das erstellt ein fixes DB-curated Set mit `set_id = RESEARCH_CURATED_TEST_SET_ID = "00000000-0000-0000-0000-000000000601"` für Entwicklungszwecke.
- Die produktiven kuratierten Sets (z.B. "Vokalsequenzen und Akzent") müssen manuell per `POST /api/research/admin/curated-sets` (oder direkt per DB) angelegt werden. Es gibt kein automatisches Seeding aus den `phenomena_presets.json`-Dateien in die DB.

---

## 4. PostgreSQL-Modell und relevante Spalten

### Tabelle `research_sets`

| Spalte | Typ | Bedeutung |
|---|---|---|
| `set_id` | TEXT PK | UUID des Sets |
| `owner_user_id` | TEXT FK→users NULL | NULL für curated, gesetzt für private |
| `corpus_language` | TEXT NOT NULL | z.B. `spanish`, `french` |
| `label` | TEXT NULL | Bezeichnung (NULL nur bei draft) |
| `note` | TEXT NULL | Freitextnotiz |
| `visibility` | TEXT NOT NULL | `private` oder `curated` |
| `lifecycle` | TEXT NOT NULL | `draft`/`saved` (private) oder `saved`/`archived` (curated) |
| `source_curated_set_id` | TEXT FK→research_sets NULL | Herkunft bei Kopie |
| `created_by_user_id` | TEXT FK→users NULL | Ersteller-Audit |
| `updated_by_user_id` | TEXT FK→users NULL | Letzter Änderer |
| `version` | INTEGER NOT NULL | Incrementell für curated |
| `created_at`/`updated_at` | TIMESTAMPTZ | Standard-Zeitstempel |
| `published_at` | TIMESTAMPTZ NULL | Zeitpunkt der Veröffentlichung (curated) |
| `archived_at` | TIMESTAMPTZ NULL | Archivierungszeitpunkt |
| `last_accessed_at` | TIMESTAMPTZ NOT NULL | Letzter Zugriff (private) |
| `expires_at` | TIMESTAMPTZ NULL | Ablaufzeit (nur private drafts) |

### Check-Constraints

```sql
ck_research_sets_visibility:         visibility IN ('private', 'curated')
ck_research_sets_lifecycle:          lifecycle IN ('draft', 'saved', 'archived')
ck_research_sets_saved_label:        lifecycle = 'draft' OR (label IS NOT NULL AND trimmed > 0)
ck_research_sets_visibility_lifecycle:
  (visibility = 'private' AND lifecycle IN ('draft', 'saved'))
  OR (visibility = 'curated' AND lifecycle IN ('saved', 'archived'))
ck_research_sets_owner_scope:
  (visibility = 'private' AND owner_user_id IS NOT NULL)
  OR (visibility = 'curated' AND owner_user_id IS NULL)
ck_research_sets_curated_expiry:     visibility = 'private' OR expires_at IS NULL
ck_research_sets_version:            version >= 1
```

**Wichtig**: DB-Constraint `ck_research_sets_visibility_lifecycle` verhindert, dass ein `private` Set `lifecycle = archived` erhält. Ebenso verhindert `ck_research_sets_owner_scope`, dass `visibility = curated` mit `owner_user_id IS NOT NULL` kombiniert wird. Ein direkter Scope-Wechsel private→curated ist durch Constraint **unmöglich**, sofern der Besitzer noch gesetzt ist.

### Tabelle `research_set_items`

- PK: `(set_id, task, item_id)` – verhindert doppelte Items
- `sort_order >= 1` (Check-Constraint)
- CASCADE DELETE bei `set_id`

### Tabelle `research_set_workbench_state`

- PK: `set_id` (1:1 zu research_sets)
- `preferred_task` NULL oder `wordlist`/`text`
- `comparison_view_task` DEFAULT `all`
- CASCADE DELETE

### Tabelle `research_set_workbench_sessions`

- PK: `(set_id, session_id)` – verhindert doppelte Sessions
- CASCADE DELETE

### FK-Verhalten bei Löschung

- Benutzer gelöscht → `owner_user_id SET CASCADE DELETE` bei `research_sets` (Besitzer-Sets werden gelöscht)
- `created_by_user_id`, `updated_by_user_id` → `ON DELETE SET NULL` (Audit bleibt erhalten)
- `source_curated_set_id` → `ON DELETE SET NULL` (Referenz-Provenienz wird auf NULL gesetzt, privates Set bleibt erhalten)

---

## 5. Aktuelle API-Flows

### Endpunkte (Blueprint `research_api`, Prefix `/api/research`)

| Methode | Route | Auth | Rolle | Funktion |
|---|---|---|---|---|
| POST | `/sets` | JWT | user/admin | Neues privates Draft-Set anlegen |
| GET | `/sets` | JWT | user/admin | Sichtbare Sets auflisten (curated + eigene private) |
| GET | `/sets/<set_id>` | JWT | user/admin | Ein Set laden (curated oder eigenes) |
| PATCH | `/sets/<set_id>` | JWT | user/admin | Metadaten/Workbench-State eines eigenen Sets ändern |
| DELETE | `/sets/<set_id>` | JWT | user/admin | Eigenes Set löschen (nur private) |
| PUT | `/sets/<set_id>/items` | JWT | user/admin | Items eines eigenen Sets ersetzen |
| PUT | `/sets/<set_id>/sessions` | JWT | user/admin | Sessions eines eigenen Sets ersetzen |
| POST | `/sets/<set_id>/save-as` | JWT | user/admin | Draft als neues gespeichertes Set kopieren |
| POST | `/sets/<set_id>/private-copy` | JWT | user/admin | Private Kopie eines (curated) Sets erstellen |
| POST | `/admin/curated-sets` | JWT | **admin only** | Neues kuratiertes Set anlegen |
| PUT | `/admin/curated-sets/<set_id>` | JWT | **admin only** | Kuratiertes Set aktualisieren (in-place) |
| POST | `/admin/curated-sets/<set_id>/archive` | JWT | **admin only** | Kuratiertes Set archivieren |
| POST | `/admin/curated-sets/<set_id>/reactivate` | JWT | **admin only** | Archiviertes kuratiertes Set reaktivieren |

### Auth-Prüfung

- Alle Endpunkte: `@jwt_required()` + `get_jwt_identity()`
- Admin-Endpunkte: `_require_admin()` prüft `g.role == Role.ADMIN` serverseitig; wirft `PermissionError` → 403

### Scope-Logik bei `create_set` (POST /sets)

`create_draft_set()` hardcodiert `visibility="private"`. Der Client kann keine `visibility` übergeben. Es gibt keinen Scope-Parameter in der API.

### Sichtbarkeit im GET /sets

- Curated sets (lifecycle=saved oder archived wenn include_archived_curated=True) sind für alle sichtbar
- `include_archived_curated=true` erfordert Admin-Rolle (serverseitige Prüfung)

---

## 6. Aktuelle UI-Flows

### Übersichtsseite (phenomena overview)

**Kuratierte Einträge zeigen:**
1. „Ansehen" (Navigation Pill) – für alle
2. „Kuratiertes Set bearbeiten" (Action Button) – nur wenn `entry.edit_curated_href` gesetzt → nur für Admins
3. „Als eigenes Set bearbeiten" (Action Button) – wenn eigene Kopie existiert: öffnet die Kopie; sonst: erstellt via `/api/research/sets/<set_id>/private-copy`

**Private Einträge zeigen:**
1. „Bearbeiten" (Navigation Pill)
2. Overflow-Menü mit „Umbenennen" und „Löschen"

**Neues Set anlegen:**
- Button „Neues Set" → POST `/api/research/sets` mit `corpus_language` → erstellt immer ein privates Draft

### Editor-Seite (phenomena editor)

Der Editor unterscheidet zwei Modi:
- `editorMode = "preset"` – curated Set geöffnet (über preset-Editor-Route)
- `editorMode = "set"` – privates Set geöffnet (über set-Editor-Route)

**Button-Logik im Editor:**

```javascript
function isCuratedRecord() { return record?.visibility === "curated"; }
function isCuratedAdminRecord() { return state.isAdmin && isCuratedRecord(); }
```

**„Kuratiertes Set archivieren"-Button** (`data-phenomena-curated-toggle-action`):
```javascript
const showCuratedToggle = isCuratedAdminRecord();
curatedToggleButton.hidden = !showCuratedToggle;
```
→ Erscheint nur, wenn `state.isAdmin === true` UND `record.visibility === "curated"`.

**Antwort auf Diagnosefrage D:**
- Bei normalen USERn im Preset-Editor: `state.isAdmin = false` → Button ist `hidden`. Der Button erscheint **nicht** bei normalen Usern.
- Bei ADMINs bei neuen/nicht-kuratierten Sets: `record.visibility !== "curated"` → `isCuratedRecord() = false` → Button ist ebenfalls `hidden`.
- Der Button erscheint **ausschließlich** für ADMINs auf dem Preset-Editor-Route eines curated Sets.

**Discard/Delete-Button:**
```javascript
discardButton.textContent = isCuratedRecord() 
  ? state.labels.discard 
  : (record.state === "saved" ? state.labels.delete : state.labels.discard);
```

**Speichern:**
- Wenn `isCuratedAdminRecord()` → PUT `/api/research/admin/curated-sets/<set_id>` (globales Update)
- Wenn `editorMode === "preset"` und nicht Admin → POST `/api/research/sets` (neue private Kopie)
- Wenn `editorMode === "set"` → PUT `/api/research/sets/<set_id>/items` + PATCH

---

## 7. Rollenrechte-Ist-Zustand

### USER (role = "user")

| Aktion | Per API möglich? | Auth-Schutz |
|---|---|---|
| Eigene Sets anlegen (private) | Ja | JWT required |
| Eigene Sets lesen | Ja | JWT + owner check |
| Eigene Sets bearbeiten | Ja | JWT + owner check |
| Eigene Sets löschen | Ja | JWT + owner check |
| Kuratierte Sets lesen (saved) | Ja | JWT required |
| Kuratierte Sets archivieren | **Nein** | `_require_admin()` → 403 |
| Kuratiertes Set global aktualisieren | **Nein** | `_require_admin()` → 403 |
| Neues kuratiertes Set anlegen | **Nein** | `_require_admin()` → 403 |
| Archivierte curated Sets sehen | **Nein** | `include_archived_curated` → 403 wenn kein Admin |
| Anderes User-Set lesen | **Nein** | owner_user_id filter → 404 |
| Scope ändern (private → curated) | **Nein** | Kein Endpunkt existiert |

### ADMIN (role = "admin")

| Aktion | Per API möglich? | Auth-Schutz |
|---|---|---|
| Alle USER-Aktionen | Ja | wie USER |
| Neues kuratiertes Set anlegen | Ja | JWT + `_require_admin()` |
| Kuratiertes Set global aktualisieren | Ja | JWT + `_require_admin()` |
| Kuratiertes Set archivieren | Ja | JWT + `_require_admin()` |
| Archiviertes Set reaktivieren | Ja | JWT + `_require_admin()` |
| Archivierte curated Sets sehen | Ja | `include_archived_curated` + admin check |

---

## 8. Abgleich mit Zielbild

Aus `docs/spec/research-access.md` und `docs/plans/phenomena_plan.md`:

| Zielbild | Status |
|---|---|
| Kuratierte Einträge exposieren „Ansehen" und „Modifizieren" | Abweichend: „Modifizieren" wurde durch „Kuratiertes Set bearbeiten" (admin only) + „Als eigenes Set bearbeiten" (alle) ersetzt. Korrektere Trennung, aber Spec nennt noch „Modifizieren" |
| Custom-Einträge exposieren „Bearbeiten" + Overflow „Umbenennen"/"Löschen" | Erreicht |
| Kuratierte Sets nicht löschbar aus Overview | Erreicht (kein Löschen für curated in Overview) |
| Kuratierte Sets nicht direkt überschreibbar durch USER | Erreicht |
| Spec: „Speichern als" ist nicht sichtbar im productive Editor | Erreicht (kein Save-As-Button im Editor-UI) |
| DB als einzige Set-Quelle | Erreicht |
| Admin kann curated Sets in-place aktualisieren | Erreicht |
| Archivieren nur als Soft-Delete (lifecycle=archived) | Erreicht |
| Neues Set für ADMINs mit Scope-Wahl | **Fehlt** – kein UI/API dafür |
| Seed/Migration von JSON-Presets nach DB | **Fehlt** – muss manuell oder per Skript erfolgen |

---

## 9. Gefundene Abweichungen und Bugs

### Bug 1: Fehlender i18n-Key `common.status.archived`

**Datei:** `app/src/app/i18n.py`

In `research_phenomena_views.py` (Zeile 204) wird `"common.status.archived"` über `_t()` aufgerufen:
```python
"common.status.archived" if stored_set.lifecycle == "archived" else "common.status.curated"
```

In `_editor_status_labels()` (Zeile 54) wird `"archived": "common.status.archived"` als Key übergeben.

Aber in `i18n.py` ist dieser Key **nicht definiert** – weder für `de` noch für `en`. Vorhandene `common.status.*` Keys: `curated`, `custom`, `saved`, `unsaved`, `new`. `archived` fehlt.

**Auswirkung:** Der Fallback in `translate()` gibt den Raw-Key `common.status.archived` zurück, oder – je nach Implementation – einen leeren String oder Fehlerwert.

### Bug 2: Keine Rollenprüfungstests für Admin-API-Endpunkte

**Dateien:** `app/tests/test_research_sets.py`

Es gibt keine Tests die prüfen:
- Ein normaler USER erhält 403 bei `POST /api/research/admin/curated-sets`
- Ein normaler USER erhält 403 bei `PUT /api/research/admin/curated-sets/<id>`
- Ein normaler USER erhält 403 bei `POST /api/research/admin/curated-sets/<id>/archive`
- Ein normaler USER erhält 403 bei `POST /api/research/admin/curated-sets/<id>/reactivate`
- Ein nicht-authentifizierter User erhält 401 an diesen Endpunkten

Die serverseitige Prüfung `_require_admin()` ist implementiert und korrekt, aber ungetestet. Regressionsschutz fehlt.

### Abweichung 3: Kein Admin-Flow für neues kuratiertes Set aus der UI

In der UI gibt es keinen Weg für ADMINs, beim Anlegen eines neuen Sets den Scope `curated` zu wählen. Der „Neues Set"-Button im Overview ruft immer `POST /api/research/sets` → immer `visibility="private"`.

Um ein kuratiertes Set anzulegen, muss der Admin:
1. Direkt `POST /api/research/admin/curated-sets` aufrufen (API, kein UI)
2. Oder ein privates Set anlegen und dann... es gibt keinen Konvertierungs-Endpunkt.

**Diagnosefrage F:** Kein UI-Flow für Scope-Wahl beim Anlegen. Das API für curated-Set-Anlegen existiert, aber kein UI-Einstiegspunkt.

### Abweichung 4: `phenomena_presets.json` ist orphaned

`load_phenomena_presets()` und `load_phenomena_preset_map()` in `research_presets.py` werden von keinem produktiven Applikationscode mehr aufgerufen. Die `phenomena_presets.json`-Dateien in `data/config/research_player/` sind nicht mehr Runtime-aktiv.

**Diagnosefrage A:** Produktive Phänomene-Sets liegen **ausschließlich in PostgreSQL**. Die JSON-Dateien sind Legacy-Artefakte.

**Risiko:** Ein zukünftiger Entwickler könnte `load_phenomena_presets()` irrtümlich als aktive Quelle betrachten.

### Abweichung 5: Kein Endpunkt und kein UI für Scope-Wechsel private→curated

**Diagnosefrage C:** Es gibt keinen API-Endpunkt, der ein bestehendes privates Set in ein kuratiertes Set umwandelt. Die DB-Constraints würden das technisch erlauben (wenn owner_user_id=NULL gesetzt und visibility='curated' gesetzt wird), aber kein Service-Layer-Code implementiert das.

**Diagnosefrage E:** Ein normaler USER kann per API kein curated Set anlegen, archivieren oder global ändern. Das ist korrekt implementiert.

### Abweichung 6: Spec nennt noch „Modifizieren" für curated Sets

`docs/plans/phenomena_plan.md` spricht von `Modifizieren` als Aktion für kuratierte Sets. Implementiert sind `Ansehen` + `Als eigenes Set bearbeiten` + (für Admins) `Kuratiertes Set bearbeiten`. Der i18n-Key `common.actions.modify` ist noch vorhanden aber nicht verwendet.

---

## 10. Veraltete oder widersprüchliche Dokumentation

- `docs/plans/phenomena_plan.md`: Planungsdokument, enthält noch „Modifizieren" als Aktion und beschreibt keinen Admin-Scope-Flow. Ist als veralteter Plan markiert (`Statushinweis: Planungsstand`), aber nicht mit aktuellem Stand abgeglichen.
- `docs/spec/research-capabilities.md` (Zeile 117): `phenomena is productive ... when the canonical task catalogs and phenomena_presets.json load successfully` – dies ist **überholt**. Der Code prüft nur noch `load_task_catalogs()`, nicht mehr `load_phenomena_presets()`. Die `phenomena_presets.json` ist nicht mehr Teil der productive-Erkennung.
- `docs/spec/platform-data-files.md` (Zeilen 352-353): Nennt `phenomena_presets.json` als kanonische Config-Datei. Stimmt nicht mehr mit der Implementierung überein (Legacy).

---

## 11. Migrations- und Datenrisiken

### Risiko 1: Keine Migration der JSON-Presets nach PostgreSQL

Die `phenomena_presets.json`-Dateien enthalten kuratierte Sets (z.B. 4 Sets für `spanish`). Diese existieren **nicht** in der PostgreSQL-Datenbank, außer sie wurden manuell per Admin-API angelegt. Beim Start eines frischen Systems sind keine kuratierten Sets in der DB vorhanden (außer dem Entwicklungs-Testset via `ensure_curated_test_set`).

**Datenrisiko:** In Produktion sind die kuratierten Sets aus den JSON-Dateien nicht sichtbar, solange sie nicht per API in die DB eingetragen wurden.

### Risiko 2: `source_curated_set_id ON DELETE SET NULL`

Wenn ein kuratiertes Set gelöscht würde (was per API nicht möglich ist, aber direkt per DB), werden alle `source_curated_set_id`-Referenzen auf NULL gesetzt. Private Kopien bleiben erhalten, verlieren aber ihre Provenienz-Information.

### Risiko 3: User-Löschung löscht alle privaten Sets (CASCADE)

`owner_user_id FK → users ON DELETE CASCADE` – wenn ein User-Account gelöscht wird, werden alle seine privaten Research-Sets automatisch mitgelöscht. Kein Soft-Delete, kein Transfer-Mechanismus.

### Risiko 4: Ablaufende Drafts

Private Drafts haben `expires_at`. Expired Drafts werden durch `delete_expired_drafts()` bereinigt (14 Tage TTL). Es gibt keinen Cronjob-Beleg in der Codebasis – es ist unklar, ob diese Bereinigung regulär ausgeführt wird.

---

## 12. Empfohlener Umsetzungsplan

### Notwendige i18n-Änderungen

**Dringend (Bug 1):** `common.status.archived` in `app/src/app/i18n.py` ergänzen:
```python
"common.status.archived": "archiviert",  # de
"common.status.archived": "archived",    # en
```

### Notwendige Tests

**Dringend (Bug 2):** Admin-Rollenprüfungstests in `app/tests/test_research_sets.py`:
- User 403 bei `POST /api/research/admin/curated-sets`
- User 403 bei `PUT /api/research/admin/curated-sets/<id>`
- User 403 bei `POST /api/research/admin/curated-sets/<id>/archive`
- User 403 bei `POST /api/research/admin/curated-sets/<id>/reactivate`
- Unauthenticated 401 an allen Admin-Endpunkten

### Notwendige DB-Änderungen

Keine dringenden. Die aktuelle Schemastruktur ist korrekt und konsistent.

Optional: Einen Service-Layer-Endpunkt für Scope-Wechsel private→curated hinzufügen (erfordert: `owner_user_id=NULL`, `visibility='curated'`, lifecycle-Anpassung).

### Notwendige API-Änderungen

Optional (Abweichung 3 + 5): Scope-Wahl beim Anlegen neuer Sets für ADMINs. Könnte durch Parameter `visibility` in `POST /api/research/sets` oder einen separaten UI-Flow für ADMINs gelöst werden.

### Notwendige UI-Änderungen

Optional (Abweichung 3): Im „Neues Set"-Flow im Overview einen Scope-Wahlschritt für ADMINs ergänzen, oder einen separaten „Neues kuratiertes Set"-Button.

### Notwendige Doku-Updates

1. `docs/spec/research-capabilities.md` Zeile 117: `phenomena_presets.json` aus productive-Bedingung entfernen. Korrekte Formulierung: phenomena ist produktiv, wenn `task_catalogs` (wordlist + text) ladbar sind.
2. `docs/spec/platform-data-files.md` Zeilen 352-353: `phenomena_presets.json` als Legacy markieren.
3. `docs/plans/phenomena_plan.md`: Entweder löschen oder als vollständig veraltet markieren.

### Datenmigration erforderlich?

**Bedingt** – wenn die kuratierten Preset-Inhalte aus den `phenomena_presets.json`-Dateien in Produktion verfügbar sein sollen, müssen diese per `POST /api/research/admin/curated-sets` oder per Skript in die PostgreSQL-DB eingespielt werden. Es gibt aktuell kein Migrations-Skript dafür.

### Config-Presets nach PostgreSQL migrieren?

**Bedingt** – die Dateien sind produktiv tot. Ein einmaliges Import-Skript, das die `phenomena_presets.json` Einträge per Service-Layer als DB-curated Sets anlegt, wäre sinnvoll, um Konsistenz herzustellen. Danach können die `phenomena_presets.json`-Dateien und die Loader-Funktionen entfernt werden.

### Einschätzung: **Klein bis Mittel**

- Dringend (i18n-Bug + Tests): **Klein** – 2-3 Stunden
- Optional (Admin-UI-Flow + Datenmigration + Doku): **Mittel**

---

## 13. Tests die ergänzt/geändert werden müssen

### Ergänzen in `app/tests/test_research_sets.py`

```python
# Admin-Rollenprüfung für alle admin curated-set Endpunkte
def test_user_cannot_create_curated_set(set_app):
    # POST /api/research/admin/curated-sets mit user role → 403

def test_user_cannot_update_curated_set(set_app):
    # PUT /api/research/admin/curated-sets/<id> mit user role → 403

def test_user_cannot_archive_curated_set(set_app):
    # POST /api/research/admin/curated-sets/<id>/archive mit user role → 403

def test_user_cannot_reactivate_curated_set(set_app):
    # POST /api/research/admin/curated-sets/<id>/reactivate mit user role → 403

def test_unauthenticated_cannot_call_admin_endpoints(set_app):
    # Ohne Authorization-Header → 401 (oder 422 je nach JWT-Config)
```

### Ergänzen in `app/tests/test_research_phenomena.py`

```python
# i18n-Key archived wird korrekt aufgelöst (nicht als Raw-Key sichtbar)
def test_archived_curated_set_shows_correct_status_label(phenomena_app):
    # archived curated Set anlegen, Overview laden, prüfen dass Label nicht "common.status.archived" ist
```

---

## 14. Server- und Migrationsauswirkungen

- **Migration 0006** (die wichtigste) ist idempotent und rückwärtskompatibel. Sie konvertiert bestehende `state`-Spalte zu `lifecycle`, fügt `visibility` hinzu und setzt bestehende Sets auf `visibility = 'private'`. Bereits in Produktion angewendet (laut commit-Historie).
- Kein Hot-Deploy-Risiko durch die beschriebenen Korrekturen (i18n + Tests).
- Falls eine Datenmigration der JSON-Presets in die DB durchgeführt wird: Diese sollte durch ein separates Skript oder Admin-API-Aufruf erfolgen, nicht als DB-Migration. Risiko: niedrig, da keine bestehenden DB-Daten überschrieben werden.

---

## 15. Offene Fragen

1. **Wird `delete_expired_drafts()` regulär ausgeführt?** Kein Cronjob-Beleg in der Codebasis gefunden. Falls nicht, akkumulieren abgelaufene Drafts in der DB ohne Bereinigung.

2. **Sollen die kuratierten Presets aus `phenomena_presets.json` in Produktion übernommen werden?** Die Dateien existieren (4 Sets für `spanish`, 0 für `french`, unbekannt für `english`/`german`). Ohne explizite Entscheidung sind sie nicht in der DB.

3. **Gibt es in Produktion bereits DB-curated-Sets (außer dem Test-Set)?** Nicht aus dem Code-Artefakt erkennbar. Müsste per DB-Query auf dem Produktionssystem geprüft werden.

4. **Wird `common.actions.modify` (i18n-Key) noch irgendwo verwendet?** Der Key ist vorhanden aber scheint nach der Umbenennung von „Modifizieren" zu „Als eigenes Set bearbeiten" nicht mehr referenziert. Sollte bereinigt werden.

---

## 16. Präzisierung 2026-05-28 – Finale Button-/Action-Logik (USER + ADMIN, aktualisiert)

Die Abschnitte 6 und 9 enthielten den historischen Ist-Zustand. Dieser Abschnitt beschreibt den finalen implementierten Stand nach drei Runs (USER-Matrix + ADMIN-Matrix + Editor-Finalisierung).

### Übersicht (USER)

- **Kuratierte Sets** zeigen für USER ausschließlich **„Ansehen"** (Navigation Pill).
- **„Als eigenes Set bearbeiten"** ist für USER nicht sichtbar.
- Technisch: Template prüft `{% if entry.edit_curated_href %}` (nur für ADMIN gesetzt).
- **Custom Sets** zeigen „Bearbeiten" + Overflow-Menü (Umbenennen/Löschen).

### Übersicht (ADMIN)

- **Kuratierte Sets** zeigen: **„Ansehen"** + **„Bearbeiten"** (kein „Kuratiertes Set bearbeiten", kein „Als eigenes Set bearbeiten").
- Technisch: Template nutzt `edit_curated_href` (nur für ADMIN gesetzt) und zeigt es mit Label `common.actions.edit`.
- **Custom Sets**: Bearbeiten + Overflow.

### Editor (USER)

| Zustand | Hauptleiste | Overflow |
|---|---|---|
| Kuratiertes Set, clean | Speichern (disabled) | – |
| Kuratiertes Set, dirty | Änderungen verwerfen, Speichern → Confirm-Dialog für Custom-Kopie | – |
| Neues Set (draft) | Speichern | – |
| Gespeichertes Custom Set, dirty | Änderungen verwerfen, Speichern | Set löschen |
| Gespeichertes Custom Set, clean | Speichern (disabled) | Set löschen |

- USER sieht keine Admin-/Curated-Aktionsbuttons (serverseitig nicht gerendert).
- Discard-Button: `discardButton.hidden = !dirty` (nur wenn dirty).
- curatedHint: nur sichtbar wenn dirty.
- Speichern von kuratiertem Set → Confirm-Dialog → eigene Custom-Kopie (POST /sets mit `source_curated_set_id`).

### Editor (ADMIN)

| Zustand | Hauptleiste | Overflow |
|---|---|---|
| Kuratiertes Set, clean | Als Custom Set speichern | Kuratiertes Set löschen |
| Kuratiertes Set, dirty | Änderungen verwerfen, Als Custom Set speichern, Änderungen speichern | Kuratiertes Set löschen |
| Neues Custom Set | Speichern, Als kuratiertes Set speichern | – |
| Gespeichertes Custom Set, dirty | Änderungen verwerfen, Speichern, Als kuratiertes Set speichern | Set löschen |
| Gespeichertes Custom Set, clean | Als kuratiertes Set speichern | Set löschen |

- „Änderungen speichern" (war: „Kuratiertes Set aktualisieren") → aktualisiert kuratiertes Set in-place.
- „Als Custom Set speichern" → erstellt private Kopie mit aktuellem Stand; eigene Custom-Route.
- „Als kuratiertes Set speichern" → publiziert Custom-Set als neues kuratiertes Set.
- Delete-Aktionen nur im Overflow, mit Confirm-Dialog.

### Overflow-Menü

- Beide Pages (Overview, Editor) nutzen `<details data-overflow-menu>`.
- Utility `app/static/js/modules/core/overflow-menu.js` steuert:
  - Klick außerhalb → schließt alle offenen Menus.
  - Escape → schließt, Fokus zurück zu Summary.
  - Nur ein Menu gleichzeitig offen.
  - Klick auf Menü-Aktion → schließt Menu.
- `aria-expanded` wird automatisch vom Browser für `<details>/<summary>` verwaltet.

### Technische Architektur (final)

- Admin-only Buttons (`delete-curated`, `save-as-custom`, `save-as-curated`) werden serverseitig NUR für ADMIN gerendert (`{% if promat_page.is_admin %}`).
- `is_admin` wird von Python-View-Buildern ins Page-Dict gesetzt.
- `syncStatus()` deklariert `const dirty = isDirty()` als erste Zeile (Regression-Schutz).
- Alle Admin-Buttons starten `hidden`; JS zeigt/versteckt je nach Kontext.
- Overflow-Container startet `hidden`; JS zeigt ihn, wenn mindestens eine Overflow-Aktion sichtbar.
- `source_curated_set_id` ist Herkunfts-Metadatum, nicht aktuelle Sichtbarkeit.

### Finale Hauptleiste vs Overflow (nach Editor-Finalisierung 2026-05-28)

**Grundregel:**
- Hauptleiste: nur Arbeits-Zustands-Aktionen (Speichern / Verwerfen).
- Overflow: alternative Speicherziele + Löschaktionen.
- Overflow nicht anzeigen, wenn keine Aktionen vorhanden sind.

| Zustand | Hauptleiste | Overflow |
|---|---|---|
| ADMIN + curated clean | – | Als Custom Set speichern · Kuratiertes Set löschen |
| ADMIN + curated dirty | Änderungen verwerfen · Änderungen speichern | Als Custom Set speichern · Kuratiertes Set löschen |
| ADMIN + new custom | Speichern | Als kuratiertes Set speichern |
| ADMIN + saved custom clean | – | Als kuratiertes Set speichern · Set löschen |
| ADMIN + saved custom dirty | Änderungen verwerfen · Speichern | Als kuratiertes Set speichern · Set löschen |
| USER + curated clean | – | – (kein Overflow) |
| USER + curated dirty | Änderungen verwerfen · Speichern → Confirm Custom-Kopie | – (kein Overflow) |
| USER + new custom | Speichern | – (kein Overflow) |
| USER + saved custom clean | – | Set löschen |
| USER + saved custom dirty | Änderungen verwerfen · Speichern | Set löschen |

**Speichern-Sichtbarkeit:**
`saveButton.hidden = !(isDraftCustom || dirty)` — d.h. neues Custom Set immer, sonst nur wenn dirty.

**Discard-Sichtbarkeit:**
`discardButton.hidden = !dirty` — immer nur wenn dirty.

**Warnung nach Speichern:**
`commitSave()` ruft `baseline = snapshot()` nach jeder Speicheroperation auf. `isDirty()` ist danach false → keine false Leave-Warnung.

**Layout:**
`pm-phenomena-editor__header` ist ein 1-spaltige Grid (`grid-template-columns: 1fr`). Titel/Status/Hint stehen auf voller Breite, Aktionsleiste darunter auf eigener Zeile.

**Overflow-CSS:**
Editor-Overflow nutzt `pm-comparison-more-filters pm-phenomena-overflow` (identisch mit Übersicht-Pattern). Kein nativer `<summary>`-Pfeil sichtbar.

### Nicht-Ziele

- Keine neuen Admin-Flows außer dem Beschriebenen.
- Keine Backend-Rechte geändert.
- Keine DB-Migration erforderlich.
- `phenomena_presets.json` Legacy-Status bleibt unverändert.
