"""Focused CI governance guards for known PROMAT regression axes."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import os
from pathlib import Path
import re


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

# start.txt is intentionally tracked at the repo root as an operator convenience entrypoint.
ROOT_TEMP_ALLOWED_FILES = frozenset({"start.txt"})


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


# Machine-dependent absolute paths must not return to active code or active configuration: storage roots are
# configured (docs/spec/platform-data-files.md, "Storage Roots"), never spelled out. Documentation, tests and
# gitignored data trees are out of scope. Container and server paths of the deployment contract (/app, /srv, /usr)
# are not machine paths and are not matched. A justified literal carries the marker below on the same line.
MACHINE_PATH_ROOTS = (
    "app/src",
    "app/scripts",
    "scripts",
    "infra",
    ".github/workflows",
    ".vscode",
    "docker-compose.dev-postgres.yml",
    "app/.env.example",
    ".env.example",
)
MACHINE_PATH_SKIP_PREFIXES = (
    "scripts/research_data_intake/import/",
    "scripts/research_data_intake/exports/",
    "scripts/research_data_intake/.mfa_cache/",
)
MACHINE_PATH_SKIP_SUFFIXES = SKIP_SUFFIXES | {".md", ".woff2", ".ttf", ".pdf", ".xlsx", ".zip"}
MACHINE_PATH_ESCAPE = "path-literal:"
MACHINE_PATH_PATTERNS = (
    ("drive path", re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]+(?=[A-Za-z0-9_.<$%])")),
    ("UNC share", re.compile(r"(?<![\\\w?:])\\\\[A-Za-z0-9][\w.-]*\\+[\w$.-]+")),
    ("home directory", re.compile(r"(?<![\w.])/(?:home|Users)/[A-Za-z0-9_.-]+/")),
    ("local archive directory name", re.compile("promat_data" + "_archive")),
)


def _machine_path_hits(text: str) -> list[str]:
    return [label for label, pattern in MACHINE_PATH_PATTERNS if pattern.search(text)]


def _python_string_literals(source: str) -> list[tuple[int, int, str]] | None:
    """(first line, last line, value) of every string literal that is code, not a docstring-like statement."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    prose = {
        id(node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
    }
    return [
        (node.lineno, node.end_lineno or node.lineno, node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in prose
    ]


def machine_path_findings_in_file(path: Path) -> list[tuple[int, str]]:
    """(line, kind) for every machine-dependent path literal in one file."""
    text = read_text(path)
    if not text:
        return []
    lines = text.splitlines()
    findings: list[tuple[int, str]] = []
    literals = _python_string_literals(text) if path.suffix == ".py" else None
    if literals is not None:
        for first, last, value in literals:
            if any(MACHINE_PATH_ESCAPE in line for line in lines[first - 1 : last]):
                continue
            findings.extend((first, label) for label in _machine_path_hits(value))
        return sorted(set(findings))
    for index, line in enumerate(lines, start=1):
        if line.lstrip().startswith(("#", "//")) or MACHINE_PATH_ESCAPE in line:
            continue
        findings.extend((index, label) for label in _machine_path_hits(line))
    return findings


def run_machine_path_guard() -> list[str]:
    findings: list[str] = []
    for relative_root in MACHINE_PATH_ROOTS:
        root = REPO_ROOT / relative_root
        if not root.exists():
            continue
        for path in _machine_path_scope_files(root):
            relative = path.relative_to(REPO_ROOT).as_posix()
            findings.extend(f"{relative}:{line}: {label}" for line, label in machine_path_findings_in_file(path))
    return findings


def _machine_path_scope_files(root: Path):
    """Files below ``root`` without ever entering the gitignored data trees (large, and partly unreadable)."""
    if root.is_file():
        yield root
        return
    for current, dirnames, filenames in os.walk(root):
        current_relative = Path(current).relative_to(REPO_ROOT).as_posix() + "/"
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in SKIP_DIRS and not (current_relative + name + "/").startswith(MACHINE_PATH_SKIP_PREFIXES)
        )
        for name in sorted(filenames):
            if Path(name).suffix.lower() not in MACHINE_PATH_SKIP_SUFFIXES:
                yield Path(current) / name


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
                if path.relative_to(REPO_ROOT).as_posix() in ROOT_TEMP_ALLOWED_FILES:
                    continue
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

    machine_path_findings = run_machine_path_guard()
    if machine_path_findings:
        failures += 1
        print(f"FAIL: machine-dependent absolute paths in active code or configuration (justify with '{MACHINE_PATH_ESCAPE} <reason>')")
        for finding in machine_path_findings:
            print(f"  - {finding}")
    else:
        print("PASS: machine-dependent absolute paths in active code or configuration")

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
