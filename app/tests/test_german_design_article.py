"""German design article (Theresa Fischer, Kathrin Siebold): manuscript integrity, English edition, tables, materials, routing.

The German edition is imported from the authors' manuscript (docs/author-sources/german-design/, git-ignored) with the
importer's ``bold-headings`` profile and a local list of agreed typo corrections next to it. The integrity tests compare the
*rendered page* with the manuscript, read by the independent OOXML reader of test_english_design_article.py, after applying
those corrections; without the manuscript (CI) they are skipped and the recorded SHA-256 is checked instead. The English
edition comes from content/research/german/design.en.md and must keep the structure, tables, IPA and item numbers.
"""

from __future__ import annotations

from difflib import SequenceMatcher
import hashlib
import html as html_module
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
import yaml
from flask import Flask

from test_english_design_article import REPO_ROOT, W, _SourceCollector, _docx_chars, _docx_styles, _formats, app  # noqa: F401

from app.design_translation import parse_translation, translation_problems
from app.page_languages import PAGE_UI_LANGUAGES

SOURCES = REPO_ROOT / "docs" / "author-sources" / "german-design"
DOCX = SOURCES / "fischer-siebold-german-design-original.docx"
CORRECTIONS = SOURCES / "fischer-siebold-german-design-corrections.yaml"
DOCX_SHA256 = "108d722ea80d12775fa3eabe7edf3549c72c09c17e1edefe84ebd06e0d67d213"
CONTENT = REPO_ROOT / "content" / "research" / "german"
ARTICLE = json.loads((CONTENT / "design.json").read_text(encoding="utf-8"))
MATERIALS = json.loads((CONTENT / "design_materials.json").read_text(encoding="utf-8"))
TRANSLATION = parse_translation((CONTENT / "design.en.md").read_text(encoding="utf-8"))
DE_PATH = "/de/research/german/design"
EN_PATH = "/en/research/german/design"
WORD_JOINER = "⁠"

#: Structural paragraphs whose bold only marks the structure (title, section headings, table captions, abstract label).
STRUCTURAL = {"p0", "p2", "p5", "p9", "p12", "p14", "p16", "p19", "p25", "p29"}
#: Table cells whose italics were made consistent with the rest of their table (agreed typographic correction).
ITALICS_NORMALIZED = {"t0r2c1", "t0r16c1", "t0r17c1", "t0r18c1"}
#: Table caption -> table it belongs to (captions follow their table in the manuscript, the page shows them as title).
CAPTIONS = {"p12": "t0", "p14": "t1", "p16": "t2"}


def _plain(fragment: str) -> str:
    return html_module.unescape(re.sub(r"<[^>]+>", "", fragment))


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace(WORD_JOINER, "")).strip()


def _read_manuscript() -> list[tuple[str, list[tuple[str, frozenset[str]]]]]:
    if not DOCX.is_file():
        pytest.skip("the authors' manuscript is kept locally only (docs/author-sources/ is git-ignored)")
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
                    chars: list[tuple[str, frozenset[str]]] = []
                    for paragraph in cell.findall(W + "p"):
                        if chars:
                            chars.append((" ", frozenset()))
                        chars.extend(_docx_chars(paragraph, styles))
                    out.append((f"t{t_index}r{r}c{c}", chars))
            t_index += 1
    return out


def _corrected_text(ref: str, text: str) -> str:
    """Manuscript text of one element after the agreed corrections (compared as plain text)."""
    corrections = yaml.safe_load(CORRECTIONS.read_text(encoding="utf-8"))["corrections"]
    for entry in corrections:
        if entry["source"] == ref:
            text = text.replace(_plain(entry["old"]), _plain(entry["new"]))
    return text


@pytest.fixture
def client(app: Flask):  # noqa: F811 - `app` is the shared fixture of test_english_design_article
    return app.test_client()


def _page(client, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.get_data(as_text=True)


def _collect(page_html: str) -> _SourceCollector:
    collector = _SourceCollector()
    collector.feed(page_html)
    return collector


# --- import and manuscript integrity ------------------------------------------------------------------------------


def test_committed_import_names_the_manuscript_and_its_corrections() -> None:
    generated = ARTICLE["_generated"]
    assert generated["source_sha256"] == DOCX_SHA256 and generated["profile"] == "bold-headings"
    assert generated["corrections"]["source"].startswith("docs/author-sources/german-design/")
    if DOCX.is_file():
        assert hashlib.sha256(DOCX.read_bytes()).hexdigest() == DOCX_SHA256
    if CORRECTIONS.is_file():
        assert hashlib.sha256(CORRECTIONS.read_bytes()).hexdigest() == generated["corrections"]["sha256"]


def test_committed_import_is_a_fresh_import(tmp_path: Path) -> None:
    if not (DOCX.is_file() and CORRECTIONS.is_file()):
        pytest.skip("manuscript and corrections are kept locally only")
    import import_design_article_docx as importer

    out = tmp_path / "design.json"
    args = ["--profile", "bold-headings", "--docx", str(DOCX), "--corrections", str(CORRECTIONS), "--references-heading", "Literatur", "--out", str(out)]
    assert importer.main(args) == 0
    fresh = json.loads(out.read_text(encoding="utf-8"))
    for payload in (fresh, ARTICLE):
        payload["_generated"].pop("source", None)
        payload["_generated"]["corrections"].pop("source", None)
    assert fresh == ARTICLE


def test_article_structure_follows_the_manuscript() -> None:
    assert [(s["heading_number"], s["heading"]) for s in ARTICLE["sections"]] == [
        ("1.", "Zielsetzung"),
        ("2.", "Auswahl der Phänomene: (Un)typische Ausspracheschwierigkeiten von Deutschlernenden"),
        ("3.", "Konzeption der Materialien"),
        ("4.", "Fazit"),
        ("", "Literatur"),
    ]
    tables = [b for s in ARTICLE["sections"] for b in s.get("blocks", []) if b["type"] == "expandable_table"]
    assert [(t["source"], t["caption"]["source"], len(t["rows"])) for t in tables] == [("t0", "p12", 19), ("t1", "p14", 22), ("t2", "p16", 2)]
    assert ARTICLE["keywords"] == [] and len(ARTICLE["sections"][-1]["references"]) == 7


def test_page_text_matches_the_manuscript_after_the_agreed_corrections(client) -> None:
    rendered = _collect(_page(client, DE_PATH))
    manuscript = _read_manuscript()
    assert not rendered.duplicates
    mismatches = []
    for ref, chars in manuscript:
        if ref == "p2":  # the manuscript's "Abstract" label; the German edition shows the platform label "Zusammenfassung"
            assert ref not in rendered.sources
            continue
        expected = _norm(_corrected_text(ref, "".join(ch for ch, _ in chars)))
        shown = _norm("".join(ch for ch, _ in rendered.sources.get(ref, [])))
        if ref in rendered.numbers:
            shown = _norm(f"{rendered.numbers[ref]} {shown}")
        if shown != expected:
            mismatches.append((ref, expected, shown))
    assert not mismatches, mismatches[:3]


def test_page_keeps_the_manuscript_order(client) -> None:
    rendered = _collect(_page(client, DE_PATH))
    expected = [ref for ref, _ in _read_manuscript() if ref != "p2"]
    for caption, table in CAPTIONS.items():  # the caption is shown as the title above its table
        expected.remove(caption)
        expected.insert(next(i for i, ref in enumerate(expected) if ref.startswith(table + "r")), caption)
    assert [ref for ref in rendered.order if ref in set(expected)] == expected


def test_page_keeps_the_manuscript_character_formatting(client) -> None:
    rendered = _collect(_page(client, DE_PATH))
    for ref, chars in _read_manuscript():
        if ref in STRUCTURAL | ITALICS_NORMALIZED:
            continue
        expected = _formats([(ch, fmt) for ch, fmt in chars if ch != WORD_JOINER])
        shown = _formats([(ch, fmt) for ch, fmt in rendered.sources[ref] if ch != WORD_JOINER])
        matcher = SequenceMatcher(None, [c for c, _ in expected], [c for c, _ in shown], autojunk=False)
        for a, b, size in matcher.get_matching_blocks():
            assert [f for _, f in expected[a:a + size]] == [f for _, f in shown[b:b + size]], ref
    italic_cells = [rendered.sources[ref] for ref in ITALICS_NORMALIZED]
    assert all(all("i" in fmt for ch, fmt in cell if not ch.isspace()) for cell in italic_cells)


# --- English edition ----------------------------------------------------------------------------------------------


def test_english_translation_is_complete_and_in_manuscript_order() -> None:
    assert translation_problems(ARTICLE, TRANSLATION) == []



def _ipa(fragment: str) -> list[str]:
    return sorted(token for token in re.findall(r"\[[^\]\s]+\]", _plain(fragment)) if not token.startswith("[+"))


def _items(fragment: str) -> list[str]:
    return re.findall(r"[\wäöüß]+ \(\d+(?:/\s?\d+)?\)", _plain(fragment))


def test_english_edition_keeps_tables_ipa_items_and_references(client) -> None:
    de = _collect(_page(client, DE_PATH))
    en = _collect(_page(client, EN_PATH))
    # same elements, same order (only the English edition shows the manuscript's own "Abstract" label, p2)
    assert de.order == [r for r in en.order if r != "p2"]
    for ref in de.order:
        de_text = "".join(ch for ch, _ in de.sources[ref])
        en_text = "".join(ch for ch, _ in en.sources[ref])
        assert _ipa(de_text) == _ipa(en_text), ref
        if ref.startswith("t"):
            assert _items(de_text) == _items(en_text), ref
        if ref in {"p30", "p31", "p32", "p33", "p34", "p35", "p36"}:
            assert de_text == en_text, ref
        years = lambda text: sorted(re.findall(r"\b20\d\d\b", text))  # noqa: E731
        assert years(de_text) == years(en_text), ref
    # the original's figures are kept, including the sentence count of the manuscript (51 in the catalog, see run log)
    assert "50 sentences: 31 declarative sentences, 10 yes/no questions and 10 wh-questions" in "".join(ch for ch, _ in en.sources["p22"])
    assert "96 items, 85 of them individual words and 11 minimal pairs" in "".join(ch for ch, _ in en.sources["p21"])


def test_english_title_and_headings() -> None:
    assert _plain(TRANSLATION["p0"][0]) == "Capturing the Pronunciation of Learners of German: Data Collection Design for the German Corpus of Pronunciation Matters"
    assert TRANSLATION["p0"][0].endswith("<em>Pronunciation Matters</em>")
    assert [_plain(TRANSLATION[ref][0]) for ref in ("p5", "p9", "p19", "p25", "p29")] == [
        "Objectives",
        "Selection of the phenomena: (A)typical pronunciation difficulties of learners of German",
        "Design of the materials",
        "Conclusion",
        "References",
    ]


# --- tables and materials -----------------------------------------------------------------------------------------


@pytest.mark.parametrize("path", [DE_PATH, EN_PATH])
def test_tables_are_closed_expandables_with_full_semantic_tables(client, path: str) -> None:
    page_html = _page(client, path)
    tables = re.findall(r'<section\s+class="pm-expandable pm-expandable--table".*?</section>', page_html, flags=re.S)
    assert len(tables) == 3
    for index, (block, rows, caption) in enumerate(zip(tables, (19, 22, 2), ("p12", "p14", "p16")), start=1):
        assert f'id="german-design-table-{index}-title" data-source="{caption}"' in block
        assert 'aria-expanded="false"' in block and f'aria-controls="german-design-table-{index}-content"' in block
        assert block.count('<th scope="row"') == rows and block.count("<td ") == rows
        assert "<thead" in block and 'aria-labelledby="german-design-table-' in block


@pytest.mark.parametrize(("path", "wordlist", "sentences"), [
    (DE_PATH, "Die deutsche Wortliste umfasst 96 Aufgabenitems: 85 Einzelwörter und 11 Minimalpaare.", "Die deutsche Satzliste umfasst 51 Sätze (T1–T51)."),
    (EN_PATH, "The German wordlist comprises 96 task items: 85 individual words and 11 minimal pairs.", "The German sentence list comprises 51 sentences (T1–T51)."),
])
def test_materials_follow_their_paragraphs_with_all_catalog_items(client, path: str, wordlist: str, sentences: str) -> None:
    page_html = _page(client, path)
    assert wordlist in page_html and sentences in page_html
    for element, after, before, material in (("german-wordlist", 'data-source="p21"', 'data-source="p22"', "wordlist"), ("german-sentence-list", 'data-source="p22"', 'data-source="p23"', "text")):
        position = page_html.index(f'aria-labelledby="{element}-title"')
        assert page_html.index(after) < position < page_html.index(before)
        block = page_html[position:page_html.index("</section>", position)]
        assert "data-source" not in block and f'data-supplement="{MATERIALS[material]["source"]}"' in block
        items = re.findall(r'data-item-id="([^"]+)">\s*<span class="pm-expandable__label">([^<]*)</span>\s*<span class="pm-expandable__text">([^<]*)</span>', block)
        assert [(i, n, html_module.unescape(t)) for i, n, t in items] == [(m["item_id"], m["item_number"], m["text"]) for m in MATERIALS[material]["items"]]
    assert len(MATERIALS["wordlist"]["items"]) == 96 and len(MATERIALS["text"]["items"]) == 51


# --- routing, metadata, citation ----------------------------------------------------------------------------------


def test_both_editions_are_published_with_switch_canonical_and_hreflang(client) -> None:
    assert "research/german/design" not in PAGE_UI_LANGUAGES
    for path, other in ((DE_PATH, EN_PATH), (EN_PATH, DE_PATH)):
        page_html = _page(client, path)
        assert f'rel="canonical" href="https://pronunciation-matters.de{path}"' in page_html
        assert f'hreflang="de" href="https://pronunciation-matters.de{DE_PATH}"' in page_html
        assert f'hreflang="en" href="https://pronunciation-matters.de{EN_PATH}"' in page_html
        assert f'href="{other}"' in page_html or f'href="{other}?' in page_html
        assert "In Vorbereitung" not in page_html and "in preparation" not in page_html.lower()


@pytest.mark.parametrize(("path", "editor"), [(DE_PATH, "Felix Tacke (Hrsg.)"), (EN_PATH, "Felix Tacke (ed.)")])
def test_byline_and_citation_name_the_two_authors(client, path: str, editor: str) -> None:
    page_html = _page(client, path)
    meta = re.findall(r'class="pm-article-meta__value[^"]*">(?:<time[^>]*>)?([^<]*)', page_html)
    assert meta[:3] == ["Theresa Fischer, Kathrin Siebold", "Philipps-Universität Marburg", "2026"]
    citation = html_module.unescape(re.search(r'data-copy-text="([^"]*)"', page_html).group(1))
    assert citation.startswith("Fischer, Theresa & Siebold, Kathrin (2026).") and editor in citation
    assert citation.endswith(f"https://pronunciation-matters.de{path}")
    assert "Pronunciation Matters" in re.search(r"<h1[^>]*>(.*?)</h1>", page_html, flags=re.S).group(1)
    assert "<em>Pronunciation Matters</em>" in re.search(r"<h1[^>]*>(.*?)</h1>", page_html, flags=re.S).group(1)
