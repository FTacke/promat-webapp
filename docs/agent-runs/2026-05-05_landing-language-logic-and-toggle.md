# 2026-05-05 · Landing Language Logic And Toggle

## Scope

- reuse the existing shared `DE | EN` switch on the public landing page without rendering the full topbar
- move landing-page copy out of `build_start_page()` into the shared translation layer
- centralize unprefixed-route language resolution and persist explicit manual language choices

## Changes

- added shared landing translation keys in `app/src/app/i18n.py`
- changed `build_start_page()` in `app/src/app/routes/public_content.py` so all visible landing copy now comes from `get_text(ui_lang, ...)`
- added shared request-language helpers in `app/src/app/i18n.py` for:
  - supported-language normalization
  - local path extraction
  - `Accept-Language` inference
  - request-level resolution priority
- updated `app/src/app/__init__.py`, `app/src/app/extensions/__init__.py`, and `app/src/app/routes/public.py` to use the same central resolver
- persisted explicit `lang` / `ui_lang` choices via the `pm_ui_lang` cookie
- changed generated language-switch targets so the shared switch marks explicit manual changes with `?lang=de` / `?lang=en`
- extracted the existing switch markup into `app/templates/partials/_ui_lang_switch.html`
- reused that partial in `app/templates/partials/_top_app_bar.html` and in `app/templates/pages/landing.html`
- added only landing-container positioning in `app/static/css/20_layout.css`; no toggle-specific landing styles were introduced
- updated `app/static/js/modules/navigation/app-bar.js` so client-side switch syncing follows the same `lang`-aware URL behavior
- updated `docs/spec/platform-data-files.md` for the shared unprefixed-route language priority and the landing-page switch rule

## Language Priority

1. explicit path language when a `/{ui_lang}` route exists
2. explicit URL language via `lang` or `ui_lang`
3. stored user preference cookie `pm_ui_lang`
4. local route-context language from `next`, same-app referrer, or comparable local path hints
5. `Accept-Language` primary value with `de*` => `de`, otherwise `en`
6. fallback `en`

## Validation

- `Run auth phase tests` -> `45 passed`
- live browser validation performed on the landing page in `de` and `en` after the code changes
