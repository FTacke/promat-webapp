"""Template-facing branding source of truth.

This module is the single authority for app identity values rendered through
templates: display names, title formatting, external brand links, contact
details, and static asset filenames used by the shell.
"""

from __future__ import annotations


BRANDING: dict[str, str] = {
    "app_display_name": "Pronunciation Matters",
    "app_short_name": "PROMAT",
    "app_tagline": "Ruhige Forschungs- und Unterrichtsplattform für Aussprache, Vergleich und Materialien.",
    "page_title_separator": "·",
    "app_meta_description": (
        "Pronunciation Matters ordnet Projektkommunikation, Forschung und Unterricht "
        "in einer textzentrierten PROMAT-Oberfläche."
    ),
    "institution_name": "Philipps-Universität Marburg",
    "institution_contact_email": "felix.tacke@uni-marburg.de",
    "footer_brand_url": "https://www.uni-marburg.de/",
    "footer_brand_label": "Philipps-Universität Marburg",
    "footer_brand_badge_alt": "Philipps-Universität Marburg",
    "footer_brand_badge_asset": "img/promat-mark.svg",
    "footer_meta_year": "2026",
    "footer_partner_label": "Hispanistica @ Marburg",
    "footer_partner_url": "https://hispanistica.com",
    "project_url": "https://example.invalid/promat",
    "contact_email": "felix.tacke@uni-marburg.de",
    "footer_copyright_holder": "Felix Tacke",
    "app_logo_alt": "Pronunciation Matters",
    "footer_logo_alt": "Pronunciation Matters",
    "favicon_asset": "img/promat_favicon.png",
    "footer_logo_asset": "img/promat-mark.svg",
    "drawer_logo_light_asset": "img/promat.png",
    "drawer_logo_dark_asset": "img/promat.png",
    "landing_logo_light_asset": "img/promat-wordmark-light.svg",
    "landing_logo_dark_asset": "img/promat-wordmark-dark.svg",
}


def format_page_title(page_label: str | None = None) -> str:
    """Return a consistently formatted document title."""
    normalized_label = (page_label or "").strip()
    if not normalized_label:
        return BRANDING["app_display_name"]
    return f"{normalized_label} {BRANDING['page_title_separator']} {BRANDING['app_display_name']}"
