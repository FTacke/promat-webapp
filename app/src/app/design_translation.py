"""Translated editions of an imported design article (docs/spec/platform-data-files.md, "Research design articles").

The original edition of an imported article is ``design.json`` (generated from the authors' manuscript). A translated
edition is a hand-maintained Markdown file next to it (``design.{lang}.md``): one block per translated element, opened by a
marker comment naming the element's manuscript reference (``<!-- p6 -->``, ``<!-- t1r4c1 -->``), followed by its text with
inline Markdown (``*italic*``, ``**bold**``). Table cells may hold several paragraphs separated by a blank line.

The translation is merged into a copy of the original structure, so both editions always share sections, tables, rows and
manuscript references. Every prose element (title, abstract, section headings, paragraphs, table captions) must be
translated exactly once and in manuscript order; table cells and bibliography entries are language-neutral by default (IPA
labels, example words with item numbers, references) and only replaced where a marker exists.
"""

from __future__ import annotations

import copy
import re
from html import unescape
from pathlib import Path
from typing import Any, Iterator

from markdown_it import MarkdownIt

_MARKER = re.compile(r"^<!--\s*([pt][0-9a-z]+)\s*-->\s*$")
_INLINE = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})


class TranslationError(ValueError):
    """The translation file does not match the original article."""


def parse_translation(text: str) -> dict[str, list[str]]:
    """Reference -> list of paragraph HTML strings, in file order (the leading comment block is ignored)."""
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    lines: list[str] = []

    def close() -> None:
        if current is None:
            return
        paragraphs = [" ".join(part.split("\n")).strip() for part in "\n".join(lines).strip().split("\n\n")]
        blocks[current] = [_INLINE.renderInline(paragraph).strip() for paragraph in paragraphs if paragraph]

    body = re.sub(r"\A\s*<!--(?!\s*[pt][0-9a-z]+\s*-->).*?-->", "", text, count=1, flags=re.S)
    for line in body.splitlines():
        marker = _MARKER.match(line)
        if marker:
            close()
            current = marker.group(1)
            if current in blocks:
                raise TranslationError(f"element {current} is translated twice")
            lines = []
            continue
        if current is None:
            if line.strip():
                raise TranslationError(f"text before the first marker: {line.strip()[:40]!r}")
            continue
        lines.append(line)
    close()
    return blocks


def _plain(html: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", html))


def _elements(article: dict[str, Any]) -> Iterator[tuple[str, str]]:
    """(reference, kind) of every translatable element in manuscript order; kind ``prose`` or ``neutral``."""
    yield article["title_source"], "prose"
    yield article["abstract_source"], "prose"
    for section in article["sections"]:
        yield section["heading_source"], "prose"
        for entry in section.get("references", []):
            yield entry["source"], "neutral"
        for block in section.get("blocks", []):
            if block["type"] == "expandable_table":
                for row in block["rows"]:
                    for cell in row:
                        yield cell["source"], "neutral"
                yield block["caption"]["source"], "prose"
            else:
                yield block["source"], "prose"


def translation_problems(article: dict[str, Any], translations: dict[str, list[str]]) -> list[str]:
    elements = list(_elements(article))
    known = {ref for ref, _ in elements}
    problems = [f"{ref}: not an element of the original" for ref in translations if ref not in known]
    for ref, kind in elements:
        paragraphs = translations.get(ref)
        if paragraphs is None:
            if kind == "prose":
                problems.append(f"{ref}: missing translation")
        elif kind == "prose" and len(paragraphs) != 1:
            problems.append(f"{ref}: a prose element has exactly one paragraph, found {len(paragraphs)}")
        elif not paragraphs:
            problems.append(f"{ref}: empty translation")
    order = [ref for ref, _ in elements if ref in translations]
    if order != [ref for ref in translations if ref in known]:
        problems.append("markers are not in manuscript order")
    return problems


def translate_article(article: dict[str, Any], translations: dict[str, list[str]]) -> dict[str, Any]:
    problems = translation_problems(article, translations)
    if problems:
        raise TranslationError("; ".join(problems))
    edition = copy.deepcopy(article)
    edition.pop("_generated", None)
    edition["title_html"] = translations[edition["title_source"]][0]
    edition["title"] = _plain(edition["title_html"])
    edition["abstract_html"] = translations[edition["abstract_source"]][0]
    for section in edition["sections"]:
        section["heading"] = _plain(translations[section["heading_source"]][0])
        for entry in section.get("references", []):
            if entry["source"] in translations:
                entry["html"] = translations[entry["source"]][0]
        for block in section.get("blocks", []):
            if block["type"] == "expandable_table":
                block["caption"]["html"] = translations[block["caption"]["source"]][0]
                for row in block["rows"]:
                    for cell in row:
                        if cell["source"] in translations:
                            cell["paragraphs"] = list(translations[cell["source"]])
            else:
                block["html"] = translations[block["source"]][0]
    return edition


def load_translated_article(article: dict[str, Any], path: Path) -> dict[str, Any]:
    return translate_article(article, parse_translation(path.read_text(encoding="utf-8")))
