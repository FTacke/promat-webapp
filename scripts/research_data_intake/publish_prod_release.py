from __future__ import annotations

import argparse
from dataclasses import dataclass
import shlex
import subprocess


DEFAULT_DATA_ROOT = "/srv/webapps_storage/promat/data"
DEFAULT_REMOTE_APP_ROOT = "/srv/webapps/promat/app"
DEFAULT_DB_CONTAINER = "promat-web-prod"
DEFAULT_CONTAINER_DATA_ROOT = "/app/data"
DEFAULT_CONTAINER_RESTART_DELAY = 15


@dataclass(frozen=True, slots=True)
class RemotePublishOptions:
    upload_id: str
    data_root: str = DEFAULT_DATA_ROOT
    remote_app_root: str = DEFAULT_REMOTE_APP_ROOT
    db_container: str = DEFAULT_DB_CONTAINER
    container_data_root: str = DEFAULT_CONTAINER_DATA_ROOT
    apply_db_upsert: bool = False
    restart_container: bool = True
    smoke_base_url: str = "https://promat.example.invalid"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote a staged PROMAT incoming upload on the production server with optional DB payload upsert."
    )
    parser.add_argument("--upload-id", required=True, help="Incoming upload id below the production data/incoming root.")
    parser.add_argument("--host", required=True, help="SSH host for the production server.")
    parser.add_argument("--ssh-user", default="root", help="SSH user. Defaults to root.")
    parser.add_argument("--data-root", default=DEFAULT_DATA_ROOT, help="Production data root.")
    parser.add_argument("--remote-app-root", default=DEFAULT_REMOTE_APP_ROOT, help="Remote checked-out app root.")
    parser.add_argument("--db-container", default=DEFAULT_DB_CONTAINER, help="Container that has app dependencies and AUTH_DATABASE_URL.")
    parser.add_argument("--container-data-root", default=DEFAULT_CONTAINER_DATA_ROOT, help="Data root as mounted inside the DB container.")
    parser.add_argument(
        "--apply-db-upsert",
        action="store_true",
        help="Validate and apply db/import_payload.json before the atomic current switch.",
    )
    parser.add_argument(
        "--no-restart-container",
        dest="restart_container",
        action="store_false",
        help="Skip the app-container restart after promote. Default is to restart so the runtime cache is invalidated.",
    )
    parser.add_argument(
        "--smoke-base-url",
        default="https://promat.example.invalid",
        help="Base URL used for health and smoke checks after promote.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the remote script instead of running SSH.")
    return parser.parse_args()


def _q(value: str) -> str:
    return shlex.quote(value)


def build_remote_publish_script(options: RemotePublishOptions) -> str:
    db_block = _db_upsert_block() if options.apply_db_upsert else _db_skip_block()
    sync_sessions_block = _sync_sessions_block()
    restart_block = _restart_container_block(DEFAULT_CONTAINER_RESTART_DELAY) if options.restart_container else _restart_skip_block()
    script = f"""#!/usr/bin/env bash
set -euo pipefail

UPLOAD_ID={_q(options.upload_id)}
DATA_ROOT={_q(options.data_root)}
APP_ROOT={_q(options.remote_app_root)}
DB_CONTAINER={_q(options.db_container)}
CONTAINER_DATA_ROOT={_q(options.container_data_root)}
SMOKE_BASE_URL={_q(options.smoke_base_url)}
INCOMING="$DATA_ROOT/incoming/$UPLOAD_ID"
RELEASES="$DATA_ROOT/releases"
CURRENT="$DATA_ROOT/current"
PUBLISH_LOG_DIR="$DATA_ROOT/publish_logs"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RELEASE_ID="release_${{TIMESTAMP}}_${{UPLOAD_ID}}"
RELEASE="$RELEASES/$RELEASE_ID"
PUBLISH_LOG="$PUBLISH_LOG_DIR/promat_publish_${{UPLOAD_ID}}_${{TIMESTAMP}}.md"
DB_DRY_RUN_OUTPUT=""
DB_APPLY_OUTPUT=""
DB_STATUS="skipped"
DB_PAYLOAD_PRESENT="no"
DB_POST_VALIDATION="not_run"
SESSIONS_SYNC_STATUS="not_run"
CONTAINER_RESTART_STATUS="not_run"
CONTAINER_RELEASE="$CONTAINER_DATA_ROOT/releases/$RELEASE_ID"

mkdir -p "$RELEASES" "$PUBLISH_LOG_DIR"
test -d "$INCOMING" || {{ echo "Incoming upload is missing: $INCOMING" >&2; exit 1; }}
test -f "$INCOMING/checksums.sha256" || {{ echo "Incoming checksums.sha256 is missing" >&2; exit 1; }}

cd "$INCOMING"
sha256sum -c checksums.sha256
if [ -f "$INCOMING/db/import_payload.json" ]; then
  DB_PAYLOAD_PRESENT="yes"
fi

mkdir -p "$RELEASE"
if [ -L "$CURRENT" ] || [ -d "$CURRENT" ]; then
  CURRENT_REAL="$(readlink -f "$CURRENT")"
  if [ -n "$CURRENT_REAL" ] && [ -d "$CURRENT_REAL" ]; then
    (cd "$CURRENT_REAL" && tar -cf - .) | (cd "$RELEASE" && tar -xf -)
  fi
fi
(cd "$INCOMING" && tar -cf - .) | (cd "$RELEASE" && tar -xf -)

cd "$RELEASE"
sha256sum -c "$INCOMING/checksums.sha256"
find "$RELEASE" \\( -name '*.wav' -o -name '*.TextGrid' -o -name '*.xlsx' \\) -print -quit | grep -q . && {{
  echo "Forbidden source artifact found in release" >&2
  exit 1
}} || true
for forbidden_dir in secure raw source alignment_source working; do
  find "$RELEASE" -type d -name "$forbidden_dir" -print -quit | grep -q . && {{
    echo "Forbidden directory found in release: $forbidden_dir" >&2
    exit 1
  }} || true
done

{db_block}

ln -sfn "releases/$RELEASE_ID" "$CURRENT.tmp"
mv -Tf "$CURRENT.tmp" "$CURRENT"

{sync_sessions_block}

{restart_block}

HEALTH_STATUS="$(curl -fsS -o /dev/null -w '%{{http_code}}' "$SMOKE_BASE_URL/health" || true)"
READY_STATUS="$(curl -fsS -o /dev/null -w '%{{http_code}}' "$SMOKE_BASE_URL/ready" || true)"

cat > "$PUBLISH_LOG" <<REPORT
# PROMAT Publish $UPLOAD_ID

- upload_id: $UPLOAD_ID
- release: $RELEASE
- current: $(readlink -f "$CURRENT")
- db_payload_present: $DB_PAYLOAD_PRESENT
- db_upsert_status: $DB_STATUS
- db_post_upsert_validation: $DB_POST_VALIDATION
- db_command: docker exec $DB_CONTAINER python /app/scripts/research_data_intake/apply_prod_db_payload.py --release-dir "$CONTAINER_RELEASE" --payload "$CONTAINER_RELEASE/db/import_payload.json"
- sessions_sync_status: $SESSIONS_SYNC_STATUS
- container_restart_status: $CONTAINER_RESTART_STATUS
- health_status: $HEALTH_STATUS
- ready_status: $READY_STATUS
- rollback_hint: repoint current to the previous release with a relative symlink; rsync the previous release sessions to DATA_ROOT/sessions/; restart the container.

## DB Dry Run

~~~json
$DB_DRY_RUN_OUTPUT
~~~

## DB Apply

~~~json
$DB_APPLY_OUTPUT
~~~
REPORT

rm -rf "$INCOMING"
echo "$PUBLISH_LOG"
"""
    return script.replace("\r\n", "\n")


def _sync_sessions_block() -> str:
    return """if [ -d "$RELEASE/sessions" ]; then
  mkdir -p "$DATA_ROOT/sessions"
  for corpus_dir in "$RELEASE/sessions"/*/; do
    [ -d "$corpus_dir" ] || continue
    corpus="$(basename "$corpus_dir")"
    corpus_target="$DATA_ROOT/sessions/$corpus"
    rm -rf "$corpus_target"
    rsync -a "$corpus_dir" "$corpus_target/"
  done
  SESSIONS_SYNC_STATUS="applied"
else
  SESSIONS_SYNC_STATUS="skipped_no_sessions_in_release"
fi
"""


def _restart_container_block(delay_seconds: int) -> str:
    return f"""if docker restart "$DB_CONTAINER" 2>/dev/null; then
  sleep {delay_seconds}
  CONTAINER_RESTART_STATUS="done"
else
  CONTAINER_RESTART_STATUS="failed"
fi
"""


def _restart_skip_block() -> str:
    return 'CONTAINER_RESTART_STATUS="skipped_no_flag"\n'


def _db_skip_block() -> str:
    return """DB_STATUS="skipped_no_flag"
DB_DRY_RUN_OUTPUT="{\\"mode\\":\\"skipped\\",\\"reason\\":\\"--apply-db-upsert not set\\"}"
DB_APPLY_OUTPUT="{\\"mode\\":\\"skipped\\",\\"reason\\":\\"--apply-db-upsert not set\\"}"
"""


def _db_upsert_block() -> str:
    base_command = (
        'docker exec "$DB_CONTAINER" python /app/scripts/research_data_intake/apply_prod_db_payload.py '
        '--release-dir "$CONTAINER_RELEASE" --payload "$CONTAINER_RELEASE/db/import_payload.json"'
    )
    dry_run_command = base_command
    apply_command = f"{base_command} --apply"
    return f"""test -f "$RELEASE/db/import_payload.json" || {{
  echo "--apply-db-upsert requires $RELEASE/db/import_payload.json" >&2
  exit 1
}}
DB_STATUS="dry_run_started"
DB_DRY_RUN_OUTPUT="$({dry_run_command})"
DB_STATUS="apply_started"
DB_APPLY_OUTPUT="$({apply_command})"
DB_STATUS="applied"
DB_POST_VALIDATION="$(printf '%s' "$DB_APPLY_OUTPUT" | grep -o '\\\"post_upsert_validation\\\"' >/dev/null && echo ok || echo missing)"
"""


def main() -> int:
    args = parse_args()
    options = RemotePublishOptions(
        upload_id=args.upload_id,
        data_root=args.data_root,
        remote_app_root=args.remote_app_root,
        db_container=args.db_container,
        container_data_root=args.container_data_root,
        apply_db_upsert=args.apply_db_upsert,
        restart_container=args.restart_container,
        smoke_base_url=args.smoke_base_url.rstrip("/"),
    )
    script = build_remote_publish_script(options)
    if args.dry_run:
        print(script)
        return 0
    target = f"{args.ssh_user}@{args.host}"
    completed = subprocess.run(
        ["ssh", target, "bash", "-s"],
        input=script.encode("utf-8"),
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
