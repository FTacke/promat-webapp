"""Final revision of the seven Spanish topic pages after the review by Ana Goás Pérez (2026-10-28).

The German, English and Spanish editions carry the same recordings, the same co-authorship and the agreed wording.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

TOPIC_DIR = Path(__file__).resolve().parents[2] / "content" / "teaching" / "spanish"
SEVEN = ("which-pronunciation", "soft-spanish-hard-german", "europe-sounds-different", "b-or-v", "soft-consonants-b-d-g", "r", "r-am-silbenende")
CO_AUTHORED = {"soft-spanish-hard-german", "europe-sounds-different", "soft-consonants-b-d-g", "r-am-silbenende"}
LANGS = ("de", "en", "es")


def _load(slug: str, lang: str) -> dict:
    return yaml.safe_load((TOPIC_DIR / slug / f"{lang}.yaml").read_text(encoding="utf-8"))


def _cards(slug: str, lang: str) -> list[dict]:
    return [block for block in _load(slug, lang)["blocks"] if block["type"] in ("audio_contrast", "audio_examples")]


@pytest.mark.parametrize("slug", SEVEN)
def test_ana_goas_perez_is_co_author_of_exactly_four_pages_in_all_editions(slug: str) -> None:
    expected = ["felix-tacke", "ana-goas-perez"] if slug in CO_AUTHORED else ["felix-tacke"]
    for lang in LANGS:
        assert _load(slug, lang)["metadata"]["creators"] == expected, (slug, lang)


@pytest.mark.parametrize("slug", SEVEN)
def test_the_three_editions_play_the_same_recordings_in_the_same_order(slug: str) -> None:
    def signature(lang: str) -> list[tuple]:
        return [(card.get("transcript"), tuple(example.get("audio") for example in card["examples"]), tuple(example.get("role") for example in card["examples"]))
                for card in _cards(slug, lang)]

    assert signature("de") == signature("en") == signature("es"), slug


def test_new_and_replaced_comparisons_are_in_all_editions() -> None:
    expected = {
        "europe-sounds-different": ["*Europa*", "*deuda*", "*álbum*", "*sueño*", "*viuda*"],
        "soft-consonants-b-d-g": ["*vida*", "*lavar*", "*con agua*", "*el baile elegante del evento*", "*el bebedor*", "*cuidado*"],
    }
    for slug, chips in expected.items():
        for lang in LANGS:
            assert [card["transcript"] for card in _cards(slug, lang)] == chips, (slug, lang)
    album = next(card for card in _cards("europe-sounds-different", "es") if card["transcript"] == "*álbum*")
    assert [e["audio"] for e in album["examples"]] == ["marele/p7-album-ref.mp3", "corpus/p7-album-learner.mp3"]


def test_agreed_spanish_wording() -> None:
    b_or_v = (TOPIC_DIR / "b-or-v" / "es.yaml").read_text(encoding="utf-8")
    assert ("algunas personas pueden llegar a pronunciar [v] creyendo que es una forma más correcta; este es un ejemplo de *spelling pronunciation*, "
            "es decir, una pronunciación influida por la grafía.") in b_or_v
    assert "véase Tacke" not in b_or_v
    bdg = (TOPIC_DIR / "soft-consonants-b-d-g" / "es.yaml").read_text(encoding="utf-8")
    assert ("No es necesario explicar todas las reglas que determinan cuándo estas consonantes se pronuncian con o sin cierre completo: "
            "basta con reconocer y experimentar la diferencia.") in bdg
    assert "alofonía" not in bdg
    r_page = (TOPIC_DIR / "r" / "es.yaml").read_text(encoding="utf-8")
    assert "Las lenguas de herencia como recurso" in r_page and "lenguas de origen" not in r_page and "Reconocer dónde se articula la r" in r_page
    r_end = (TOPIC_DIR / "r-am-silbenende" / "es.yaml").read_text(encoding="utf-8")
    assert "sin que la punta de la lengua llegue a hacer contacto, de modo que la pronunciación se acerca a [ˈfloɐ̯]" in r_end
    assert "En alemán estándar, la *r* al final de una sílaba se vocaliza con frecuencia." in r_end
    for gone in ("Vater-Schwa", "Tiefschwa", "[zeːɐ̯]", "[ˈfaːtɐ]"):
        assert gone not in r_end, gone


@pytest.mark.parametrize("lang", LANGS)
def test_unchanged_comparisons_keep_their_recordings(lang: str) -> None:
    # barón – varón (MAR.ELE), reír on both r pages, the r-am-silbenende cards and con agua / el bebedor stay as they were
    def audio(slug: str, transcript: str) -> list[str]:
        return [e["audio"] for card in _cards(slug, lang) if card.get("transcript") == transcript for e in card["examples"]]

    assert audio("b-or-v", "*barón – varón*") == ["marele/baron-varon-ref.mp3", "marele/baron-varon-learner.mp3"]
    assert audio("r", "*reír*") == ["corpus/p2-reir-ref.mp3", "corpus/p2-reir-learner.mp3"]
    assert audio("r-am-silbenende", "*reír*") == ["corpus/p3-reir-ref.mp3", "corpus/p3-reir-learner.mp3"]
    assert [card["transcript"] for card in _cards("r-am-silbenende", lang)] == ["*flor*", "*lavar*", "*enfermo*", "*reír*"]
    assert audio("soft-consonants-b-d-g", "*el bebedor*") == ["marele/bebedor-ref.mp3", "marele/bebedor-learner.mp3"]
