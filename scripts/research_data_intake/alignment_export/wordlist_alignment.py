from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path


EXPECTED_WORDLIST_COUNT = 92
SILENCE_MARKERS = {"", "sp", "sil", "silence", "silent"}


@dataclass(frozen=True, slots=True)
class CatalogItem:
    item_id: str
    item_number: str
    text: str


@dataclass(frozen=True, slots=True)
class TimedWordlistItem:
    item_id: str
    item_number: str
    text: str
    start_seconds: float
    end_seconds: float
    start_ms: int
    end_ms: int
    split_mp3: str

    def to_json(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "item_number": self.item_number,
            "text": self.text,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "split_mp3": self.split_mp3,
        }


@dataclass(frozen=True, slots=True)
class TextGridInterval:
    start_seconds: float
    end_seconds: float
    text: str


def load_wordlist_catalog(path: Path) -> list[CatalogItem]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("task") != "wordlist":
        raise ValueError(f"Catalog task must be 'wordlist': {path}")
    if payload.get("language") != "spanish":
        raise ValueError(f"Catalog language must be 'spanish': {path}")
    items_payload = payload.get("items")
    if not isinstance(items_payload, list):
        raise ValueError(f"Catalog items must be a list: {path}")
    if len(items_payload) != EXPECTED_WORDLIST_COUNT:
        raise ValueError(f"Catalog must define exactly {EXPECTED_WORDLIST_COUNT} items: {path}")

    catalog_items: list[CatalogItem] = []
    for index, item_payload in enumerate(items_payload, start=1):
        if not isinstance(item_payload, dict):
            raise ValueError(f"Catalog item {index} must be an object: {path}")
        expected_item_id = f"wl_{index:03d}"
        expected_item_number = str(index)
        item_id = item_payload.get("item_id")
        item_number = item_payload.get("item_number")
        text = item_payload.get("text")
        if item_id != expected_item_id:
            raise ValueError(f"Catalog item_id mismatch at index {index}: expected {expected_item_id}, got {item_id}")
        if item_number != expected_item_number:
            raise ValueError(
                f"Catalog item_number mismatch at index {index}: expected {expected_item_number}, got {item_number}"
            )
        if not isinstance(text, str) or not text:
            raise ValueError(f"Catalog text must be a non-empty string at index {index}")
        catalog_items.append(CatalogItem(item_id=item_id, item_number=item_number, text=text))
    return catalog_items


def parse_textgrid_intervals(path: Path) -> list[TextGridInterval]:
    raw_text = path.read_text(encoding="utf-16")
    pattern = re.compile(
        r"intervals \[\d+\]:\s*xmin = ([0-9.]+)\s*xmax = ([0-9.]+)\s*text = \"(.*?)\"",
        re.DOTALL,
    )
    intervals = [
        TextGridInterval(start_seconds=float(start), end_seconds=float(end), text=text)
        for start, end, text in pattern.findall(raw_text)
    ]
    if not intervals:
        raise ValueError(f"No intervals found in TextGrid: {path}")
    return intervals


def round_textgrid_seconds(seconds: float) -> float:
    return round(seconds, 4)


def seconds_to_ms(seconds: float) -> int:
    return int(round(seconds * 1000))


def build_timed_items(
    catalog_items: list[CatalogItem],
    intervals: list[TextGridInterval],
    validate_labels: str,
) -> tuple[list[TimedWordlistItem], list[str]]:
    non_silence_intervals = [interval for interval in intervals if interval.text.strip().lower() not in SILENCE_MARKERS]
    if len(non_silence_intervals) != EXPECTED_WORDLIST_COUNT:
        raise ValueError(
            f"TextGrid must provide exactly {EXPECTED_WORDLIST_COUNT} non-silence intervals, got {len(non_silence_intervals)}"
        )

    warnings: list[str] = []
    timed_items: list[TimedWordlistItem] = []
    for catalog_item, interval in zip(catalog_items, non_silence_intervals, strict=True):
        if interval.text != catalog_item.text:
            message = (
                f"TextGrid label mismatch for {catalog_item.item_id}: catalog={catalog_item.text!r} textgrid={interval.text!r}"
            )
            if validate_labels == "fail":
                raise ValueError(message)
            if validate_labels == "warn":
                warnings.append(message)

        start_seconds = round_textgrid_seconds(interval.start_seconds)
        end_seconds = round_textgrid_seconds(interval.end_seconds)
        if end_seconds <= start_seconds:
            raise ValueError(f"Non-positive timing interval for {catalog_item.item_id}: {start_seconds} >= {end_seconds}")

        timed_items.append(
            TimedWordlistItem(
                item_id=catalog_item.item_id,
                item_number=catalog_item.item_number,
                text=catalog_item.text,
                start_seconds=start_seconds,
                end_seconds=end_seconds,
                start_ms=seconds_to_ms(start_seconds),
                end_ms=seconds_to_ms(end_seconds),
                split_mp3=f"items/wordlist/{catalog_item.item_id}.mp3",
            )
        )
    return timed_items, warnings


def build_alignment_payload(session_id: str, person_id: str, items: list[TimedWordlistItem]) -> dict[str, object]:
    return {
        "session_id": session_id,
        "person_id": person_id,
        "task": "wordlist",
        "audio": {
            "full_mp3": "derived/wordlist.mp3",
        },
        "items": [item.to_json() for item in items],
    }


def write_alignment_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")