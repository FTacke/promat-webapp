# 2026-04-27 · Admin CSP YouTube and Drawer Icon · Run 147

## Scope

- Fixed the dev/runtime Content-Security-Policy so the existing project-page YouTube embed is no longer blocked by the global frame policy.
- Restored the shared section icon in the admin sidebar drawer header.
- Added focused regressions for the admin drawer icon and the CSP header allowance.

## Implementation

- Updated `app/src/app/__init__.py` so the global CSP now includes `frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com` alongside the existing restrictive defaults.
- Updated `app/src/app/protected_navigation.py` so the shared admin panel builder renders the normal section icon again instead of suppressing it.
- Updated `app/tests/test_auth_phase1.py` to assert the restored admin drawer icon and to cover the CSP header through an isolated `register_security_headers(...)` test.
- Kept the existing project-about rendering regression in `app/tests/test_research_sessions.py` focused on page content rather than the stripped public test fixture headers.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_auth_phase1.py -q -k "admin_users_page_uses_sidebar_only_for_admin_area_navigation or security_headers_allow_project_youtube_embed"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k project_about_page_embeds_video_and_hides_intro`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_auth_phase1.py -q`
- Live header check on `http://127.0.0.1:8000/de/project/about` confirmed the delivered CSP now contains `frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com;`.

## Notes

- No active spec file needed an update in this run because the project video embed and shared drawer icon were already accepted product behavior; this run repaired implementation drift rather than changing a current rule.
- The public `url_app` research-session fixture does not include the global security-header hook, so CSP coverage was added as an isolated hook test instead of being attached to that fixture-driven page test.
