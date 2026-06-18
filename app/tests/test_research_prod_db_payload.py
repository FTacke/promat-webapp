from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

sys.path.insert(0, str(TEST_REPO_ROOT / "app" / "src"))
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

from app.auth.models import Base  # noqa: E402
from app.research_metadata import ResearchPerson, ResearchSession, ResearchSessionExposure  # noqa: E402
import apply_prod_db_payload as db_payload  # noqa: E402


def _database_url(tmp_path: Path) -> str:
    db_path = tmp_path / "auth.sqlite"
    engine = create_engine(f"sqlite+pysqlite:///{db_path.as_posix()}", future=True)
    Base.metadata.create_all(
        engine,
        tables=[ResearchPerson.__table__, ResearchSession.__table__, ResearchSessionExposure.__table__],
    )
    return f"sqlite+pysqlite:///{db_path.as_posix()}"


def _write_runtime_session(
    release_dir: Path,
    *,
    language_slug: str,
    session_id: str,
    tasks: tuple[str, ...],
) -> None:
    session_dir = release_dir / "sessions" / language_slug / session_id
    (session_dir / "alignment").mkdir(parents=True)
    (session_dir / "derived").mkdir(parents=True)
    metadata_tasks = []
    for task in tasks:
        (session_dir / "alignment" / f"{task}.json").write_text("{}", encoding="utf-8")
        (session_dir / "derived" / f"{task}.mp3").write_bytes(b"mp3")
        metadata_tasks.append(
            {
                "task_type": task,
                "alignment_file": f"alignment/{task}.json",
                "derived_file": f"derived/{task}.mp3",
            }
        )
    (session_dir / "metadata.json").write_text(
        json.dumps({"session_id": session_id, "tasks": metadata_tasks}, ensure_ascii=False),
        encoding="utf-8",
    )


def _payload(
    *,
    batch_name: str = "english_batch_20260618",
    person_id: str = "EN-L-0001",
    session_id: str = "EN-L-0001-2026-S01",
    target_language: str = "en",
    corpus_language: str = "english",
    tasks: list[str] | None = None,
) -> dict[str, object]:
    tasks = ["text"] if tasks is None else tasks
    return {
        "batch_name": batch_name,
        "generated_at": "2026-06-18T12:00:00+00:00",
        "persons": [
            {
                "person_id": person_id,
                "speaker_type": "learner",
                "l1": "DE",
                "additional_languages": ["FR", "ES"],
                "research_consent_signed": "yes",
                "teaching_consent_signed": "unknown",
            }
        ],
        "sessions": [
            {
                "session_id": session_id,
                "person_id": person_id,
                "session_ref": "S01",
                "corpus_language": corpus_language,
                "target_language": target_language,
                "recording_year": 2026,
                "recording_date": "2026-06-18",
                "recorded_by": "Research Team",
                "context": "baseline",
                "documented_tasks": tasks,
            }
        ],
        "exposures": [
            {
                "session_id": session_id,
                "country": "United Kingdom",
                "duration_months": 2,
                "type": "stay",
                "exposure_notes": "Short stay.",
            }
        ],
    }


def _write_payload(release_dir: Path, payload: dict[str, object]) -> Path:
    payload_path = release_dir / "db" / "import_payload.json"
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return payload_path


def test_db_payload_dry_run_reports_inserts_without_writing(tmp_path: Path) -> None:
    release_dir = tmp_path / "release"
    _write_runtime_session(release_dir, language_slug="english", session_id="EN-L-0001-2026-S01", tasks=("text",))
    payload_path = _write_payload(release_dir, _payload())
    database_url = _database_url(tmp_path)

    report = db_payload.run_payload_upsert(
        release_dir=release_dir,
        payload_path=payload_path,
        database_url=database_url,
        apply_changes=False,
    )

    assert report["mode"] == "dry_run"
    assert report["tables"]["research_people"]["insert"] == 1
    assert report["tables"]["research_sessions"]["insert"] == 1
    assert report["tables"]["research_session_exposures"]["insert"] == 1

    engine = create_engine(database_url, future=True)
    with engine.connect() as connection:
        assert connection.execute(select(ResearchPerson)).all() == []


def test_db_payload_apply_is_idempotent_and_does_not_duplicate_rows(tmp_path: Path) -> None:
    release_dir = tmp_path / "release"
    _write_runtime_session(release_dir, language_slug="english", session_id="EN-L-0001-2026-S01", tasks=("text",))
    payload_path = _write_payload(release_dir, _payload())
    database_url = _database_url(tmp_path)

    first = db_payload.run_payload_upsert(
        release_dir=release_dir,
        payload_path=payload_path,
        database_url=database_url,
        apply_changes=True,
    )
    second = db_payload.run_payload_upsert(
        release_dir=release_dir,
        payload_path=payload_path,
        database_url=database_url,
        apply_changes=True,
    )

    assert first["tables"]["research_people"]["insert"] == 1
    assert second["tables"]["research_people"]["unchanged"] == 1
    assert second["tables"]["research_sessions"]["unchanged"] == 1
    assert second["tables"]["research_session_exposures"]["unchanged"] == 1

    engine = create_engine(database_url, future=True)
    with engine.connect() as connection:
        assert len(connection.execute(select(ResearchPerson)).all()) == 1
        assert len(connection.execute(select(ResearchSession)).all()) == 1
        assert len(connection.execute(select(ResearchSessionExposure)).all()) == 1


def test_db_payload_keeps_different_languages_and_batches_separate(tmp_path: Path) -> None:
    release_dir = tmp_path / "release"
    _write_runtime_session(release_dir, language_slug="english", session_id="EN-L-0001-2026-S01", tasks=("text",))
    _write_runtime_session(release_dir, language_slug="french", session_id="FR-L-0002-2026-S01", tasks=("wordlist",))
    english_payload = _write_payload(release_dir, _payload())
    database_url = _database_url(tmp_path)

    db_payload.run_payload_upsert(
        release_dir=release_dir,
        payload_path=english_payload,
        database_url=database_url,
        apply_changes=True,
    )
    french_payload = _write_payload(
        release_dir,
        _payload(
            batch_name="french_batch_20260527",
            person_id="FR-L-0002",
            session_id="FR-L-0002-2026-S01",
            target_language="fr",
            corpus_language="french",
            tasks=["wordlist"],
        ),
    )
    db_payload.run_payload_upsert(
        release_dir=release_dir,
        payload_path=french_payload,
        database_url=database_url,
        apply_changes=True,
    )

    engine = create_engine(database_url, future=True)
    session_factory = sessionmaker(bind=engine, future=True)
    with session_factory() as session:
        sessions = session.scalars(select(ResearchSession).order_by(ResearchSession.session_id)).all()
    assert [(row.session_id, row.target_language) for row in sessions] == [
        ("EN-L-0001-2026-S01", "en"),
        ("FR-L-0002-2026-S01", "fr"),
    ]


def test_db_payload_invalid_payload_blocks_upsert(tmp_path: Path) -> None:
    release_dir = tmp_path / "release"
    _write_runtime_session(release_dir, language_slug="english", session_id="EN-L-0001-2026-S01", tasks=("text",))
    payload = _payload()
    payload["persons"][0]["consent_file"] = r"C:\secure\consent.pdf"
    payload_path = _write_payload(release_dir, payload)

    with pytest.raises(db_payload.PayloadUpsertError, match="Windows path"):
        db_payload.run_payload_upsert(
            release_dir=release_dir,
            payload_path=payload_path,
            database_url=_database_url(tmp_path),
            apply_changes=True,
        )


def test_db_payload_missing_payload_fails_cleanly(tmp_path: Path) -> None:
    release_dir = tmp_path / "release"
    release_dir.mkdir()

    with pytest.raises(db_payload.PayloadUpsertError, match="missing"):
        db_payload.load_payload(release_dir / "db" / "import_payload.json")
