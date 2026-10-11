"""Web derivatives of the raster illustrations of the Teaching topic pages.

A raster illustration (PNG or JPEG) under ``content/teaching/{language}/{topic}/media/images/`` is the **master**: it
stays untouched in full resolution. For delivery, a WebP derivative with the same stem sits beside it
(``name.png`` -> ``name.webp``); the shared ``image`` block of the topic pages serves it through ``<picture>`` and keeps
the master as the fallback. The derivatives are declared in ``content/teaching/image-derivatives.yaml`` (master
SHA-256, derivative SHA-256, width, quality), so a changed master or a stale derivative is caught by ``--check``.

    python scripts/teaching_images.py --build [--width 960] [--quality 92]   # (re)build missing or changed derivatives
    python scripts/teaching_images.py --check                                # verify declaration, files and hashes

Parameters are chosen per illustration by looking at the result (see ``docs/runbooks/teaching-illustrations.md``), not
fixed globally: width = 2 x the widest CSS display width (the figure is at most 30 rem = 480 px, so 960 px), never
upscaled; quality as low as stays visually indistinguishable at 2x zoom. Vector images (SVG) need no derivative.

``--build`` needs ``pip install Pillow``; ``--check`` needs only PyYAML.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import struct
import sys
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "content" / "teaching"
MANIFEST = CONTENT_ROOT / "image-derivatives.yaml"
MASTER_SUFFIXES = {".png", ".jpg", ".jpeg"}
DEFAULT_WIDTH = 960
DEFAULT_QUALITY = 92
HEADER = """# Web derivatives (WebP) of the raster illustrations of the Teaching topic pages (declaration; see scripts/teaching_images.py).
#
# The master (PNG/JPEG) stays untouched; the derivative beside it is what the shared image block delivers. Rebuild with
# `python scripts/teaching_images.py --build` after replacing a master; `--check` (and a pytest) fails on a stale entry.
"""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def masters() -> list[Path]:
    """Every raster illustration below ``content/teaching/*/*/media/images/``."""
    found = [path for path in CONTENT_ROOT.glob("*/*/media/images/**/*") if path.is_file() and path.suffix.lower() in MASTER_SUFFIXES]
    return sorted(found)


def rel(path: Path) -> str:
    return path.relative_to(CONTENT_ROOT).as_posix()


def derivative_of(master: Path) -> Path:
    return master.with_suffix(".webp")


def png_size(path: Path) -> tuple[int, int] | None:
    """(width, height) from the PNG header without an imaging library; ``None`` for other formats."""
    with path.open("rb") as handle:
        head = handle.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


def webp_size(path: Path) -> tuple[int, int] | None:
    """(width, height) of a WebP file (VP8, VP8L or VP8X) without an imaging library."""
    with path.open("rb") as handle:
        head = handle.read(40)
    if len(head) < 30 or head[:4] != b"RIFF" or head[8:12] != b"WEBP":
        return None
    kind = head[12:16]
    if kind == b"VP8 ":
        width, height = struct.unpack("<HH", head[26:30])
        return width & 0x3FFF, height & 0x3FFF
    if kind == b"VP8L":
        bits = int.from_bytes(head[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if kind == b"VP8X":
        return int.from_bytes(head[24:27], "little") + 1, int.from_bytes(head[27:30], "little") + 1
    return None


def load_manifest() -> dict[str, Any]:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {} if MANIFEST.is_file() else {}


def dump_manifest(data: dict[str, Any]) -> None:
    MANIFEST.write_text(HEADER + "\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8", newline="\n")


def check(data: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    entries = {entry.get("master"): entry for entry in data.get("derivatives") or []}
    for master in masters():
        key = rel(master)
        entry = entries.pop(key, None)
        if entry is None:
            problems.append(f"{key}: raster illustration has no declared WebP derivative (run --build)")
            continue
        target = derivative_of(master)
        if rel(target) != entry.get("derivative"):
            problems.append(f"{key}: declared derivative {entry.get('derivative')!r} is not {rel(target)!r}")
        if sha256_of(master) != entry.get("master_sha256"):
            problems.append(f"{key}: master changed since the derivative was built (run --build); masters are never edited in place")
        if not target.is_file():
            problems.append(f"{rel(target)}: derivative missing")
            continue
        if sha256_of(target) != entry.get("derivative_sha256"):
            problems.append(f"{rel(target)}: sha256 differs from the declaration (run --build)")
        master_size, target_size = png_size(master), webp_size(target)
        if master_size and target_size:
            if abs(master_size[0] * target_size[1] - master_size[1] * target_size[0]) > max(master_size[0], master_size[1]):
                problems.append(f"{rel(target)}: aspect ratio {target_size} differs from the master {master_size}")
            if target_size[0] > master_size[0]:
                problems.append(f"{rel(target)}: derivative is wider than its master (never upscale)")
        if target.stat().st_size >= master.stat().st_size:
            problems.append(f"{rel(target)}: derivative is not smaller than its master")
    for key in sorted(entries):
        problems.append(f"{key}: declared master no longer exists")
    return problems


def build(data: dict[str, Any], width: int, quality: int, only: list[str]) -> list[str]:
    try:
        from PIL import Image
    except ImportError:  # pragma: no cover - dev tool
        return ["Pillow is required for --build (pip install Pillow)"]
    entries = {entry["master"]: entry for entry in data.get("derivatives") or []}
    for master in masters():
        key = rel(master)
        if only and key not in only and master.name not in only:
            continue
        previous = entries.get(key) or {}
        # keep the parameters of an existing entry unless they are given explicitly on the command line
        use_width = width or previous.get("width") or DEFAULT_WIDTH
        use_quality = quality or previous.get("quality") or DEFAULT_QUALITY
        with Image.open(master) as image:
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            target_width = min(use_width, image.width)
            target_height = round(image.height * target_width / image.width)
            resized = image if target_width == image.width else image.resize((target_width, target_height), Image.LANCZOS)
            target = derivative_of(master)
            resized.save(target, "WEBP", quality=use_quality, method=6)
        entries[key] = {
            "master": key,
            "master_sha256": sha256_of(master),
            "derivative": rel(target),
            "derivative_sha256": sha256_of(target),
            "width": target_width,
            "quality": use_quality,
        }
        print(f"{key}: {master.stat().st_size // 1024} KB -> {target.stat().st_size // 1024} KB ({target_width} x {target_height}, q{use_quality})")
    data["derivatives"] = [entries[key] for key in sorted(entries)]
    dump_manifest(data)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--build", action="store_true", help="build the WebP derivatives and refresh the declaration")
    parser.add_argument("--check", action="store_true", help="verify the declaration (default)")
    parser.add_argument("--width", type=int, default=0, help=f"derivative width in px (default {DEFAULT_WIDTH}, never above the master)")
    parser.add_argument("--quality", type=int, default=0, help=f"WebP quality (default {DEFAULT_QUALITY})")
    parser.add_argument("only", nargs="*", help="limit --build to these masters (path below content/teaching or file name)")
    args = parser.parse_args()
    data = load_manifest()
    if args.build:
        problems = build(data, args.width, args.quality, args.only)
        print("built" if not problems else "build failed")
    else:
        problems = check(data)
        print("image derivatives OK" if not problems else "image derivatives FAILED")
    for problem in problems:
        print(" -", problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
