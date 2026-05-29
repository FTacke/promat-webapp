# Phänomene-Set-Editor: Layout-Neuordnung

**Datum:** 2026-05-29  
**Status:** Abgeschlossen

## Ziel

Semantisch klarere Anordnung im Phänomene-Set-Editor ohne Redesign. Keine neuen Features, keine Änderung an Speicherlogik oder Rechte-Matrix.

## Geänderte Dateien

| Datei | Art der Änderung |
|---|---|
| `app/templates/pages/research_phenomena_editor.html` | Layout-Restructuring: flache Elementstruktur, Aktionsleiste unten, Label umbenannt |
| `app/static/css/20_layout.css` | Veraltete Klassen entfernt (`header`, `header-main`, `header-actions`, `note-card`), `note-field` in display:grid-Gruppe |
| `app/static/css/30_components.css` | `max-width` aus title-row entfernt, `border-top` aus note-card entfernt, header-actions-Styles entfernt |
| `app/src/app/i18n.py` | Neue Keys: `research.phenomena.editor.description` und `research.phenomena.editor.description_placeholder` (de + en) |
| `app/src/app/research_phenomena_views.py` | Labels-Dict: `note` → `research.phenomena.editor.description`, `notePlaceholder` → `research.phenomena.editor.description_placeholder` |

## Neue Template-Struktur (workspace-head)

Vorher: `header` → [`header-main`, `header-actions`] + separates `note-card`

Nachher: flache Reihenfolge direkt im `workspace-head`:
1. `pm-phenomena-editor__title-field` (Set-Name-Input, volle Breite)
2. `pm-phenomena-editor__status-row` (Badges + Statustext)
3. `pm-phenomena-editor__hint` (Herkunftshinweis, falls vorhanden)
4. `pm-phenomena-editor__note-field` (Beschreibung-Textarea, volle Breite)
5. `pm-phenomena-editor__action-bar pm-action-row pm-action-row--end` (CTAs rechts, mobile gestapelt)

## Verwendete Patterns

- **Zurück-Button:** Bereits via `content_header.back_link` → `_content_header.html` → `render_navigation_pill` (direction: back) — war korrekt verdrahtet, keine Änderung nötig.
- **Aktionsleiste:** `pm-action-row pm-action-row--end` — bestehendes Pattern (flex-end desktop, column+stretch mobile bei ≤719 px).
- **Beschreibungsfeld:** Weiterhin `pm-phenomena-editor__note-field` + `pm-phenomena-editor__note-input` — bestehende CSS-Regeln greifen unverändert.
- **Edit-Icon im Namensfeld:** `pm-phenomena-editor__title-affordance` + `pm-icon-mask--edit` — unverändert.
- **Overflow:** `pm-comparison-more-filters` + `data-overflow-menu` — unverändert.

## `(modifiziert)`-Zusatz

Bereits vor diesem Run im JS implementiert (`persistSaveAsCopy`, Funktion in `research-phenomena-editor.js`):
- Wird angehängt wenn `label === originalLabel` (kein bewusster Umbenennung) und `isCuratedRecord()` und nicht bereits `endsWith(" (modifiziert)")`.
- Gilt für USER (Speichern → Kopie) und ADMIN (Als Custom Set speichern) — beide Pfade rufen `persistSaveAsCopy()` auf.
- Test: `test_editor_static_js_persist_save_as_copy_appends_modified_suffix` ✓

## Testergebnis

```
111 passed  (test_research_phenomena.py + test_research_sets.py)
ruff: All checks passed
governance: All checks passed
compileall: OK
```
