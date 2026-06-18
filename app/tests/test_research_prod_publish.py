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
    switch_index = script.index('ln -sfn "releases/$RELEASE_ID" "$CURRENT.tmp"')
    assert "docker exec \"$DB_CONTAINER\" python /app/scripts/research_data_intake/apply_prod_db_payload.py" in script
    assert "--release-dir \"$CONTAINER_RELEASE\"" in script
    assert "test -f \"$RELEASE/db/import_payload.json\"" in script
    assert "--apply)" in script
    assert dry_run_index < apply_index < switch_index


def test_current_symlink_is_relative() -> None:
    script = build_remote_publish_script(
        RemotePublishOptions(
            upload_id="english_batch_20260618_runtime",
            smoke_base_url="https://promat.example.test",
        )
    )

    assert 'ln -sfn "releases/$RELEASE_ID" "$CURRENT.tmp"' in script
    assert 'ln -sfn "$RELEASE"' not in script


def test_sessions_are_synced_from_release_after_current_switch() -> None:
    script = build_remote_publish_script(
        RemotePublishOptions(
            upload_id="english_batch_20260618_runtime",
            smoke_base_url="https://promat.example.test",
        )
    )

    switch_index = script.index('ln -sfn "releases/$RELEASE_ID" "$CURRENT.tmp"')
    sync_index = script.index('for corpus_dir in "$RELEASE/sessions"')
    health_index = script.index("HEALTH_STATUS=")
    assert switch_index < sync_index < health_index
    assert 'rm -rf "$corpus_target"' in script
    assert 'rsync -a "$corpus_dir" "$corpus_target/"' in script
    assert 'SESSIONS_SYNC_STATUS="applied"' in script


def test_container_is_restarted_after_session_sync() -> None:
    script = build_remote_publish_script(
        RemotePublishOptions(
            upload_id="english_batch_20260618_runtime",
            smoke_base_url="https://promat.example.test",
        )
    )

    sync_index = script.index('SESSIONS_SYNC_STATUS="applied"')
    restart_index = script.index('docker restart "$DB_CONTAINER"')
    health_index = script.index("HEALTH_STATUS=")
    assert sync_index < restart_index < health_index
    assert 'CONTAINER_RESTART_STATUS="done"' in script


def test_no_restart_flag_skips_restart_block() -> None:
    script = build_remote_publish_script(
        RemotePublishOptions(
            upload_id="english_batch_20260618_runtime",
            restart_container=False,
            smoke_base_url="https://promat.example.test",
        )
    )

    assert 'docker restart' not in script
    assert 'CONTAINER_RESTART_STATUS="skipped_no_flag"' in script


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
    assert "sessions_sync_status: $SESSIONS_SYNC_STATUS" in script
    assert "container_restart_status: $CONTAINER_RESTART_STATUS" in script
    assert "## DB Dry Run" in script
    assert "## DB Apply" in script
    assert "```json" not in script
    assert "~~~json" in script
    assert "\r" not in script
