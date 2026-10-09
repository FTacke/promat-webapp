"""Presentation of L1 vocabulary codes as readable, localized language names.

The stored values (``KAB``, ``FR``, ...) and all filter logic stay untouched; this module only turns a code into
the language name of the UI language. No ISO code, tooltip or info indicator is shown. Codes that cannot be
resolved are shown verbatim.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .config.data_conventions import L1_CODES
from .i18n import translate


@dataclass(frozen=True, slots=True)
class L1Display:
    value: str
    label: str

    @property
    def resolved(self) -> bool:
        return self.label != self.value


def resolve_l1(ui_lang: str | None, value: object) -> L1Display | None:
    """Resolve one stored L1 value; ``None`` for empty values, the verbatim value for unknown codes."""
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    code = "unknown" if raw.lower() == "unknown" else raw.upper()
    if code not in L1_CODES:
        return L1Display(value=raw, label=raw)
    return L1Display(value=code, label=translate(ui_lang, f"language.l1.{code}"))


def l1_label(ui_lang: str | None, value: object) -> str:
    """Plain language name for filters, chips, badges and other text places; empty for an empty value."""
    display = resolve_l1(ui_lang, value)
    return display.label if display is not None else ""


def l1_text(ui_lang: str | None, value: object) -> str:
    """Language name for a metadata value; ``-`` for an empty value."""
    return l1_label(ui_lang, value) or "-"


def l1_list_text(ui_lang: str | None, values: Iterable[object]) -> str:
    """Comma-separated language names; ``-`` when there are none."""
    labels = [label for label in (l1_label(ui_lang, value) for value in values) if label]
    return ", ".join(labels) if labels else "-"


__all__ = [
    "L1Display",
    "l1_label",
    "l1_list_text",
    "l1_text",
    "resolve_l1",
]
