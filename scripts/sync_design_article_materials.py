"""Copy a corpus's elicitation materials from its task catalogs into the versioned design-article content.

Contract: docs/spec/platform-data-files.md, "Research design articles"; procedure: docs/runbooks/design-article-import.md.

A design article must render without the operator-owned runtime catalogs (CI, image smoke), so it ships its own copy of
the wordlist, exactly as the task catalog stores it: same order, item ids, item numbers and spellings,
nothing corrected or merged. ``app/tests/test_design_page_catalog_parity.py`` fails as soon as copy and catalog diverge.

Usage::

    python scripts/sync_design_article_materials.py --corpus english
    python scripts/sync_design_article_materials.py --corpus english --check
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
#: Catalog tasks shown with the article (the reading text is shown as the author's own example, not from the catalog).
TASKS = ("wordlist",)


def catalog_dir(corpus: str) -> Path:
    return REPO_ROOT / "data" / "config" / "research_player" / corpus / "task_catalogs"


def build_materials(corpus: str) -> dict[str, object]:
    materials: dict[str, object] = {}
    for task in TASKS:
        path = catalog_dir(corpus) / f"{task}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("task") != task or payload.get("language") != corpus:
            raise SystemExit(f"{path} is not the {task} catalog of {corpus}")
        materials[task] = {
            "source": path.relative_to(REPO_ROOT).as_posix(),
            "items": [
                {"item_id": item["item_id"], "item_number": str(item["item_number"]), "text": item["text"]}
                for item in payload["items"]
            ],
        }
    return materials


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--corpus", required=True, help="corpus slug, e.g. english")
    parser.add_argument("--check", action="store_true", help="do not write; fail if the content copy differs")
    args = parser.parse_args(argv)

    out_path = REPO_ROOT / "content" / "research" / args.corpus / "design_materials.json"
    payload = {
        "_generated": {
            "by": "scripts/sync_design_article_materials.py",
            "note": "Verbatim copy of the corpus task catalogs. Do not edit by hand; re-run the sync after a catalog change.",
        },
        **build_materials(args.corpus),
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        current = out_path.read_text(encoding="utf-8") if out_path.is_file() else ""
        if current != rendered:
            print(f"{out_path} differs from the task catalogs", file=sys.stderr)
            return 1
        print(f"{out_path} matches the task catalogs")
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
