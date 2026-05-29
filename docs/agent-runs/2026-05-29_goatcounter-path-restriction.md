# 2026-05-29 — GoatCounter: Einschränkung auf öffentliche Seiten

## Ausgangslage

GoatCounter wurde über `base.html` global auf allen Seiten gerendert, also auch auf `/login`, `/auth/*` und `/admin/*`. Die Production-URL wurde als fester Wert im Context Processor injiziert.

## Lösung

Die Einschränkung erfolgt im Context Processor `inject_utilities()` in `app/src/app/__init__.py`. Der Wert `goatcounter_url` wird zu leerem String, wenn der Pfad mit `/admin`, `/auth` beginnt oder exakt `/login` ist. Das Template-Check `{% if goatcounter_url %}` in `base.html` bleibt unverändert.

```python
_gc_url = app.config.get("GOATCOUNTER_URL", "")
_gc_path = request.path
_goatcounter_url = (
    _gc_url
    if _gc_url
    and not (
        _gc_path.startswith("/admin")
        or _gc_path.startswith("/auth")
        or _gc_path == "/login"
    )
    else ""
)
```

Keine CSP-Änderung nötig, da CSP-Header unabhängig von der Script-Ausgabe gesetzt werden.

## Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `app/src/app/__init__.py` | Path-Exclusion-Logik in `inject_utilities()` |
| `app/tests/test_auth_phase1.py` | `test_goatcounter_script_renders_from_single_central_config` auf `/privacy` umgestellt; 3 neue Tests für Login, Auth-Account und Admin-Analytics |

## Neue Tests

- `test_goatcounter_script_renders_on_public_page_with_production_config` — `/privacy` rendert Script mit gesetzter URL
- `test_goatcounter_script_not_rendered_on_login_page_with_production_config` — `/login` rendert kein Script, auch wenn URL gesetzt
- `test_goatcounter_script_not_rendered_on_auth_account_with_production_config` — `/auth/account` (eingeloggt) rendert kein Script
- `test_goatcounter_script_not_rendered_on_admin_analytics_page` — `/admin/analytics/page` (eingeloggt als Admin) rendert kein Script

## CI-Ergebnis

```
644 passed, 120 warnings
ruff: All checks passed
Governance: All governance checks passed
compileall: clean
```
