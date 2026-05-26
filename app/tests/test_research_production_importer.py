from __future__ import annotations

import json
import os
import sys
import zipfile
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.datavalidation import DataValidation
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

import app.research_sessions as research_sessions  # noqa: E402
from app.auth.models import Base  # noqa: E402
from app.research_metadata import ResearchPerson, ResearchSession, ResearchSessionExposure  # noqa: E402
import import_batch_to_production as production_importer  # noqa: E402
from intake_workbook_reader import load_intake_workbook  # noqa: E402


def _set_runtime_env(tmp_path: Path, monkeypatch) -> Path:
    runtime_root = tmp_path / "runtime-root"
    (runtime_root / "data" / "sessions").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(runtime_root))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))
    monkeypatch.setenv("PROMAT_LOCAL_ARCHIVE_ROOT", str(tmp_path / "archive-root"))
    research_sessions.load_language_sessions.cache_clear()
    research_sessions.load_person_records.cache_clear()
    return runtime_root


def _session_row(
    *,
    person_id: str,
    session_ref: str,
    workbook_session_id: str,
    target_language: str,
    recording_year: int | None,
    recording_date: str,
    recorded_by: str = "Ana Romero",
    context: str = "baseline",
    standard_variety: str | None = None,
    level_self: str | None = None,
    level_code: str | None = None,
    session_notes: str | None = "test learner session",
) -> list[object]:
    return [
        person_id,
        session_ref,
        workbook_session_id,
        target_language,
        standard_variety,
        level_self,
        level_code,
        recording_year,
        recording_date,
        recorded_by,
        context,
        "no",
        session_notes,
    ]


def _write_workbook(
    tmp_path: Path,
    *,
    person_id: str = "ES-L-0001",
    speaker_type: str = "learner",
    include_out_of_scope_invalid_row: bool = False,
    use_deprecated_consent_column: bool = False,
    research_consent_signed: str = "yes",
    teaching_consent_signed: str = "unknown",
    standard_variety: str | None = None,
    exposure_duration: object = 6,
    exposure_type: str = "erasmus",
    exposure_country: str = "Spain",
    exposure_notes: str = "Semester in Madrid.",
) -> Path:
    workbook_path = tmp_path / "intake.xlsx"
    workbook = Workbook()

    secure_sheet = workbook.active
    secure_sheet.title = "Secure_Person_Intake"
    secure_sheet.append(
        [
            "person_id",
            "last_name",
            "first_name",
            "email",
            "consent_signed" if use_deprecated_consent_column else "research_consent_signed",
            "consent_date",
            "consent_file",
            "teaching_consent_signed",
            "questionnaire_file",
            "paper_original_location",
            "intake_date",
            "intake_by",
            "needs_review",
            "verified_by",
            "verified_date",
            "secure_notes",
        ]
    )
    secure_sheet.append(
        [
            person_id,
            "Mustermann",
            "Anna",
            "anna@example.test",
            research_consent_signed,
            "2026-03-14",
            "consent_anna.pdf",
            teaching_consent_signed,
            "questionnaire_anna.pdf",
            "cabinet A",
            "2026-03-14",
            "Ana Romero",
            "no",
            None,
            None,
            "Internal secure note.",
        ]
    )

    person_sheet = workbook.create_sheet("Research_Person")
    person_sheet.title = "Research_Person"
    person_sheet.append(
        [
            "person_id",
            "speaker_type",
            "l1",
            "l1_additional",
            "mother_l1",
            "father_l1",
            "additional_languages",
            "gender",
            "birth_year",
            "current_region",
            "childhood_region",
            "origin_country",
            "origin_region",
            "needs_review",
            "person_notes",
        ]
    )
    person_sheet.append(
        [
            person_id,
            speaker_type,
            "DE" if speaker_type == "learner" else "ES",
            "IT; EN",
            "IT",
            "DE",
            "EN; FR",
            "female",
            2001,
            "NRW",
            "Bayern",
            None,
            None,
            "no",
            None,
        ]
    )

    session_sheet = workbook.create_sheet("Research_Session_Intake")
    session_sheet.append(
        [
            "person_id",
            "session_ref",
            "session_id",
            "target_language",
            "standard_variety",
            "level_self",
            "level_code",
            "recording_year",
            "recording_date",
            "recorded_by",
            "context",
            "needs_review",
            "session_notes",
        ]
    )
    session_sheet.append(
        _session_row(
            person_id=person_id,
            session_ref="S01",
            workbook_session_id="SHOULD-BE-IGNORED",
            target_language="ES",
            standard_variety=standard_variety if standard_variety is not None else ("ES_STD" if speaker_type == "native_speaker" else None),
            level_self="B1-B2" if speaker_type == "learner" else None,
            level_code="B1" if speaker_type == "learner" else None,
            recording_year=2026,
            recording_date="2026-03-14",
        )
    )
    if include_out_of_scope_invalid_row:
        session_sheet.append(
            _session_row(
                person_id="FR-L-0001",
                session_ref="S01",
                workbook_session_id="ALSO-IGNORED",
                target_language="FR",
                recording_year=None,
                recording_date="2026-04-01",
            )
        )

    exposure_sheet = workbook.create_sheet("Exposure")
    exposure_sheet.append(
        [
            "person_id",
            "session_ref",
            "target_language",
            "country",
            "duration_months",
            "type",
            "exposure_notes",
            "needs_review",
        ]
    )
    if speaker_type == "learner":
        exposure_sheet.append(
            [
                person_id,
                "S01",
                "ES",
                exposure_country,
                exposure_duration,
                exposure_type,
                exposure_notes,
                "no",
            ]
        )

    vocabulary_sheet = workbook.create_sheet("Vocabularies")
    vocabulary_sheet.append(
        [
            "gender",
            "speaker_type",
            "l1_code",
            "target_language",
            "level_code",
            "level_self",
            "standard_variety",
            "context",
            "exposure_type",
            "task_type",
            "recorded_by",
            "yes_no_unknown",
        ]
    )
    vocabulary_sheet.append(["female", "learner", "DE", "ES", "B1", "B1-B2", "EC_STD", "baseline", "study", "wordlist", "Ana Romero", "yes"])
    vocabulary_sheet.append([None, None, None, None, None, None, "CL_STD", None, "erasmus", None, None, "no"])
    vocabulary_sheet.append([None, None, None, None, None, None, "PE_STD", None, "school_exchange", None, None, "unknown"])

    workbook.save(workbook_path)
    workbook.close()
    return workbook_path


def _patch_workbook_sqref(workbook_path: Path, original: str, replacement: str) -> None:
    patched_path = workbook_path.with_suffix(".patched.xlsx")
    with zipfile.ZipFile(workbook_path, "r") as source_zip, zipfile.ZipFile(patched_path, "w") as target_zip:
        for item in source_zip.infolist():
            data = source_zip.read(item.filename)
            if item.filename.startswith("xl/worksheets/") and item.filename.endswith(".xml"):
                data = data.replace(original.encode("utf-8"), replacement.encode("utf-8"))
            target_zip.writestr(item, data)
    patched_path.replace(workbook_path)


def _prepare_interview_batch(
    tmp_path: Path,
    *,
    person_id: str = "ES-L-0001",
    include_raw_master: bool,
    include_working_interview: bool = True,
) -> Path:
    batch_dir = tmp_path / "spanish_batch_20260421"
    (batch_dir / "intake_data").mkdir(parents=True, exist_ok=True)
    (batch_dir / "processed").mkdir(parents=True, exist_ok=True)
    filename_prefix = person_id.lower().replace("-", "_")

    (batch_dir / "processed" / f"{filename_prefix}_interview_processed.wav").write_bytes(b"batch-source-interview")
    (batch_dir / "processed" / f"{filename_prefix}_interview_processed.json").write_text(
        json.dumps(
            {
                "segments": [
                    {
                        "speaker": "spk1",
                        "words": [
                            {"start": 0.0, "end": 0.5, "text": "Item", "duration": 0.5, "conf": 1, "pristine": True}
                        ],
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    if include_working_interview:
        (batch_dir / "working" / person_id / "interview" / "source").mkdir(parents=True, exist_ok=True)
        (batch_dir / "working" / person_id / "interview" / "alignment").mkdir(parents=True, exist_ok=True)

        interview_wav = batch_dir / "working" / person_id / "interview" / "source" / "interview.wav"
        interview_wav.write_bytes(b"working-interview-wav")
        interview_json = batch_dir / "working" / person_id / "interview" / "alignment" / "interview.json"
        interview_json.write_text(
            json.dumps(
                {
                    "session_id": None,
                    "person_id": person_id,
                    "task": "interview",
                    "audio": {"full_mp3": "derived/interview.mp3"},
                    "segments": [
                        {
                            "segment_id": "seg_001",
                            "segment_number": "1",
                            "speaker_code": "interviewer",
                            "start_ms": 0,
                            "end_ms": 1000,
                            "text": "Item Nummer 25.",
                            "tokens": [
                                {"token_id": "seg_001_tok_001", "text": "Item", "start_ms": 0, "end_ms": 250},
                                {"token_id": "seg_001_tok_002", "text": "Nummer", "start_ms": 250, "end_ms": 600},
                                {"token_id": "seg_001_tok_003", "text": "25", "suffix": ".", "start_ms": 600, "end_ms": 1000},
                            ],
                            "annotations": [
                                {
                                    "kind": "material_ref",
                                    "item_id": "wl_025",
                                    "task": "wordlist",
                                    "insert_after_token_id": "seg_001_tok_003",
                                    "label": "oír",
                                    "item_number": "25",
                                    "canonical_text": "oír",
                                }
                            ],
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if include_raw_master:
        raw_dir = batch_dir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / f"{filename_prefix}_interview_raw.wav").write_bytes(b"batch-raw-interview")

    return batch_dir


def _session_factory(tmp_path: Path):
    database_path = tmp_path / "research.sqlite3"
    engine = create_engine(f"sqlite+pysqlite:///{database_path.as_posix()}", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)


def test_load_intake_workbook_derives_session_id_and_ignores_out_of_scope_rows(tmp_path: Path) -> None:
    workbook_path = _write_workbook(tmp_path, include_out_of_scope_invalid_row=True)

    workbook_data = load_intake_workbook(workbook_path, target_language="es")

    assert workbook_data.errors == ()
    assert len(workbook_data.sessions) == 1
    assert workbook_data.sessions[0].session_id == "ES-L-0001-2026-S01"
    assert workbook_data.persons["ES-L-0001"].research_consent_signed == "yes"
    assert workbook_data.persons["ES-L-0001"].teaching_consent_signed == "unknown"
    assert workbook_data.warnings == (
        "Research_Session_Intake row 2 contains session_id='SHOULD-BE-IGNORED'; ignored because session_id is derived.",
    )


def test_load_intake_workbook_accepts_deprecated_consent_column_with_warning(tmp_path: Path) -> None:
    workbook_path = _write_workbook(tmp_path, use_deprecated_consent_column=True)

    workbook_data = load_intake_workbook(workbook_path, target_language="es")

    assert workbook_data.errors == ()
    assert workbook_data.persons["ES-L-0001"].research_consent_signed == "yes"
    assert workbook_data.warnings[0] == "Deprecated column consent_signed used; please rename to research_consent_signed."


def test_load_intake_workbook_normalizes_whole_column_sqref_without_modifying_original(tmp_path: Path) -> None:
    workbook_path = _write_workbook(tmp_path)
    workbook = load_workbook(workbook_path)
    sheet = workbook["Research_Session_Intake"]
    validation = DataValidation(type="list", formula1='"baseline,follow_up"')
    sheet.add_data_validation(validation)
    validation.add("H2:H1048576")
    workbook.save(workbook_path)
    workbook.close()
    _patch_workbook_sqref(workbook_path, "H2:H1048576", "H:H")

    workbook_data = load_intake_workbook(workbook_path, target_language="es")

    assert workbook_data.errors == ()
    assert workbook_data.sessions[0].session_id == "ES-L-0001-2026-S01"
    assert any("sqref 'H:H'" in warning and "original workbook was not modified" in warning for warning in workbook_data.warnings)
    with zipfile.ZipFile(workbook_path, "r") as workbook_zip:
        assert b'sqref="H:H"' in workbook_zip.read("xl/worksheets/sheet3.xml")


@pytest.mark.parametrize(
    ("raw_duration", "expected_duration"),
    [("0,75", 0.75), ("3,5", 3.5), ("6,5", 6.5), ("0.75", 0.75), ("3.5", 3.5)],
)
def test_load_intake_workbook_normalizes_decimal_exposure_duration_months(
    tmp_path: Path,
    raw_duration: object,
    expected_duration: float,
) -> None:
    workbook_path = _write_workbook(tmp_path, exposure_duration=raw_duration)

    workbook_data = load_intake_workbook(workbook_path, target_language="es")

    exposure = workbook_data.exposures_by_key[next(iter(workbook_data.exposures_by_key))][0]
    assert exposure.duration_months == expected_duration


def test_load_intake_workbook_keeps_country_string_and_normalizes_unspecified_exposure_type(tmp_path: Path) -> None:
    workbook_path = _write_workbook(
        tmp_path,
        exposure_duration="3",
        exposure_type="unspecified",
        exposure_country="France; Israel",
        exposure_notes="Stayed in Strasbourg and Vannes for approximately three weeks.",
    )

    workbook_data = load_intake_workbook(workbook_path, target_language="es")

    exposure = workbook_data.exposures_by_key[next(iter(workbook_data.exposures_by_key))][0]
    assert exposure.country == "France; Israel"
    assert exposure.exposure_type == "unknown"
    assert exposure.exposure_notes == "Stayed in Strasbourg and Vannes for approximately three weeks."
    assert workbook_data.warnings[-1] == "Deprecated exposure type unspecified in Exposure row 2; normalized to unknown."


@pytest.mark.parametrize("workbook_value", ["EC_STD", "CL_STD", "PE_STD", "BO_STD", "UY_STD", "PY_STD", "VE_STD"])
def test_load_intake_workbook_accepts_new_standard_varieties(tmp_path: Path, workbook_value: str) -> None:
    workbook_path = _write_workbook(tmp_path, speaker_type="native_speaker", standard_variety=workbook_value)

    workbook_data = load_intake_workbook(workbook_path, target_language="es")

    assert workbook_data.sessions[0].standard_variety == workbook_value.lower()


def test_production_import_syncs_interview_runtime_db_and_metadata(tmp_path: Path, monkeypatch) -> None:
    runtime_root = _set_runtime_env(tmp_path, monkeypatch)
    batch_dir = _prepare_interview_batch(tmp_path, include_raw_master=True)
    workbook_path = _write_workbook(tmp_path)
    workbook_data = load_intake_workbook(workbook_path, target_language="es")
    session_factory = _session_factory(tmp_path)

    monkeypatch.setattr(
        production_importer,
        "create_full_task_mp3",
        lambda source_wav, target_mp3: target_mp3.write_bytes(b"runtime-interview-mp3"),
    )

    with session_factory() as db_session:
        plans, plan_warnings = production_importer._build_import_plans(
            batch_dir=batch_dir,
            workbook_data=workbook_data,
            create_missing_only=False,
            sync_tasks=True,
            sync_raw_only=False,
            allow_session_id_change=False,
            db_session=db_session,
        )
        assert plan_warnings == []
        assert len(plans) == 1
        plan = plans[0]
        by_task = {task_plan.task_key: task_plan for task_plan in plan.task_plans}
        assert by_task["interview"].action == "sync"
        assert by_task["interview"].status == "ready"

        production_importer._apply_plan(db_session, plan, validate_wordlist_labels="off")

    session_dir = runtime_root / "data" / "sessions" / "spanish" / "ES-L-0001-2026-S01"
    archive_dir = tmp_path / "archive-root" / "sessions" / "es" / "ES-L-0001-2026-S01"
    metadata = json.loads((session_dir / "metadata.json").read_text(encoding="utf-8"))
    interview_alignment = json.loads((session_dir / "alignment" / "interview.json").read_text(encoding="utf-8"))

    assert not (session_dir / "source" / "interview.wav").exists()
    assert not (session_dir / "raw" / "interview.wav").exists()
    assert (session_dir / "derived" / "interview.mp3").read_bytes() == b"runtime-interview-mp3"
    assert interview_alignment["session_id"] == "ES-L-0001-2026-S01"
    assert interview_alignment["audio"] == {"full_mp3": "derived/interview.mp3"}
    assert interview_alignment["segments"][0]["tokens"][2]["suffix"] == "."
    assert all("trailing_punctuation" not in annotation for annotation in interview_alignment["segments"][0]["annotations"])

    interview_task = next(task for task in metadata["tasks"] if task["task_type"] == "interview")
    assert interview_task == {
        "task_type": "interview",
        "label": "Interview zur Aussprache",
        "alignment_file": "alignment/interview.json",
        "derived_file": "derived/interview.mp3",
    }
    exposure_entry = metadata["exposure_entries"][0]
    assert exposure_entry["exposure_notes"] == "Semester in Madrid."
    assert metadata["research_consent_signed"] == "yes"
    assert metadata["teaching_consent_signed"] == "unknown"
    assert metadata["session_notes"] == "test learner session"

    file_paths = {entry["path"] for entry in metadata["files"]}
    assert "alignment/interview.json" in file_paths
    assert "derived/interview.mp3" in file_paths
    assert "source/interview.wav" not in file_paths
    assert "raw/interview.wav" not in file_paths

    archive_manifest = json.loads((archive_dir / "metadata" / "archive_manifest.json").read_text(encoding="utf-8"))
    assert (archive_dir / "source" / "interview.wav").read_bytes() == b"batch-source-interview"
    assert (archive_dir / "raw" / "interview.wav").read_bytes() == b"batch-raw-interview"
    assert (archive_dir / "runtime" / "derived" / "interview.mp3").read_bytes() == b"runtime-interview-mp3"
    assert archive_manifest["session_id"] == "ES-L-0001-2026-S01"
    assert archive_manifest["source_batch"] == "spanish_batch_20260421"

    research_sessions.load_language_sessions.cache_clear()
    research_sessions.load_person_records.cache_clear()
    runtime_session = research_sessions.get_session("spanish", "ES-L-0001-2026-S01")
    assert runtime_session is not None
    assert runtime_session.documented_task_types == ("interview",)
    assert runtime_session.exposure_entries[0].exposure_notes == "Semester in Madrid."

    with session_factory() as db_session:
        person_rows = db_session.scalars(select(ResearchPerson)).all()
        session_rows = db_session.scalars(select(ResearchSession)).all()
        exposure_rows = db_session.scalars(select(ResearchSessionExposure)).all()

    assert [row.person_id for row in person_rows] == ["ES-L-0001"]
    assert [row.session_id for row in session_rows] == ["ES-L-0001-2026-S01"]
    assert session_rows[0].documented_tasks == "interview"
    assert len(exposure_rows) == 1
    assert exposure_rows[0].exposure_notes == "Semester in Madrid."
    assert person_rows[0].research_consent_signed == "yes"
    assert person_rows[0].teaching_consent_signed == "unknown"


def test_production_import_does_not_treat_source_as_raw_fallback(tmp_path: Path, monkeypatch) -> None:
    runtime_root = _set_runtime_env(tmp_path, monkeypatch)
    batch_dir = _prepare_interview_batch(tmp_path, include_raw_master=False)
    workbook_path = _write_workbook(tmp_path)
    workbook_data = load_intake_workbook(workbook_path, target_language="es")
    session_factory = _session_factory(tmp_path)

    monkeypatch.setattr(
        production_importer,
        "create_full_task_mp3",
        lambda source_wav, target_mp3: target_mp3.write_bytes(b"runtime-interview-mp3"),
    )

    with session_factory() as db_session:
        plans, _ = production_importer._build_import_plans(
            batch_dir=batch_dir,
            workbook_data=workbook_data,
            create_missing_only=False,
            sync_tasks=True,
            sync_raw_only=False,
            allow_session_id_change=False,
            db_session=db_session,
        )
        production_importer._apply_plan(db_session, plans[0], validate_wordlist_labels="off")

    session_dir = runtime_root / "data" / "sessions" / "spanish" / "ES-L-0001-2026-S01"
    archive_dir = tmp_path / "archive-root" / "sessions" / "es" / "ES-L-0001-2026-S01"
    assert not (session_dir / "source" / "interview.wav").exists()
    assert not (session_dir / "raw" / "interview.wav").exists()
    assert (archive_dir / "source" / "interview.wav").exists()
    assert not (archive_dir / "raw" / "interview.wav").exists()


def test_production_import_rerun_is_idempotent_for_interview_session(tmp_path: Path, monkeypatch) -> None:
    _set_runtime_env(tmp_path, monkeypatch)
    batch_dir = _prepare_interview_batch(tmp_path, include_raw_master=True)
    workbook_path = _write_workbook(tmp_path)
    workbook_data = load_intake_workbook(workbook_path, target_language="es")
    session_factory = _session_factory(tmp_path)

    monkeypatch.setattr(
        production_importer,
        "create_full_task_mp3",
        lambda source_wav, target_mp3: target_mp3.write_bytes(b"runtime-interview-mp3"),
    )

    with session_factory() as db_session:
        plans, _ = production_importer._build_import_plans(
            batch_dir=batch_dir,
            workbook_data=workbook_data,
            create_missing_only=False,
            sync_tasks=True,
            sync_raw_only=False,
            allow_session_id_change=False,
            db_session=db_session,
        )
        production_importer._apply_plan(db_session, plans[0], validate_wordlist_labels="off")

    with session_factory() as db_session:
        plans, _ = production_importer._build_import_plans(
            batch_dir=batch_dir,
            workbook_data=workbook_data,
            create_missing_only=False,
            sync_tasks=True,
            sync_raw_only=False,
            allow_session_id_change=False,
            db_session=db_session,
        )
        assert plans[0].mode_action == "update"
        production_importer._apply_plan(db_session, plans[0], validate_wordlist_labels="off")

    session_dir = tmp_path / "runtime-root" / "data" / "sessions" / "spanish" / "ES-L-0001-2026-S01"
    metadata = json.loads((session_dir / "metadata.json").read_text(encoding="utf-8"))
    interview_tasks = [task for task in metadata["tasks"] if task["task_type"] == "interview"]
    assert len(interview_tasks) == 1
    file_paths = [entry["path"] for entry in metadata["files"]]
    assert file_paths.count("alignment/interview.json") == 1
    assert file_paths.count("derived/interview.mp3") == 1
    assert file_paths.count("source/interview.wav") == 0
    assert file_paths.count("raw/interview.wav") == 0

    with session_factory() as db_session:
        person_rows = db_session.scalars(select(ResearchPerson)).all()
        session_rows = db_session.scalars(select(ResearchSession)).all()
        exposure_rows = db_session.scalars(select(ResearchSessionExposure)).all()

    assert len(person_rows) == 1
    assert len(session_rows) == 1
    assert len(exposure_rows) == 1


def test_production_import_skips_native_speaker_interview_even_with_inputs(tmp_path: Path, monkeypatch) -> None:
    runtime_root = _set_runtime_env(tmp_path, monkeypatch)
    batch_dir = _prepare_interview_batch(
        tmp_path,
        person_id="ES-N-0001",
        include_raw_master=True,
        include_working_interview=True,
    )
    workbook_path = _write_workbook(tmp_path, person_id="ES-N-0001", speaker_type="native_speaker")
    workbook_data = load_intake_workbook(workbook_path, target_language="es")
    session_factory = _session_factory(tmp_path)

    with session_factory() as db_session:
        plans, plan_warnings = production_importer._build_import_plans(
            batch_dir=batch_dir,
            workbook_data=workbook_data,
            create_missing_only=False,
            sync_tasks=True,
            sync_raw_only=False,
            allow_session_id_change=False,
            db_session=db_session,
        )
        assert plan_warnings == []
        assert len(plans) == 1
        plan = plans[0]
        by_task = {task_plan.task_key: task_plan for task_plan in plan.task_plans}
        assert by_task["interview"].action == "skip"
        assert by_task["interview"].status == "not_expected_for_native_speaker"

        production_importer._apply_plan(db_session, plan, validate_wordlist_labels="off")

    session_dir = runtime_root / "data" / "sessions" / "spanish" / "ES-N-0001-2026-S01"
    metadata = json.loads((session_dir / "metadata.json").read_text(encoding="utf-8"))

    assert metadata["speaker_type"] == "native_speaker"
    assert metadata["tasks"] == []
    file_paths = {entry["path"] for entry in metadata["files"]}
    assert file_paths == {"metadata.json"}
    assert not (session_dir / "source" / "interview.wav").exists()
    assert not (session_dir / "alignment" / "interview.json").exists()
    assert not (session_dir / "derived" / "interview.mp3").exists()
    assert not (session_dir / "raw" / "interview.wav").exists()

    with session_factory() as db_session:
        session_rows = db_session.scalars(select(ResearchSession)).all()

    assert [row.session_id for row in session_rows] == ["ES-N-0001-2026-S01"]
    assert session_rows[0].documented_tasks is None


def test_load_intake_workbook_exposes_secure_persons(tmp_path: Path) -> None:
    workbook_path = _write_workbook(tmp_path, person_id="ES-L-0001")

    workbook_data = load_intake_workbook(workbook_path, target_language="es")

    assert "ES-L-0001" in workbook_data.secure_persons
    sp = workbook_data.secure_persons["ES-L-0001"]
    assert sp.last_name == "Mustermann"
    assert sp.first_name == "Anna"
    assert sp.email == "anna@example.test"
    assert sp.research_consent_signed == "yes"
    assert sp.needs_review is False
    assert sp.intake_by == "Ana Romero"
    assert sp.paper_original_location == "cabinet A"


def test_load_intake_workbook_person_id_filter_accepts_set(tmp_path: Path) -> None:
    workbook_path = _write_workbook(tmp_path, person_id="ES-L-0001")

    workbook_data = load_intake_workbook(workbook_path, target_language="es", person_id_filter={"ES-L-0001"})

    assert len(workbook_data.sessions) == 1
    assert workbook_data.sessions[0].person_id == "ES-L-0001"
    assert workbook_data.errors == ()


def test_run_text_pipeline_skips_missing_working_text_inputs_in_write_mode(tmp_path: Path) -> None:
    batch_dir = tmp_path / "spanish_batch_20260525"
    batch_dir.mkdir()

    notes = production_importer._run_text_pipeline(
        batch_dir=batch_dir,
        person_id="ES-L-0010",
        target_language="es",
        mfa_executable="docker",
        dry_run=False,
    )

    assert notes == [
        "Skipped text MFA for ES-L-0010: working text inputs are not present; task will remain missing unless existing runtime artifacts are available."
    ]


def test_run_text_pipeline_dry_run_does_not_require_written_manifest(tmp_path: Path, monkeypatch) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    person_id = "EN-L-0008"
    (batch_dir / "working" / person_id / "text" / "source").mkdir(parents=True)
    (batch_dir / "working" / person_id / "text" / "alignment").mkdir()
    (batch_dir / "working" / person_id / "text" / "source" / "text.wav").write_bytes(b"wav")
    (batch_dir / "working" / person_id / "text" / "alignment" / "text.TextGrid").write_text("textgrid", encoding="utf-8")
    text_catalog_path = tmp_path / "text.json"
    text_catalog_path.write_text('{"task": "text", "language": "en", "items": []}\n', encoding="utf-8")

    monkeypatch.setattr(production_importer, "_text_task_catalog_path", lambda target_language: text_catalog_path)
    monkeypatch.setattr(
        production_importer,
        "prepare_text_mfa_for_person",
        lambda **kwargs: {"segments": 55, "warnings": ["EN-L-0008 text: omitted t_01 because the spoken title was not recorded"]},
    )

    def fail_run_text_mfa_for_person(**kwargs):
        raise AssertionError("dry-run must not require a written mfa_manifest.json")

    monkeypatch.setattr(production_importer, "run_text_mfa_for_person", fail_run_text_mfa_for_person)

    notes = production_importer._run_text_pipeline(
        batch_dir=batch_dir,
        person_id=person_id,
        target_language="en",
        mfa_executable="docker",
        dry_run=True,
    )

    assert notes == [
        "Prepared text MFA corpus for EN-L-0008: segments=55",
        "Text MFA prep warning for EN-L-0008: EN-L-0008 text: omitted t_01 because the spoken title was not recorded",
        "Planned MFA for EN-L-0008: executable=docker",
        "Planned working text alignment import for EN-L-0008 after MFA outputs are available.",
    ]
