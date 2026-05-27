from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from language_config import describe_language_config, iter_language_configs, supported_language_codes  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check or optionally download the configured MFA acoustic and dictionary models for one or more intake languages.",
    )
    parser.add_argument(
        "--language",
        action="append",
        choices=supported_language_codes(),
        help="Restrict the check or download to one configured intake language code. Repeat for multiple languages.",
    )
    parser.add_argument(
        "--download-models",
        action="store_true",
        help="Opt in to actual MFA model downloads. Without this flag the script only checks the MFA CLI and prints the configured models.",
    )
    parser.add_argument(
        "--mfa-executable",
        default="mfa",
        help="MFA executable name or absolute path. Run this from an MFA-enabled shell when using a conda environment.",
    )
    return parser.parse_args()


def _selected_configs(args: argparse.Namespace) -> list[object]:
    return iter_language_configs(args.language)


def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


def _extract_output(process: subprocess.CompletedProcess[str]) -> str:
    combined = (process.stdout or "").strip() or (process.stderr or "").strip()
    return combined


def _check_mfa(executable: str) -> str:
    process = _run_command([executable, "version"])
    output = _extract_output(process)
    if process.returncode != 0:
        raise RuntimeError(f"MFA CLI is not available through {executable!r}: {output or 'no output'}")
    return output.splitlines()[0] if output else "unknown"


def _download_model(executable: str, model_type: str, model_name: str) -> None:
    process = _run_command([executable, "model", "download", model_type, model_name])
    output = _extract_output(process)
    if process.returncode != 0:
        raise RuntimeError(f"MFA model download failed for {model_type}/{model_name}: {output or 'no output'}")
    if output:
        print(output)


def _run() -> int:
    args = parse_args()
    configs = _selected_configs(args)
    version = _check_mfa(args.mfa_executable)

    print("[mfa-model-plan]")
    print(f"mfa_executable={args.mfa_executable}")
    print(f"mfa_version={version}")
    print(f"mode={'download' if args.download_models else 'check-only'}")
    for config in configs:
        print(f"language={describe_language_config(config)}")

    if not args.download_models:
        return 0

    for config in configs:
        print(f"download acoustic {config.mfa_acoustic_model}")
        _download_model(args.mfa_executable, "acoustic", config.mfa_acoustic_model)
        print(f"download dictionary {config.mfa_dictionary_model}")
        _download_model(args.mfa_executable, "dictionary", config.mfa_dictionary_model)
    return 0


def main() -> int:
    try:
        return _run()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())