"""Teaching in four languages: the hubs of Spanish, English, French and German, and the announced placeholder pages.

A placeholder (``status: placeholder``) is a public topic page with title, teaser and the authorship "tba" only: listed
on its hub and counted on the language selection, but without blocks, dates, citation or structured data, and not
indexed (docs/spec/platform-data-files.md, availability rule).
"""

from __future__ import annotations

import html as html_module
import importlib.util
from pathlib import Path
import re
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_teaching_content_editions import _app, _edition_links  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
TEACHING = REPO_ROOT / "content" / "teaching"

HUB_TITLES = {
    "spanish": ("Spanische Aussprache verstehen", "Understanding Spanish Pronunciation"),
    "english": ("Englische Aussprache verstehen", "Understanding English Pronunciation"),
    "french": ("Französische Aussprache verstehen", "Understanding French Pronunciation"),
    "german": ("Deutsche Aussprache verstehen", "Understanding German Pronunciation"),
}
SPANISH = ["which-pronunciation", "soft-spanish-hard-german", "europe-sounds-different", "b-or-v", "soft-consonants-b-d-g", "r", "r-am-silbenende"]
NEW_TOPICS = {
    "english": {
        "which-english-pronunciation": ("Welches Englisch unterrichten?", "Which English to teach?"),
        "ship-or-sheep": ("Ship oder sheep? Wenn Vokale Wörter verändern", "Ship or sheep? When vowels change words"),
        "english-th": ("Das englische th: zwei Laute, viele Varianten", "The English th: two sounds, many variants"),
        "weak-forms-and-schwa": ("Warum kleine Wörter plötzlich anders klingen", "Why small words suddenly sound different"),
        "english-stress": ("Englisch betont anders", "Stress works differently in English"),
    },
    "french": {
        "nasal-vowels": ("Was die Nase mit französischen Vokalen zu tun hat", "What the nose has to do with French vowels"),
        "u-or-ou": ("u oder ou? Zwei Schreibungen, zwei Vokale", "u or ou? Two spellings, two vowels"),
        "liaison": ("Liaison: Wenn stumme Konsonanten hörbar werden", "Liaison: when silent consonants become audible"),
        "schwa": ("Das flüchtige e: Wo bleibt das Schwa?", "The fleeting e: where does the schwa go?"),
        "spelling-and-pronunciation": ("Französisch klingt anders, als es geschrieben wird", "French sounds different from how it is spelled"),
        "french-stress": ("Wo liegt die Betonung im Französischen?", "Where does the stress fall in French?"),
    },
    "german": {
        "miete-or-mitte": ("Miete oder Mitte? Wenn Vokale Wörter unterscheiden", "Miete or Mitte? When vowels tell words apart"),
        "ich-or-ach": ("Ich oder ach? Zwei Laute für ch", "Ich or ach? Two sounds for ch"),
        "final-devoicing": ("Rad oder Rat? Am Wortende wird es stimmlos", "Rad or Rat? Voiceless at the end of the word"),
        "german-stress": ("Was die Betonung im Deutschen verändert", "What stress changes in German"),
    },
}
START = {"english": "which-english-pronunciation", "french": "nasal-vowels", "german": "miete-or-mitte"}


@pytest.fixture(scope="module")
def client():
    from app import teaching_content

    teaching_content.clear_teaching_content_caches()
    return _app().test_client()


def _get(client, url: str) -> str:
    response = client.get(url)
    assert response.status_code == 200, url
    return response.get_data(as_text=True)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", html_module.unescape(re.sub(r"<[^>]+>", " ", html)))


@pytest.mark.parametrize(("ui_lang", "unit"), [("de", "Themenseiten"), ("en", "topic pages")])
def test_language_selection_shows_four_active_languages_with_their_counts(client, ui_lang: str, unit: str) -> None:
    html = _get(client, f"/{ui_lang}/teaching")
    assert html.count("pm-teaching-language-row--available") == 4 and "pm-teaching-language-row--pending" not in html
    text = _text(html)
    labels = ("Spanisch", "Englisch", "Französisch", "Deutsch") if ui_lang == "de" else ("Spanish", "English", "French", "German")
    positions = [text.index(f"{label} {count} {unit}") for label, count in zip(labels, (7, 5, 6, 4))]
    assert positions == sorted(positions)  # order Spanish, English, French, German
    for slug in HUB_TITLES:
        assert f'href="/{ui_lang}/teaching/{slug}"' in html


@pytest.mark.parametrize("ui_lang", ["de", "en"])
@pytest.mark.parametrize("teaching_lang", list(HUB_TITLES))
def test_hub_titles_and_structure(client, teaching_lang: str, ui_lang: str) -> None:
    html = _get(client, f"/{ui_lang}/teaching/{teaching_lang}")
    title = HUB_TITLES[teaching_lang][ui_lang == "en"]
    assert re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S).group(1).strip() == title
    assert re.search(r"<title>([^<]*)</title>", html).group(1).startswith(title)
    groups = re.findall(r'class="pm-teaching-topic-group__title">([^<]+)<', html)
    assert groups == (["Zum Einstieg", "Aussprachephänomene entdecken"] if ui_lang == "de" else ["Getting started", "Exploring pronunciation features"])
    assert html.count('pm-teaching-topic-grid pm-teaching-topic-grid--compact') == 2  # the Spanish two-column grid
    cards = re.findall(rf'href="/{ui_lang}/teaching/{teaching_lang}/([a-z0-9-]+)"', html)
    if teaching_lang == "spanish":
        assert cards == SPANISH
    else:
        assert cards == list(NEW_TOPICS[teaching_lang]) and cards[0] == START[teaching_lang]
        first_group = html.split('id="teaching-group-2"')[0]
        assert re.findall(rf'href="/{ui_lang}/teaching/{teaching_lang}/([a-z0-9-]+)"', first_group) == [START[teaching_lang]]
        intro = _text(re.search(r'pm-teaching-overview__intro-text">(.*?)</p>', html, re.S).group(1))
        # the introductions describe the series; they do not promise listening examples that do not exist yet
        assert "entstehen derzeit" in intro or "currently being developed" in intro
        for promise in ("Hörbeispiele", "listening examples", "audio examples"):
            assert promise not in intro


def test_spanish_content_edition_hub_title() -> None:
    hub = yaml.safe_load((TEACHING / "spanish" / "hubs" / "es.yaml").read_text(encoding="utf-8"))
    assert hub["title"] == "Comprender la pronunciación del español"


@pytest.mark.parametrize("ui_lang", ["de", "en"])
@pytest.mark.parametrize(("teaching_lang", "slug"), [(lang, slug) for lang, topics in NEW_TOPICS.items() for slug in topics])
def test_placeholder_pages_show_title_teaser_and_tba_only(client, teaching_lang: str, slug: str, ui_lang: str) -> None:
    html = _get(client, f"/{ui_lang}/teaching/{teaching_lang}/{slug}")
    source = yaml.safe_load((TEACHING / teaching_lang / slug / f"{ui_lang}.yaml").read_text(encoding="utf-8"))
    assert source["title"] == NEW_TOPICS[teaching_lang][slug][ui_lang == "en"] and source["status"] == "placeholder"
    assert source["summary"] and source["blocks"] == [{"type": "topic_meta"}] and "metadata" not in source
    assert re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S).group(1).strip() == html_module.escape(source["title"], quote=False)
    meta = re.findall(r'pm-teaching-topic-meta__(?:label|value)">([^<]*)<', html)
    assert meta == (["Autor:innen:", "tba"] if ui_lang == "de" else ["Authors:", "tba"])  # no dates
    # nothing after the header: no sections, no empty containers, no bottom navigation, no citation
    for absent in ("pm-teaching-topic-sections", "pm-teaching-block-stack", "pm-teaching-topic-bottom-nav", "data-copy-text", "pm-admonition--citation"):
        assert absent not in html, absent
    head = html.split("</head>")[0]
    assert '<meta name="robots" content="noindex">' in head and 'rel="canonical"' not in head and "ld+json" not in head and "citation_title" not in head
    back = re.search(r'pm-content-header__back" aria-label="([^"]+)">.*?pm-back-link__pill" href="([^"]+)"', html, re.S)
    assert back.groups() == (("Alle Themen" if ui_lang == "de" else "All topics"), f"/{ui_lang}/teaching/{teaching_lang}")
    assert _edition_links(html) == []  # no language link without a translation


@pytest.mark.parametrize("ui_lang", ["de", "en"])
@pytest.mark.parametrize("slug", SPANISH)
def test_every_spanish_topic_page_returns_to_all_topics(client, slug: str, ui_lang: str) -> None:
    label = "Alle Themen" if ui_lang == "de" else "All topics"
    html = _get(client, f"/{ui_lang}/teaching/spanish/{slug}")
    assert re.findall(r'pm-nav-pill__label">([^<]+)<', html) == [label, label]  # header and bottom
    assert f'href="/{ui_lang}/teaching/spanish"' in html
    assert _edition_links(html) == [(f"/{ui_lang}/teaching/spanish/es/{slug}?from={ui_lang}", "es", "En español")]
    assert "data-copy-text" in html  # the written pages keep their citation
    # in the Spanish content edition the back link belongs to the navigation (UI language) and stays in the edition
    es = _get(client, f"/{ui_lang}/teaching/spanish/es/{slug}?from={ui_lang}")
    assert re.findall(r'pm-nav-pill__label">([^<]+)<', es) == [label, label]
    assert f'href="/{ui_lang}/teaching/spanish/es?from={ui_lang}"' in es


def test_old_french_scaffolds_with_german_slugs_are_gone(client) -> None:
    for slug in ("gleitlaute", "nasalvokale"):
        assert not (TEACHING / "french" / slug).exists()
        assert client.get(f"/de/teaching/french/{slug}").status_code == 404


@pytest.fixture
def validator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("validate_teaching_content_placeholders", REPO_ROOT / "scripts" / "validate_teaching_content.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.publication_module = module.load_publication_module()  # load from the real repository before re-rooting
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CONTENT_ROOT", tmp_path / "content" / "teaching")
    return module


def _placeholder(lang: str, other: str, extra: str = "") -> str:
    return f"resource_id: promat-teaching-xx-topic\nstatus: placeholder\ntitle: T {lang}\nsummary: S.\nequivalents:\n  {other}: topic\n{extra}blocks:\n- type: topic_meta\n"


def _validate(validator, files: dict[str, str]) -> str:
    root = validator.CONTENT_ROOT / "english"
    for relative, text in files.items():
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text(text, encoding="utf-8")
    errors: list[str] = []
    validator.validate_publication_front_matter(errors, validator.publication_module, "english", ["de", "en"], {})
    return "\n".join(errors)


def test_validator_accepts_a_clean_placeholder(validator) -> None:
    assert _validate(validator, {"topic/de.yaml": _placeholder("de", "en"), "topic/en.yaml": _placeholder("en", "de")}) == ""


def test_validator_rejects_placeholders_with_authors_dates_or_content(validator) -> None:
    bad = _placeholder("de", "en", "metadata:\n  creators:\n  - felix-tacke\n  created: 2026-10-27\n").replace(
        "blocks:\n- type: topic_meta\n", "blocks:\n- type: topic_meta\n- type: text\n  body: Filler.\n")
    errors = _validate(validator, {"topic/de.yaml": bad, "topic/en.yaml": _placeholder("en", "de")})
    for expected in ("a placeholder names no authors", "a placeholder carries no publication dates", "a placeholder has no content blocks yet (found text)"):
        assert expected in errors, expected
