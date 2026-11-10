"""French topic page "Die Liaison" (Janina Reinhardt, draft of 2026-11-10) in DE, EN and the French content edition."""

from __future__ import annotations

import html as html_module
from pathlib import Path
import re
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from test_teaching_content_editions import BASE_URL, _app, _canonical, _edition_links, _hreflang  # noqa: E402
import teaching_audio_slots as slots  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
TOPIC = REPO_ROOT / "content" / "teaching" / "french" / "liaison"
EDITIONS = {"de": "/de/teaching/french/liaison", "en": "/en/teaching/french/liaison", "fr": "/de/teaching/french/fr/liaison?from=de"}
CARDS = ["*des pâtes – des heures*", "*ils ont – ils sont*", "*Blanche-Neige et les onze poissons bleus*", "*Il était huit heures*", "*huit*", "*vers neuf heures*"]
AUDIO = ["corpus/fr1-des-pates.mp3", "corpus/fr1-des-heures.mp3", "corpus/fr1-z-des-heures.mp3", "corpus/fr1-t-est-allee.mp3", "corpus/fr1-n-un-aspect.mp3",
         "corpus/fr1-ils-ont.mp3", "corpus/fr1-ils-sont.mp3", "corpus/fr1-les-onze.mp3", "corpus/fr1-huit-heures.mp3", "corpus/fr1-huit.mp3", "corpus/fr1-neuf-heures.mp3"]


@pytest.fixture(scope="module")
def client():
    from app import teaching_content

    teaching_content.clear_teaching_content_caches()
    return _app().test_client()


def _load(lang: str) -> dict:
    return yaml.safe_load((TOPIC / f"{lang}.yaml").read_text(encoding="utf-8"))


def _audio(lang: str) -> list[str]:
    return [e["audio"] for b in _load(lang)["blocks"] if b["type"] in ("audio_contrast", "audio_examples") for e in b["examples"]]


@pytest.mark.parametrize("lang", ["de", "en", "fr"])
def test_three_editions_share_structure_audio_and_authorship(lang: str) -> None:
    page = _load(lang)
    assert page["resource_id"] == "promat-teaching-fr-liaison" and page["metadata"]["creators"] == ["janina-reinhardt"]
    assert [b["type"] for b in page["blocks"]] == [b["type"] for b in _load("de")["blocks"]]
    assert _audio(lang) == AUDIO
    assert [b["transcript"] for b in page["blocks"] if b["type"] == "audio_contrast"] == CARDS
    assert len(next(b for b in page["blocks"] if b["type"] == "teaching_impulses")["items"]) == 3
    assert not [b for b in page["blocks"] if b["type"] in ("citation", "hero")]  # no typed citation, no second title


def test_titles_and_teasers() -> None:
    assert _load("de")["title"] == "Die Liaison: Wenn stumme Konsonanten hörbar werden"
    assert _load("de")["summary"] == "Warum in *les amis* ein [z]-Laut zu hören ist – und wann Wörter im Französischen auf diese Weise verbunden werden."
    assert _load("fr")["title"] == "La liaison : quand les consonnes muettes se font entendre"
    assert _load("en")["title"] == "Liaison: when silent consonants become audible"


def test_editorial_decisions_in_the_german_master() -> None:
    text = (TOPIC / "de.yaml").read_text(encoding="utf-8")
    # liaison and enchaînement are distinguished; the Pustka quotation is replaced by an own definition (the book stays in Vertiefung)
    assert "Davon zu unterscheiden ist das *enchaînement*" in text and "Pustka 2026, S. 159" not in text and "Pustka (2026)" in text
    # ils ont is played first and resolved first (the draft listed the files in the opposite order)
    assert "In der ersten Aufnahme ist *ils‿ont*" in text and "In der zweiten Aufnahme ist *ils sont*" in text
    # numerals: no blanket rules
    for blanket in ("grundsätzlich die Liaison", "grundsätzlich keine Liaison"):
        assert blanket not in text
    assert "Nach vielen Zahlwörtern" in text and "in der Regel nicht gebunden" in text
    # huit and neuf are explained as special cases, not as ordinary liaison
    assert "Das ist ein *enchaînement*, keine Liaison im engeren Sinn." in text and "Streng genommen ist auch das keine gewöhnliche Liaison" in text
    for draft_note in ("#Wortliste", "#Satzliste", "[Hörbeispiel", "verlinken?", "forvo", "Themenseite 2", "Autorin:", "Erstellt:"):
        assert draft_note not in text, draft_note


def test_audio_registry_releases_and_provenance() -> None:
    slots.configure("french")
    try:
        data = slots.load_slots()
        assert slots.check(data) == []
        recordings = {r["file"]: (r["session_id"], r["item"]["id"], r["category"]) for _c, r in slots.iter_recordings(data)}
        assert recordings == {
            "corpus/fr1-des-pates.mp3": ("FR-N-0001-2026-S01", "wl_055", "reference"),
            "corpus/fr1-des-heures.mp3": ("FR-N-0001-2026-S01", "t_54", "reference"),
            "corpus/fr1-z-des-heures.mp3": ("FR-N-0001-2026-S01", "t_50", "reference"),
            "corpus/fr1-t-est-allee.mp3": ("FR-N-0001-2026-S01", "t_04", "reference"),
            "corpus/fr1-n-un-aspect.mp3": ("FR-N-0001-2026-S01", "t_33", "reference"),
            "corpus/fr1-ils-ont.mp3": ("FR-N-0001-2026-S01", "wl_045", "reference"),
            "corpus/fr1-ils-sont.mp3": ("FR-N-0001-2026-S01", "wl_009", "reference"),
            "corpus/fr1-les-onze.mp3": ("FR-N-0001-2026-S01", "t_05", "reference"),
            "corpus/fr1-huit-heures.mp3": ("FR-N-0002-2026-S01", "t_22", "reference"),  # the speaker named in the draft
            "corpus/fr1-huit.mp3": ("FR-N-0001-2026-S01", "wl_058", "reference"),
            "corpus/fr1-neuf-heures.mp3": ("FR-N-0001-2026-S01", "t_43", "reference"),
        }
        on_disk = sorted(f"corpus/{p.name}" for p in (TOPIC / "media" / "audio" / "corpus").glob("*.mp3"))
        assert on_disk == sorted(recordings)
        sessions_root = REPO_ROOT / "data" / "sessions"
        if slots.runtime_available(sessions_root):
            assert slots.check(data, sessions_root) == []
            assert all(row["result"] == "OK" and row["consent"] == "yes" for row in slots.release_rows(data, sessions_root))
    finally:
        slots.configure("spanish")
    assert slots.load_slots()["comparisons"][0]["topic"] != "liaison"  # the Spanish registry is untouched


@pytest.mark.parametrize("edition", list(EDITIONS))
def test_pages_render_with_working_players_and_localised_labels(client, edition: str) -> None:
    response = client.get(EDITIONS[edition])
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for file in AUDIO:
        assert f"/teaching-media/french/liaison/audio/{file}" in html, file
    assert client.get(f"/teaching-media/french/liaison/audio/{AUDIO[0]}").status_code == 200
    content = html[html.index('<h1 id="promat-page-title"'):html.index("pm-teaching-topic-bottom-nav")]
    labels = {"de": ("Referenzsprecher:in", "Auflösung ausblenden", "Diese Themenseite zitieren", "Autor:innen"),
              "en": ("Reference speaker", "Hide solution", "Cite this topic page", "Authors"),
              "fr": ("Voix de référence", "Masquer la solution", "Citer cette page thématique", "Rédaction")}[edition]
    for label in labels:
        assert label in content, label
    if edition == "fr":
        for foreign in ("Referenzsprecher", "Reference speaker", "Wortfolge", "Word sequence", "Auflösung", "Show solution", "Autor:innen", "zitieren"):
            assert foreign not in content, foreign
        assert re.search(r'<article [^>]*lang="fr"', html)
    citation = html_module.unescape(re.search(r'data-copy-text="([^"]*)"', html).group(1))
    assert citation.startswith("Reinhardt, Janina (2026).") and "Felix Tacke (" in citation and "Goás" not in citation


def test_french_edition_links_return_navigation_and_metadata(client) -> None:
    for ui_lang in ("de", "en"):
        html = client.get(f"/{ui_lang}/teaching/french/liaison").get_data(as_text=True)
        assert _edition_links(html) == [(f"/{ui_lang}/teaching/french/fr/liaison?from={ui_lang}", "fr", "En français")]
        assert [lang for lang, _href in _hreflang(html)] == ["de", "en", "fr"]
        hub = client.get(f"/{ui_lang}/teaching/french").get_data(as_text=True)
        assert _edition_links(hub) == [(f"/{ui_lang}/teaching/french/fr?from={ui_lang}", "fr", "En français")]
    html = client.get("/en/teaching/french/fr/liaison?from=de").get_data(as_text=True)
    assert _edition_links(html) == [("/de/teaching/french/liaison", "de", "Auf Deutsch")]
    assert _canonical(html) == f"{BASE_URL}/de/teaching/french/fr/liaison"
    direct = client.get("/en/teaching/french/fr/liaison").get_data(as_text=True)
    assert _edition_links(direct) == [("/en/teaching/french/liaison", "en", "In English")]
    switch = dict((code, html_module.unescape(href)) for href, code in re.findall(r'<a href="([^"]+)"\s+data-ui-lang-link="([a-z]+)"', html))
    assert switch["de"] == "/de/teaching/french/fr/liaison?from=de&lang=de"  # the DE/EN switch keeps the French content
    fr_hub = client.get("/de/teaching/french/fr?from=de").get_data(as_text=True)
    assert "Comprendre la prononciation du français" in fr_hub and "La liaison" in fr_hub
    assert re.findall(r'href="/de/teaching/french/fr/([a-z0-9-]+)\?from=de"', fr_hub) == ["liaison"]
