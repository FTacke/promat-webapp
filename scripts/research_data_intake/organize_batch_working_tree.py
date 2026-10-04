"""Incremental batch-local working-tree organizer for research intake.

Turns a drop-in batch (``scripts/research_data_intake/import/<name_batch>/``) into the canonical
batch-local ``working/{person_id}/{task}/`` tree that the central importer consumes.

Provenance note
---------------
This module lives in the canonical, versioned source location next to ``import_batch_to_production.py``.
An earlier, never-committed copy used to live in the gitignored ``import/`` drop-in directory, which made
the intake irreproducible from a fresh checkout. This version was reconstructed from the behaviour pinned
down by ``app/tests/test_research_working_tree_intake.py``, the intake runbook, the scanner helpers in
``intake_batch_common.py`` and the historical run logs under ``docs/agent-runs/``. Status names that the
tests do not pin (``missing_*``, ``conflict_*`` other than the two covered ones) follow the same naming
scheme. Operators who still hold the original local file should diff it against this one once and then
delete the local copy; see ``docs/runbooks/research-intake-working-pipeline.md``.

Behaviour
---------
* Works per ``person_id`` and task (``wordlist``, ``text``, ``interview``) and records what it built in the
  batch-local ``working/.intake_state.json`` (input snapshots ``size + mtime_ns``).
* A task whose selected inputs are unchanged and whose expected outputs exist is ``unchanged`` and is not
  touched at all (including MFA artefacts below ``working/{person}/text/``).
* A changed or newly complete task is rebuilt by replacing only ``working/{person}/{task}/``.
* Interview JSON is derived from the Amberscript export; material references are resolved against the
  canonical task catalogs. Transformation errors are reported per task and never abort the batch and never
  destroy a previously good task tree.
* Ambiguous or competing candidates are hard conflicts; nothing is guessed.
* ``interview`` is neutral (``not_expected_for_native_speaker``) for ``-N-`` person ids.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import shutil
import sys
from typing import Any


SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from alignment_export.import_interview_amberscript import (  # noqa: E402
    InterviewImportError,
    build_interview_alignment_payload,
    write_interview_alignment_json,
)
from intake_batch_common import (  # noqa: E402
    SUPPORTED_TASKS,
    SUPPORTED_TRANSFER_MODES,
    BatchTaskCandidates,
    ParsedBatchFile,
    build_batch_inventory,
    choose_unique_candidate,
    empty_batch_task_candidates,
    files_match,
    is_native_speaker_person_id,
    resolve_batch_dir,
    scan_import_batch,
    transfer_file,
    working_alignment_json_path,
    working_alignment_path,
    working_intake_state_path,
    working_source_path,
    working_task_root,
)


STATE_VERSION = 1

STATUS_UNCHANGED = "unchanged"
STATUS_REBUILT = "rebuilt"
STATUS_PLANNED_REBUILD = "planned_rebuild"
STATUS_NATIVE_INTERVIEW = "not_expected_for_native_speaker"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _posix_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _input_snapshot(entry: ParsedBatchFile) -> dict[str, object]:
    stat_result = entry.source_path.stat()
    return {
        "path": entry.relative_source,
        "size": stat_result.st_size,
        "mtime_ns": stat_result.st_mtime_ns,
        "hash": None,
        "source_root": entry.source_root,
        "stage": entry.stage,
        "file_kind": entry.file_kind,
    }


class _Selection:
    """Resolved inputs (or the reason there are none) for one person/task."""

    def __init__(self, person_id: str, task: str) -> None:
        self.person_id = person_id
        self.task = task
        self.status: str | None = None
        self.message: str | None = None
        self.source_wav: ParsedBatchFile | None = None
        self.alignment_input: ParsedBatchFile | None = None
        self.raw_wav_used_as_source = False

    @property
    def alignment_key(self) -> str:
        return "source_json" if self.task == "interview" else "alignment_textgrid"

    def selected_inputs(self) -> dict[str, dict[str, object]]:
        inputs: dict[str, dict[str, object]] = {}
        if self.source_wav is not None:
            inputs["source_wav"] = _input_snapshot(self.source_wav)
        if self.alignment_input is not None:
            inputs[self.alignment_key] = _input_snapshot(self.alignment_input)
        return inputs


def _select_wav(
    candidates: BatchTaskCandidates,
    selection: _Selection,
) -> tuple[ParsedBatchFile | None, str | None]:
    """Prefer the processed (``source``) WAV, fall back to a unique raw WAV. ``origin`` is never a fallback."""
    if candidates.source_wav:
        chosen, problem = choose_unique_candidate(
            candidates.source_wav,
            source_label=f"{selection.person_id}/{selection.task}",
            selection_label="processed wav",
        )
        if chosen is None:
            return None, "conflict_multiple_processed_wav_candidates:" + (problem or "")
        return chosen, None
    if candidates.raw_wav:
        chosen, problem = choose_unique_candidate(
            candidates.raw_wav,
            source_label=f"{selection.person_id}/{selection.task}",
            selection_label="raw wav",
        )
        if chosen is None:
            return None, "conflict_multiple_raw_wav_candidates:" + (problem or "")
        selection.raw_wav_used_as_source = True
        return chosen, None
    return None, None


def _select_inputs(person_id: str, task: str, candidates: BatchTaskCandidates) -> _Selection:
    selection = _Selection(person_id, task)

    if task == "interview" and is_native_speaker_person_id(person_id):
        selection.status = STATUS_NATIVE_INTERVIEW
        selection.message = "interview is not expected for native_speaker"
        return selection

    wav, wav_problem = _select_wav(candidates, selection)
    if wav_problem is not None:
        status, _, message = wav_problem.partition(":")
        selection.status = status
        selection.message = message or status
        return selection

    if task == "interview":
        alignment_candidates = candidates.interview_alignment_json
        alignment_label, alignment_kind = "interview json", "json"
    else:
        alignment_candidates = candidates.alignment_textgrid
        alignment_label, alignment_kind = "textgrid", "textgrid"

    alignment, alignment_problem = choose_unique_candidate(
        alignment_candidates,
        source_label=f"{person_id}/{task}",
        selection_label=alignment_label,
    )
    if alignment is None and alignment_problem is not None:
        selection.status = f"conflict_multiple_{alignment_kind}_candidates"
        selection.message = alignment_problem
        return selection

    if wav is None and alignment is None:
        selection.status = f"missing_wav_and_{alignment_kind}"
        selection.message = f"no wav and no {alignment_kind} found for {person_id}/{task}"
        return selection
    if wav is None:
        selection.status = "missing_wav"
        selection.message = f"no wav found for {person_id}/{task}"
        return selection
    if alignment is None:
        selection.status = f"missing_{alignment_kind}"
        selection.message = f"no {alignment_kind} found for {person_id}/{task}"
        return selection

    selection.source_wav = wav
    selection.alignment_input = alignment
    return selection


def _expected_outputs(batch_dir: Path, person_id: str, task: str) -> list[Path]:
    if task == "interview":
        return [
            working_source_path(batch_dir, person_id, task),
            working_alignment_json_path(batch_dir, person_id, task),
        ]
    return [
        working_source_path(batch_dir, person_id, task),
        working_alignment_path(batch_dir, person_id, task),
    ]


def _load_state(batch_dir: Path) -> dict[str, Any]:
    state_path = working_intake_state_path(batch_dir)
    if not state_path.exists():
        return {"version": STATE_VERSION, "batch": batch_dir.as_posix(), "updated_at": None, "persons": {}}
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        payload = None
    if not isinstance(payload, dict) or not isinstance(payload.get("persons"), dict):
        return {"version": STATE_VERSION, "batch": batch_dir.as_posix(), "updated_at": None, "persons": {}}
    return payload


def _write_state(batch_dir: Path, state: dict[str, Any]) -> None:
    state["version"] = STATE_VERSION
    state["batch"] = batch_dir.as_posix()
    state["updated_at"] = _now_iso()
    state_path = working_intake_state_path(batch_dir)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _task_state(state: dict[str, Any], person_id: str, task: str) -> dict[str, Any]:
    persons = state.get("persons")
    if not isinstance(persons, dict):
        return {}
    person_entry = persons.get(person_id)
    if not isinstance(person_entry, dict):
        return {}
    task_entry = person_entry.get(task)
    return task_entry if isinstance(task_entry, dict) else {}


def _state_inputs_match(task_state: dict[str, Any], selected_inputs: dict[str, dict[str, object]]) -> bool:
    recorded = task_state.get("selected_inputs")
    if not isinstance(recorded, dict) or set(recorded) != set(selected_inputs):
        return False
    for key, current in selected_inputs.items():
        previous = recorded.get(key)
        if not isinstance(previous, dict):
            return False
        for field in ("path", "size", "mtime_ns"):
            if previous.get(field) != current.get(field):
                return False
    return True


def _state_outputs_exist(batch_dir: Path, task_state: dict[str, Any]) -> bool:
    outputs = task_state.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        return False
    return all(isinstance(item, str) and _exists(batch_dir / item) for item in outputs)


def _bootstrap_matches_sources(batch_dir: Path, selection: _Selection) -> bool:
    """True when an untracked working tree already holds exactly the selected, copied inputs.

    Interview is never adopted this way because its JSON is derived and cannot be compared to the source.
    """
    if selection.task == "interview" or selection.source_wav is None or selection.alignment_input is None:
        return False
    person_id, task = selection.person_id, selection.task
    wav_target = working_source_path(batch_dir, person_id, task)
    alignment_target = working_alignment_path(batch_dir, person_id, task)
    return files_match(selection.source_wav.source_path, wav_target) and files_match(
        selection.alignment_input.source_path, alignment_target
    )


def _should_rebuild(
    *,
    batch_dir: Path,
    selection: _Selection,
    task_state: dict[str, Any],
    forced: bool,
) -> tuple[bool, str | None]:
    """Return ``(rebuild, adoption_reason)``; ``(False, reason)`` means unchanged."""
    if forced:
        return True, None
    selected_inputs = selection.selected_inputs()
    if task_state and _state_inputs_match(task_state, selected_inputs) and _state_outputs_exist(batch_dir, task_state):
        # The state may predate outputs that are tracked today (for example the interview JSON), so the
        # currently expected outputs must exist too, not only the ones recorded historically.
        current_outputs_missing = any(
            not _exists(path) for path in _expected_outputs(batch_dir, selection.person_id, selection.task)
        )
        if not current_outputs_missing:
            return False, "state_matches"
    if not task_state and _bootstrap_matches_sources(batch_dir, selection):
        return False, "bootstrap_adopted"
    return True, None


def _safe_remove_task_root(batch_dir: Path, task_root: Path) -> None:
    working_root = (batch_dir / "working").resolve()
    resolved = task_root.resolve()
    if resolved == working_root or working_root not in resolved.parents:
        raise ValueError(f"Refusing to remove path outside the batch working tree: {task_root}")
    if task_root.is_symlink() or task_root.is_file():
        task_root.unlink()
    elif task_root.exists():
        shutil.rmtree(task_root)


def _existing_inputs_conflict(batch_dir: Path, selection: _Selection) -> bool:
    """True when a copied input target already exists with different content."""
    assert selection.source_wav is not None and selection.alignment_input is not None
    person_id, task = selection.person_id, selection.task
    targets = [(selection.source_wav.source_path, working_source_path(batch_dir, person_id, task))]
    if task != "interview":
        targets.append((selection.alignment_input.source_path, working_alignment_path(batch_dir, person_id, task)))
    return any(_exists(target) and not files_match(source, target) for source, target in targets)


def _build_task(
    *,
    batch_dir: Path,
    selection: _Selection,
    transfer_mode: str,
    existing_tree_is_owned: bool,
    replace_existing: bool,
) -> tuple[str, str | None, list[str]]:
    """Rebuild one task subtree. Returns ``(status, message, outputs)``."""
    person_id, task = selection.person_id, selection.task
    assert selection.source_wav is not None and selection.alignment_input is not None
    task_root = working_task_root(batch_dir, person_id, task)

    if not existing_tree_is_owned and not replace_existing and _existing_inputs_conflict(batch_dir, selection):
        return (
            "conflict_existing_working_tree",
            f"{task_root.as_posix()} already holds different inputs that this organizer did not build; use --replace-existing",
            [],
        )

    interview_payload: dict[str, object] | None = None
    if task == "interview":
        # Transform first: a failing transform must not destroy a previously good task tree.
        try:
            interview_payload = build_interview_alignment_payload(
                source_json_path=selection.alignment_input.source_path,
                person_id=person_id,
                session_id=None,
            )
        except InterviewImportError as exc:
            return exc.status_code, str(exc), []
        except (OSError, ValueError, KeyError) as exc:
            return "error_interview_transform", f"{type(exc).__name__}: {exc}", []

    _safe_remove_task_root(batch_dir, task_root)
    wav_target = working_source_path(batch_dir, person_id, task)
    transfer_file(selection.source_wav.source_path, wav_target, transfer_mode, dry_run=False)
    outputs = [_posix_relative(wav_target, batch_dir)]

    if task == "interview":
        assert interview_payload is not None
        json_target = working_alignment_json_path(batch_dir, person_id, task)
        write_interview_alignment_json(json_target, interview_payload)
        outputs.append(_posix_relative(json_target, batch_dir))
    else:
        grid_target = working_alignment_path(batch_dir, person_id, task)
        transfer_file(selection.alignment_input.source_path, grid_target, transfer_mode, dry_run=False)
        outputs.append(_posix_relative(grid_target, batch_dir))
    return STATUS_REBUILT, None, outputs


def organize_batch_working_tree(
    *,
    batch_dir: Path,
    transfer_mode: str = "copy",
    dry_run: bool = False,
    replace_existing: bool = False,
    force_tasks: set[str] | None = None,
    person_ids: set[str] | None = None,
) -> dict[str, object]:
    if transfer_mode not in SUPPORTED_TRANSFER_MODES:
        raise ValueError(f"Unsupported transfer mode: {transfer_mode}")
    forced_tasks = set(force_tasks or set())
    unknown_forced = forced_tasks - set(SUPPORTED_TASKS)
    if unknown_forced:
        raise ValueError(f"Unsupported force-task value(s): {', '.join(sorted(unknown_forced))}")
    batch_dir = Path(batch_dir)
    requested_person_ids = {value.strip().upper() for value in (person_ids or set()) if value.strip()}

    scan_report = scan_import_batch(batch_dir)
    inventory = build_batch_inventory(list(scan_report.parsed_files))
    warnings: list[str] = list(scan_report.warnings)

    if requested_person_ids:
        selected_person_ids = sorted(requested_person_ids)
    else:
        selected_person_ids = sorted(inventory)

    state = _load_state(batch_dir)
    persons_state = state.setdefault("persons", {})
    now = _now_iso()
    task_reports: list[dict[str, object]] = []

    for person_id in selected_person_ids:
        person_inventory = inventory.get(person_id, {})
        person_state = persons_state.setdefault(person_id, {}) if not dry_run else persons_state.get(person_id, {})
        for task in SUPPORTED_TASKS:
            candidates = person_inventory.get(task) or empty_batch_task_candidates()
            selection = _select_inputs(person_id, task, candidates)
            task_state = _task_state(state, person_id, task)
            report: dict[str, object] = {
                "person_id": person_id,
                "task": task,
                "status": selection.status or "",
                "message": selection.message,
                "raw_wav_used_as_source": selection.raw_wav_used_as_source,
                "selected_inputs": selection.selected_inputs(),
                "outputs": [],
            }

            if selection.status is not None:
                if selection.status != STATUS_NATIVE_INTERVIEW:
                    warnings.append(f"{person_id}/{task}: {selection.status}: {selection.message}")
                task_reports.append(report)
                continue

            rebuild, adoption = _should_rebuild(
                batch_dir=batch_dir,
                selection=selection,
                task_state=task_state,
                forced=task in forced_tasks,
            )
            if not rebuild:
                report["status"] = STATUS_UNCHANGED
                report["outputs"] = [
                    _posix_relative(path, batch_dir) for path in _expected_outputs(batch_dir, person_id, task)
                ]
                if not dry_run and adoption == "bootstrap_adopted":
                    person_state[task] = {
                        "selected_inputs": selection.selected_inputs(),
                        "recognized_sources": {},
                        "last_build_status": STATUS_UNCHANGED,
                        "last_build_time": None,
                        "last_evaluated_at": now,
                        "outputs": report["outputs"],
                    }
                elif not dry_run and task_state:
                    task_state["last_evaluated_at"] = now
                task_reports.append(report)
                continue

            if dry_run:
                report["status"] = STATUS_PLANNED_REBUILD
                report["outputs"] = [
                    _posix_relative(path, batch_dir) for path in _expected_outputs(batch_dir, person_id, task)
                ]
                task_reports.append(report)
                continue

            status, message, outputs = _build_task(
                batch_dir=batch_dir,
                selection=selection,
                transfer_mode=transfer_mode,
                existing_tree_is_owned=bool(task_state),
                replace_existing=replace_existing,
            )
            report["status"] = status
            report["message"] = message
            report["outputs"] = outputs
            if status == STATUS_REBUILT:
                person_state[task] = {
                    "selected_inputs": selection.selected_inputs(),
                    "recognized_sources": {},
                    "last_build_status": STATUS_REBUILT,
                    "last_build_time": now,
                    "last_evaluated_at": now,
                    "outputs": outputs,
                }
            else:
                warnings.append(f"{person_id}/{task}: {status}: {message}")
                if task_state:
                    task_state["last_build_status"] = status
                    task_state["last_evaluated_at"] = now
            task_reports.append(report)

    if not dry_run and persons_state:
        _write_state(batch_dir, state)

    def _count(predicate: Any) -> int:
        return sum(1 for entry in task_reports if predicate(str(entry["status"])))

    summary = {
        "persons": len(selected_person_ids),
        "tasks": len(task_reports),
        "rebuilt": _count(lambda status: status == STATUS_REBUILT),
        "planned_rebuild": _count(lambda status: status == STATUS_PLANNED_REBUILD),
        "unchanged": _count(lambda status: status == STATUS_UNCHANGED),
        "missing": _count(lambda status: status.startswith("missing_")),
        "conflicts": _count(lambda status: status.startswith("conflict_")),
        "errors": _count(lambda status: status.startswith("error_")),
        "not_expected": _count(lambda status: status == STATUS_NATIVE_INTERVIEW),
    }
    return {
        "batch": batch_dir.as_posix(),
        "dry_run": dry_run,
        "transfer_mode": transfer_mode,
        "replace_existing": replace_existing,
        "force_tasks": sorted(forced_tasks),
        "person_ids": selected_person_ids,
        "tasks": task_reports,
        "warnings": warnings,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organize a drop-in intake batch into the incremental batch-local working tree.",
    )
    parser.add_argument("--batch-dir", required=True, help="Batch directory path or batch name under scripts/research_data_intake/import/.")
    parser.add_argument("--dry-run", action="store_true", help="Plan only; do not write the working tree or the intake state.")
    parser.add_argument("--transfer-mode", choices=SUPPORTED_TRANSFER_MODES, default="copy")
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Also replace working task trees that this organizer did not build itself.",
    )
    parser.add_argument(
        "--force-task",
        action="append",
        choices=SUPPORTED_TASKS,
        default=[],
        dest="force_tasks",
        help="Rebuild this task even when its inputs are unchanged. Repeatable.",
    )
    parser.add_argument(
        "--person-id",
        action="append",
        default=[],
        dest="person_ids",
        help="Limit the run to this person_id. Repeatable.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the full report as JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    batch_dir = resolve_batch_dir(args.batch_dir, require_processed=False)
    report = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode=args.transfer_mode,
        dry_run=args.dry_run,
        replace_existing=args.replace_existing,
        force_tasks=set(args.force_tasks),
        person_ids=set(args.person_ids) or None,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[batch] {report['batch']}")
        print(f"[mode] {'dry-run' if args.dry_run else 'write'} transfer={args.transfer_mode} replace_existing={args.replace_existing}")
        print("[tasks]")
        for entry in report["tasks"]:
            suffix = f" ({entry['message']})" if entry["message"] else ""
            print(f"- {entry['person_id']} {entry['task']}: {entry['status']}{suffix}")
        print("[warnings]")
        for warning in report["warnings"] or ["none"]:
            print(f"- {warning}")
        print("[summary] " + " ".join(f"{key}={value}" for key, value in report["summary"].items()))
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
