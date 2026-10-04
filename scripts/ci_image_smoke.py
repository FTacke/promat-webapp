"""Smoke-check the runtime assets of the built production image.

Run inside the image, for example (see ``.github/workflows/ci.yml``):

    docker run --rm -i -e PROMAT_RUNTIME_ROOT=/app -e PROMAT_PUBLIC_ROOT=/tmp/public \
        promat-ci-image python - < scripts/ci_image_smoke.py

It proves that content which the web app reads at runtime is packaged in the image and not only present in a
development checkout (the legal pages once read ``docs/plans/``, which the image does not contain).
"""

from __future__ import annotations

import os
from pathlib import Path
import sys


# /app is the application root inside the image; the override lets tests exercise an image-shaped layout.
APP_ROOT = Path(os.environ.get("PROMAT_IMAGE_APP_ROOT", "/app"))
sys.path.insert(0, str(APP_ROOT / "src"))

from app.routes.public_content import LEGAL_PAGES, build_legal_page  # noqa: E402
from app.teaching_content import list_teaching_languages  # noqa: E402


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
