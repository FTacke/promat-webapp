"""Storage roots: fail-closed archive root, the local ``.env`` reader and the separate backup role.

Temp directories only. The autouse fixture ``isolated_storage_roots`` (conftest) guarantees that no operator root
is visible; every root used here is set by the test itself.
"""

from __future__ import annotations

import json
import os
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
import intake_storage  # noqa: E402
import preservation as pres  # noqa: E402
import storage_roots  # noqa: E402
from test_archive_preservation import UNIT, _archive_session  # noqa: E402
from test_storage_inventory import inventory  # noqa: E402

ARCHIVE_ENV = storage_roots.LOCAL_ARCHIVE_ROOT_ENV


def _env_file(tmp_path: Path, monkeypatch, text: str) -> Path:
    path = tmp_path / "operator config" / ".env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    monkeypatch.setattr(storage_roots, "ENV_FILE", path)
    return path


# ------------------------------------------------------------------------------------- H1: fail closed

def test_archive_root_has_no_built_in_location_and_fails_closed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert not hasattr(intake_storage, "DEFAULT_LOCAL_ARCHIVE_ROOT")
    assert not hasattr(inventory, "DEFAULT_LOCAL_ARCHIVE_ROOT")
    with pytest.raises(intake_storage.IntakeStorageError) as error:
        intake_storage.get_local_archive_root()
    assert ARCHIVE_ENV in str(error.value) and "no default" in str(error.value)
    with pytest.raises(intake_storage.IntakeStorageError):
        intake_storage.archive_sessions_root()
    assert list(tmp_path.iterdir()) == []  # nothing was created anywhere on the way to the error


def test_writing_an_archive_without_a_configured_root_writes_nothing(tmp_path: Path, monkeypatch) -> None:
    workdir = tmp_path / "cwd"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    with pytest.raises(intake_storage.IntakeStorageError):
        _archive_session(tmp_path, None)
    assert list(workdir.iterdir()) == []
    assert not any(path.name in {"sessions", "batches"} for path in tmp_path.rglob("*"))


def test_preservation_cli_reports_a_missing_archive_root_as_configuration_error(capsys) -> None:
    assert cli.run(["status"]) == cli.EXIT_CONFIG
    assert ARCHIVE_ENV in capsys.readouterr().out


def test_inventory_reports_an_unconfigured_archive_root_without_assuming_one(monkeypatch, capsys) -> None:
    monkeypatch.setattr(inventory, "measured_locations", lambda: [])
    monkeypatch.setattr(inventory, "worktrees", lambda: [])
    assert inventory.archive_root() is None
    assert inventory.main([]) == 0
    assert "Archive root: NOT CONFIGURED" in capsys.readouterr().out


def test_relative_archive_root_is_refused(monkeypatch) -> None:
    monkeypatch.setenv(ARCHIVE_ENV, "archive")
    with pytest.raises(intake_storage.IntakeStorageError) as error:
        intake_storage.get_local_archive_root()
    assert "absolute" in str(error.value)


# ------------------------------------------------------------------------------------- H2: local .env

def test_env_file_supplies_the_roots_when_the_environment_does_not(tmp_path: Path, monkeypatch) -> None:
    archive = tmp_path / "archive ñ"
    _env_file(
        tmp_path,
        monkeypatch,
        f"# comment\n\n{ARCHIVE_ENV}=\"{archive}\"\nPROMAT_BACKUP_ROOT = {tmp_path / 'backup'}\nPROMAT_PRESERVATION_ROOT=\n",
    )
    assert intake_storage.get_local_archive_root() == archive
    assert storage_roots.configured_source(ARCHIVE_ENV) == ".env"
    assert storage_roots.configured_root(storage_roots.BACKUP_ROOT_ENV) == tmp_path / "backup"
    assert storage_roots.configured_root(storage_roots.PRESERVATION_ROOT_ENV) is None  # empty value = unset
    assert not archive.exists()  # resolving a root never creates it


def test_process_environment_always_wins_over_the_env_file(tmp_path: Path, monkeypatch) -> None:
    _env_file(tmp_path, monkeypatch, f"{ARCHIVE_ENV}={tmp_path / 'from file'}\n")
    monkeypatch.setenv(ARCHIVE_ENV, str(tmp_path / "from environment"))
    assert intake_storage.get_local_archive_root() == tmp_path / "from environment"
    assert storage_roots.configured_source(ARCHIVE_ENV) == "environment"


def test_env_file_is_limited_to_storage_roots_and_never_touches_the_environment(tmp_path: Path, monkeypatch) -> None:
    path = _env_file(
        tmp_path,
        monkeypatch,
        f"FLASK_SECRET_KEY=from-file\nPROMAT_RUNTIME_ROOT={tmp_path}\n{ARCHIVE_ENV}={tmp_path / 'archive'}\n",
    )
    before = dict(os.environ)
    assert storage_roots.read_env_file() == {ARCHIVE_ENV: str(tmp_path / "archive")}
    intake_storage.get_local_archive_root()
    assert dict(os.environ) == before
    assert ARCHIVE_ENV not in os.environ
    with pytest.raises(ValueError):
        storage_roots.configured_value("FLASK_SECRET_KEY")
    assert path.read_text(encoding="utf-8").startswith("FLASK_SECRET_KEY")  # the file is only read


def test_env_file_with_bom_and_missing_file_are_handled(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / ".env"
    path.write_bytes(b"\xef\xbb\xbf" + f"{ARCHIVE_ENV}={tmp_path / 'a'}\r\n".encode())
    monkeypatch.setattr(storage_roots, "ENV_FILE", path)
    assert intake_storage.get_local_archive_root() == tmp_path / "a"
    monkeypatch.setattr(storage_roots, "ENV_FILE", tmp_path / "missing" / ".env")
    assert storage_roots.read_env_file() == {}


def test_env_example_names_exactly_the_three_roots_without_values() -> None:
    text = (TEST_REPO_ROOT / ".env.example").read_text(encoding="utf-8")
    assignments = [line for line in text.splitlines() if line and not line.startswith("#")]
    assert assignments == [f"{name}=" for name in storage_roots.STORAGE_ROOT_VARIABLES]
    ignored = (TEST_REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in ignored


# ------------------------------------------------------------------------------------- backup role

@pytest.fixture
def archive(tmp_path: Path) -> Path:
    root = tmp_path / "archive"
    _archive_session(tmp_path, root)
    return root


def _backup(tmp_path: Path, archive: Path, *extra: str) -> int:
    return cli.run(["backup-copy", "--archive-root", str(archive), "--backup-root", str(tmp_path / "ssd" / "backup"), *extra])


def test_backup_copy_is_verified_marked_as_backup_and_does_not_preserve(tmp_path: Path, archive: Path) -> None:
    (tmp_path / "ssd").mkdir()
    backup_path = tmp_path / "ssd" / "backup"
    assert _backup(tmp_path, archive) == cli.EXIT_OK
    assert not backup_path.exists()  # dry-run is the default and creates nothing
    assert _backup(tmp_path, archive, "--execute") == cli.EXIT_OK

    marker = json.loads((backup_path / "BACKUP_ROOT.json").read_text(encoding="utf-8"))
    assert marker["role"] == "backup" and marker["root_id"]
    assert not (backup_path / pres.MARKER_FILENAME).exists()
    unit_copy = backup_path / "archive" / Path(*UNIT.split("/"))
    assert fixity.compute_manifest(unit_copy) == fixity.compute_manifest(archive / Path(*UNIT.split("/")))

    receipt = json.loads(pres.local_receipt_path(archive, UNIT, pres.BACKUP).read_text(encoding="utf-8"))
    assert receipt["schema"] == "promat.backup_receipt.v1" and receipt["role"] == "backup"
    assert receipt["root_id"] == marker["root_id"] and receipt["verification"] == "full_sha256_readback"
    assert (backup_path / "_backup" / "receipts" / pres.receipt_filename(UNIT)).is_file()
    assert not pres.local_receipt_path(archive, UNIT, pres.PRESERVATION).exists()

    root = pres.open_preservation_root(backup_path, archive_root=archive, initialize=False, role=pres.BACKUP)
    state = pres.derive_state(archive, UNIT, root, full_verify=True)
    assert state["state"] == pres.STATE_BACKED_UP  # verified, and still never cleanup-eligible
    # A backup is not preservation: the preservation state of the unit is unchanged.
    assert pres.derive_state(archive, UNIT, None, full_verify=False)["state"] == pres.STATE_PENDING


def test_backup_never_makes_local_data_cleanup_eligible(tmp_path: Path, archive: Path) -> None:
    (tmp_path / "ssd").mkdir()
    assert _backup(tmp_path, archive, "--execute") == cli.EXIT_OK
    root = pres.open_preservation_root(tmp_path / "ssd" / "backup", archive_root=archive, initialize=False, role=pres.BACKUP)
    assert pres.STATE_CLEANUP_ELIGIBLE not in pres.BACKUP.states
    with pytest.raises(pres.PreservationConfigError):
        pres.cleanup_eligibility_report(archive, root)
    assert cli.run(["cleanup-report", "--archive-root", str(archive), "--preservation-root", str(tmp_path / "ssd" / "backup")]) == cli.EXIT_CONFIG


def test_a_backup_root_is_refused_as_preservation_root_and_the_reverse(tmp_path: Path, archive: Path) -> None:
    backup_path, preservation_path = tmp_path / "backup", tmp_path / "preservation"
    pres.open_preservation_root(backup_path, archive_root=archive, initialize=True, role=pres.BACKUP)
    pres.open_preservation_root(preservation_path, archive_root=archive, initialize=True)

    with pytest.raises(pres.PreservationConfigError, match="is a backup root"):
        pres.open_preservation_root(backup_path, archive_root=archive, initialize=True)
    with pytest.raises(pres.PreservationConfigError, match="is a preservation root"):
        pres.open_preservation_root(preservation_path, archive_root=archive, initialize=True, role=pres.BACKUP)
    assert cli.run(["copy", "--execute", "--archive-root", str(archive), "--preservation-root", str(backup_path)]) == cli.EXIT_CONFIG
    assert cli.run(["backup-copy", "--execute", "--archive-root", str(archive), "--backup-root", str(preservation_path)]) == cli.EXIT_CONFIG
    assert not (backup_path / pres.MARKER_FILENAME).exists() and not (backup_path / "archive").exists()
    assert not (preservation_path / "BACKUP_ROOT.json").exists() and not (preservation_path / "archive").exists()


def test_one_directory_cannot_be_configured_as_both_roles(tmp_path: Path, archive: Path, monkeypatch) -> None:
    shared = tmp_path / "shared"
    monkeypatch.setenv(pres.PRESERVATION_ROOT_ENV, str(shared))
    monkeypatch.setenv(pres.BACKUP_ROOT_ENV, str(shared / "nested"))
    assert cli.run(["backup-copy", "--execute", "--archive-root", str(archive)]) == cli.EXIT_CONFIG
    assert cli.run(["copy", "--execute", "--archive-root", str(archive)]) == cli.EXIT_CONFIG
    assert not shared.exists()


def test_backup_commands_reject_the_other_roles_option_and_scope_limits(tmp_path: Path, archive: Path) -> None:
    assert cli.run(["backup-copy", "--archive-root", str(archive), "--preservation-root", str(tmp_path / "x")]) == cli.EXIT_CONFIG
    assert cli.run(["copy", "--archive-root", str(archive), "--backup-root", str(tmp_path / "x")]) == cli.EXIT_CONFIG
    assert cli.run(["backup-copy", "--archive-root", str(archive), "--backup-root", str(tmp_path / "x"), "--exclude-secure"]) == cli.EXIT_CONFIG


def test_backup_root_may_not_be_the_archive_root(tmp_path: Path, archive: Path) -> None:
    assert cli.run(["backup-copy", "--execute", "--archive-root", str(archive), "--backup-root", str(archive / "backup")]) == cli.EXIT_CONFIG
    assert not (archive / "backup").exists()


def test_backup_copy_is_additive_and_never_overwrites_or_deletes(tmp_path: Path, archive: Path) -> None:
    (tmp_path / "ssd").mkdir()
    assert _backup(tmp_path, archive, "--execute") == cli.EXIT_OK
    unit_copy = tmp_path / "ssd" / "backup" / "archive" / Path(*UNIT.split("/"))
    stray = unit_copy.parent / "ES-L-0099-2026-S01" / "raw" / "kept.wav"
    stray.parent.mkdir(parents=True)
    stray.write_bytes(b"only in the backup")
    damaged = unit_copy / "runtime" / "metadata.json"
    damaged.write_text("changed in the backup", encoding="utf-8")

    assert _backup(tmp_path, archive, "--execute") == cli.EXIT_PROBLEMS  # conflict reported, nothing replaced
    assert damaged.read_text(encoding="utf-8") == "changed in the backup"
    assert stray.read_bytes() == b"only in the backup"


def test_backup_verify_detects_a_corrupted_backup(tmp_path: Path, archive: Path, capsys) -> None:
    (tmp_path / "ssd").mkdir()
    backup_path = tmp_path / "ssd" / "backup"
    assert _backup(tmp_path, archive, "--execute") == cli.EXIT_OK
    assert cli.run(["backup-verify", "--archive-root", str(archive), "--backup-root", str(backup_path)]) == cli.EXIT_OK
    assert "BACKED_UP=1" in capsys.readouterr().out
    (backup_path / "archive" / Path(*UNIT.split("/")) / "source" / "wordlist.wav").write_bytes(b"bit rot")
    assert cli.run(["backup-verify", "--archive-root", str(archive), "--backup-root", str(backup_path)]) == cli.EXIT_PROBLEMS
    assert "BACKUP_PENDING=1" in capsys.readouterr().out


def test_offline_backup_volume_is_a_reported_state_not_an_error(tmp_path: Path, archive: Path, monkeypatch, capsys) -> None:
    offline = tmp_path / "unplugged ssd" / "backup"
    monkeypatch.setenv(ARCHIVE_ENV, str(archive))
    monkeypatch.setenv(pres.BACKUP_ROOT_ENV, str(offline))

    assert cli.run(["backup-status"]) == cli.EXIT_OK
    assert "BACKUP_PENDING=1" in capsys.readouterr().out
    assert cli.run(["backup-copy", "--execute"]) == cli.EXIT_CONFIG  # the parent is missing: never created
    section = inventory.backup_section()
    assert section["configured"] is True and section["reachable"] is False
    assert not offline.parent.exists()
    # Intake and the archive getter do not depend on the backup volume at all.
    assert intake_storage.get_local_archive_root() == archive


# ------------------------------------------------------------------------------------- cold verification

@pytest.mark.skipif(os.name != "nt", reason="unbuffered reads are implemented for Windows volumes")
def test_unbuffered_hash_equals_the_buffered_hash(tmp_path: Path) -> None:
    for size in (0, 1, 511, 4096, 1024 * 1024, 1024 * 1024 + 17, 3 * 1024 * 1024 + 4095):
        path = tmp_path / "dir with ñ" / f"file {size}.bin"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(os.urandom(size))
        assert fixity.sha256_file_unbuffered(pres.fs_path(path)) == fixity.sha256_file(path), size
    with pytest.raises(OSError):
        fixity.sha256_file_unbuffered(tmp_path / "missing.bin")


@pytest.mark.skipif(os.name != "nt", reason="unbuffered reads are implemented for Windows volumes")
def test_backup_verify_unbuffered_confirms_and_detects_corruption(tmp_path: Path, archive: Path, capsys) -> None:
    (tmp_path / "ssd").mkdir()
    backup_path = tmp_path / "ssd" / "backup"
    assert _backup(tmp_path, archive, "--execute") == cli.EXIT_OK
    capsys.readouterr()
    arguments = ["backup-verify", "--unbuffered", "--archive-root", str(archive), "--backup-root", str(backup_path)]
    assert cli.run(arguments) == cli.EXIT_OK
    out = capsys.readouterr().out
    assert "BACKED_UP=1" in out and "read_mode=unbuffered" in out and "verified_files=" in out
    (backup_path / "archive" / Path(*UNIT.split("/")) / "raw").mkdir(exist_ok=True)
    (backup_path / "archive" / Path(*UNIT.split("/")) / "source" / "wordlist.wav").write_bytes(b"bit rot")
    assert cli.run(arguments) == cli.EXIT_PROBLEMS


# ------------------------------------------------------------------------------------- supplemental sets

@pytest.fixture
def supplemental_world(tmp_path: Path, archive: Path) -> dict[str, Path]:
    """An archive with non-unit entries plus operator-local files outside the archive."""
    (archive / "praat_pipeline" / "catalogs").mkdir(parents=True)
    (archive / "praat_pipeline" / "catalogs" / "wordlist.txt").write_text("uno\ndos\n", encoding="utf-8")
    (archive / "first_generation").mkdir()
    (archive / "first_generation" / "intake.xlsx").write_bytes(b"PK first generation")
    pres.baseline_unit(archive, UNIT, execute=True)  # covered by its unit manifest: writes nothing
    (archive / "fixity" / "baseline").mkdir(parents=True, exist_ok=True)
    (archive / "fixity" / "baseline" / "batches__old.sha256").write_text("", encoding="utf-8")
    checkout = tmp_path / "checkout ñ"
    for batch in ("spanish_batch_1", "french_batch_1"):
        (checkout / "import" / batch / "working").mkdir(parents=True)
        (checkout / "import" / batch / f"intake_{batch}.xlsx").write_bytes(b"PK " + batch.encode())
        (checkout / "import" / batch / "big.wav").write_bytes(b"RIFF not a workbook")
        (checkout / "import" / batch / "working" / "nested.xlsx").write_bytes(b"PK nested, not matched")
    (checkout / "config" / "spanish" / "task_catalogs").mkdir(parents=True)
    (checkout / "config" / "spanish" / "task_catalogs" / "wordlist.json").write_text('{"items": []}', encoding="utf-8")
    (tmp_path / "ssd").mkdir()
    return {"archive": archive, "checkout": checkout, "backup": tmp_path / "ssd" / "backup"}


def _supplemental(world: dict[str, Path], *extra: str) -> int:
    return cli.run([
        "backup-supplemental", "--archive-root", str(world["archive"]), "--backup-root", str(world["backup"]),
        "--label", "2026-10-07",
        "--extra", f"intake_workbooks={world['checkout'] / 'import' / '*' / '*.xlsx'}",
        "--extra", f"research_player_config={world['checkout'] / 'config'}",
        *extra,
    ])


def test_supplemental_backup_copies_uncovered_material_with_its_own_manifest(supplemental_world, capsys) -> None:
    world = supplemental_world
    assert _supplemental(world) == cli.EXIT_OK
    assert not world["backup"].exists()  # dry-run
    assert "would_back_up=5" in capsys.readouterr().out
    assert _supplemental(world, "--execute") == cli.EXIT_OK

    base = world["backup"] / "supplemental" / "2026-10-07"
    assert sorted(p.name for p in base.iterdir()) == ["_manifests", "first_generation", "fixity", "intake_workbooks", "praat_pipeline", "research_player_config"]
    assert (base / "praat_pipeline" / "catalogs" / "wordlist.txt").read_text(encoding="utf-8") == "uno\ndos\n"
    assert (base / "fixity" / "baseline" / "batches__old.sha256").is_file()
    # The glob takes the workbooks of every batch, and nothing else from the batch folders.
    workbooks = sorted(p.relative_to(base / "intake_workbooks").as_posix() for p in (base / "intake_workbooks").rglob("*") if p.is_file())
    assert workbooks == ["french_batch_1/intake_french_batch_1.xlsx", "spanish_batch_1/intake_spanish_batch_1.xlsx"]
    assert (base / "research_player_config" / "spanish" / "task_catalogs" / "wordlist.json").is_file()

    manifest = fixity.read_manifest(base / "_manifests" / "intake_workbooks.sha256")
    assert sorted(manifest) == workbooks
    meta = json.loads((base / "_manifests" / "intake_workbooks.json").read_text(encoding="utf-8"))
    assert meta["role"] == "backup" and meta["file_count"] == 2 and meta["verification"] == "full_sha256_readback"
    assert str(world["checkout"]) not in json.dumps(meta)  # no machine path in the evidence
    assert (world["archive"] / "backup" / "receipts" / "supplemental" / "2026-10-07__intake_workbooks.json").is_file()
    assert (world["backup"] / "BACKUP_ROOT.json").is_file() and not (world["backup"] / pres.MARKER_FILENAME).exists()
    assert _supplemental(world, "--execute") == cli.EXIT_OK  # idempotent: everything already present


def test_backup_verify_covers_supplemental_sets_without_their_source(supplemental_world, capsys) -> None:
    world = supplemental_world
    assert _supplemental(world, "--execute") == cli.EXIT_OK
    assert cli.run(["backup-copy", "--execute", "--archive-root", str(world["archive"]), "--backup-root", str(world["backup"])]) == cli.EXIT_OK
    import shutil

    shutil.rmtree(world["checkout"])  # the sets verify against their own manifests
    capsys.readouterr()
    verify = ["backup-verify", "--archive-root", str(world["archive"]), "--backup-root", str(world["backup"])]
    assert cli.run(verify) == cli.EXIT_OK
    out = capsys.readouterr().out
    assert "supplemental_ok=5" in out and "supplemental_failed=0" in out and "BACKED_UP=1" in out

    target = world["backup"] / "supplemental" / "2026-10-07" / "intake_workbooks" / "spanish_batch_1" / "intake_spanish_batch_1.xlsx"
    target.write_bytes(b"damaged")
    assert cli.run(verify) == cli.EXIT_PROBLEMS
    assert "supplemental_failed=1" in capsys.readouterr().out
    target.unlink()
    assert cli.run(verify) == cli.EXIT_PROBLEMS  # a missing file is a failure as well


def test_supplemental_label_is_a_snapshot_and_is_never_overwritten(supplemental_world, capsys) -> None:
    world = supplemental_world
    assert _supplemental(world, "--execute") == cli.EXIT_OK
    catalog = world["checkout"] / "config" / "spanish" / "task_catalogs" / "wordlist.json"
    catalog.write_text('{"items": ["changed"]}', encoding="utf-8")
    capsys.readouterr()

    assert _supplemental(world, "--execute") == cli.EXIT_PROBLEMS
    assert "conflict_manifest_differs=1" in capsys.readouterr().out
    kept = world["backup"] / "supplemental" / "2026-10-07" / "research_player_config" / "spanish" / "task_catalogs" / "wordlist.json"
    assert kept.read_text(encoding="utf-8") == '{"items": []}'

    arguments = [
        "backup-supplemental", "--execute", "--archive-root", str(world["archive"]), "--backup-root", str(world["backup"]),
        "--label", "2026-11-01", "--extra", f"research_player_config={world['checkout'] / 'config'}",
    ]
    assert cli.run(arguments) == cli.EXIT_OK
    newer = world["backup"] / "supplemental" / "2026-11-01" / "research_player_config" / "spanish" / "task_catalogs" / "wordlist.json"
    assert newer.read_text(encoding="utf-8") == '{"items": ["changed"]}' and kept.read_text(encoding="utf-8") == '{"items": []}'


def test_supplemental_rejects_unusable_sets(supplemental_world, capsys) -> None:
    world = supplemental_world
    base = ["backup-supplemental", "--archive-root", str(world["archive"]), "--backup-root", str(world["backup"])]
    assert cli.run([*base, "--extra", "no-separator"]) == cli.EXIT_CONFIG
    assert cli.run([*base, "--extra", f"praat_pipeline={world['checkout']}"]) == cli.EXIT_CONFIG  # name already taken
    assert cli.run([*base, "--extra", f"empty={world['checkout'] / 'does not exist'}"]) == cli.EXIT_PROBLEMS
    assert cli.run([*base, "--label", "../escape"]) == cli.EXIT_PROBLEMS
    assert not world["backup"].exists()


def test_only_the_storage_tooling_knows_the_backup_and_preservation_roots() -> None:
    """Neither intake nor the web application may read, or fall back to, the backup or the preservation root."""
    allowed = {"preservation.py", "archive_preservation.py", "storage_roots.py"}
    for path in INTAKE_DIR.rglob("*.py"):
        relative = path.relative_to(INTAKE_DIR).parts
        if path.name in allowed or relative[0] in {"import", "exports", ".mfa_cache"}:
            continue
        assert "BACKUP_ROOT" not in path.read_text(encoding="utf-8"), path.name
    for path in (TEST_REPO_ROOT / "app" / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not any(name in text for name in storage_roots.STORAGE_ROOT_VARIABLES), path.name
