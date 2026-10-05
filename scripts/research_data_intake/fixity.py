"""Standard fixity manifests (``checksums.sha256``) for archive units.

Format is the existing intake convention: sha256sum lines ``<64 hex>  <relative posix path>``, UTF-8, LF only,
sorted by path, never a drive letter, backslash or absolute path. Standalone on purpose so provenance and
preservation tooling can use it without importing the intake pipeline.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import re
from typing import Iterable

CHECKSUM_FILENAME = "checksums.sha256"
_LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")
_CHUNK = 1024 * 1024


class FixityError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_relative_path(relative_path: str) -> str:
    if not relative_path or "\\" in relative_path or relative_path.startswith("/") or re.match(r"^[A-Za-z]:", relative_path):
        raise FixityError(f"not a deterministic relative POSIX path: {relative_path!r}")
    parts = PurePosixPath(relative_path).parts
    if any(part in {"..", "."} for part in parts):
        raise FixityError(f"path escapes the unit root: {relative_path!r}")
    return relative_path


def list_unit_files(root: Path, *, exclude: Iterable[str] = ()) -> list[str]:
    """Sorted relative POSIX paths of all regular files below ``root`` (symlinks are not followed)."""
    excluded = set(exclude)
    result: list[str] = []
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort()
        for name in sorted(filenames):
            full = Path(current) / name
            if full.is_symlink() or not full.is_file():
                continue
            relative = full.relative_to(root).as_posix()
            if relative not in excluded:
                result.append(relative)
    return sorted(result)


def write_manifest(entries: dict[str, str], output_path: Path) -> None:
    lines = [f"{entries[path]}  {validate_relative_path(path)}" for path in sorted(entries)]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + ("\n" if lines else ""))


def read_manifest(manifest_path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    text = manifest_path.read_bytes().decode("utf-8")
    if "\r" in text:
        raise FixityError(f"{manifest_path.name}: CR characters are not allowed (LF only)")
    for number, line in enumerate(text.split("\n"), start=1):
        if not line:
            continue
        match = _LINE.match(line)
        if match is None:
            raise FixityError(f"{manifest_path.name}:{number}: malformed checksum line")
        relative = validate_relative_path(match.group(2))
        if relative in entries:
            raise FixityError(f"{manifest_path.name}:{number}: duplicate path {relative}")
        entries[relative] = match.group(1)
    return entries


def compute_manifest(root: Path, *, exclude: Iterable[str] = ()) -> dict[str, str]:
    return {relative: sha256_file(root / relative) for relative in list_unit_files(root, exclude=exclude)}


def verify_manifest(root: Path, entries: dict[str, str], *, check_extra: bool = True, exclude: Iterable[str] = ()) -> dict[str, list[str]]:
    """Compare ``entries`` with ``root``; returns ``missing``, ``mismatched``, ``unreadable`` and ``extra`` lists."""
    result: dict[str, list[str]] = {"missing": [], "mismatched": [], "unreadable": [], "extra": []}
    for relative, expected in sorted(entries.items()):
        path = root / relative
        if not path.is_file():
            result["missing"].append(relative)
            continue
        try:
            actual = sha256_file(path)
        except OSError:
            result["unreadable"].append(relative)
            continue
        if actual != expected:
            result["mismatched"].append(relative)
    if check_extra:
        known = set(entries) | set(exclude)
        result["extra"] = [path for path in list_unit_files(root) if path not in known]
    return result
