from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import re
from typing import Any

from sqlalchemy import JSON, MetaData, String, Text, create_engine, select, update

from item_text_normalization import FRENCH_ITEM_TEXT_CORRECTIONS


REPO_ROOT = Path(__file__).resolve().parents[2]
PATH_FIELD_RE = re.compile(r"(?:asset|file|path|storage|url|uri|key)", re.IGNORECASE)
PATH_VALUE_RE = re.compile(r"[\\/]|^[a-z][a-z0-9+.-]*://", re.IGNORECASE)
JSON_SUFFIXES = {".json"}
SKIPPED_GENERATED_PARTS = {".mfa_cache", "mfa_corpus", "mfa_output"}


class FrenchItemMigrationError(RuntimeError):
    """Raised when the narrowly scoped item migration cannot run safely."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or apply the exact French item correction in research DB rows and runtime JSON."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Report changes without writing (default).")
    mode.add_argument("--apply", action="store_true", help="Apply the reported exact replacements transactionally.")
    parser.add_argument(
        "--data-root",
        help="PROMAT data root containing sessions/, config/, and optional current/. Defaults to $PROMAT_RUNTIME_ROOT/data or repo data/.",
    )
    parser.add_argument(
        "--extra-root",
        action="append",
        default=[],
        help="Additional file tree to scan, for example a local exports/ directory. May be repeated.",
    )
    parser.add_argument(
        "--auth-database-url",
        help="Research/auth DB URL. Defaults to AUTH_DATABASE_URL.",
    )
    parser.add_argument("--skip-db", action="store_true", help="Skip database inspection and updates.")
    parser.add_argument("--skip-files", action="store_true", help="Skip runtime/config file inspection and updates.")
    return parser.parse_args()


def _resolved_data_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    runtime_root = (os.getenv("PROMAT_RUNTIME_ROOT") or "").strip()
    if runtime_root:
        return (Path(runtime_root).expanduser() / "data").resolve()
    return (REPO_ROOT / "data").resolve()


def _file_roots(data_root: Path, extra_roots: list[str]) -> list[Path]:
    candidates = [
        data_root / "config" / "research_player" / "french",
        data_root / "sessions" / "french",
        data_root / "current" / "config" / "research_player" / "french",
        data_root / "current" / "sessions" / "french",
        *(Path(value).expanduser().resolve() for value in extra_roots),
    ]
    roots: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if not candidate.exists():
            continue
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        roots.append(candidate)
    return roots


def _replace_text(value: str) -> tuple[str, int]:
    normalized = value
    occurrences = 0
    for source, replacement in FRENCH_ITEM_TEXT_CORRECTIONS.items():
        occurrences += normalized.count(source)
        normalized = normalized.replace(source, replacement)
    return normalized, occurrences


def _json_changes(value: Any, pointer: str = "$") -> tuple[Any, list[dict[str, Any]]]:
    if isinstance(value, str):
        replacement, occurrences = _replace_text(value)
        changes = []
        if occurrences:
            changes.append(
                {
                    "json_path": pointer,
                    "occurrences": occurrences,
                    "asset_or_path_reference": bool(PATH_VALUE_RE.search(value)),
                }
            )
        return replacement, changes
    if isinstance(value, list):
        normalized_items: list[Any] = []
        changes: list[dict[str, Any]] = []
        for index, item in enumerate(value):
            normalized, nested_changes = _json_changes(item, f"{pointer}[{index}]")
            normalized_items.append(normalized)
            changes.extend(nested_changes)
        return normalized_items, changes
    if isinstance(value, dict):
        normalized_object: dict[Any, Any] = {}
        changes: list[dict[str, Any]] = []
        for key, item in value.items():
            normalized_key = key
            if isinstance(key, str):
                normalized_key, key_occurrences = _replace_text(key)
                if key_occurrences:
                    changes.append(
                        {
                            "json_path": f"{pointer}.<key:{key}>",
                            "occurrences": key_occurrences,
                            "asset_or_path_reference": bool(PATH_FIELD_RE.search(key)),
                        }
                    )
            normalized, nested_changes = _json_changes(item, f"{pointer}.{normalized_key}")
            normalized_object[normalized_key] = normalized
            changes.extend(nested_changes)
        return normalized_object, changes
    return value, []


def scan_files(roots: list[Path], *, apply: bool) -> dict[str, Any]:
    file_changes: list[dict[str, Any]] = []
    path_matches: list[str] = []
    scanned_files = 0
    seen_files: set[Path] = set()

    for root in roots:
        for path in sorted(root.rglob("*")):
            if any(part in SKIPPED_GENERATED_PARTS for part in path.parts):
                continue
            relative_display = str(path)
            if any(source in relative_display for source in FRENCH_ITEM_TEXT_CORRECTIONS):
                path_matches.append(relative_display)
            try:
                is_json_file = path.is_file() and path.suffix.lower() in JSON_SUFFIXES
            except OSError:
                continue
            if not is_json_file:
                continue
            resolved = path.resolve()
            if resolved in seen_files:
                continue
            seen_files.add(resolved)
            scanned_files += 1
            text = path.read_text(encoding="utf-8")
            replacement, occurrences = _replace_text(text)
            if not occurrences:
                continue
            try:
                payload = json.loads(text)
                replacement_payload = json.loads(replacement)
            except json.JSONDecodeError as exc:
                raise FrenchItemMigrationError(f"Cannot safely migrate invalid JSON {path}: {exc}") from exc
            normalized_payload, locations = _json_changes(payload)
            if normalized_payload != replacement_payload:
                raise FrenchItemMigrationError(f"JSON replacement verification failed for {path}")
            file_changes.append(
                {
                    "path": str(path),
                    "occurrences": occurrences,
                    "locations": locations,
                    "asset_or_path_reference": any(change["asset_or_path_reference"] for change in locations),
                }
            )

    asset_path_changes_required = bool(path_matches) or any(
        change["asset_or_path_reference"] for change in file_changes
    )
    if apply and asset_path_changes_required:
        raise FrenchItemMigrationError(
            "Asset/file path references contain the noncanonical value; no automatic rename was attempted. "
            "Keep stable technical IDs or stage a copy-and-reference migration before applying."
        )
    if apply:
        for change in file_changes:
            path = Path(change["path"])
            text = path.read_text(encoding="utf-8")
            replacement, _ = _replace_text(text)
            temporary = path.with_name(f".{path.name}.theatre-migration.tmp")
            temporary.write_text(replacement, encoding="utf-8", newline="")
            os.replace(temporary, path)

    return {
        "status": "applied" if apply else "dry-run",
        "roots": [str(root) for root in roots],
        "scanned_json_files": scanned_files,
        "affected_files": len(file_changes),
        "affected_occurrences": sum(change["occurrences"] for change in file_changes),
        "changes": file_changes,
        "path_name_matches": path_matches,
        "asset_path_changes_required": asset_path_changes_required,
        "asset_strategy": (
            "No asset/path migration is needed. Stable item IDs and MP3 asset keys remain unchanged."
            if not asset_path_changes_required
            else "Do not delete assets. Keep technical IDs where possible; otherwise copy to the new key, update all references, verify, then retire the old key separately."
        ),
    }


def _is_scannable_column(column: Any) -> bool:
    return isinstance(column.type, (String, Text, JSON))


def _row_identifier(row: dict[str, Any], primary_keys: list[str]) -> dict[str, Any]:
    return {key: row[key] for key in primary_keys}


def scan_database(database_url: str, *, apply: bool) -> dict[str, Any]:
    engine = create_engine(database_url, future=True)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    tables = [table for name, table in sorted(metadata.tables.items()) if name.startswith("research_")]
    changes: list[dict[str, Any]] = []
    affected_rows_by_table: dict[str, set[str]] = defaultdict(set)

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            for table in tables:
                primary_keys = [column.name for column in table.primary_key.columns]
                columns = [column for column in table.columns if _is_scannable_column(column)]
                if not primary_keys or not columns:
                    continue
                selected_names = list(dict.fromkeys([*primary_keys, *(column.name for column in columns)]))
                for row_proxy in connection.execute(select(*(table.c[name] for name in selected_names))):
                    row = dict(row_proxy._mapping)
                    row_id = _row_identifier(row, primary_keys)
                    updates: dict[str, Any] = {}
                    for column in columns:
                        value = row[column.name]
                        if isinstance(value, str):
                            replacement, occurrences = _replace_text(value)
                            locations = []
                            if occurrences:
                                locations = [
                                    {
                                        "json_path": None,
                                        "occurrences": occurrences,
                                        "asset_or_path_reference": bool(
                                            PATH_FIELD_RE.search(column.name) or PATH_VALUE_RE.search(value)
                                        ),
                                    }
                                ]
                        elif isinstance(value, (dict, list)):
                            replacement, locations = _json_changes(value)
                            occurrences = sum(location["occurrences"] for location in locations)
                        else:
                            continue
                        if not occurrences:
                            continue
                        asset_reference = any(location["asset_or_path_reference"] for location in locations)
                        changes.append(
                            {
                                "table": table.name,
                                "column": column.name,
                                "id": row_id,
                                "occurrences": occurrences,
                                "locations": locations,
                                "asset_or_path_reference": asset_reference,
                            }
                        )
                        affected_rows_by_table[table.name].add(json.dumps(row_id, sort_keys=True, default=str))
                        if apply and asset_reference:
                            raise FrenchItemMigrationError(
                                f"Refusing to rewrite asset/path-like DB value in {table.name}.{column.name} {row_id}; "
                                "stage a copy-and-reference migration first."
                            )
                        updates[column.name] = replacement
                    if apply and updates:
                        predicate = None
                        for key in primary_keys:
                            clause = table.c[key] == row[key]
                            predicate = clause if predicate is None else predicate & clause
                        connection.execute(update(table).where(predicate).values(**updates))
            if apply:
                transaction.commit()
            else:
                transaction.rollback()
        except Exception:
            transaction.rollback()
            raise
        finally:
            engine.dispose()

    affected_tables = {
        table: {
            "affected_rows": len(row_ids),
            "affected_ids": [json.loads(row_id) for row_id in sorted(row_ids)],
        }
        for table, row_ids in sorted(affected_rows_by_table.items())
    }
    return {
        "status": "applied" if apply else "dry-run",
        "scanned_tables": [table.name for table in tables],
        "affected_tables": affected_tables,
        "affected_table_count": len(affected_tables),
        "affected_rows": sum(entry["affected_rows"] for entry in affected_tables.values()),
        "affected_cells": len(changes),
        "affected_occurrences": sum(change["occurrences"] for change in changes),
        "changes": changes,
        "asset_path_changes_required": any(change["asset_or_path_reference"] for change in changes),
    }


def run_migration(
    *,
    data_root: Path,
    extra_roots: list[str],
    database_url: str | None,
    apply: bool,
    skip_db: bool,
    skip_files: bool,
) -> dict[str, Any]:
    if skip_db and skip_files:
        raise FrenchItemMigrationError("--skip-db and --skip-files cannot be used together")
    report: dict[str, Any] = {
        "migration": "french_item_theatre_circumflex",
        "mode": "apply" if apply else "dry-run",
        "replacement_rule": FRENCH_ITEM_TEXT_CORRECTIONS,
    }
    if skip_files:
        report["files"] = {"status": "skipped"}
    else:
        report["files"] = scan_files(_file_roots(data_root, extra_roots), apply=apply)

    if skip_db:
        report["database"] = {"status": "skipped"}
    elif not database_url:
        report["database"] = {
            "status": "unavailable",
            "reason": "AUTH_DATABASE_URL or --auth-database-url is required",
        }
    else:
        report["database"] = scan_database(database_url, apply=apply)

    file_report = report["files"]
    database_report = report["database"]
    report["summary"] = {
        "affected_tables": database_report.get("affected_table_count", 0),
        "affected_db_rows": database_report.get("affected_rows", 0),
        "affected_files": file_report.get("affected_files", 0),
        "affected_occurrences": (
            database_report.get("affected_occurrences", 0) + file_report.get("affected_occurrences", 0)
        ),
        "asset_path_changes_required": bool(
            database_report.get("asset_path_changes_required", False)
            or file_report.get("asset_path_changes_required", False)
        ),
    }
    return report


def main() -> int:
    args = parse_args()
    try:
        report = run_migration(
            data_root=_resolved_data_root(args.data_root),
            extra_roots=args.extra_root,
            database_url=(args.auth_database_url or os.getenv("AUTH_DATABASE_URL") or "").strip() or None,
            apply=args.apply,
            skip_db=args.skip_db,
            skip_files=args.skip_files,
        )
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
