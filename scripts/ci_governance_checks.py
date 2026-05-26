"""Focused CI governance guards for known PROMAT regression axes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
}
SKIP_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".mp3",
    ".wav",
    ".sqlite3",
    ".db",
}

ROOT_TEMP_PATTERNS = (
    "inspect_*.py",
    "tmp_*.py",
    "measure_*.py",
    "verify_*.py",
    "capture_*.py",
    "capture_*.ps1",
    "qa_check.py",
    "simple_qa.py",
    "_es_diag.txt",
    "*_screenshot.png",
    "desktop_*.png",
    "mobile_*.png",
    "grid_debug_*.png",
    "screenshot_debug*.png",
    "start.txt",
)


@dataclass(frozen=True)
class Guard:
    name: str
    roots: tuple[str, ...]
    forbidden: tuple[str, ...]


GUARDS = (
    Guard(
        name="forbidden auth refresh frontend paths",
        roots=("app/static", "app/src", "app/templates", "app/tests"),
        forbidden=("/auth/refresh", "initAuthRefresh", "token-refresh"),
    ),
    Guard(
        name="forbidden legacy interaction classes",
        roots=("app/static", "app/src", "app/templates", "app/tests"),
        forbidden=("pm-research-button", "pm-research-inline-action"),
    ),
    Guard(
        name="shell recovery template guard",
        roots=("app/templates",),
        forbidden=("pm-shell-", "pm-topbar", 'class="pm-footer"', "class='pm-footer'"),
    ),
    Guard(
        name="shell recovery css guard",
        roots=(
            "app/static/css/layout.css",
            "app/static/css/20_layout.css",
            "app/static/css/30_components.css",
        ),
        forbidden=(".pm-shell-", ".pm-topbar", ".pm-footer"),
    ),
    Guard(
        name="deleted legacy asset references",
        roots=("app",),
        forbidden=(
            "account_profile.html",
            "account_delete.html",
            "account_profile.js",
            "account_delete.js",
            "account_password.js",
            "admin_dashboard.html",
        ),
    ),
    Guard(
        name="auth and research view local i18n branches",
        roots=("app/templates/auth", "app/src/app/research_views.py"),
        forbidden=("if ui_lang == 'de'", 'if ui_lang == "de"'),
    ),
)


def iter_text_files(root: Path):
    if root.is_file():
        yield root
        return

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        yield path


def read_text(path: Path) -> str:
    data = path.read_bytes()
    if b"\x00" in data:
        return ""
    return data.decode("utf-8", errors="ignore")


def run_guard(guard: Guard) -> list[str]:
    findings: list[str] = []
    seen_paths: set[Path] = set()

    for relative_root in guard.roots:
        root = REPO_ROOT / relative_root
        if not root.exists():
            findings.append(f"missing expected path: {relative_root}")
            continue

        for path in iter_text_files(root):
            if path in seen_paths:
                continue
            seen_paths.add(path)
            text = read_text(path)
            if not text:
                continue

            lines = text.splitlines()
            for needle in guard.forbidden:
                for index, line in enumerate(lines, start=1):
                    if needle in line:
                        findings.append(f"{path.relative_to(REPO_ROOT)}:{index}: {needle}")

    return findings


def run_root_temp_artifact_guard() -> list[str]:
    findings: list[str] = []
    for pattern in ROOT_TEMP_PATTERNS:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if path.is_file():
                findings.append(path.relative_to(REPO_ROOT).as_posix())
    return findings


def main() -> int:
    failures = 0

    root_temp_findings = run_root_temp_artifact_guard()
    if root_temp_findings:
        failures += 1
        print("FAIL: temporary QA/debug files in repo root")
        for finding in root_temp_findings:
            print(f"  - {finding}")
    else:
        print("PASS: temporary QA/debug files in repo root")

    for guard in GUARDS:
        findings = run_guard(guard)
        if findings:
            failures += 1
            print(f"FAIL: {guard.name}")
            for finding in findings:
                print(f"  - {finding}")
        else:
            print(f"PASS: {guard.name}")

    if failures:
        print(f"\nGovernance checks failed: {failures} guard(s) reported findings.")
        return 1

    print("\nAll governance checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())