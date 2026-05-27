from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

import upload_prod_package  # noqa: E402


def test_require_safe_remote_dir_rejects_reserved_segments() -> None:
    with pytest.raises(ValueError):
        upload_prod_package._require_safe_remote_dir(
            "/srv/webapps_storage/promat/data/incoming/current/french_batch_20260527_initial_fix01"
        )

    with pytest.raises(ValueError):
        upload_prod_package._require_safe_remote_dir(
            "/srv/webapps_storage/promat/data/incoming/releases/french_batch_20260527_initial_fix01"
        )

    with pytest.raises(ValueError):
        upload_prod_package._require_safe_remote_dir(
            "/srv/webapps_storage/promat/data/incoming/production/french_batch_20260527_initial_fix01"
        )


def test_require_safe_remote_dir_accepts_upload_id_target() -> None:
    upload_prod_package._require_safe_remote_dir(
        "/srv/webapps_storage/promat/data/incoming/french_batch_20260527_initial_fix01"
    )


def test_choose_upload_method_auto_prefers_rsync_when_available() -> None:
    method = upload_prod_package._choose_upload_method("auto", rsync_available=True, remote_rsync_available=True)

    assert method == "rsync"


def test_choose_upload_method_auto_falls_back_to_tar_ssh_when_rsync_missing() -> None:
    method = upload_prod_package._choose_upload_method("auto", rsync_available=False, remote_rsync_available=False)

    assert method == "tar-over-ssh"


def test_choose_upload_method_rsync_requires_local_and_remote_rsync() -> None:
    with pytest.raises(RuntimeError):
        upload_prod_package._choose_upload_method("rsync", rsync_available=False, remote_rsync_available=True)

    with pytest.raises(RuntimeError):
        upload_prod_package._choose_upload_method("rsync", rsync_available=True, remote_rsync_available=False)


def test_choose_upload_method_tar_ssh_always_allowed() -> None:
    method = upload_prod_package._choose_upload_method("tar-ssh", rsync_available=False, remote_rsync_available=False)

    assert method == "tar-over-ssh"
