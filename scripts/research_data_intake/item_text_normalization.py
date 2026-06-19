from __future__ import annotations

from dataclasses import dataclass


FRENCH_ITEM_TEXT_CORRECTIONS = {"théatre": "théâtre"}
FRENCH_LANGUAGE_VALUES = {"fr", "french"}


@dataclass(frozen=True, slots=True)
class ItemTextCorrection:
    source: str
    replacement: str
    occurrences: int

    def report_message(self, *, task: str, item_id: str | None = None) -> str:
        item_part = f" item_id={item_id}" if item_id else ""
        return (
            "canonical_item_correction"
            f" language=french task={task}{item_part}"
            f" source={self.source!r} replacement={self.replacement!r} occurrences={self.occurrences}"
        )


def canonicalize_item_text(language: str, value: str) -> tuple[str, tuple[ItemTextCorrection, ...]]:
    if language.strip().lower() not in FRENCH_LANGUAGE_VALUES:
        return value, ()

    normalized = value
    corrections: list[ItemTextCorrection] = []
    for source, replacement in FRENCH_ITEM_TEXT_CORRECTIONS.items():
        occurrences = normalized.count(source)
        if occurrences:
            normalized = normalized.replace(source, replacement)
            corrections.append(
                ItemTextCorrection(source=source, replacement=replacement, occurrences=occurrences)
            )
    return normalized, tuple(corrections)


def contains_noncanonical_french_item_text(value: str) -> bool:
    return any(source in value for source in FRENCH_ITEM_TEXT_CORRECTIONS)
