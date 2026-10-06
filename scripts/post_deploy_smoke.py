"""Read-only smoke check of a running PROMAT site (post-deploy and operator spot check).

    python scripts/post_deploy_smoke.py --base-url https://pronunciation-matters.de

Only plain GET requests are sent, redirects are never followed, nothing is logged in, nothing is posted and no
state is changed. The exit code is 0 only if every check passes. It verifies what the deployment must provide:

* the legal pages answer 200 (they once returned 500 because their source was not in the image);
* the public landing, teaching and research-design pages answer 200 and carry a server-rendered ``<title>``;
* topic pages whose YAML marks them as draft / not public are not served as pages;
* a protected research page redirects to the login instead of rendering;
* the citation box of the finished topic page names the page's own canonical URL, and that URL answers 200
  without a redirect.

The draft list is derived from ``content/teaching`` of the checkout this script runs from, so it follows the
content instead of a hand-maintained list. The browser-side checks (``document.title`` after JavaScript has run,
Back button after logout) live in ``scripts/qa/browser_smoke.py``.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
import html
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlparse
import urllib.request

REPO_ROOT = Path(__file__).resolve().parents[1]
TEACHING_ROOT = REPO_ROOT / "content" / "teaching"

LEGAL_PATHS = ("/impressum", "/de/impressum", "/en/impressum", "/de/privacy", "/en/privacy")
PUBLIC_PATHS = (
    "/de",
    "/en",
    "/de/teaching",
    "/en/teaching",
    "/de/teaching/spanish",
    "/de/teaching/spanish/which-pronunciation",
    "/en/teaching/spanish/which-pronunciation",
    "/de/research/spanish/design",
    "/en/research/spanish/design",
)
PROTECTED_PATHS = ("/de/research/spanish/speakers", "/en/research/spanish/comparison", "/de/research/spanish/player/x/wordlist")
CITED_PAGES = ("/de/teaching/spanish/which-pronunciation", "/en/teaching/spanish/which-pronunciation")
# Citable resources: canonical URL, one JSON-LD block and a generated citation that names exactly this URL.
RESOURCE_PAGES = (
    *CITED_PAGES,
    "/de/research/spanish",
    "/en/research/french",
    "/de/research/spanish/design",
    "/en/research/spanish/design",
    "/de/teaching/spanish",
    "/en/teaching/spanish",
)
UNKNOWN_RESOURCE_PATHS = ("/de/teaching/spanish/this-topic-does-not-exist",)

Response = tuple[int, dict[str, str], str]
Fetch = Callable[[str], Response]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # noqa: D401 - urllib hook
        return None


def http_fetch(base_url: str) -> Fetch:
    opener = urllib.request.build_opener(_NoRedirect)

    def fetch(path: str) -> Response:
        request = urllib.request.Request(base_url.rstrip("/") + path, headers={"User-Agent": "promat-post-deploy-smoke/1"})
        try:
            with opener.open(request, timeout=20) as response:
                return response.status, {k.lower(): v for k, v in response.headers.items()}, response.read().decode("utf-8", "replace")
        except HTTPError as error:
            return error.code, {k.lower(): v for k, v in error.headers.items()}, error.read().decode("utf-8", "replace")

    return fetch


# Standard library only: this runs on the deploy host, which has no project virtualenv.
_DRAFT_MARKER = re.compile(r"^\s*(?:status:\s*draft|is_public:\s*false)\s*$", flags=re.M | re.I)


def draft_topic_paths() -> list[str]:
    paths: list[str] = []
    for locale_file in sorted(TEACHING_ROOT.glob("*/*/??.yaml")):
        teaching_lang, topic_slug, locale_name = locale_file.relative_to(TEACHING_ROOT).parts
        if topic_slug == "hubs":
            continue
        if _DRAFT_MARKER.search(locale_file.read_text(encoding="utf-8")):
            paths.append(f"/{locale_name.removesuffix('.yaml')}/teaching/{teaching_lang}/{topic_slug}")
    return paths


def _topic_title(path: Path) -> str:
    match = re.search(r"^title:\s*(.+?)\s*$", path.read_text(encoding="utf-8"), flags=re.M)
    return match.group(1).strip("\"'") if match else ""


def _title(body: str) -> str:
    match = re.search(r"<title>(.*?)</title>", body, flags=re.S)
    return html.unescape(match.group(1)).strip() if match else ""


def run_checks(fetch: Fetch, *, canonical_origin: str) -> list[str]:
    failures: list[str] = []

    for path in (*LEGAL_PATHS, *PUBLIC_PATHS):
        status, _headers, body = fetch(path)
        if status != 200:
            failures.append(f"GET {path}: expected 200, got {status}")
        elif not _title(body):
            failures.append(f"GET {path}: no server-rendered <title>")

    for path in draft_topic_paths():
        status, _headers, _body = fetch(path)
        if status == 200:
            failures.append(f"GET {path}: draft topic is publicly served (200)")

    for path in PROTECTED_PATHS:
        status, headers, _body = fetch(path)
        if status not in {302, 303} or not headers.get("location", "").startswith("/login"):
            failures.append(f"GET {path}: expected a redirect to /login, got {status} {headers.get('location', '')!r}")

    titles = {path: _title(fetch(path)[2]) for path in CITED_PAGES}
    for path, title in titles.items():
        topic_file = TEACHING_ROOT / "spanish" / "which-pronunciation" / f"{path.split('/')[1]}.yaml"
        expected = _topic_title(topic_file)
        if expected and expected not in title:
            failures.append(f"GET {path}: <title> {title!r} does not contain the page title {expected!r}")

    for path in UNKNOWN_RESOURCE_PATHS:
        status, _headers, _body = fetch(path)
        if status != 404:
            failures.append(f"GET {path}: an unknown resource must answer 404, got {status}")

    for path in RESOURCE_PAGES:
        status, _headers, body = fetch(path)
        if status != 200:
            failures.append(f"GET {path}: expected 200, got {status}")
            continue
        expected_url = canonical_origin + path
        canonicals = re.findall(r'<link rel="canonical" href="([^"]*)">', body)
        if canonicals != [expected_url]:
            failures.append(f"GET {path}: canonical is {canonicals!r}, expected {expected_url!r}")
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, flags=re.S)
        try:
            structured = json.loads(blocks[0]) if len(blocks) == 1 else None
        except ValueError:
            structured = None
        if not isinstance(structured, dict) or structured.get("url") != expected_url or not structured.get("identifier"):
            failures.append(f"GET {path}: missing or inconsistent JSON-LD (url/identifier)")

    for path in RESOURCE_PAGES:
        status, _headers, body = fetch(path)
        if status != 200:
            continue
        copy_texts = [html.unescape(text) for text in re.findall(r'data-copy-text="([^"]*)"', body)]
        urls = [url.rstrip(".,;") for text in copy_texts for url in re.findall(r"https?://[^\s)\]]+", text)]
        if not urls:
            failures.append(f"GET {path}: the citation box names no URL")
        for url in urls:
            parsed = urlparse(url)
            if f"{parsed.scheme}://{parsed.netloc}" != canonical_origin or parsed.path != path:
                failures.append(f"GET {path}: citation URL {url!r} is not {canonical_origin}{path}")
                continue
            cited_status, _h, _b = fetch(parsed.path)
            if cited_status != 200:
                failures.append(f"citation URL {url}: expected 200 without redirect, got {cited_status}")

    ready_status, _headers, ready_body = fetch("/ready")
    if ready_status != 200:
        failures.append(f"GET /ready: expected 200, got {ready_status}")
    elif any(token in ready_body for token in ("Traceback", "Error:", "Exception")):
        failures.append("GET /ready: response contains exception details")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", required=True, help="Origin of the site to check, for example https://pronunciation-matters.de")
    parser.add_argument("--canonical-origin", help="Origin the citation URLs must use; defaults to --base-url")
    args = parser.parse_args(argv)

    base_url = args.base_url.rstrip("/")
    failures = run_checks(http_fetch(base_url), canonical_origin=(args.canonical_origin or base_url).rstrip("/"))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print(f"post-deploy smoke OK for {base_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
