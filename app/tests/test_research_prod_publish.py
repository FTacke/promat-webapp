from __future__ import annotations

import sys
from pathlib import Path


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

from publish_prod_release import RemotePublishOptions, build_remote_publish_script  # noqa: E402


def test_publish_without_flag_skips_db_upsert() -> None:
    script = build_remote_publish_script(
        RemotePublishOptions(
            upload_id="english_batch_20260618_runtime",
            smoke_base_url="https://promat.example.test",
        )
    )

    assert "DB_STATUS=\"skipped_no_flag\"" in script
    assert "--apply-db-upsert not set" in script
    assert "--apply)" not in script


def test_publish_with_flag_runs_db_dry_run_and_apply_before_current_switch() -> None:
    script = build_remote_publish_script(
        RemotePublishOptions(
            upload_id="english_batch_20260618_runtime",
            apply_db_upsert=True,
            smoke_base_url="https://promat.example.test",
        )
    )

    dry_run_index = script.index("DB_DRY_RUN_OUTPUT")
    apply_index = script.index("DB_APPLY_OUTPUT")
    switch_index = script.index("ln -sfn \"$RELEASE\" \"$CURRENT.tmp\"")
    assert "docker exec -i \"$DB_CONTAINER\" python -" in script
    assert "--release-dir \"$CONTAINER_RELEASE\"" in script
    assert "test -f \"$RELEASE/db/import_payload.json\"" in script
    assert "apply_prod_db_payload.py" in script
    assert "--apply < \"$APP_ROOT/scripts/research_data_intake/apply_prod_db_payload.py\"" in script
    assert dry_run_index < apply_index < switch_index


def test_publish_log_documents_db_upsert_status() -> None:
    script = build_remote_publish_script(
        RemotePublishOptions(
            upload_id="english_batch_20260618_runtime",
            apply_db_upsert=True,
            smoke_base_url="https://promat.example.test",
        )
    )

    assert "db_payload_present: $DB_PAYLOAD_PRESENT" in script
    assert "db_upsert_status: $DB_STATUS" in script
    assert "db_post_upsert_validation: $DB_POST_VALIDATION" in script
    assert "## DB Dry Run" in script
    assert "## DB Apply" in script
