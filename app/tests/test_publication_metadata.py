"""Publication metadata architecture (Run 4): registry, resource identity, head metadata, JSON-LD and citations.

Contract: ``docs/spec/platform-data-files.md, "Publication Metadata"``.
"""

from __future__ import annotations

import html as html_module
import json
import os
from pathlib import Path
import re
import sys

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app" / "src"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app import publication, teaching_content  # noqa: E402

ORIGIN = "https://pronunciation-matters.de"
PLATFORM_TITLE = "Pronunciation Matters: A Multilingual Platform for Learner Pronunciation Research and Teaching"
PUBLISHER = "Philipps-Universität Marburg"

#: representative public pages: (path, expected canonical path)
PUBLIC_PAGES = [
    ("/de", "/de"),
    ("/en", "/en"),
    ("/de/project", "/de/project/about"),
    ("/en/project/team", "/en/project/team"),
    ("/de/research", "/de/research"),
    ("/de/research/spanish", "/de/research/spanish"),
    ("/en/research/french", "/en/research/french"),
    ("/de/research/spanish/design", "/de/research/spanish/design"),
    ("/de/teaching", "/de/teaching"),
    ("/de/teaching/spanish", "/de/teaching/spanish"),
    ("/en/teaching/french", "/en/teaching/french"),
    ("/de/teaching/spanish/which-pronunciation", "/de/teaching/spanish/which-pronunciation"),
    ("/en/teaching/spanish/which-pronunciation", "/en/teaching/spanish/which-pronunciation"),
    ("/de/impressum", "/de/impressum"),
]


@pytest.fixture
def client(real_app_factory):
    publication.clear_publication_caches()
    teaching_content.clear_teaching_content_caches()
    return real_app_factory(env_name="testing").test_client()


def _head(client, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200, (path, response.status_code)
    return response.get_data(as_text=True).split("</head>")[0]


def _attr(head: str, pattern: str) -> list[str]:
    return [html_module.unescape(value) for value in re.findall(pattern, head)]


def _json_ld(head: str) -> dict | None:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, flags=re.S)
    assert len(blocks) <= 1, "exactly one primary structured representation per page"
    return json.loads(blocks[0]) if blocks else None


def _copy_text(client, path: str) -> list[str]:
    body = client.get(path).get_data(as_text=True)
    return [html_module.unescape(value) for value in re.findall(r'data-copy-text="([^"]*)"', body)]


# --- registry and resource identity ---------------------------------------------------------------------------


def test_registry_is_valid_and_the_platform_title_has_one_source() -> None:
    assert publication.validate_registry() == []
    assert publication.platform_entry()["title"] == PLATFORM_TITLE
    occurrences = [
        path
        for root in (REPO_ROOT / "app" / "src", REPO_ROOT / "app" / "templates", REPO_ROOT / "content")
        for path in root.rglob("*")
        if path.is_file() and path.suffix in {".py", ".html", ".yaml"} and "A Multilingual Platform for Learner Pronunciation" in path.read_text(encoding="utf-8", errors="ignore")
    ]
    assert [path.name for path in occurrences] == ["resources.yaml"]


def test_resource_ids_are_unique_across_registry_and_public_topics() -> None:
    ids = list(publication.registry_resource_ids())
    for topic_file in sorted((REPO_ROOT / "content" / "teaching").glob("*/*/??.yaml")):
        topic = yaml.safe_load(topic_file.read_text(encoding="utf-8")) or {}
        if topic_file.parent.name != "hubs" and topic.get("resource_id") and topic_file.stem == "de":
            ids.append(topic["resource_id"])
    assert len(ids) == len(set(ids))


def test_people_and_roles_come_from_the_registry_only() -> None:
    for source in ("public_content.py", "public_page_content_data.py"):
        text = (REPO_ROOT / "app" / "src" / "app" / "routes" / source).read_text(encoding="utf-8")
        # (the acknowledgements of the team page are prose and may name people; corpus responsibilities may not)
        for name in ("Janina Reinhardt", "Kathrin Siebold", "Rolf Kreyer", "Amelie Spieß", "Theresa Fischer"):
            assert name not in text, (source, name)
    assert publication.person("theresa-fischer")["display_name"] == "Theresa Fischer, M.A."
    assert publication.person("felix-tacke")["sort_name"] == "Tacke, Felix"


def _broken_registry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutate) -> list[str]:
    registry = yaml.safe_load((REPO_ROOT / "content" / "publication" / "resources.yaml").read_text(encoding="utf-8"))
    mutate(registry)
    path = tmp_path / "resources.yaml"
    path.write_text(yaml.safe_dump(registry, allow_unicode=True), encoding="utf-8")
    monkeypatch.setenv("PROMAT_PUBLICATION_REGISTRY", str(path))
    publication.clear_publication_caches()
    try:
        return publication.validate_registry()
    finally:
        monkeypatch.delenv("PROMAT_PUBLICATION_REGISTRY")
        publication.clear_publication_caches()


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda r: r["languages"]["french"]["research_corpus"].update(resource_id="promat-corpus-es"), "already used"),
        (lambda r: r["languages"]["french"]["research_corpus"].update(creators=["nobody"]), "unknown person"),
        (lambda r: r["languages"]["french"]["research_corpus"].update(creators=[]), "needs at least one creator"),
        (lambda r: r["platform"].update(canonical_base_url="https://www.pronunciation-matters.de"), "without www"),
        (lambda r: r["platform"].update(canonical_base_url="http://pronunciation-matters.de"), "https origin"),
        (lambda r: r["people"].update({"placeholder": {"given": "N.", "family": "N."}}), "placeholder"),
        (lambda r: r["languages"]["spanish"]["research_corpus"].update(doi="not-a-doi"), "is not a DOI"),
        (lambda r: r["languages"]["spanish"]["research_corpus"].update(data_as_of="October 2026"), "YYYY"),
        (lambda r: r["languages"]["spanish"]["research_corpus"]["contributors"].append({"person": "felix-tacke", "role": "boss"}), "contributor role"),
    ],
)
def test_registry_validation_rejects_broken_bibliographic_data(tmp_path, monkeypatch, mutate, expected) -> None:
    errors = _broken_registry(tmp_path, monkeypatch, mutate)
    assert any(expected in error for error in errors), errors


def test_unknown_and_unpublished_topics_are_not_found(client) -> None:
    assert client.get("/de/teaching/spanish/does-not-exist").status_code == 404
    assert client.get("/de/teaching/spanish/Which-Pronunciation").status_code == 404
    for draft in ("/de/teaching/french/liaison", "/en/teaching/french/liaison", "/de/teaching/spanish/r-am-silbenende", "/de/teaching/spanish/r"):
        assert client.get(draft).status_code == 404, draft
    assert client.get("/de/teaching/klingon/anything").status_code == 404


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def alias_content(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "content" / "teaching"
    _write(root / "spanish" / "teaching.yaml", "teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs:\n  - de\n")
    _write(root / "spanish" / "hubs" / "de.yaml", "title: Spanisch\ntopics:\n  - new-name\n")
    _write(
        root / "spanish" / "new-name" / "de.yaml",
        "resource_id: promat-test-renamed\ntitle: Neu\nsummary: Kurz\naliases:\n  - old-name\nmetadata:\n  creators:\n    - felix-tacke\n  created: 2026-01-02\nblocks: []\n",
    )
    _write(root / "spanish" / "draft-topic" / "de.yaml", "title: Entwurf\nstatus: draft\naliases:\n  - old-draft\nblocks: []\n")
    monkeypatch.setattr(teaching_content, "TEACHING_CONTENT_ROOT", root)
    teaching_content.clear_teaching_content_caches()
    yield root
    teaching_content.clear_teaching_content_caches()


def test_only_listed_aliases_redirect_permanently(alias_content) -> None:
    resolve = teaching_content.resolve_topic_route_target
    assert resolve("spanish", "de", "new-name") == {"status": "ok", "ui_lang": "de", "topic_slug": "new-name"}
    assert resolve("spanish", "de", "old-name") == {"status": "redirect-topic", "ui_lang": "de", "topic_slug": "new-name", "code": 301}
    assert resolve("spanish", "de", "old-draft") == {"status": "not-found"}, "an alias never exposes an unpublished topic"
    assert resolve("spanish", "de", "draft-topic") == {"status": "not-found"}
    assert resolve("spanish", "de", "unknown") == {"status": "not-found"}
    # documented language fallback: no English edition of this teaching language
    assert resolve("spanish", "en", "new-name") == {"status": "redirect-topic", "ui_lang": "de", "topic_slug": "new-name", "code": 302}


# --- head metadata --------------------------------------------------------------------------------------------


def test_titles_are_unique_localized_and_without_duplicated_branding(client) -> None:
    titles = {path: _attr(_head(client, path), r"<title>(.*?)</title>")[0] for path, _ in PUBLIC_PAGES}
    for ui_lang in ("de", "en"):  # unique within a language; /de and /en are editions of the same page
        localized = [title for path, title in titles.items() if path.startswith(f"/{ui_lang}")]
        assert len(set(localized)) == len(localized), localized
    for path, title in titles.items():
        parts = [part.strip() for part in title.split("·")]
        assert len(parts) == len(set(parts)), (path, title)
        assert parts[-1] == "Pronunciation Matters"
    assert titles["/de/teaching/spanish/which-pronunciation"].startswith("Welche Aussprache unterrichten?")
    assert titles["/en/teaching/spanish/which-pronunciation"].startswith("Which pronunciation should you teach?")
    assert _attr(_head(client, "/en/research/french/design"), r"<title>(.*?)</title>")[0] == "Design: French corpus · Pronunciation Matters"


def test_descriptions_are_localized_and_resource_specific(client) -> None:
    descriptions = {path: _attr(_head(client, path), r'<meta name="description" content="([^"]*)">') for path, _ in PUBLIC_PAGES}
    for path, values in descriptions.items():
        assert len(values) == 1 and values[0].strip(), path
        assert "PROMAT-Oberfläche" not in values[0]
    german_markers = (" und ", " für ", " zur ", " der ")
    for path, values in descriptions.items():
        if path.startswith("/en"):
            assert not any(marker in values[0] for marker in german_markers), (path, values[0])
    assert descriptions["/de"][0] != descriptions["/en"][0]
    assert "seseo" in descriptions["/de/teaching/spanish/which-pronunciation"][0]
    assert "Spanisch" in descriptions["/de/research/spanish"][0]
    assert descriptions["/de/teaching/spanish"][0] != descriptions["/de/teaching"][0]
    # level 3: localized platform fallback
    assert descriptions["/de/impressum"][0] == publication.platform_description("de")


@pytest.mark.parametrize(("path", "canonical_path"), PUBLIC_PAGES)
def test_public_pages_have_one_canonical_url_on_the_canonical_host(client, path: str, canonical_path: str) -> None:
    canonicals = _attr(_head(client, path), r'<link rel="canonical" href="([^"]*)">')
    assert canonicals == [ORIGIN + canonical_path]
    assert _attr(_head(client, path), r'<meta name="robots" content="([^"]*)">') == []


def test_parameter_variants_do_not_create_new_identities(client) -> None:
    base = "/de/teaching/spanish/which-pronunciation"
    for variant in (base + "?utm_source=x", base + "?lang=en", base + "?ui_lang=en&x=1"):
        assert _attr(_head(client, variant), r'<link rel="canonical" href="([^"]*)">') == [ORIGIN + base]
    assert _attr(_head(client, "/privacy"), r'<link rel="canonical" href="([^"]*)">')[0].endswith("/privacy")
    assert re.fullmatch(rf"{ORIGIN}/(de|en)/privacy", _attr(_head(client, "/privacy"), r'<link rel="canonical" href="([^"]*)">')[0])


def test_hreflang_is_reciprocal_and_only_for_real_equivalents(client) -> None:
    for path, canonical_path in PUBLIC_PAGES:
        alternates = dict(re.findall(r'<link rel="alternate" hreflang="([a-z]+)" href="([^"]*)">', _head(client, path)))
        assert set(alternates) == {"de", "en"}, path
        assert ORIGIN + canonical_path in alternates.values(), path
        for lang, href in alternates.items():
            other = dict(re.findall(r'<link rel="alternate" hreflang="([a-z]+)" href="([^"]*)">', _head(client, href.removeprefix(ORIGIN))))
            assert other == alternates, (path, lang)


def test_topic_without_a_public_equivalent_gets_no_hreflang(alias_content, real_app_factory) -> None:
    flask_app = real_app_factory(env_name="testing")
    head = flask_app.test_client().get("/de/teaching/spanish/new-name").get_data(as_text=True).split("</head>")[0]
    assert '<link rel="canonical" href="https://pronunciation-matters.de/de/teaching/spanish/new-name">' in head
    assert "hreflang" not in head


def test_unpublished_and_protected_pages_are_not_indexable_and_carry_no_resource_metadata(client) -> None:
    for path in ("/en/research/french/design", "/de/research/german/design", "/login", "/access-request"):
        head = _head(client, path)
        assert _attr(head, r'<meta name="robots" content="([^"]*)">') == ["noindex"], path
        assert "rel=\"canonical\"" not in head and "hreflang" not in head and "application/ld+json" not in head, path
        assert "citation_title" not in head, path
    body = client.get("/en/research/french/design").get_data(as_text=True)
    assert "in preparation" in body
    for developer_wording in ("technical slug", "structurally prepared", "Data wiring"):
        assert developer_wording not in body
    assert "data-copy-text" not in body


def test_dates_are_machine_readable(client) -> None:
    body = client.get("/de/teaching/spanish/which-pronunciation").get_data(as_text=True)
    assert '<time datetime="2026-05-11">11.05.2026</time>' in body
    assert '<time datetime="2026-05-13">13.05.2026</time>' in body


# --- JSON-LD --------------------------------------------------------------------------------------------------


def test_json_ld_describes_the_resource_hierarchy(client) -> None:
    platform = _json_ld(_head(client, "/de"))
    assert platform["@type"] == "WebSite" and platform["name"] == PLATFORM_TITLE and platform["identifier"] == "promat"
    assert platform["editor"][0]["name"] == "Felix Tacke" and "author" not in platform
    assert platform["publisher"]["name"] == PUBLISHER

    corpus = _json_ld(_head(client, "/en/research/french"))
    assert corpus["@type"] == "Dataset" and corpus["identifier"] == "promat-corpus-fr" and corpus["inLanguage"] == "fr"
    assert [person["name"] for person in corpus["creator"]] == ["Janina Reinhardt"]
    assert [person["name"] for person in corpus["contributor"]] == ["Amelie Spieß"]
    assert corpus["isPartOf"] == {"@type": "WebSite", "@id": f"{ORIGIN}/en", "identifier": "promat", "name": PLATFORM_TITLE}
    assert corpus["url"] == corpus["@id"] == f"{ORIGIN}/en/research/french"

    area = _json_ld(_head(client, "/de/teaching/spanish"))
    assert area["@type"] == "Collection" and area["inLanguage"] == "de" and area["about"]["name"] == "Spanish"
    assert area["isPartOf"]["@id"] == f"{ORIGIN}/de"

    topic = _json_ld(_head(client, "/en/teaching/spanish/which-pronunciation"))
    assert topic["@type"] == ["Article", "LearningResource"]
    assert topic["name"] == "Which pronunciation should you teach?"
    assert [person["name"] for person in topic["author"]] == ["Felix Tacke"]
    assert topic["datePublished"] == "2026-05-11" and topic["dateModified"] == "2026-05-13"
    assert topic["inLanguage"] == "en"
    assert topic["isPartOf"]["identifier"] == "promat-teaching-es" and topic["isPartOf"]["@id"] == f"{ORIGIN}/en/teaching/spanish"
    assert topic["identifier"] == _json_ld(_head(client, "/de/teaching/spanish/which-pronunciation"))["identifier"]

    design = _json_ld(_head(client, "/de/research/spanish/design"))
    assert design["@type"] == "ScholarlyArticle" and design["isPartOf"]["identifier"] == "promat-corpus-es"

    for payload in (platform, corpus, area, topic, design):
        assert "license" not in payload and "sameAs" not in payload and "version" not in payload, "undecided values are never invented"
    assert _json_ld(_head(client, "/de/research")) is None
    assert _json_ld(_head(client, "/en/teaching/french")) is None, "an area without published topics is not described as a resource"


# --- citations ------------------------------------------------------------------------------------------------


def test_generated_citations_follow_the_four_levels(client) -> None:
    assert _copy_text(client, "/en/project") == [f"Tacke, Felix (2026–). {PLATFORM_TITLE}. {PUBLISHER}. {ORIGIN}/en"]
    assert _copy_text(client, "/en/research/french") == [
        f"Reinhardt, Janina (2026–). Pronunciation Matters: French Learner Pronunciation Corpus. In: Felix Tacke (ed.), {PLATFORM_TITLE}. {PUBLISHER}. {ORIGIN}/en/research/french"
    ]
    assert _copy_text(client, "/de/teaching/spanish") == [
        f"Tacke, Felix (2026–). Pronunciation Matters: Spanish Pronunciation Teaching Resources. In: Felix Tacke (Hrsg.), {PLATFORM_TITLE}. {PUBLISHER}. {ORIGIN}/de/teaching/spanish"
    ]
    assert _copy_text(client, "/de/teaching/spanish/which-pronunciation") == [
        f"Tacke, Felix (2026). „Welche Aussprache unterrichten?“. In: Felix Tacke (Hrsg.), {PLATFORM_TITLE}. {PUBLISHER}. {ORIGIN}/de/teaching/spanish/which-pronunciation"
    ]
    assert _copy_text(client, "/en/teaching/spanish/which-pronunciation") == [
        f"Tacke, Felix (2026). “Which pronunciation should you teach?”. In: Felix Tacke (ed.), {PLATFORM_TITLE}. {PUBLISHER}. {ORIGIN}/en/teaching/spanish/which-pronunciation"
    ]


def test_citations_use_the_exact_page_title_author_and_url(client) -> None:
    for ui_lang in ("de", "en"):
        path = f"/{ui_lang}/teaching/spanish/which-pronunciation"
        topic = yaml.safe_load((REPO_ROOT / "content" / "teaching" / "spanish" / "which-pronunciation" / f"{ui_lang}.yaml").read_text(encoding="utf-8"))
        (text,) = _copy_text(client, path)
        assert topic["title"] in text
        assert text.endswith(ORIGIN + path)
        assert "www." not in text and not text.rstrip(".").endswith(ORIGIN)
        assert PLATFORM_TITLE in text
        head = _head(client, path)
        assert _attr(head, r'<meta name="citation_title" content="([^"]*)">') == [topic["title"]]
        assert _attr(head, r'<meta name="citation_author" content="([^"]*)">') == ["Tacke, Felix"]
        assert _attr(head, r'<meta name="author" content="([^"]*)">') == ["Felix Tacke"]
        assert _attr(head, r'<meta name="citation_public_url" content="([^"]*)">') == [ORIGIN + path]


def test_pages_that_are_not_scholarly_units_offer_no_citation(client) -> None:
    for path in ("/de", "/de/research", "/de/teaching", "/de/project/team", "/de/impressum", "/en/teaching/french", "/de/research/german", "/de/teaching/german"):
        assert _copy_text(client, path) == [], path


def test_platform_editor_never_becomes_the_author_of_someone_elses_resource() -> None:
    corpus = publication.corpus_resource("french", "de")
    citation = publication.format_citation(corpus, "de")["text"]
    assert citation.startswith("Reinhardt, Janina (2026–).")
    assert "In: Felix Tacke (Hrsg.)," in citation
    assert [creator["name"] for creator in corpus["creators"]] == ["Janina Reinhardt"]
    assert [editor["name"] for editor in corpus["editors"]] == ["Felix Tacke"]

    topic = publication.topic_resource(
        "french", "en", "liaison", resource_id="promat-test", title="Liaison", creator_ids=["janina-reinhardt", "amelie-spiess"],
        date_published="2027-03-01", date_modified="2028-01-01",
    )
    text = publication.format_citation(topic, "en")["text"]
    assert text.startswith("Reinhardt, Janina & Spieß, Amelie (2027). “Liaison”. In: Felix Tacke (ed.),")


def test_year_logic_keeps_the_publication_year_when_the_page_is_modified() -> None:
    topic = publication.topic_resource(
        "spanish", "de", "x", resource_id="promat-test", title="T", creator_ids=["felix-tacke"], date_published="2026-05-11", date_modified="2029-01-01",
    )
    assert publication.citation_year(topic) == "2026"
    assert publication.citation_year(publication.platform_resource("de")) == "2026–"
    assert publication.citation_year(publication.corpus_resource("spanish", "de")) == "2026–"
    assert publication.json_ld(topic)["dateModified"] == "2029-01-01"


def test_doi_version_data_as_of_and_license_are_optional_and_need_no_template_change() -> None:
    corpus = publication.corpus_resource("spanish", "en")
    assert corpus["doi"] is None and corpus["version"] is None and corpus["data_as_of"] is None and corpus["license"] is None
    plain = publication.format_citation(corpus, "en")["text"]
    assert plain.endswith(f"{ORIGIN}/en/research/spanish") and "Version" not in plain

    corpus.update(doi="10.1234/promat.es", version="1.2", data_as_of="2026-09-30", license="https://example.org/licence")
    citation = publication.format_citation(corpus, "en")
    assert "Corpus (Version 1.2; data as of: 2026-09-30). In:" in citation["text"]
    assert citation["text"].endswith("https://doi.org/10.1234/promat.es")
    assert '<a href="https://doi.org/10.1234/promat.es">' in citation["html"]
    payload = publication.json_ld(corpus)
    assert payload["sameAs"] == "https://doi.org/10.1234/promat.es" and payload["version"] == "1.2"
    assert payload["license"] == "https://example.org/licence" and payload["dateModified"] == "2026-09-30"
    assert ("citation_doi", "10.1234/promat.es") in publication.reference_manager_tags(corpus)
    assert "Datenstand: 2026-09-30" in publication.format_citation(corpus, "de")["text"]


def test_resources_without_real_authors_or_publication_are_not_citable() -> None:
    assert publication.corpus_resource("german", "de")["citable"] is False, "in preparation"
    assert publication.teaching_area_resource("french", "de")["citable"] is False, "no responsible person recorded"
    assert publication.teaching_area_resource("spanish", "de", has_public_topics=False)["citable"] is False
    draft = publication.topic_resource(
        "french", "de", "liaison", resource_id="promat-test", title="Liaison", creator_ids=[], date_published="2026-06-02", date_modified=None,
    )
    assert draft["citable"] is False and publication.format_citation(draft, "de") is None
    unpublished = publication.topic_resource(
        "french", "de", "liaison", resource_id="promat-test", title="Liaison", creator_ids=["janina-reinhardt"], date_published="2026-06-02", date_modified=None, published=False,
    )
    assert unpublished["citable"] is False


def test_json_ld_block_cannot_break_out_of_its_script_element() -> None:
    topic = publication.topic_resource(
        "spanish", "de", "x", resource_id="promat-test", title="</script><script>alert(1)</script>", creator_ids=["felix-tacke"], date_published="2026-01-01", date_modified=None,
    )
    text = publication.json_ld_script_text(topic)
    assert "</script>" not in text
    assert json.loads(text)["name"] == "</script><script>alert(1)</script>"
    html = publication.format_citation(topic, "de")["html"]
    assert "<script>" not in html


# --- one source for corpus people -------------------------------------------------------------------------------


def test_corpus_cards_and_team_page_show_the_same_people(client) -> None:
    for ui_lang in ("de", "en"):
        cards = client.get(f"/{ui_lang}/research").get_data(as_text=True)
        team = client.get(f"/{ui_lang}/project/team").get_data(as_text=True)
        for language_slug in ("spanish", "french", "german", "english"):
            entry = publication.language_entry("research_corpus", language_slug)
            for names in (
                publication.display_names(entry["creators"]),
                publication.display_names(publication.contributor_ids(language_slug, "material_design")),
                publication.display_names(publication.contributor_ids(language_slug, "data_collection")),
            ):
                value = html_module.escape(", ".join(names))
                assert value in cards and value in team, (ui_lang, language_slug, value)


# --- content validator ------------------------------------------------------------------------------------------


def _load_validator():
    import importlib.util

    spec = importlib.util.spec_from_file_location("validate_teaching_content", REPO_ROOT / "scripts" / "validate_teaching_content.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GOOD_TOPIC = "resource_id: promat-test-topic\ntitle: Thema\nsummary: Kurz\nequivalents:\n  {other}: topic\nmetadata:\n  creators:\n    - felix-tacke\n  created: 2026-01-02\nblocks: []\n"


def _validate_topics(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, de: str, en: str | None) -> list[str]:
    validator = _load_validator()
    root = tmp_path / "content" / "teaching"
    _write(root / "spanish" / "topic" / "de.yaml", de)
    if en is not None:
        _write(root / "spanish" / "topic" / "en.yaml", en)
    monkeypatch.setattr(validator, "CONTENT_ROOT", root)
    errors: list[str] = []
    validator.validate_publication_front_matter(errors, validator.load_publication_module(), "spanish", ["de", "en"], dict(publication.registry_resource_ids()))
    return errors


def test_validator_accepts_a_complete_bilingual_public_topic(tmp_path, monkeypatch) -> None:
    assert _validate_topics(tmp_path, monkeypatch, GOOD_TOPIC.format(other="en"), GOOD_TOPIC.format(other="de")) == []


def test_validator_ignores_unfinished_topics(tmp_path, monkeypatch) -> None:
    draft = "title: Entwurf\nstatus: draft\nmetadata:\n  authors:\n    - NN\n"
    assert _validate_topics(tmp_path, monkeypatch, draft, draft) == []


@pytest.mark.parametrize(
    ("de", "expected"),
    [
        (GOOD_TOPIC.format(other="en").replace("resource_id: promat-test-topic\n", ""), "needs a resource_id"),
        (GOOD_TOPIC.format(other="en").replace("promat-test-topic", "promat-corpus-es"), "already used"),
        (GOOD_TOPIC.format(other="en").replace("    - felix-tacke\n", "    - nobody\n"), "unknown creator"),
        (GOOD_TOPIC.format(other="en").replace("  creators:\n    - felix-tacke\n", "  authors:\n    - Felix Tacke\n"), "metadata.creators must list"),
        (GOOD_TOPIC.format(other="en").replace("  created: 2026-01-02\n", ""), "metadata.created must be an ISO date"),
        (GOOD_TOPIC.format(other="en").replace("  created: 2026-01-02\n", "  created: 2026-01-02\n  updated: 2025-01-01\n"), "earlier than"),
        (GOOD_TOPIC.format(other="en") + "citation:\n  text: Tacke (2026).\n", "remove the typed citation"),
        (GOOD_TOPIC.format(other="en").replace("summary: Kurz\n", ""), "summary or description is required"),
        (GOOD_TOPIC.format(other="en").replace("equivalents:\n  en: topic\n", ""), "no public en equivalent"),
        (GOOD_TOPIC.format(other="en") + "doi: nonsense\n", "is not a DOI"),
        (GOOD_TOPIC.format(other="en") + "aliases:\n  - topic\n", "collides with an existing topic"),
    ],
)
def test_validator_rejects_incomplete_public_front_matter(tmp_path, monkeypatch, de: str, expected: str) -> None:
    errors = _validate_topics(tmp_path, monkeypatch, de, GOOD_TOPIC.format(other="de"))
    assert any(expected in error for error in errors), errors


def test_validator_requires_one_resource_id_for_all_language_editions(tmp_path, monkeypatch) -> None:
    errors = _validate_topics(tmp_path, monkeypatch, GOOD_TOPIC.format(other="en"), GOOD_TOPIC.format(other="de").replace("promat-test-topic", "promat-test-other"))
    assert any("must share one resource_id" in error for error in errors), errors


def test_validator_requires_the_other_language_edition_to_be_public(tmp_path, monkeypatch) -> None:
    errors = _validate_topics(tmp_path, monkeypatch, GOOD_TOPIC.format(other="en"), "title: Draft\nstatus: draft\n")
    assert any("no public en equivalent" in error for error in errors), errors


def test_the_repository_content_passes_the_validator() -> None:
    assert _load_validator().main() == 0
