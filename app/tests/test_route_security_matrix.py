"""Route/security matrix over the composed application (``create_app("testing")``).

Every URL rule of the real app must be classified. Public routes form an explicit allowlist; every other route is
protected and has to turn an anonymous request away (login redirect or 401/403) before it renders or acts. A new
route that is in neither list fails the suite, so access is always a conscious decision (TI-17).
"""

from __future__ import annotations

import pytest

PUBLIC_ENDPOINTS = {
    "public.landing_page",
    "public.localized_landing_page",
    "public.access_request_thanks",
    "public.access_request_page",
    "public.access_request_submit",
    "public.impressum_page",
    "public.privacy_page",
    "public.project_home",
    "public.project_page",
    "public.research_home",
    "public.research_language_root",
    "public.teaching_home",
    "public.teaching_language_root",
    "public.teaching_language_page",
    "public.teaching_topic_media",
    "public.login",
    "public.health_check",
    "public.readiness_check",
    "auth.login",
    "auth.login_post",
    "auth.logout_any",
    "auth.password_forgot_page",
    "auth.password_forgot_submit",
    "auth.password_forgot_api",
    "auth.password_reset_page",
    "auth.password_reset_submit",
    "auth.password_reset_api",
    "auth.check_session",
    "static",
}

#: `research_language_page` is public for `design` only; every other page slug is gated (see below).
GATED_BY_PARAMETER = {"public.research_language_page"}

PROTECTED_ENDPOINTS = {
    "public.research_phenomena_preset_editor",
    "public.research_phenomena_set_editor",
    "public.research_player",
    "public.research_player_audio",
    "public.research_player_item_download",
    "public.research_speaker_profile",
    "auth.account_page",
    "auth.account_update",
    "auth.account_password_page",
    "auth.account_password_submit",
    "auth.change_password",
    "auth.account_page_legacy",
    "admin.dashboard",
    "admin.admins_list",
    "admin.analytics_page",
    "admin.groups_create",
    "admin.groups_update",
    "admin.groups_set_password",
    "admin.users_list",
    "admin.users_create",
    "admin.users_detail",
    "admin.users_update",
    "admin.users_prepare_invite",
    "admin.users_reset_password",
    "admin.users_send_invite",
    "admin.users_page",
    "research_api.create_admin_curated_set",
    "research_api.update_admin_curated_set",
    "research_api.delete_admin_curated_set",
    "research_api.archive_admin_curated_set",
    "research_api.reactivate_admin_curated_set",
    "research_api.create_admin_curated_set_from_custom",
    "research_api.create_set",
    "research_api.list_sets",
    "research_api.get_set",
    "research_api.patch_set",
    "research_api.delete_set",
    "research_api.put_set_items",
    "research_api.private_copy_set",
    "research_api.save_as_new_set",
    "research_api.put_set_sessions",
}

DUMMY_ARGUMENTS = {
    "ui_lang": "de",
    "language_slug": "spanish",
    "page_slug": "speakers",
    "preset_id": "preset-1",
    "set_id": "set-1",
    "session_id": "ES-L-0001-2026-S01",
    "task": "wordlist",
    "item_id": "wl_001",
    "person_id": "ES-L-0001",
    "user_id": "user-1",
}

ANONYMOUS_REFUSALS = {302, 303, 401, 403}


@pytest.fixture
def app(real_app_factory):
    return real_app_factory(env_name="testing")


def _rules(app):
    return [rule for rule in app.url_map.iter_rules()]


def _build(rule, values: dict[str, str]) -> str:
    adapter = rule.map.bind("localhost")
    return adapter.build(rule.endpoint, values, method=sorted(rule.methods - {"HEAD", "OPTIONS"})[0])


def test_every_route_is_classified_as_public_or_protected(app) -> None:
    classified = PUBLIC_ENDPOINTS | PROTECTED_ENDPOINTS | GATED_BY_PARAMETER
    unclassified = sorted({rule.endpoint for rule in _rules(app)} - classified)
    assert unclassified == [], f"classify these endpoints as public (allowlist) or protected: {unclassified}"
    stale = sorted(classified - {rule.endpoint for rule in _rules(app)})
    assert stale == [], f"remove endpoints that no longer exist from the matrix: {stale}"


def test_protected_routes_turn_anonymous_requests_away_for_every_method(app) -> None:
    client = app.test_client()
    failures: list[str] = []
    for rule in _rules(app):
        if rule.endpoint not in PROTECTED_ENDPOINTS:
            continue
        url = _build(rule, {name: DUMMY_ARGUMENTS.get(name, "x") for name in rule.arguments})
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            response = client.open(url, method=method, json={} if method != "GET" else None)
            if response.status_code not in ANONYMOUS_REFUSALS:
                failures.append(f"{method} {url} -> {response.status_code}")
    assert failures == []


@pytest.mark.parametrize("ui_lang", ["de", "en"])
@pytest.mark.parametrize("page_slug", ["speakers", "comparison", "player", "phenomena", "something-else"])
def test_research_pages_other_than_design_are_gated(app, ui_lang: str, page_slug: str) -> None:
    response = app.test_client().get(f"/{ui_lang}/research/spanish/{page_slug}")
    assert response.status_code in ANONYMOUS_REFUSALS or response.status_code == 404
    if response.status_code != 404:
        assert "/login" in response.headers.get("Location", "")


@pytest.mark.parametrize("ui_lang", ["de", "en"])
def test_design_page_is_the_only_public_research_page(app, ui_lang: str) -> None:
    assert app.test_client().get(f"/{ui_lang}/research/spanish/design").status_code == 200


def test_public_get_routes_do_not_require_login(app) -> None:
    client = app.test_client()
    for url in ("/", "/de", "/en", "/de/research", "/de/research/spanish", "/de/teaching", "/de/teaching/spanish", "/de/impressum", "/en/privacy", "/login", "/access-request", "/health"):
        response = client.get(url)
        assert response.status_code in (200, 301, 302, 308), (url, response.status_code)
        assert "/login" not in response.headers.get("Location", ""), url
        if url != "/":
            assert response.status_code == 200, url
