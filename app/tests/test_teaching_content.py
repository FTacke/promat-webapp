from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from flask import Flask


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

from app import register_context_processors
from app.routes.public import blueprint as public_blueprint
from app import teaching_content


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def teaching_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Flask:
    runtime_root = tmp_path
    public_root = runtime_root / "public"
    public_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(runtime_root))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(public_root))
    monkeypatch.setattr(teaching_content, "TEACHING_CONTENT_ROOT", runtime_root / "content" / "teaching")
    teaching_content.clear_teaching_content_caches()

    app_root = Path(__file__).resolve().parents[1]
    app = Flask(
        __name__,
        template_folder=str(app_root / "templates"),
        static_folder=str(app_root / "static"),
    )
    app.config["SERVER_NAME"] = "promat.test"
    register_context_processors(app)
    app.register_blueprint(public_blueprint)
    yield app
    teaching_content.clear_teaching_content_caches()


def test_build_teaching_topic_page_keeps_image_block_without_alt(
    teaching_app: Flask,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: Spanisch\ntopics:\n  - slug: topic-one\n    title: Thema eins\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\nblocks:\n  - type: image\n    src: /teaching/spanish/images/example.png\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    image_block = next(block for block in page["blocks"] if block["type"] == "image")
    assert image_block["alt"] == ""
    assert "missing alt text" in caplog.text


def test_build_teaching_topic_page_skips_empty_credits_groups(teaching_app: Flask, tmp_path: Path) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: Spanisch\ntopics:\n  - slug: topic-one\n    title: Thema eins\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\ncredits:\n  authors:\n    - role: Ohne Namen\nblocks:\n  - type: credits\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    assert all(block["type"] != "credits" for block in page["blocks"])


def test_build_teaching_topic_page_keeps_only_existing_next_topics(teaching_app: Flask, tmp_path: Path) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: Spanisch\ntopics:\n  - slug: topic-one\n    title: Thema eins\n  - slug: topic-two\n    title: Thema zwei\n  - slug: topic-missing\n    title: Thema fehlt\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\nblocks:\n  - type: next_topics\n    topics:\n      - topic-two\n      - topic-missing\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-two.yaml",
        "title: Thema zwei\nblocks: []\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    next_topics = next(block for block in page["blocks"] if block["type"] == "next_topics")
    assert [card["slug"] for card in next_topics["cards"]] == ["topic-two"]


def test_build_teaching_topic_page_ignores_unknown_block_types(
    teaching_app: Flask,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: Spanisch\ntopics:\n  - slug: topic-one\n    title: Thema eins\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\nblocks:\n  - type: strange_box\n  - type: text\n    body: Testabsatz\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    assert [block["type"] for block in page["blocks"]] == ["text"]
    assert "Ignoring unknown teaching block type 'strange_box'" in caplog.text


def test_build_teaching_hub_page_marks_missing_target_edition_as_disabled(teaching_app: Flask, tmp_path: Path) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: Spanisch\ntopics:\n  - slug: topic-one\n    title: Thema eins\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\nblocks: []\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_hub_page("en", "spanish")

    assert page is not None
    assert page["resolved_ui_lang"] == "de"
    switch_items = {item["ui_lang"]: item for item in page["teaching_switch_items"]}
    assert switch_items["de"]["is_current"] is True
    assert switch_items["en"]["is_disabled"] is True
    assert switch_items["en"]["href"] is None


def test_resolve_teaching_switch_path_falls_back_to_hub_when_target_topic_is_missing(teaching_app: Flask, tmp_path: Path) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n  - en\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: Spanisch\ntopics:\n  - slug: topic-one\n    title: Thema eins\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\nblocks: []\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "en" / "index.yaml",
        "title: Spanish\ntopics:\n  - slug: topic-two\n    title: Topic two\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "en" / "topics" / "topic-two.yaml",
        "title: Topic two\nblocks: []\n",
    )

    assert teaching_content.resolve_teaching_switch_path("/de/teaching/spanish/topic-one", "en") == "/en/teaching/spanish"
    assert teaching_content.resolve_teaching_switch_path("/de/teaching/spanish/topic-one", "fr") is None


def test_discover_default_teaching_content_root_prefers_nearest_existing_content_tree(tmp_path: Path) -> None:
    local_module_path = tmp_path / "repo" / "app" / "src" / "app" / "teaching_content.py"
    local_module_path.parent.mkdir(parents=True, exist_ok=True)
    local_module_path.write_text("# test\n", encoding="utf-8")
    local_content_root = tmp_path / "repo" / "content" / "teaching"
    local_content_root.mkdir(parents=True, exist_ok=True)

    container_module_path = tmp_path / "image" / "app" / "src" / "app" / "teaching_content.py"
    container_module_path.parent.mkdir(parents=True, exist_ok=True)
    container_module_path.write_text("# test\n", encoding="utf-8")
    container_content_root = tmp_path / "image" / "app" / "content" / "teaching"
    container_content_root.mkdir(parents=True, exist_ok=True)

    assert teaching_content._discover_default_teaching_content_root(local_module_path) == local_content_root
    assert teaching_content._discover_default_teaching_content_root(container_module_path) == container_content_root
