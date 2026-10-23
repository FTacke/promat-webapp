"""English design article: verbatim integrity against the author's DOCX, corpus supplements, English-only routing.

The integrity tests compare the *rendered page* with the original manuscript
(docs/author-sources/english-design/kreyer-english-design-original.docx). The manuscript is not public and therefore not
in the repository (git-ignored, kept locally by the maintainer); the tests that need it are skipped without it, and CI
checks that the committed import names exactly the manuscript's SHA-256. The DOCX is read here with an independent
minimal OOXML reader, not with the importer, so an importer bug cannot hide itself. Every manuscript paragraph and table
cell carries `data-source` on the page; text is compared character by character (only runs of whitespace are collapsed,
because HTML collapses them too) and so is the character formatting (italic, bold, underline, superscript, subscript).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from flask import Flask, g

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app" / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app import register_context_processors  # noqa: E402
from app.i18n import PREFERRED_UI_LANGUAGE_COOKIE_NAME  # noqa: E402
from app.page_languages import PAGE_UI_LANGUAGES, available_page_path, page_ui_languages, unavailable_ui_language_target  # noqa: E402
from app.routes.auth import blueprint as auth_blueprint  # noqa: E402
from app.routes.public import blueprint as public_blueprint  # noqa: E402

DOCX = REPO_ROOT / "docs" / "author-sources" / "english-design" / "kreyer-english-design-original.docx"
DOCX_SHA256 = "af31cc6ec01ec21e8c13cefa9f5dbf3009503d0935ec8ec2f0f278869ae15a6d"
ARTICLE_JSON = REPO_ROOT / "content" / "research" / "english" / "design.json"
MATERIALS_JSON = REPO_ROOT / "content" / "research" / "english" / "design_materials.json"
EN_PATH = "/en/research/english/design"
DE_PATH = "/de/research/english/design"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
FORMAT_TAGS = {"em": "i", "strong": "b", "u": "u", "sup": "sup", "sub": "sub"}

#: Automatic Word numbering (not part of the paragraph text), as Word renders the manuscript (checked visually against
#: Word's own PDF export on 2026-10-23).
EXPECTED_NUMBERS = {"p7": "1.", "p14": "2.", "p24": "3.", "p35": "4.", "p38": "5.", "p9": "(1)", "p27": "(2)"}
#: Manuscript formatting that is deliberately not reproduced, with the reason.
FORMAT_EXCEPTIONS = {
    "p2": "The 'Abstract' label (Word character style 'Book Title', bold italic) is shown as the platform's article label.",
}


# --- independent DOCX reader --------------------------------------------------------------------------------------


def _docx_styles(archive: zipfile.ZipFile) -> dict[str, set[str]]:
    styles = ET.fromstring(archive.read("word/styles.xml"))
    formats: dict[str, set[str]] = {}
    for style in styles.findall(W + "style"):
        rpr = style.find(W + "rPr")
        found: set[str] = set()
        if rpr is not None:
            for tag in ("b", "i"):
                element = rpr.find(W + tag)
                if element is not None and element.get(W + "val") not in ("0", "false"):
                    found.add(tag)
        formats[style.get(W + "styleId")] = found
    return formats


def _docx_chars(paragraph: ET.Element, styles: dict[str, set[str]]) -> list[tuple[str, frozenset[str]]]:
    ppr = paragraph.find(W + "pPr")
    pstyle = ppr.find(W + "pStyle") if ppr is not None else None
    base = set(styles.get(pstyle.get(W + "val"), set())) if pstyle is not None else set()
    chars: list[tuple[str, frozenset[str]]] = []
    for run in paragraph.iter(W + "r"):
        fmt = set(base)
        rpr = run.find(W + "rPr")
        if rpr is not None:
            rstyle = rpr.find(W + "rStyle")
            if rstyle is not None:
                fmt |= styles.get(rstyle.get(W + "val"), set())
            for tag in ("b", "i", "u"):
                element = rpr.find(W + tag)
                if element is not None:
                    if element.get(W + "val") in ("0", "false", "none"):
                        fmt.discard(tag)
                    else:
                        fmt.add(tag)
            vert = rpr.find(W + "vertAlign")
            if vert is not None and vert.get(W + "val") in ("superscript", "subscript"):
                fmt.add("sup" if vert.get(W + "val") == "superscript" else "sub")
        for child in run:
            if child.tag == W + "t":
                chars.extend((ch, frozenset(fmt)) for ch in child.text or "")
            elif child.tag == W + "tab":
                chars.append(("\t", frozenset(fmt)))
    return chars


def read_docx() -> list[tuple[str, list[tuple[str, frozenset[str]]]]]:
    """(reference, characters) of every non-empty top-level paragraph and table cell, in document order."""
    if not DOCX.is_file():
        pytest.skip("the author's manuscript is kept locally only (docs/author-sources/ is git-ignored)")
    with zipfile.ZipFile(DOCX) as archive:
        styles = _docx_styles(archive)
        body = ET.fromstring(archive.read("word/document.xml")).find(W + "body")
    out: list[tuple[str, list[tuple[str, frozenset[str]]]]] = []
    p_index = t_index = 0
    for child in body:
        if child.tag == W + "p":
            chars = _docx_chars(child, styles)
            if "".join(ch for ch, _ in chars).strip():
                out.append((f"p{p_index}", chars))
            p_index += 1
        elif child.tag == W + "tbl":
            for r, row in enumerate(child.findall(W + "tr")):
                for c, cell in enumerate(row.findall(W + "tc")):
                    chars = [item for p in cell.findall(W + "p") for item in _docx_chars(p, styles)]
                    if "".join(ch for ch, _ in chars).strip():
                        out.append((f"t{t_index}r{r}c{c}", chars))
            t_index += 1
    return out


# --- rendered page reader -----------------------------------------------------------------------------------------


class _SourceCollector(HTMLParser):
    """Characters (with formatting) of every element carrying `data-source`, plus the automatic numbers."""

    VOID = {"br", "img", "input", "meta", "link", "hr", "col", "source", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str | None, bool]] = []  # tag, source ref, is-number element
        self.sources: dict[str, list[tuple[str, frozenset[str]]]] = {}
        self.order: list[str] = []
        self.numbers: dict[str, str] = {}
        self.duplicates: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        attributes = dict(attrs)
        ref = attributes.get("data-source")
        number_ref = attributes.get("data-source-number")
        if ref is not None and tag != "table":
            if ref in self.sources:
                self.duplicates.append(ref)
            self.sources[ref] = []
            self.order.append(ref)
        if number_ref is not None:
            self.numbers[number_ref] = ""
        self.stack.append((tag, ref if tag != "table" else None, number_ref))

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        while self.stack:
            open_tag, _, _ = self.stack.pop()
            if open_tag == tag:
                break

    def handle_data(self, data):
        number_ref = next((n for _, _, n in reversed(self.stack) if n), None)
        if number_ref is not None:
            self.numbers[number_ref] += data
            return
        ref = next((r for _, r, _ in reversed(self.stack) if r), None)
        if ref is None:
            return
        fmt = frozenset(FORMAT_TAGS[t] for t, _, _ in self.stack if t in FORMAT_TAGS)
        self.sources[ref].extend((ch, fmt) for ch in data)


def _normalized_text(chars: list[tuple[str, frozenset[str]]]) -> str:
    return re.sub(r"\s+", " ", "".join(ch for ch, _ in chars)).strip()


def _formats(chars: list[tuple[str, frozenset[str]]]) -> list[tuple[str, frozenset[str]]]:
    return [(ch, fmt) for ch, fmt in chars if not ch.isspace()]


# --- app ----------------------------------------------------------------------------------------------------------


@pytest.fixture
def app() -> Flask:
    app_root = REPO_ROOT / "app"
    flask_app = Flask(__name__, template_folder=str(app_root / "templates"), static_folder=str(app_root / "static"))
    flask_app.config["SERVER_NAME"] = "promat.test"
    register_context_processors(flask_app)

    @flask_app.before_request
    def _anonymous() -> None:
        g.user = None
        g.user_id = None
        g.role = None

    flask_app.register_blueprint(auth_blueprint)
    flask_app.register_blueprint(public_blueprint)
    return flask_app


@pytest.fixture
def page_html(app: Flask) -> str:
    response = app.test_client().get(EN_PATH)
    assert response.status_code == 200
    return response.get_data(as_text=True)


@pytest.fixture
def rendered(page_html: str) -> _SourceCollector:
    collector = _SourceCollector()
    collector.feed(page_html)
    return collector


# --- manuscript integrity -----------------------------------------------------------------------------------------


def test_the_committed_import_names_the_provided_manuscript() -> None:
    """Runs everywhere (also without the DOCX): the import was made from exactly the delivered manuscript."""
    generated = json.loads(ARTICLE_JSON.read_text(encoding="utf-8"))["_generated"]
    assert generated["source_sha256"] == DOCX_SHA256
    assert generated["source"] == DOCX.relative_to(REPO_ROOT).as_posix()


def test_the_manuscript_is_the_provided_original() -> None:
    if not DOCX.is_file():
        pytest.skip("the author's manuscript is kept locally only (docs/author-sources/ is git-ignored)")
    assert hashlib.sha256(DOCX.read_bytes()).hexdigest() == DOCX_SHA256


def test_every_manuscript_part_is_on_the_page_once_and_in_order(rendered: _SourceCollector) -> None:
    docx_refs = [ref for ref, _ in read_docx()]
    assert not rendered.duplicates
    assert rendered.order == docx_refs


def test_page_text_matches_the_manuscript_character_by_character(rendered: _SourceCollector) -> None:
    differences = []
    for ref, chars in read_docx():
        expected = _normalized_text(chars)
        actual = _normalized_text(rendered.sources.get(ref, []))
        if expected != actual:
            differences.append(f"{ref}:\n  docx: {expected!r}\n  page: {actual!r}")
    assert not differences, "\n".join(differences)


def test_page_keeps_the_manuscript_character_formatting(rendered: _SourceCollector) -> None:
    differences = []
    for ref, chars in read_docx():
        if ref in FORMAT_EXCEPTIONS:
            continue
        expected = _formats(chars)
        actual = _formats(rendered.sources.get(ref, []))
        if expected != actual:
            mismatch = next(i for i, (a, b) in enumerate(zip(expected, actual + [("", frozenset())] * len(expected))) if a != b)
            context = "".join(ch for ch, _ in expected[max(0, mismatch - 15) : mismatch + 15])
            differences.append(f"{ref} near {context!r}: docx {expected[mismatch]!r}, page {actual[mismatch] if mismatch < len(actual) else None!r}")
    assert not differences, "\n".join(differences)


def test_formatting_check_covers_italics_bold_underline_and_superscript(rendered: _SourceCollector) -> None:
    """Guard against a vacuous comparison: the manuscript really has these formats and the page reproduces them."""
    page_formats = {fmt for chars in rendered.sources.values() for _, fmts in chars for fmt in fmts}
    assert {"i", "b", "u", "sup"} <= page_formats


def test_automatic_chapter_and_example_numbers_are_kept(rendered: _SourceCollector) -> None:
    assert rendered.numbers == EXPECTED_NUMBERS


def test_ipa_and_typographic_characters_survive(page_html: str) -> None:
    for fragment in ("[ɜː]", "[øː]", "[ɐ]", "[ɹ]", "[ɻ]", "[ʁ]", "[ɫ]", "[ŋ]", "[ɪnwaɪtɪd]", "[ʃǝʊ<sup>w</sup>ʌs]", "ɪndiə<strong>ɹ</strong>ɔː<strong>ɹ</strong>eɪʒə", "‘The Young Rat’", "father’s", "– a pup was chasing", "<sup>4</sup>2018 [2003]"):
        assert fragment in page_html, fragment


def test_imported_article_is_a_fresh_import_of_the_manuscript(tmp_path: Path) -> None:
    """content/research/english/design.json must not be hand-edited: re-importing the DOCX reproduces it exactly."""
    import import_design_article_docx

    if not DOCX.is_file():
        pytest.skip("the author's manuscript is kept locally only (docs/author-sources/ is git-ignored)")
    assert import_design_article_docx.main(["--docx", str(DOCX), "--out", str(ARTICLE_JSON), "--check"]) == 0


def test_table_groups_follow_the_manuscript(page_html: str) -> None:
    groups = re.findall(r'class="pm-article-grouped-table__group-heading" data-source="([^"]+)">([^<]*)<', page_html)
    assert [text for _, text in groups] == [
        "The sound inventory - consontants",
        "The sound inventory - vowels",
        "Allophonic contrasts",
        "Phenomena of connected speech and phonotactics",
    ]
    article = json.loads(ARTICLE_JSON.read_text(encoding="utf-8"))
    table = next(b for s in article["sections"] for b in s.get("blocks", []) if b["type"] == "grouped_table")
    # Rows 10 and 15 of the Word table are empty spacer rows; every other row is on the page.
    assert table["skipped_empty_rows"] == [10, 15]
    assert [len(group["rows"]) for group in table["groups"]] == [5, 3, 3, 4]


# --- corpus supplements -------------------------------------------------------------------------------------------


def _expandable(page_html: str, element_id: str) -> str:
    section = re.search(rf'<section\s+class="pm-expandable"\s+aria-labelledby="{element_id}-title".*?</section>', page_html, re.S)
    assert section is not None, element_id
    return section.group(0)


def _markup_skeleton(fragment: str) -> list[str]:
    """Tag and class sequence of a fragment, without texts, ids and data attributes."""
    return [f"{tag}.{classes}" for tag, classes in re.findall(r'<([a-z0-9]+)(?:\s[^>]*?class="([^"]*)")?[^>]*>', fragment)]


def test_wordlist_shows_all_catalog_items_unchanged(page_html: str) -> None:
    from html import unescape

    items = re.findall(
        r'data-item-id="([^"]+)">\s*<span class="pm-expandable__label">([^<]*)</span>\s*<span class="pm-expandable__text">([^<]*)</span>',
        _expandable(page_html, "english-wordlist"),
    )
    materials = json.loads(MATERIALS_JSON.read_text(encoding="utf-8"))
    expected = [(item["item_id"], item["item_number"], item["text"]) for item in materials["wordlist"]["items"]]
    assert [(item_id, unescape(label), unescape(text)) for item_id, label, text in items] == expected
    assert len(expected) == 95
    assert expected[0] == ("wl_001", "1", "so") and expected[-1] == ("wl_095", "95", "Annie - Kenny")


def test_wordlist_title_and_summary_follow_the_spanish_pattern(page_html: str) -> None:
    wordlist = _expandable(page_html, "english-wordlist")
    assert '<h3 class="pm-expandable__title" id="english-wordlist-title">Wordlist</h3>' in wordlist
    assert '<p class="pm-expandable__summary">The English wordlist comprises 95 task items: 84 individual words and 11 minimal pairs.</p>' in wordlist


def test_wordlist_markup_matches_the_spanish_wordlist(app: Flask, page_html: str) -> None:
    """Same component, classes and structure as the Spanish wordlist: no eyebrow, no extra modifier, no tint."""
    spanish = _expandable(app.test_client().get("/en/research/spanish/design").get_data(as_text=True), "spanish-final-wordlist")
    english = _expandable(page_html, "english-wordlist")
    spanish_skeleton, english_skeleton = _markup_skeleton(spanish), _markup_skeleton(english)
    item_start = spanish_skeleton.index("li.pm-expandable__item")
    assert english_skeleton[:item_start] == spanish_skeleton[:item_start]
    assert set(english_skeleton[item_start:]) == set(spanish_skeleton[item_start:])
    assert "data-source=" not in english  # platform material, never presented as manuscript text
    assert 'data-supplement="data/config/research_player/english/task_catalogs/wordlist.json"' in english


def test_wordlist_is_the_only_added_material_and_sits_after_its_paragraph(page_html: str) -> None:
    assert len(re.findall(r'<section\s+class="pm-expandable[ "]', page_html)) == 1
    assert "english-reading-text" not in page_html
    assert "Reading text as used in the recordings" not in page_html
    assert "Supplementary corpus material" not in page_html and "SUPPLEMENTARY" not in page_html
    assert "Let someone else do it" not in page_html  # catalog-only wording of the reading text
    wordlist_paragraph = page_html.index('data-source="p32"')
    wordlist = page_html.index('aria-labelledby="english-wordlist-title"')
    interview = page_html.index('data-source="p33"')
    assert wordlist_paragraph < wordlist < interview


# --- English-only page --------------------------------------------------------------------------------------------


def test_only_the_english_design_page_is_declared_single_language() -> None:
    assert PAGE_UI_LANGUAGES == {"research/english/design": ("en",)}
    assert page_ui_languages(EN_PATH) == ("en",)
    assert page_ui_languages(DE_PATH) == ("en",)
    for bilingual in ("/de/research/english", "/en/research/english/speakers", "/de/research/spanish/design", "/en/teaching/english", "/de/research/english/design/x", "/"):
        assert page_ui_languages(bilingual) == ("de", "en"), bilingual
    assert unavailable_ui_language_target(DE_PATH) == EN_PATH
    assert unavailable_ui_language_target(EN_PATH) is None
    assert available_page_path(DE_PATH) == EN_PATH
    assert available_page_path("/de/research/spanish/design") == "/de/research/spanish/design"


def test_german_url_redirects_to_the_english_page(app: Flask) -> None:
    client = app.test_client()
    response = client.get(DE_PATH)
    assert response.status_code == 302
    assert response.headers["Location"] == EN_PATH

    response = client.get(DE_PATH + "?lang=de&utm_source=mail")
    assert response.status_code == 302
    assert response.headers["Location"] == EN_PATH + "?utm_source=mail"

    followed = client.get(DE_PATH, follow_redirects=True)
    assert followed.status_code == 200
    assert followed.request.path == EN_PATH
    assert len(followed.history) == 1


def test_stored_german_preference_does_not_redirect_the_english_page(app: Flask) -> None:
    client = app.test_client()
    client.set_cookie(PREFERRED_UI_LANGUAGE_COOKIE_NAME, "de", domain="promat.test")
    response = client.get(EN_PATH, headers={"Accept-Language": "de-DE,de;q=0.9"})
    assert response.status_code == 200
    assert '<html lang="en"' in response.get_data(as_text=True)


def test_language_switch_shows_german_as_unavailable(page_html: str) -> None:
    switch = re.search(r'<div class="promat-topbar__language-switch".*?</div>', page_html, re.S).group(0)
    entries = re.findall(r"<(a|span)\s[^>]*class=\"promat-topbar__language-link[^\"]*\"[^>]*>(DE|EN)</\1>", switch)
    assert [label for _, label in entries] == ["DE", "EN"]
    assert entries[0][0] == "span" and entries[1][0] == "a"
    de_entry = re.search(r"<span[^>]*>DE</span>", switch).group(0)
    assert 'aria-disabled="true"' in de_entry and "is-unavailable" in de_entry
    assert "href" not in de_entry and "data-ui-lang-link" not in de_entry
    assert 'title="This page is not available in German"' in de_entry
    assert 'href="/en/research/english/design?lang=en"' in switch
    assert "/de/research/english/design" not in switch


def test_head_names_only_the_english_edition(page_html: str) -> None:
    assert '<link rel="canonical" href="https://pronunciation-matters.de/en/research/english/design">' in page_html
    assert "hreflang" not in page_html
    assert '<meta name="robots"' not in page_html


def test_navigation_from_german_research_pages_links_the_english_edition(app: Flask) -> None:
    html = app.test_client().get("/de/research/english").get_data(as_text=True)
    assert 'href="/en/research/english/design"' in html
    assert 'href="/de/research/english/design"' not in html


def test_bilingual_pages_keep_their_language_switch_and_hreflang(app: Flask) -> None:
    client = app.test_client()
    for path, other in (("/de/research/spanish/design", "/en/research/spanish/design"), ("/de/research/english", "/en/research/english")):
        html = client.get(path).get_data(as_text=True)
        assert 'href="' + path + '?lang=de"' in html
        assert 'href="' + other + '?lang=en"' in html
        assert "is-unavailable" not in html
    spanish = client.get("/en/research/spanish/design").get_data(as_text=True)
    assert 'hreflang="de" href="https://pronunciation-matters.de/de/research/spanish/design"' in spanish
    assert 'hreflang="en" href="https://pronunciation-matters.de/en/research/spanish/design"' in spanish
    for path in ("/de/research/french/design", "/en/research/german/design"):
        assert client.get(path).status_code == 200


def test_article_byline_and_citation_name_the_author_not_the_platform_editor(page_html: str) -> None:
    assert "Author:</span>" in page_html or "Author:" in page_html
    assert "Rolf Kreyer" in page_html
    assert "Kreyer, Rolf (2026). “Capturing the Pronunciation of Learners of English as a Foreign Language: Data Collection Design for the English Corpus of Pronunciation Matters”. In: Felix Tacke (ed.)," in page_html
