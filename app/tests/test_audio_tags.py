"""Web MP3s carry no descriptive source tags (DATA-01)."""

from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "research_data_intake"))

import audio_tags  # noqa: E402
import scan_audio_tags  # noqa: E402
from intake_storage import validate_prod_package, validate_runtime_tree, validate_archive_tree  # noqa: E402

# Three fake MPEG-1 Layer III frame headers + zero padding: enough for a byte-exact frame comparison.
AUDIO = (b"\xff\xfb\x90\x64" + b"\x00" * 413) * 3
SENTINEL_TITLE = "Sentinelname_Liste_ENG"


def _syncsafe(value: int) -> bytes:
    return bytes([(value >> 21) & 0x7F, (value >> 14) & 0x7F, (value >> 7) & 0x7F, value & 0x7F])


def _frame(frame_id: str, text: str) -> bytes:
    payload = b"\x03" + text.encode("utf-8")
    return frame_id.encode("ascii") + _syncsafe(len(payload)) + b"\x00\x00" + payload


def _mp3(*frames: bytes, id3v1: bool = False) -> bytes:
    body = b"".join(frames)
    tag = b"ID3\x04\x00\x00" + _syncsafe(len(body)) + body if frames else b""
    trailer = b"TAG" + b"\x00" * 125 if id3v1 else b""
    return tag + AUDIO + trailer


def test_reader_reports_frame_ids_and_flags_descriptive_tags(tmp_path: Path) -> None:
    path = tmp_path / "a.mp3"
    path.write_bytes(_mp3(_frame("TIT2", SENTINEL_TITLE), _frame("TPE1", "x"), _frame("TSSE", "Lavf61"), _frame("COMM", "c"), id3v1=True))

    report = audio_tags.read_tags(path)

    assert report.disallowed == ["id3v2:COMM", "id3v2:TIT2", "id3v2:TPE1", "id3v1"]
    assert report.id3v2_frames["TSSE"] == ["Lavf61"]


def test_encoder_only_and_untagged_files_are_allowed(tmp_path: Path) -> None:
    (tmp_path / "enc.mp3").write_bytes(_mp3(_frame("TSSE", "Lavf61.1.100")))
    (tmp_path / "none.mp3").write_bytes(_mp3())

    assert audio_tags.read_tags(tmp_path / "enc.mp3").disallowed == []
    assert audio_tags.read_tags(tmp_path / "none.mp3").disallowed == []


def test_strip_keeps_the_mpeg_frames_byte_for_byte(tmp_path: Path) -> None:
    source = tmp_path / "in.mp3"
    source.write_bytes(_mp3(_frame("TIT2", SENTINEL_TITLE), _frame("TRCK", "1"), id3v1=True))
    target = tmp_path / "out.mp3"

    audio_tags.strip_tags(source, target)

    assert target.read_bytes() == AUDIO
    assert audio_tags.read_tags(target).disallowed == []


def test_runtime_validator_rejects_a_contaminated_file_without_echoing_the_value(tmp_path: Path) -> None:
    session = tmp_path / "ES-L-0001-2026-S01"
    (session / "derived").mkdir(parents=True)
    (session / "derived" / "wordlist.mp3").write_bytes(_mp3(_frame("TIT2", SENTINEL_TITLE)))

    errors = validate_runtime_tree(session)

    assert any("disallowed tag id3v2:TIT2" in error for error in errors)
    assert not any(SENTINEL_TITLE in error for error in errors)

    (session / "derived" / "wordlist.mp3").write_bytes(_mp3(_frame("TSSE", "Lavf61")))
    assert validate_runtime_tree(session) == []


def test_prod_package_validator_rejects_a_contaminated_mp3(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    (package / "sessions" / "spanish" / "ES-L-0001-2026-S01" / "derived").mkdir(parents=True)
    (package / "sessions" / "spanish" / "ES-L-0001-2026-S01" / "derived" / "wordlist.mp3").write_bytes(_mp3(_frame("TPE1", "Someone")))

    assert any("prod package MP3 carries disallowed tag id3v2:TPE1" in error for error in validate_prod_package(package))


def test_archive_layer_is_not_rejudged_against_the_tag_policy(tmp_path: Path) -> None:
    archive = tmp_path / "ES-L-0001-2026-S01"
    (archive / "runtime" / "derived").mkdir(parents=True)
    (archive / "runtime" / "derived" / "wordlist.mp3").write_bytes(_mp3(_frame("TIT2", SENTINEL_TITLE)))

    assert not any("disallowed tag" in error for error in validate_archive_tree(archive))


def test_scan_tool_reports_counts_only_and_cleans_in_place(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "sessions"
    (root / "spanish" / "ES-L-0001-2026-S01" / "derived").mkdir(parents=True)
    bad = root / "spanish" / "ES-L-0001-2026-S01" / "derived" / "wordlist.mp3"
    good = root / "spanish" / "ES-L-0001-2026-S01" / "derived" / "text.mp3"
    bad.write_bytes(_mp3(_frame("TIT2", SENTINEL_TITLE), _frame("TSSE", "Lavf61")))
    good.write_bytes(_mp3(_frame("TSSE", "Lavf61")))
    good_before = good.read_bytes()

    assert scan_audio_tags.main(["--root", str(root)]) == 1
    assert SENTINEL_TITLE not in capsys.readouterr().out

    assert scan_audio_tags.main(["--root", str(root), "--clean"]) == 0
    assert audio_tags.read_tags(bad).disallowed == []
    assert hashlib.sha256(bad.read_bytes()).hexdigest() == hashlib.sha256(AUDIO).hexdigest()
    assert good.read_bytes() == good_before  # a compliant file is not touched
    assert scan_audio_tags.main(["--root", str(root)]) == 0


def test_scan_tool_refuses_archive_and_secure_trees(tmp_path: Path) -> None:
    for name in ("secure", "source", "archive"):
        target = tmp_path / name / "sessions"
        target.mkdir(parents=True)
        assert scan_audio_tags.main(["--root", str(target), "--clean"]) == 2


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg is not installed")
def test_conversion_does_not_inherit_the_tags_of_the_source_recording(tmp_path: Path) -> None:
    from audio_conversion.ffmpeg_audio import create_full_task_mp3, create_split_mp3

    wav = tmp_path / "source.wav"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=2", "-metadata", f"title={SENTINEL_TITLE}", "-metadata", "artist=Sentinel", "-metadata", "comment=Sentinel", str(wav)],
        check=True,
    )
    full = tmp_path / "derived" / "wordlist.mp3"
    split = tmp_path / "items" / "wl_001.mp3"

    create_full_task_mp3(wav, full)
    create_split_mp3(full, split, 0.2, 1.0)

    for produced in (full, split):
        report = audio_tags.read_tags(produced)
        assert report.disallowed == [], produced
        assert SENTINEL_TITLE.encode() not in produced.read_bytes()
        assert produced.stat().st_size > 1000
