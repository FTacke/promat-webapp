"""Presentation of L1 vocabulary codes as readable, localized language names.

The stored values (``KAB``, ``FR``, ...) and all filter logic stay untouched; this module only turns a code into
the language name of the UI language plus an optional info indicator carrying the ISO standard and code.
Codes that cannot be resolved are shown verbatim.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import count

from markupsafe import Markup

from .config.data_conventions import L1_CODES, get_l1_iso_reference
from .i18n import translate

_TIP_IDS = count(1)


@dataclass(frozen=True, slots=True)
class L1Display:
    value: str
    label: str
    tooltip: str | None
    info_label: str | None

    @property
    def resolved(self) -> bool:
        return self.tooltip is not None or self.label != self.value


def resolve_l1(ui_lang: str | None, value: object) -> L1Display | None:
    """Resolve one stored L1 value; ``None`` for empty values, the verbatim value for unknown codes."""
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    code = "unknown" if raw.lower() == "unknown" else raw.upper()
    if code not in L1_CODES:
        return L1Display(value=raw, label=raw, tooltip=None, info_label=None)
    label = translate(ui_lang, f"language.l1.{code}")
    reference = get_l1_iso_reference(code)
    if reference is None:
        return L1Display(value=code, label=label, tooltip=None, info_label=None)
    standard, iso_code = reference
    return L1Display(
        value=code,
        label=label,
        tooltip=translate(ui_lang, "language.l1.tooltip", standard=standard, code=iso_code),
        info_label=translate(ui_lang, "language.l1.info_label"),
    )


def l1_label(ui_lang: str | None, value: object) -> str:
    """Plain language name (no markup) for filters, chips and other text-only places."""
    display = resolve_l1(ui_lang, value)
    return display.label if display is not None else ""


def l1_client_payload(ui_lang: str | None, value: object) -> dict[str, str]:
    """Plain data for client-rendered surfaces (value, label, tooltip, info label)."""
    display = resolve_l1(ui_lang, value)
    if display is None:
        return {"value": "", "label": "", "tooltip": "", "infoLabel": ""}
    return {
        "value": display.value,
        "label": display.label,
        "tooltip": display.tooltip or "",
        "infoLabel": display.info_label or "",
    }


def _tip_markup(display: L1Display) -> Markup:
    if display.tooltip is None:
        return Markup("")
    tip_id = f"pm-l1-tip-{next(_TIP_IDS)}"
    return Markup(
        '<span class="pm-info-tip pm-info-tip--inline">'
        '<button type="button" class="pm-info-tip__trigger" aria-expanded="false" '
        'aria-label="{aria}" aria-describedby="{tip_id}"><span aria-hidden="true">i</span></button>'
        '<span class="pm-info-tip__body" role="tooltip" id="{tip_id}">{tooltip}</span>'
        "</span>"
    ).format(aria=f"{display.info_label}: {display.label}", tip_id=tip_id, tooltip=display.tooltip)


def l1_markup(ui_lang: str | None, value: object, *, prefix: str = "") -> Markup | str:
    """Language name with the info indicator as safe markup; ``-`` for an empty value."""
    display = resolve_l1(ui_lang, value)
    if display is None:
        return "-"
    text = f"{prefix}{display.label}"
    if display.tooltip is None:
        return text
    return Markup('<span class="pm-l1">{text}{tip}</span>').format(text=text, tip=_tip_markup(display))


def l1_list_markup(ui_lang: str | None, values: Iterable[object]) -> Markup | str:
    """Comma-separated language names, each with its own info indicator; ``-`` when there are none."""
    items = [l1_markup(ui_lang, value) for value in values]
    items = [item for item in items if item != "-"]
    if not items:
        return "-"
    return Markup(", ").join(items)


__all__ = [
    "L1Display",
    "l1_client_payload",
    "l1_label",
    "l1_list_markup",
    "l1_markup",
    "resolve_l1",
]
