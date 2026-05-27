from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from intake_batch_common import (  # noqa: E402
    resolve_batch_dir,
    working_text_manifest_path,
    working_text_mfa_corpus_dir,
    working_text_mfa_output_dir,
    working_text_mfa_state_path,
)
from language_config import resolve_language_config  # noqa: E402


DEFAULT_DOCKER_IMAGE = "mmcauliffe/montreal-forced-aligner:latest"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Montreal Forced Aligner for one person-scoped text working tree.",
    )
    parser.add_argument("--batch-dir", required=True, help="Batch directory path or batch name under scripts/research_data_intake/import/.")
    parser.add_argument("--person-id", required=True, help="Canonical person_id such as EN-L-0001.")
    parser.add_argument("--language", required=True, help="Intake language code or corpus slug, for example en or english.")
    parser.add_argument("--mfa-executable", default="mfa", help="MFA executable name or absolute path. Default: mfa.")
    parser.add_argument("--dry-run", action="store_true", help="Validate the MFA inputs and command without executing MFA.")
    return parser.parse_args()


def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


def _extract_output(process: subprocess.CompletedProcess[str]) -> str:
    return (process.stdout or "").strip() or (process.stderr or "").strip()


def _load_json_object(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return None


def _docker_cache_dir(batch_dir: Path, person_id: str, cache_key: str) -> Path:
    cache_dir = batch_dir / ".mfa_cache" / person_id / cache_key
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _manifest_cache_key(manifest_path: Path) -> str:
    return hashlib.sha256(manifest_path.read_bytes()).hexdigest()[:16]


def _docker_volume(path: Path, container_path: str) -> str:
    return f"{path.resolve()}:{container_path}"


def _docker_image() -> str:
    return os.getenv("PROMAT_MFA_DOCKER_IMAGE", DEFAULT_DOCKER_IMAGE)


def check_mfa_available(mfa_executable: str = "mfa") -> str:
    if mfa_executable == "docker":
        process = _run_command(["docker", "--version"])
        output = _extract_output(process)
        if process.returncode != 0:
            raise RuntimeError(f"Docker is not available for MFA container execution: {output or 'no output'}")
        return output.splitlines()[0] if output else "unknown"
    process = _run_command([mfa_executable, "version"])
    output = _extract_output(process)
    if process.returncode != 0:
        raise RuntimeError(f"MFA CLI is not available through {mfa_executable!r}: {output or 'no output'}")
    return output.splitlines()[0] if output else "unknown"


def run_text_mfa_for_person(
    *,
    batch_dir: Path,
    person_id: str,
    language: str,
    mfa_executable: str = "mfa",
    dry_run: bool = False,
) -> dict[str, object]:
    normalized_person_id = person_id.strip().upper()
    config = resolve_language_config(language)
    mfa_corpus_dir = working_text_mfa_corpus_dir(batch_dir, normalized_person_id)
    mfa_output_dir = working_text_mfa_output_dir(batch_dir, normalized_person_id)
    manifest_path = working_text_manifest_path(batch_dir, normalized_person_id)

    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing text MFA manifest for {normalized_person_id}: {manifest_path}")
    if not mfa_corpus_dir.exists() or not any(mfa_corpus_dir.iterdir()):
        raise FileNotFoundError(f"Missing or empty text MFA corpus for {normalized_person_id}: {mfa_corpus_dir}")
    mfa_output_dir.mkdir(parents=True, exist_ok=True)

    version = check_mfa_available(mfa_executable)
    cache_key = _manifest_cache_key(manifest_path)
    if mfa_executable == "docker":
        docker_image = _docker_image()
        cache_dir = _docker_cache_dir(batch_dir, normalized_person_id, cache_key)
        docker_shell_command = " && ".join(
            [
                f"mfa model download acoustic {config.mfa_acoustic_model}",
                f"mfa model download dictionary {config.mfa_dictionary_model}",
                "mfa align --clean --single_speaker --num_jobs 1 /data/corpus "
                f"{config.mfa_dictionary_model} {config.mfa_acoustic_model} /data/output",
            ]
        )
        command = [
            "docker",
            "run",
            "--rm",
            "-e",
            "MFA_ROOT_DIR=/mfa",
            "-v",
            _docker_volume(mfa_corpus_dir, "/data/corpus"),
            "-v",
            _docker_volume(mfa_output_dir, "/data/output"),
            "-v",
            _docker_volume(cache_dir, "/mfa"),
            docker_image,
            "bash",
            "-lc",
            docker_shell_command,
        ]
    else:
        command = [
            mfa_executable,
            "align",
            "--clean",
            "--single_speaker",
            "--num_jobs",
            "1",
            str(mfa_corpus_dir),
            config.mfa_dictionary_model,
            config.mfa_acoustic_model,
            str(mfa_output_dir),
        ]
    if dry_run:
        return {
            "person_id": normalized_person_id,
            "language_code": config.code,
            "language_slug": config.corpus_slug,
            "mfa_executable": mfa_executable,
            "mfa_version": version,
            "command": command,
            "mode": "dry-run",
        }

    process = _run_command(command)
    output = _extract_output(process)
    if process.returncode != 0:
        raise RuntimeError(
            f"MFA alignment failed for {normalized_person_id}: {output or 'no output'}"
        )
    state_path = working_text_mfa_state_path(batch_dir, normalized_person_id)
    manifest_payload = _load_json_object(manifest_path) or {}
    state_payload = {
        "person_id": normalized_person_id,
        "language_code": config.code,
        "language_slug": config.corpus_slug,
        "language": config.corpus_slug,
        "mfa_executable": mfa_executable,
        "mfa_version": version,
        "cache_key": cache_key,
        "state_version": "2026-05-27-text-mfa-run-v1",
        "manifest_path": str(manifest_path.relative_to(batch_dir)).replace("\\", "/"),
        "mfa_output_dir": str(mfa_output_dir.relative_to(batch_dir)).replace("\\", "/"),
        "preparation_version": manifest_payload.get("preparation_version"),
        "source_signatures": manifest_payload.get("source_signatures"),
    }
    state_path.write_text(json.dumps(state_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "person_id": normalized_person_id,
        "language_code": config.code,
        "language_slug": config.corpus_slug,
        "mfa_executable": mfa_executable,
        "mfa_version": version,
        "cache_key": cache_key,
        "command": command,
        "mode": "write",
        "output": output,
    }


def _run() -> int:
    args = parse_args()
    batch_dir = resolve_batch_dir(args.batch_dir, require_processed=False)
    result = run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id=args.person_id,
        language=args.language,
        mfa_executable=args.mfa_executable,
        dry_run=args.dry_run,
    )
    print(f"person_id={result['person_id']}")
    print(f"language={result['language_code']} ({result['language_slug']})")
    print(f"mfa_executable={result['mfa_executable']}")
    print(f"mfa_version={result['mfa_version']}")
    print(f"mode={result['mode']}")
    return 0


def main() -> int:
    try:
        return _run()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
