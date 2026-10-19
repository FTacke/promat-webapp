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
    "r-am-silbenende": {"de": "Das r am Wortende", "en": "The r at the End of a Word"},
    "b-or-v": {"de": "B oder V? Wenn die Schrift mitredet", "en": "B or V? When spelling has a say"},
    "soft-consonants-b-d-g": {"de": "Weiche Konsonanten: b, d und g", "en": "Soft consonants: b, d and g"},
    "accent-changes-everything": {"de": "Ein Akzent verändert alles", "en": "An accent changes everything"},
}
IMPULSES = {"soft-spanish-hard-german": 3, "r": 3, "r-am-silbenende": 3, "b-or-v": 3, "soft-consonants-b-d-g": 4, "accent-changes-everything": 3}
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
    assert len(sources) == len(expected) >= {"soft-spanish-hard-german": 8, "b-or-v": 5, "r-am-silbenende": 6}.get(slug, 8)
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
                    assert item["href"].startswith(("https://linguistik.hispanistica.com/", "https://doi.org/10.1515/"))


def test_listening_comparisons_name_speaker_category_and_item(client) -> None:
    html = _html(client, "de", "soft-spanish-hard-german")
    assert "Referenzsprecher:in" in html and "Lernende:r" in html
    assert "Pronunciation Matters · D27" in html and "Pronunciation Matters · W76" in html and "Pronunciation Matters · QY5" in html
    assert "Mexiko" not in html and "(B1)" not in html  # no fixed speaker identities: the recordings stay replaceable
    html = _html(client, "en", "r")
    assert "Reference speaker" in html and "Learner (B1)" in html and "Spain · W88" in html and "L1 German · W88" in html
    assert html.count('<details class="pm-teaching-solution">') == 1  # closed by default: no autoplay, no revealed solution


@pytest.mark.parametrize("lang", ["de", "en"])
def test_soft_spanish_page_has_the_four_comparisons_in_order_with_marele_first(client, lang: str) -> None:
    html = _html(client, lang, "soft-spanish-hard-german")
    # o hay (MAR.ELE) first, then tiene hambre (D27), reír (W76), los otros (QY5); sus amigos (D24) has no audio box any more
    names = ("marele/o-hay-ref", "marele/o-hay-learner", "corpus/p1-hambre-ref", "corpus/p1-hambre-learner", "corpus/p1-reir-ref", "corpus/p1-reir-learner", "corpus/p1-losotros-ref", "corpus/p1-losotros-learner")
    positions = [html.index(f"audio/{name}") for name in names]
    assert positions == sorted(positions) and "p1-amigos" not in html and "D24" not in html
    assert html.count("pm-teaching-block--audio-contrast") == 4
    assert "hispanistica.com/projects/marele" not in html  # origin is named as plain text, not linked (MAR.ELE site is being retired)
    assert html.count("pm-teaching-audio-contrast__example-subtitle\">MAR.ELE<") == 2
    assert "MAR.ELE" not in html.split("pm-teaching-block")[0]  # neither the meta description nor the page subtitle names it
    # the reference recording is announced first in every comparison, the learner recording second
    labels = re.findall(r'pm-teaching-audio-contrast__example-title">([^<]+)<', html)
    assert labels == (["Referenzsprecher:in", "Lernende:r"] if lang == "de" else ["Reference speaker", "Learner"]) * 4
    # only the o hay comparison keeps a collapsible solution (closed by default); D27 and D24 apply what was explained
    assert html.count('<details class="pm-teaching-solution">') == 1
    assert html.index('<details class="pm-teaching-solution">') < html.index("corpus/p1-hambre-ref")
    assert ("Auflösung: Was ist zu hören?" if lang == "de" else "Solution: What can be heard?") in html
    # the dynamic word-sequence chip stays in every comparison and shows exactly the passage that is played
    chips = re.findall(r'pm-teaching-audio-contrast__transcript-text">(.*?)</span>', html)
    assert chips == ["<em>o hay</em>", "<em>tiene hambre</em>", "<em>reír</em>", "¿Tampoco <em><strong>los otros</strong></em> quieren venir?"]
    assert "[o.ˈai]" in html and "[ʔo.ʔai]" in html and "[diː ˈʔɛntə]" in html  # IPA of the o hay solution and of die Ente
    # sus amigos stays a text example next to los otros (no audio box); never "mis amigos"
    assert "<em>sus amigos</em>" in html and "<em>los otros</em>" in html and "mis amigos" not in html
    assert "Vier Hörvergleiche" in html if lang == "de" else "Four listening comparisons" in html
    assert "Drei Hörvergleiche" not in html and "Three listening comparisons" not in html
    # every comparison box carries the audio icon and a title: same module as the comparisons of "which-pronunciation"
    assert html.count("audio-section-icon") == 4 and html.count("promat-content-block__title pm-panel__title") >= 4
    titles = re.findall(r'<h3 class="promat-content-block__title pm-panel__title">(.*?)</h3>', html)
    expected = ([f"Hörvergleich: <em>{w}</em>" for w in ("o hay", "tiene hambre", "reír", "los otros")] if lang == "de"
                else [f"Listening comparison: <em>{w}</em>" for w in ("o hay", "tiene hambre", "reír", "los otros")])
    assert titles == expected
    # editorial progression: orientation -> o hay -> articulation -> transfer contexts -> resyllabification -> classroom prompts
    headings = re.findall(r'<h2 [^>]*class="pm-teaching-section-heading__title">([^<]*)</h2>', html)
    assert headings == (["Wie entsteht der Knacklaut?", "Wo können Knacklaute bei Lernenden auftreten?", "Wenn Wortgrenzen verschwimmen", "Impulse für den Unterricht"] if lang == "de"
                        else ["How is the glottal stop produced?", "Where can learners produce glottal stops?", "When word boundaries blur", "Classroom prompts"])
    assert "Hören und entdecken" not in html and "Listen and discover" not in html
    assert html.index("pm-teaching-block--audio-contrast") < html.index(headings[0])  # the first comparison follows the orientation text directly
    assert "su\u2011sa\u2011mi\u2011gos" in html and "lo\u2011so\u2011tros" in html
    # reír is the second comparison of the transfer section, directly after tiene hambre and without extra text or solution
    assert html.index("corpus/p1-hambre-learner") < html.index("Listening comparison: <em>reír" if lang == "en" else "Hörvergleich: <em>reír")
    assert html.index("corpus/p1-reir-learner") < html.index(headings[2])
    assert "Auf einen Blick" not in html and "At a glance" not in html
    assert "https://linguistik.hispanistica.com/aussprache/#laute-des-spanischen-herausforderungen" in html


@pytest.mark.parametrize("lang", ["de", "en"])
def test_soft_spanish_classroom_prompts_are_the_three_numbered_impulses(client, lang: str) -> None:
    html = _html(client, lang, "soft-spanish-hard-german")
    titles = re.findall(r'class="pm-teaching-impulses__item-title">([^<]+)<', html)
    assert titles == (["Erst hören, dann erklären", "Aussprache bewusst erproben", "Sprachen vergleichen"] if lang == "de"
                      else ["Listen first, explain later", "Explore pronunciation consciously", "Compare languages"])
    # impulse 02: both resilbification examples and the stepwise utterance series, Spanish examples in italics, arrows kept with the item before
    bodies = re.findall(r'class="pm-teaching-impulses__item-body">(.*?)</p>', html, re.S)
    assert len(bodies) == 3
    nbsp = "\u00a0"
    series = f"<em>el amigo</em>{nbsp}→ <em>el amigo de Ana</em>{nbsp}→ <em>el amigo de Ana es alto</em>"
    assert series in bodies[1] and bodies[1].endswith(series + ".")
    assert "<em>los otros</em>" in bodies[1] and "<em>sus amigos</em>" in bodies[1] and "<em>die Ente</em>" in bodies[1]
    assert "\u00ad" not in bodies[1]  # no artificial soft hyphens in the example series
    assert ("Auch einfache, schrittweise erweiterte Äußerungen eignen sich dafür" if lang == "de" else "Simple utterances that gradually increase in length also work well") in bodies[1]
    assert ("Anschließend spanische Wortfolgen ohne zusätzlichen Knacklaut sprechen" if lang == "de" else "Then practise Spanish word sequences without an additional glottal stop") in bodies[1]
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
    comparisons = [c for c in slots.load_slots()["comparisons"] if c["topic"] == "soft-spanish-hard-german"]
    assert [c["id"] for c in comparisons] == ["p1-ohay", "p1-hambre", "p1-reir", "p1-losotros"]
    corpus = {c["id"]: {r["slot"]: (r["session_id"], r["item"]["id"]) for r in c["recordings"]} for c in comparisons if c["id"] != "p1-ohay"}
    # the manually curated combinations (phonetic curation by Ana Goás Pérez)
    assert corpus == {
        "p1-hambre": {"ref": ("ES-N-0004-2026-S01", "d_27"), "learner": ("ES-L-0006-2026-S01", "d_27")},
        "p1-reir": {"ref": ("ES-N-0005-2026-S01", "wl_076"), "learner": ("ES-L-0019-2026-S01", "wl_076")},
        "p1-losotros": {"ref": ("ES-N-0002-2026-S01", "qy_05"), "learner": ("ES-L-0007-2026-S01", "qy_05")},
    }


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


def test_cropped_recordings_are_declared_with_cut_points_and_source_hashes() -> None:
    data = slots.load_slots()
    cropped = {(c["id"], r["slot"]): r for c, r in slots.iter_recordings(data) if r.get("crop")}
    # tiene hambre (D27) is a cut-out of the item MP3; reír (word list) is already isolated and los otros (QY5) plays the full sentence
    assert set(cropped) == {("p1-hambre", "ref"), ("p1-hambre", "learner")}
    for comparison in data["comparisons"]:
        if comparison["id"] == "p1-losotros":
            assert all("crop" not in r and "source_sha256" not in r for r in comparison["recordings"])
    for (_comparison, _slot), recording in cropped.items():
        crop = recording["crop"]
        assert 0 < crop["start_ms"] < crop["end_ms"] and crop["fade_in_ms"] >= 5 and crop["fade_out_ms"] >= 10
        assert len(recording["source_sha256"]) == 64 and recording["sha256"] != recording["source_sha256"]
        assert crop["tool"].startswith("ffmpeg")
    # every cropped comparison names the words it cuts out; the chips on the page show exactly these words
    by_id = {c["id"]: c for c in data["comparisons"]}
    assert by_id["p1-hambre"]["target_tokens"] == ["tiene", "hambre"] and by_id["p1-losotros"]["target_tokens"] == ["los", "otros"]
    # the clips are short passages, not the full sentences
    for name, upper_ms in (("p1-hambre-ref", 900), ("p1-hambre-learner", 1200)):
        size = (TOPIC_DIR / "soft-spanish-hard-german" / "media" / "audio" / "corpus" / f"{name}.mp3").stat().st_size
        assert 8_000 < size < upper_ms * 20  # 160 kbit/s = 20 bytes per ms


def test_cut_outs_are_reproducible_from_the_declared_cut_points(tmp_path) -> None:
    import shutil as shutil_module

    sessions_root = REPO_ROOT / "data" / "sessions"
    if shutil_module.which("ffmpeg") is None or not slots.runtime_available(sessions_root):
        pytest.skip("ffmpeg or the local research runtime is not present")
    data = slots.load_slots()
    for comparison, recording in slots.iter_recordings(data):
        if not recording.get("crop"):
            continue
        source = slots.source_path(sessions_root, recording)
        assert slots.sha256_of(source) == recording["source_sha256"]  # the corpus recording itself is untouched
        target = tmp_path / Path(recording["file"]).name
        slots.derive_crop(source, target, recording["crop"])
        if recording["crop"]["tool"] == f"ffmpeg {slots.ffmpeg_version()}":
            assert slots.sha256_of(target) == recording["sha256"], recording["file"]  # bit-identical with the same tool version


def test_released_sessions_only_and_the_reserve_is_documented_but_not_integrated() -> None:
    data = slots.load_slots()
    used = {r["session_id"] for _c, r in slots.iter_recordings(data) if not slots.is_external(r)}
    reserves = data["reserves"]
    assert [r["id"] for r in reserves if r["topic"] == "soft-spanish-hard-german"] == ["p1-amigos"]
    soft = next(r for r in reserves if r["id"] == "p1-amigos")
    assert {soft["reference"], soft["learner"]} == {"ES-N-0004-2026-S01", "ES-L-0001-2026-S01"}
    reserve_sessions = {r[role] for r in reserves for role in ("reference", "learner")}
    # sessions without a Teaching release never appear, neither as recording nor as reserve
    for excluded in slots.EXCLUDED_SESSIONS:
        assert excluded not in used and excluded not in reserve_sessions
    assert "ES-L-0014-2026-S01" in slots.EXCLUDED_SESSIONS
    # a reserve has no media and no audio box
    assert not list((TOPIC_DIR / "soft-spanish-hard-german" / "media" / "audio" / "corpus").glob("p1-amigos*"))
    broken = {**data, "comparisons": [dict(data["comparisons"][0])]}
    broken["comparisons"][0]["recordings"] = [dict(data["comparisons"][1]["recordings"][1], session_id="ES-L-0014-2026-S01")]
    broken["comparisons"][0]["topic"] = "soft-spanish-hard-german"
    assert any("excluded from Teaching use" in problem for problem in slots.check(broken))


@pytest.mark.parametrize("lang", ["de", "en"])
def test_soft_spanish_page_names_both_authors_in_display_citation_and_structured_data(client, lang: str) -> None:
    html = _html(client, lang, "soft-spanish-hard-german")
    assert "Felix Tacke, Ana Goás Pérez" in html  # visible author line (shared convention: names joined by comma)
    title = "Weiches Spanisch, hartes Deutsch" if lang == "de" else "Soft Spanish, hard German"
    quote_open, quote_close = ("„", "“") if lang == "de" else ("“", "”")
    editor = "Hrsg." if lang == "de" else "ed."
    # generated citation: creators of this page, editor of the platform stays Felix Tacke
    assert f"Tacke, Felix &amp; Goás Pérez, Ana (2026). {quote_open}{title}{quote_close}. In: Felix Tacke ({editor})" in html
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
    import json as json_module
    data = json_module.loads(ld)
    authors = data.get("author") or data.get("creator")
    names = [a["name"] for a in (authors if isinstance(authors, list) else [authors])]
    assert names == ["Felix Tacke", "Ana Goás Pérez"] or [n.replace("Prof. Dr. ", "") for n in names] == ["Felix Tacke", "Ana Goás Pérez"]
    # the shared authorship is page-specific: other topics and the editor of the platform are unchanged
    other = _html(client, lang, "r")
    assert "Goás Pérez" not in other.split("pm-teaching-block")[0] and "Goás Pérez, Ana" not in other
    assert "Illustration: Felix Tacke" in html  # the illustration credit stays with Felix Tacke only


@pytest.mark.parametrize("lang", ["de", "en"])
def test_spanish_hub_has_one_compact_introduction_paragraph(client, lang: str) -> None:
    hub = client.get(f"/{lang}/teaching/spanish").get_data(as_text=True)
    intro = re.search(r'<section class="pm-reading pm-teaching-overview__intro"[^>]*>(.*?)</section>', hub, re.S).group(1)
    paragraphs = re.findall(r'<p class="pm-teaching-overview__intro-text">(.*?)</p>', intro, re.S)
    expected = ("Die Themenseiten bieten fachliche Orientierung, Hörbeispiele und Anregungen für kurze Ausspracheimpulse im Spanischunterricht. "
                "Oft genügen dafür zehn Minuten zwischendurch – und viele Phänomene lassen sich mit passenden Beispielen schon ab A1 aufgreifen.") if lang == "de" else (
                "The topic pages offer linguistic guidance, listening examples, and ideas for short pronunciation activities in Spanish lessons. "
                "Often, just ten minutes here and there are enough – and many of these features can be introduced as early as A1 with suitable examples.")
    assert [html_module.unescape(paragraph).strip() for paragraph in paragraphs] == [expected]
    assert "<strong" not in intro and "<em" not in intro  # no emphasis inside the paragraph, no separate A1 box
    assert "Aussprache von Anfang an" not in hub and "Pronunciation from the start" not in hub and "pm-teaching-overview__note" not in hub
    for slug in TOPICS:  # the A1 remark belongs to the overview only
        assert "A1" not in _html(client, lang, slug)


@pytest.mark.parametrize("lang", ["de", "en"])
def test_b_or_v_page_follows_the_agreed_dramaturgy(client, lang: str) -> None:
    html = _html(client, lang, "b-or-v")
    de = lang == "de"
    # headings: letters/sound, two letters -> two sounds; then the classroom prompts (no allophony section of its own)
    headings = re.findall(r'<h2 [^>]*class="pm-teaching-section-heading__title">([^<]*)</h2>', html)
    assert headings == (["Zwei Buchstaben, ein Laut", "Wenn zwei Buchstaben zu zwei Lauten werden", "Impulse für den Unterricht"] if de
                        else ["Two letters, one sound", "When two letters become two sounds", "Classroom prompts"])
    # three listening boxes; the first one directly follows the short orientation text and is the only one with a collapsible solution
    titles = re.findall(r'<h3 class="promat-content-block__title pm-panel__title">(.*?)</h3>', html)
    prefix = "Hörvergleich" if de else "Listening comparison"
    assert titles[:3] == [f"{prefix}: <em>bienes – vienes</em>", f"{prefix}: <em>barón – varón</em>", f"{prefix}: <em>vienes</em>"]
    assert html.count('<details class="pm-teaching-solution">') == 1
    assert html.index("pm-teaching-block--audio-contrast") < html.index(headings[0]) and html.index('<details class="pm-teaching-solution">') < html.index(headings[0])
    chips = re.findall(r'pm-teaching-audio-contrast__transcript-text">(.*?)</span>', html)
    assert chips == ["<em>bienes – vienes</em>", "<em>barón – varón</em>", "<em>bienes – vienes</em>"]
    # first box: two reference voices (no learner label), then reference + learner in the MAR.ELE and the corpus box
    labels = re.findall(r'pm-teaching-audio-contrast__example-title">([^<]+)<', html)
    ref, learner = ("Referenzsprecher:in", "Lernende:r") if de else ("Reference speaker", "Learner")
    assert labels == [ref, ref, ref, learner, ref, learner]
    subtitles = re.findall(r'pm-teaching-audio-contrast__example-subtitle">([^<]+)<', html)
    assert subtitles[:2] == (["Mexiko · W92", "Chile · W92"] if de else ["Mexico · W92", "Chile · W92"])
    assert subtitles[2:4] == ["MAR.ELE", "MAR.ELE"] and "hispanistica.com/projects/marele" not in html
    # allophony: a short note with one link to the soft-consonants page, no audio of its own (vino/vida/lavar boxes are gone)
    assert f'href="/{lang}/teaching/spanish/soft-consonants-b-d-g"' in html and "p4-vino" not in html and "p4-vida" not in html and "p4-lavar" not in html
    assert client.get(f"/{lang}/teaching/spanish/soft-consonants-b-d-g").status_code == 200
    # info box: titled, short and without invented quantities
    box = re.search(r'pm-admonition--context.*?</section>', html, re.S).group(0)
    box_text = html_module.unescape(re.sub(r"<[^>]+>", " ", box))
    assert ("auch Erstsprachler:innen sind manchmal unsicher" if de else "even native speakers are sometimes unsure") in box_text
    assert len(re.findall(r"[.!?](?:\s|$)", box_text)) <= 5 and "Tacke 2020" in box_text
    for forbidden in ("die meisten", "most native", "Katalan", "Catalan", "Prozent", "per cent"):
        assert forbidden not in html
    assert "⟨b⟩ / ⟨v⟩ → /b/" in html  # the quiet typographic summary
    # the classroom prompts include the reverse direction (writing); the German misspelling is framed as an illustration
    prompts = re.findall(r'class="pm-teaching-impulses__item-title">([^<]+)<', html)
    assert prompts == (["Erst hören, dann lesen", "Die Schrift bewusst hinterfragen", "Auch beim Schreiben entstehen Schwierigkeiten"] if de
                       else ["Listen first, then read", "Question the spelling consciously", "Writing causes difficulties too"])
    assert "<em>Fater</em>" in html and "<em>tubo</em>" in html and ("nicht als empirischer Befund" if de else "not as an empirical finding") in html
    # further reading: three textbook chapters and the 2020 publication, each with a short note
    items = re.findall(r'href="(https://[^"]+)"[^>]*>', html.split('<ul class="pm-teaching-further-reading__list">')[1])
    assert [u for u in items if "hispanistica.com" in u or "doi.org" in u][:4] == [
        "https://linguistik.hispanistica.com/orthographie/#unsystematische-alternanzen-b-vs-v",
        "https://linguistik.hispanistica.com/fehlerlinguistik/#einfluss-des-schriftbilds",
        "https://linguistik.hispanistica.com/aussprache/#kontextabhangige-mal-so-mal-so-laute",
        "https://doi.org/10.1515/9783110458084-025",
    ]


@pytest.mark.parametrize("lang", ["de", "en"])
def test_b_or_v_authorship_and_citation_are_page_specific(client, lang: str) -> None:
    html = _html(client, lang, "b-or-v")
    title = "B oder V? Wenn die Schrift mitredet" if lang == "de" else "B or V? When spelling has a say"
    quote_open, quote_close = ("„", "“") if lang == "de" else ("“", "”")
    assert f"Tacke, Felix (2026). {quote_open}{title}{quote_close}. In: Felix Tacke" in html
    assert "Goás Pérez" not in html  # authorship is documented per page: Ana Goás Pérez is not a co-author of this page
    assert html.count("pm-admonition--citation") == 1


def test_b_or_v_recordings_are_released_provenance_documented_and_replaceable() -> None:
    data = slots.load_slots()
    comparisons = {c["id"]: c for c in data["comparisons"] if c["topic"] == "b-or-v"}
    assert list(comparisons) == ["p4-bienes-vienes", "p4-baron-varon"]
    bienes = {r["slot"]: (r["session_id"], r["item"]["id"]) for r in comparisons["p4-bienes-vienes"]["recordings"]}
    # two reference voices that are not the MAR.ELE reference speakers, and a provisional learner candidate (to be audited)
    assert bienes == {"ref-mx": ("ES-N-0004-2026-S01", "wl_092"), "ref-cl": ("ES-N-0005-2026-S01", "wl_092"), "learner": ("ES-L-0019-2026-S01", "wl_092")}
    used = {session for session, _item in bienes.values()}
    assert not used & {"ES-N-0001-2026-S01", "ES-N-0002-2026-S01", "ES-N-0003-2026-S01"} and "ES-N-0003-2026-S01" in slots.EXCLUDED_SESSIONS  # no Ecuador
    baron = {r["slot"]: r for r in comparisons["p4-baron-varon"]["recordings"]}
    assert baron["ref"]["origin"]["source_file"].endswith("marele/baron_varon_l1.mp3") and baron["learner"]["origin"]["source_file"].endswith("marele/baron_varon_ele.mp3")
    assert baron["ref"]["origin"]["transcription"] == "[baˈɾon] – [baˈɾon]" and baron["learner"]["origin"]["transcription"] == "[baˈʁon] – *[vaˈʁon]"
    assert all(r["origin"]["corpus"] == "MAR.ELE" and "session_id" not in r for r in baron.values())
    reserves = {r["id"]: r for r in data["reserves"] if r["topic"] == "b-or-v"}
    assert {r["learner"] for r in reserves.values()} == {"ES-L-0006-2026-S01", "ES-L-0007-2026-S01"}
    assert not (slots.EXCLUDED_SESSIONS.keys() & {r["learner"] for r in reserves.values()})
    # the MAR.ELE originals are copied byte for byte (identical to the committed hashes, never re-encoded)
    for r in baron.values():
        assert r["sha256"] == slots.sha256_of(slots.media_path("b-or-v", r["file"]))


@pytest.mark.parametrize("lang", ["de", "en"])
def test_r_at_word_end_page_follows_the_agreed_dramaturgy(client, lang: str) -> None:
    html = _html(client, lang, "r-am-silbenende")
    de = lang == "de"
    headings = re.findall(r'<h2 [^>]*class="pm-teaching-section-heading__title">([^<]*)</h2>', html)
    assert headings == (["Wenn das deutsche r zum Vokal wird", "Nicht nur am Wortende", "Zwei r in einem Wort", "Impulse für den Unterricht"] if de
                        else ["When the German r becomes a vowel", "Not only at the end of a word", "Two r sounds in one word", "Classroom prompts"])
    # exactly three listening stations in the agreed order; only the first one has a collapsible solution; the first follows the short intro directly
    prefix = "Hörvergleich" if de else "Listening comparison"
    titles = re.findall(r'<h3 class="promat-content-block__title pm-panel__title">(.*?)</h3>', html)
    assert titles[:3] == [f"{prefix}: <em>flor</em>", f"{prefix}: <em>enfermo</em>", f"{prefix}: <em>reír</em>"] and html.count("pm-teaching-block--audio-contrast") == 3
    assert html.count('<details class="pm-teaching-solution">') == 1 and html.index('<details class="pm-teaching-solution">') < html.index(headings[0])
    assert html.index("pm-teaching-block--audio-contrast") < html.index(headings[0])
    chips = re.findall(r'pm-teaching-audio-contrast__transcript-text">(.*?)</span>', html)
    assert chips == ["<em>flor</em>", "<em>enfermo</em>", "<em>reír</em>"]
    ref, learner = ("Referenzsprecher:in", "Lernende:r") if de else ("Reference speaker", "Learner")
    assert re.findall(r'pm-teaching-audio-contrast__example-title">([^<]+)<', html) == [ref, learner] * 3
    subtitles = re.findall(r'pm-teaching-audio-contrast__example-subtitle">([^<]+)<', html)
    assert subtitles[0::2] == (["Spanien · W16", "Mexiko · W50", "Chile · W76"] if de else ["Spain · W16", "Mexico · W50", "Chile · W76"])
    # old building blocks are gone: overview box, generic rubric, variation box, cuidar/lavar cards
    for gone in ("Auf einen Blick", "At a glance", "Hören und entdecken", "Listen and discover", "cuidar", "lavar la ropa", "p3-cuidar", "p3-lavar", "Lernendenmuster", "Learner pattern", "pm-admonition--context"):
        assert gone not in html, gone
    # German phonetics: sehr / Vater / Lehrer with IPA, the Vater schwa named, and the Spanish contrast in IPA
    for fragment in ("[zeːɐ̯]", "[ˈfaːtɐ]", "[ˈleːʁɐ]", "[ˈfloɾ]", "[en.ˈfeɾ.mo]", "[re.ˈiɾ]", "[ʁe.ˈɪɐ]"):
        assert fragment in html, fragment
    assert ("Vater-Schwa" if de else "Vater schwa") in html
    # cross links: the other topic pages
    assert f'href="/{lang}/teaching/spanish/soft-spanish-hard-german"' in html and f'href="/{lang}/teaching/spanish/r"' in html
    assert "https://linguistik.hispanistica.com/aussprache/#anders-artikulierte-laute-die-r-laute" in html
    prompts = re.findall(r'class="pm-teaching-impulses__item-title">([^<]+)<', html)
    assert prompts == (["Das eigene Deutsch entdecken", "Spanische Wortenden bewusst hören", "Vom Wortende zur Silbe"] if de
                       else ["Discover your own German", "Listen to Spanish word endings consciously", "From word ending to syllable"])
    # the Vertiefung box lists exactly three resources with a short note each
    items = re.findall(r'pm-teaching-further-reading__item-title">([^<]+)<', html)
    assert items == (["Aussprache im digitalen Lehrbuch", "Das spanische r", "Weiches Spanisch, hartes Deutsch"] if de
                     else ["Pronunciation in the digital textbook", "The Spanish r", "Soft Spanish, hard German"])
    assert client.get(f"/{lang}/teaching/spanish/r").status_code == 200


@pytest.mark.parametrize("lang", ["de", "en"])
def test_r_at_word_end_citation_and_slug_are_stable(client, lang: str) -> None:
    html = _html(client, lang, "r-am-silbenende")
    title = "Das r am Wortende" if lang == "de" else "The r at the End of a Word"
    quote_open, quote_close = ("„", "“") if lang == "de" else ("“", "”")
    assert f"Tacke, Felix (2026). {quote_open}{title}{quote_close}. In: Felix Tacke" in html and "Goás Pérez" not in html
    assert f"https://pronunciation-matters.de/{lang}/teaching/spanish/r-am-silbenende" in html  # canonical URL keeps the old slug


def test_r_at_word_end_curation_is_released_traceable_and_keeps_the_positively_rated_reir_recording() -> None:
    data = slots.load_slots()
    comparisons = {c["id"]: c for c in data["comparisons"] if c["topic"] == "r-am-silbenende"}
    assert list(comparisons) == ["p3-flor", "p3-enfermo", "p3-reir"]
    picked = {cid: {r["slot"]: (r["session_id"], r["item"]["id"]) for r in c["recordings"]} for cid, c in comparisons.items()}
    # three different reference varieties (Spain, Mexico, Chile); learner picks are provisional and replaceable via this register
    assert picked == {
        "p3-flor": {"ref": ("ES-N-0002-2026-S01", "wl_016"), "learner": ("ES-L-0006-2026-S01", "wl_016")},
        "p3-enfermo": {"ref": ("ES-N-0004-2026-S01", "wl_050"), "learner": ("ES-L-0006-2026-S01", "wl_050")},
        "p3-reir": {"ref": ("ES-N-0005-2026-S01", "wl_076"), "learner": ("ES-L-0019-2026-S01", "wl_076")},
    }
    assert not {s for c in picked.values() for s, _i in c.values()} & set(slots.EXCLUDED_SESSIONS)
    # the W76 learner recording (A2, L1 German) that was rated suitable is unchanged, byte for byte, and also used on the sibling page
    reir_learner = next(r for r in comparisons["p3-reir"]["recordings"] if r["slot"] == "learner")
    assert reir_learner["sha256"] == "bd7e35613ab7265ecf821dd22c3b082aa15b56d4c09ddfd5a19656e101e84725"
    sibling = next(r for c in data["comparisons"] if c["id"] == "p1-reir" for r in c["recordings"] if r["slot"] == "learner")
    assert sibling["sha256"] == reir_learner["sha256"] and sibling["session_id"] == reir_learner["session_id"]
    reserves = [r for r in data["reserves"] if r["topic"] == "r-am-silbenende"]
    assert {r["learner"] for r in reserves} == {"ES-L-0001-2026-S01", "ES-L-0019-2026-S01", "ES-L-0004-2026-S01"}
    assert not list((TOPIC_DIR / "r-am-silbenende" / "media" / "audio" / "corpus").glob("p3-cuidar*")) and not list((TOPIC_DIR / "r-am-silbenende" / "media" / "audio" / "corpus").glob("p3-lavar*"))


@pytest.mark.parametrize("lang", ["de", "en"])
def test_spanish_overview_has_two_sections_in_two_column_grids(client, lang: str) -> None:
    hub = client.get(f"/{lang}/teaching/spanish").get_data(as_text=True)
    de = lang == "de"
    titles = re.findall(r'<h2 id="teaching-group-\d" class="pm-teaching-topic-group__title">([^<]+)</h2>', hub)
    assert titles == (["Zum Einstieg", "Aussprachephänomene entdecken"] if de else ["Getting started", "Exploring pronunciation features"])
    grids = re.findall(r'<div class="pm-card-grid pm-teaching-topic-grid([^"]*)">', hub)
    assert grids == [" pm-teaching-topic-grid--compact"] * 2  # same grid and maximum width for both sections
    cards = re.findall(rf'href="/{lang}/teaching/spanish/([a-z0-9-]+)"', hub)
    assert cards == ["which-pronunciation", "soft-spanish-hard-german", "b-or-v", "soft-consonants-b-d-g", "r", "r-am-silbenende", "accent-changes-everything"]
    assert len(set(cards)) == len(cards) == hub.count("pm-teaching-topic-card--available") == 7  # every existing page exactly once
    assert "vokal" not in hub.lower() and "vowel" not in hub.lower() and "pm-teaching-topic-card--pending" not in hub  # planned vowel page: no placeholder
    for slug in cards:
        assert client.get(f"/{lang}/teaching/spanish/{slug}").status_code == 200
    # the two-column layout is a property of this hub only: other teaching hubs keep their grids
    for other in ("french", "german", "english"):
        source = REPO_ROOT / "content" / "teaching" / other / "hubs" / f"{lang}.yaml"
        assert not source.exists() or "card_columns" not in source.read_text(encoding="utf-8")


def test_hubs_list_all_topics_in_the_requested_order() -> None:
    for lang in ("de", "en"):
        hub = yaml.safe_load((TOPIC_DIR / "hubs" / f"{lang}.yaml").read_text(encoding="utf-8"))
        assert [g["topics"] for g in hub["groups"]] == [
            ["which-pronunciation", "soft-spanish-hard-german"],
            ["b-or-v", "soft-consonants-b-d-g", "r", "r-am-silbenende", "accent-changes-everything"],
        ]


def test_slot_registry_is_consistent_with_media_and_pages() -> None:
    data = slots.load_slots()
    assert slots.check(data) == []
    declared = {(c["topic"], r["file"]) for c, r in slots.iter_recordings(data)}
    on_disk = {(path.parents[3].name, f"{path.parent.name}/{path.name}") for kind in ("corpus", "marele") for path in TOPIC_DIR.glob(f"*/media/audio/{kind}/*.mp3")}
    assert declared == on_disk and len(declared) == 45
    for comparison, recording in slots.iter_recordings(data):
        assert recording["category"] in ("reference", "learner")
        if not slots.is_external(recording):
            assert recording["session_id"].startswith(slots.SESSION_PREFIX[recording["category"]])


def test_slot_sources_are_released_sessions_when_the_local_runtime_is_present() -> None:
    sessions_root = REPO_ROOT / "data" / "sessions"
    if not slots.runtime_available(sessions_root):
        pytest.skip("local research runtime not present")
    assert slots.check(slots.load_slots(), sessions_root) == []
