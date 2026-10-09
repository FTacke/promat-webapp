"""Central L1 display: readable language names only (no ISO tooltip), ISO reference stays in the data model."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app" / "src"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app.config.data_conventions import L1_CODES, get_l1_iso_reference  # noqa: E402
from app.i18n import SUPPORTED_UI_LANGUAGES, TRANSLATIONS  # noqa: E402
from app.l1_display import l1_label, l1_list_text, l1_text, resolve_l1  # noqa: E402


@pytest.mark.parametrize("ui_lang", SUPPORTED_UI_LANGUAGES)
def test_every_l1_code_has_a_translated_name_in_every_ui_language(ui_lang: str) -> None:
    for code in L1_CODES:
        key = f"language.l1.{code}"
        assert key in TRANSLATIONS[ui_lang], f"missing {key} for {ui_lang}"
        name = TRANSLATIONS[ui_lang][key]
        assert name and name != code, f"{key} is not a readable name"


def test_names_of_newly_integrated_languages() -> None:
    expected = {
        "KAB": ("Kabylisch", "Kabyle"),
        "NMG": ("Ngumba bzw. Kwasio", "Ngumba or Kwasio"),
        "RCF": ("Réunion-Kreolisch", "Réunion Creole"),
        "DUA": ("Duala", "Duala"),
    }
    for code, (german, english) in expected.items():
        assert l1_label("de", code) == german
        assert l1_label("en", code) == english


def test_iso_reference_stays_in_the_data_model() -> None:
    assert get_l1_iso_reference("FR") == ("ISO 639-1", "fr")
    assert get_l1_iso_reference("KU") == ("ISO 639-1", "ku")
    for code in ("KAB", "NMG", "RCF", "DUA"):
        assert get_l1_iso_reference(code) == ("ISO 639-3", code.lower())
    # CZ is a historical vocabulary code; the language is registered as ISO 639-1 "cs".
    assert get_l1_iso_reference("CZ") == ("ISO 639-1", "cs")
    assert get_l1_iso_reference("unknown") is None
    assert get_l1_iso_reference("XX") is None


def test_unknown_marker_and_unresolvable_codes_stay_verbatim_without_invented_languages() -> None:
    unknown = resolve_l1("de", "unknown")
    assert unknown.label == "Unbekannt"
    odd = resolve_l1("en", "Xyz")
    assert odd.label == "Xyz" and odd.value == "Xyz" and not odd.resolved
    assert l1_text("en", "Xyz") == "Xyz"
    assert l1_label("en", None) == "" and l1_text("de", None) == "-" and l1_text("de", "  ") == "-"


def test_display_is_plain_text_without_iso_code_tooltip_or_info_indicator() -> None:
    for ui_lang in SUPPORTED_UI_LANGUAGES:
        for code in L1_CODES:
            for text in (l1_label(ui_lang, code), l1_text(ui_lang, code)):
                assert isinstance(text, str) and "<" not in text and "ISO" not in text
    assert l1_text("de", "KAB") == "Kabylisch"
    assert l1_text("de", "<script>alert(1)</script>") == "<script>alert(1)</script>"  # plain text; templates escape it
    assert not hasattr(resolve_l1("de", "KAB"), "tooltip")


def test_iso_tooltip_translation_keys_are_gone() -> None:
    for ui_lang in SUPPORTED_UI_LANGUAGES:
        assert "language.l1.tooltip" not in TRANSLATIONS[ui_lang]
        assert "language.l1.info_label" not in TRANSLATIONS[ui_lang]


def test_list_text_lists_each_language_by_name() -> None:
    assert l1_list_text("en", ("IT", "EN")) == "Italian, English"
    assert l1_list_text("de", ("IT", "EN")) == "Italienisch, Englisch"
    assert l1_list_text("en", ()) == "-"


def test_resolution_keeps_the_stored_code_for_filtering() -> None:
    display = resolve_l1("de", "kab")
    assert display.value == "KAB" and display.label == "Kabylisch" and display.resolved
