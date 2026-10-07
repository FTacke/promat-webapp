"""The hard-coded machine path ratchet of scripts/ci_governance_checks.py: empty baseline plus positive controls."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("ci_governance_checks", TEST_REPO_ROOT / "scripts" / "ci_governance_checks.py")
governance = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = governance  # the module's dataclass needs to find its own module
_spec.loader.exec_module(governance)

DRIVE = "C:" + "\\dev\\promat"
SHARE = "\\\\" + "server\\share\\folder"


def _kinds(path: Path) -> list[str]:
    return [label for _line, label in governance.machine_path_findings_in_file(path)]


def test_active_code_and_configuration_contain_no_machine_paths() -> None:
    assert governance.run_machine_path_guard() == []


def test_guard_scope_covers_the_active_trees_and_skips_data_trees() -> None:
    scanned = {
        path.relative_to(TEST_REPO_ROOT).as_posix()
        for root in governance.MACHINE_PATH_ROOTS
        if (TEST_REPO_ROOT / root).exists()
        for path in governance._machine_path_scope_files(TEST_REPO_ROOT / root)
    }
    for expected in (
        "scripts/research_data_intake/intake_storage.py",
        "scripts/storage_inventory.py",
        "app/src/app/runtime_paths.py",
        "app/scripts/dev-start.ps1",
        "infra/docker-compose.prod.yml",
        ".vscode/tasks.json",
        ".env.example",
    ):
        assert expected in scanned, expected
    assert not any(path.startswith(governance.MACHINE_PATH_SKIP_PREFIXES) for path in scanned)
    assert not any(path.endswith(".md") for path in scanned)


def test_python_string_literals_are_flagged(tmp_path: Path) -> None:
    source = tmp_path / "module.py"
    source.write_text(
        "from pathlib import Path\n"
        f"ROOT = Path({DRIVE!r})\n"
        "OTHER = 'D:/projects/backup'\n"
        "SHARE = " + repr(SHARE) + "\n"
        "HOME = '/home/someone/data'\n"
        "NAME = 'promat_data' '_archive'\n",
        encoding="utf-8",
    )
    assert _kinds(source) == ["drive path", "drive path", "UNC share", "home directory", "local archive directory name"]


def test_docstrings_comments_and_marked_literals_are_not_flagged(tmp_path: Path) -> None:
    source = tmp_path / "module.py"
    source.write_text(
        f'"""Usage: python tool.py --root {DRIVE.replace(chr(92), "/")}"""\n'
        f"# historically this lived in {DRIVE.replace(chr(92), '/')}\n"
        "def run():\n"
        '    """Example: K:/Pronunciation_Matters"""\n'
        "    return 1\n"
        "LEGACY = 'K:/Pronunciation_Matters'  # path-literal: fixture for the legacy reader\n",
        encoding="utf-8",
    )
    assert _kinds(source) == []


def test_configured_and_deployment_paths_are_not_machine_paths(tmp_path: Path) -> None:
    source = tmp_path / "module.py"
    source.write_text(
        "A = '${workspaceFolder}/.venv/Scripts/python.exe'\n"
        "B = '$PSScriptRoot/tools'\n"
        "C = '/app/data/sessions'\n"
        "D = '/srv/webapps/promat/data'\n"
        "E = '/usr/sbin/sendmail'\n"
        "F = 'postgresql+psycopg2://user:pw@127.0.0.1:54321/db'\n"
        "G = 'https://example.org/path'\n"
        "H = 'sqlite:///tmp/test.sqlite3'\n"
        "I = '\\\\\\\\?\\\\'\n"
        "J = 'tmp/ui-qa'\n",
        encoding="utf-8",
    )
    assert _kinds(source) == []


def test_configuration_files_are_checked_line_by_line(tmp_path: Path) -> None:
    compose = tmp_path / "compose.yml"
    compose.write_text(
        "services:\n"
        "  db:\n"
        "    image: postgres:15\n"
        "    ports:\n"
        '      - "127.0.0.1:${PORT:-54321}:5432"\n'
        "    volumes:\n"
        "      - ./data/db/postgres_dev:/var/lib/postgresql/data\n"
        "      # - D:/old/location:/data\n"
        "      - D:/backup/location:/data\n",
        encoding="utf-8",
    )
    assert governance.machine_path_findings_in_file(compose) == [(9, "drive path")]

    tasks = tmp_path / "tasks.json"
    tasks.write_text('{"command": "c:/dev/promat/.venv/Scripts/python.exe"}\n', encoding="utf-8")
    assert _kinds(tasks) == ["drive path"]

    script = tmp_path / "capture.ps1"
    script.write_text('$out = "' + DRIVE + '\\tmp"\n$ok = Join-Path $PSScriptRoot "tmp"\n', encoding="utf-8")
    assert governance.machine_path_findings_in_file(script) == [(1, "drive path")]
