from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
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
DEFAULT_MFA_EXECUTABLE = "docker"
MFA_EXECUTABLE_ENV = "PROMAT_MFA_EXECUTABLE"
MFA_ROOT_CONTAINER_PATH = "/mfa"
MFA_CORPUS_CONTAINER_PATH = "/data/corpus"
MFA_OUTPUT_CONTAINER_PATH = "/data/output"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Montreal Forced Aligner for one person-scoped text working tree.",
    )
    parser.add_argument("--batch-dir", required=True, help="Batch directory path or batch name under scripts/research_data_intake/import/.")
    parser.add_argument("--person-id", required=True, help="Canonical person_id such as EN-L-0001.")
    parser.add_argument("--language", required=True, help="Intake language code or corpus slug, for example en or english.")
    parser.add_argument("--mfa-executable", help="MFA executable name or absolute path. Default resolution: CLI value, then PROMAT_MFA_EXECUTABLE, then docker.")
    parser.add_argument("--dry-run", action="store_true", help="Validate the MFA inputs and command without executing MFA.")
    return parser.parse_args()


def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


def _extract_output(process: subprocess.CompletedProcess[str]) -> str:
    parts = [part.strip() for part in (process.stdout, process.stderr) if part and part.strip()]
    return "\n".join(parts)


def _load_json_object(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return None


def _manifest_cache_key(manifest_path: Path) -> str:
    return hashlib.sha256(manifest_path.read_bytes()).hexdigest()[:16]


def _docker_volume(path: Path, container_path: str) -> str:
    return f"{path.resolve()}:{container_path}"


def _docker_image() -> str:
    return os.getenv("PROMAT_MFA_DOCKER_IMAGE", DEFAULT_DOCKER_IMAGE)


def shared_mfa_cache_root() -> Path:
    return SCRIPT_ROOT / ".mfa_cache" / "shared"


def shared_mfa_cache_dir(language_code: str) -> Path:
    return shared_mfa_cache_root() / language_code


def _model_file_targets(cache_dir: Path, acoustic_model: str, dictionary_model: str) -> dict[str, Path]:
    return {
        "acoustic": cache_dir / "pretrained_models" / "acoustic" / f"{acoustic_model}.zip",
        "dictionary": cache_dir / "pretrained_models" / "dictionary" / f"{dictionary_model}.dict",
    }


def _missing_model_types(cache_dir: Path, acoustic_model: str, dictionary_model: str) -> list[str]:
    targets = _model_file_targets(cache_dir, acoustic_model, dictionary_model)
    return [model_type for model_type, path in targets.items() if not path.exists()]


def _legacy_model_candidates(batch_dir: Path, model_type: str, filename: str, target_path: Path) -> list[Path]:
    legacy_root = batch_dir / ".mfa_cache"
    if not legacy_root.exists():
        return []
    subdir = "acoustic" if model_type == "acoustic" else "dictionary"
    candidates: list[Path] = []
    for path in sorted(legacy_root.glob(f"*/*/pretrained_models/{subdir}/{filename}")):
        if not path.is_file():
            continue
        try:
            if path.resolve() == target_path.resolve():
                continue
        except FileNotFoundError:
            pass
        candidates.append(path)
    return candidates


def legacy_mfa_model_migration_sources(
    *,
    batch_dir: Path,
    cache_dir: Path,
    acoustic_model: str,
    dictionary_model: str,
) -> dict[str, Path]:
    migration_sources: dict[str, Path] = {}
    targets = _model_file_targets(cache_dir, acoustic_model, dictionary_model)
    filenames = {
        "acoustic": f"{acoustic_model}.zip",
        "dictionary": f"{dictionary_model}.dict",
    }
    for model_type, target_path in targets.items():
        if target_path.exists():
            continue
        candidates = _legacy_model_candidates(batch_dir, model_type, filenames[model_type], target_path)
        if candidates:
            migration_sources[model_type] = candidates[0]
    return migration_sources


def migrate_legacy_mfa_models_to_shared(
    *,
    batch_dir: Path,
    cache_dir: Path,
    acoustic_model: str,
    dictionary_model: str,
) -> list[str]:
    migrated: list[str] = []
    targets = _model_file_targets(cache_dir, acoustic_model, dictionary_model)
    migration_sources = legacy_mfa_model_migration_sources(
        batch_dir=batch_dir,
        cache_dir=cache_dir,
        acoustic_model=acoustic_model,
        dictionary_model=dictionary_model,
    )
    for model_type, source_path in migration_sources.items():
        target_path = targets[model_type]
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        migrated.append(f"{model_type}:{source_path}")
    return migrated


def _docker_base_command(cache_dir: Path) -> list[str]:
    return [
        "docker",
        "run",
        "--rm",
        "-e",
        f"MFA_ROOT_DIR={MFA_ROOT_CONTAINER_PATH}",
        "-v",
        _docker_volume(cache_dir, MFA_ROOT_CONTAINER_PATH),
        _docker_image(),
        "bash",
        "-lc",
    ]


def _docker_ensure_models_command(cache_dir: Path, missing_model_types: list[str], acoustic_model: str, dictionary_model: str) -> list[str] | None:
    if not missing_model_types:
        return None
    downloads: list[str] = []
    if "acoustic" in missing_model_types:
        downloads.append(f"mfa model download acoustic {acoustic_model}")
    if "dictionary" in missing_model_types:
        downloads.append(f"mfa model download dictionary {dictionary_model}")
    return [*_docker_base_command(cache_dir), " && ".join(downloads)]


def _docker_align_command(
    *,
    cache_dir: Path,
    mfa_corpus_dir: Path,
    mfa_output_dir: Path,
    acoustic_model: str,
    dictionary_model: str,
) -> list[str]:
    shell_command = (
        "mfa align --clean --single_speaker --num_jobs 1 "
        f"{MFA_CORPUS_CONTAINER_PATH} {dictionary_model} {acoustic_model} {MFA_OUTPUT_CONTAINER_PATH}"
    )
    command = _docker_base_command(cache_dir)
    image_index = command.index(_docker_image())
    return [
        *command[:image_index],
        "-v",
        _docker_volume(mfa_corpus_dir, MFA_CORPUS_CONTAINER_PATH),
        "-v",
        _docker_volume(mfa_output_dir, MFA_OUTPUT_CONTAINER_PATH),
        *command[image_index:],
        shell_command,
    ]


def resolve_mfa_executable(cli_value: str | None) -> str:
    explicit = (cli_value or "").strip()
    if explicit:
        return explicit
    env_value = (os.getenv(MFA_EXECUTABLE_ENV) or "").strip()
    if env_value:
        return env_value
    return DEFAULT_MFA_EXECUTABLE


def check_mfa_available(mfa_executable: str = "mfa") -> str:
    if mfa_executable == "docker":
        process = _run_command(["docker", "--version"])
        output = _extract_output(process)
        if process.returncode != 0:
            raise RuntimeError(f"Docker-MFA requested but docker is not available/running: {output or 'no output'}")
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
    manifest_cache_key = _manifest_cache_key(manifest_path)
    migrated_models: list[str] = []
    planned_model_migrations: dict[str, str] = {}
    ensure_command: list[str] | None = None
    if mfa_executable == "docker":
        cache_dir = shared_mfa_cache_dir(config.code)
        migration_sources = legacy_mfa_model_migration_sources(
            batch_dir=batch_dir,
            cache_dir=cache_dir,
            acoustic_model=config.mfa_acoustic_model,
            dictionary_model=config.mfa_dictionary_model,
        )
        planned_model_migrations = {model_type: str(path) for model_type, path in migration_sources.items()}
        if not dry_run:
            cache_dir.mkdir(parents=True, exist_ok=True)
            migrated_models = migrate_legacy_mfa_models_to_shared(
                batch_dir=batch_dir,
                cache_dir=cache_dir,
                acoustic_model=config.mfa_acoustic_model,
                dictionary_model=config.mfa_dictionary_model,
            )
        missing_model_types = _missing_model_types(
            cache_dir,
            config.mfa_acoustic_model,
            config.mfa_dictionary_model,
        )
        if dry_run:
            missing_model_types = [
                model_type for model_type in missing_model_types if model_type not in migration_sources
            ]
        ensure_command = _docker_ensure_models_command(
            cache_dir,
            missing_model_types,
            config.mfa_acoustic_model,
            config.mfa_dictionary_model,
        )
        command = _docker_align_command(
            cache_dir=cache_dir,
            mfa_corpus_dir=mfa_corpus_dir,
            mfa_output_dir=mfa_output_dir,
            acoustic_model=config.mfa_acoustic_model,
            dictionary_model=config.mfa_dictionary_model,
        )
    else:
        cache_dir = None
        missing_model_types = []
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
            "model_cache_dir": str(cache_dir) if cache_dir is not None else None,
            "missing_models": missing_model_types,
            "planned_model_migrations": planned_model_migrations,
            "ensure_command": ensure_command,
            "align_command": command,
            "command": command,
            "mode": "dry-run",
        }

    if ensure_command is not None:
        ensure_process = _run_command(ensure_command)
        ensure_output = _extract_output(ensure_process)
        if ensure_process.returncode != 0:
            raise RuntimeError(
                f"MFA model ensure failed for {config.code}: {ensure_output or 'no output'}"
            )

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
        "manifest_cache_key": manifest_cache_key,
        "model_cache_dir": str(cache_dir) if cache_dir is not None else None,
        "model_cache_strategy": "shared_language" if cache_dir is not None else "mfa_default",
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
        "manifest_cache_key": manifest_cache_key,
        "model_cache_dir": str(cache_dir) if cache_dir is not None else None,
        "model_cache_strategy": "shared_language" if cache_dir is not None else "mfa_default",
        "migrated_models": migrated_models,
        "planned_model_migrations": planned_model_migrations,
        "ensure_command": ensure_command,
        "align_command": command,
        "command": command,
        "mode": "write",
        "output": output,
    }


def _run() -> int:
    args = parse_args()
    mfa_executable = resolve_mfa_executable(args.mfa_executable)
    batch_dir = resolve_batch_dir(args.batch_dir, require_processed=False)
    result = run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id=args.person_id,
        language=args.language,
        mfa_executable=mfa_executable,
        dry_run=args.dry_run,
    )
    print(f"person_id={result['person_id']}")
    print(f"language={result['language_code']} ({result['language_slug']})")
    print(f"mfa_executable={result['mfa_executable']}")
    print(f"mfa_version={result['mfa_version']}")
    if result.get("model_cache_dir"):
        print(f"model_cache_dir={result['model_cache_dir']}")
    if result.get("planned_model_migrations"):
        print("planned_model_migrations=" + json.dumps(result["planned_model_migrations"], ensure_ascii=False))
    if result.get("ensure_command") is None:
        print("ensure_command=None")
    else:
        print("ensure_command=" + json.dumps(result["ensure_command"], ensure_ascii=False))
    if result.get("align_command") is not None:
        print("align_command=" + json.dumps(result["align_command"], ensure_ascii=False))
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
