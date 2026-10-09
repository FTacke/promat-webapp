"""Translation parity, controlled-vocabulary coverage and the golden runtime metadata format (Run 3, TI-17/TI-19)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app" / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "qa"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app.config.data_conventions import STANDARD_VARIETIES  # noqa: E402
from app.i18n import SUPPORTED_UI_LANGUAGES, TRANSLATIONS  # noqa: E402
from app.research_views import STANDARD_VARIETY_LABEL_KEYS  # noqa: E402
import fixture_runtime  # noqa: E402

#: Keys that are intentionally empty (the visible copy is rendered elsewhere).
INTENTIONALLY_EMPTY = {"research.speakers.intro", "research.comparison.intro"}
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def test_german_and_english_define_exactly_the_same_keys() -> None:
    assert set(SUPPORTED_UI_LANGUAGES) == {"de", "en"}
    de, en = set(TRANSLATIONS["de"]), set(TRANSLATIONS["en"])
    assert sorted(de - en) == [], "keys that exist only in German"
    assert sorted(en - de) == [], "keys that exist only in English"


def test_translations_keep_their_placeholders_and_are_not_empty() -> None:
    de, en = TRANSLATIONS["de"], TRANSLATIONS["en"]
    mismatched = sorted(key for key in de if sorted(PLACEHOLDER.findall(de[key])) != sorted(PLACEHOLDER.findall(en.get(key, ""))))
    assert mismatched == []
    empty = sorted({key for language in ("de", "en") for key, value in TRANSLATIONS[language].items() if not value.strip()} - INTENTIONALLY_EMPTY)
    assert empty == []


def test_german_copy_uses_real_umlauts_not_transliterations() -> None:
    suspicious = re.compile(r"\b(?:fuer|ueber|waehlen|zurueck|Auswahl\w*ae|oeffnen|Loeschen)\b")
    offenders = sorted(key for key, value in TRANSLATIONS["de"].items() if suspicious.search(value))
    assert offenders == []


def test_status_labels_of_the_german_ui_are_german() -> None:
    de = TRANSLATIONS["de"]
    for key in ("common.status.curated", "common.status.custom", "research.comparison.state_draft", "research.comparison.state_curated", "research.comparison.state_custom"):
        assert de[key] not in {"curated", "custom", "Draft", "draft"}, key


def test_every_standard_variety_code_has_a_label_in_both_languages() -> None:
    codes = {code for group in STANDARD_VARIETIES.values() for code in group}
    assert sorted(codes - set(STANDARD_VARIETY_LABEL_KEYS)) == [], "variety codes without a registry entry"
    for language in ("de", "en"):
        missing = sorted(key for key in STANDARD_VARIETY_LABEL_KEYS.values() if key not in TRANSLATIONS[language])
        assert missing == [], f"variety label keys missing in {language}"


def test_irish_english_standard_variety_is_localized_centrally_and_other_varieties_are_untouched() -> None:
    key = STANDARD_VARIETY_LABEL_KEYS["ie_std"]
    assert TRANSLATIONS["de"][key] == "Irisches Englisch"
    assert TRANSLATIONS["en"][key] == "Irish English"
    assert "ie_std" in STANDARD_VARIETIES["en"]
    assert {code: TRANSLATIONS["de"][STANDARD_VARIETY_LABEL_KEYS[code]] for code in ("gb_std", "us_std", "au_std", "nz_std")} == {
        "gb_std": "Großbritannien",
        "us_std": "USA",
        "au_std": "Australien",
        "nz_std": "Neuseeland",
    }
    assert {code: TRANSLATIONS["en"][STANDARD_VARIETY_LABEL_KEYS[code]] for code in ("gb_std", "us_std", "au_std", "nz_std")} == {
        "gb_std": "United Kingdom",
        "us_std": "United States",
        "au_std": "Australia",
        "nz_std": "New Zealand",
    }


def test_comparison_level_prefix_is_compact_and_still_a_self_assessment() -> None:
    assert TRANSLATIONS["de"]["research.comparison.self_placement_prefix"] == "Niveau (selbst):"
    assert TRANSLATIONS["en"]["research.comparison.self_placement_prefix"] == "Level (self):"
    # Other presentations of the field keep their full wording.
    assert TRANSLATIONS["de"]["common.labels.level"] == "Selbsteinordnung"
    assert TRANSLATIONS["en"]["common.labels.level"] == "Self-placement"


GOLDEN_KEYS = [
    "person_id", "session_id", "target_language", "speaker_type", "l1", "l1_additional", "mother_l1", "father_l1", "additional_languages",
    "gender", "birth_year", "current_region", "childhood_region", "origin_country", "origin_region", "person_notes", "research_consent_signed",
    "teaching_consent_signed", "consent_date", "standard_variety", "level_code", "level_self", "recording_year", "recording_date", "context",
    "recorded_by", "needs_review", "session_notes", "notes", "tasks", "files", "stays_in_target_country", "exposure_entries",
]


def test_golden_metadata_has_exactly_the_runtime_key_set() -> None:
    for session_id, person_id, speaker_type, marker in (
        ("ES-L-0001-2026-S01", "ES-L-0001", "learner", "A2"),
        ("ES-N-0001-2026-S01", "ES-N-0001", "native_speaker", "es_std"),
    ):
        payload = fixture_runtime.metadata_payload(session_id, person_id, "es", speaker_type, marker)
        assert list(payload) == GOLDEN_KEYS
        assert set(payload["tasks"][0]) == {"task_type", "label", "alignment_file", "derived_file"}
        assert set(payload["files"][0]) == {"path", "file_role", "format", "status"}


@pytest.fixture
def fixture_runtime_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    from app.research_sessions import load_language_sessions, load_person_records

    root = fixture_runtime.build_runtime(tmp_path)
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(root))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(root / "public"))
    for loader in (load_language_sessions, load_person_records):
        loader.cache_clear()
    yield root
    for loader in (load_language_sessions, load_person_records):
        loader.cache_clear()


@pytest.mark.parametrize(("corpus", "expected_people"), [("spanish", 3), ("french", 1), ("english", 1)])
def test_runtime_loaders_accept_the_golden_metadata_of_every_corpus(fixture_runtime_env: Path, corpus: str, expected_people: int) -> None:
    from app.research_sessions import load_person_records

    records = load_person_records(corpus)
    assert len(records) == expected_people
    metadata = json.loads(next((fixture_runtime_env / "data" / "sessions" / corpus).glob("*/metadata.json")).read_text(encoding="utf-8"))
    assert metadata["target_language"] == {"spanish": "es", "french": "fr", "english": "en"}[corpus]
