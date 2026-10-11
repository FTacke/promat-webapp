"""The six Spanish phenomenon topic pages: routes, structure, citations, bilingual parity and the audio slot registry."""

from __future__ import annotations

import html as html_module
import os
from pathlib import Path
import re
import sys

from flask import Flask, g
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app" / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app import register_context_processors  # noqa: E402
from app.routes.auth import blueprint as auth_blueprint  # noqa: E402
from app.routes.public import blueprint as public_blueprint  # noqa: E402
import teaching_audio_slots as slots  # noqa: E402

TOPICS = {
    "soft-spanish-hard-german": {"de": "Weiches Spanisch, hartes Deutsch", "en": "Soft Spanish, hard German"},
    "r": {"de": "Das spanische r", "en": "The Spanish r"},
    "r-am-silbenende": {"de": "R am Silbenende", "en": "Syllable-final r"},
    "b-or-v": {"de": "B oder V? Im Spanischen klingt beides gleich!", "en": "B or V? In Spanish, they sound the same!"},
    "soft-consonants-b-d-g": {"de": "Weiche Konsonanten: b, d und g", "en": "Soft consonants: b, d and g"},
    "accent-changes-everything": {"de": "Ein Akzent verändert alles", "en": "An accent changes everything"},
}
TOPIC_DIR = REPO_ROOT / "content" / "teaching" / "spanish"
PAIRS = [(slug, lang) for slug in TOPICS for lang in ("de", "en")]


@pytest.fixture(scope="module")
def client():
    app_root = REPO_ROOT / "app"
    app = Flask("topics", template_folder=str(app_root / "templates"), static_folder=str(app_root / "static"))
    app.config["SERVER_NAME"] = "promat.test"
    register_context_processors(app)

    @app.before_request
    def _anonymous() -> None:
        g.user = None
        g.user_id = None
        g.role = None

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(public_blueprint)
    return app.test_client()


def _html(client, lang: str, slug: str) -> str:
    response = client.get(f"/{lang}/teaching/spanish/{slug}")
    assert response.status_code == 200, (lang, slug)
    return response.get_data(as_text=True)


def _blocks(slug: str, lang: str) -> list[dict]:
    return yaml.safe_load((TOPIC_DIR / slug / f"{lang}.yaml").read_text(encoding="utf-8"))["blocks"]


@pytest.mark.parametrize(("slug", "lang"), PAIRS)
def test_topic_page_renders_with_title_citation_and_sections(client, slug: str, lang: str) -> None:
    html = _html(client, lang, slug)
    title = TOPICS[slug][lang]

    page_title = html_module.unescape(re.search(r"<title>(.*?)</title>", html, re.S).group(1))
    assert page_title.startswith(title)
    assert html.count("<h1") == 1
    url = f"https://pronunciation-matters.de/{lang}/teaching/spanish/{slug}"
    assert f'<a href="{url}">{url}</a>' in html  # generated citation names the page's own canonical URL
    assert html.count("pm-admonition--citation") == 1
    assert "Beschreibung folgt" not in html and "Hier kann später" not in html and "noch ausgearbeitet" not in html
    # didactic skeleton: listen, solution, explanation, corpus comparisons, classroom task, further reading
    assert html.count('class="pm-teaching-solution"') == (3 if slug == "soft-spanish-hard-german" else 1)
    assert html.count("pm-teaching-block--audio-contrast") >= 3
    assert "pm-teaching-block--teaching-impulses" not in html  # the classroom task is one tip box
    assert "pm-admonition--tip" in html
    assert "pm-teaching-further-reading" in html
    assert 'class="pm-teaching-audio-contrast__example' in html
    assert "is-unavailable" not in html and "audio-card-status" not in html


@pytest.mark.parametrize("slug", sorted(TOPICS))
def test_editions_are_structurally_identical_and_linked(client, slug: str) -> None:
    de, en = _blocks(slug, "de"), _blocks(slug, "en")
    assert [b["type"] for b in de] == [b["type"] for b in en]
    def audio(blocks: list[dict]) -> list[str]:
        return [ex["audio"] for b in blocks if b["type"] == "audio_contrast" for ex in b["examples"]]

    assert audio(de) == audio(en)
    assert [b.get("examples") and len(b["examples"]) for b in de] == [b.get("examples") and len(b["examples"]) for b in en]
    # the language switch leads to the equivalent edition of the same topic
    assert f'href="/en/teaching/spanish/{slug}' in _html(client, "de", slug)
    assert f'href="/de/teaching/spanish/{slug}' in _html(client, "en", slug)


@pytest.mark.parametrize(("slug", "lang"), PAIRS)
def test_every_recording_of_a_page_is_public_audio(client, slug: str, lang: str) -> None:
    html = _html(client, lang, slug)
    sources = sorted(set(re.findall(r'<source src="([^"]+)" type="audio/mpeg">', html)))
    expected = {ex["audio"] for b in _blocks(slug, lang) if b["type"] == "audio_contrast" for ex in b["examples"]}
    assert len(sources) == len(expected) >= (6 if slug == "soft-spanish-hard-german" else 8)
    for source in sources:
        assert source.startswith((f"/teaching-media/spanish/{slug}/audio/corpus/", f"/teaching-media/spanish/{slug}/audio/marele/"))
        response = client.get(source)
        assert response.status_code == 200 and response.mimetype == "audio/mpeg" and response.content_length > 5000


@pytest.mark.parametrize("slug", sorted(TOPICS))
def test_internal_links_of_further_reading_resolve(client, slug: str) -> None:
    for lang in ("de", "en"):
        for block in _blocks(slug, lang):
            for item in block.get("items", []) if block["type"] == "further_reading" else []:
                if item["href"].startswith("/"):
                    assert item["href"].startswith(f"/{lang}/teaching/spanish/")
                    assert client.get(item["href"]).status_code == 200
                else:
                    assert item["href"].startswith("https://linguistik.hispanistica.com/")


def test_listening_comparisons_name_speaker_category_and_item(client) -> None:
    html = _html(client, "de", "soft-spanish-hard-german")
    assert "Muttersprachliche Referenz" in html and "Lernende:r" in html
    assert "Pronunciation Matters · D27" in html and "Pronunciation Matters · D24" in html
    assert "Mexiko" not in html and "(B1)" not in html  # no fixed speaker identities: the recordings stay replaceable
    html = _html(client, "en", "r")
    assert "Native-speaker reference" in html and "Learner (B1)" in html and "Spain · W88" in html and "L1 German · W88" in html
    assert html.count('<details class="pm-teaching-solution">') == 1  # closed by default: no autoplay, no revealed solution


@pytest.mark.parametrize("lang", ["de", "en"])
def test_soft_spanish_page_has_the_three_comparisons_in_order_with_marele_first(client, lang: str) -> None:
    html = _html(client, lang, "soft-spanish-hard-german")
    # o hay (MAR.ELE) first, then tiene hambre (D27), then sus amigos (D24)
    positions = [html.index(f"audio/{name}") for name in ("marele/o-hay-ref", "marele/o-hay-learner", "corpus/p1-hambre-ref", "corpus/p1-hambre-learner", "corpus/p1-amigos-ref", "corpus/p1-amigos-learner")]
    assert positions == sorted(positions)
    assert "hispanistica.com/projects/marele" not in html  # origin is named as plain text, not linked (MAR.ELE site is being retired)
    assert html.count("pm-teaching-audio-contrast__example-subtitle\">MAR.ELE<") == 2
    assert "MAR.ELE" not in html.split("pm-teaching-block")[0]  # neither the meta description nor the page subtitle names it
    # the reference recording is announced first in every comparison, the learner recording second
    labels = re.findall(r'pm-teaching-audio-contrast__example-title">([^<]+)<', html)
    assert labels == (["Muttersprachliche Referenz", "Lernende:r"] if lang == "de" else ["Native-speaker reference", "Learner"]) * 3
    # recurring solution, closed by default, and the target word sequence of D24 is "sus amigos" (not "mis amigos")
    assert html.count('<details class="pm-teaching-solution">') == 3
    assert ("Auflösung: Was ist zu hören?" if lang == "de" else "Solution: What can be heard?") in html
    assert "<em><strong>sus amigos</strong></em>" in html and "mis amigos" not in html
    # every comparison box carries the audio icon and a title: same module as the comparisons of "which-pronunciation"
    assert html.count("audio-section-icon") == 3 and html.count("promat-content-block__title pm-panel__title") >= 3
    titles = re.findall(r'<h3 class="promat-content-block__title pm-panel__title">(.*?)</h3>', html)
    expected = (["Mit und ohne Knacklaut: <em>o hay</em>", "Ohne zusätzlichen Neueinsatz: <em>tiene hambre</em>", "Resilbifizierung: <em>sus amigos</em>"] if lang == "de"
                else ["With and without a glottal stop: <em>o hay</em>", "No additional fresh onset: <em>tiene hambre</em>", "Resyllabification: <em>sus amigos</em>"])
    assert titles == expected
    assert "Auf einen Blick" not in html and "At a glance" not in html
    assert "https://linguistik.hispanistica.com/aussprache/#laute-des-spanischen-herausforderungen" in html


def test_marele_recordings_are_declared_with_origin_and_the_checked_mapping() -> None:
    comparison = next(c for c in slots.load_slots()["comparisons"] if c["id"] == "p1-ohay")
    by_slot = {r["slot"]: r for r in comparison["recordings"]}
    # glottis_l1 = target pronunciation [o.ˈai] (reference), glottis_ele = learner pronunciation [ʔo.ʔai]
    assert by_slot["ref"]["category"] == "reference" and by_slot["ref"]["origin"]["source_file"].endswith("marele/glottis_l1.mp3")
    assert by_slot["learner"]["category"] == "learner" and by_slot["learner"]["origin"]["source_file"].endswith("marele/glottis_ele.mp3")
    assert {r["origin"]["corpus"] for r in by_slot.values()} == {"MAR.ELE"}
    assert [r["origin"]["transcription"] for r in (by_slot["ref"], by_slot["learner"])] == ["[o.ˈai]", "[ʔo.ʔai]"]
    assert all("session_id" not in r and "item" not in r for r in by_slot.values())
    corpus = {c["id"]: {r["slot"]: r["item"]["id"] for r in c["recordings"]} for c in slots.load_slots()["comparisons"] if c["topic"] == "soft-spanish-hard-german" and c["id"] != "p1-ohay"}
    assert corpus == {"p1-hambre": {"ref": "d_27", "learner": "d_27"}, "p1-amigos": {"ref": "d_24", "learner": "d_24"}}


def test_hubs_list_all_topics_in_the_requested_order() -> None:
    for lang in ("de", "en"):
        hub = yaml.safe_load((TOPIC_DIR / "hubs" / f"{lang}.yaml").read_text(encoding="utf-8"))
        assert [g["topics"] for g in hub["groups"]] == [
            ["which-pronunciation", "soft-spanish-hard-german"],
            ["r", "r-am-silbenende", "b-or-v", "soft-consonants-b-d-g", "accent-changes-everything"],
        ]


def test_slot_registry_is_consistent_with_media_and_pages() -> None:
    data = slots.load_slots()
    assert slots.check(data) == []
    declared = {(c["topic"], r["file"]) for c, r in slots.iter_recordings(data)}
    on_disk = {(path.parents[3].name, f"{path.parent.name}/{path.name}") for kind in ("corpus", "marele") for path in TOPIC_DIR.glob(f"*/media/audio/{kind}/*.mp3")}
    assert declared == on_disk and len(declared) == 54
    for comparison, recording in slots.iter_recordings(data):
        assert recording["category"] in ("reference", "learner")
        if not slots.is_external(recording):
            assert recording["session_id"].startswith(slots.SESSION_PREFIX[recording["category"]])


def test_slot_sources_are_released_sessions_when_the_local_runtime_is_present() -> None:
    sessions_root = REPO_ROOT / "data" / "sessions"
    if not slots.runtime_available(sessions_root):
        pytest.skip("local research runtime not present")
    assert slots.check(slots.load_slots(), sessions_root) == []
