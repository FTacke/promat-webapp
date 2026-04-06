from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from alignment_export.wordlist_alignment import TimedWordlistItem
from audio_conversion.ffmpeg_audio import create_split_mp3


SPLIT_PADDING_SECONDS = 0.25


@dataclass(frozen=True, slots=True)
class SplitBoundary:
    item_id: str
    start_seconds: float
    end_seconds: float
    output_path: Path


def build_split_boundaries(
    session_dir: Path,
    items: list[TimedWordlistItem],
    audio_duration_seconds: float,
) -> list[SplitBoundary]:
    boundaries: list[SplitBoundary] = []
    for item in items:
        start_seconds = max(0.0, item.start_seconds - SPLIT_PADDING_SECONDS)
        end_seconds = min(audio_duration_seconds, item.end_seconds + SPLIT_PADDING_SECONDS)
        boundaries.append(
            SplitBoundary(
                item_id=item.item_id,
                start_seconds=start_seconds,
                end_seconds=end_seconds,
                output_path=session_dir / item.split_mp3,
            )
        )
    return boundaries


def create_wordlist_splits(source_mp3: Path, boundaries: list[SplitBoundary]) -> None:
    if boundaries:
        boundaries[0].output_path.parent.mkdir(parents=True, exist_ok=True)
        for existing_split in boundaries[0].output_path.parent.glob("*.mp3"):
            existing_split.unlink()
    for boundary in boundaries:
        create_split_mp3(source_mp3, boundary.output_path, boundary.start_seconds, boundary.end_seconds)