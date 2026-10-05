"""Provenance, fixity and institutional-preservation tooling. Temp directories only: no K:, no production."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import pytest

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))
INTAKE_DIR = TEST_REPO_ROOT / "scripts" / "research_data_intake"
sys.path.insert(0, str(INTAKE_DIR))

import archive_preservation as cli  # noqa: E402
import fixity  # noqa: E402
import preservation as pres  # noqa: E402
import provenance as prov  # noqa: E402
from intake_batch_common import ParsedBatchFile  # noqa: E402
from intake_storage import write_batch_archive_reports, write_secure_person_export, write_session_archive  # noqa: E402


def _write(path: Path, payload: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload if isinstance(payload, bytes) else payload.encode("utf-8"))


def _runtime(tmp_path: Path, session_id: str) -> Path:
    session_dir = tmp_path / "runtime" / session_id
    _write(session_dir / "metadata.json", "{}\n")
    _write(session_dir / "alignment" / "wordlist.json", '{"items": []}\n')
    _write(session_dir / "derived" / "wordlist.mp3", b"ID3\x04\x00\x00\x00\x00\x00\x00")
    _write(session_dir / "items" / "wordlist" / "wl_001.mp3", b"ID3\x04\x00\x00\x00\x00\x00\x00")
    return session_dir


def _inputs(tmp_path: Path, tag: str) -> list[ParsedBatchFile]:
    wav = tmp_path / "drop" / f"{tag}_es_l_0001_wordlist_processed.wav"
    grid = tmp_path / "drop" / f"{tag}_es_l_0001_wordlist_processed.TextGrid"
    _write(wav, b"RIFF" + tag.encode())
    _write(grid, "TextGrid " + tag)
    common = {"source_root": "batch_root", "person_id": "ES-L-0001", "task": "wordlist", "stage": "processed"}
    return [
        ParsedBatchFile(source_path=wav, relative_source="C:\\drop\\" + wav.name, file_kind="wav", file_role="source", **common),
        ParsedBatchFile(source_path=grid, relative_source=grid.name, file_kind="textgrid", file_role="alignment_source", **common),
    ]


def _archive_session(tmp_path: Path, archive: Path, session_id: str = "ES-L-0001-2026-S01", **kwargs):
    return write_session_archive(
        session_dir=_runtime(tmp_path, session_id),
        language_code="es",
        session_id=session_id,
        person_id="ES-L-0001",
        source_batch="es_batch_1",
        input_files=_inputs(tmp_path, session_id[-3:]),
        warnings=[],
        importer_version="test@abc",
        archive_root=archive,
        **kwargs,
    )


def _snapshot(root: Path) -> dict[str, str]:
    return fixity.compute_manifest(root)


UNIT = "sessions/es/ES-L-0001-2026-S01"


# ------------------------------------------------------------------------------------------ provenance

def test_session_manifest_records_per_file_provenance_and_relationships(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    result = _archive_session(tmp_path, archive, provenance={"git_revision": "abc1234", "tool_versions": {"ffmpeg": "x"}})
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    wav = next(e for e in manifest["input_files"] if e["path"] == "source/wordlist.wav")
    assert wav["original_filename"].endswith("_es_l_0001_wordlist_processed.wav")
    assert wav["canonical_name"] == "wordlist.wav"
    assert wav["batch_id"] == "es_batch_1" and wav["session_id"] == "ES-L-0001-2026-S01"
    assert len(wav["sha256"]) == 64 and wav["size"] > 0 and wav["intake_timestamp"]
    assert "C:" not in wav["original_relative_source"] and "\\" not in wav["original_relative_source"]

    mp3 = next(e for e in manifest["generated_runtime_files"] if e["path"] == "runtime/derived/wordlist.mp3")
    assert mp3["derived_from"] == ["source/wordlist.wav"]
    item = next(e for e in manifest["generated_runtime_files"] if e["path"].endswith("items/wordlist/wl_001.mp3"))
    assert item["derived_from"] == ["source/wordlist.wav"]
    meta = next(e for e in manifest["generated_runtime_files"] if e["path"] == "runtime/metadata.json")
    assert meta["derived_from"] == []

    assert manifest["provenance_schema_version"] == prov.PROVENANCE_SCHEMA_VERSION
    assert manifest["provenance"]["git_revision"] == "abc1234"
    assert manifest["provenance"]["tool_versions"] == {"ffmpeg": "x"}


def test_session_without_run_provenance_still_gets_unknown_placeholders(tmp_path: Path) -> None:
    result = _archive_session(tmp_path, tmp_path / "archive")
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["provenance"]["git_revision"] == "unknown"
    assert manifest["provenance"]["workbook"] is None


def test_session_fixity_manifest_is_complete_and_stays_complete_after_secure_export(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    result = _archive_session(tmp_path, archive)
    session = result.archive_session_dir
    manifest_file = session / "metadata" / "checksums.sha256"
    assert manifest_file.is_file()
    assert set(fixity.read_manifest(manifest_file)) == set(fixity.list_unit_files(session)) - {"metadata/checksums.sha256"}

    write_secure_person_export(archive_session_dir=session, person_id="ES-L-0001", secure_data={"email": "x@example.test"})
    entries = fixity.read_manifest(manifest_file)
    assert "secure/secure_person_intake.json" in entries
    assert not any(fixity.verify_manifest(session, entries, exclude=["metadata/checksums.sha256"]).values())
    raw = manifest_file.read_bytes().decode("utf-8")
    assert "\r" not in raw and "\\" not in raw and re.fullmatch(r"([0-9a-f]{64}  [^\s].*\n)+", raw)


def test_secure_export_does_not_create_fixity_for_archives_that_never_had_one(tmp_path: Path) -> None:
    session = tmp_path / "archive" / "sessions" / "es" / "S"
    (session / "metadata").mkdir(parents=True)
    write_secure_person_export(archive_session_dir=session, person_id="P", secure_data={})
    assert not (session / "metadata" / "checksums.sha256").exists()


def test_importer_version_uses_revision_and_falls_back_to_unknown(tmp_path: Path, monkeypatch) -> None:
    prov.clear_provenance_cache()
    monkeypatch.setenv("PROMAT_GIT_REVISION", "deadbeef")
    assert prov.importer_version("import_batch_to_production") == "import_batch_to_production@deadbeef"
    monkeypatch.delenv("PROMAT_GIT_REVISION")
    prov.clear_provenance_cache()
    assert prov.importer_version("tool", repo_root=tmp_path) == "tool@unknown"
    prov.clear_provenance_cache()


def test_tool_versions_degrade_when_tools_are_missing(monkeypatch) -> None:
    prov.clear_provenance_cache()
    monkeypatch.setattr(prov, "_run", lambda *a, **k: None)
    assert prov.tool_versions() == {"ffmpeg": "unavailable", "mfa": "unavailable"}
    prov.clear_provenance_cache()


def test_catalog_provenance_reads_header_fields_and_survives_garbage(tmp_path: Path) -> None:
    good = tmp_path / "catalog.json"
    good.write_text(json.dumps({"language": "es", "task_type": "text", "schema_version": 3, "items": [1, 2, 3]}), encoding="utf-8")
    record = prov.catalog_provenance(good)
    assert (record["language"], record["catalog_type"], record["schema_version"], record["item_count"]) == ("es", "text", "3", 3)
    assert len(record["sha256"]) == 64
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    assert prov.catalog_provenance(bad)["item_count"] is None


def test_batch_reports_store_workbook_in_secure_class_with_provenance(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    workbook = tmp_path / "drop" / "intake.xlsx"
    _write(workbook, b"PK-fake-workbook")
    result = write_batch_archive_reports(
        batch_name="es_batch_1",
        import_payload={},
        intake_report_markdown="a",
        validation_report_markdown="b",
        archive_report_markdown="c",
        archive_root=archive,
        workbook_path=workbook,
        provenance={"git_revision": "abc1234", "tool_versions": {}},
    )
    batch = result.batch_dir
    assert (batch / "secure" / "workbook" / "intake.xlsx").read_bytes() == b"PK-fake-workbook"
    provenance = json.loads((batch / "batch_provenance.json").read_text(encoding="utf-8"))
    assert provenance["workbook"]["sha256"] == fixity.sha256_file(workbook)
    assert provenance["workbook"]["storage_class"] == "secure"
    entries = fixity.read_manifest(batch / "checksums.sha256")
    assert {"secure/workbook/intake.xlsx", "batch_provenance.json", "import_payload.json"} <= set(entries)


def test_batch_reports_without_provenance_keep_the_original_four_file_manifest(tmp_path: Path) -> None:
    result = write_batch_archive_reports(
        batch_name="b", import_payload={}, intake_report_markdown="a", validation_report_markdown="b",
        archive_report_markdown="c", archive_root=tmp_path / "archive",
    )
    assert set(fixity.read_manifest(result.checksums_path)) == {
        "import_payload.json", "intake_report.md", "validation_report.md", "archive_report.md",
    }


# ------------------------------------------------------------------------------------------ fixity

@pytest.mark.parametrize("bad", ["", "/abs", "C:/x", "a\\b", "../x", "a/../b"])
def test_fixity_rejects_non_deterministic_paths(bad: str) -> None:
    with pytest.raises(fixity.FixityError):
        fixity.validate_relative_path(bad)


def test_fixity_manifest_rejects_malformed_and_duplicate_lines(tmp_path: Path) -> None:
    path = tmp_path / "c.sha256"
    sha = "a" * 64
    path.write_text(f"{sha}  x\n{sha}  x\n", encoding="utf-8")
    with pytest.raises(fixity.FixityError):
        fixity.read_manifest(path)
    path.write_text("nothex  x\n", encoding="utf-8")
    with pytest.raises(fixity.FixityError):
        fixity.read_manifest(path)


# ------------------------------------------------------------------------------------------ baseline

def _legacy_archive(tmp_path: Path) -> Path:
    """An archive written before fixity manifests existed (no metadata/checksums.sha256)."""
    archive = tmp_path / "archive"
    _archive_session(tmp_path, archive)
    (archive / "sessions" / "es" / "ES-L-0001-2026-S01" / "metadata" / "checksums.sha256").unlink()
    _write(archive / "batches" / "old_batch" / "import_payload.json", "{}\n")
    return archive


def test_baseline_is_additive_and_never_changes_existing_archive_files(tmp_path: Path) -> None:
    archive = _legacy_archive(tmp_path)
    before = _snapshot(archive)
    results = [pres.baseline_unit(archive, u, execute=True) for u in pres.discover_units(archive)]
    assert {r["status"] for r in results} == {"baseline_written"}
    after = _snapshot(archive)
    assert {p: h for p, h in after.items() if not p.startswith("fixity/")} == before
    assert set(after) - set(before) == {
        f"fixity/baseline/{pres.unit_id_to_filename(u)}.{ext}" for u in pres.discover_units(archive) for ext in ("sha256", "json")
    }


def test_baseline_dry_run_writes_nothing(tmp_path: Path) -> None:
    archive = _legacy_archive(tmp_path)
    before = _snapshot(archive)
    assert pres.baseline_unit(archive, UNIT, execute=False)["status"] == "would_write_baseline"
    assert _snapshot(archive) == before


def test_baseline_reports_unit_manifest_coverage_and_does_not_duplicate_it(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    _archive_session(tmp_path, archive)
    result = pres.baseline_unit(archive, UNIT, execute=True)
    assert result["status"] == "covered_by_unit_manifest"
    assert not (archive / "fixity").exists()


def test_baseline_with_unreadable_file_writes_no_baseline_and_reports_it(tmp_path: Path, monkeypatch) -> None:
    archive = _legacy_archive(tmp_path)
    real = fixity.sha256_file

    def flaky(path: Path) -> str:
        if path.name == "wordlist.wav":
            raise PermissionError("locked")
        return real(path)

    monkeypatch.setattr(fixity, "sha256_file", flaky)
    result = pres.baseline_unit(archive, UNIT, execute=True)
    assert result["status"] == "incomplete_unreadable_files"
    assert result["unreadable"][0]["path"] == "source/wordlist.wav"
    assert not pres.baseline_path(archive, UNIT).exists()


def test_existing_baseline_is_never_rewritten_and_drift_is_reported(tmp_path: Path) -> None:
    archive = _legacy_archive(tmp_path)
    pres.baseline_unit(archive, UNIT, execute=True)
    baseline_before = pres.baseline_path(archive, UNIT).read_bytes()
    (archive / UNIT / "source" / "wordlist.wav").write_bytes(b"changed")
    result = pres.baseline_unit(archive, UNIT, execute=True)
    assert result["status"] == "baseline_drift" and result["drift"]["mismatched"] == ["source/wordlist.wav"]
    assert pres.baseline_path(archive, UNIT).read_bytes() == baseline_before


# ------------------------------------------------------------------------------------------ preservation root

def test_no_default_preservation_root(monkeypatch) -> None:
    monkeypatch.delenv(pres.PRESERVATION_ROOT_ENV, raising=False)
    with pytest.raises(pres.PreservationConfigError):
        pres.resolve_preservation_root_path(None)


def test_preservation_root_from_env_and_cli_precedence(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(pres.PRESERVATION_ROOT_ENV, str(tmp_path / "env"))
    assert pres.resolve_preservation_root_path(None) == tmp_path / "env"
    assert pres.resolve_preservation_root_path(tmp_path / "cli") == tmp_path / "cli"


def test_root_must_be_separate_from_local_archive(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    archive.mkdir()
    for bad in (archive, archive / "inside", tmp_path):
        with pytest.raises(pres.PreservationConfigError):
            pres.open_preservation_root(bad, archive_root=archive, initialize=True)


def test_root_initialisation_creates_marker_once_and_requires_reachable_parent(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    archive.mkdir()
    root = pres.open_preservation_root(tmp_path / "pres", archive_root=archive, initialize=True)
    again = pres.open_preservation_root(tmp_path / "pres", archive_root=archive, initialize=True)
    assert root.root_id and root.root_id == again.root_id
    with pytest.raises(pres.PreservationConfigError, match="reachable"):
        pres.open_preservation_root(tmp_path / "missing_volume" / "pres", archive_root=archive, initialize=True)
    assert pres.open_preservation_root(tmp_path / "nothing", archive_root=archive, initialize=False).root_id is None
    assert not (tmp_path / "nothing").exists()


def test_windows_extended_paths_are_pure_string_transforms() -> None:
    assert pres.to_extended_windows_path("K:\\a\\b") == "\\\\?\\K:\\a\\b"
    assert pres.to_extended_windows_path("K:/a/b") == "\\\\?\\K:\\a\\b"
    assert pres.to_extended_windows_path("\\\\server\\share\\a") == "\\\\?\\UNC\\server\\share\\a"
    assert pres.to_extended_windows_path("\\\\?\\K:\\a") == "\\\\?\\K:\\a"
    assert pres.to_extended_windows_path("relative\\x") == "relative\\x"


def test_tooling_has_no_hard_coded_physical_location() -> None:
    for name in ("preservation.py", "archive_preservation.py", "provenance.py", "fixity.py"):
        text = (INTAKE_DIR / name).read_text(encoding="utf-8")
        assert not re.search(r"Pronunciation_Matters|[\"'][A-Za-z]:\\\\", text), name


# ------------------------------------------------------------------------------------------ verified copy

@pytest.fixture
def world(tmp_path: Path):
    archive = tmp_path / "archive"
    _archive_session(tmp_path, archive)
    _archive_session(tmp_path, archive, session_id="ES-L-0002-2026-S01")
    write_secure_person_export(archive_session_dir=archive / UNIT, person_id="ES-L-0001", secure_data={"email": "x@example.test"})
    pres_path = tmp_path / "institutional"
    return archive, pres_path


def _root(archive: Path, pres_path: Path, *, initialize: bool = True) -> pres.PreservationRoot:
    return pres.open_preservation_root(pres_path, archive_root=archive, initialize=initialize)


def test_copy_dry_run_writes_nothing_anywhere(world) -> None:
    archive, pres_path = world
    before = _snapshot(archive)
    root = _root(archive, pres_path, initialize=False)
    result = pres.copy_unit(archive, UNIT, root, execute=False)
    assert result.status == "would_preserve" and {f["status"] for f in result.files} == {"would_copy"}
    assert _snapshot(archive) == before
    assert not pres_path.exists()


def test_copy_execute_copies_verifies_and_reaches_preserved_then_cleanup_eligible(world) -> None:
    archive, pres_path = world
    assert pres.derive_state(archive, UNIT, None, full_verify=True)["state"] == pres.STATE_PENDING
    root = _root(archive, pres_path)
    result = pres.copy_unit(archive, UNIT, root, execute=True)
    assert result.status == "preserved" and result.receipt_path
    dest = root.unit_dir(UNIT)
    assert _snapshot(dest) == _snapshot(archive / UNIT)
    assert not [p for p in dest.rglob("*") if p.name.endswith(".partial")]

    quick = pres.derive_state(archive, UNIT, root, full_verify=False)
    assert quick["state"] == pres.STATE_PRESERVED  # a quick check never grants cleanup eligibility
    full = pres.derive_state(archive, UNIT, root, full_verify=True)
    assert full["state"] == pres.STATE_CLEANUP_ELIGIBLE
    assert full["evidence"]["destination_check"] == "full_sha256" and full["evidence"]["local_matches_fixity"]
    assert (root.receipts_dir / pres.receipt_filename(UNIT)).is_file()


def test_unit_without_any_copy_is_pending_not_preserved(world) -> None:
    archive, pres_path = world
    root = _root(archive, pres_path)
    assert pres.derive_state(archive, UNIT, root, full_verify=True)["state"] == pres.STATE_PENDING


def test_unit_without_fixity_is_active_local_and_copy_refuses(tmp_path: Path) -> None:
    archive = _legacy_archive(tmp_path)
    root = _root(archive, tmp_path / "inst")
    assert pres.derive_state(archive, UNIT, root, full_verify=True)["state"] == pres.STATE_ACTIVE_LOCAL
    result = pres.copy_unit(archive, UNIT, root, execute=True)
    assert result.status == "failed" and "baseline" in result.problems[0]
    assert not root.unit_dir(UNIT).exists()


def test_copy_is_idempotent_and_resumes_after_interruption(world) -> None:
    archive, pres_path = world
    root = _root(archive, pres_path)
    pres.copy_unit(archive, UNIT, root, execute=True)
    dest = root.unit_dir(UNIT)
    victim = dest / "source" / "wordlist.wav"
    victim.unlink()
    (dest / "source" / "wordlist.wav.partial").write_bytes(b"half a fi")  # interrupted earlier run
    result = pres.copy_unit(archive, UNIT, root, execute=True)
    statuses = {f["path"]: f["status"] for f in result.files}
    assert statuses["source/wordlist.wav"] == "copied"
    assert set(statuses.values()) <= {"copied", "already_present"} and result.status == "preserved"
    assert not (dest / "source" / "wordlist.wav.partial").exists()
    assert pres.copy_unit(archive, UNIT, root, execute=True).status == "preserved"


def test_mismatching_destination_file_is_never_overwritten(world) -> None:
    archive, pres_path = world
    root = _root(archive, pres_path)
    target = root.unit_dir(UNIT) / "source" / "wordlist.wav"
    _write(target, b"someone else's data")
    result = pres.copy_unit(archive, UNIT, root, execute=True)
    assert result.status == "failed"
    assert any("conflict_destination_mismatch" in p for p in result.problems)
    assert target.read_bytes() == b"someone else's data"
    assert not (archive / "preservation").exists()  # no receipt for a failed unit


def test_source_that_no_longer_matches_fixity_is_not_copied(world) -> None:
    archive, pres_path = world
    root = _root(archive, pres_path)
    (archive / UNIT / "source" / "wordlist.wav").write_bytes(b"bit rot")
    result = pres.copy_unit(archive, UNIT, root, execute=True)
    assert result.status == "failed" and any("source_mismatch" in p for p in result.problems)
    assert not (root.unit_dir(UNIT) / "source" / "wordlist.wav").exists()
    assert not list(root.unit_dir(UNIT).rglob("*.partial"))


def test_files_not_covered_by_fixity_block_the_copy(world) -> None:
    archive, pres_path = world
    _write(archive / UNIT / "reports" / "stray.txt", "added later")
    root = _root(archive, pres_path)
    # coverage is incomplete, so no expected fixity exists until a baseline is made
    assert pres.copy_unit(archive, UNIT, root, execute=True).status == "failed"
    pres.baseline_unit(archive, UNIT, execute=True)
    assert pres.copy_unit(archive, UNIT, root, execute=True).status == "preserved"


def test_exclude_secure_is_never_preserved(world) -> None:
    archive, pres_path = world
    root = _root(archive, pres_path)
    result = pres.copy_unit(archive, UNIT, root, execute=True, exclude_secure=True)
    assert result.status == "incomplete"
    assert not (root.unit_dir(UNIT) / "secure").exists()
    state = pres.derive_state(archive, UNIT, root, full_verify=True)
    assert state["state"] == pres.STATE_PENDING and "scope-limited" in state["reasons"][0]


def test_archive_change_after_receipt_returns_unit_to_pending(world) -> None:
    archive, pres_path = world
    root = _root(archive, pres_path)
    pres.copy_unit(archive, UNIT, root, execute=True)
    write_secure_person_export(archive_session_dir=archive / UNIT, person_id="ES-L-0001", secure_data={"email": "new@example.test"})
    state = pres.derive_state(archive, UNIT, root, full_verify=False)
    assert state["state"] == pres.STATE_PENDING and "changed after the receipt" in state["reasons"][0]


def test_corrupted_destination_is_detected_by_full_verification_only(world) -> None:
    archive, pres_path = world
    root = _root(archive, pres_path)
    pres.copy_unit(archive, UNIT, root, execute=True)
    victim = root.unit_dir(UNIT) / "source" / "wordlist.wav"
    original = victim.read_bytes()
    victim.write_bytes(b"X" * len(original))  # same size, different content
    assert pres.derive_state(archive, UNIT, root, full_verify=False)["state"] == pres.STATE_PRESERVED
    full = pres.derive_state(archive, UNIT, root, full_verify=True)
    assert full["state"] == pres.STATE_PENDING and "verification failed" in full["reasons"][0]


def test_local_drift_blocks_cleanup_eligibility(world) -> None:
    archive, pres_path = world
    root = _root(archive, pres_path)
    pres.copy_unit(archive, UNIT, root, execute=True)
    (archive / UNIT / "source" / "wordlist.wav").write_bytes(b"local rot")
    state = pres.derive_state(archive, UNIT, root, full_verify=True)
    assert state["state"] != pres.STATE_CLEANUP_ELIGIBLE


def test_changing_the_root_requires_a_new_verified_copy(world, tmp_path: Path) -> None:
    archive, pres_path = world
    old_root = _root(archive, pres_path)
    pres.copy_unit(archive, UNIT, old_root, execute=True)
    new_root = pres.open_preservation_root(tmp_path / "new_location", archive_root=archive, initialize=True)
    state = pres.derive_state(archive, UNIT, new_root, full_verify=True)
    assert state["state"] == pres.STATE_PENDING and "different preservation root" in state["reasons"][0]
    assert pres.copy_unit(archive, UNIT, new_root, execute=True).status == "preserved"
    assert pres.derive_state(archive, UNIT, new_root, full_verify=True)["state"] == pres.STATE_CLEANUP_ELIGIBLE


def test_moving_a_root_is_copy_verify_config_only_and_inherits_lineage(world, tmp_path: Path) -> None:
    archive, pres_path = world
    old_root = _root(archive, pres_path)
    pres.copy_unit(archive, UNIT, old_root, execute=True)
    new_path = tmp_path / "moved"
    exit_code = cli.run(["copy", "--archive-root", str(old_root.archive_dir), "--preservation-root", str(new_path), "--unit", UNIT, "--execute"])
    assert exit_code == 0
    marker = json.loads((new_path / pres.MARKER_FILENAME).read_text(encoding="utf-8"))
    assert marker["migrated_from_root_id"] == old_root.root_id
    assert _snapshot(new_path / "archive" / UNIT) == _snapshot(pres_path / "archive" / UNIT)


# ------------------------------------------------------------------------------------------ cleanup report

def test_cleanup_report_lists_duplicates_and_deletes_nothing(world, tmp_path: Path) -> None:
    archive, pres_path = world
    root = _root(archive, pres_path)
    pres.copy_unit(archive, UNIT, root, execute=True)
    batch_working = tmp_path / "batch_working"
    shutil_source = archive / UNIT / "source" / "wordlist.wav"
    _write(batch_working / "person" / "wordlist.wav", shutil_source.read_bytes())
    _write(batch_working / "person" / "unique.wav", b"unique and not preserved")
    archive_before, working_before, dest_before = _snapshot(archive), _snapshot(batch_working), _snapshot(pres_path)

    report = pres.cleanup_eligibility_report(archive, root, candidate_dirs=[batch_working])

    assert report["deletes_anything"] is False and report["schema"] == pres.CLEANUP_SCHEMA
    assert report["counts"][pres.STATE_CLEANUP_ELIGIBLE] == 1 and report["counts"][pres.STATE_PENDING] == 1
    entry = report["candidate_directories"][0]
    assert [d["path"] for d in entry["duplicates"]] == ["person/wordlist.wav"]
    assert entry["duplicates"][0]["preserved_as"] == f"{UNIT}/source/wordlist.wav"
    assert [n["path"] for n in entry["not_covered"]] == ["person/unique.wav"]
    assert (_snapshot(archive), _snapshot(batch_working), _snapshot(pres_path)) == (archive_before, working_before, dest_before)


def test_cleanup_report_survives_unstatable_candidate_file(world, tmp_path: Path, monkeypatch) -> None:
    # Windows regression: stat() on e.g. Kaldi *.ark files under .mfa_cache raises WinError 1920.
    archive, pres_path = world
    root = _root(archive, pres_path)
    pres.copy_unit(archive, UNIT, root, execute=True)
    batch = tmp_path / "batch"
    _write(batch / "ok.wav", b"unique and not preserved")
    _write(batch / ".mfa_cache" / "ali.1.ark", b"unreadable on windows")
    real_is_file = Path.is_file

    def flaky_is_file(self: Path) -> bool:
        if self.name.endswith(".ark"):
            raise OSError(1920, "cannot access the file")
        return real_is_file(self)

    monkeypatch.setattr(Path, "is_file", flaky_is_file)
    report = pres.cleanup_eligibility_report(archive, root, candidate_dirs=[batch])

    entry = report["candidate_directories"][0]
    assert [u["path"] for u in entry["unreadable"]] == [".mfa_cache/ali.1.ark"]
    assert [n["path"] for n in entry["not_covered"]] == ["ok.wav"]
    assert entry["duplicates"] == []


def test_cleanup_report_without_preservation_marks_nothing_eligible(world, tmp_path: Path) -> None:
    archive, _ = world
    report = pres.cleanup_eligibility_report(archive, None)
    assert report["counts"][pres.STATE_CLEANUP_ELIGIBLE] == 0 and report["counts"][pres.STATE_PRESERVED] == 0


def test_preservation_modules_contain_no_deletion_of_archive_data() -> None:
    for name in ("preservation.py", "archive_preservation.py"):
        text = (INTAKE_DIR / name).read_text(encoding="utf-8")
        assert "rmtree" not in text and "os.remove" not in text
    # the only unlink calls are the tool's own *.partial files and its write probe
    for line in (INTAKE_DIR / "preservation.py").read_text(encoding="utf-8").splitlines():
        if ".unlink(" in line:
            assert any(token in line for token in ("partial", "probe")), line


# ------------------------------------------------------------------------------------------ CLI

def test_cli_end_to_end_with_reports_and_exit_codes(world, tmp_path: Path, capsys) -> None:
    archive, pres_path = world
    reports = tmp_path / "reports"
    common = ["--archive-root", str(archive), "--preservation-root", str(pres_path)]

    assert cli.run(["copy", *common, "--report-dir", str(reports)]) == 0  # dry-run is the default
    assert not pres_path.exists()
    dry = json.loads(next(reports.glob("copy-*.json")).read_text(encoding="utf-8"))
    assert dry["execute"] is False and dry["summary"]["would_preserve"] == 2
    assert next(reports.glob("copy-*.md")).read_text(encoding="utf-8").startswith("# Archive preservation report: copy")

    assert cli.run(["copy", *common, "--execute"]) == 0
    assert cli.run(["verify", *common, "--report-dir", str(reports)]) == 0
    verify = json.loads(sorted(reports.glob("verify-*.json"))[-1].read_text(encoding="utf-8"))
    assert verify["summary"][pres.STATE_CLEANUP_ELIGIBLE] == 2

    assert cli.run(["cleanup-report", *common]) == 0
    assert "deletes_anything=False" in capsys.readouterr().out

    (pres_path / "archive" / UNIT / "source" / "wordlist.wav").write_bytes(b"corrupt")
    assert cli.run(["verify", *common]) == 1


def test_cli_baseline_command_and_config_errors(tmp_path: Path, monkeypatch) -> None:
    archive = _legacy_archive(tmp_path)
    assert cli.run(["baseline", "--archive-root", str(archive)]) == 0
    assert not (archive / "fixity").exists()
    assert cli.run(["baseline", "--archive-root", str(archive), "--execute"]) == 0
    assert (archive / "fixity" / "baseline").is_dir()
    monkeypatch.delenv(pres.PRESERVATION_ROOT_ENV, raising=False)
    assert cli.run(["copy", "--archive-root", str(archive)]) == 2
    assert cli.run(["copy", "--archive-root", str(tmp_path / "does_not_exist"), "--preservation-root", str(tmp_path / "p")]) == 2
    assert cli.run(["status", "--archive-root", str(archive)]) == 0  # status works without a root: nothing preserved


def test_reports_name_archive_root_entries_the_unit_copy_does_not_cover(world, tmp_path: Path) -> None:
    archive, pres_path = world
    (archive / "praat_pipeline").mkdir()
    assert pres.uncovered_top_level(archive) == ["praat_pipeline"]
    root = _root(archive, pres_path)
    pres.copy_unit(archive, UNIT, root, execute=True)  # tool-owned dirs (preservation/, fixity/) never show up
    assert pres.uncovered_top_level(archive) == ["praat_pipeline"]
    assert pres.cleanup_eligibility_report(archive, root)["archive_root_entries_not_covered_by_unit_copy"] == ["praat_pipeline"]
