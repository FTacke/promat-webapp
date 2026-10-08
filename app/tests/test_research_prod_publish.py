from __future__ import annotations

import sys
from pathlib import Path


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

from publish_prod_release import (  # noqa: E402
    RemotePublishOptions,
    build_remote_publish_script,
    build_standalone_retention_script,
)


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


# ── Release-Retention ─────────────────────────────────────────────────────────

def _default_script() -> str:
    return build_remote_publish_script(
        RemotePublishOptions(
            upload_id="english_batch_20260618_runtime",
            smoke_base_url="https://promat.example.test",
        )
    )


def test_retention_current_release_is_never_deleted() -> None:
    script = _default_script()
    # current is excluded via readlink comparison
    assert 'RETENTION_CURRENT="$(readlink -f "$CURRENT"' in script
    assert '[ "$_r" != "$RETENTION_CURRENT" ] || continue' in script


def test_retention_keeps_previous_release_within_age_limit() -> None:
    script = _default_script()
    assert "_AGE" in script
    assert '"$_AGE" -le 7' in script
    assert "_RET_PREV_KEPT" in script
    assert "continue" in script


def test_retention_deletes_previous_release_older_than_age_limit() -> None:
    script = _default_script()
    # When age > retention_days the rm -rf path is taken
    assert 'rm -rf "$_r"' in script
    assert "_RET_DELETED" in script


def test_retention_path_safety_check_prevents_out_of_bounds_delete() -> None:
    script = _default_script()
    assert '"$DATA_ROOT/releases/release_"*)' in script
    assert "*) continue ;;" in script


def test_retention_only_runs_when_health_and_ready_are_200() -> None:
    script = _default_script()
    health_gate_index = script.index('if [ "$HEALTH_STATUS" = "200" ] && [ "$READY_STATUS" = "200" ]')
    inner_block_index = script.index('_RET_PREV_COUNT=0')
    retention_applied_index = script.index('RETENTION_STATUS="applied"')
    log_index = script.index("release_retention_status: $RETENTION_STATUS")
    # Gate wraps the inner block; log comes after
    assert health_gate_index < inner_block_index < retention_applied_index < log_index


def test_no_release_retention_flag_skips_cleanup() -> None:
    script = build_remote_publish_script(
        RemotePublishOptions(
            upload_id="english_batch_20260618_runtime",
            smoke_base_url="https://promat.example.test",
            no_release_retention=True,
        )
    )
    assert 'RETENTION_STATUS="skipped_no_flag"' in script
    assert 'rm -rf "$_r"' not in script
    assert "RETENTION_POLICY=none_no_flag" in script


def test_publish_log_contains_retention_fields() -> None:
    script = _default_script()
    assert "release_retention_status: $RETENTION_STATUS" in script
    assert "current_release: $RETENTION_CURRENT" in script
    assert "previous_release_kept: $RETENTION_PREVIOUS_KEPT" in script
    assert "previous_release_age_days: $RETENTION_PREVIOUS_AGE_DAYS" in script
    assert "deleted_releases: $RETENTION_DELETED" in script
    assert "retention_policy: $RETENTION_POLICY" in script


def test_retention_custom_days_wired_into_script() -> None:
    script = build_remote_publish_script(
        RemotePublishOptions(
            upload_id="english_batch_20260618_runtime",
            smoke_base_url="https://promat.example.test",
            release_retention_days=14,
            release_retention_previous=2,
        )
    )
    assert '"$_AGE" -le 14' in script
    assert '"$_RET_PREV_COUNT" -lt 2' in script
    assert "keep_current_plus_2_previous_max_14_days" in script


def test_standalone_retention_preview_shows_would_delete_without_rm() -> None:
    script = build_standalone_retention_script(
        data_root="/srv/webapps_storage/promat/data",
        retention_days=7,
        retention_previous=1,
        apply=False,
    )
    assert "DRY_RUN" in script
    assert "would_delete:" in script
    assert "keep_as_previous" in script
    assert "rm -rf" not in script
    assert "\r" not in script


def test_standalone_retention_apply_script_does_rm() -> None:
    script = build_standalone_retention_script(
        data_root="/srv/webapps_storage/promat/data",
        retention_days=7,
        retention_previous=1,
        apply=True,
    )
    assert "APPLY" in script
    assert 'rm -rf "$_r"' in script
    assert "\r" not in script


def _replace_script(**overrides) -> str:
    options = dict(
        upload_id="corpora_replace_20261008",
        apply_db_upsert=True,
        smoke_base_url="https://promat.example.test",
        replace_corpora=("english", "french", "spanish"),
    )
    options.update(overrides)
    return build_remote_publish_script(RemotePublishOptions(**options))


def test_replace_removes_old_corpus_sessions_from_the_staged_release_only() -> None:
    script = _replace_script()

    stage_copy = script.index('tar -cf - .) | (cd "$RELEASE" && tar -xf -)')
    for slug in ("english", "french", "spanish"):
        removal = script.index(f'rm -rf -- "$RELEASE/sessions/{slug}"')
        assert stage_copy < removal < script.index('(cd "$INCOMING" && tar -cf - .)')
    assert 'rm -rf -- "$RELEASE/sessions/german"' not in script
    assert "$CURRENT/sessions" not in script and 'rm -rf -- "$CURRENT' not in script


def test_replace_requires_the_upload_manifest_to_declare_exactly_the_same_corpora() -> None:
    script = _replace_script()

    assert 'MANIFEST_REPLACE="$(python3 -c' in script
    assert '[ "$MANIFEST_REPLACE" != english,french,spanish ]' in script
    assert script.index("MANIFEST_REPLACE") < script.index('mkdir -p "$RELEASE"')


def test_replace_passes_each_language_to_the_db_dry_run_and_apply() -> None:
    script = _replace_script()

    assert script.count("--replace-language en --replace-language fr --replace-language es") == 2
    assert "--replace-language de" not in script


def test_replace_without_db_upsert_is_rejected() -> None:
    import pytest

    with pytest.raises(ValueError, match="requires --apply-db-upsert"):
        _replace_script(apply_db_upsert=False)
    with pytest.raises(ValueError, match="unsupported replace corpus"):
        _replace_script(replace_corpora=("klingon",))


def test_upload_without_replace_flag_is_refused_when_manifest_declares_replacement() -> None:
    script = build_remote_publish_script(
        RemotePublishOptions(upload_id="plain_upload", apply_db_upsert=True, smoke_base_url="https://promat.example.test")
    )

    assert "Upload manifest declares replace_corpora but --replace-corpus was not given" in script
    assert 'rm -rf -- "$RELEASE/sessions/' not in script


def test_db_post_validation_status_must_be_ok_before_the_current_switch() -> None:
    script = _replace_script()

    assert script.index('test "$DB_POST_VALIDATION" = "ok"') < script.index('ln -sfn "releases/$RELEASE_ID"')
