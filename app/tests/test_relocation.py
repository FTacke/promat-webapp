"""Relocation canary: the app and the archive tooling work from any location, with spaces and non-ASCII names.

Everything lives below ``tmp_path / "Pronunciation Matters ñ"`` and is built from synthetic fixtures; the working
directory is deliberately an unrelated folder, so nothing may depend on where the checkout or the data stand.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "qa"))

import fixity  # noqa: E402
import intake_storage  # noqa: E402
import preservation as pres  # noqa: E402
import storage_roots  # noqa: E402
from conftest import _clear_catalog_caches  # noqa: E402
from fixture_runtime import build_runtime  # noqa: E402
from test_archive_preservation import UNIT, _archive_session  # noqa: E402
from test_session_state import _add_user, _login  # noqa: E402

BASE_NAME = "Pronunciation Matters ñ"
SESSION = "ES-L-0001-2026-S01"


@pytest.fixture
def elsewhere(tmp_path: Path, monkeypatch) -> Path:
    """An unrelated working directory: neither the repository nor any data root."""
    directory = tmp_path / "unrelated working directory"
    directory.mkdir()
    monkeypatch.chdir(directory)
    return directory


def _clear_runtime_caches() -> None:
    """The session loaders cache per process (the app is restarted after a data change); tests share one process."""
    from app.research_player_runtime import load_task_ready_sessions
    from app.research_sessions import load_language_sessions, load_person_records

    _clear_catalog_caches()
    for cached in (load_language_sessions, load_person_records, load_task_ready_sessions):
        cached.cache_clear()


@pytest.fixture
def relocated_app(tmp_path: Path, real_app_factory, elsewhere: Path):
    runtime_root = build_runtime(tmp_path / BASE_NAME / "nested" / "runtime root ñ")
    _clear_runtime_caches()
    flask_app = real_app_factory(runtime_root=runtime_root)
    with flask_app.app_context():
        _add_user("user-1", "alice")
    yield flask_app, runtime_root
    _clear_runtime_caches()


def test_app_serves_pages_assets_and_audio_from_a_relocated_runtime(relocated_app, elsewhere: Path) -> None:
    flask_app, runtime_root = relocated_app
    assert Path(flask_app.config["SESSIONS_ROOT"]) == runtime_root / "data" / "sessions"
    assert BASE_NAME in str(flask_app.config["RUNTIME_ROOT"])
    assert Path.cwd() == elsewhere

    client = flask_app.test_client()
    assert client.get("/de/project/about").status_code == 200
    assert client.get("/en/teaching").status_code == 200  # repo-relative content, resolved without the cwd
    assert client.get("/de/impressum").status_code == 200  # content/legal, resolved from the package location
    asset = client.get("/static/css/00_tokens.css")
    assert asset.status_code == 200 and asset.data
    assert client.get("/de/research/spanish/design").status_code == 200
    assert client.get("/ready").status_code == 200

    audio_path = f"/de/research/spanish/player/{SESSION}/wordlist/audio.mp3"
    assert client.get(audio_path).status_code in {302, 303}  # protected: no anonymous delivery
    member = _login(flask_app, "alice")
    assert member.get("/de/research/spanish/speakers").status_code == 200
    assert member.get(f"/de/research/spanish/player/{SESSION}/wordlist").status_code == 200
    audio = member.get(audio_path)
    assert audio.status_code == 200
    assert audio.data == (runtime_root / "data" / "sessions" / "spanish" / SESSION / "derived" / "wordlist.mp3").read_bytes()
    assert list(elsewhere.iterdir()) == []  # the app wrote nothing into the working directory


def test_archive_unit_stays_valid_after_the_archive_root_moves(tmp_path: Path, monkeypatch, elsewhere: Path) -> None:
    base = tmp_path / BASE_NAME
    first, second = base / "archive a", base / "moved ñ" / "archive b"
    monkeypatch.setenv(storage_roots.LOCAL_ARCHIVE_ROOT_ENV, str(first))

    result = _archive_session(tmp_path, None)  # the root comes from the configuration, not from an argument
    assert result.archive_session_dir == first / "sessions" / "es" / SESSION
    before = fixity.compute_manifest(first)
    expected = pres.resolve_expected_fixity(first, UNIT)
    assert expected is not None and expected.origin == "unit_manifest"

    # Nothing persisted knows where the archive stands.
    unit_dir = first / Path(*UNIT.split("/"))
    for name in ("metadata/archive_manifest.json", "metadata/checksums.sha256", "reports/import_report.json"):
        text = (unit_dir / name).read_text(encoding="utf-8")
        assert str(tmp_path) not in text and BASE_NAME not in text and str(tmp_path).replace("\\", "/") not in text, name
    assert "\\" not in (unit_dir / "metadata" / "checksums.sha256").read_text(encoding="utf-8")
    manifest = json.loads((unit_dir / "metadata" / "archive_manifest.json").read_text(encoding="utf-8"))
    assert all(not Path(entry["path"]).is_absolute() for entry in manifest["input_files"] + manifest["generated_runtime_files"])

    second.parent.mkdir(parents=True)
    shutil.move(str(first), str(second))
    monkeypatch.setenv(storage_roots.LOCAL_ARCHIVE_ROOT_ENV, str(second))

    assert intake_storage.get_local_archive_root() == second
    assert intake_storage.archive_session_dir("es", SESSION) == second / "sessions" / "es" / SESSION
    assert fixity.compute_manifest(second) == before
    moved = pres.resolve_expected_fixity(second, UNIT)
    assert moved is not None and moved.manifest_sha256 == expected.manifest_sha256
    check = fixity.verify_manifest(second / Path(*UNIT.split("/")), moved.entries)
    assert check == {"missing": [], "mismatched": [], "unreadable": [], "extra": []}
    assert pres.derive_state(second, UNIT, None, full_verify=False)["state"] == pres.STATE_PENDING
    assert not first.exists()
    assert list(elsewhere.iterdir()) == []


def test_without_an_archive_root_nothing_falls_back_to_a_former_location(tmp_path: Path, elsewhere: Path) -> None:
    with pytest.raises(intake_storage.IntakeStorageError):
        intake_storage.get_local_archive_root()
    with pytest.raises(intake_storage.IntakeStorageError):
        _archive_session(tmp_path, None)
    assert list(elsewhere.iterdir()) == []
    created = {path.name for path in tmp_path.rglob("*") if path.is_dir()}
    assert not created & {"sessions", "batches", "promat_data" + "_archive"}
