"""Import an author's DOCX manuscript as a public research design article (verbatim, formatting-preserving).

Contract: docs/spec/platform-data-files.md, "Research design articles"; procedure: docs/runbooks/design-article-import.md.

The importer reads the OOXML of the manuscript directly (``word/document.xml``, ``styles.xml``, ``numbering.xml``) and
writes a JSON article for ``content/research/{corpus}/design.json``. It never edits text: every character of every run is
kept, adjacent runs with the same character formatting are merged, and italics, bold, underline, superscript and subscript
become ``<em>``, ``<strong>``, ``<u>``, ``<sup>`` and ``<sub>``. Automatic Word numbering (chapter numbers, example
numbers) is resolved from ``numbering.xml`` because it is not part of the paragraph text.

Every imported element carries a ``source`` reference to its DOCX position (``p{n}`` = n-th top-level paragraph,
``t{n}r{r}c{c}`` = table cell). The rendered page repeats these references as ``data-source`` attributes, so the integrity
test (app/tests/test_english_design_article.py) can compare the live page with the manuscript character by character.

Structure recognition (anything the rules do not cover aborts the import instead of guessing):

- the first ``heading 1`` paragraph is the article title;
- a paragraph whose text is ``Abstract`` / ``Keywords`` is a label, the next non-empty paragraph its value
  (keywords are split at `` · ``);
- ``heading 2`` paragraphs open sections (number from the heading list), ``heading 3`` paragraphs are subheadings whose
  number precedes a tab;
- a paragraph numbered with a parenthesised list (``(%1)``) opens a numbered example; directly following paragraphs that
  are indented to the list text (``w:ind left`` >= 600 twips) continue it;
- tables become grouped tables: a row whose second cell is empty (or whose first cell spans the table) is a group
  heading, rows without any text are layout spacers and are listed in ``skipped_empty_rows``;
- after the references heading every non-empty paragraph is one bibliography entry.

Usage::

    python scripts/import_design_article_docx.py \
        --docx docs/author-sources/english-design/kreyer-english-design-original.docx \
        --out content/research/english/design.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
REPO_ROOT = Path(__file__).resolve().parents[1]

#: Character formats kept from the manuscript, in nesting order (outermost first), and their HTML tags.
FORMAT_TAGS: tuple[tuple[str, str], ...] = (("b", "strong"), ("i", "em"), ("u", "u"), ("sup", "sup"), ("sub", "sub"))
#: Minimum left indent (twips) for a paragraph that continues the numbered example above it.
EXAMPLE_CONTINUATION_INDENT = 600
KEYWORD_SEPARATOR = " · "


class ImportError_(RuntimeError):
    """The manuscript has a structure the importer does not recognise; nothing is written."""


@dataclass
class Segment:
    text: str
    formats: frozenset[str]


@dataclass
class Paragraph:
    index: int
    style: str
    segments: list[Segment]
    num_id: str | None = None
    ilvl: str = "0"
    indent_left: int = 0

    @property
    def text(self) -> str:
        return "".join(segment.text for segment in self.segments)


@dataclass
class Table:
    index: int
    position: int  # index of the next top-level paragraph, i.e. where the table sits in the flow
    rows: list[list[tuple[list[Paragraph], int]]] = field(default_factory=list)  # cells: (paragraphs, grid span)


def _on(element: ET.Element | None) -> bool:
    return element is not None and element.get(W + "val") not in ("0", "false", "none")


class Docx:
    def __init__(self, path: Path) -> None:
        self.path = path
        with zipfile.ZipFile(path) as archive:
            self.document = ET.fromstring(archive.read("word/document.xml"))
            self.styles = ET.fromstring(archive.read("word/styles.xml"))
            self.numbering = ET.fromstring(archive.read("word/numbering.xml")) if "word/numbering.xml" in archive.namelist() else None
        self._style_elements = {style.get(W + "styleId"): style for style in self.styles.findall(W + "style")}
        self._counters: dict[tuple[str, str], int] = {}

    def style_name(self, style_id: str) -> str:
        """Built-in style name (``heading 2``, ``List Paragraph``, ``Normal``); style ids are localized (``berschrift2``)."""
        if not style_id:
            return "Normal"
        style = self._style_elements.get(style_id)
        name = style.find(W + "name") if style is not None else None
        return name.get(W + "val") if name is not None else style_id

    # --- character formatting -------------------------------------------------------------------------------------

    def _character_style_formats(self, style_id: str | None) -> set[str]:
        formats: set[str] = set()
        seen: set[str] = set()
        while style_id and style_id not in seen:
            seen.add(style_id)
            style = self._style_elements.get(style_id)
            if style is None:
                break
            formats |= self._rpr_formats(style.find(W + "rPr"), include_style=False)
            based_on = style.find(W + "basedOn")
            style_id = based_on.get(W + "val") if based_on is not None else None
        return formats

    def _rpr_formats(self, rpr: ET.Element | None, *, include_style: bool = True) -> set[str]:
        formats: set[str] = set()
        if rpr is None:
            return formats
        if include_style:
            rstyle = rpr.find(W + "rStyle")
            if rstyle is not None:
                formats |= self._character_style_formats(rstyle.get(W + "val"))
        for tag, name in (("b", "b"), ("i", "i")):
            element = rpr.find(W + tag)
            if element is not None:
                formats.add(name) if _on(element) else formats.discard(name)
        underline = rpr.find(W + "u")
        if underline is not None and _on(underline):
            formats.add("u")
        vert = rpr.find(W + "vertAlign")
        if vert is not None:
            value = vert.get(W + "val")
            if value == "superscript":
                formats.add("sup")
            elif value == "subscript":
                formats.add("sub")
        for unsupported in ("strike", "dstrike", "caps", "smallCaps", "vanish", "highlight"):
            if _on(rpr.find(W + unsupported)):
                raise ImportError_(f"unsupported character formatting <w:{unsupported}> in {self.path.name}")
        return formats

    def _paragraph_style_formats(self, style_id: str) -> set[str]:
        """Bold/italic defined on the paragraph style (e.g. a heading style); applies to every run."""
        formats: set[str] = set()
        seen: set[str] = set()
        while style_id and style_id not in seen:
            seen.add(style_id)
            style = self._style_elements.get(style_id)
            if style is None:
                break
            formats |= self._rpr_formats(style.find(W + "rPr"), include_style=False)
            based_on = style.find(W + "basedOn")
            style_id = based_on.get(W + "val") if based_on is not None else ""
        return formats

    # --- paragraphs ------------------------------------------------------------------------------------------------

    def _style_num(self, style_id: str) -> tuple[str | None, str]:
        seen: set[str] = set()
        while style_id and style_id not in seen:
            seen.add(style_id)
            style = self._style_elements.get(style_id)
            if style is None:
                break
            numpr = style.find(f"{W}pPr/{W}numPr")
            if numpr is not None and numpr.find(W + "numId") is not None:
                ilvl = numpr.find(W + "ilvl")
                return numpr.find(W + "numId").get(W + "val"), ilvl.get(W + "val") if ilvl is not None else "0"
            based_on = style.find(W + "basedOn")
            style_id = based_on.get(W + "val") if based_on is not None else ""
        return None, "0"

    def paragraph(self, element: ET.Element, index: int) -> Paragraph:
        ppr = element.find(W + "pPr")
        style = ""
        num_id: str | None = None
        ilvl = "0"
        indent_left = 0
        if ppr is not None:
            pstyle = ppr.find(W + "pStyle")
            style = pstyle.get(W + "val") if pstyle is not None else ""
            numpr = ppr.find(W + "numPr")
            if numpr is not None and numpr.find(W + "numId") is not None:
                num_id = numpr.find(W + "numId").get(W + "val")
                level = numpr.find(W + "ilvl")
                ilvl = level.get(W + "val") if level is not None else "0"
            ind = ppr.find(W + "ind")
            if ind is not None:
                indent_left = int(ind.get(W + "left") or ind.get(W + "start") or 0)
        if num_id is None:
            num_id, ilvl = self._style_num(style)
        if num_id == "0":
            num_id = None
        base_formats = self._paragraph_style_formats(style)
        segments: list[Segment] = []
        for node in element.iter():
            if node.tag in (W + "del", W + "moveFrom", W + "ins", W + "moveTo"):
                raise ImportError_(f"tracked changes in paragraph {index}; accept or reject them in Word first")
            if node.tag != W + "r":
                continue
            formats = frozenset(base_formats | self._rpr_formats(node.find(W + "rPr")))
            for child in node:
                if child.tag == W + "t":
                    text = child.text or ""
                elif child.tag == W + "tab":
                    text = "\t"
                elif child.tag in (W + "br", W + "cr"):
                    raise ImportError_(f"manual line break in paragraph {index}")
                elif child.tag in (W + "rPr", W + "lastRenderedPageBreak"):
                    continue
                else:
                    raise ImportError_(f"unsupported run content <{child.tag.replace(W, 'w:')}> in paragraph {index}")
                if not text:
                    continue
                if segments and segments[-1].formats == formats:
                    segments[-1].text += text
                else:
                    segments.append(Segment(text, formats))
        return Paragraph(index, style, segments, num_id, ilvl, indent_left)

    # --- numbering -------------------------------------------------------------------------------------------------

    def _level(self, num_id: str, ilvl: str) -> tuple[str, ET.Element]:
        if self.numbering is None:
            raise ImportError_("numbered paragraph without numbering.xml")
        num = next((n for n in self.numbering.findall(W + "num") if n.get(W + "numId") == num_id), None)
        if num is None:
            raise ImportError_(f"unknown numbering id {num_id}")
        if num.find(W + "lvlOverride") is not None:
            raise ImportError_(f"numbering id {num_id} uses level overrides; not supported")
        abstract_id = num.find(W + "abstractNumId").get(W + "val")
        abstract = next(a for a in self.numbering.findall(W + "abstractNum") if a.get(W + "abstractNumId") == abstract_id)
        level = next(lvl for lvl in abstract.findall(W + "lvl") if lvl.get(W + "ilvl") == ilvl)
        return abstract_id, level

    def list_pattern(self, paragraph: Paragraph) -> str | None:
        if paragraph.num_id is None:
            return None
        _, level = self._level(paragraph.num_id, paragraph.ilvl)
        return level.find(W + "lvlText").get(W + "val")

    def number(self, paragraph: Paragraph) -> str:
        """Next rendered number of a numbered paragraph (Word counts per abstract list and level)."""
        abstract_id, level = self._level(paragraph.num_id or "", paragraph.ilvl)
        fmt = level.find(W + "numFmt").get(W + "val")
        if fmt != "decimal":
            raise ImportError_(f"numbering format {fmt!r} is not supported")
        key = (abstract_id, paragraph.ilvl)
        start = int(level.find(W + "start").get(W + "val")) if level.find(W + "start") is not None else 1
        self._counters[key] = self._counters.get(key, start - 1) + 1
        return level.find(W + "lvlText").get(W + "val").replace(f"%{int(paragraph.ilvl) + 1}", str(self._counters[key]))

    # --- body ------------------------------------------------------------------------------------------------------

    def body(self) -> list[Paragraph | Table]:
        items: list[Paragraph | Table] = []
        paragraph_index = 0
        table_index = 0
        for child in self.document.find(W + "body"):
            if child.tag == W + "p":
                items.append(self.paragraph(child, paragraph_index))
                paragraph_index += 1
            elif child.tag == W + "tbl":
                table = Table(table_index, paragraph_index)
                for tr in child.findall(W + "tr"):
                    row = []
                    for tc in tr.findall(W + "tc"):
                        span_element = tc.find(f"{W}tcPr/{W}gridSpan")
                        if tc.find(f"{W}tcPr/{W}vMerge") is not None:
                            raise ImportError_("vertically merged table cells are not supported")
                        span = int(span_element.get(W + "val")) if span_element is not None else 1
                        row.append(([self.paragraph(p, -1) for p in tc.findall(W + "p")], span))
                    table.rows.append(row)
                items.append(table)
                table_index += 1
            elif child.tag != W + "sectPr":
                raise ImportError_(f"unsupported body element {child.tag}")
        return items


def segments_html(segments: list[Segment]) -> str:
    """HTML of formatted segments; tags nest in FORMAT_TAGS order and close as late as possible."""
    order = [name for name, _ in FORMAT_TAGS]
    tags = dict(FORMAT_TAGS)
    out: list[str] = []
    stack: list[str] = []
    for segment in segments:
        wanted = [name for name in order if name in segment.formats]
        keep = 0
        while keep < len(stack) and keep < len(wanted) and stack[keep] == wanted[keep]:
            keep += 1
        for name in reversed(stack[keep:]):
            out.append(f"</{tags[name]}>")
        stack = stack[:keep]
        for name in wanted[keep:]:
            out.append(f"<{tags[name]}>")
            stack.append(name)
        out.append(escape(segment.text, quote=False))
    for name in reversed(stack):
        out.append(f"</{tags[name]}>")
    return "".join(out)


def _cell(paragraphs: list[Paragraph], ref: str) -> dict[str, str]:
    filled = [p for p in paragraphs if p.text.strip()]
    if len(filled) > 1:
        raise ImportError_(f"table cell {ref} has more than one paragraph")
    return {"html": segments_html(filled[0].segments) if filled else "", "source": ref}


def _table_block(doc: Docx, table: Table) -> dict[str, object]:
    groups: list[dict[str, object]] = []
    skipped: list[int] = []
    for r, row in enumerate(table.rows):
        texts = [" ".join(p.text for p in cell).strip() for cell, _ in row]
        ref = lambda c: f"t{table.index}r{r}c{c}"  # noqa: E731 - local formatter
        if not any(texts):
            skipped.append(r)
            continue
        is_heading = (len(row) == 1 and row[0][1] > 1) or (len(row) == 2 and texts[0] and not texts[1])
        if is_heading:
            groups.append({"heading": _cell(row[0][0], ref(0)), "rows": []})
            continue
        if len(row) != 2 or not groups:
            raise ImportError_(f"table {table.index} row {r} is neither a group heading nor a two-cell row inside a group")
        groups[-1]["rows"].append([_cell(row[0][0], ref(0)), _cell(row[1][0], ref(1))])
    return {"type": "grouped_table", "source": f"t{table.index}", "groups": groups, "skipped_empty_rows": skipped}


def build_article(docx_path: Path, references_heading: str) -> dict[str, object]:
    doc = Docx(docx_path)
    items = doc.body()
    article: dict[str, object] = {}
    sections: list[dict[str, object]] = []
    pending_label: str | None = None
    in_references = False
    current_example: dict[str, object] | None = None

    def blocks() -> list[dict[str, object]]:
        if not sections:
            raise ImportError_("body text before the first section heading")
        return sections[-1]["blocks"]  # type: ignore[return-value]

    for item in items:
        if isinstance(item, Table):
            current_example = None
            blocks().append(_table_block(doc, item))
            continue
        paragraph = item
        ref = f"p{paragraph.index}"
        text = paragraph.text
        style_name = doc.style_name(paragraph.style)
        if not text.strip():
            current_example = None
            continue
        if "title" not in article:
            if style_name != "heading 1":
                raise ImportError_(f"the first paragraph with text ({ref}) is not a heading 1 title")
            article["title"] = text
            article["title_html"] = segments_html(paragraph.segments)
            article["title_source"] = ref
            continue
        if pending_label:
            if pending_label == "abstract":
                article["abstract_html"] = segments_html(paragraph.segments)
                article["abstract_source"] = ref
            else:
                if any(segment.formats for segment in paragraph.segments):
                    raise ImportError_("formatted keywords are not supported")
                article["keywords"] = text.split(KEYWORD_SEPARATOR)
                article["keywords_source"] = ref
            pending_label = None
            continue
        if text.strip() in ("Abstract", "Keywords") and not sections:
            pending_label = text.strip().lower()
            article[f"{pending_label}_label"] = {"text": text.strip(), "source": ref}
            continue
        if style_name == "heading 2":
            current_example = None
            number = doc.number(paragraph) if paragraph.num_id else ""
            if any(segment.formats for segment in paragraph.segments):
                raise ImportError_(f"formatted section heading {ref} is not supported")
            in_references = text.strip() == references_heading
            section: dict[str, object] = {"heading": text, "heading_number": number, "heading_source": ref, "blocks": []}
            if in_references:
                section = {"heading": text, "heading_number": number, "heading_source": ref, "list_class": "pm-literature", "references": []}
            sections.append(section)
            continue
        if style_name == "heading 3":
            current_example = None
            if "\t" not in text or paragraph.segments[0].formats:
                raise ImportError_(f"subheading {ref} has no tab-separated number")
            number, _, rest = text.partition("\t")
            rest_segments = list(paragraph.segments)
            consumed = len(number) + 1
            while consumed:
                head = rest_segments[0]
                if len(head.text) <= consumed:
                    consumed -= len(head.text)
                    rest_segments.pop(0)
                else:
                    rest_segments[0] = Segment(head.text[consumed:], head.formats)
                    consumed = 0
            blocks().append({"type": "subheading", "number": number, "html": segments_html(rest_segments), "source": ref})
            continue
        if in_references:
            sections[-1]["references"].append({"html": segments_html(paragraph.segments), "source": ref})  # type: ignore[union-attr]
            continue
        pattern = doc.list_pattern(paragraph)
        if pattern is not None:
            if pattern != "(%1)":
                raise ImportError_(f"list paragraph {ref} with numbering {pattern!r} is not a numbered example")
            current_example = {"type": "example", "number": doc.number(paragraph), "number_source": ref, "paragraphs": []}
            current_example["paragraphs"].append({"html": segments_html(paragraph.segments), "source": ref})  # type: ignore[union-attr]
            blocks().append(current_example)
            continue
        if current_example is not None and paragraph.indent_left >= EXAMPLE_CONTINUATION_INDENT:
            current_example["paragraphs"].append({"html": segments_html(paragraph.segments), "source": ref})  # type: ignore[union-attr]
            continue
        current_example = None
        if style_name != "Normal":
            raise ImportError_(f"paragraph {ref} has unexpected style {style_name!r}")
        blocks().append({"type": "paragraph_html", "html": segments_html(paragraph.segments), "source": ref})

    for required in ("title", "abstract_html", "keywords"):
        if required not in article:
            raise ImportError_(f"manuscript has no {required}")
    if not sections or not sections[-1].get("references"):
        raise ImportError_(f"manuscript has no references section headed {references_heading!r}")
    article["sections"] = sections
    return article


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--docx", required=True, type=Path, help="author manuscript (never modified)")
    parser.add_argument("--out", required=True, type=Path, help="article JSON to write, e.g. content/research/english/design.json")
    parser.add_argument("--references-heading", default="References", help="text of the bibliography section heading")
    parser.add_argument("--check", action="store_true", help="do not write; fail if --out differs from a fresh import")
    args = parser.parse_args(argv)

    docx_path = args.docx if args.docx.is_absolute() else REPO_ROOT / args.docx
    out_path = args.out if args.out.is_absolute() else REPO_ROOT / args.out
    article = build_article(docx_path, args.references_heading)
    payload = {
        "_generated": {
            "by": "scripts/import_design_article_docx.py",
            "source": docx_path.relative_to(REPO_ROOT).as_posix(),
            "source_sha256": hashlib.sha256(docx_path.read_bytes()).hexdigest(),
            "note": "Verbatim import of the author's manuscript. Do not edit by hand; correct the manuscript and re-run the importer.",
        },
        **article,
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        current = out_path.read_text(encoding="utf-8") if out_path.is_file() else ""
        if current != rendered:
            print(f"{out_path} is not the current import of {args.docx}", file=sys.stderr)
            return 1
        print(f"{out_path} matches a fresh import")
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
