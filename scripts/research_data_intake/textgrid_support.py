from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


SILENCE_MARKERS = {"", "sp", "sil", "silence", "silent", "<sil>", "_"}
_TEXTGRID_INTERVAL_PATTERN = re.compile(
    r'intervals \[\d+\]:\s*xmin = ([0-9.]+)\s*xmax = ([0-9.]+)\s*text = "((?:""|[^"])*)"',
    re.DOTALL,
)
_TEXTGRID_TIER_PATTERN = re.compile(
    r"item \[\d+\]:\s*class = \"IntervalTier\"\s*name = \"(.*?)\"\s*xmin = [0-9.]+\s*xmax = [0-9.]+\s*"
    r"intervals: size = \d+\s*(.*?)(?=\n\s*item \[\d+\]:|\Z)",
    re.DOTALL,
)


@dataclass(frozen=True, slots=True)
class TextGridInterval:
    start_seconds: float
    end_seconds: float
    text: str


@dataclass(frozen=True, slots=True)
class TextGridTier:
    name: str
    intervals: list[TextGridInterval]


def _read_textgrid_text(path: Path) -> str:
    for encoding in ("utf-16", "utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError:
            continue
    raise ValueError(f"Unsupported TextGrid encoding: {path}")


def parse_textgrid_intervals(path: Path) -> list[TextGridInterval]:
    raw_text = _read_textgrid_text(path)
    intervals = _parse_intervals_from_text(raw_text)
    if not intervals:
        raise ValueError(f"No intervals found in TextGrid: {path}")
    return intervals


def _parse_intervals_from_text(raw_text: str) -> list[TextGridInterval]:
    return [
        TextGridInterval(start_seconds=float(start), end_seconds=float(end), text=text.replace('""', '"'))
        for start, end, text in _TEXTGRID_INTERVAL_PATTERN.findall(raw_text)
    ]


def parse_textgrid_tiers(path: Path) -> list[TextGridTier]:
    raw_text = _read_textgrid_text(path)
    tiers = [
        TextGridTier(name=name, intervals=_parse_intervals_from_text(tier_text))
        for name, tier_text in _TEXTGRID_TIER_PATTERN.findall(raw_text)
    ]
    if not tiers:
        raise ValueError(f"No named tiers found in TextGrid: {path}")
    return tiers


def get_textgrid_tier(path: Path, tier_name: str) -> TextGridTier:
    normalized_name = tier_name.strip().lower()
    for tier in parse_textgrid_tiers(path):
        if tier.name.strip().lower() == normalized_name:
            return tier
    raise ValueError(f"Tier {tier_name!r} not found in TextGrid: {path}")


def spoken_intervals(intervals: list[TextGridInterval]) -> list[TextGridInterval]:
    spoken = []
    for interval in intervals:
        normalized_text = interval.text.strip().lower()
        if normalized_text in SILENCE_MARKERS or normalized_text.startswith("silent"):
            continue
        spoken.append(interval)
    if not spoken:
        raise ValueError("TextGrid does not contain any spoken intervals.")
    return spoken


def round_textgrid_seconds(seconds: float) -> float:
    return round(seconds, 4)


def seconds_to_ms(seconds: float) -> int:
    return int(round(seconds * 1000))
