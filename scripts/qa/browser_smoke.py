"""Reusable browser smoke for the public surface and the logout/cache invariants (Playwright, Chromium).

    python scripts/qa/browser_smoke.py --base-url http://127.0.0.1:8000 --out tmp/ui-qa/<date>-browser-smoke
    PROMAT_QA_USER=... PROMAT_QA_PASSWORD=... python scripts/qa/browser_smoke.py --base-url ... --out ...

Needs ``pip install playwright`` and ``playwright install chromium`` (not part of the project requirements).
Credentials are read from the environment only and are never printed; without them the login-dependent checks are
reported as SKIPPED. The script is read-only apart from signing in and out with the given account.

Checks, each in ``de`` and ``en`` where a language applies:

* ``document.title`` after the page has fully loaded equals the server-rendered ``<title>`` (no client rewrite);
* no console output from the removed page-title module;
* unfinished (draft) Teaching topics redirect to their hub, which does not link them;
* with credentials: no third-party analytics request on protected research pages, protected responses are
  ``private, no-store``, and after logout the Back button does not show the protected page from the cache;
* screenshots of the visited pages are written to ``--out``.
"""

from __future__ import annotations

import argparse
import html
import os
from pathlib import Path
import re
import sys

from playwright.sync_api import Page, sync_playwright

TITLE_PAGES = {
    "de": ("/de", "/de/teaching", "/de/teaching/spanish", "/de/teaching/spanish/which-pronunciation", "/de/research/spanish/design", "/de/impressum", "/de/privacy"),
    "en": ("/en", "/en/teaching", "/en/teaching/spanish", "/en/teaching/spanish/which-pronunciation", "/en/research/spanish/design", "/en/impressum", "/en/privacy"),
}
DRAFT_TOPICS = {"de": ("/de/teaching/french/liaison", "/de/teaching/spanish/r-am-silbenende"), "en": ("/en/teaching/french/liaison", "/en/teaching/spanish/r-am-silbenende")}
PROTECTED_PAGES = {"de": "/de/research/spanish/speakers", "en": "/en/research/spanish/speakers"}
THIRD_PARTY_MARKERS = ("gc.zgo.at", "goatcounter.com")


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.checks = 0

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        print(("PASS " if condition else "FAIL ") + label)
        if not condition:
            self.failures.append(label)

    def skip(self, label: str) -> None:
        print("SKIP " + label)


def server_title(page: Page, url: str) -> str:
    body = page.request.get(url).text()
    match = re.search(r"<title>(.*?)</title>", body, flags=re.S)
    return html.unescape(match.group(1)).strip() if match else ""


def screenshot(page: Page, out: Path, name: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out / f"{name}.png"), full_page=True)


def slug(path: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", path.lower()).strip("_") or "root"


def run(base_url: str, out: Path, username: str | None, password: str | None) -> int:
    report = Report()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        console_messages: list[str] = []
        page.on("console", lambda message: console_messages.append(message.text))
        requested_urls: list[str] = []
        page.on("request", lambda request: requested_urls.append(request.url))

        for ui_lang, paths in TITLE_PAGES.items():
            for path in paths:
                response = page.goto(base_url + path, wait_until="networkidle")
                ok = response is not None and response.status == 200
                report.check(ok, f"[{ui_lang}] {path} loads (200)")
                if not ok:
                    continue
                expected = server_title(page, base_url + path)
                report.check(bool(expected) and page.title() == expected, f"[{ui_lang}] {path} document.title == server <title> ({page.title()!r})")
                screenshot(page, out, f"{ui_lang}_{slug(path)}")
        report.check(not any("[Page Title]" in message for message in console_messages), "no console output from the removed page-title module")

        titles = {path: server_title(page, base_url + path) for path in ("/de/teaching/spanish/which-pronunciation", "/de/research/spanish/design", "/de/impressum")}
        report.check(len(set(titles.values())) == len(titles), "route titles differ between pages")

        for ui_lang, paths in DRAFT_TOPICS.items():
            for path in paths:
                page.goto(base_url + path, wait_until="networkidle")
                report.check(not page.url.rstrip("/").endswith(path.rsplit("/", 1)[-1]), f"[{ui_lang}] draft {path} is redirected away ({page.url})")
                hub_html = page.content()
                report.check(f'href="{path}"' not in hub_html, f"[{ui_lang}] hub does not link draft {path}")
            screenshot(page, out, f"{ui_lang}_teaching_hub_after_draft_redirect")

        if not (username and password):
            report.skip("login-dependent checks (set PROMAT_QA_USER / PROMAT_QA_PASSWORD)")
        else:
            for ui_lang, protected in PROTECTED_PAGES.items():
                page.goto(f"{base_url}/login?next={protected}", wait_until="networkidle")
                page.fill('input[name="email"]', username)
                page.fill('input[name="password"]', password)
                requested_urls.clear()
                with page.expect_navigation(wait_until="networkidle"):
                    page.click('button[type="submit"]')
                report.check(page.url.endswith(protected), f"[{ui_lang}] login returns to {protected} ({page.url})")
                report.check(not any(marker in url for url in requested_urls for marker in THIRD_PARTY_MARKERS), f"[{ui_lang}] no third-party analytics request on {protected}")
                response = page.request.get(base_url + protected)
                report.check("no-store" in response.headers.get("cache-control", ""), f"[{ui_lang}] protected response is no-store")
                screenshot(page, out, f"{ui_lang}_protected_{slug(protected)}")

                # Logout through the real UI control (the delegated click handler works while the menu is closed).
                logout = page.locator('[data-logout="fetch"]').first
                with page.expect_navigation(wait_until="networkidle"):
                    logout.evaluate("element => element.click()")
                session = page.request.get(base_url + "/auth/session").json()
                report.check(session.get("authenticated") is False, f"[{ui_lang}] logout via the UI control ends the session")
                page.go_back(wait_until="networkidle")
                shows_protected = "/login" not in page.url and protected in page.url
                report.check(not shows_protected, f"[{ui_lang}] Back after logout does not show the protected page ({page.url})")
                screenshot(page, out, f"{ui_lang}_back_after_logout")

        browser.close()
    print(f"\n{report.checks} checks, {len(report.failures)} failed")
    for failure in report.failures:
        print(f"  FAILED: {failure}", file=sys.stderr)
    return 1 if report.failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--out", required=True, type=Path, help="Directory for screenshots, for example tmp/ui-qa/<date>-browser-smoke")
    args = parser.parse_args()
    return run(args.base_url.rstrip("/"), args.out, os.environ.get("PROMAT_QA_USER"), os.environ.get("PROMAT_QA_PASSWORD"))


if __name__ == "__main__":
    raise SystemExit(main())
