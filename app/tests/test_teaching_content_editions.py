"""Additional Teaching content editions (``content_editions`` in ``teaching.yaml``, e.g. ``es`` or ``fr``).

UI language and content language are independent: ``/{ui_lang}/...`` and ``?lang=`` keep steering the platform
navigation, a content edition lives under ``/{ui_lang}/teaching/{teaching_lang}/{content_lang}[/{topic}]`` and is only
linked, listed, indexed and served once it is published (docs/spec/platform-data-files.md, "Teaching content editions").
"""

from __future__ import annotations

import html as html_module
import importlib.util
import os
from pathlib import Path
import re
import sys

import pytest
from flask import Flask, g


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app import register_context_processors  # noqa: E402
from app.routes.auth import blueprint as auth_blueprint  # noqa: E402
from app.routes.public import blueprint as public_blueprint  # noqa: E402
from app import teaching_content  # noqa: E402

BASE_URL = "https://pronunciation-matters.de"


def _app() -> Flask:
    app_root = Path(__file__).resolve().parents[1]
    app = Flask(__name__, template_folder=str(app_root / "templates"), static_folder=str(app_root / "static"))
    register_context_processors(app)

    @app.before_request
    def _anonymous() -> None:
        g.user = None
        g.user_id = None
        g.role = None

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(public_blueprint)
    return app


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _topic(title: str, *, extra: str = "", equivalents: str = "") -> str:
    return (
        f"resource_id: promat-teaching-test-topic-one\ntitle: '{title}'\nsummary: Summary of {title}.\n"
        f"{equivalents}metadata:\n  creators:\n  - felix-tacke\n  created: 2026-10-01\n  updated: 2026-10-20\n{extra}"
        "blocks:\n- type: topic_meta\n- type: text\n  body: Body text.\n"
    )


def _language(root: Path, teaching_lang: str, *, editions: tuple[str, ...], files: dict[str, str]) -> None:
    content = root / "content" / "teaching" / teaching_lang
    manifest = f"teaching_lang: {teaching_lang}\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n  - en\n"
    if editions:
        manifest += "content_editions:\n" + "".join(f"  - {code}\n" for code in editions)
    _write(content / "teaching.yaml", manifest)
    for relative, text in files.items():
        _write(content / relative, text)


def _hub(title: str, *slugs: str) -> str:
    return f"title: '{title}'\ngroups:\n  - title: Group\n    topics:\n" + "".join(f"      - {slug}\n" for slug in slugs)


def _base_spanish(**extra_files: str) -> dict[str, str]:
    files = {
        "hubs/de.yaml": _hub("Spanisch: Themenseiten", "topic-one", "topic-two"),
        "hubs/en.yaml": _hub("Spanish: Topic pages", "topic-one", "topic-two"),
        "topic-one/de.yaml": _topic("Thema eins", equivalents="equivalents:\n  en: topic-one\n"),
        "topic-one/en.yaml": _topic("Topic one", equivalents="equivalents:\n  de: topic-one\n"),
        "topic-two/de.yaml": _topic("Thema zwei").replace("topic-one", "topic-two"),
        "topic-two/en.yaml": _topic("Topic two").replace("topic-one", "topic-two"),
    }
    files.update(extra_files)
    return files


@pytest.fixture
def make_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(teaching_content, "TEACHING_CONTENT_ROOT", tmp_path / "content" / "teaching")

    def factory(language_files: dict[str, tuple[tuple[str, ...], dict[str, str]]]):
        for teaching_lang, (editions, files) in language_files.items():
            _language(tmp_path, teaching_lang, editions=editions, files=files)
        teaching_content.clear_teaching_content_caches()
        return _app().test_client()

    yield factory
    teaching_content.clear_teaching_content_caches()


def _get(client, url: str) -> tuple[int, str]:
    response = client.get(url)
    return response.status_code, response.get_data(as_text=True)


def _edition_links(html: str) -> list[tuple[str, str, str]]:
    """(href, lang, label) of the content-edition links opposite the back link."""
    nav = re.search(r'<nav class="pm-content-edition-links"[^>]*>(.*?)</nav>', html, re.S)
    if not nav:
        return []
    return [
        (html_module.unescape(href), lang, label)
        for href, lang, label in re.findall(
            r'<a class="pm-content-edition-links__link" href="([^"]+)" lang="([a-z]+)" hreflang="[a-z]+">.*?'
            r'pm-content-edition-links__label">([^<]+)</span>',
            nav.group(1),
            re.S,
        )
    ]


def _hreflang(html: str) -> list[tuple[str, str]]:
    return re.findall(r'<link rel="alternate" hreflang="([a-z]+)" href="([^"]+)">', html)


def _canonical(html: str) -> str:
    return re.search(r'<link rel="canonical" href="([^"]+)">', html).group(1)


# --- nothing is visible before an edition is published -----------------------------------------------------------


def test_declared_edition_without_files_is_invisible_and_not_served(make_client) -> None:
    client = make_client({"spanish": (("es",), _base_spanish())})
    for url in ("/de/teaching/spanish/topic-one", "/en/teaching/spanish", "/de/teaching/spanish"):
        status, html = _get(client, url)
        assert status == 200 and _edition_links(html) == [] and "pm-content-header__nav-row" not in html, url
        assert all(lang in ("de", "en") for lang, _href in _hreflang(html)), url
    for url in ("/de/teaching/spanish/es", "/en/teaching/spanish/es", "/de/teaching/spanish/es/topic-one", "/en/teaching/spanish/es/topic-one?from=de"):
        assert client.get(url).status_code == 404, url


def test_draft_edition_files_stay_unpublished(make_client) -> None:
    client = make_client({"spanish": (("es",), _base_spanish(**{
        "hubs/es.yaml": "status: draft\n" + _hub("Español: páginas temáticas", "topic-one"),
        "topic-one/es.yaml": _topic("Tema uno", extra="status: draft\n"),
    }))})
    assert client.get("/de/teaching/spanish/es/topic-one").status_code == 404
    assert client.get("/de/teaching/spanish/es").status_code == 404
    status, html = _get(client, "/de/teaching/spanish/topic-one")
    assert status == 200 and _edition_links(html) == [] and "/es/" not in "".join(href for _lang, href in _hreflang(html))


def test_an_edition_of_an_unpublished_topic_is_not_served(make_client) -> None:
    files = _base_spanish(**{"topic-one/es.yaml": _topic("Tema uno")})
    files["topic-one/de.yaml"] = _topic("Thema eins", extra="status: draft\n")
    files["topic-one/en.yaml"] = _topic("Topic one", extra="status: draft\n")
    client = make_client({"spanish": (("es",), files)})
    assert client.get("/de/teaching/spanish/es/topic-one").status_code == 404


def test_undeclared_language_files_are_never_served(make_client) -> None:
    client = make_client({"spanish": (("es",), _base_spanish(**{"topic-one/fr.yaml": _topic("Sujet un"), "hubs/fr.yaml": _hub("Espagnol", "topic-one")}))})
    for url in ("/de/teaching/spanish/fr/topic-one", "/de/teaching/spanish/fr"):
        assert client.get(url).status_code == 404, url


# --- published edition: links, routing, return navigation -------------------------------------------------------


@pytest.fixture
def published(make_client):
    return make_client({"spanish": (("es",), _base_spanish(**{
        "hubs/es.yaml": _hub("Español: páginas temáticas", "topic-one", "topic-two"),
        "topic-one/es.yaml": _topic("Tema uno"),
    }))})


@pytest.mark.parametrize("ui_lang", ["de", "en"])
def test_published_edition_is_linked_from_the_same_place_on_hub_and_topic(published, ui_lang: str) -> None:
    status, topic_html = _get(published, f"/{ui_lang}/teaching/spanish/topic-one")
    assert status == 200 and _edition_links(topic_html) == [(f"/{ui_lang}/teaching/spanish/es/topic-one?from={ui_lang}", "es", "En español")]
    status, hub_html = _get(published, f"/{ui_lang}/teaching/spanish")
    assert status == 200 and _edition_links(hub_html) == [(f"/{ui_lang}/teaching/spanish/es?from={ui_lang}", "es", "En español")]
    # the link sits in the header row, opposite the back link and before the title
    for html in (topic_html, hub_html):
        row = html.index("pm-content-header__nav-row")
        assert row < html.index("pm-content-header__back") < html.index("pm-content-edition-links") < html.index("promat-page__title")
    # a topic without a published translation has no link
    status, html = _get(published, f"/{ui_lang}/teaching/spanish/topic-two")
    assert status == 200 and _edition_links(html) == []


@pytest.mark.parametrize(("ui_lang", "origin", "label", "target"), [
    ("de", "de", "Auf Deutsch", "/de/teaching/spanish/topic-one"),
    ("en", "en", "In English", "/en/teaching/spanish/topic-one"),
    ("en", "de", "Auf Deutsch", "/de/teaching/spanish/topic-one"),  # switched the UI to EN after coming from DE
    ("de", "en", "In English", "/en/teaching/spanish/topic-one"),
])
def test_edition_topic_returns_to_the_edition_the_reader_came_from(published, ui_lang: str, origin: str, label: str, target: str) -> None:
    status, html = _get(published, f"/{ui_lang}/teaching/spanish/es/topic-one?from={origin}")
    assert status == 200
    assert _edition_links(html) == [(target, origin, label)]
    # content in Spanish, platform navigation in the UI language
    assert f'<html lang="{ui_lang}"' in html and 'data-content-lang="es"' in html and re.search(r'<article [^>]*lang="es"', html)
    assert "Tema uno" in html and f'pm-content-header__nav-row" lang="{ui_lang}"' in html
    # back to the hub of the same edition, carrying the origin
    assert f'href="/{ui_lang}/teaching/spanish/es?from={origin}"' in html


@pytest.mark.parametrize("ui_lang", ["de", "en"])
def test_direct_visit_returns_to_the_current_ui_language(published, ui_lang: str) -> None:
    label = "Auf Deutsch" if ui_lang == "de" else "In English"
    status, html = _get(published, f"/{ui_lang}/teaching/spanish/es/topic-one")
    assert status == 200 and _edition_links(html) == [(f"/{ui_lang}/teaching/spanish/topic-one", ui_lang, label)]


@pytest.mark.parametrize("bad", ["https://evil.example/", "//evil.example", "es", "xx", "/de/teaching", "de%0d%0aSet-Cookie:x"])
def test_origin_is_validated_and_never_used_as_a_url(published, bad: str) -> None:
    status, html = _get(published, f"/en/teaching/spanish/es/topic-one?from={bad}")
    assert status == 200
    assert _edition_links(html) == [("/en/teaching/spanish/topic-one", "en", "In English")]
    # neither the return link, the edition's own links, the UI switch nor its meta hook echo the value
    # (the login link's `next` keeps the encoded request URL on every page; that is the existing return-target flow)
    assert '<meta name="promat-ui-switch-params" content="from=en">' in html
    assert _switch_links(html)["de"] == "/de/teaching/spanish/es/topic-one?from=en&lang=de"
    assert 'href="/en/teaching/spanish/es?from=en"' in html


def test_edition_hub_lists_only_published_translations_and_keeps_the_origin(published) -> None:
    status, html = _get(published, "/en/teaching/spanish/es?from=de")
    assert status == 200 and "Español: páginas temáticas" in html
    assert 'href="/en/teaching/spanish/es/topic-one?from=de"' in html
    assert "topic-two" not in html.split("pm-teaching-group-stack")[1]  # no untranslated placeholder card
    assert _edition_links(html) == [("/de/teaching/spanish", "de", "Auf Deutsch")]


# --- global DE/EN switch keeps the content edition ----------------------------------------------------------------


def _switch_links(html: str) -> dict[str, str]:
    return {code: html_module.unescape(href) for href, code in re.findall(r'<a href="([^"]+)"\s+data-ui-lang-link="([a-z]+)"', html)}


def test_ui_switch_keeps_the_spanish_content_and_the_origin(published) -> None:
    _status, html = _get(published, "/de/teaching/spanish/es/topic-one?from=de")
    assert _switch_links(html)["en"] == "/en/teaching/spanish/es/topic-one?from=de&lang=en"
    assert '<meta name="promat-ui-switch-params" content="from=de">' in html
    # a direct visit has no origin yet: the switch records the edition of the current UI language
    _status, html = _get(published, "/de/teaching/spanish/es/topic-one")
    assert _switch_links(html)["en"] == "/en/teaching/spanish/es/topic-one?from=de&lang=en"
    _status, html = _get(published, "/en/teaching/spanish/es?from=en")
    assert _switch_links(html)["de"] == "/de/teaching/spanish/es?from=en&lang=de"
    # after switching, the page still shows the Spanish text and still returns to German
    status, html = _get(published, "/en/teaching/spanish/es/topic-one?from=de&lang=en")
    assert status == 200 and "Tema uno" in html and _edition_links(html)[0][2] == "Auf Deutsch"


def test_ui_switch_of_german_and_english_pages_is_unchanged(published) -> None:
    _status, html = _get(published, "/de/teaching/spanish/topic-one?lang=de")
    assert _switch_links(html) == {"de": "/de/teaching/spanish/topic-one?lang=de", "en": "/en/teaching/spanish/topic-one?lang=en"}
    assert "promat-ui-switch-params" not in html


# --- metadata: canonical, hreflang, citation ----------------------------------------------------------------------


@pytest.mark.parametrize("ui_lang", ["de", "en"])
def test_edition_has_one_canonical_and_reciprocal_hreflang(published, ui_lang: str) -> None:
    canonical_es = f"{BASE_URL}/de/teaching/spanish/es/topic-one"
    _status, html = _get(published, f"/{ui_lang}/teaching/spanish/es/topic-one?from=de")
    assert _canonical(html) == canonical_es  # same canonical whatever the navigation language
    expected = [("de", f"{BASE_URL}/de/teaching/spanish/topic-one"), ("en", f"{BASE_URL}/en/teaching/spanish/topic-one"), ("es", canonical_es)]
    assert _hreflang(html) == expected
    _status, base_html = _get(published, f"/{ui_lang}/teaching/spanish/topic-one")
    assert _hreflang(base_html) == expected and _canonical(base_html) == f"{BASE_URL}/{ui_lang}/teaching/spanish/topic-one"
    # a topic without a translation keeps its DE/EN pair only
    _status, html_two = _get(published, f"/{ui_lang}/teaching/spanish/topic-two")
    assert [lang for lang, _href in _hreflang(html_two)] == ["de", "en"]
    _status, hub_html = _get(published, f"/{ui_lang}/teaching/spanish/es")
    assert _canonical(hub_html) == f"{BASE_URL}/de/teaching/spanish/es" and [lang for lang, _href in _hreflang(hub_html)] == ["de", "en", "es"]


def test_edition_citation_and_json_ld_keep_the_publication_identity(published) -> None:
    _status, html = _get(published, "/en/teaching/spanish/es/topic-one")
    assert '"identifier":"promat-teaching-test-topic-one"' in html and '"inLanguage":"es"' in html
    assert f'"url":"{BASE_URL}/de/teaching/spanish/es/topic-one"' in html
    assert re.search(r"Tacke, Felix \(2026\)\. .Tema uno.\. In: Felix Tacke", html)
    assert f"{BASE_URL}/de/teaching/spanish/es/topic-one</a>" in html
    _status, base = _get(published, "/de/teaching/spanish/topic-one")
    assert '"identifier":"promat-teaching-test-topic-one"' in base and '"inLanguage":"de"' in base


# --- the same mechanism for French ---------------------------------------------------------------------------------


def test_french_teaching_resources_use_the_same_mechanism(make_client) -> None:
    files = {
        "hubs/de.yaml": _hub("Französisch: Themenseiten", "liaison"),
        "hubs/en.yaml": _hub("French: Topic pages", "liaison"),
        "liaison/de.yaml": _topic("Die Liaison").replace("promat-teaching-test-topic-one", "promat-teaching-fr-liaison"),
        "liaison/en.yaml": _topic("Liaison").replace("promat-teaching-test-topic-one", "promat-teaching-fr-liaison"),
        "liaison/fr.yaml": _topic("La liaison").replace("promat-teaching-test-topic-one", "promat-teaching-fr-liaison"),
    }
    client = make_client({"french": (("fr",), files), "spanish": (("es",), _base_spanish())})
    status, html = _get(client, "/en/teaching/french/liaison")
    assert status == 200 and _edition_links(html) == [("/en/teaching/french/fr/liaison?from=en", "fr", "En français")]
    status, html = _get(client, "/de/teaching/french/fr/liaison?from=en")
    assert status == 200 and "La liaison" in html and _edition_links(html) == [("/en/teaching/french/liaison", "en", "In English")]
    assert re.search(r'<article [^>]*lang="fr"', html)
    assert client.get("/de/teaching/french/fr").status_code == 404  # no French-language hub published yet
    assert client.get("/de/teaching/spanish/fr/liaison").status_code == 404  # editions are declared per teaching language


# --- the real repository ----------------------------------------------------------------------------------------


def test_repository_declares_spanish_edition_but_publishes_nothing_yet() -> None:
    teaching_content.clear_teaching_content_caches()
    assert teaching_content.content_edition_codes("spanish") == ["es"]
    assert teaching_content.content_edition_codes("french") == []
    assert not list((REPO_ROOT / "content" / "teaching").glob("*/*/es.yaml")) and not list((REPO_ROOT / "content" / "teaching").glob("*/*/fr.yaml"))
    client = _app().test_client()
    for ui_lang in ("de", "en"):
        for path in ("", "/soft-spanish-hard-german", "/b-or-v"):
            status, html = _get(client, f"/{ui_lang}/teaching/spanish{path}")
            assert status == 200 and "pm-content-edition-links" not in html and "En español" not in html
            assert [lang for lang, _href in _hreflang(html)] == ["de", "en"]
        assert client.get(f"/{ui_lang}/teaching/spanish/es").status_code == 404
        assert client.get(f"/{ui_lang}/teaching/spanish/es/soft-spanish-hard-german").status_code == 404


# --- content validation ------------------------------------------------------------------------------------------


@pytest.fixture
def validator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("validate_teaching_content_editions", REPO_ROOT / "scripts" / "validate_teaching_content.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CONTENT_ROOT", tmp_path / "content" / "teaching")
    return module


def _validate(validator, tmp_path: Path, editions: tuple[str, ...], files: dict[str, str], teaching_lang: str = "spanish") -> list[str]:
    _language(tmp_path, teaching_lang, editions=editions, files=files)
    errors: list[str] = []
    manifest = validator._load_yaml_map(validator.CONTENT_ROOT / teaching_lang / "teaching.yaml")
    validator.validate_content_editions(errors, teaching_lang, manifest, ["de", "en"])
    return errors


def test_validator_accepts_a_consistent_edition(validator, tmp_path: Path) -> None:
    assert _validate(validator, tmp_path, ("es",), _base_spanish(**{"topic-one/es.yaml": _topic("Tema uno"), "hubs/es.yaml": _hub("Español", "topic-one")})) == []


def test_validator_rejects_inconsistent_editions(validator, tmp_path: Path) -> None:
    files = _base_spanish(**{
        "topic-two/es.yaml": _topic("Tema dos").replace("felix-tacke", "janina-reinhardt"),  # other resource id and creators
        "topic-one/fr.yaml": _topic("Sujet un"),  # undeclared edition
        "hubs/es.yaml": _hub("Español", "topic-one"),  # lists a topic without es.yaml
        "es/de.yaml": _topic("Kollision").replace("topic-one", "es"),  # topic slug equal to the edition code
    })
    errors = "\n".join(_validate(validator, tmp_path, ("es", "de", "es", "spa"), files))
    for expected in (
        "content edition 'de' is a UI language",
        "content edition 'es' is listed twice",
        "content edition 'spa' must be a two-letter",
        "topic-one/fr.yaml: language file of an undeclared content edition",
        "lists 'topic-one', which has no es.yaml",
        "a topic slug must not equal the content edition code 'es'",
        "spanish/topic-two/es: resource_id must be the one of the topic",
        "spanish/topic-two/es: metadata.creators must be the same people",
    ):
        assert expected in errors, expected
