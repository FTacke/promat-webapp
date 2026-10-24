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
    "europe-sounds-different": {"de": "Europa klingt auf Spanisch anders", "en": "Europe sounds different in Spanish"},
    "r": {"de": "Das spanische r", "en": "The Spanish r"},
    "r-am-silbenende": {"de": "Das r am Wortende", "en": "The r at the End of a Word"},
    "b-or-v": {"de": "B oder V? Wenn die Schrift mitredet", "en": "B or V? When spelling has a say"},
    "soft-consonants-b-d-g": {"de": "b, d und g: Zu hart ausgesprochen?", "en": "b, d and g: Pronounced too hard?"},
}
# Not yet released (status: draft in both editions): neither listed in the hub nor served; its tests return with the release.
UNRELEASED = "accent-changes-everything"
IMPULSES = {"soft-spanish-hard-german": 3, "europe-sounds-different": 3, "r": 3, "r-am-silbenende": 3, "b-or-v": 3, "soft-consonants-b-d-g": 3}
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
    assert "pm-admonition--tip" not in html and "Kurzaufgabe" not in html and "Quick task" not in html
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
    assert len(sources) == len(expected) >= {"soft-spanish-hard-german": 8, "b-or-v": 5, "r-am-silbenende": 8, "soft-consonants-b-d-g": 8}.get(slug, 8)
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
    assert "Reference speaker" in html and "Learner" in html and "Spain · W90" in html and "Chile · W2" in html and "L1 German · W2" in html
    assert "Learner (" not in html  # no proficiency level on the labels (as on the sibling pages)
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
    assert titles[:3] == [f"{prefix}: <em>bienes – vienes</em>", f"{prefix}: <em>barón – varón</em>", f"{prefix}: <em>bienes – vienes</em>"]
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
    assert headings == (["Wenn das deutsche r zum Vokal wird", "Wenn auf das r ein Konsonant folgt", "Besonders knifflig: r am Anfang und am Ende", "Impulse für den Unterricht"] if de
                        else ["When the German r becomes a vowel", "When a consonant follows the r", "Especially tricky: r at the beginning and at the end", "Classroom prompts"])
    # exactly four listening stations in the agreed order; only the first one has a collapsible solution; the first follows the short intro directly
    prefix = "Hörvergleich" if de else "Listening comparison"
    titles = re.findall(r'<h3 class="promat-content-block__title pm-panel__title">(.*?)</h3>', html)
    assert titles[:4] == [f"{prefix}: <em>flor</em>", f"{prefix}: <em>lavar</em>", f"{prefix}: <em>enfermo</em>", f"{prefix}: <em>reír</em>"] and html.count("pm-teaching-block--audio-contrast") == 4
    # lavar sits after the explanation of German r-vocalisation (inside its section) and before the enfermo section
    assert html.index(headings[0]) < html.index(f"{prefix}: <em>lavar</em>") < html.index(headings[1]) < html.index(f"{prefix}: <em>enfermo</em>")
    assert html.count('<details class="pm-teaching-solution">') == 1 and html.index('<details class="pm-teaching-solution">') < html.index(headings[0])
    assert html.index("pm-teaching-block--audio-contrast") < html.index(headings[0])
    chips = re.findall(r'pm-teaching-audio-contrast__transcript-text">(.*?)</span>', html)
    assert chips == ["<em>flor</em>", "<em>lavar</em>", "<em>enfermo</em>", "<em>reír</em>"]
    # the precise listening questions (neutral, no solution taken in advance); only flor has a solution
    questions = [html_module.unescape(re.sub(r"<[^>]+>", "", q)).strip() for q in re.findall(r'class="audio-section-description">(.*?)</p>', html, re.S)]
    assert questions == ([
        "Wie klingt das r am Wortende in den beiden Aufnahmen?", "Wie wird das auslautende r in den beiden Aufnahmen realisiert?",
        "Wie klingt das r vor m in den beiden Aufnahmen?", "Wie klingen das r am Wortanfang und das r am Wortende in den beiden Aufnahmen?"] if de else [
        "How does the r at the end of the word sound in the two recordings?", "How is the word-final r realised in the two recordings?",
        "How does the r before m sound in the two recordings?", "How do the r at the beginning and the r at the end of the word sound in the two recordings?"])
    # the isolated German/Spanish comparison line after the explanation is gone
    assert "<strong>Deutsch:</strong>" not in html and "<strong>German:</strong>" not in html and "Nicht nur am Wortende" not in html and "Zwei r in einem Wort" not in html
    ref, learner = ("Referenzsprecher:in", "Lernende:r") if de else ("Reference speaker", "Learner")
    assert re.findall(r'pm-teaching-audio-contrast__example-title">([^<]+)<', html) == [ref, learner] * 4
    subtitles = re.findall(r'pm-teaching-audio-contrast__example-subtitle">([^<]+)<', html)
    assert subtitles[0::2] == (["Spanien · W16", "Spanien · W9", "Mexiko · W50", "Chile · W76"] if de else ["Spain · W16", "Spain · W9", "Mexico · W50", "Chile · W76"])
    # old building blocks are gone: overview box, generic rubric, variation box, cuidar/lavar cards
    for gone in ("Auf einen Blick", "At a glance", "Hören und entdecken", "Listen and discover", "cuidar", "lavar la ropa", "p3-cuidar", "Lernendenmuster", "Learner pattern", "pm-admonition--context"):
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
def test_spanish_r_page_follows_the_agreed_dramaturgy(client, lang: str) -> None:
    html = _html(client, lang, "r")
    de = lang == "de"
    headings = re.findall(r'<h2 [^>]*class="pm-teaching-section-heading__title">([^<]*)</h2>', html)
    assert headings == ([
        "Zwei r-Laute – und die Schrift hilft mit", "Einfach und mehrfach – auch bei anderen Wörtern", "Wenn das deutsche r ins Spanische übertragen wird",
        "Nicht jedes r klingt gleich", "Impulse für den Unterricht"] if de else [
        "Two r sounds – and the spelling helps", "Tap and trill – in other words, too", "When the German r is carried over into Spanish",
        "Not every r sounds the same", "Classroom prompts"])
    # five listening stations in the agreed order; the first follows the short introduction directly and is the only one with a solution
    prefix = "Hörvergleich" if de else "Listening comparison"
    titles = re.findall(r'<h3 class="promat-content-block__title pm-panel__title">(.*?)</h3>', html)
    assert titles[:5] == [f"{prefix}: <em>pero – perro</em>", f"{prefix}: <em>caro</em>", f"{prefix}: <em>carro</em>", f"{prefix}: <em>reloj</em>", f"{prefix}: <em>reír</em>"]
    assert html.count("pm-teaching-block--audio-contrast") == 5
    assert html.count('<details class="pm-teaching-solution">') == 1
    assert html.index("pm-teaching-block--audio-contrast") < html.index('<details class="pm-teaching-solution">') < html.index(headings[0])
    positions = [html.index(f"{prefix}: <em>{word}</em>") for word in ("pero – perro", "caro", "carro", "reloj", "reír")]
    assert positions == sorted(positions)
    assert html.index(headings[1]) < positions[1] < positions[2] < html.index(headings[2]) < positions[3] < positions[4] < html.index(headings[3])
    chips = re.findall(r'pm-teaching-audio-contrast__transcript-text">(.*?)</span>', html)
    assert chips == ["<em>pero – perro</em>", "<em>caro</em>", "<em>carro</em>", "<em>reloj</em>", "<em>reír</em>"]
    # open, neutral listening questions (the first does not give away the number of tongue taps)
    questions = [html_module.unescape(re.sub(r"<[^>]+>", "", q)).strip() for q in re.findall(r'class="audio-section-description">(.*?)</p>', html, re.S)]
    assert questions == ([
        "Worin unterscheiden sich die beiden r-Laute?", "Wie klingt das einfache r bei den beiden Referenzsprecher:innen?", "Wie klingt das mehrfache r bei den beiden Referenzsprecher:innen?",
        "Wie unterscheidet sich das r am Wortanfang in den beiden Aufnahmen?", "Wie klingt das r am Wortanfang in den beiden Aufnahmen?"] if de else [
        "How do the two r sounds differ?", "How does the tapped r sound for the two reference speakers?", "How does the trilled rr sound for the two reference speakers?",
        "How does the r at the beginning of the word differ in the two recordings?", "How does the r at the beginning of the word sound in the two recordings?"])
    # speaker labels follow the real speaker status: reference-reference pairs never say "learner"
    ref, learner = ("Referenzsprecher:in", "Lernende:r") if de else ("Reference speaker", "Learner")
    assert re.findall(r'pm-teaching-audio-contrast__example-title">([^<]+)<', html) == [ref] * 7 + [learner, ref, learner]
    subtitles = re.findall(r'pm-teaching-audio-contrast__example-subtitle">([^<]+)<', html)
    country = ("Spanien", "Chile", "Deutsch") if de else ("Spain", "Chile", "German")
    assert subtitles == [f"{country[0]} · W90", f"{country[1]} · W90", f"{country[0]} · W85", f"{country[1]} · W85", f"{country[0]} · W57", f"{country[1]} · W57",
                         f"{country[1]} · W2", f"L1 {country[2]} · W2", f"{country[1]} · W76", f"L1 {country[2]} · W76"]
    for fragment in ("[ˈpeɾo]", "[ˈpero]", "[reˈlox]", "⟨r⟩", "⟨rr⟩", "[ʁ]", "[ɾ]", "[r]"):
        assert fragment in html, fragment
    # removed building blocks: overview box, generic rubric, old comparison titles, the sentence variant D1, and no placeholder graphic
    for gone in ("Auf einen Blick", "At a glance", "Hören und entdecken", "Listen and discover", "D1", "Zwei Wörter, zwei r-Laute", "Platzhalter", "placeholder", "pm-admonition--tip"):
        assert gone not in html, gone
    # orientation intro: short, before the first listening card
    blocks = _blocks("r", lang)
    assert [b["type"] for b in blocks[:3]] == ["topic_meta", "text", "audio_contrast"]
    assert len(re.findall(r"[.!?](?:\s|$)", blocks[1]["body"])) == 3 and len(blocks[1]["body"]) < 420  # two to three sentences, no long pre-explanation
    # heritage-language box and its place in the dramaturgy
    box = "Herkunftssprachen als Ressource" if de else "Heritage languages as a resource"
    assert html.count(box) == 1 and html.index(headings[3]) < html.index(box) < html.index(headings[4])
    for language in (("Türkisch", "Kurdisch", "Italienisch") if de else ("Turkish", "Kurdish", "Italian")):
        assert language in html
    # classroom prompts and further reading
    prompts = re.findall(r'class="pm-teaching-impulses__item-title">([^<]+)<', html)
    assert prompts == (["Erst den Unterschied hören", "Die Artikulationsstelle bewusst machen", "Die Schreibung als Hilfe nutzen"] if de
                       else ["Hear the difference first", "Make the place of articulation conscious", "Use the spelling as a help"])
    items = re.findall(r'pm-teaching-further-reading__item-title">([^<]+)<', html)
    assert items == (["Aussprache im digitalen Lehrbuch", "Orthographie im digitalen Lehrbuch", "Herkunftssprachen im digitalen Lehrbuch", "Das r am Wortende"] if de
                     else ["Pronunciation in the digital textbook", "Orthography in the digital textbook", "Heritage languages in the digital textbook", "The r at the End of a Word"])
    for href in ("https://linguistik.hispanistica.com/aussprache/#anders-artikulierte-laute-die-r-laute", "https://linguistik.hispanistica.com/orthographie/#se-escribe-casi-como-se-habla",
                 "https://linguistik.hispanistica.com/herkunftssprachen/#gerolltes-r-normal-in-allen-herkunftssprachen"):
        assert href in html, href
    assert html.count(f'href="/{lang}/teaching/spanish/r-am-silbenende"') == 2  # in the text before the reír card and in the Vertiefung
    assert "claro" in html


@pytest.mark.parametrize("lang", ["de", "en"])
def test_spanish_r_articulation_graphic_sits_after_the_explanation_with_exact_texts(client, lang: str) -> None:
    html = _html(client, lang, "r")
    de = lang == "de"
    src = "/teaching-media/spanish/r/images/spanish-german-r-articulation"
    heading = "Zwei r-Laute – und die Schrift hilft mit" if de else "Two r sounds – and the spelling helps"
    next_heading = "Einfach und mehrfach – auch bei anderen Wörtern" if de else "Tap and trill – in other words, too"
    # exactly one figure: after the explanation of the articulation (with the transition sentence), before the spelling paragraph and the caro/carro cards
    assert html.count("<figure") == 1
    spelling = "Zwischen Vokalen unterscheiden die beiden Laute Wörter" if de else "Between vowels, the two sounds distinguish words"
    assert html.index(heading) < html.index("Beide spanischen r-Laute" if de else "Both Spanish r sounds") < html.index(f"{src}.png") < html.index(spelling) < html.index(next_heading)
    assert html.index(f"{src}.png") < html.index("pm-teaching-block--audio-contrast", html.index(next_heading))
    # no new main heading and no info box for the graphic
    assert re.findall(r'<h2 [^>]*class="pm-teaching-section-heading__title">([^<]*)</h2>', html).count(heading) == 1 and "pm-admonition" not in html.split("<figure")[1].split("</figure>")[0]
    # same shared image component as the [d]/[ð] graphic: wide figure, WebP with PNG master fallback, intrinsic size (no distortion), lazy decoding
    assert 'pm-teaching-figure pm-teaching-figure--wide">' in html and f'<source type="image/webp" srcset="{src}.webp">' in html
    assert 'width="1448" height="1086"' in html and 'loading="lazy"' in html
    figure = re.search(r'<figure id="[^"]+" data-teaching-width="wide" class="pm-teaching-block pm-teaching-figure pm-teaching-figure--wide">(.*?)</figure>', html, re.S).group(1)
    alt = html_module.unescape(re.search(r'alt="([^"]+)"', figure).group(1))
    caption = html_module.unescape(re.search(r'pm-teaching-figure__caption-text">(.*?)</span>', figure, re.S).group(1))
    credit = html_module.unescape(re.search(r'pm-teaching-figure__credit">(.*?)</span>', figure, re.S).group(1))
    if de:
        assert alt == ("Schematische Seitenschnitte des Mundraums: links die spanischen alveolaren R-Laute [ɾ] und [r] mit vorderer Zungenartikulation, "
                       "rechts das deutsche uvulare [ʁ] mit weiter hinten liegender Artikulationsstelle.")
        assert caption == ("Die spanischen R-Laute [ɾ] und [r] werden mit der Zungenspitze am Zahndamm gebildet. Beim im Standarddeutschen verbreiteten [ʁ] liegt die "
                           "Artikulationsstelle dagegen weiter hinten, am Zäpfchen. Die schematische Darstellung zeigt den Unterschied der Artikulationsorte.")
        assert credit == "Illustration: Felix Tacke (Konzept und Prompting), KI-generiert · Pronunciation Matters (2026)"
        assert "Im Standarddeutschen wird das r dagegen häufig weiter hinten gebildet, am Zäpfchen." in html
    else:
        assert alt.startswith("Schematic side views of the mouth:") and "[ɾ]" in alt and "[ʁ]" in alt and "uvular" in alt and "alveolar" in alt
        assert caption.startswith("The Spanish r sounds [ɾ] and [r] are produced with the tip of the tongue at the alveolar ridge.") and "at the uvula" in caption
        assert credit == "Illustration: Felix Tacke (concept and prompting), AI-generated · Pronunciation Matters (2026)"
        assert "In Standard German, by contrast, the r is often produced further back, at the uvula." in html
    # the caption shows the shared place of articulation, never a number of taps; [ʁ] is not equated with the uvular trill [ʀ]
    for text in (alt, caption):
        assert "[ʀ]" not in text and "einmal" not in text and "mehrfach" not in text and "once" not in text and "several" not in text
    assert client.get(f"{src}.webp").mimetype == "image/webp" and client.get(f"{src}.png").status_code == 200


def test_spanish_r_graphic_master_is_kept_with_a_declared_webp_derivative() -> None:
    import teaching_images as images

    media = TOPIC_DIR / "r" / "media" / "images"
    assert sorted(path.name for path in media.iterdir()) == ["spanish-german-r-articulation.png", "spanish-german-r-articulation.webp"]
    master = media / "spanish-german-r-articulation.png"
    assert images.png_size(master) == (1448, 1086) and images.webp_size(master.with_suffix(".webp")) == (1448, 1086)
    assert images.sha256_of(master) == "35ce4527b3f3f2fc3d030d99a755422b4feeffbc6302ff3f61633d0f5ae4afd3"
    assert images.check(images.load_manifest()) == [] and master.with_suffix(".webp").stat().st_size < master.stat().st_size / 5
    # both language editions use the one image resource; no copy is left in the repository root
    assert [b["src"] for lang in ("de", "en") for b in _blocks("r", lang) if b["type"] == "image"] == ["spanish-german-r-articulation.png"] * 2
    assert not list(REPO_ROOT.glob("*articulation*")) and not list(REPO_ROOT.glob("*.webp"))


@pytest.mark.parametrize("lang", ["de", "en"])
def test_spanish_r_page_citation_authorship_and_teaser(client, lang: str) -> None:
    html = _html(client, lang, "r")
    title = "Das spanische r" if lang == "de" else "The Spanish r"
    quote_open, quote_close = ("„", "“") if lang == "de" else ("“", "”")
    assert f"Tacke, Felix (2026). {quote_open}{title}{quote_close}. In: Felix Tacke" in html and "Goás Pérez" not in html  # authorship unchanged: Felix Tacke only
    assert f"https://pronunciation-matters.de/{lang}/teaching/spanish/r" in html
    teaser = ("Zwei spanische r-Laute – und warum das deutsche r anders klingt." if lang == "de"
              else "Two Spanish r sounds – and why the German r sounds different.")
    assert teaser in html_module.unescape(html)


def test_spanish_r_curation_is_released_traceable_and_reuses_the_reir_recording() -> None:
    data = slots.load_slots()
    comparisons = {c["id"]: c for c in data["comparisons"] if c["topic"] == "r"}
    assert list(comparisons) == ["p2-pero", "p2-caro", "p2-carro", "p2-reloj", "p2-reir"]
    picked = {cid: [(r["slot"], r["category"], r["session_id"], r["item"]["id"]) for r in c["recordings"]] for cid, c in comparisons.items()}
    spain, chile = "ES-N-0002-2026-S01", "ES-N-0005-2026-S01"
    assert picked == {
        "p2-pero": [("ref_a", "reference", spain, "wl_090"), ("ref_b", "reference", chile, "wl_090")],
        "p2-caro": [("ref_a", "reference", spain, "wl_085"), ("ref_b", "reference", chile, "wl_085")],
        "p2-carro": [("ref_a", "reference", spain, "wl_057"), ("ref_b", "reference", chile, "wl_057")],
        "p2-reloj": [("ref", "reference", chile, "wl_002"), ("learner", "learner", "ES-L-0011-2026-S01", "wl_002")],
        "p2-reir": [("ref", "reference", chile, "wl_076"), ("learner", "learner", "ES-L-0019-2026-S01", "wl_076")],
    }
    assert not {rec[2] for recs in picked.values() for rec in recs} & set(slots.EXCLUDED_SESSIONS)
    # W76 is the same recording pair as on the sibling pages: same session, item and bytes (no second audio file was produced)
    reir = {r["slot"]: r for r in comparisons["p2-reir"]["recordings"]}
    for comparison_id in ("p3-reir", "p1-reir"):
        sibling = {r["slot"]: r for c in data["comparisons"] if c["id"] == comparison_id for r in c["recordings"]}
        for slot in ("ref", "learner"):
            assert (sibling[slot]["session_id"], sibling[slot]["item"]) == (reir[slot]["session_id"], reir[slot]["item"])
            assert sibling[slot]["sha256"] == reir[slot]["sha256"]
    assert reir["learner"]["sha256"] == "bd7e35613ab7265ecf821dd22c3b082aa15b56d4c09ddfd5a19656e101e84725"
    # the media folder holds exactly the ten declared files (the old learner pairs are gone)
    corpus = TOPIC_DIR / "r" / "media" / "audio" / "corpus"
    assert sorted(path.name for path in corpus.glob("*.mp3")) == sorted(r["file"].split("/")[1] for c in comparisons.values() for r in c["recordings"])
    assert len(list(corpus.glob("*.mp3"))) == 10
    # reloj learner: documented reserves (not integrated), all inside the release gate
    reserves = [r for r in data["reserves"] if r["topic"] == "r"]
    assert {r["learner"] for r in reserves} == {"ES-L-0019-2026-S01", "ES-L-0021-2026-S01", "ES-L-0005-2026-S01"}
    assert not {r["learner"] for r in reserves} & set(slots.EXCLUDED_SESSIONS)


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
    assert list(comparisons) == ["p3-flor", "p3-lavar", "p3-enfermo", "p3-reir"]
    picked = {cid: {r["slot"]: (r["session_id"], r["item"]["id"]) for r in c["recordings"]} for cid, c in comparisons.items()}
    # reference varieties vary between the examples (Spain, Spain, Mexico, Chile); learner picks are provisional and replaceable via this register
    assert picked == {
        "p3-flor": {"ref": ("ES-N-0002-2026-S01", "wl_016"), "learner": ("ES-L-0006-2026-S01", "wl_016")},
        "p3-lavar": {"ref": ("ES-N-0001-2026-S01", "wl_009"), "learner": ("ES-L-0016-2026-S01", "wl_009")},
        "p3-enfermo": {"ref": ("ES-N-0004-2026-S01", "wl_050"), "learner": ("ES-L-0006-2026-S01", "wl_050")},
        "p3-reir": {"ref": ("ES-N-0005-2026-S01", "wl_076"), "learner": ("ES-L-0019-2026-S01", "wl_076")},
    }
    assert not {s for c in picked.values() for s, _i in c.values()} & set(slots.EXCLUDED_SESSIONS)
    # the W76 learner recording (A2, L1 German) that was rated suitable is unchanged, byte for byte, and also used on the sibling page
    reir_learner = next(r for r in comparisons["p3-reir"]["recordings"] if r["slot"] == "learner")
    assert reir_learner["sha256"] == "bd7e35613ab7265ecf821dd22c3b082aa15b56d4c09ddfd5a19656e101e84725"
    sibling = next(r for c in data["comparisons"] if c["id"] == "p1-reir" for r in c["recordings"] if r["slot"] == "learner")
    assert sibling["sha256"] == reir_learner["sha256"] and sibling["session_id"] == reir_learner["session_id"]
    # lavar uses a different learner than flor/enfermo (ES-L-0006); the enfermo pair that was rated very suitable is unchanged, byte for byte
    by_id = {cid: {r["slot"]: r for r in c["recordings"]} for cid, c in comparisons.items()}
    assert by_id["p3-lavar"]["learner"]["session_id"] != by_id["p3-flor"]["learner"]["session_id"]
    assert by_id["p3-enfermo"]["learner"]["sha256"] == "bf58c6d41e572dbf2bc48ef1ac90f2678e47495d49ddaeae88dc173819c0e4a8"
    assert by_id["p3-enfermo"]["ref"]["sha256"] == "4e6bce8e9fee40d2b64a41351b7ea1d42675eaac2f3b55629c830d926ad56f2d"
    assert by_id["p3-flor"]["ref"]["sha256"] == "0fb0caf8167297bbb1123f3b3411262e267233e6fdfcdf680170a9021890adfb"
    assert by_id["p3-flor"]["learner"]["sha256"] == "1484200994b9ceb4a9bd2aea4f15c5f3ca067c59771eaf37969fb434501ad3d8"
    reserves = [r for r in data["reserves"] if r["topic"] == "r-am-silbenende"]
    assert {r["learner"] for r in reserves} == {"ES-L-0001-2026-S01", "ES-L-0019-2026-S01", "ES-L-0004-2026-S01", "ES-L-0005-2026-S01"}
    corpus = TOPIC_DIR / "r-am-silbenende" / "media" / "audio" / "corpus"
    assert not list(corpus.glob("p3-cuidar*")) and sorted(path.name for path in corpus.glob("p3-lavar*")) == ["p3-lavar-learner.mp3", "p3-lavar-ref.mp3"]


@pytest.mark.parametrize("lang", ["de", "en"])
def test_spanish_overview_has_two_sections_in_two_column_grids(client, lang: str) -> None:
    hub = client.get(f"/{lang}/teaching/spanish").get_data(as_text=True)
    de = lang == "de"
    titles = re.findall(r'<h2 id="teaching-group-\d" class="pm-teaching-topic-group__title">([^<]+)</h2>', hub)
    assert titles == (["Zum Einstieg", "Aussprachephänomene entdecken"] if de else ["Getting started", "Exploring pronunciation features"])
    grids = re.findall(r'<div class="pm-card-grid pm-teaching-topic-grid([^"]*)">', hub)
    assert grids == [" pm-teaching-topic-grid--compact"] * 2  # same grid and maximum width for both sections
    cards = re.findall(rf'href="/{lang}/teaching/spanish/([a-z0-9-]+)"', hub)
    assert cards == ["which-pronunciation", "soft-spanish-hard-german", "europe-sounds-different", "b-or-v", "soft-consonants-b-d-g", "r", "r-am-silbenende"]
    assert len(set(cards)) == len(cards) == hub.count("pm-teaching-topic-card--available") == 7  # every released page exactly once; the draft page is not listed
    assert UNRELEASED not in hub
    assert "pm-teaching-topic-card--pending" not in hub  # no placeholder cards for planned pages
    for slug in cards:
        assert client.get(f"/{lang}/teaching/spanish/{slug}").status_code == 200
    # the two-column layout is a property of this hub only: other teaching hubs keep their grids
    for other in ("french", "german", "english"):
        source = REPO_ROOT / "content" / "teaching" / other / "hubs" / f"{lang}.yaml"
        assert not source.exists() or "card_columns" not in source.read_text(encoding="utf-8")


@pytest.mark.parametrize("lang", ["de", "en"])
def test_b_d_g_page_follows_the_agreed_dramaturgy(client, lang: str) -> None:
    html = _html(client, lang, "soft-consonants-b-d-g")
    de = lang == "de"
    headings = re.findall(r'<h2 [^>]*class="pm-teaching-section-heading__title">([^<]*)</h2>', html)
    assert headings == (["Verschluss oder Annäherung?", "Auch b und g werden weich", "Mehrere Approximanten in einer Wortfolge", "Impulse für den Unterricht"] if de
                        else ["Closure or approximation?", "b and g become soft, too", "Several approximants in one word sequence", "Classroom prompts"])
    # the heading sits directly before the el bebedor card, followed by its short introduction; the card keeps the explanation of the three positions
    assert html.index(headings[2]) < html.index(f'{"Hörvergleich" if de else "Listening comparison"}: <em>el bebedor</em>') and html.index('<em>con agua</em>') < html.index(headings[2])
    assert ("nicht auf die Stellung zwischen Vokalen beschränkt" if de else "not limited to the position between vowels") in html
    assert html.count("nicht auf die Position zwischen Vokalen beschränkt" if de else "therefore not limited") == 0
    # question cards (vida, lavar, con agua) and an explanatory statement for the summarising el bebedor card (no question, no repeated list of positions after the card)
    leads = [html_module.unescape(re.sub(r"<[^>]+>", "", q)).strip() for q in re.findall(r'class="audio-section-description">(.*?)</p>', html, re.S)]
    assert leads == ([
        "Was unterscheidet die Aussprache des d?", "Wie wird der Konsonant zwischen den beiden a ausgesprochen?", "Wie wird das g in den beiden Aufnahmen ausgesprochen?",
        "Die Wortfolge zeigt drei approximantische Realisierungen: [β] nach /l/ und zwischen Vokalen sowie [ð] zwischen Vokalen."] if de else [
        "What distinguishes the pronunciation of the d?", "How is the consonant between the two a pronounced?", "How is the g pronounced in the two recordings?",
        "The word sequence shows three approximant realisations: [β] after /l/ and between vowels, and [ð] between vowels."])
    assert ("das erste b nach l" if de else "the first b after l") not in html
    # four listening stations: d (vida, the only collapsible solution), b (lavar), g (con agua, MAR.ELE), several positions (el bebedor, MAR.ELE)
    prefix = "Hörvergleich" if de else "Listening comparison"
    titles = re.findall(r'<h3 class="promat-content-block__title pm-panel__title">(.*?)</h3>', html)
    assert titles[:4] == [f"{prefix}: <em>vida</em>", f"{prefix}: <em>lavar</em>", f"{prefix}: <em>con agua</em>", f"{prefix}: <em>el bebedor</em>"]
    assert html.count("pm-teaching-block--audio-contrast") == 4
    assert html.count('<details class="pm-teaching-solution">') == 1 and html.index('<details class="pm-teaching-solution">') < html.index(headings[0])
    assert re.findall(r'pm-teaching-audio-contrast__transcript-text">(.*?)</span>', html) == ["<em>vida</em>", "<em>lavar</em>", "<em>con agua</em>", "<em>el bebedor</em>"]
    ref, learner = ("Referenzsprecher:in", "Lernende:r") if de else ("Reference speaker", "Learner")
    assert re.findall(r'pm-teaching-audio-contrast__example-title">([^<]+)<', html) == [ref, learner] * 4
    subtitles = re.findall(r'pm-teaching-audio-contrast__example-subtitle">([^<]+)<', html)
    assert subtitles[0::2] == (["Mexiko · W45", "Spanien · W9", "MAR.ELE", "MAR.ELE"] if de else ["Mexico · W45", "Spain · W9", "MAR.ELE", "MAR.ELE"])
    assert "Chile" not in html and "hispanistica.com/projects/marele" not in html  # no Chilean reference for lavar; MAR.ELE named as plain text
    # removed building blocks: overview box, generic rubric, logro card, the separate [β] is not [v] note, the old context section
    for gone in ("Auf einen Blick", "At a glance", "Hören und entdecken", "Listen and discover", "cuidado", "labio", "p5-logro", "p5-algo", "p5-vino", "Nicht immer weich", "Not always soft",
                 "kein deutsches [v]", "not a German [v]", "<em>logro</em>]"):
        assert gone not in html, gone
    # articulation diagram directly after the closure/approximation explanation: wide figure, WebP + master fallback, exact caption, credit and alt text
    src = "/teaching-media/spanish/soft-consonants-b-d-g/images/dental-stop-approximant"
    assert html.index(headings[0]) < html.index(f"{src}.png") < html.index(headings[1])
    assert 'pm-teaching-figure pm-teaching-figure--wide">' in html and f'<source type="image/webp" srcset="{src}.webp">' in html and 'width="1448" height="1086"' in html
    figure = re.search(r'<figure id="[^"]+" data-teaching-width="wide" class="pm-teaching-block pm-teaching-figure pm-teaching-figure--wide">(.*?)</figure>', html, re.S).group(1)
    alt = html_module.unescape(re.search(r'alt="([^"]+)"', figure).group(1))
    caption = html_module.unescape(re.search(r'pm-teaching-figure__caption-text">(.*?)</span>', figure, re.S).group(1))
    credit = html_module.unescape(re.search(r'pm-teaching-figure__credit">(.*?)</span>', figure, re.S).group(1))
    if de:
        assert alt.startswith("Zwei schematische Seitenschnitte des Mundraums") and "[d]" in alt and "[ð]" in alt
        assert caption == ("Zwei Realisierungen des spanischen /d/: Beim Verschlusslaut [d] wird der Luftstrom durch einen vollständigen Verschluss kurz unterbrochen. "
                           "Beim Approximanten [ð] nähert sich die Zunge den oberen Zähnen nur an; die Luft kann weiterströmen.")
        assert credit == "Illustration: Felix Tacke (Konzept und Prompting), KI-generiert · Pronunciation Matters (2026)"
    else:
        assert alt.startswith("Two schematic cross-sections of the oral cavity") and "[d]" in alt and "[ð]" in alt
        assert caption.startswith("Two realisations of Spanish /d/:") and "approximant [ð]" in caption
        assert credit == "Illustration: Felix Tacke (concept and prompting), AI-generated · Pronunciation Matters (2026)"
    assert client.get(f"{src}.webp").mimetype == "image/webp" and client.get(f"{src}.png").status_code == 200
    # IPA of the explanation; con agua is described as g between [a] and the glide [w], not as an ordinary vowel-vowel position
    for fragment in ("[ˈbi.ða]", "[ˈbi.da]", "[la.ˈβaɾ]", "[ˈa.ɣwa]", "[el.βe.βe.ˈðoɾ]", "[ˈteŋ.go]"):
        assert fragment in html, fragment
    assert ("dem Gleitlaut [w]" if de else "the glide [w]") in html
    # info box directly after el bebedor, with the agreed title and the rule of thumb; no second explanation of the contexts
    box = re.search(r'pm-admonition--context.*?</section>', html, re.S).group(0)
    assert html.index("el.βe.βe") < html.index(box[:60]) and html.count("pm-admonition--context") == 1
    box_text = html_module.unescape(re.sub(r"<[^>]+>", " ", box))
    assert ("Wann klingen b, d und g sonst noch weich?" if de else "When else do b, d and g sound soft?") in box_text
    for word in ("logro", "regla", "algo", "caldo", "tengo", "bebedor"):
        assert word in box_text, word
    assert "signo" not in html  # signo has g BEFORE the nasal, so it is no postnasal example (tengo is)
    assert ("Zwischen Vokalen werden b, d und g im Spanischen meist ohne vollständigen Verschluss ausgesprochen" if de
            else "between vowels, b, d and g in Spanish are mostly pronounced without a complete closure") in box_text
    prompts = re.findall(r'class="pm-teaching-impulses__item-title">([^<]+)<', html)
    assert prompts == (["Erst hören, dann erklären", "Verschluss und Annäherung erproben", "Das Muster übertragen"] if de
                       else ["Listen first, explain later", "Try out closure and approximation", "Transfer the pattern"])
    assert "<em>el bebedor</em>" in html.split("pm-teaching-impulses__item-title")[-1]
    # the two sibling pages are linked in the Vertiefung box only, not in the running text
    rest = html.split('<ul class="pm-teaching-further-reading__list">')
    assert f'href="/{lang}/teaching/spanish/b-or-v"' in rest[1] and f'href="/{lang}/teaching/spanish/soft-spanish-hard-german"' in rest[1]
    assert f'href="/{lang}/teaching/spanish/b-or-v"' not in rest[0].split('<main')[-1] and f'href="/{lang}/teaching/spanish/soft-spanish-hard-german"' not in rest[0].split('<main')[-1]
    assert re.findall(r'href="(https://linguistik\.hispanistica\.com/[^"]+)"', rest[1]) == [
        "https://linguistik.hispanistica.com/aussprache/#kontextabhangige-mal-so-mal-so-laute", "https://linguistik.hispanistica.com/fehlerlinguistik/#transfer-aus-der-erstsprache"]


@pytest.mark.parametrize("lang", ["de", "en"])
def test_b_d_g_authorship_citation_and_slug(client, lang: str) -> None:
    html = _html(client, lang, "soft-consonants-b-d-g")
    title = "b, d und g: Zu hart ausgesprochen?" if lang == "de" else "b, d and g: Pronounced too hard?"
    quote_open, quote_close = ("„", "“") if lang == "de" else ("“", "”")
    assert f"Tacke, Felix (2026). {quote_open}{title}{quote_close}. In: Felix Tacke" in html and "Goás Pérez" not in html
    assert f"https://pronunciation-matters.de/{lang}/teaching/spanish/soft-consonants-b-d-g" in html


def test_b_d_g_curation_is_released_traceable_and_the_diagram_master_is_kept() -> None:
    import teaching_images as images

    data = slots.load_slots()
    comparisons = {c["id"]: c for c in data["comparisons"] if c["topic"] == "soft-consonants-b-d-g"}
    assert list(comparisons) == ["p5-vida", "p5-lavar", "p5-agua", "p5-bebedor"]
    picked = {cid: {r["slot"]: (r["session_id"], r["item"]["id"]) for r in c["recordings"]} for cid, c in comparisons.items() if cid in ("p5-vida", "p5-lavar")}
    # lavar: a Spanish (not Chilean) reference; the learner recording of the earlier version is kept
    assert picked == {
        "p5-vida": {"ref": ("ES-N-0004-2026-S01", "wl_045"), "learner": ("ES-L-0007-2026-S01", "wl_045")},
        "p5-lavar": {"ref": ("ES-N-0001-2026-S01", "wl_009"), "learner": ("ES-L-0006-2026-S01", "wl_009")},
    }
    assert not {s for c in picked.values() for s, _i in c.values()} & set(slots.EXCLUDED_SESSIONS) and "ES-N-0005-2026-S01" not in {s for c in picked.values() for s, _i in c.values()}
    # con agua and el bebedor are the MAR.ELE pairs: copied byte for byte, provenance and the textbook transcriptions documented
    expected = {"p5-agua": ("agua_l1.mp3", "agua_ele.mp3", "[ko.ˈna.ɣwa]", "[kon.ˈa.gwa]"), "p5-bebedor": ("bebedor_l1.mp3", "bebedor_ele.mp3", "[el.βe.βe.ˈðoɾ]", "[el.be.be.ˈdoɐ]")}
    for cid, (ref_file, learner_file, ref_ipa, learner_ipa) in expected.items():
        by_slot = {r["slot"]: r for r in comparisons[cid]["recordings"]}
        assert by_slot["ref"]["category"] == "reference" and by_slot["ref"]["origin"]["source_file"].endswith(f"marele/{ref_file}") and by_slot["ref"]["origin"]["transcription"] == ref_ipa
        assert by_slot["learner"]["category"] == "learner" and by_slot["learner"]["origin"]["source_file"].endswith(f"marele/{learner_file}") and by_slot["learner"]["origin"]["transcription"] == learner_ipa
        for recording in by_slot.values():
            assert recording["origin"]["corpus"] == "MAR.ELE" and "session_id" not in recording
            assert recording["sha256"] == slots.sha256_of(slots.media_path("soft-consonants-b-d-g", recording["file"]))
    reserves = [r for r in data["reserves"] if r["topic"] == "soft-consonants-b-d-g"]
    assert {r["learner"] for r in reserves} == {"ES-L-0020-2026-S01", "ES-L-0018-2026-S01", "ES-L-0010-2026-S01", "ES-L-0017-2026-S01"}
    assert not any(r["id"].startswith("p5-logro") for r in reserves) and all(r["reference"] != "ES-N-0005-2026-S01" for r in reserves if r["id"].startswith("p5-lavar"))
    media = TOPIC_DIR / "soft-consonants-b-d-g" / "media"
    assert sorted(path.name for path in (media / "audio" / "corpus").glob("*.mp3")) == ["p5-lavar-learner.mp3", "p5-lavar-ref.mp3", "p5-vida-learner.mp3", "p5-vida-ref.mp3"]
    assert sorted(path.name for path in (media / "audio" / "marele").glob("*.mp3")) == ["agua-learner.mp3", "agua-ref.mp3", "bebedor-learner.mp3", "bebedor-ref.mp3"]
    # the diagram master is kept untouched next to its WebP derivative (declared with hashes); no working copy is left in the repository root
    master = media / "images" / "dental-stop-approximant.png"
    assert images.sha256_of(master) == "fc477f9f74c128fdc4674231200fdfc1bc3788e329a8ab461d9edd12457916ae" and images.png_size(master) == (1448, 1086)
    assert images.check(images.load_manifest()) == [] and master.with_suffix(".webp").stat().st_size < master.stat().st_size / 10
    assert not list(REPO_ROOT.glob("Aussprache-Diagramm*"))


def test_hubs_list_all_topics_in_the_requested_order() -> None:
    for lang in ("de", "en"):
        hub = yaml.safe_load((TOPIC_DIR / "hubs" / f"{lang}.yaml").read_text(encoding="utf-8"))
        assert [g["topics"] for g in hub["groups"]] == [
            ["which-pronunciation", "soft-spanish-hard-german"],
            ["europe-sounds-different", "b-or-v", "soft-consonants-b-d-g", "r", "r-am-silbenende"],  # accent-changes-everything: draft, not listed until released
        ]


def test_slot_registry_is_consistent_with_media_and_pages() -> None:
    data = slots.load_slots()
    assert slots.check(data) == []
    declared = {(c["topic"], r["file"]) for c, r in slots.iter_recordings(data)}
    on_disk = {(path.parents[3].name, f"{path.parent.name}/{path.name}") for kind in ("corpus", "marele") for path in TOPIC_DIR.glob(f"*/media/audio/{kind}/*.mp3")}
    assert declared == on_disk and len(declared) == 57
    for comparison, recording in slots.iter_recordings(data):
        assert recording["category"] in ("reference", "learner")
        if not slots.is_external(recording):
            assert recording["session_id"].startswith(slots.SESSION_PREFIX[recording["category"]])


def test_slot_sources_are_released_sessions_when_the_local_runtime_is_present() -> None:
    sessions_root = REPO_ROOT / "data" / "sessions"
    if not slots.runtime_available(sessions_root):
        pytest.skip("local research runtime not present")
    assert slots.check(slots.load_slots(), sessions_root) == []


# --- "Europa klingt auf Spanisch anders" (europe-sounds-different): vowels and diphthongs -------------------------------------

EUROPE = "europe-sounds-different"


@pytest.mark.parametrize("lang", ["de", "en"])
def test_europe_page_follows_the_agreed_dramaturgy(client, lang: str) -> None:
    html = _html(client, lang, EUROPE)
    de = lang == "de"
    headings = re.findall(r'<h2 [^>]*class="pm-teaching-section-heading__title">([^<]*)</h2>', html)
    assert headings == (["Fünf Vokale – nicht ganz wie im Deutschen", "Wenn aus einem Diphthong zwei Silben werden", "Impulse für den Unterricht"] if de
                        else ["Five vowels – not quite as in German", "When a diphthong turns into two syllables", "Classroom prompts"])
    # five listening cards in the agreed order; the first follows the short introduction directly and is the only one with a solution
    prefix = "Hörvergleich" if de else "Listening comparison"
    titles = re.findall(r'<h3 class="promat-content-block__title pm-panel__title">(.*?)</h3>', html)
    assert titles[:5] == [f"{prefix}: <em>{w}</em>" for w in ("Europa", "deuda")] + [f"{prefix}: <em>mismo</em> – <em>álbum</em>"] + [f"{prefix}: <em>{w}</em>" for w in ("sueño", "viuda")]
    assert html.count("pm-teaching-block--audio-contrast") == 5 and html.count('<details class="pm-teaching-solution">') == 1
    pos = {w: html.index(f"{prefix}: <em>{w}</em>") for w in ("Europa", "deuda", "sueño", "viuda")}
    pos["mismo"] = html.index(f"{prefix}: <em>mismo</em> – <em>álbum</em>")
    assert html.index("pm-teaching-block--audio-contrast") < html.index('<details class="pm-teaching-solution">') < pos["deuda"]
    assert pos["Europa"] < pos["deuda"] < html.index(headings[0]) < pos["mismo"] < html.index(headings[1]) < pos["sueño"] < pos["viuda"] < html.index(headings[2])
    chips = re.findall(r'pm-teaching-audio-contrast__transcript-text">(.*?)</span>', html)
    assert chips == ["<em>Europa</em>", "<em>deuda</em>", "<em>mismo</em> – <em>álbum</em>", "<em>sueño</em>", "<em>viuda</em>"]
    questions = [html_module.unescape(re.sub(r"<[^>]+>", "", q)).strip() for q in re.findall(r'class="audio-section-description">(.*?)</p>', html, re.S)]
    assert questions == ([
        "Wie klingt die Buchstabenfolge eu in den beiden Aufnahmen?", "Wie wird die Vokalverbindung eu in deuda ausgesprochen?",
        "Wie unterscheiden sich die Vokale i und u in den beiden Aufnahmen?", "Wie viele Silben sind in den beiden Aufnahmen zu hören?",
        "Bleibt die Vokalfolge iu innerhalb einer Silbe?"] if de else [
        "How does the letter sequence eu sound in the two recordings?", "How is the vowel sequence eu pronounced in deuda?",
        "How do the vowels i and u differ in the two recordings?", "How many syllables can be heard in the two recordings?",
        "Does the vowel sequence iu stay within one syllable?"])
    ref, learner = ("Referenzsprecher:in", "Lernende:r") if de else ("Reference speaker", "Learner")
    assert re.findall(r'pm-teaching-audio-contrast__example-title">([^<]+)<', html) == [ref, learner] * 5
    country = ("Spanien", "Chile", "Deutsch") if de else ("Spain", "Chile", "German")
    assert re.findall(r'pm-teaching-audio-contrast__example-subtitle">([^<]+)<', html) == [
        f"{country[0]} · W80", f"L1 {country[2]} · W80", f"{country[0]} · W22", f"L1 {country[2]} · W22", "MAR.ELE", "MAR.ELE",
        f"{country[0]} · W40", f"L1 {country[2]} · W40", f"{country[0]} · W3", f"L1 {country[2]} · W3"]
    # the combined card: exactly two players, both marked as two single words spliced one after the other (never one connected utterance)
    card = html[pos["mismo"]:pos["sueño"]]  # from the card title to the next card (the explanation text sits inside this stretch)
    assert sorted(set(re.findall(r'<source src="([^"]+)"', card))) == [f"/teaching-media/spanish/{EUROPE}/audio/marele/p7-mismo-album-{who}.mp3" for who in ("learner", "ref")]
    note = "Zwei Einzelwörter, hintereinander montiert" if de else "Two single words, spliced one after the other"
    assert card.count(note) == 2
    # phonetic statements of the explanation text
    for fragment in ("[ɔɪ̯]", "[eu̯ˈɾopa]", "[ˈdeu̯ða]", "⟨eu⟩", "[iː]", "[ɪ]", "[ʊ]", "[uː]", "[ˈsweɲo]", "[ˈbjuða]", "fuego", "fu-e-go", "fue-go", "viu-da"):
        assert fragment in html, fragment
    assert ("bieten" in html and "Album" in html) and ("das mit [ʊ] gesprochen wird" in html if de else "which is pronounced with [ʊ]" in html)
    # nothing general, nothing excluded: no overview box, no generic rubric, no graphic, no discarded candidate words
    for gone in ("Auf einen Blick", "At a glance", "Hören und entdecken", "Listen and discover", "pm-teaching-figure", "pm-admonition--tip", "ciudad", "cuidado", "tierra", "buscó", "centro", "pastel", "Vokaltrapez", "vowel chart"):
        assert gone not in html, gone
    blocks = _blocks(EUROPE, lang)
    assert [b["type"] for b in blocks[:3]] == ["topic_meta", "text", "audio_contrast"]
    assert len(re.findall(r"[.!?](?:\s|$)", blocks[1]["body"])) in (2, 3) and len(blocks[1]["body"]) < 420
    prompts = re.findall(r'class="pm-teaching-impulses__item-title">([^<]+)<', html)
    assert prompts == (["Vertraute Schreibungen vergleichen", "Vokalqualität bewusst machen", "Diphthonge als eine Silbe sprechen"] if de
                       else ["Compare familiar spellings", "Make vowel quality conscious", "Say diphthongs as one syllable"])
    items = re.findall(r'pm-teaching-further-reading__item-title">([^<]+)<', html)
    assert items == (["Aussprache im digitalen Lehrbuch", "Orthographie im digitalen Lehrbuch", "Weiches Spanisch, hartes Deutsch"] if de
                     else ["Pronunciation in the digital textbook", "Orthography in the digital textbook", "Soft Spanish, hard German"])
    for href in ("https://linguistik.hispanistica.com/aussprache/#laute-des-spanischen-herausforderungen", "https://linguistik.hispanistica.com/orthographie/#vokale",
                 f'href="/{lang}/teaching/spanish/soft-spanish-hard-german"'):
        assert href in html, href
    assert client.get(f"/{lang}/teaching/spanish/soft-spanish-hard-german").status_code == 200


@pytest.mark.parametrize("lang", ["de", "en"])
def test_europe_page_title_teaser_citation_and_authorship(client, lang: str) -> None:
    html = _html(client, lang, EUROPE)
    title = "Europa klingt auf Spanisch anders" if lang == "de" else "Europe sounds different in Spanish"
    teaser = ("Wie vertraute Schreibungen und Lautmuster die spanische Aussprache beeinflussen." if lang == "de"
              else "How familiar spellings and sound patterns influence pronunciation in Spanish.")
    assert teaser in html and html.count("<h1") == 1 and title in html_module.unescape(re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S).group(1))
    quote_open, quote_close = ("„", "“") if lang == "de" else ("“", "”")
    assert f"Tacke, Felix (2026). {quote_open}{title}{quote_close}. In: Felix Tacke" in html and "Goás Pérez" not in html
    assert f"https://pronunciation-matters.de/{lang}/teaching/spanish/{EUROPE}" in html
    assert ("Europa" if lang == "de" else "Europe") in title  # the title uses the word Europe as the vivid entry in both languages


def test_europe_curation_is_released_traceable_and_the_montage_is_declared() -> None:
    import re as re_module

    data = slots.load_slots()
    comparisons = {c["id"]: c for c in data["comparisons"] if c["topic"] == EUROPE}
    assert list(comparisons) == ["p7-europa", "p7-deuda", "p7-mismo-album", "p7-sueno", "p7-viuda"]
    n1, n2 = "ES-N-0001-2026-S01", "ES-N-0002-2026-S01"
    l10, l21 = "ES-L-0010-2026-S01", "ES-L-0021-2026-S01"
    picked = {cid: [(r["slot"], r["category"], r.get("session_id")) for r in c["recordings"]] for cid, c in comparisons.items()}
    assert picked == {
        "p7-europa": [("ref", "reference", n2), ("learner", "learner", l21)],
        "p7-deuda": [("ref", "reference", n2), ("learner", "learner", l21)],  # same pair as Europa: the second case of the same phenomenon
        "p7-mismo-album": [("ref", "reference", None), ("learner", "learner", None)],  # MAR.ELE single-word items, no ProMat session
        "p7-sueno": [("ref", "reference", n1), ("learner", "learner", l10)],
        "p7-viuda": [("ref", "reference", n1), ("learner", "learner", l10)],
    }
    assert not {s for recs in picked.values() for _slot, _cat, s in recs} & set(slots.EXCLUDED_SESSIONS)
    items = {cid: [r["item"]["id"] for r in c["recordings"]] for cid, c in comparisons.items() if cid != "p7-mismo-album"}
    assert items == {"p7-europa": ["wl_080"] * 2, "p7-deuda": ["wl_022"] * 2, "p7-sueno": ["wl_040"] * 2, "p7-viuda": ["wl_003"] * 2}
    # discarded candidate words are not part of the page's recordings
    assert not {c["target"] for c in comparisons.values()} & {"ciudad", "cuidado", "tierra", "buscó", "centro", "pastel"}
    # the montage: two single-word MAR.ELE items per speaker, in the order mismo, álbum, with a short declared pause; originals untouched (hashes), tool recorded
    sources = {"ref": ["items/inf-L1-ES_es_040_mismo.mp3", "items/inf-L1-ES_es_049_álbum.mp3"], "learner": ["items/inf-019_040_mismo.mp3", "items/inf-019_049_álbum.mp3"]}
    for recording in comparisons["p7-mismo-album"]["recordings"]:
        assert recording["origin"] == {"corpus": "MAR.ELE"} and "item" not in recording and "crop" not in recording
        assert [p["source_file"] for p in recording["parts"]] == sources[recording["slot"]]
        assert [p["target_tokens"] for p in recording["parts"]] == [["mismo"], ["álbum"]]
        assert recording["join"]["pause_ms"] == 300 and recording["join"]["tool"].startswith("ffmpeg")
        for part in recording["parts"]:
            crop = part["crop"]
            assert 0 < crop["start_ms"] < crop["end_ms"] and crop["fade_in_ms"] >= 10 and crop["fade_out_ms"] >= 15
            assert re_module.fullmatch(r"[0-9a-f]{64}", part["source_sha256"]) and part["source_sha256"] != recording["sha256"]
    # the page does not present it as one utterance; the clips are short two-word montages, not full sentences
    media = TOPIC_DIR / EUROPE / "media" / "audio"
    for name, low, high in (("p7-mismo-album-ref", 1400, 1900), ("p7-mismo-album-learner", 1500, 2000)):
        size = (media / "marele" / f"{name}.mp3").stat().st_size
        assert low * 20 < size < high * 20  # 160 kbit/s = 20 bytes per ms
    declared = sorted(r["file"].split("/")[1] for c in comparisons.values() for r in c["recordings"] if r["file"].startswith("corpus/"))
    assert sorted(path.name for path in (media / "corpus").glob("*.mp3")) == declared and len(declared) == 8
    assert sorted(path.name for path in (media / "marele").glob("*.mp3")) == ["p7-mismo-album-learner.mp3", "p7-mismo-album-ref.mp3"]
    reserves = {r["id"]: r for r in data["reserves"] if r["topic"] == EUROPE}
    assert sorted(reserves) == sorted(["p7-europa-reserve-0008", "p7-deuda-reserve-0008", "p7-mismo-reserve-0004", "p7-album-reserve-0004", "p7-mismo-reserve-0019",
                                       "p7-album-reserve-0019", "p7-sueno-reserve-0015", "p7-viuda-reserve-0017"])
    assert not {r["learner"] for r in reserves.values()} & set(slots.EXCLUDED_SESSIONS)


def test_montage_declaration_rules_are_enforced() -> None:
    import copy

    data = slots.load_slots()
    assert slots.check(data) == []

    def broken(mutate) -> list[str]:
        candidate = copy.deepcopy(data)
        recording = next(r for _c, r in slots.iter_recordings(candidate) if r.get("parts"))
        mutate(recording)
        return slots.check(candidate)

    # external montage (MAR.ELE)
    assert any("montage needs" in p for p in broken(lambda r: r["join"].pop("pause_ms")))
    assert any("montage needs" in p for p in broken(lambda r: r.update(parts=r["parts"][:1])))
    assert any("every part of a montage needs a crop" in p for p in broken(lambda r: r["parts"][1].pop("crop")))
    assert any("source_sha256" in p for p in broken(lambda r: r["parts"][0].update(source_sha256="")))
    assert any("source_file" in p for p in broken(lambda r: r["parts"][0].pop("source_file")))
    assert any("origin.corpus" in p for p in broken(lambda r: r["origin"].update(corpus="")))
    assert any("sha256 differs" in p for p in broken(lambda r: r.update(sha256="0" * 64)))

    # session montage (ProMat corpus items of ONE session): the same rules apply to a declaration made from corpus items
    def as_session_montage(candidate) -> dict:
        recording = next(r for c in candidate["comparisons"] if c["id"] == "p7-europa" for r in c["recordings"] if r["slot"] == "learner")
        crop, item, sha = {"start_ms": 100, "end_ms": 900, "fade_in_ms": 15, "fade_out_ms": 25}, recording.pop("item"), recording["sha256"]
        recording["parts"] = [{"item": item, "target_tokens": ["europa"], "crop": dict(crop), "source_sha256": sha},
                              {"item": {"task": "wordlist", "id": "wl_022"}, "target_tokens": ["deuda"], "crop": dict(crop), "source_sha256": sha}]
        recording["join"] = {"pause_ms": 300, "tool": "ffmpeg"}
        return recording

    candidate = copy.deepcopy(data)
    as_session_montage(candidate)
    assert not any("montage needs" in p for p in slots.check(candidate))
    candidate = copy.deepcopy(data)
    as_session_montage(candidate)["join"].pop("pause_ms")
    assert any("montage needs" in p for p in slots.check(candidate))
    candidate = copy.deepcopy(data)
    as_session_montage(candidate)["parts"][0]["item"] = {"task": "wordlist", "id": "x"}
    assert any("invalid corpus item" in p for p in slots.check(candidate))


def test_montage_is_reproducible_from_the_declared_cut_points_and_pause(tmp_path) -> None:
    import os
    import shutil as shutil_module
    import subprocess

    marele_root = Path(os.environ.get("PROMAT_MARELE_ROOT") or r"C:\dev_backup\marele-webapp")
    if shutil_module.which("ffmpeg") is None or not (marele_root / "items").is_dir():
        pytest.skip("ffmpeg or the MAR.ELE backup is not present")
    data = slots.load_slots()
    montages = [(c, r) for c, r in slots.iter_recordings(data) if r.get("parts")]
    assert len(montages) == 2
    for _comparison, recording in montages:
        origins = [marele_root / part["source_file"] for part in recording["parts"]]
        assert [slots.sha256_of(o) for o in origins] == [p["source_sha256"] for p in recording["parts"]]  # the MAR.ELE items are untouched
        target = tmp_path / Path(recording["file"]).name
        slots.derive_montage(origins, target, recording["parts"], recording["join"])
        if recording["join"]["tool"] == f"ffmpeg {slots.ffmpeg_version()}":
            assert slots.sha256_of(target) == recording["sha256"], recording["file"]  # bit-identical with the same tool version
        if shutil_module.which("ffprobe"):
            seconds = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(target)], capture_output=True, text=True, check=True).stdout)
            expected = (sum(p["crop"]["end_ms"] - p["crop"]["start_ms"] for p in recording["parts"]) + recording["join"]["pause_ms"]) / 1000
            assert abs(seconds - expected) < 0.06  # words, then exactly the declared pause, nothing else


def test_session_montage_parts_are_checked_item_by_item_in_the_release_report() -> None:
    import copy

    sessions_root = REPO_ROOT / "data" / "sessions"
    if not slots.runtime_available(sessions_root):
        pytest.skip("local research runtime not present")
    data = copy.deepcopy(slots.load_slots())
    recording = next(r for c in data["comparisons"] if c["id"] == "p7-europa" for r in c["recordings"] if r["slot"] == "learner")
    crop, item = {"start_ms": 100, "end_ms": 900, "fade_in_ms": 15, "fade_out_ms": 25}, recording.pop("item")
    recording["parts"] = [{"item": item, "target_tokens": ["europa"], "crop": crop}, {"item": {"task": "wordlist", "id": "wl_022"}, "target_tokens": ["deuda"], "crop": crop}]
    rows = [r for r in slots.release_rows(data, sessions_root) if r["use"] == "p7-europa · integrated" and r["role"] == "learner"]
    assert sorted((r["session"], r["item"]) for r in rows) == [("ES-L-0021-2026-S01", "wl_022"), ("ES-L-0021-2026-S01", "wl_080")]
    assert all(r["result"] == "OK" and r["consent"] == "yes" and r["review"] == "False" for r in rows)
    # the MAR.ELE montage has no ProMat session and therefore no ProMat release row
    assert not [r for r in slots.release_rows(slots.load_slots(), sessions_root) if r["use"].startswith("p7-mismo-album")]


SEVEN_SPANISH_PAGES = ("which-pronunciation", "soft-spanish-hard-german", "europe-sounds-different", "b-or-v", "soft-consonants-b-d-g", "r", "r-am-silbenende")


@pytest.mark.parametrize("lang", ["de", "en"])
def test_listening_cards_follow_the_shared_editorial_standard(lang: str) -> None:
    """Neutral card titles, no imperatives, no result in the title; a card may carry a question OR an explanatory sentence (no question is required)."""
    prefix = "Hörvergleich: " if lang == "de" else "Listening comparison: "
    imperatives = ("Achte auf", "Achtet auf", "Hör genau", "Hört genau", "Versuche", "Versucht", "Listen for", "Listen carefully", "Pay attention", "Try to", "Notice")
    forbidden_title_fragments = ("vs.", "Mit und ohne", "With and without", "genauso korrekt", "just as correct")
    for slug in SEVEN_SPANISH_PAGES:
        cards = [b for b in _blocks(slug, lang) if b["type"] == "audio_contrast"]
        assert cards, slug
        for card in cards:
            title, chip = str(card["title"]), str(card.get("transcript") or "")
            assert title.startswith(prefix), (slug, title)
            assert not any(fragment in title for fragment in forbidden_title_fragments), (slug, title)
            if "¿" not in chip:  # a card whose chip is a whole sentence names only its target words in the title (los otros)
                assert title[len(prefix):].replace("*", "") == chip.replace("*", ""), (slug, title, chip)
            lead = str(card.get("lead") or "")
            assert not lead.startswith(imperatives), (slug, lead)
            assert not any(word in lead for word in imperatives), (slug, lead)
        # nothing on the page addresses pupils directly
        for block in _blocks(slug, lang):
            if block["type"] == "text":
                assert not str(block["body"]).lstrip().startswith(imperatives), slug


def test_listening_cards_have_identical_function_and_audio_in_both_languages() -> None:
    for slug in SEVEN_SPANISH_PAGES:
        de_cards = [b for b in _blocks(slug, "de") if b["type"] == "audio_contrast"]
        en_cards = [b for b in _blocks(slug, "en") if b["type"] == "audio_contrast"]
        assert len(de_cards) == len(en_cards), slug
        for de_card, en_card in zip(de_cards, en_cards):
            assert de_card.get("transcript") == en_card.get("transcript"), slug
            assert [e["audio"] for e in de_card["examples"]] == [e["audio"] for e in en_card["examples"]], slug
            assert bool(de_card.get("lead")) == bool(en_card.get("lead")), slug  # question/explanation on both or neither
            assert str(de_card.get("lead", "")).endswith("?") == str(en_card.get("lead", "")).endswith("?"), (slug, de_card.get("lead"))


def test_spanish_topic_teasers_are_single_sentences_that_do_not_repeat_the_title() -> None:
    import re as re_module

    for slug in SEVEN_SPANISH_PAGES:
        for lang in ("de", "en"):
            meta = yaml.safe_load((TOPIC_DIR / slug / f"{lang}.yaml").read_text(encoding="utf-8"))
            summary = str(meta["summary"])
            assert len(re_module.findall(r"[.!?](?:\s|$)", summary)) <= 1, (slug, lang, summary)
            assert summary.rstrip(".?!").lower() != str(meta["title"]).rstrip(".?!").lower(), (slug, lang)
    expected = {
        ("europe-sounds-different", "de"): "Wie vertraute Schreibungen und Lautmuster die spanische Aussprache beeinflussen.",
        ("r", "de"): "Zwei spanische r-Laute – und warum das deutsche r anders klingt.",
        ("r-am-silbenende", "de"): "Warum das deutsche r häufig zum Vokal wird, das spanische aber konsonantisch bleibt.",
    }
    for (slug, lang), teaser in expected.items():
        meta = yaml.safe_load((TOPIC_DIR / slug / f"{lang}.yaml").read_text(encoding="utf-8"))
        assert meta["summary"] == teaser == meta["description"]
    assert "im Spanischen meist nicht" not in yaml.safe_load((TOPIC_DIR / "r-am-silbenende" / "de.yaml").read_text(encoding="utf-8"))["summary"]


def test_unreleased_accent_topic_is_hidden_from_hub_and_not_served(client) -> None:
    """The accent page is a draft: not in the hub files (a listed draft would show as a placeholder card), no page, no media; releasing it = remove `status: draft` and list it again."""
    for lang in ("de", "en"):
        source = yaml.safe_load((TOPIC_DIR / UNRELEASED / f"{lang}.yaml").read_text(encoding="utf-8"))
        assert source["status"] == "draft"
        hub = client.get(f"/{lang}/teaching/spanish").get_data(as_text=True)
        assert f"/{lang}/teaching/spanish/{UNRELEASED}" not in hub
        assert client.get(f"/{lang}/teaching/spanish/{UNRELEASED}").status_code == 404
    media = next((TOPIC_DIR / UNRELEASED / "media" / "audio").rglob("*.mp3"))
    assert client.get(f"/teaching-media/spanish/{UNRELEASED}/audio/{media.relative_to(TOPIC_DIR / UNRELEASED / 'media' / 'audio').as_posix()}").status_code == 404
