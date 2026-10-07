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
* A *backup root* (``PROMAT_BACKUP_ROOT`` or ``--backup-root``) is a physically separate copy made by the same
  verified copy. It is a different role (``RootRole``): its own marker file, receipts and states, it never makes
  a unit PRESERVED or cleanup-eligible, and a directory marked as one role is refused as the other.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import uuid
from typing import Any, Iterable

import fixity
import provenance as provenance_helpers
import storage_roots

PRESERVATION_ROOT_ENV = storage_roots.PRESERVATION_ROOT_ENV
BACKUP_ROOT_ENV = storage_roots.BACKUP_ROOT_ENV
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

STATE_BACKUP_PENDING = "BACKUP_PENDING"
STATE_BACKED_UP = "BACKED_UP"

SCOPE_COMPLETE = "complete"
SCOPE_EXCLUDED_SECURE = "excluded_secure"


@dataclass(frozen=True)
class RootRole:
    """What a destination root is. The two roles share the verified copy and nothing else."""

    name: str
    env: str
    cli_option: str
    marker_filename: str
    receipt_schema: str
    local_receipts: str  # relative to the local archive root
    dest_receipts: str  # relative to the destination root
    pending_state: str
    done_state: str
    planned_status: str
    done_status: str
    grants_cleanup: bool

    @property
    def states(self) -> tuple[str, ...]:
        states = (STATE_ACTIVE_LOCAL, self.pending_state, self.done_state)
        return states + ((STATE_CLEANUP_ELIGIBLE,) if self.grants_cleanup else ())


PRESERVATION = RootRole(
    name="preservation",
    env=PRESERVATION_ROOT_ENV,
    cli_option="--preservation-root",
    marker_filename=MARKER_FILENAME,
    receipt_schema=RECEIPT_SCHEMA,
    local_receipts=RECEIPTS_RELATIVE,
    dest_receipts=DEST_RECEIPTS_DIR,
    pending_state=STATE_PENDING,
    done_state=STATE_PRESERVED,
    planned_status="would_preserve",
    done_status="preserved",
    grants_cleanup=True,
)
BACKUP = RootRole(
    name="backup",
    env=BACKUP_ROOT_ENV,
    cli_option="--backup-root",
    marker_filename="BACKUP_ROOT.json",
    receipt_schema="promat.backup_receipt.v1",
    local_receipts="backup/receipts",
    dest_receipts="_backup/receipts",
    pending_state=STATE_BACKUP_PENDING,
    done_state=STATE_BACKED_UP,
    planned_status="would_back_up",
    done_status="backed_up",
    grants_cleanup=False,
)
ROLES = (PRESERVATION, BACKUP)



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
    role: RootRole = PRESERVATION

    @property
    def archive_dir(self) -> Path:
        return self.path / DEST_ARCHIVE_DIR

    @property
    def receipts_dir(self) -> Path:
        return self.path / self.role.dest_receipts

    def unit_dir(self, unit_id: str) -> Path:
        return self.archive_dir / Path(*unit_id.split("/"))


def resolve_preservation_root_path(cli_value: str | Path | None, role: RootRole = PRESERVATION) -> Path:
    configured = str(cli_value).strip() if cli_value else (storage_roots.configured_value(role.env) or "")
    if not configured:
        raise PreservationConfigError(
            f"No {role.name} root configured. Set {role.env} or pass {role.cli_option}. "
            "There is deliberately no default location."
        )
    return Path(configured).expanduser()


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def read_marker(root_path: Path, role: RootRole = PRESERVATION) -> dict[str, Any] | None:
    marker_path = fs_path(root_path / role.marker_filename)
    if not marker_path.is_file():
        return None
    try:
        payload = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PreservationConfigError(f"unreadable {role.name} root marker: {marker_path}") from exc
    if not isinstance(payload, dict) or not payload.get("root_id"):
        raise PreservationConfigError(f"invalid {role.name} root marker: {marker_path}")
    # Markers written before roles existed carry no role; only preservation roots existed then.
    if payload.get("role", PRESERVATION.name) != role.name:
        raise PreservationConfigError(f"{marker_path} declares the role {payload.get('role')!r}, not {role.name!r}")
    return payload


def _refuse_other_role(root_path: Path, role: RootRole) -> None:
    """A directory is one role only: refuse a root that is marked, or configured, as the other role."""
    for other in ROLES:
        if other is role:
            continue
        if fs_path(root_path / other.marker_filename).is_file():
            raise PreservationConfigError(
                f"{root_path} is a {other.name} root ({other.marker_filename} is present); it cannot be used as the {role.name} root."
            )
        try:
            other_path = storage_roots.configured_root(other.env)
        except storage_roots.StorageRootNotConfigured:
            other_path = None
        if other_path is not None and (_is_within(root_path, other_path) or _is_within(other_path, root_path)):
            raise PreservationConfigError(
                f"The {role.name} root must be separate from the configured {other.name} root ({other.env})."
            )


def open_preservation_root(
    root_path: Path,
    *,
    archive_root: Path,
    initialize: bool,
    migrated_from: Path | None = None,
    role: RootRole = PRESERVATION,
) -> PreservationRoot:
    """Open a configured root. ``initialize`` (execute mode only) creates the directory, marker and write probe."""
    if _is_within(root_path, archive_root) or _is_within(archive_root, root_path):
        raise PreservationConfigError(f"The {role.name} root must be separate from the local archive root.")
    _refuse_other_role(root_path, role)
    if not root_path.exists():
        if not initialize:
            return PreservationRoot(path=root_path, root_id=None, role=role)
        if not root_path.parent.exists():
            raise PreservationConfigError(
                f"Parent of the {role.name} root does not exist (is the volume reachable?): {root_path.parent}"
            )
        fs_path(root_path).mkdir(parents=False, exist_ok=True)
    marker = read_marker(root_path, role)
    if marker is None:
        if not initialize:
            return PreservationRoot(path=root_path, root_id=None, role=role)
        payload: dict[str, Any] = {
            "schema": MARKER_SCHEMA,
            "role": role.name,
            "root_id": str(uuid.uuid4()),
            "created_at": provenance_helpers.utc_timestamp(),
            "note": f"Identity of this {role.name} root. CURRENT PHYSICAL LOCATION - NOT ARCHITECTURAL IDENTITY: moving it needs a verified copy, integrity verification and a configuration change only.",
        }
        previous = read_marker(migrated_from, role) if migrated_from is not None else None
        if previous is not None:
            payload["migrated_from_root_id"] = previous["root_id"]
        fs_path(root_path / role.marker_filename).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        marker = payload
    if initialize:
        assert_writable(root_path)
    return PreservationRoot(path=root_path, root_id=str(marker["root_id"]), role=role)


def assert_writable(directory: Path) -> None:
    probe = fs_path(directory / f".write-probe-{uuid.uuid4().hex}{PARTIAL_SUFFIX}")
    try:
        probe.write_bytes(b"promat")
        if probe.read_bytes() != b"promat":
            raise PreservationConfigError(f"write probe read back differently in {directory}")
    except OSError as exc:
        raise PreservationConfigError(f"root is not writable: {directory} ({exc})") from exc
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


_TOOL_OWNED_TOP_LEVEL = {"sessions", "batches", "fixity", "preservation", "backup"}


def uncovered_top_level(archive_root: Path) -> list[str]:
    """Top-level archive-root entries that are not units (for example legacy pipeline or first-generation
    workbook folders). The unit copy does NOT preserve them; reports list them so they are not forgotten."""
    if not archive_root.is_dir():
        return []
    return sorted(child.name for child in archive_root.iterdir() if child.name not in _TOOL_OWNED_TOP_LEVEL)


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
    status: str = "pending"  # the role's done or planned status | incomplete | failed
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
        result.status = root.role.planned_status
        return result
    verification = verify_destination(root, unit_id, expected, scope=scope)
    if not verification["ok"]:
        result.status = "failed"
        result.problems.append(f"post-copy verification failed: { {k: v[:5] for k, v in verification.items() if isinstance(v, list) and v} }")
        return result
    result.status = root.role.done_status if scope == SCOPE_COMPLETE else "incomplete"
    receipt = write_receipt(archive_root, root, unit_id, expected, scope=scope, verification=verification)
    result.receipt_path = str(receipt)
    return result


def _hasher(unbuffered: bool):
    return fixity.sha256_file_unbuffered if unbuffered else fixity.sha256_file


def verify_destination(
    root: PreservationRoot,
    unit_id: str,
    expected: ExpectedFixity,
    *,
    scope: str = SCOPE_COMPLETE,
    unbuffered: bool = False,
) -> dict[str, Any]:
    """Full SHA-256 check of one unit in the destination. ``unbuffered`` reads from the device, not the file cache."""
    entries = expected.entries
    if scope == SCOPE_EXCLUDED_SECURE:
        entries = {p: h for p, h in entries.items() if not _is_secure(p)}
    dest = root.unit_dir(unit_id)
    check = fixity.verify_manifest(fs_path(dest), entries, check_extra=True, hasher=_hasher(unbuffered))
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


def local_receipt_path(archive_root: Path, unit_id: str, role: RootRole = PRESERVATION) -> Path:
    return archive_root / Path(role.local_receipts) / receipt_filename(unit_id)


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
        "schema": root.role.receipt_schema,
        "role": root.role.name,
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
    local = local_receipt_path(archive_root, unit_id, root.role)
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
    role: RootRole | None = None,
    unbuffered: bool = False,
) -> dict[str, Any]:
    """State of one unit with the evidence it rests on. Pure read; never modifies anything.

    ``role`` is only needed when no root is given; an opened root carries its own role.
    """
    role = root.role if root is not None else (role or PRESERVATION)
    evidence: dict[str, Any] = {}
    reasons: list[str] = []
    expected = resolve_expected_fixity(archive_root, unit_id)
    if expected is None:
        return {"unit": unit_id, "state": STATE_ACTIVE_LOCAL, "reasons": ["no expected fixity (baseline missing)"], "evidence": evidence}
    evidence["expected_fixity_origin"] = expected.origin
    evidence["manifest_sha256"] = expected.manifest_sha256
    state = role.pending_state
    if root is None or root.root_id is None:
        reasons.append(f"{role.name} root not configured or not initialised")
        return {"unit": unit_id, "state": state, "reasons": reasons, "evidence": evidence}
    receipt_file = local_receipt_path(archive_root, unit_id, role)
    if not receipt_file.is_file():
        reasons.append(f"no {role.name} receipt")
        return {"unit": unit_id, "state": state, "reasons": reasons, "evidence": evidence}
    try:
        receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        reasons.append(f"unreadable {role.name} receipt")
        return {"unit": unit_id, "state": state, "reasons": reasons, "evidence": evidence}
    evidence["receipt"] = str(receipt_file)
    if receipt.get("scope") != SCOPE_COMPLETE:
        reasons.append(f"receipt scope is {receipt.get('scope')!r}: scope-limited copies never count as preserved")
    elif receipt.get("schema") != role.receipt_schema:
        reasons.append(f"receipt is not a {role.name} receipt")
    elif receipt.get("root_id") != root.root_id:
        reasons.append(f"receipt belongs to a different {role.name} root (root changed: re-run the verified copy)")
    elif receipt.get("manifest_sha256") != expected.manifest_sha256:
        reasons.append("archive unit changed after the receipt (manifest hash differs)")
    else:
        dest = fs_path(root.unit_dir(unit_id))
        if full_verify:
            verification = verify_destination(root, unit_id, expected, unbuffered=unbuffered)
            evidence["destination_check"] = "full_sha256_unbuffered" if unbuffered else "full_sha256"
            evidence["destination_files"] = verification["file_count"]
            evidence["destination_bytes"] = verification["total_bytes"]
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
            state = role.done_state
            if full_verify and role.grants_cleanup:
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


def _candidate_files(directory: Path) -> Iterable[tuple[str, str | None]]:
    """Regular files below ``directory`` as ``(relative_path, error)``; never raises for one unreadable entry.

    Windows can fail ``stat`` on some tool-internal files (for example Kaldi ``.ark`` files below ``.mfa_cache``,
    ``WinError 1920``). Such files are reported as unreadable (and so never counted as covered) instead of
    aborting the whole report.
    """
    for current, dirnames, filenames in os.walk(directory, followlinks=False):
        dirnames.sort()
        for name in sorted(filenames):
            full = Path(current) / name
            relative = full.relative_to(directory).as_posix()
            try:
                if full.is_symlink() or not full.is_file():
                    continue
            except OSError as exc:
                yield relative, str(exc)
                continue
            yield relative, None


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
    if root is not None and not root.role.grants_cleanup:
        raise PreservationConfigError(f"A {root.role.name} root never makes local data cleanup-eligible.")
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
        for relative, walk_error in _candidate_files(directory):
            file_path = directory / relative
            if walk_error is not None:
                entry["unreadable"].append({"path": relative, "error": walk_error})
                continue
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
        "archive_root_entries_not_covered_by_unit_copy": uncovered_top_level(archive_root),
        "units": units,
        "candidate_directories": candidates,
    }


# ---------------------------------------------------------------------------------------------------------
# Supplemental sets (material outside the archive units)
# ---------------------------------------------------------------------------------------------------------

SUPPLEMENTAL_DIR = "supplemental"
SUPPLEMENTAL_MANIFESTS = "_manifests"
SUPPLEMENTAL_SCHEMA = "promat.supplemental_set.v1"
_SUPPLEMENTAL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def archive_supplemental_sources(archive_root: Path) -> dict[str, Path]:
    """Archive-root entries that the unit copy does not cover, plus the fixity baselines."""
    sources = {name: archive_root / name for name in uncovered_top_level(archive_root)}
    if (archive_root / "fixity").is_dir():
        sources["fixity"] = archive_root / "fixity"
    return sources


def collect_source_files(source: str | Path) -> dict[str, Path]:
    """Files of one supplemental source as ``{relative POSIX path: file}``: a directory, a file or a glob pattern."""
    parts = Path(source).parts
    wildcard = next((index for index, part in enumerate(parts) if any(char in part for char in "*?[")), None)
    if wildcard is not None:
        base = Path(*parts[:wildcard]) if wildcard else Path(".")
        matches = sorted(path for path in base.glob("/".join(parts[wildcard:])) if path.is_file())
        return {path.relative_to(base).as_posix(): path for path in matches}
    path = Path(source)
    if path.is_file():
        return {path.name: path}
    if path.is_dir():
        return {relative: path / relative for relative in fixity.list_unit_files(path)}
    return {}


def supplemental_set_dir(root: PreservationRoot, label: str, name: str) -> Path:
    return root.path / SUPPLEMENTAL_DIR / label / name


def supplemental_manifest_path(root: PreservationRoot, label: str, name: str) -> Path:
    return root.path / SUPPLEMENTAL_DIR / label / SUPPLEMENTAL_MANIFESTS / f"{name}.sha256"


def copy_supplemental_set(
    archive_root: Path,
    root: PreservationRoot,
    label: str,
    name: str,
    files: dict[str, Path],
    *,
    execute: bool,
) -> dict[str, Any]:
    """Verified, additive copy of one named file set into ``supplemental/<label>/<name>/`` of the root.

    The set gets its own manifest in the destination, so it can be verified later without its source. A label is
    a snapshot: when the source changed since that label was written, this is a conflict and nothing is replaced;
    the changed state goes under a new label.
    """
    unit = f"{SUPPLEMENTAL_DIR}/{label}/{name}"
    result: dict[str, Any] = {"unit": unit, "status": "failed", "files": len(files), "bytes": 0, "problems": []}
    if not _SUPPLEMENTAL_NAME.match(label) or not _SUPPLEMENTAL_NAME.match(name) or name == SUPPLEMENTAL_MANIFESTS:
        result["problems"].append("label and set name must be plain names (letters, digits, '.', '_', '-')")
        return result
    if not files:
        result["problems"].append("no files found for this set")
        return result
    collisions = _case_collisions(files)
    if collisions:
        result["problems"].append(f"case collisions: {sorted(collisions)[:5]}")
        return result
    try:
        entries = {relative: fixity.sha256_file(fs_path(path)) for relative, path in sorted(files.items())}
        result["bytes"] = sum(fs_path(path).stat().st_size for path in files.values())
    except OSError as exc:
        result["problems"].append(f"unreadable source file: {exc}")
        return result
    manifest_file = fs_path(supplemental_manifest_path(root, label, name))
    if manifest_file.is_file() and fixity.read_manifest(manifest_file) != entries:
        result["status"] = "conflict_manifest_differs"
        result["problems"].append("the source differs from what this label already holds; nothing replaced (use a new --label)")
        return result
    dest = supplemental_set_dir(root, label, name)
    outcomes = []
    for relative, path in sorted(files.items()):
        outcome = copy_file_verified(path, dest / relative, entries[relative], execute=execute)
        outcome["path"] = relative
        outcomes.append(outcome)
    bad = [o for o in outcomes if o["status"] not in {"copied", "already_present", "would_copy"}]
    if bad:
        result["problems"].extend(f"{o['path']}: {o['status']}" for o in bad[:20])
        return result
    if not execute:
        result["status"] = root.role.planned_status
        return result
    check = fixity.verify_manifest(fs_path(dest), entries, check_extra=True)
    if any(check.values()):
        result["problems"].append("post-copy verification failed: " + ", ".join(f"{k}={len(v)}" for k, v in check.items() if v))
        return result
    if not manifest_file.is_file():
        fixity.write_manifest(entries, manifest_file)
    meta = {
        "schema": SUPPLEMENTAL_SCHEMA,
        "role": root.role.name,
        "root_id": root.root_id,
        "label": label,
        "set": name,
        "verified_at": provenance_helpers.utc_timestamp(),
        "verification": "full_sha256_readback",
        "file_count": len(entries),
        "total_bytes": result["bytes"],
        "manifest_sha256": manifest_digest(entries),
        "tool_revision": provenance_helpers.current_git_revision(),
    }
    text = json.dumps(meta, indent=2) + "\n"
    manifest_file.with_suffix(".json").write_text(text, encoding="utf-8")
    local = archive_root / Path(root.role.local_receipts) / SUPPLEMENTAL_DIR / f"{label}__{name}.json"
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_text(text, encoding="utf-8")
    result["status"] = root.role.done_status
    return result


def verify_supplemental(root: PreservationRoot, *, unbuffered: bool = False) -> list[dict[str, Any]]:
    """Verify every supplemental set of a root against the manifest stored beside it (the source is not needed)."""
    results: list[dict[str, Any]] = []
    base = fs_path(root.path / SUPPLEMENTAL_DIR)
    if not base.is_dir():
        return results
    for label_dir in sorted(path for path in base.iterdir() if path.is_dir()):
        manifests = label_dir / SUPPLEMENTAL_MANIFESTS
        names = sorted(path.stem for path in manifests.glob("*.sha256")) if manifests.is_dir() else []
        for name in names:
            entries = fixity.read_manifest(manifests / f"{name}.sha256")
            check = fixity.verify_manifest(label_dir / name, entries, check_extra=True, hasher=_hasher(unbuffered))
            results.append({
                "unit": f"{SUPPLEMENTAL_DIR}/{label_dir.name}/{name}",
                "ok": not any(check.values()),
                "files": len(entries),
                "bytes": sum((label_dir / name / p).stat().st_size for p in entries if (label_dir / name / p).is_file()),
                **{key: value for key, value in check.items() if value},
            })
        for stray in sorted(p.name for p in label_dir.iterdir() if p.is_dir() and p.name != SUPPLEMENTAL_MANIFESTS and p.name not in names):
            results.append({"unit": f"{SUPPLEMENTAL_DIR}/{label_dir.name}/{stray}", "ok": False, "files": 0, "bytes": 0, "no_manifest": True})
    return results
