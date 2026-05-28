# Phänomene USER-Aktionsmatrix – Button-Sichtbarkeit bereinigt

Datum: 2026-05-28

## Ziel

Ausschließlich den USER-Bereich der Phänomene-Set-UI glätten. Buttons, die für USER fachlich falsch oder technisch wirkungslos sind, werden korrekt ein-/ausgeblendet. Admin-Bereich wird nicht neu gestaltet.

## Consulted Sources

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

### `app/templates/pages/research_phenomena_overview.html`
- „Als eigenes Set bearbeiten" (Link oder Copy-Button) wird in `{% if entry.show_edit_as_own %}` eingeschlossen.
- USER sieht bei kuratierten Sets ab jetzt ausschließlich „Ansehen".

### `app/src/app/research_phenomena_views.py`
- `_overview_card_from_curated_set()`: neues Feld `show_edit_as_own = is_admin`.
- `_editor_state()`: zwei neue Labelschlüssel `saveCopyTitle`, `saveCopyMessage` in die Labels-Map aufgenommen.

### `app/static/js/pages/research-phenomena-editor.js`
- `syncStatus()`: `discardButton.hidden = !isAdmin && !dirty` — USER sieht „Änderungen verwerfen" nur wenn dirty.
- `syncStatus()`: `curatedHint.hidden = !dirty` für USER-Kontext — Hinweis erscheint erst bei Änderungen.
- `saveButton` click-Handler: Wenn `!state.isAdmin && isCuratedRecord() && isDirty()` → Confirm-Dialog mit `saveCopyTitle`/`saveCopyMessage` vor der Speicherung.
- `persistCurrentRecord()`: bei `editorMode === "preset"` wird jetzt `source_curated_set_id: record.set_id` übergeben (war `preset_id: record.source_preset_id` → führte zu fehlender Provenienz).

### `app/templates/pages/research_phenomena_editor.html`
- Discard-Button startet mit `hidden`-Attribut (kein Flash vor JS-Initialisierung).

### `app/src/app/i18n.py`
- `research.phenomena.editor.curated_hint` (DE + EN): Text präzisiert — nicht mehr „Änderungen an diesem kuratierten Set...".
  - DE: „Beim Speichern wird eine eigene Kopie angelegt – das kuratierte Original bleibt unverändert."
  - EN: „Saving creates your own copy – the curated original stays unchanged."
- Neue Keys (DE + EN):
  - `research.phenomena.editor.save_copy_title`
  - `research.phenomena.editor.save_copy_message`

### `app/tests/test_research_phenomena.py`
- Bestehende Assertions angepasst: `curatedHint`-Texte und `show_edit_as_own`-Felder.
- `test_public_phenomena_overview_route_renders_split_overview`: assert `">Als eigenes Set bearbeiten<" not in html` für USER.
- 14 neue Tests ergänzt (USER-Matrix Overview + Editor + Regression + JS-Source-Checks).

## Wichtige Entscheidungen

- **Kein Server-Side-Rendering für Admin-Buttons im Editor**: Die bestehende Architektur (Template rendert alle Buttons, JS kontrolliert Sichtbarkeit) bleibt erhalten. Admin-only-Buttons tragen `hidden` als Template-Default; `syncStatus()` hält `hidden` aufrecht wenn `isAdmin=false`.
- **Overview server-side**: `show_edit_as_own` wird serverseitig berechnet → der Copy-Button wird gar nicht erst gerendert für USER. Kein JS-Gating nötig.
- **Confirm-Dialog für USER+Curated-Save**: Wichtigster Hinweis (kuratiertes Set bleibt unverändert) gehört in den Dialog, nicht in einen dauerhaften Hint-Text.
- **`source_curated_set_id` in Copy-Flow**: Minimale Korrektur im `persistCurrentRecord()`-Pfad für `editorMode=preset`; kein Backend-Change nötig (Parameter existierte bereits).

## Abweichungen

- Keine Abweichungen vom spezifizierten USER-Zielbild.
- Admin-Bereich: unverändert, wie im Ziel definiert.
- Keine DB-Migration, kein Server-Hotfix.

## Verifikation

```
python -m pytest app/tests/test_research_phenomena.py -q  → 41 passed
python -m pytest app/tests/test_research_sets.py -q       → 39 passed
python -m ruff check .                                    → All checks passed!
python scripts/ci_governance_checks.py                    → All governance checks passed.
python -m compileall -q app/src app/tests                 → (kein Output = OK)
```

**Browser-QA** (USER-Account, Entwicklungsserver):

| Seite | Sichtbare Buttons | Erwartet | Ergebnis | Console errors |
|---|---|---|---|---|
| Übersicht – Kuratiertes Set | Ansehen | Nur Ansehen | pass | nein |
| Übersicht – Kuratiertes Set | kein „Als eigenes Set bearbeiten" | Nicht sichtbar | pass | nein |
| Editor – Kuratiertes Set initial | Speichern (disabled), kein Discard | Kein Discard wenn clean | pass | nein |
| Editor – Kuratiertes Set nach Änderung | Speichern (aktiv), Änderungen verwerfen | Beides aktiv | pass | nein |
| Editor – Kuratiertes Set, Speichern-Klick | Confirm-Dialog | Dialog erscheint | pass | nein |
| Editor – Neues Set | Speichern, kein Discard initial | Speichern aktiv | pass | nein |
| Editor – Gespeichertes Custom Set | Speichern (bei Änderung), Set löschen | Set löschen sichtbar | pass | nein |

## Offene Punkte

- Admin-Bereich wird separat geprüft (separater Run).
- `phenomena_presets.json` bleibt Legacy; kein Seeding-Skript in diesem Run.
- `delete_expired_drafts()` Cronjob-Status ungeklärt (aus Diagnose-Abschnitt 15 übernommen).

## Nächste sinnvolle Schritte

- Admin-Editor-Matrix prüfen (separater fokussierter Run).
- `common.actions.modify` i18n-Key bereinigen falls nicht mehr genutzt.
