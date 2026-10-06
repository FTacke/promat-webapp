"""Smoke-check the runtime assets of the built production image.

Run inside the image, for example (see ``.github/workflows/ci.yml``):

    docker run --rm -i -e PROMAT_RUNTIME_ROOT=/app -e PROMAT_PUBLIC_ROOT=/tmp/public \
        promat-ci-image python - < scripts/ci_image_smoke.py

It proves that content which the web app reads at runtime is packaged in the image and not only present in a
development checkout (the legal pages once read ``docs/plans/``, which the image does not contain), and that the
composed application inside the image serves the pages every deployment must have: the legal pages, the public
landing/teaching/research-design pages, no public draft topics, and a login redirect for protected research
pages. The same page list is checked against the live site after a deployment by ``scripts/post_deploy_smoke.py``.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import sys
import tempfile


# /app is the application root inside the image; the override lets tests exercise an image-shaped layout.
APP_ROOT = Path(os.environ.get("PROMAT_IMAGE_APP_ROOT", "/app"))
sys.path.insert(0, str(APP_ROOT / "src"))

# The HTTP smoke starts the real application factory against a throw-away SQLite file. These are read when the
# configuration module is imported, so they are set before any app import.
_SMOKE_DIR = Path(tempfile.mkdtemp(prefix="promat-image-smoke-"))
os.environ["AUTH_DATABASE_URL"] = f"sqlite:///{(_SMOKE_DIR / 'smoke.sqlite3').as_posix()}"
os.environ.setdefault("PROMAT_PUBLIC_BASE_URL", "https://promat.invalid")

from app.routes.public_content import LEGAL_PAGES, build_legal_page  # noqa: E402
from app.teaching_content import list_teaching_languages  # noqa: E402


# (path, expected status). Keep in step with scripts/post_deploy_smoke.py.
LEGAL_PATHS = ("/impressum", "/de/impressum", "/en/impressum", "/de/privacy", "/en/privacy")
PUBLIC_PATHS = ("/de", "/en", "/de/teaching", "/en/teaching", "/de/teaching/spanish/which-pronunciation", "/de/research/spanish/design", "/en/research/spanish/design")
PROTECTED_PATHS = ("/de/research/spanish/speakers", "/de/research/spanish/player/x/wordlist")


def _draft_topic_paths() -> list[str]:
    """Paths of topic editions whose own YAML says draft or not public; none of them may answer 200."""
    import yaml

    paths: list[str] = []
    for locale_file in sorted((APP_ROOT / "content" / "teaching").glob("*/*/??.yaml")):
        teaching_lang, topic_slug, locale_name = locale_file.relative_to(APP_ROOT / "content" / "teaching").parts
        if topic_slug == "hubs":
            continue
        topic = yaml.safe_load(locale_file.read_text(encoding="utf-8")) or {}
        hub = topic.get("hub") if isinstance(topic.get("hub"), dict) else {}
        if str(topic.get("status", "")).lower() == "draft" or str(hub.get("status", "")).lower() == "draft" or topic.get("is_public") is False:
            paths.append(f"/{locale_name.removesuffix('.yaml')}/teaching/{teaching_lang}/{topic_slug}")
    return paths


def _http_smoke(failures: list[str]) -> None:
    from sqlalchemy import create_engine

    from app import create_app
    from app.auth.models import Base

    engine = create_engine(os.environ["AUTH_DATABASE_URL"])
    Base.metadata.create_all(engine)
    engine.dispose()
    client = create_app("testing").test_client()

    for path in (*LEGAL_PATHS, *PUBLIC_PATHS):
        response = client.get(path)
        if response.status_code != 200:
            failures.append(f"GET {path} returned {response.status_code}, expected 200")
            continue
        title = re.search(r"<title>(.*?)</title>", response.get_data(as_text=True), flags=re.S)
        if title is None or not title.group(1).strip():
            failures.append(f"GET {path} has no server-rendered <title>")
    for path in _draft_topic_paths():
        if client.get(path).status_code == 200:
            failures.append(f"GET {path} is public (200) but the topic file marks it as a draft / not public")
    for path in PROTECTED_PATHS:
        response = client.get(path)
        if response.status_code != 302 or not response.headers.get("Location", "").startswith("/login"):
            failures.append(f"GET {path} should redirect to /login, got {response.status_code}")


def main() -> int:
    failures: list[str] = []
    for ui_lang in ("de", "en"):
        for page_key in LEGAL_PAGES:
            page = build_legal_page(ui_lang, page_key)
            body = "" if page is None else "".join(section["body_html"] for section in page["sections"])
            if not body.strip():
                failures.append(f"legal page {page_key!r} ({ui_lang}) rendered empty")
    if not list_teaching_languages():
        failures.append("no teaching languages found under content/teaching")
    try:
        _http_smoke(failures)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"HTTP smoke could not run: {type(exc).__name__}: {exc}")
    if (APP_ROOT / "docs").exists():
        failures.append("docs/ unexpectedly present in the image; runtime must not depend on it")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("image runtime assets OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
