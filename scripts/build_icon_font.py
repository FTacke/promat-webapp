"""Build the subset of Material Symbols Rounded that the app actually uses.

    python scripts/build_icon_font.py --source <full MaterialSymbolsRounded[FILL,GRAD,opsz,wght].woff2> \
        [--out app/static/fonts/MaterialSymbolsRounded.woff2]

The full variable font is about 5 MB and was loaded on every page. The CSS (`material-symbols.css`) always uses
``FILL 0, wght 300, GRAD 0, opsz 24``, so the axes are pinned to those values and only the glyphs whose ligature
name appears in the app sources (templates, JavaScript, Python) are kept. Icons stay ligature text in the markup
(``<span class="material-symbols-rounded">save</span>``); when a new icon name is added to the sources, rerun this
script with the full font (https://github.com/google/material-design-icons, ``variablefont`` directory).

Requires ``pip install fonttools brotli``.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = (REPO_ROOT / "app" / "templates", REPO_ROOT / "app" / "static" / "js", REPO_ROOT / "app" / "src")
SOURCE_SUFFIXES = {".html", ".js", ".py", ".mjs"}
AXES = {"FILL": 0, "wght": 300, "GRAD": 0, "opsz": 24}


def ligature_names(font: TTFont) -> set[str]:
    """All icon names (ligature input strings) of the font."""
    glyph_order = font.getGlyphOrder()
    cmap = font.getBestCmap()
    reverse = {glyph: chr(code) for code, glyph in cmap.items()}
    names: set[str] = set()
    for lookup in font["GSUB"].table.LookupList.Lookup:
        for subtable in lookup.SubTable:
            subtable = getattr(subtable, "ExtSubTable", subtable)
            for first, ligatures in getattr(subtable, "ligatures", {}).items():
                for ligature in ligatures:
                    parts = [first, *ligature.Component]
                    if all(part in reverse for part in parts):
                        names.add("".join(reverse[part] for part in parts))
    del glyph_order
    return names


def prune_ligatures(font: TTFont, keep: set[str]) -> None:
    """Drop every ligature rule except the used icons, so the subsetter's GSUB closure does not pull in all glyphs
    whose names happen to be spelled with the retained letters."""
    reverse = {glyph: chr(code) for code, glyph in font.getBestCmap().items()}
    for lookup in font["GSUB"].table.LookupList.Lookup:
        for subtable in lookup.SubTable:
            subtable = getattr(subtable, "ExtSubTable", subtable)
            ligature_map = getattr(subtable, "ligatures", None)
            if not ligature_map:
                continue
            for first in list(ligature_map):
                kept = [
                    ligature
                    for ligature in ligature_map[first]
                    if all(part in reverse for part in (first, *ligature.Component))
                    and "".join(reverse[part] for part in (first, *ligature.Component)) in keep
                ]
                if kept:
                    ligature_map[first] = kept
                else:
                    del ligature_map[first]


def used_names(candidates: set[str]) -> set[str]:
    corpus = ""
    for directory in SOURCE_DIRS:
        for path in directory.rglob("*"):
            if path.suffix in SOURCE_SUFFIXES and path.is_file():
                corpus += path.read_text(encoding="utf-8", errors="ignore") + "\n"
    # An icon name counts as used only where it is written as an icon: `>name<` (ligature text in markup) or a
    # quoted string (`icon: "name"`, `textContent = 'name'`). This avoids keeping glyphs for words in prose.
    return {
        name
        for name in candidates
        if re.search(r">\s*%s\s*<" % re.escape(name), corpus) or re.search(r"[\"'`]%s[\"'`]" % re.escape(name), corpus)
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "app" / "static" / "fonts" / "MaterialSymbolsRounded.woff2")
    args = parser.parse_args()

    font = TTFont(args.source)
    names = used_names(ligature_names(font))
    prune_ligatures(font, names)
    instance = instancer.instantiateVariableFont(font, AXES, inplace=False)
    options = Options()
    options.layout_features = ["liga", "rlig", "calt"]
    options.flavor = "woff2"
    options.hinting = False
    options.notdef_outline = True
    options.glyph_names = False
    subsetter = Subsetter(options)
    subsetter.populate(text="".join(sorted(names)) + " ")
    subsetter.subset(instance)
    instance.flavor = "woff2"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    instance.save(args.out)
    print(f"{len(names)} icons kept, {args.out.stat().st_size} bytes -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
