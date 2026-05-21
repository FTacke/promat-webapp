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


def test_render_markdown_inline_renders_emphasis_code_and_links() -> None:
    rendered = teaching_content.render_markdown_inline("Der *seseo* nutzt `s` und [Link](https://example.test).")

    assert "<em>seseo</em>" in rendered
    assert "<code>s</code>" in rendered
    assert '<a href="https://example.test">Link</a>' in rendered
    assert "<p>" not in rendered


def test_render_markdown_block_renders_paragraphs_links_and_escapes_raw_html() -> None:
    rendered = teaching_content.render_markdown_block(
        "Erster Absatz mit [Link](https://example.test).\n\n- Punkt eins\n- Punkt zwei\n\n<script>alert(1)</script>"
    )

    assert "<p>Erster Absatz" in rendered
    assert "<ul>" in rendered
    assert '<a href="https://example.test">Link</a>' in rendered
    assert "<script>" not in rendered
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered


def test_build_teaching_topic_page_adds_inline_markdown_html_for_title_fields(
    teaching_app: Flask,
    tmp_path: Path,
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
        "title: 'Welche Aussprache mit *seseo*?'\nblocks:\n  - type: section_heading\n    title: '*Seseo* und *distinción*'\n  - type: audio_contrast\n    title: 'Mit und ohne Unterscheidung: *casa* vs. *caza*'\n    transcript: 'casa – caza'\n    examples:\n      - label: '*Distinción*'\n        audio: /teaching/spanish/audio/variation/distincion-casa-caza.mp3\n      - label: '*Seseo*'\n        audio: /teaching/spanish/audio/variation/seseo-casa-caza.mp3\n  - type: audio_examples\n    title: 'Noch ein Aussprachemerkmal: `ll` und `y`'\n    collapsible: true\n    examples:\n      - label: 'Beispiel'\n        audio: /teaching/spanish/audio/variation/seseo-casa-caza.mp3\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    assert page["content_header"]["title_html"] == "Welche Aussprache mit <em>seseo</em>?"
    section_heading = next(block for block in page["blocks"] if block["type"] == "section_heading")
    assert section_heading["title_html"] == "<em>Seseo</em> und <em>distinción</em>"
    assert "<p>" not in section_heading["title_html"]
    audio_contrast = next(block for block in page["blocks"] if block["type"] == "audio_contrast")
    assert audio_contrast["title_html"] == "Mit und ohne Unterscheidung: <em>casa</em> vs. <em>caza</em>"
    assert "<p>" not in audio_contrast["title_html"]
    audio_examples = next(block for block in page["blocks"] if block["type"] == "audio_examples")
    assert audio_examples["title_html"] == "Noch ein Aussprachemerkmal: <code>ll</code> und <code>y</code>"
    assert "<p>" not in audio_examples["title_html"]


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


def test_build_teaching_topic_page_applies_layout_span_defaults_and_fallbacks(teaching_app: Flask, tmp_path: Path) -> None:
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
        "title: Thema eins\nblocks:\n  - type: hero\n    lead: Leitgedanke\n  - type: text\n    layout:\n      span: 1\n    body: Testabsatz\n  - type: rich_text\n    layout:\n      span: 9\n    body: '**Test**'\n  - type: warning_box\n    body: Hinweis\n  - type: download\n    layout:\n      span: '3'\n    href: /teaching/spanish/downloads/test.txt\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    assert page["intro"] == "Leitgedanke"
    assert [(block["type"], block["layout"]["span"]) for block in page["blocks"]] == [
        ("text", 1),
        ("rich_text", 2),
        ("admonition", 1),
        ("download", 2),
    ]


def test_build_teaching_topic_page_groups_blocks_into_sections(teaching_app: Flask, tmp_path: Path) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: Spanisch\ntopics:\n  - slug: topic-one\n    title: Thema eins\n  - slug: topic-two\n    title: Thema zwei\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-two.yaml",
        "title: Thema zwei\nblocks: []\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\ndescription: Kurze Einleitung\nblocks:\n  - type: text\n    body: Introtext\n  - type: info_box\n    title: Einstieg\n    body: Erste Info\n  - type: section_heading\n    title: Abschnitt eins\n  - type: text\n    layout:\n      span: 1\n    body: Erster Abschnittstext\n  - type: embed\n    layout:\n      span: 1\n    provider: datawrapper\n    src: https://datawrapper.dwcdn.net/Uza2n/1/\n  - type: next_topics\n    title: Weiter im Hub\n    topics:\n      - topic-two\ncitation:\n  text: 'Beispielzitat.'\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    assert [section["kind"] for section in page["topic_sections"]] == ["intro", "section", "next_topics", "citation"]
    assert [block["type"] for block in page["topic_sections"][0]["blocks"]] == ["text", "admonition"]
    assert page["topic_sections"][1]["heading"]["title"] == "Abschnitt eins"
    assert [block["layout"]["span"] for block in page["topic_sections"][1]["blocks"]] == [1, 1]
    assert page["topic_sections"][2]["blocks"][0]["type"] == "next_topics"
    assert page["topic_sections"][3]["blocks"][0]["type"] == "citation"


def test_build_teaching_topic_page_derives_metadata_and_appends_top_level_citation(teaching_app: Flask, tmp_path: Path) -> None:
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
        "title: Thema eins\ndescription: Kurzbeschreibung\npeer_review:\n  - Gloria Gabriel\ncreated: 2025-07-06\nupdated: 2026-03-05\ncredits:\n  authors:\n    - name: Marlon Merte\n    - name: Felix Tacke\ncitation:\n  text: 'Merte, Marlon / Tacke, Felix (2026): Thema eins.'\n  url: https://example.test/topic-one\nblocks:\n  - type: text\n    body: Testabsatz\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    assert page["intro"] == "Kurzbeschreibung"
    assert page["topic_metadata"] == {
        "authors": {
            "key": "authors",
            "label": "Autor:innen",
            "value": "Marlon Merte, Felix Tacke",
        },
        "details": [
            {"key": "peer_review", "label": "Peer Review", "value": "Gloria Gabriel"},
            {"key": "created", "label": "Erstellt", "value": "06.07.2025"},
            {"key": "updated", "label": "Geändert", "value": "05.03.2026"},
        ],
    }
    assert page["blocks"][-1]["type"] == "citation"
    assert page["blocks"][-1]["layout"]["span"] == 2
    assert page["blocks"][-1]["citation"] == {
        "title": "Diese Themenseite zitieren",
        "title_html": "Diese Themenseite zitieren",
        "text": "Merte, Marlon / Tacke, Felix (2026): Thema eins.",
        "doi": "",
        "url": "https://example.test/topic-one",
        "copy_text": "Merte, Marlon / Tacke, Felix (2026): Thema eins.\nhttps://example.test/topic-one",
        "body_html_blocks": [
            "<p>Merte, Marlon / Tacke, Felix (2026): Thema eins.</p>",
            '<dl class="pm-teaching-citation__meta"><div class="pm-teaching-citation__meta-item"><dt class="pm-teaching-citation__label">URL</dt><dd class="pm-teaching-citation__value"><a href="https://example.test/topic-one" class="pm-teaching-inline-link">https://example.test/topic-one</a></dd></div></dl>',
        ],
    }


def test_build_teaching_topic_page_moves_metadata_into_explicit_topic_meta_block_and_preserves_inline_code(
    teaching_app: Flask,
    tmp_path: Path,
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
        "title: Thema eins\ndescription: Kurzbeschreibung\nmetadata:\n  authors:\n    - Marlon Merte\n  created: 2025-07-06\nblocks:\n  - type: topic_meta\n  - type: text\n    body: |\n      Wer `caza` wie `casa` ausspricht, spricht nicht schlechteres Spanisch.\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    assert page["topic_metadata"] == {
        "authors": {
            "key": "authors",
            "label": "Autor:innen",
            "value": "Marlon Merte",
        },
        "details": [
            {"key": "created", "label": "Erstellt", "value": "06.07.2025"},
        ],
    }
    assert all(block["type"] != "topic_meta" for block in page["blocks"])
    assert page["blocks"][0]["type"] == "text"
    assert "<code>caza</code>" in page["blocks"][0]["body_html_blocks"][0]
    assert "<code>casa</code>" in page["blocks"][0]["body_html_blocks"][0]


def test_build_teaching_topic_page_handles_audio_examples_and_contrast_transcript_inheritance(
    teaching_app: Flask,
    tmp_path: Path,
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
        "title: Thema eins\nblocks:\n  - type: audio_examples\n    title: Beispiele\n    collapsible: true\n    default_open: false\n    source:\n      label: CO.RA.PAN\n      url: https://corapan.hispanistica.com\n    examples:\n      - label: Mexiko\n        transcript: hola con `c`\n        note: seseo mit `z/c`\n        token_id: MX1\n      - label: Chile\n        transcript: cerca\n  - type: audio_contrast\n    title: Kontrast\n    transcript: casa - caza\n    examples:\n      - label: Distincion\n        note: unterschiedlich\n      - label: Seseo\n        transcript: casa = caza\n        note: gleich\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    examples_block = page["blocks"][0]
    contrast_block = page["blocks"][1]
    assert examples_block["type"] == "audio_examples"
    assert len(examples_block["examples"]) == 2
    assert examples_block["collapsible"] is True
    assert examples_block["default_open"] is False
    assert examples_block["source"]["label"] == "CO.RA.PAN"
    assert examples_block["source"]["url"] == "https://corapan.hispanistica.com"
    assert examples_block["examples"][0]["token_id"] == "MX1"
    assert examples_block["examples"][0]["speaker_id"] == ""
    assert "<code>c</code>" in examples_block["examples"][0]["transcript_html"]
    assert "<code>z/c</code>" in examples_block["examples"][0]["note_html"]
    assert contrast_block["type"] == "audio_contrast"
    assert contrast_block["examples"][0]["transcript"] == "casa - caza"
    assert contrast_block["examples"][1]["transcript"] == "casa = caza"
    assert contrast_block["examples"][0]["note"] == "unterschiedlich"


def test_build_teaching_topic_page_keeps_public_audio_contrast_urls_and_availability(
    teaching_app: Flask,
    tmp_path: Path,
) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: Spanisch\ntopics:\n  - slug: topic-one\n    title: Thema eins\n",
    )
    public_audio_dir = tmp_path / "public" / "teaching" / "spanish" / "audio" / "variation"
    public_audio_dir.mkdir(parents=True, exist_ok=True)
    (public_audio_dir / "distincion-casa-caza.mp3").write_bytes(b"test-distincion")
    (public_audio_dir / "seseo-casa-caza.mp3").write_bytes(b"test-seseo")
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\nblocks:\n  - type: audio_contrast\n    title: Kontrast\n    transcript: casa - caza\n    examples:\n      - label: Distincion\n        audio: /teaching/spanish/audio/variation/distincion-casa-caza.mp3\n        note: unterschiedlich\n      - label: Seseo\n        audio: /teaching/spanish/audio/variation/seseo-casa-caza.mp3\n        note: gleich\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    contrast_block = page["blocks"][0]
    assert contrast_block["type"] == "audio_contrast"
    assert contrast_block["layout"]["span"] == 2
    assert len(contrast_block["examples"]) == 2
    assert contrast_block["examples"][0]["audio"] == "/teaching/spanish/audio/variation/distincion-casa-caza.mp3"
    assert contrast_block["examples"][1]["audio"] == "/teaching/spanish/audio/variation/seseo-casa-caza.mp3"
    assert contrast_block["examples"][0]["is_available"] is True
    assert contrast_block["examples"][1]["is_available"] is True
    assert contrast_block["examples"][0]["transcript"] == "casa - caza"


def test_build_teaching_topic_page_keeps_public_audio_examples_source_token_ids_and_audio(
    teaching_app: Flask,
    tmp_path: Path,
) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: Spanisch\ntopics:\n  - slug: topic-one\n    title: Thema eins\n",
    )
    public_audio_dir = tmp_path / "public" / "teaching" / "spanish" / "audio" / "corapan"
    public_audio_dir.mkdir(parents=True, exist_ok=True)
    (public_audio_dir / "MEXb80def27c.mp3").write_bytes(b"mex")
    (public_audio_dir / "CHL8b78ac16b.mp3").write_bytes(b"chl")
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\nblocks:\n  - type: audio_examples\n    title: Seseo in authentischen Ausschnitten\n    lead: \"Achten Sie auf `z/c`.\"\n    source:\n      label: CO.RA.PAN\n      url: https://corapan.hispanistica.com\n    examples:\n      - label: Mexiko\n        transcript: \"cerca con `c`\"\n        note: \"`c` klingt wie `s`.\"\n        token_id: MEXb80def27c\n        audio: /teaching/spanish/audio/corapan/MEXb80def27c.mp3\n      - label: Chile\n        transcript: más cerca\n        token_id: CHL8b78ac16b\n        audio: /teaching/spanish/audio/corapan/CHL8b78ac16b.mp3\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    examples_block = page["blocks"][0]
    assert examples_block["type"] == "audio_examples"
    assert examples_block["layout"]["span"] == 2
    assert examples_block["source"]["label"] == "CO.RA.PAN"
    assert examples_block["source"]["url"] == "https://corapan.hispanistica.com"
    assert len(examples_block["examples"]) == 2
    assert examples_block["examples"][0]["audio"] == "/teaching/spanish/audio/corapan/MEXb80def27c.mp3"
    assert examples_block["examples"][0]["is_available"] is True
    assert examples_block["examples"][0]["token_id"] == "MEXb80def27c"
    assert "<code>c</code>" in examples_block["examples"][0]["transcript_html"]
    assert "<code>c</code>" in examples_block["examples"][0]["note_html"]


def test_build_teaching_topic_page_handles_datawrapper_embeds_and_skips_invalid_ones(
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
        "title: Thema eins\nblocks:\n  - type: embed\n    title: Karte\n    provider: datawrapper\n    src: https://datawrapper.dwcdn.net/Uza2n/1/\n    height: 831\n    caption: Kartenbild\n  - type: embed\n    title: Ohne Quelle\n    provider: datawrapper\n  - type: embed\n    title: Unbekannt\n    provider: generic\n    src: https://example.test/embed\n  - type: text\n    body: Wer `caza` wie `casa` ausspricht, sieht keine rohen <script>-Tags aus YAML.\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    assert [block["type"] for block in page["blocks"]] == ["embed", "text"]
    embed_block = page["blocks"][0]
    assert embed_block["provider"] == "datawrapper"
    assert embed_block["src"] == "https://datawrapper.dwcdn.net/Uza2n/1/"
    assert embed_block["height"] == 831
    assert embed_block["caption"] == "Kartenbild"
    assert "unsupported teaching embed provider 'generic'" in caplog.text
    assert "<script>" not in page["blocks"][1]["body_html_blocks"][0]


def test_build_teaching_topic_page_applies_default_embed_height(teaching_app: Flask, tmp_path: Path) -> None:
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
        "title: Thema eins\nblocks:\n  - type: embed\n    title: Karte\n    provider: datawrapper\n    src: https://datawrapper.dwcdn.net/poSnB/7/\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    assert page["blocks"][0]["type"] == "embed"
    assert page["blocks"][0]["height"] == 540


def test_build_teaching_topic_page_keeps_only_valid_further_reading_links(teaching_app: Flask, tmp_path: Path) -> None:
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
        "title: Thema eins\nblocks:\n  - type: further_reading\n    title: Weiterlesen\n    collapsible: true\n    default_open: false\n    body: |\n      Mehr Hintergründe in den Lehrbuchkapiteln.\n    links:\n      - label: Gültig\n        href: '#'\n      - label: Ohne Ziel\n      - href: '#'\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    reading_block = page["blocks"][0]
    assert reading_block["type"] == "further_reading"
    assert reading_block["collapsible"] is True
    assert reading_block["default_open"] is False
    assert reading_block["links"] == [{"label": "Gültig", "label_html": "Gültig", "href": "#"}]


def test_build_teaching_topic_page_prioritizes_top_level_citation_and_uses_copy_text(
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
        "title: Thema eins\ncitation:\n  title: Diese Seite *zitieren*\n  text: 'Tacke: *Pronunciation Matters*. Online: [pronunciation-matters.de](https://www.pronunciation-matters.de)'\n  copy_text: 'Tacke: Pronunciation Matters. Online: https://www.pronunciation-matters.de'\nblocks:\n  - type: text\n    body: Intro\n  - type: citation\n    title: Alte Zitation\n    text: Veraltete Zitation\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    citations = [block for block in page["blocks"] if block["type"] == "citation"]
    assert len(citations) == 1
    citation = citations[0]["citation"]
    assert citation["title"] == "Diese Seite *zitieren*"
    assert citation["title_html"] == "Diese Seite <em>zitieren</em>"
    assert citation["copy_text"] == "Tacke: Pronunciation Matters. Online: https://www.pronunciation-matters.de"
    assert '<a href="https://www.pronunciation-matters.de">pronunciation-matters.de</a>' in citation["body_html_blocks"][0]
    assert "Ignoring explicit teaching citation block" in caplog.text


def test_build_teaching_topic_page_falls_back_to_plain_text_copy_for_citation_text(
    teaching_app: Flask,
    tmp_path: Path,
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
        "title: Thema eins\ncitation:\n  text: >-\n    Tacke: *Pronunciation Matters*.\n    Online: [pronunciation-matters.de](https://www.pronunciation-matters.de)\nblocks:\n  - type: text\n    body: Intro\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    citation = page["blocks"][-1]["citation"]
    assert citation["copy_text"] == "Tacke: Pronunciation Matters. Online: pronunciation-matters.de"


def test_build_teaching_topic_page_exposes_markdown_ready_header_fields(teaching_app: Flask, tmp_path: Path) -> None:
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
        "title: 'Thema mit *seseo*'\ndescription: 'Intro mit `z/c` und [Link](https://example.test)'\nblocks:\n  - type: text\n    body: Introabsatz\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_topic_page("de", "spanish", "topic-one")

    assert page is not None
    assert page["page_title"] == "Thema mit seseo"
    assert page["content_header"]["title_html"] == "Thema mit <em>seseo</em>"
    assert "<code>z/c</code>" in page["content_header"]["intro_html"]
    assert '<a href="https://example.test">Link</a>' in page["content_header"]["intro_html"]


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


def test_build_teaching_hub_page_groups_topics_and_sets_back_link(teaching_app: Flask, tmp_path: Path) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: \"Spanisch: Aussprache unterrichten\"\noverview_intro: Zwischen Hero und Karten\ngroups:\n  - title: Grundlagen\n    description: Kurze Einordnung\n    topics:\n      - topic-one\n  - title: Leer\n    topics:\n      - missing-topic\ntopics:\n  - slug: topic-one\n    title: Thema eins\n    category: Grundlagen\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\nblocks: []\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_hub_page("de", "spanish")

    assert page is not None
    assert page["back_link"]["label"] == "Sprachauswahl"
    assert page["content_header"]["back_link"] == {
        "label": "Sprachauswahl",
        "href": "/de/teaching",
    }
    assert page["overview_intro"] == "Zwischen Hero und Karten"
    assert [group["title"] for group in page["topic_groups"]] == ["Grundlagen"]
    assert page["topic_groups"][0]["description"] == "Kurze Einordnung"
    assert [card["slug"] for card in page["topic_groups"][0]["cards"]] == ["topic-one"]
    assert page["empty_state"] is None


def test_build_teaching_hub_page_keeps_listed_missing_topics_as_unavailable_cards(teaching_app: Flask, tmp_path: Path) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: \"Spanisch: Aussprache unterrichten\"\ngroups:\n  - title: Grundlagen\n    topics:\n      - topic-one\n      - topic-two\ntopics:\n  - slug: topic-one\n    title: Thema eins\n    level: Einstieg\n    category: Grundlagen\n  - slug: topic-two\n    title: Thema zwei\n    summary: Noch nicht fertig\n    level: Aufbau\n    category: Grundlagen\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\nblocks: []\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_hub_page("de", "spanish")

    assert page is not None
    cards = page["topic_groups"][0]["cards"]
    assert [card["slug"] for card in cards] == ["topic-one", "topic-two"]
    assert cards[0]["is_available"] is True
    assert cards[1]["is_available"] is False
    assert cards[1]["href"] == ""


def test_build_teaching_hub_page_keeps_explicitly_unavailable_topics_pending_even_when_file_exists(
    teaching_app: Flask,
    tmp_path: Path,
) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "teaching.yaml",
        "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "index.yaml",
        "title: \"Spanisch: Aussprache unterrichten\"\ngroups:\n  - title: Grundlagen\n    topics:\n      - topic-one\n      - topic-two\ntopics:\n  - slug: topic-one\n    title: Thema eins\n    is_available: true\n  - slug: topic-two\n    title: Thema zwei\n    is_available: false\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-one.yaml",
        "title: Thema eins\nblocks: []\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "spanish" / "de" / "topics" / "topic-two.yaml",
        "title: Thema zwei\nblocks: []\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_hub_page("de", "spanish")

    assert page is not None
    cards = page["topic_groups"][0]["cards"]
    assert [card["slug"] for card in cards] == ["topic-one", "topic-two"]
    assert cards[0]["is_available"] is True
    assert cards[1]["is_available"] is False
    assert cards[1]["href"] == ""


def test_build_teaching_hub_page_returns_empty_state_for_empty_languages(teaching_app: Flask, tmp_path: Path) -> None:
    _write_text(
        tmp_path / "content" / "teaching" / "english" / "teaching.yaml",
        "teaching_lang: english\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n",
    )
    _write_text(
        tmp_path / "content" / "teaching" / "english" / "de" / "index.yaml",
        "title: Englisch unterrichten\ngroups: []\ntopics: []\n",
    )

    with teaching_app.test_request_context():
        page = teaching_content.build_teaching_hub_page("de", "english")

    assert page is not None
    assert page["topic_groups"] == []
    assert page["empty_state"] == {
        "title": "Themenseiten im Aufbau",
        "text": "Für diese Sprache sind noch keine öffentlichen Themenseiten hinterlegt.",
    }


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
