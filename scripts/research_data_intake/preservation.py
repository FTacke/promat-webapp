"""Institutional preservation layer for the local research archive (additive; never touches intake).

Model (see docs/spec/platform-data-files.md, "Archive provenance and preservation"):

* The local archive (``PROMAT_LOCAL_ARCHIVE_ROOT``) is a working archive. Writing to it is not preservation.
* A *preservation root* is a second, institutional filesystem location, configured through
  ``PROMAT_PRESERVATION_ROOT`` or ``--preservation-root``. Its current physical location is operational
  configuration, never architectural identity: nothing in this module knows a drive letter or a folder name,
  and the root is never defaulted.
* A unit (one session archive or one batch archive) is PRESERVED only after every file exists in the
  preservation root and was verified against *expected fixity* (a ``checksums.sha256`` of the unit, or an
  additive baseline). Copies are written to ``*.partial``, read back, and only then renamed. Nothing is ever
  deleted or silently overwritten here; this module contains no deletion of archive or source data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import shutil
import uuid
from typing import Any, Iterable

import fixity
import provenance as provenance_helpers

PRESERVATION_ROOT_ENV = "PROMAT_PRESERVATION_ROOT"
MARKER_FILENAME = "PRESERVATION_ROOT.json"
MARKER_SCHEMA = 1
RECEIPT_SCHEMA = "promat.preservation_receipt.v1"
BASELINE_RELATIVE = "fixity/baseline"
RECEIPTS_RELATIVE = "preservation/receipts"
DEST_ARCHIVE_DIR = "archive"
DEST_RECEIPTS_DIR = "_preservation/receipts"
PARTIAL_SUFFIX = ".partial"

STATE_ACTIVE_LOCAL = "ACTIVE_LOCAL"
STATE_PENDING = "PRESERVATION_PENDING"
STATE_PRESERVED = "PRESERVED"
STATE_CLEANUP_ELIGIBLE = "LOCAL_CLEANUP_ELIGIBLE"
STATES = (STATE_ACTIVE_LOCAL, STATE_PENDING, STATE_PRESERVED, STATE_CLEANUP_ELIGIBLE)

SCOPE_COMPLETE = "complete"
SCOPE_EXCLUDED_SECURE = "excluded_secure"




class PreservationError(RuntimeError):
    pass


class PreservationConfigError(PreservationError):
    pass


# ---------------------------------------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------------------------------------

def to_extended_windows_path(path: str) -> str:
    """Return the ``\\\\?\\`` long-path form of an absolute Windows path (pure string function, testable anywhere)."""
    if path.startswith("\\\\?\\"):
        return path
    if path.startswith("\\\\"):
        return "\\\\?\\UNC\\" + path[2:]
    if len(path) >= 3 and path[1] == ":" and path[2] in "\\/":
        return "\\\\?\\" + path.replace("/", "\\")
    return path


def fs_path(path: Path) -> Path:
    """Path to use for file operations; applies the extended form on Windows only."""
    if os.name == "nt":
        return Path(to_extended_windows_path(str(path)))
    return path


def unit_id_to_filename(unit_id: str) -> str:
    return unit_id.replace("/", "__")


# ---------------------------------------------------------------------------------------------------------
# Preservation root
# ---------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class PreservationRoot:
    path: Path
    root_id: str | None  # None when the root has no marker yet (dry-run before initialisation)

    @property
    def archive_dir(self) -> Path:
        return self.path / DEST_ARCHIVE_DIR

    @property
    def receipts_dir(self) -> Path:
        return self.path / DEST_RECEIPTS_DIR

    def unit_dir(self, unit_id: str) -> Path:
        return self.archive_dir / Path(*unit_id.split("/"))


def resolve_preservation_root_path(cli_value: str | Path | None) -> Path:
    configured = str(cli_value).strip() if cli_value else (os.getenv(PRESERVATION_ROOT_ENV) or "").strip()
    if not configured:
        raise PreservationConfigError(
            f"No preservation root configured. Set {PRESERVATION_ROOT_ENV} or pass --preservation-root. "
            "There is deliberately no default location."
        )
    return Path(configured).expanduser()


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def read_marker(root_path: Path) -> dict[str, Any] | None:
    marker_path = fs_path(root_path / MARKER_FILENAME)
    if not marker_path.is_file():
        return None
    try:
        payload = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PreservationConfigError(f"unreadable preservation root marker: {marker_path}") from exc
    if not isinstance(payload, dict) or not payload.get("root_id"):
        raise PreservationConfigError(f"invalid preservation root marker: {marker_path}")
    return payload


def open_preservation_root(root_path: Path, *, archive_root: Path, initialize: bool, migrated_from: Path | None = None) -> PreservationRoot:
    """Open a configured root. ``initialize`` (execute mode only) creates the directory, marker and write probe."""
    if _is_within(root_path, archive_root) or _is_within(archive_root, root_path):
        raise PreservationConfigError("The preservation root must be separate from the local archive root.")
    if not root_path.exists():
        if not initialize:
            return PreservationRoot(path=root_path, root_id=None)
        if not root_path.parent.exists():
            raise PreservationConfigError(
                f"Parent of the preservation root does not exist (is the volume reachable?): {root_path.parent}"
            )
        fs_path(root_path).mkdir(parents=False, exist_ok=True)
    marker = read_marker(root_path)
    if marker is None:
        if not initialize:
            return PreservationRoot(path=root_path, root_id=None)
        payload: dict[str, Any] = {
            "schema": MARKER_SCHEMA,
            "root_id": str(uuid.uuid4()),
            "created_at": provenance_helpers.utc_timestamp(),
            "note": "Identity of this preservation root. CURRENT PHYSICAL LOCATION - NOT ARCHITECTURAL IDENTITY: moving it needs a verified copy, integrity verification and a configuration change only.",
        }
        previous = read_marker(migrated_from) if migrated_from is not None else None
        if previous is not None:
            payload["migrated_from_root_id"] = previous["root_id"]
        fs_path(root_path / MARKER_FILENAME).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        marker = payload
    if initialize:
        assert_writable(root_path)
    return PreservationRoot(path=root_path, root_id=str(marker["root_id"]))


def assert_writable(directory: Path) -> None:
    probe = fs_path(directory / f".write-probe-{uuid.uuid4().hex}{PARTIAL_SUFFIX}")
    try:
        probe.write_bytes(b"promat")
        if probe.read_bytes() != b"promat":
            raise PreservationConfigError(f"write probe read back differently in {directory}")
    except OSError as exc:
        raise PreservationConfigError(f"preservation root is not writable: {directory} ({exc})") from exc
    finally:
        try:
            probe.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------------------------------------------------
# Units and expected fixity
# ---------------------------------------------------------------------------------------------------------

def discover_units(archive_root: Path) -> list[str]:
    units: list[str] = []
    sessions = archive_root / "sessions"
    if sessions.is_dir():
        for language_dir in sorted(p for p in sessions.iterdir() if p.is_dir()):
            units.extend(f"sessions/{language_dir.name}/{p.name}" for p in sorted(language_dir.iterdir()) if p.is_dir())
    batches = archive_root / "batches"
    if batches.is_dir():
        units.extend(f"batches/{p.name}" for p in sorted(batches.iterdir()) if p.is_dir())
    return units


def unit_path(archive_root: Path, unit_id: str) -> Path:
    return archive_root / Path(*unit_id.split("/"))


def unit_manifest_relative(unit_id: str) -> str:
    return "metadata/checksums.sha256" if unit_id.startswith("sessions/") else fixity.CHECKSUM_FILENAME


def baseline_path(archive_root: Path, unit_id: str) -> Path:
    return archive_root / Path(BASELINE_RELATIVE) / f"{unit_id_to_filename(unit_id)}.sha256"


@dataclass
class ExpectedFixity:
    entries: dict[str, str]
    origin: str  # "baseline" | "unit_manifest"
    manifest_sha256: str


def manifest_digest(entries: dict[str, str]) -> str:
    text = "".join(f"{entries[path]}  {path}\n" for path in sorted(entries))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolve_expected_fixity(archive_root: Path, unit_id: str) -> ExpectedFixity | None:
    """Expected fixity of a unit: its additive baseline, else a unit manifest that covers every file; else None."""
    root = unit_path(archive_root, unit_id)
    baseline = baseline_path(archive_root, unit_id)
    if baseline.is_file():
        entries = fixity.read_manifest(baseline)
        return ExpectedFixity(entries, "baseline", manifest_digest(entries))
    manifest_relative = unit_manifest_relative(unit_id)
    manifest_file = root / manifest_relative
    if not manifest_file.is_file():
        return None
    try:
        entries = fixity.read_manifest(manifest_file)
    except fixity.FixityError:
        return None
    files = set(fixity.list_unit_files(root))
    if set(entries) != files - {manifest_relative}:
        return None  # incomplete coverage: a baseline is needed
    entries[manifest_relative] = fixity.sha256_file(manifest_file)
    return ExpectedFixity(entries, "unit_manifest", manifest_digest(entries))


def _is_secure(relative: str) -> bool:
    return relative == "secure" or relative.startswith("secure/")


# ---------------------------------------------------------------------------------------------------------
# Baseline (additive fixity for existing archives)
# ---------------------------------------------------------------------------------------------------------

def baseline_unit(archive_root: Path, unit_id: str, *, execute: bool) -> dict[str, Any]:
    """Create fixity for one existing unit without touching any of its files."""
    root = unit_path(archive_root, unit_id)
    result: dict[str, Any] = {"unit": unit_id, "files": 0, "bytes": 0, "unreadable": [], "status": ""}
    existing = baseline_path(archive_root, unit_id)
    if existing.is_file():
        entries = fixity.read_manifest(existing)
        check = fixity.verify_manifest(root, entries)
        drift = {key: value for key, value in check.items() if value}
        result.update(files=len(entries), status="baseline_drift" if drift else "baseline_present", drift=drift)
        return result
    expected = resolve_expected_fixity(archive_root, unit_id)
    if expected is not None and expected.origin == "unit_manifest":
        check = fixity.verify_manifest(root, expected.entries)
        drift = {key: value for key, value in check.items() if value}
        result.update(files=len(expected.entries), status="unit_manifest_drift" if drift else "covered_by_unit_manifest", drift=drift)
        return result
    entries = {}
    for relative in fixity.list_unit_files(root):
        file_path = root / relative
        try:
            entries[relative] = fixity.sha256_file(fs_path(file_path))
            result["bytes"] += fs_path(file_path).stat().st_size
        except OSError as exc:
            result["unreadable"].append({"path": relative, "error": str(exc)})
    result["files"] = len(entries)
    if result["unreadable"]:
        result["status"] = "incomplete_unreadable_files"  # no baseline: it would claim fixity for a partial unit
        return result
    result["status"] = "would_write_baseline" if not execute else "baseline_written"
    if execute:
        fixity.write_manifest(entries, existing)
        meta = {
            "unit": unit_id,
            "created_at": provenance_helpers.utc_timestamp(),
            "git_revision": provenance_helpers.current_git_revision(),
            "file_count": len(entries),
            "total_bytes": result["bytes"],
            "manifest_sha256": manifest_digest(entries),
            "note": "Additive baseline of an archive unit that predates fixity manifests. Records current content, not historical correctness.",
        }
        existing.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return result


# ---------------------------------------------------------------------------------------------------------
# Verified copy
# ---------------------------------------------------------------------------------------------------------

FILE_STATUSES = (
    "copied",
    "already_present",
    "would_copy",
    "conflict_destination_mismatch",
    "source_missing",
    "source_mismatch",
    "case_collision",
    "error",
)


def copy_file_verified(source: Path, destination: Path, expected_sha256: str, *, execute: bool) -> dict[str, Any]:
    """Copy one file only if source and destination content match ``expected_sha256`` end to end.

    Order: verify source -> write ``*.partial`` -> read back -> atomic rename. An existing destination with
    other content is a conflict and is never overwritten.
    """
    src, dst = fs_path(source), fs_path(destination)
    record: dict[str, Any] = {"path": None, "sha256": expected_sha256}
    if not src.is_file():
        return {**record, "status": "source_missing"}
    try:
        if dst.is_file():
            if fixity.sha256_file(dst) == expected_sha256:
                return {**record, "status": "already_present"}
            return {**record, "status": "conflict_destination_mismatch"}
        if not execute:
            if fixity.sha256_file(src) != expected_sha256:
                return {**record, "status": "source_mismatch"}
            return {**record, "status": "would_copy"}
        dst.parent.mkdir(parents=True, exist_ok=True)
        partial = dst.with_name(dst.name + PARTIAL_SUFFIX)
        if partial.exists():
            partial.unlink()  # an interrupted earlier run; it is never trusted, only replaced
        digest = hashlib.sha256()
        with src.open("rb") as reader, partial.open("wb") as writer:
            for chunk in iter(lambda: reader.read(1024 * 1024), b""):
                digest.update(chunk)
                writer.write(chunk)
            writer.flush()
            os.fsync(writer.fileno())
        if digest.hexdigest() != expected_sha256:
            partial.unlink()
            return {**record, "status": "source_mismatch"}
        if fixity.sha256_file(partial) != expected_sha256:  # read-back from the destination volume
            partial.unlink()
            return {**record, "status": "error", "error": "read-back verification of the partial copy failed"}
        shutil.copystat(src, partial)
        os.replace(partial, dst)
        return {**record, "status": "copied"}
    except OSError as exc:
        return {**record, "status": "error", "error": str(exc)}


def _case_collisions(paths: Iterable[str]) -> set[str]:
    seen: dict[str, str] = {}
    collisions: set[str] = set()
    for path in paths:
        key = path.lower()
        if key in seen and seen[key] != path:
            collisions.update({seen[key], path})
        seen.setdefault(key, path)
    return collisions


@dataclass
class UnitCopyResult:
    unit: str
    scope: str
    status: str = "pending"  # preserved | would_preserve | incomplete | failed
    files: list[dict[str, Any]] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    receipt_path: str | None = None


def copy_unit(
    archive_root: Path,
    unit_id: str,
    root: PreservationRoot,
    *,
    execute: bool,
    exclude_secure: bool = False,
) -> UnitCopyResult:
    scope = SCOPE_EXCLUDED_SECURE if exclude_secure else SCOPE_COMPLETE
    result = UnitCopyResult(unit=unit_id, scope=scope)
    expected = resolve_expected_fixity(archive_root, unit_id)
    if expected is None:
        result.status = "failed"
        result.problems.append("no expected fixity: run the baseline command first")
        return result
    source_root = unit_path(archive_root, unit_id)
    dest_root = root.unit_dir(unit_id)
    paths = sorted(expected.entries)
    if exclude_secure:
        paths = [path for path in paths if not _is_secure(path)]
    collisions = _case_collisions(paths)
    # Files in the unit that fixity does not cover would be silently left behind: refuse instead.
    uncovered = [p for p in fixity.list_unit_files(source_root) if p not in expected.entries]
    if uncovered:
        result.status = "failed"
        result.problems.append(f"files without expected fixity (re-baseline is additive-only; investigate): {uncovered[:5]}")
        return result
    for relative in paths:
        if relative in collisions:
            result.files.append({"path": relative, "status": "case_collision"})
            continue
        outcome = copy_file_verified(source_root / relative, dest_root / relative, expected.entries[relative], execute=execute)
        outcome["path"] = relative
        result.files.append(outcome)
    bad = [f for f in result.files if f["status"] not in {"copied", "already_present", "would_copy"}]
    if bad:
        result.status = "failed"
        result.problems.extend(f"{f['path']}: {f['status']}" for f in bad[:20])
        return result
    if not execute:
        result.status = "would_preserve"
        return result
    verification = verify_destination(root, unit_id, expected, scope=scope)
    if not verification["ok"]:
        result.status = "failed"
        result.problems.append(f"post-copy verification failed: { {k: v[:5] for k, v in verification.items() if isinstance(v, list) and v} }")
        return result
    result.status = "preserved" if scope == SCOPE_COMPLETE else "incomplete"
    receipt = write_receipt(archive_root, root, unit_id, expected, scope=scope, verification=verification)
    result.receipt_path = str(receipt)
    return result


def verify_destination(root: PreservationRoot, unit_id: str, expected: ExpectedFixity, *, scope: str = SCOPE_COMPLETE) -> dict[str, Any]:
    entries = expected.entries
    if scope == SCOPE_EXCLUDED_SECURE:
        entries = {p: h for p, h in entries.items() if not _is_secure(p)}
    dest = root.unit_dir(unit_id)
    check = fixity.verify_manifest(fs_path(dest), entries, check_extra=True)
    partials = [p for p in check["extra"] if p.endswith(PARTIAL_SUFFIX)]
    check["extra"] = [p for p in check["extra"] if p not in partials]
    return {
        **check,
        "partial_files": partials,
        "file_count": len(entries),
        "total_bytes": sum((dest / p).stat().st_size for p in entries if (dest / p).is_file()),
        "ok": not (check["missing"] or check["mismatched"] or check["unreadable"] or partials),
    }


# ---------------------------------------------------------------------------------------------------------
# Receipts and states
# ---------------------------------------------------------------------------------------------------------

def receipt_filename(unit_id: str) -> str:
    return f"{unit_id_to_filename(unit_id)}.json"


def local_receipt_path(archive_root: Path, unit_id: str) -> Path:
    return archive_root / Path(RECEIPTS_RELATIVE) / receipt_filename(unit_id)


def write_receipt(
    archive_root: Path,
    root: PreservationRoot,
    unit_id: str,
    expected: ExpectedFixity,
    *,
    scope: str,
    verification: dict[str, Any],
) -> Path:
    payload = {
        "schema": RECEIPT_SCHEMA,
        "unit": unit_id,
        "scope": scope,
        "root_id": root.root_id,
        "verified_at": provenance_helpers.utc_timestamp(),
        "verification": "full_sha256_readback",
        "expected_fixity_origin": expected.origin,
        "manifest_sha256": expected.manifest_sha256,
        "file_count": verification["file_count"],
        "total_bytes": verification["total_bytes"],
        "tool_revision": provenance_helpers.current_git_revision(),
        "destination_hint": str(root.path),  # informational only; identity is root_id
    }
    text = json.dumps(payload, indent=2) + "\n"
    local = local_receipt_path(archive_root, unit_id)
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_text(text, encoding="utf-8")
    remote = fs_path(root.receipts_dir / receipt_filename(unit_id))
    remote.parent.mkdir(parents=True, exist_ok=True)
    remote.write_text(text, encoding="utf-8")
    return local


def derive_state(
    archive_root: Path,
    unit_id: str,
    root: PreservationRoot | None,
    *,
    full_verify: bool,
) -> dict[str, Any]:
    """State of one unit with the evidence it rests on. Pure read; never modifies anything."""
    evidence: dict[str, Any] = {}
    reasons: list[str] = []
    expected = resolve_expected_fixity(archive_root, unit_id)
    if expected is None:
        return {"unit": unit_id, "state": STATE_ACTIVE_LOCAL, "reasons": ["no expected fixity (baseline missing)"], "evidence": evidence}
    evidence["expected_fixity_origin"] = expected.origin
    evidence["manifest_sha256"] = expected.manifest_sha256
    state = STATE_PENDING
    if root is None or root.root_id is None:
        reasons.append("preservation root not configured or not initialised")
        return {"unit": unit_id, "state": state, "reasons": reasons, "evidence": evidence}
    receipt_file = local_receipt_path(archive_root, unit_id)
    if not receipt_file.is_file():
        reasons.append("no preservation receipt")
        return {"unit": unit_id, "state": state, "reasons": reasons, "evidence": evidence}
    try:
        receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        reasons.append("unreadable preservation receipt")
        return {"unit": unit_id, "state": state, "reasons": reasons, "evidence": evidence}
    evidence["receipt"] = str(receipt_file)
    if receipt.get("scope") != SCOPE_COMPLETE:
        reasons.append(f"receipt scope is {receipt.get('scope')!r}: scope-limited copies never count as preserved")
    elif receipt.get("root_id") != root.root_id:
        reasons.append("receipt belongs to a different preservation root (root changed: re-run the verified copy)")
    elif receipt.get("manifest_sha256") != expected.manifest_sha256:
        reasons.append("archive unit changed after the receipt (manifest hash differs)")
    else:
        dest = fs_path(root.unit_dir(unit_id))
        if full_verify:
            verification = verify_destination(root, unit_id, expected)
            evidence["destination_check"] = "full_sha256"
            ok = verification["ok"]
            if not ok:
                reasons.append("destination verification failed: " + ", ".join(f"{k}={len(v)}" for k, v in verification.items() if isinstance(v, list) and v and k != "extra"))
        else:
            evidence["destination_check"] = "exists_and_size_only"
            ok = all(
                (dest / p).is_file() and (dest / p).stat().st_size == (unit_path(archive_root, unit_id) / p).stat().st_size
                for p in expected.entries
                if (unit_path(archive_root, unit_id) / p).is_file()
            )
            if not ok:
                reasons.append("destination files missing or of different size")
        if ok:
            state = STATE_PRESERVED
            if full_verify:
                local_check = fixity.verify_manifest(unit_path(archive_root, unit_id), expected.entries, check_extra=False)
                local_ok = not any(local_check.values())
                separate = not _is_within(root.path, archive_root)
                evidence["local_matches_fixity"] = local_ok
                evidence["destination_separate_from_local_archive"] = separate
                if local_ok and separate:
                    state = STATE_CLEANUP_ELIGIBLE
                else:
                    reasons.append("local copy does not match expected fixity; investigate before any cleanup" if not local_ok else "destination is not separate")
    return {"unit": unit_id, "state": state, "reasons": reasons, "evidence": evidence}


# ---------------------------------------------------------------------------------------------------------
# Cleanup-eligibility report (report only)
# ---------------------------------------------------------------------------------------------------------

CLEANUP_SCHEMA = "promat.cleanup_eligibility.v1"


def cleanup_eligibility_report(
    archive_root: Path,
    root: PreservationRoot | None,
    *,
    candidate_dirs: Iterable[Path] = (),
) -> dict[str, Any]:
    """Compute which local data is duplicated by fully verified preserved units. Never deletes anything.

    ``candidate_dirs`` are local trees (for example batch working folders) whose files are matched by SHA-256
    against the preserved units only; matched files are *duplicates of preserved content*, not an instruction.
    """
    units = [derive_state(archive_root, unit, root, full_verify=True) for unit in discover_units(archive_root)]
    eligible = [u for u in units if u["state"] == STATE_CLEANUP_ELIGIBLE]
    preserved_files: dict[tuple[int, str], str] = {}
    for unit in eligible:
        expected = resolve_expected_fixity(archive_root, unit["unit"])
        if expected is None:
            continue
        base = unit_path(archive_root, unit["unit"])
        for relative, sha in expected.entries.items():
            preserved_files[((base / relative).stat().st_size, sha)] = f"{unit['unit']}/{relative}"
    sizes = {size for size, _ in preserved_files}
    candidates: list[dict[str, Any]] = []
    for directory in candidate_dirs:
        entry: dict[str, Any] = {"directory_name": directory.name, "duplicates": [], "not_covered": [], "unreadable": []}
        for relative in fixity.list_unit_files(directory):
            file_path = directory / relative
            try:
                size = file_path.stat().st_size
                if size not in sizes:
                    entry["not_covered"].append({"path": relative, "size": size})
                    continue
                sha = fixity.sha256_file(file_path)
            except OSError as exc:
                entry["unreadable"].append({"path": relative, "error": str(exc)})
                continue
            match = preserved_files.get((size, sha))
            if match:
                entry["duplicates"].append({"path": relative, "size": size, "sha256": sha, "preserved_as": match})
            else:
                entry["not_covered"].append({"path": relative, "size": size})
        candidates.append(entry)
    counts = {state: sum(1 for u in units if u["state"] == state) for state in STATES}
    return {
        "schema": CLEANUP_SCHEMA,
        "generated_at": provenance_helpers.utc_timestamp(),
        "deletes_anything": False,
        "note": "Report only. Eligibility is not an instruction; deleting preserved source material is an explicit operator action.",
        "preservation_root_id": root.root_id if root else None,
        "counts": counts,
        "units": units,
        "candidate_directories": candidates,
    }
