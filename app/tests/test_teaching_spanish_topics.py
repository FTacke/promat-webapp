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
IMPULSES = {"soft-spanish-hard-german": 3, "r": 3, "r-am-silbenende": 2, "b-or-v": 3, "soft-consonants-b-d-g": 4, "accent-changes-everything": 3}
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
    assert html.count('class="pm-teaching-solution"') == 1  # soft-spanish-hard-german keeps its single solution (o hay)
    assert html.count("pm-teaching-block--audio-contrast") >= 3
    # classroom prompts: one numbered impulse list under the shared accent-underlined heading, no tip box
    assert html.count('class="pm-teaching-block pm-teaching-block--teaching-impulses pm-panel pm-reading"') == 1
    assert html.count('class="pm-teaching-impulses__item"') == IMPULSES[slug]
    assert html.count('class="pm-teaching-impulses__item-title"') == IMPULSES[slug]
    assert "pm-admonition--tip" not in html and "Kurzaufgabe" not in html and "Quick task" not in html and "Für den Unterricht" not in html
    heading = "Impulse für den Unterricht" if lang == "de" else "Classroom prompts"
    assert re.findall(r'<h2 [^>]*class="pm-teaching-section-heading__title">([^<]*)</h2>', html).count(heading) == 1
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
    assert "Referenzsprecher:in" in html and "Lernende:r" in html
    assert "Pronunciation Matters · D27" in html and "Pronunciation Matters · D24" in html
    assert "Mexiko" not in html and "(B1)" not in html  # no fixed speaker identities: the recordings stay replaceable
    html = _html(client, "en", "r")
    assert "Reference speaker" in html and "Learner (B1)" in html and "Spain · W88" in html and "L1 German · W88" in html
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
    assert labels == (["Referenzsprecher:in", "Lernende:r"] if lang == "de" else ["Reference speaker", "Learner"]) * 3
    # only the o hay comparison keeps a collapsible solution (closed by default); D27 and D24 apply what was explained
    assert html.count('<details class="pm-teaching-solution">') == 1
    assert html.index('<details class="pm-teaching-solution">') < html.index("corpus/p1-hambre-ref")
    assert ("Auflösung: Was ist zu hören?" if lang == "de" else "Solution: What can be heard?") in html
    assert html.count("pm-teaching-audio-contrast__transcript-text") == 3  # the dynamic word-sequence chip stays in every comparison
    assert "[o.ˈai]" in html and "[ʔo.ʔai]" in html and "[diː ˈʔɛntə]" in html  # IPA of the o hay solution and of die Ente
    # target word sequence of D24 is "sus amigos" (not "mis amigos")
    assert "<em><strong>sus amigos</strong></em>" in html and "mis amigos" not in html
    # every comparison box carries the audio icon and a title: same module as the comparisons of "which-pronunciation"
    assert html.count("audio-section-icon") == 3 and html.count("promat-content-block__title pm-panel__title") >= 3
    titles = re.findall(r'<h3 class="promat-content-block__title pm-panel__title">(.*?)</h3>', html)
    expected = (["Hörvergleich: <em>o hay</em>", "Hörvergleich: <em>tiene hambre</em>", "Hörvergleich: <em>sus amigos</em>"] if lang == "de"
                else ["Listening comparison: <em>o hay</em>", "Listening comparison: <em>tiene hambre</em>", "Listening comparison: <em>sus amigos</em>"])
    assert titles == expected
    # editorial progression: orientation -> o hay -> articulation -> transfer contexts -> resyllabification -> classroom prompts
    headings = re.findall(r'<h2 [^>]*class="pm-teaching-section-heading__title">([^<]*)</h2>', html)
    assert headings == (["Wie entsteht der Knacklaut?", "Wo können Knacklaute bei Lernenden auftreten?", "Wenn Wortgrenzen verschwimmen", "Impulse für den Unterricht"] if lang == "de"
                        else ["How is the glottal stop produced?", "Where can learners produce glottal stops?", "When word boundaries blur", "Classroom prompts"])
    assert "Hören und entdecken" not in html and "Listen and discover" not in html
    assert html.index("pm-teaching-block--audio-contrast") < html.index(headings[0])  # the first comparison follows the orientation text directly
    assert "reír" in html and "su\u2011sa\u2011mi\u2011gos" in html
    assert "Auf einen Blick" not in html and "At a glance" not in html
    assert "https://linguistik.hispanistica.com/aussprache/#laute-des-spanischen-herausforderungen" in html


@pytest.mark.parametrize("lang", ["de", "en"])
def test_soft_spanish_classroom_prompts_are_the_three_numbered_impulses(client, lang: str) -> None:
    html = _html(client, lang, "soft-spanish-hard-german")
    titles = re.findall(r'class="pm-teaching-impulses__item-title">([^<]+)<', html)
    assert titles == (["Erst hören, dann erklären", "Aussprache bewusst erproben", "Sprachen vergleichen"] if lang == "de"
                      else ["Listen first, explain later", "Try out pronunciation deliberately", "Compare languages"])
    # the old summary sentence of the three comparisons is gone; the impulses come after the last solution and before the further reading
    assert "Die drei Hörvergleiche veranschaulichen" not in html and "The three listening comparisons illustrate" not in html
    assert html.rindex('<details class="pm-teaching-solution">') < html.index("pm-teaching-impulses") < html.index("pm-teaching-further-reading")


@pytest.mark.parametrize("lang", ["de", "en"])
def test_glottal_stop_illustration_sits_between_the_explanation_and_tiene_hambre(client, lang: str) -> None:
    html = _html(client, lang, "soft-spanish-hard-german")
    src = "/teaching-media/spanish/soft-spanish-hard-german/images/glottal-stop-larynx-hand.png"
    assert html.count(f'<img src="{src}"') == 1
    figure = re.search(r'<figure id="[^"]+" data-teaching-width="wide" class="pm-teaching-block pm-teaching-figure">(.*?)</figure>', html, re.S).group(1)
    alt = html_module.unescape(re.search(r'alt="([^"]+)"', figure).group(1))
    caption = html_module.unescape(re.search(r'pm-teaching-figure__caption-text">(.*?)</span>', figure, re.S).group(1))
    credit = html_module.unescape(re.search(r'pm-teaching-figure__credit">(.*?)</span>', figure, re.S).group(1))
    if lang == "de":
        assert caption == "Die Handhaltung veranschaulicht die Lage des Kehlkopfs, in dem der Knacklaut gebildet wird."
        assert credit == "Illustration: Felix Tacke (Konzept und Prompting), KI-generiert · Pronunciation Matters (2026)"
        assert "Kehlkopf" in alt
    else:
        assert caption == "The hand gesture indicates the position of the larynx, where the glottal stop is produced."
        assert credit == "Illustration: Felix Tacke (concept and prompting), AI-generated · Pronunciation Matters (2026)"
        assert "larynx" in alt
    assert "Illustration:" not in alt and "KI-generiert" not in alt and "AI-generated" not in alt  # the credit is not repeated in the alt text
    # order: explanation heading, illustration, then the next section
    how = "Wie entsteht der Knacklaut?" if lang == "de" else "How is the glottal stop produced?"
    next_heading = "Wo können Knacklaute bei Lernenden auftreten?" if lang == "de" else "Where can learners produce glottal stops?"
    assert html.index(how) < html.index(src) < html.index(next_heading)
    response = client.get(src)
    assert response.status_code == 200 and response.mimetype == "image/png"
    # one shared file for both editions, and no working copy left in the repository root
    assert len(list(TOPIC_DIR.glob("soft-spanish-hard-german/media/images/*.png"))) == 1
    assert not (REPO_ROOT / "glottis.png").exists()


@pytest.mark.parametrize("lang", ["de", "en"])
def test_glottal_stop_illustration_is_delivered_as_webp_with_the_master_as_fallback(client, lang: str) -> None:
    html = _html(client, lang, "soft-spanish-hard-german")
    base = "/teaching-media/spanish/soft-spanish-hard-german/images/glottal-stop-larynx-hand"
    assert f'<source type="image/webp" srcset="{base}.webp">' in html
    assert f'<img src="{base}.png"' in html and 'width="1448" height="1086" loading="lazy"' in html
    webp = client.get(f"{base}.webp")
    assert webp.status_code == 200 and webp.mimetype == "image/webp"
    master = client.get(f"{base}.png")
    assert master.status_code == 200 and master.mimetype == "image/png"
    assert webp.content_length < master.content_length / 10  # >90 % smaller than the master
    assert webp.content_length < 100_000


def test_illustration_masters_are_untouched_and_derivatives_are_declared() -> None:
    import teaching_images as images

    assert images.check(images.load_manifest()) == []
    master = TOPIC_DIR / "soft-spanish-hard-german" / "media" / "images" / "glottal-stop-larynx-hand.png"
    # the master is the original upload, byte for byte (SHA-256 of the committed file of 2026-10-11)
    assert images.sha256_of(master) == "46b2d048503ff43fe478395e1a0897ca2bb98af72e92c952bbcd73f412f062a6"
    assert images.png_size(master) == (1448, 1086)
    webp = master.with_suffix(".webp")
    assert images.webp_size(webp) == (960, 720)


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


@pytest.mark.parametrize(("slug", "lang"), PAIRS)
def test_speaker_terms_are_central_and_non_normative(client, slug: str, lang: str) -> None:
    html = _html(client, lang, slug)
    reference, learner = ("Referenzsprecher:in", "Lernende:r") if lang == "de" else ("Reference speaker", "Learner")
    titles = re.findall(r'pm-teaching-audio-contrast__example-title">([^<]+)<', html)
    assert titles and set(titles) <= {reference, learner} | {f"{learner} ({level})" for level in ("A1", "A2", "B1", "B2", "C1", "C2")}
    assert titles[0] == reference and titles.count(reference) >= len(titles) - titles.count(reference)  # some comparisons are reference-only
    for term in ("Muttersprach", "muttersprach", "Muttersprecher", "Native-speaker", "native-speaker", "Modellaussprache", "Modellsprecher"):
        assert term not in html, term
    # the topic sources name the role, not the wording (the terms live in the translation layer)
    source = (TOPIC_DIR / slug / f"{lang}.yaml").read_text(encoding="utf-8")
    assert "label: Muttersprach" not in source and "label: Native-speaker" not in source and "role: reference" in source and "role: learner" in source


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
