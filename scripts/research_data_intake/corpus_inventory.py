"""Corpus inventory and release manifest of runtime sessions.

Read-only. For each corpus it lists people, sessions, documented tasks and a content hash per session over every
runtime file, plus one hash for the whole corpus. The same command run against a local runtime and against the
production data mount (inside the web container) therefore proves that both hold the identical release.

    python scripts/research_data_intake/corpus_inventory.py --language english --language french --out inv.json
    python scripts/research_data_intake/corpus_inventory.py --language english --compare inv_prod.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from language_config import resolve_language_config  # noqa: E402

SCHEMA_VERSION = 1
TASKS = ("wordlist", "text", "interview")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _session_entry(session_dir: Path) -> dict[str, Any]:
    metadata = json.loads((session_dir / "metadata.json").read_text(encoding="utf-8"))
    files = sorted(path for path in session_dir.rglob("*") if path.is_file())
    content = hashlib.sha256()
    total_bytes = 0
    for path in files:
        relative = path.relative_to(session_dir).as_posix()
        content.update(f"{relative}\0{_sha256_file(path)}\n".encode("utf-8"))
        total_bytes += path.stat().st_size
    documented = [
        str(task.get("task_type"))
        for task in metadata.get("tasks", [])
        if isinstance(task, dict) and task.get("task_type") in TASKS
    ]
    return {
        "session_id": session_dir.name,
        "person_id": metadata.get("person_id"),
        "speaker_type": metadata.get("speaker_type"),
        "tasks": sorted(documented),
        "file_count": len(files),
        "bytes": total_bytes,
        "content_sha256": content.hexdigest(),
    }


def build_inventory(sessions_root: Path, language_values: list[str]) -> dict[str, Any]:
    corpora: dict[str, Any] = {}
    for value in language_values:
        config = resolve_language_config(value)
        corpus_dir = sessions_root / config.corpus_slug
        sessions = [
            _session_entry(path)
            for path in sorted(corpus_dir.iterdir() if corpus_dir.is_dir() else [])
            if path.is_dir() and (path / "metadata.json").is_file()
        ]
        people: dict[str, str | None] = {}
        for entry in sessions:
            people[str(entry["person_id"])] = entry["speaker_type"]
        task_counts = {task: sum(1 for entry in sessions if task in entry["tasks"]) for task in TASKS}
        digest = hashlib.sha256()
        for entry in sessions:
            digest.update(f"{entry['session_id']}\0{entry['content_sha256']}\n".encode("utf-8"))
        corpora[config.corpus_slug] = {
            "language": config.code,
            "person_count": len(people),
            "learner_count": sum(1 for kind in people.values() if kind == "learner"),
            "native_speaker_count": sum(1 for kind in people.values() if kind == "native_speaker"),
            "session_count": len(sessions),
            "sessions_with_task": task_counts,
            "person_ids": sorted(people),
            "sessions": sessions,
            "corpus_sha256": digest.hexdigest(),
        }
    return {"schema_version": SCHEMA_VERSION, "corpora": corpora}


def compare_inventories(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    differences: list[str] = []
    for slug in sorted(set(left["corpora"]) | set(right["corpora"])):
        a = left["corpora"].get(slug)
        b = right["corpora"].get(slug)
        if a is None or b is None:
            differences.append(f"{slug}: present on one side only")
            continue
        sessions_a = {entry["session_id"]: entry["content_sha256"] for entry in a["sessions"]}
        sessions_b = {entry["session_id"]: entry["content_sha256"] for entry in b["sessions"]}
        for session_id in sorted(set(sessions_a) - set(sessions_b)):
            differences.append(f"{slug}: {session_id} only in left")
        for session_id in sorted(set(sessions_b) - set(sessions_a)):
            differences.append(f"{slug}: {session_id} only in right")
        for session_id in sorted(set(sessions_a) & set(sessions_b)):
            if sessions_a[session_id] != sessions_b[session_id]:
                differences.append(f"{slug}: {session_id} content differs")
    return differences


def _resolve_sessions_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    runtime_root = os.environ.get("PROMAT_RUNTIME_ROOT")
    base = Path(runtime_root) if runtime_root else REPO_ROOT
    return base / "data" / "sessions"


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory and content manifest of runtime corpora (read-only).")
    parser.add_argument("--language", action="append", required=True, help="Corpus code or slug (repeatable).")
    parser.add_argument("--sessions-root", help="Runtime sessions root. Default: <PROMAT_RUNTIME_ROOT>/data/sessions.")
    parser.add_argument("--out", help="Write the inventory JSON to this file instead of stdout.")
    parser.add_argument("--compare", help="Compare against another inventory JSON and exit 1 on any difference.")
    args = parser.parse_args()

    inventory = build_inventory(_resolve_sessions_root(args.sessions_root), args.language)
    text = json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
    elif not args.compare:
        sys.stdout.write(text)
    for slug, corpus in inventory["corpora"].items():
        print(
            f"{slug}: persons={corpus['person_count']} (learners={corpus['learner_count']}, "
            f"native={corpus['native_speaker_count']}) sessions={corpus['session_count']} "
            f"tasks={corpus['sessions_with_task']} sha256={corpus['corpus_sha256'][:16]}",
            file=sys.stderr,
        )
    if args.compare:
        other = json.loads(Path(args.compare).read_text(encoding="utf-8"))
        differences = compare_inventories(inventory, other)
        for line in differences:
            print(f"DIFF {line}", file=sys.stderr)
        print("inventories identical" if not differences else f"{len(differences)} differences", file=sys.stderr)
        return 1 if differences else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
