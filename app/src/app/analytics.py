"""Privacy-safe aggregated analytics for public PROMAT content surfaces."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone

from flask import Flask, current_app, request
from sqlalchemy import select

from .auth.models import AnalyticsDaily, AnalyticsLanguageAreaDaily
from .extensions.sqlalchemy_ext import get_session

ANALYTICS_COOKIE_NAME = "pm_analytics_state"
ANALYTICS_COOKIE_DAYS = 45
TRACKED_ROOT_SECTIONS = {"project", "research", "teaching"}
TRACKED_MATRIX_SECTIONS = {"research", "teaching"}
TRACKED_UI_LANGS = {"de", "en"}
TRACKED_CORPORA = {"spanish", "french", "german", "english"}


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _today_utc() -> date:
    return _now_utc().date()


def _parse_cookie_state(raw: str | None) -> dict[str, dict[str, list[str]]]:
    if not raw:
        return {"days": {}}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"days": {}}
    days = parsed.get("days")
    if not isinstance(days, dict):
        return {"days": {}}
    normalized: dict[str, list[str]] = {}
    for key, value in days.items():
        if isinstance(key, str) and isinstance(value, list):
            normalized[key] = [str(item) for item in value]
    return {"days": normalized}


def _prune_cookie_state(state: dict[str, dict[str, list[str]]]) -> bool:
    changed = False
    cutoff = _today_utc() - timedelta(days=ANALYTICS_COOKIE_DAYS)
    valid_days: dict[str, list[str]] = {}
    for day_key, entries in state.get("days", {}).items():
        try:
            parsed_day = date.fromisoformat(day_key)
        except ValueError:
            changed = True
            continue
        if parsed_day < cutoff:
            changed = True
            continue
        valid_days[day_key] = entries
    if valid_days != state.get("days", {}):
        state["days"] = valid_days
        changed = True
    return changed


def _describe_request() -> dict[str, str] | None:
    if request.method != "GET":
        return None

    path = request.path or ""
    segments = [segment for segment in path.split("/") if segment]
    if len(segments) < 2:
        return None

    ui_lang, section = segments[0], segments[1]
    if ui_lang not in TRACKED_UI_LANGS or section not in TRACKED_ROOT_SECTIONS:
        return None

    descriptor: dict[str, str] = {"section": section}
    if section in TRACKED_MATRIX_SECTIONS and len(segments) >= 3:
        corpus_language = segments[2]
        if corpus_language in TRACKED_CORPORA:
            descriptor["corpus_language"] = corpus_language
    return descriptor


def _is_trackable_response() -> bool:
    if request.method != "GET":
        return False
    if request.endpoint == "static":
        return False
    if request.path.startswith("/admin") or request.path.startswith("/auth"):
        return False
    if request.path.startswith("/api/"):
        return False
    if request.path in {"/favicon.ico", "/robots.txt", "/health"}:
        return False
    if request.headers.get("HX-Request"):
        return False
    return True


def _bump_analytics_counters(descriptor: dict[str, str], unique_keys: set[str]) -> None:
    today = _today_utc()
    now = _now_utc()
    with get_session() as session:
        daily = session.execute(
            select(AnalyticsDaily).where(AnalyticsDaily.activity_date == today)
        ).scalars().first()
        if daily is None:
            daily = AnalyticsDaily(
                activity_date=today,
                unique_visitors=0,
                page_views=0,
                created_at=now,
                updated_at=now,
            )
            session.add(daily)
        daily.page_views += 1
        if "all" in unique_keys:
            daily.unique_visitors += 1
        daily.updated_at = now

        corpus_language = descriptor.get("corpus_language")
        section = descriptor.get("section")
        if section in TRACKED_MATRIX_SECTIONS and corpus_language:
            area = session.execute(
                select(AnalyticsLanguageAreaDaily).where(
                    AnalyticsLanguageAreaDaily.activity_date == today,
                    AnalyticsLanguageAreaDaily.section == section,
                    AnalyticsLanguageAreaDaily.corpus_language == corpus_language,
                )
            ).scalars().first()
            if area is None:
                area = AnalyticsLanguageAreaDaily(
                    activity_date=today,
                    section=section,
                    corpus_language=corpus_language,
                    unique_visitors=0,
                    page_views=0,
                    created_at=now,
                    updated_at=now,
                )
                session.add(area)
            area.page_views += 1
            if f"{section}:{corpus_language}" in unique_keys:
                area.unique_visitors += 1
            area.updated_at = now


def track_page_response(response):
    if not _is_trackable_response() or response.status_code >= 400:
        return response

    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        return response

    descriptor = _describe_request()
    if descriptor is None:
        return response

    state = _parse_cookie_state(request.cookies.get(ANALYTICS_COOKIE_NAME))
    state_changed = _prune_cookie_state(state)
    today_key = _today_utc().isoformat()
    seen_keys = set(state.setdefault("days", {}).get(today_key, []))
    new_unique_keys: set[str] = set()

    if "all" not in seen_keys:
        seen_keys.add("all")
        new_unique_keys.add("all")
        state_changed = True

    section = descriptor.get("section")
    corpus_language = descriptor.get("corpus_language")
    if section in TRACKED_MATRIX_SECTIONS and corpus_language:
        matrix_key = f"{section}:{corpus_language}"
        if matrix_key not in seen_keys:
            seen_keys.add(matrix_key)
            new_unique_keys.add(matrix_key)
            state_changed = True

    state["days"][today_key] = sorted(seen_keys)
    _bump_analytics_counters(descriptor, new_unique_keys)

    if state_changed:
        response.set_cookie(
            ANALYTICS_COOKIE_NAME,
            json.dumps(state, separators=(",", ":")),
            max_age=ANALYTICS_COOKIE_DAYS * 24 * 60 * 60,
            httponly=True,
            samesite="Lax",
            secure=bool(current_app.config.get("SESSION_COOKIE_SECURE", False)),
        )
    return response


def analytics_window_start(period: str) -> date | None:
    today = _today_utc()
    if period == "7d":
        return today - timedelta(days=6)
    if period == "30d":
        return today - timedelta(days=29)
    return None


def summarize_analytics(period: str) -> dict[str, object]:
    start_date = analytics_window_start(period)
    with get_session() as session:
        daily_stmt = select(AnalyticsDaily).order_by(AnalyticsDaily.activity_date.desc())
        area_stmt = select(AnalyticsLanguageAreaDaily).order_by(
            AnalyticsLanguageAreaDaily.corpus_language.asc(),
            AnalyticsLanguageAreaDaily.section.asc(),
            AnalyticsLanguageAreaDaily.activity_date.desc(),
        )
        if start_date is not None:
            daily_stmt = daily_stmt.where(AnalyticsDaily.activity_date >= start_date)
            area_stmt = area_stmt.where(AnalyticsLanguageAreaDaily.activity_date >= start_date)
        daily_rows = list(session.execute(daily_stmt).scalars().all())
        area_rows = list(session.execute(area_stmt).scalars().all())

    totals = {
        "unique_visitors": sum(row.unique_visitors for row in daily_rows),
        "page_views": sum(row.page_views for row in daily_rows),
        "days_with_activity": len(daily_rows),
    }

    matrix: dict[tuple[str, str], dict[str, int]] = {}
    for row in area_rows:
        key = (row.corpus_language, row.section)
        bucket = matrix.setdefault(key, {"unique_visitors": 0, "page_views": 0})
        bucket["unique_visitors"] += row.unique_visitors
        bucket["page_views"] += row.page_views

    trend_rows = [
        {
            "date": row.activity_date.isoformat(),
            "unique_visitors": row.unique_visitors,
            "page_views": row.page_views,
        }
        for row in sorted(daily_rows, key=lambda row: row.activity_date)
    ]

    return {
        "period": period,
        "start_date": start_date.isoformat() if start_date else None,
        "totals": totals,
        "matrix": matrix,
        "trend_rows": trend_rows,
    }


def register_analytics(app: Flask) -> None:
    @app.after_request
    def _record_page_analytics(response):
        return track_page_response(response)