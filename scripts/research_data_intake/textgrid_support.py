from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


SILENCE_MARKERS = {"", "sp", "sil", "silence", "silent", "<sil>", "_"}
_TEXTGRID_INTERVAL_PATTERN = re.compile(
    r"intervals \[\d+\]:\s*xmin = ([0-9.]+)\s*xmax = ([0-9.]+)\s*text = \"(.*?)\"",
    re.DOTALL,
)


@dataclass(frozen=True, slots=True)
class TextGridInterval:
    start_seconds: float
    end_seconds: float
    text: str


def _read_textgrid_text(path: Path) -> str:
    for encoding in ("utf-16", "utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError:
            continue
    raise ValueError(f"Unsupported TextGrid encoding: {path}")


def parse_textgrid_intervals(path: Path) -> list[TextGridInterval]:
    raw_text = _read_textgrid_text(path)
    intervals = [
        TextGridInterval(start_seconds=float(start), end_seconds=float(end), text=text)
        for start, end, text in _TEXTGRID_INTERVAL_PATTERN.findall(raw_text)
    ]
    if not intervals:
        raise ValueError(f"No intervals found in TextGrid: {path}")
    return intervals


def spoken_intervals(intervals: list[TextGridInterval]) -> list[TextGridInterval]:
    spoken = [interval for interval in intervals if interval.text.strip().lower() not in SILENCE_MARKERS]
    if not spoken:
        raise ValueError("TextGrid does not contain any spoken intervals.")
    return spoken


def round_textgrid_seconds(seconds: float) -> float:
    return round(seconds, 4)
