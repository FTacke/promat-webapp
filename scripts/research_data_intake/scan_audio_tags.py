"""Read-only scan of the tags in runtime MP3 files, and an in-place metadata-only clean for derived web audio.

    python scripts/research_data_intake/scan_audio_tags.py --root data/sessions
    python scripts/research_data_intake/scan_audio_tags.py --root data/sessions --clean

The scan prints counts per frame id, per corpus and per value *pattern* (letters replaced by ``a``, digits by
``9``), never the tag values themselves; no names enter logs or reports. ``--clean`` rewrites only files that
violate the policy in ``audio_tags.py`` (atomic replace, MPEG frames unchanged) and only below ``--root``;
archive/source/secure trees are refused. Exit code 1 means disallowed tags remain.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audio_tags import read_tags, strip_tags  # noqa: E402

FORBIDDEN_ROOT_PARTS = {"secure", "raw", "source", "alignment_source", "archive", "batches"}


def _pattern(value: str) -> str:
    return re.sub(r"\d", "9", re.sub(r"[^\W\d_]", "a", value, flags=re.UNICODE))[:40]


def _mp3_files(root: Path):
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name.lower().endswith(".mp3"):
                yield Path(dirpath) / name


def _audio_digest(path: Path) -> str:
    report = read_tags(path)
    data = path.read_bytes()
    end = len(data) - 128 if report.id3v1 else len(data)
    return hashlib.sha256(data[report.id3v2_size : end]).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, type=Path, help="runtime sessions root (data/sessions)")
    parser.add_argument("--clean", action="store_true", help="strip disallowed tags in place (frames unchanged)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if FORBIDDEN_ROOT_PARTS & {part.lower() for part in root.parts}:
        print("refusing to touch an archive/source/secure tree", file=sys.stderr)
        return 2

    total = 0
    frames: Counter[str] = Counter()
    patterns: Counter[str] = Counter()
    corpora: Counter[str] = Counter()
    sessions: set[str] = set()
    bad_files: list[Path] = []
    tagged = 0
    for path in _mp3_files(root):
        total += 1
        report = read_tags(path)
        if report.id3v2_frames or report.id3v1 or report.apev2:
            tagged += 1
        for frame_id, values in report.id3v2_frames.items():
            frames[frame_id] += 1
            if frame_id in {"TIT2", "TPE1", "TALB", "COMM", "TXXX"}:
                for value in values:
                    patterns[f"{frame_id}:{_pattern(value)}"] += 1
        if report.id3v1:
            frames["ID3v1"] += 1
        if report.apev2:
            frames["APEv2"] += 1
        if report.disallowed:
            bad_files.append(path)
            relative = path.relative_to(root).parts
            corpora[relative[0] if relative else "?"] += 1
            if len(relative) > 1:
                sessions.add("/".join(relative[:2]))

    print(f"mp3 files: {total}; with any tag: {tagged}; violating policy: {len(bad_files)}")
    print("frames:", dict(sorted(frames.items())))
    print("violating files per corpus:", dict(sorted(corpora.items())), "| sessions affected:", len(sessions))
    print("value patterns (top 12):", patterns.most_common(12))

    if args.clean and bad_files:
        for path in bad_files:
            before = _audio_digest(path)
            temp = path.with_suffix(".mp3.clean")
            strip_tags(path, temp)
            if _audio_digest(temp) != before:
                temp.unlink(missing_ok=True)
                raise SystemExit(f"audio frames changed while cleaning {path.name}; aborted")
            os.replace(temp, path)
        remaining = sum(1 for path in _mp3_files(root) if read_tags(path).disallowed)
        print(f"cleaned: {len(bad_files)}; violating after clean: {remaining}")
        return 1 if remaining else 0
    return 1 if bad_files else 0


if __name__ == "__main__":
    raise SystemExit(main())
