"""Guards that the web app only depends on files the production image actually ships.

``app/Dockerfile`` copies ``app/`` to ``/app`` and ``content/`` to ``/app/content``. Development-only trees such as
``docs/`` are not part of the image, so runtime code must not read from them.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "ci_image_smoke.py"
DOCKERFILE = REPO_ROOT / "app" / "Dockerfile"


def _build_image_layout(destination: Path) -> Path:
    """Reproduce the Dockerfile's `COPY app/ ./` and `COPY content/ ./content/` without docs/ or repo files."""
    image_root = destination / "app"
    shutil.copytree(
        REPO_ROOT / "app",
        image_root,
        ignore=shutil.ignore_patterns("static", "tests", "__pycache__", "*.pyc", ".pytest_cache", ".ruff_cache"),
    )
    shutil.copytree(REPO_ROOT / "content", image_root / "content", ignore=shutil.ignore_patterns("teaching_import"))
    return image_root


def test_dockerfile_copies_app_and_content_but_not_docs() -> None:
    copied = re.findall(r"^COPY\s+(?:--\S+\s+)*(\S+)\s", DOCKERFILE.read_text(encoding="utf-8"), re.MULTILINE)

    assert "app/" in copied
    assert "content/" in copied
    assert not any(source.startswith("docs") for source in copied)


def test_runtime_assets_resolve_from_image_layout_without_docs(tmp_path: Path) -> None:
    image_root = _build_image_layout(tmp_path)
    assert not (image_root / "docs").exists()

    env = {key: value for key, value in os.environ.items() if not key.startswith("PROMAT_")}
    env.update(
        {
            "PROMAT_IMAGE_APP_ROOT": str(image_root),
            "PROMAT_RUNTIME_ROOT": str(image_root),
            "PROMAT_PUBLIC_ROOT": str(tmp_path / "public"),
            "FLASK_ENV": "production",
        }
    )
    result = subprocess.run(
        [sys.executable, str(SMOKE_SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
        cwd=image_root,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "image runtime assets OK" in result.stdout


def test_legal_pages_render_in_image_layout_with_distinct_german_and_english_text(tmp_path: Path) -> None:
    image_root = _build_image_layout(tmp_path)
    env = {key: value for key, value in os.environ.items() if not key.startswith("PROMAT_")}
    env.update(
        {
            "PROMAT_RUNTIME_ROOT": str(image_root),
            "PROMAT_PUBLIC_ROOT": str(tmp_path / "public"),
            "FLASK_ENV": "production",
            "PYTHONPATH": str(image_root / "src"),
        }
    )
    snippet = (
        "from app.routes.public_content import build_legal_page\n"
        "print(build_legal_page('de', 'impressum')['sections'][0]['body_html'])\n"
        "print('=====')\n"
        "print(build_legal_page('en', 'impressum')['sections'][0]['body_html'])\n"
    )
    result = subprocess.run([sys.executable, "-c", snippet], capture_output=True, text=True, env=env, cwd=image_root, check=False)

    assert result.returncode == 0, result.stdout + result.stderr
    german, english = result.stdout.split("=====")
    assert "Anbieter dieser Internetpräsenz" in german
    assert "Anbieter dieser Internetpräsenz" not in english
    assert english.strip()
