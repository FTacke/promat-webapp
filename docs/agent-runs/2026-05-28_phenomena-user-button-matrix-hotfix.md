# Phänomene USER-Aktionsmatrix – Hotfix JS-Crash (dirty undefiniert)

Datum: 2026-05-28

## Ziel

Sofortbehebung eines ReferenceError (`dirty is not defined`) in `research-phenomena-editor.js:syncStatus()`, der den Editor vollständig crashte und den USER-Button-Fix aus dem vorangegangenen Run unwirksam machte. Gleichzeitig Härtung durch serverseitiges Nicht-Rendern der Admin-only-Buttons für USER.

## Consulted Sources

- `docs/agent-runs/2026-05-28_phenomena-user-button-matrix.md` (vorheriger Run)
- `app/static/js/pages/research-phenomena-editor.js`
- `app/templates/pages/research_phenomena_editor.html`
- `app/src/app/research_phenomena_views.py`
- `app/tests/test_research_phenomena.py`

## Ursache

Im vorherigen Run wurde `dirty` in zwei Stellen in `syncStatus()` verwendet:
- `discardButton.hidden = !isAdmin && !dirty`
- `curatedHint.hidden = !dirty`

Aber `dirty` war nicht als lokale Variable in `syncStatus()` deklariert – `isDirty()` existiert als Funktion, wurde aber nie in eine `const` aufgelöst. Der Editor crashte beim Laden mit `ReferenceError: dirty is not defined` an Zeile 297. Dadurch lief keine JS-Logik durch, alle Button-Hiding-Änderungen waren wirkungslos.

## Geänderte Bereiche

### `app/static/js/pages/research-phenomena-editor.js`
- Erste Zeile von `syncStatus()`: `const dirty = isDirty();` ergänzt.
- Alle nachfolgenden Verwendungen von `dirty` in `syncStatus()` sind jetzt korrekt aufgelöst.

### `app/src/app/research_phenomena_views.py`
- `build_phenomena_preset_editor_page()` und `build_phenomena_set_editor_page()`: `"is_admin": _is_admin()` zum Page-Dict hinzugefügt.
- Damit kann das Template serverseitig auf die Admin-Rolle prüfen.

### `app/templates/pages/research_phenomena_editor.html`
- `data-phenomena-delete-curated-action` und `data-phenomena-save-as-curated-action` werden jetzt nur noch für `{% if promat_page.is_admin %}` gerendert.
- USER erhält diese Buttons nicht mehr im DOM – weder sichtbar noch versteckt.
- Falls JS ausfällt, sind keine Admin-Buttons für USER vorhanden.

### `app/tests/test_research_phenomena.py`
- Neue Regression: `test_editor_js_dirty_declared_before_use_in_sync_status` – prüft dass `const dirty = isDirty()` in `syncStatus()` vor jeder Verwendung von `dirty` steht.
- `test_editor_user_preset_view_has_is_admin_false_in_client_state`: Assertions angepasst: `not in html` für Admin-Buttons (war `in html`).
- `test_editor_user_new_custom_set_has_is_admin_false_and_buttons_present`: desgleichen.
- Meine neuen Usertests aus dem vorherigen Run: `data-phenomena-delete-curated-action hidden` → `data-phenomena-delete-curated-action not in html`.

## Wichtige Entscheidungen

- **Serverseitiges Nicht-Rendern statt JS-Hiding**: Admin-Buttons (`delete-curated`, `save-as-curated`) werden für USER vollständig aus dem HTML ausgelassen. Das ist robuster als reines JS-Hiding: kein Flash-Risk, kein Abhängigkeit von JS-Ausführung für Sicherheitsrelevanz.
- **JS bleibt defensiv**: `syncStatus()` prüft weiterhin `if (deleteCuratedButton)` vor Zugriff – null-sicher auch wenn der Button fehlt. Event-Listener nutzen Optional Chaining `?.`.

## Abweichungen

- Keine. Die Korrektur schärft das Zielbild aus dem vorherigen Run.

## Verifikation

```
python -m pytest app/tests/test_research_phenomena.py -q  → 42 passed
python -m pytest app/tests/test_research_sets.py -q       → 39 passed
python -m ruff check .                                    → All checks passed!
python scripts/ci_governance_checks.py                    → All governance checks passed.
python -m compileall -q app/src app/tests                 → (kein Output = OK)
```

**Browser-QA** (USER-Account, nach Hotfix):

| Seite | Console errors | Sichtbare Buttons | Ergebnis |
|---|---|---|---|
| Editor – Kuratiertes Set initial | keine | Speichern (disabled), kein Discard, kein Kuratiert-Button | pass |
| Editor – Kuratiertes Set, Item gewählt | keine | Speichern (aktiv), Änderungen verwerfen sichtbar | pass |
| Editor – Speichern-Klick nach Änderung | keine | Confirm-Dialog erscheint | pass |
| Editor – Neues Set | keine | Speichern, kein Discard initial, kein Kuratiert-Button | pass |
| Editor – Gespeichertes Custom Set | keine | Speichern (bei Änderung), Set löschen | pass |
| Item-Auswahl (toggle) | keine | Items togglen korrekt | pass |

## Offene Punkte

- Admin-Bereich separat prüfen (nächster dedizierter Run).
- `common.actions.modify` i18n-Key bereinigen falls nicht mehr genutzt.

## Nächste sinnvolle Schritte

- Admin-Editor-Matrix separat prüfen.
- Serverseitiges Rendering-Pattern (`is_admin` im Page-Dict) für andere rollenabhängige Editor-Seiten erwägen.
