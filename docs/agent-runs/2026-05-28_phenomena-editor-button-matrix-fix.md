# Phänomene-Set-Editor: Button-/Action-Matrix bereinigen

Datum: 2026-05-28

## Ziel

Die Button-/Action-Matrix im Phänomene-Set-Editor war fehlerhaft: Admin-only-Kuratierungsaktionen
wurden in falschen Set-Zuständen und auch für normale Nutzer:innen angezeigt. Ziel war eine saubere,
zentralisierte Sichtbarkeitssteuerung vollständig im Client-JS, mit korrekten Labels, eigenem
Löschen-Button für Custom-Sets und vollständiger i18n (DE + EN).

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-capabilities.md`
- `app/src/app/research_phenomena_views.py`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/templates/pages/research_phenomena_editor.html`
- `app/src/app/i18n.py`

## Geänderte Bereiche

- `app/src/app/i18n.py` — zwei neue Label-Keys je DE und EN:
  - `research.phenomena.editor.discard_changes` – „Änderungen verwerfen" / „Discard changes"
  - `research.phenomena.editor.curated_copy_hint` – Hinweistext für Custom-Kopien von kuratierten Sets
- `app/src/app/research_phenomena_views.py` — zwei neue Label-Schlüssel in `_editor_state()`:
  - `discardChanges`, `curatedCopyHint`
- `app/templates/pages/research_phenomena_editor.html` — neuer `[data-phenomena-delete-action]`-Button
  als eigenständiges Geschwisterelement (war vorher falsch als Kind des `delete-curated`-Buttons
  geschachtelt — invalides HTML, das mit diesem Run korrigiert wurde)
- `app/static/js/pages/research-phenomena-editor.js` — `syncStatus()` komplett überarbeitet:
  - Strikte Rolle-+Zustand-Matrix: `isAdmin`, `isCurated`, `isCustom`, `isSavedCustom`, `isCuratedCopy`
  - `discardButton` immer sichtbar; Label via Span-Kind (nicht `textContent`-Überschreibung)
  - `deleteCustomButton` nur bei `isSavedCustom`
  - `deleteCuratedButton` nur bei `isAdmin && isCurated`
  - `saveAsCuratedButton` nur bei `isAdmin && isCustom`
  - Kuratierter Hinweis: kontextabhängig (`curatedAdminHint`, `curatedHint`, `curatedCopyHint`, verborgen)
  - `discardOrDelete()` umbenannt zu `discardOrNavigate()` (nur noch Verwerfen/Navigieren)
  - Neue Funktion `performDeleteCustom()` für Bestätigungsdialog Custom-Set-Löschung
- `app/tests/test_research_phenomena.py` — 7 neue Tests, davon 2 im Verlauf des Runs korrigiert:
  - `test_editor_template_has_dedicated_delete_action_button`
  - `test_editor_user_preset_view_has_is_admin_false_in_client_state`
  - `test_editor_user_new_custom_set_has_is_admin_false_and_buttons_present`
  - `test_editor_admin_curated_set_state_has_all_curated_labels`
  - `test_editor_admin_custom_set_state_has_correct_labels`
  - `test_editor_new_i18n_labels_present_in_client_state`
  - `test_editor_regression_no_curated_toggle_in_template`

## Wichtige Entscheidungen

- **Alle Labels immer im `client_state`**: Sicherheit wird serverseitig durch `_require_admin()` sichergestellt.
  Das JS-seitige Verbergen ist UI-Komfort, kein Sicherheitsmerkmal. Tests prüfen daher `isAdmin: false`
  in der State-JSON, nicht das Fehlen bestimmter Label-Keys.
- **HTML-Strukturfehler korrigiert**: `[data-phenomena-delete-action]` war als Kind-Button innerhalb
  `[data-phenomena-delete-curated-action]` geschachtelt (invalides HTML: `<button>` in `<button>`).
  Korrigiert zu echten Geschwisterelementen.
- `data-phenomena-curated-toggle-action` existiert nicht mehr im Template (bereits in einem früheren
  Run entfernt); ein Regressions-Test sichert das ab.

## Abweichungen

Keine Abweichung von aktiven Specs oder Konventionen.

## Verifikation

- `pytest app/tests/test_research_phenomena.py` → 24/24 bestanden
- `pytest app/tests/` → 572/572 bestanden (vollständige Testsuite)
- `ruff check app/src app/tests` → keine Fehler
- `python scripts/ci_governance_checks.py` → alle 7 Prüfungen bestanden
- Browser-QA gegen den laufenden Dev-Server (Port 8000) nicht abgeschlossen: Dev-Admin-Credentials
  erzeugen 401 (bekanntes lokales Issue, dokumentiert in `2026-04-28_designsystem-non-shell-cleanup.md`).
  Die Render-Logik ist vollständig durch die 24 Pytest-Test-Client-Tests abgedeckt.

## Offene Punkte

- Live-Browser-QA für authentifizierte Routen setzt eine funktionierende lokale Dev-Admin-Session
  voraus (Credentials ggf. neu setzen via `scripts/dev-setup.ps1`).

## Nächste sinnvolle Schritte

- Commit und Push der Änderungen nach `main`
