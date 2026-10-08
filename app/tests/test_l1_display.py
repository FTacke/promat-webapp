"""Central L1 display: readable language names, ISO standard of each code, verbatim fallback for unknown codes."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from markupsafe import Markup

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app" / "src"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app.config.data_conventions import L1_CODES, get_l1_iso_reference  # noqa: E402
from app.i18n import SUPPORTED_UI_LANGUAGES, TRANSLATIONS  # noqa: E402
from app.l1_display import l1_client_payload, l1_label, l1_list_markup, l1_markup, resolve_l1  # noqa: E402


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


def test_iso_standard_follows_the_code_not_a_blanket_label() -> None:
    assert get_l1_iso_reference("FR") == ("ISO 639-1", "fr")
    assert get_l1_iso_reference("KU") == ("ISO 639-1", "ku")
    for code in ("KAB", "NMG", "RCF", "DUA"):
        assert get_l1_iso_reference(code) == ("ISO 639-3", code.lower())
    # CZ is a historical vocabulary code; the language is registered as ISO 639-1 "cs".
    assert get_l1_iso_reference("CZ") == ("ISO 639-1", "cs")
    assert get_l1_iso_reference("unknown") is None
    assert get_l1_iso_reference("XX") is None


def test_tooltip_names_the_actual_standard_and_code() -> None:
    assert resolve_l1("en", "RCF").tooltip == "ISO 639-3: rcf"
    assert resolve_l1("de", "rcf").tooltip == "ISO 639-3: rcf"
    assert resolve_l1("de", "FR").tooltip == "ISO 639-1: fr"
    assert resolve_l1("de", "CZ").tooltip == "ISO 639-1: cs"


def test_unknown_marker_and_unresolvable_codes_stay_verbatim_without_invented_languages() -> None:
    unknown = resolve_l1("de", "unknown")
    assert unknown.label == "Unbekannt" and unknown.tooltip is None
    odd = resolve_l1("en", "Xyz")
    assert odd.label == "Xyz" and odd.tooltip is None and odd.info_label is None
    assert l1_markup("en", "Xyz") == "Xyz"
    assert l1_label("en", None) == "" and l1_markup("de", None) == "-" and l1_markup("de", "  ") == "-"


def test_markup_escapes_untrusted_values_and_links_trigger_to_tooltip() -> None:
    # Unresolvable values come back as plain text, so templates escape them; mixed into markup they are escaped too.
    hostile = l1_markup("de", '<script>alert(1)</script>')
    assert not isinstance(hostile, Markup)
    assert "<script>" not in str(Markup.escape(hostile))
    assert "<script>" not in str(l1_list_markup("de", ["<script>alert(1)</script>", "FR"]))

    markup = l1_markup("de", "KAB")
    assert isinstance(markup, Markup)
    html = str(markup)
    assert html.startswith('<span class="pm-l1">Kabylisch')
    assert 'role="tooltip"' in html and "ISO 639-3: kab" in html
    assert 'aria-label="ISO-Sprachcode anzeigen: Kabylisch"' in html
    assert ">KAB<" not in html  # no permanently visible technical code next to the name


def test_tooltip_ids_are_unique_per_rendered_indicator() -> None:
    first, second = str(l1_markup("en", "FR")), str(l1_markup("en", "FR"))
    first_id = first.split('aria-describedby="')[1].split('"')[0]
    second_id = second.split('aria-describedby="')[1].split('"')[0]
    assert first_id != second_id


def test_list_markup_lists_each_language_by_name() -> None:
    html = str(l1_list_markup("en", ("IT", "EN")))
    assert "Italian" in html and "English" in html and "ISO 639-1: it" in html and "ISO 639-1: en" in html
    assert l1_list_markup("en", ()) == "-"


def test_client_payload_keeps_the_stored_code_for_filtering() -> None:
    payload = l1_client_payload("de", "KAB")
    assert payload == {"value": "KAB", "label": "Kabylisch", "tooltip": "ISO 639-3: kab", "infoLabel": "ISO-Sprachcode anzeigen"}
    assert l1_client_payload("de", None)["label"] == ""
