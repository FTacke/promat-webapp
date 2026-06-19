from __future__ import annotations

import json
from pathlib import Path
import sys

from sqlalchemy import JSON, Column, MetaData, String, Table, Text, create_engine, insert, select


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

import migrate_french_theatre_item as migration  # noqa: E402
from intake_storage import validate_prod_package  # noqa: E402


def _database_url(tmp_path: Path) -> str:
    return f"sqlite+pysqlite:///{(tmp_path / 'research.sqlite').as_posix()}"


def test_runtime_french_item_catalog_and_exports_use_canonical_value() -> None:
    catalog_path = TEST_REPO_ROOT / "data" / "config" / "research_player" / "french" / "task_catalogs" / "wordlist.json"
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    item = next(item for item in payload["items"] if item["item_id"] == "wl_014")

    assert item["text"] == "théâtre"
    for alignment_path in (TEST_REPO_ROOT / "data" / "sessions" / "french").glob("*/alignment/wordlist.json"):
        assert "théatre" not in alignment_path.read_text(encoding="utf-8")


def test_file_migration_dry_run_apply_and_idempotence(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    alignment_path = data_root / "sessions" / "french" / "FR-L-0001-2026-S01" / "alignment" / "wordlist.json"
    alignment_path.parent.mkdir(parents=True)
    alignment_path.write_text(
        json.dumps(
            {
                "items": [{"item_id": "wl_014", "text": "théatre", "split_mp3": "items/wordlist/wl_014.mp3"}]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    dry_run = migration.run_migration(
        data_root=data_root,
        extra_roots=[],
        database_url=None,
        apply=False,
        skip_db=True,
        skip_files=False,
    )
    assert dry_run["summary"]["affected_files"] == 1
    assert dry_run["summary"]["asset_path_changes_required"] is False
    assert "théatre" in alignment_path.read_text(encoding="utf-8")

    applied = migration.run_migration(
        data_root=data_root,
        extra_roots=[],
        database_url=None,
        apply=True,
        skip_db=True,
        skip_files=False,
    )
    payload = json.loads(alignment_path.read_text(encoding="utf-8"))
    assert applied["summary"]["affected_files"] == 1
    assert payload["items"][0]["text"] == "théâtre"
    assert payload["items"][0]["item_id"] == "wl_014"
    assert payload["items"][0]["split_mp3"] == "items/wordlist/wl_014.mp3"

    repeated = migration.run_migration(
        data_root=data_root,
        extra_roots=[],
        database_url=None,
        apply=True,
        skip_db=True,
        skip_files=False,
    )
    assert repeated["summary"]["affected_files"] == 0


def test_database_migration_dry_run_apply_and_idempotence(tmp_path: Path) -> None:
    database_url = _database_url(tmp_path)
    engine = create_engine(database_url, future=True)
    metadata = MetaData()
    cache = Table(
        "research_item_cache",
        metadata,
        Column("cache_id", String(32), primary_key=True),
        Column("label", Text),
        Column("payload", JSON),
    )
    unrelated = Table(
        "users",
        metadata,
        Column("user_id", String(32), primary_key=True),
        Column("note", Text),
    )
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            insert(cache),
            [
                {"cache_id": "fr-wl-014", "label": "théatre", "payload": {"display_text": "théatre"}},
                {"cache_id": "en-theatre", "label": "theatre", "payload": {"display_text": "theatre"}},
            ],
        )
        connection.execute(insert(unrelated), [{"user_id": "u1", "note": "théatre"}])

    dry_run = migration.scan_database(database_url, apply=False)
    assert dry_run["affected_tables"]["research_item_cache"]["affected_rows"] == 1
    with engine.connect() as connection:
        row = connection.execute(select(cache).where(cache.c.cache_id == "fr-wl-014")).one()
        assert row.label == "théatre"

    applied = migration.scan_database(database_url, apply=True)
    assert applied["affected_rows"] == 1
    with engine.connect() as connection:
        rows = {row.cache_id: row for row in connection.execute(select(cache))}
        unrelated_row = connection.execute(select(unrelated)).one()
        assert rows["fr-wl-014"].label == "théâtre"
        assert rows["fr-wl-014"].payload["display_text"] == "théâtre"
        assert rows["en-theatre"].label == "theatre"
        assert rows["en-theatre"].payload["display_text"] == "theatre"
        assert unrelated_row.note == "théatre"

    repeated = migration.scan_database(database_url, apply=True)
    assert repeated["affected_rows"] == 0
    engine.dispose()


def test_prod_package_validation_rejects_noncanonical_french_item(tmp_path: Path) -> None:
    package_dir = tmp_path / "package"
    bad_json = package_dir / "sessions" / "french" / "FR-L-0001-2026-S01" / "alignment" / "wordlist.json"
    bad_json.parent.mkdir(parents=True)
    bad_json.write_text('{"text":"théatre"}', encoding="utf-8")

    errors = validate_prod_package(package_dir)

    assert any("noncanonical French item text" in error for error in errors)
