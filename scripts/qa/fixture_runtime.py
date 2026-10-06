"""Synthetic research runtime for browser smokes and format tests (no real data, no personal values).

    python scripts/qa/fixture_runtime.py --root tmp/ui-qa/<date>-fixture-runtime

Builds ``<root>/data/sessions/<corpus>/<session_id>/`` in the real runtime format (``metadata.json``,
``alignment/wordlist.json``, ``derived/wordlist.mp3``, ``items/wordlist/<item>.mp3``) for one Spanish learner pair,
one Spanish native speaker, one French and one English learner, and copies the tracked task catalogs of
``app/tests/fixtures/runtime`` next to them. The MP3 bytes are a tiny placeholder (HEAD/Range requests work, the
browser smoke stubs playback). All person values are invented.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_CONFIG = REPO_ROOT / "app" / "tests" / "fixtures" / "runtime" / "data" / "config"
PLACEHOLDER_MP3 = b"ID3\x04\x00\x00\x00\x00\x00\x00\xff\xfb\x90\x64" + (b"\x00" * 256)

#: corpus -> (iso code, [(session_id, person_id, speaker_type, level_or_variety)])
SESSIONS = {
    "spanish": ("es", [("ES-L-0001-2026-S01", "ES-L-0001", "learner", "A2"), ("ES-L-0002-2026-S01", "ES-L-0002", "learner", "B1"), ("ES-N-0001-2026-S01", "ES-N-0001", "native_speaker", "es_std")]),
    "french": ("fr", [("FR-L-0001-2026-S01", "FR-L-0001", "learner", "A2")]),
    "english": ("en", [("EN-L-0001-2026-S01", "EN-L-0001", "learner", "B2")]),
}


def metadata_payload(session_id: str, person_id: str, iso: str, speaker_type: str, marker: str) -> dict[str, object]:
    """``metadata.json`` with exactly the keys the real runtime files carry (golden format)."""
    learner = speaker_type == "learner"
    return {
        "person_id": person_id,
        "session_id": session_id,
        "target_language": iso,
        "speaker_type": speaker_type,
        "l1": "DE" if learner else None,
        "l1_additional": ["EN"] if learner else [],
        "mother_l1": "DE" if learner else None,
        "father_l1": "DE" if learner else None,
        "additional_languages": ["English"] if learner else [],
        "gender": "female" if learner else "male",
        "birth_year": 1999 if learner else 1990,
        "current_region": "Testregion" if learner else None,
        "childhood_region": "Testregion" if learner else None,
        "origin_country": None if learner else "Spain",
        "origin_region": None if learner else "Testregion",
        "person_notes": None,
        "research_consent_signed": "yes" if learner else None,
        "teaching_consent_signed": "no" if learner else None,
        "consent_date": "2026-01-01" if learner else None,
        "standard_variety": None if learner else marker,
        "level_code": marker if learner else None,
        "level_self": marker if learner else None,
        "recording_year": 2026,
        "recording_date": "2026-03-01",
        "context": "baseline",
        "recorded_by": "Fixture Recorder",
        "needs_review": False,
        "session_notes": None,
        "notes": None,
        "tasks": [
            {"task_type": "wordlist", "label": "wordlist", "alignment_file": "alignment/wordlist.json", "derived_file": "derived/wordlist.mp3"},
        ],
        "files": [
            {"path": "alignment/wordlist.json", "file_role": "alignment", "format": "json", "status": "ready"},
            {"path": "derived/wordlist.mp3", "file_role": "derived_audio", "format": "mp3", "status": "ready"},
        ],
        "stays_in_target_country": True if learner else None,
        "exposure_entries": [],
    }


def catalog_items(corpus: str) -> list[dict[str, str]]:
    payload = json.loads((FIXTURE_CONFIG / "research_player" / corpus / "task_catalogs" / "wordlist.json").read_text(encoding="utf-8"))
    return payload["items"]


def alignment_payload(session_id: str, person_id: str, items: list[dict[str, str]]) -> dict[str, object]:
    return {
        "session_id": session_id,
        "person_id": person_id,
        "task": "wordlist",
        "audio": {"full_mp3": "derived/wordlist.mp3"},
        "items": [
            {
                "item_id": item["item_id"],
                "item_number": item.get("item_number") or item["item_id"].split("_")[-1].lstrip("0"),
                "text": item["text"],
                "start_ms": 500 + index * 1000,
                "end_ms": 1200 + index * 1000,
                "split_mp3": f"items/wordlist/{item['item_id']}.mp3",
            }
            for index, item in enumerate(items)
        ],
    }


def build_runtime(root: Path) -> Path:
    """Create the fixture runtime under ``root`` and return it."""
    for corpus, (iso, sessions) in SESSIONS.items():
        shutil.copytree(FIXTURE_CONFIG / "research_player" / corpus, root / "data" / "config" / "research_player" / corpus, dirs_exist_ok=True)
        items = catalog_items(corpus)
        for session_id, person_id, speaker_type, marker in sessions:
            session_dir = root / "data" / "sessions" / corpus / session_id
            (session_dir / "alignment").mkdir(parents=True, exist_ok=True)
            (session_dir / "derived").mkdir(parents=True, exist_ok=True)
            (session_dir / "items" / "wordlist").mkdir(parents=True, exist_ok=True)
            (session_dir / "metadata.json").write_text(json.dumps(metadata_payload(session_id, person_id, iso, speaker_type, marker), indent=2) + "\n", encoding="utf-8")
            (session_dir / "alignment" / "wordlist.json").write_text(json.dumps(alignment_payload(session_id, person_id, items), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            (session_dir / "derived" / "wordlist.mp3").write_bytes(PLACEHOLDER_MP3)
            for item in items:
                (session_dir / "items" / "wordlist" / f"{item['item_id']}.mp3").write_bytes(PLACEHOLDER_MP3)
    spanish_config = root / "data" / "config" / "research_player" / "spanish"
    first, second = (item["item_id"] for item in catalog_items("spanish")[:2])
    (spanish_config / "phenomena_presets.json").write_text(
        json.dumps(
            {
                "language": "spanish",
                "presets": [
                    {
                        "preset_id": "fixture_preset",
                        "label": "Fixture preset",
                        "description": "Two wordlist items for the browser smoke.",
                        "language": "spanish",
                        "items": [{"task": "wordlist", "item_id": first}, {"task": "wordlist", "item_id": second}],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "public").mkdir(parents=True, exist_ok=True)
    (root / "logs").mkdir(parents=True, exist_ok=True)
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    print(build_runtime(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
