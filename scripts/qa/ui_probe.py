"""Reusable UI probe: performance, accessibility (axe-core) and mobile overflow for representative pages.

    python scripts/qa/ui_probe.py --base-url http://127.0.0.1:8765 --out tmp/ui-qa/<date>-probe \
        [--user qa.user@example.org --password ...] [--session ES-L-0001-2026-S01] [--only perf|axe|overflow]

Needs ``pip install playwright axe-playwright-python`` and ``playwright install chromium``. Credentials are read from
arguments or ``PROMAT_QA_USER`` / ``PROMAT_QA_PASSWORD`` and never printed; without them the login-protected pages
are skipped. Results are written as JSON (``perf.json``, ``axe.json``, ``overflow.json``) so before/after runs can be
compared. Read-only apart from signing in and out.

* perf: cold-cache page load under constant throttling (default 1.6 Mbit/s down, 150 ms RTT): total transfer,
  request count, largest asset, font transfer, DOMContentLoaded and load time.
* axe: axe-core violations per page, language and theme (impact serious/critical are counted separately).
* overflow: ``scrollWidth > viewport width`` at 390, 820 and 1280 px.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import time

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

AXE_JS = None
try:  # axe.min.js ships with axe-playwright-python
    import axe_playwright_python

    AXE_JS = (Path(axe_playwright_python.__file__).parent / "axe.min.js").read_text(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

PROTECTED_NAMES = {"speakers", "comparison", "player", "phenomena", "phenomena_set"}
THROTTLE = {"download": 1.6 * 1024 * 1024 / 8, "upload": 750 * 1024 / 8, "latency": 150}


def public_pages() -> dict[str, str]:
    return {
        "landing": "/{l}",
        "login": "/login?ui_lang={l}",
        "access_request": "/access-request?ui_lang={l}",
        "research_hub": "/{l}/research/spanish",
        "teaching_hub": "/{l}/teaching/spanish",
        "teaching_topic": "/{l}/teaching/spanish/which-pronunciation",
    }


def create_probe_set(page: Page, base: str, item_ids: list[str]) -> str | None:
    """Create a private set (label 'UI probe') with the given wordlist items; returns its id. Only for QA accounts."""
    return page.evaluate(
        """async ([base, ids]) => {
            const post = await fetch(base + '/api/research/sets', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({corpus_language: 'spanish', label: 'UI probe', lifecycle: 'saved'})});
            if (!post.ok) return null; const id = (await post.json()).set.set_id;
            const put = await fetch(base + '/api/research/sets/' + id + '/items', {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({items: ids.map(i => ({task: 'wordlist', item_id: i}))})});
            return put.ok ? id : null; }""",
        [base, item_ids],
    )


def protected_pages(session_id: str, set_id: str | None = None) -> dict[str, str]:
    extra = {"phenomena_set": "/{l}/research/spanish/phenomena/sets/" + set_id} if set_id else {}
    return extra | {
        "speakers": "/{l}/research/spanish/speakers",
        "comparison": "/{l}/research/spanish/comparison",
        "player": "/{l}/research/spanish/player/" + session_id + "/wordlist?source=speakers",
        "phenomena": "/{l}/research/spanish/phenomena",
    }


def new_context(browser: Browser, *, theme: str = "light", width: int = 1280, height: int = 900) -> BrowserContext:
    context = browser.new_context(viewport={"width": width, "height": height})
    context.add_init_script(f"try {{ localStorage.setItem('site-theme', '{theme}'); }} catch (e) {{}}")
    return context


def login(page: Page, base: str, user: str, password: str) -> None:
    page.goto(f"{base}/login", wait_until="networkidle")
    page.fill('input[name="email"]', user)
    page.fill('input[name="password"]', password)
    with page.expect_navigation(wait_until="networkidle"):
        page.click('button[type="submit"]')


def measure_perf(browser: Browser, base: str, path: str, *, cookies=None) -> dict:
    context = new_context(browser)
    if cookies:
        context.add_cookies(cookies)
    page = context.new_page()
    cdp = context.new_cdp_session(page)
    cdp.send("Network.enable")
    cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
    cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": THROTTLE["latency"], "downloadThroughput": THROTTLE["download"], "uploadThroughput": THROTTLE["upload"]})
    sizes: dict[str, int] = {}
    urls: dict[str, str] = {}
    cdp.on("Network.requestWillBeSent", lambda e: urls.__setitem__(e["requestId"], e["request"]["url"]))
    cdp.on("Network.loadingFinished", lambda e: sizes.__setitem__(e["requestId"], int(e.get("encodedDataLength", 0))))
    page.add_init_script(
        "window.__lcp=0;new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});"
    )
    started = time.time()
    page.goto(base + path, wait_until="load", timeout=120000)
    page.wait_for_timeout(1500)
    nav = page.evaluate("() => { const n = performance.getEntriesByType('navigation')[0]; return {dcl: n.domContentLoadedEventEnd, load: n.loadEventEnd, lcp: window.__lcp}; }")
    items = sorted(((sizes.get(i, 0), urls[i]) for i in urls if i in sizes), reverse=True)
    result = {
        "path": path,
        "transfer_kb": round(sum(s for s, _ in items) / 1024, 1),
        "requests": len(items),
        "largest": [{"kb": round(s / 1024, 1), "url": re.sub(r"^https?://[^/]+", "", u)[:90]} for s, u in items[:3]],
        "font_kb": round(sum(s for s, u in items if re.search(r"\.(woff2?|ttf)(\?|$)", u)) / 1024, 1),
        "dcl_ms": round(nav["dcl"]), "load_ms": round(nav["load"]), "lcp_ms": round(nav["lcp"]),
        "wall_s": round(time.time() - started, 1),
    }
    context.close()
    return result


def run_axe(page: Page) -> dict:
    page.evaluate(AXE_JS)
    data = page.evaluate("async () => { const r = await axe.run(document, {resultTypes:['violations']}); return r.violations.map(v => ({id: v.id, impact: v.impact, nodes: v.nodes.length, sample: (v.nodes[0]||{}).target})); }")
    return {"violations": data, "serious_or_critical": sum(1 for v in data if v["impact"] in ("serious", "critical"))}


def measure_overflow(page: Page, base: str, path: str, width: int) -> dict:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(base + path, wait_until="networkidle")
    page.wait_for_timeout(500)
    info = page.evaluate(
        """() => { const w = document.documentElement.clientWidth; const sw = document.documentElement.scrollWidth;
        const offenders = []; if (sw > w) { for (const el of document.querySelectorAll('body *')) { const r = el.getBoundingClientRect();
        if (r.right > w + 1 && r.width > 0 && getComputedStyle(el).position !== 'fixed') { offenders.push((el.id ? '#'+el.id : el.tagName.toLowerCase()) + '.' + String(el.className).split(' ')[0]); if (offenders.length >= 4) break; } } }
        return {client_width: w, scroll_width: sw, offenders}; }"""
    )
    return {"path": path, "viewport": width, **info, "overflow": info["scroll_width"] > info["client_width"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--user", default=os.environ.get("PROMAT_QA_USER"))
    parser.add_argument("--password", default=os.environ.get("PROMAT_QA_PASSWORD"))
    parser.add_argument("--session", default="ES-L-0001-2026-S01")
    parser.add_argument("--probe-items", default="", help="comma-separated wordlist item ids; creates a private 'UI probe' set to cover the set editor")
    parser.add_argument("--only", choices=["perf", "axe", "overflow"])
    parser.add_argument("--langs", default="de,en")
    parser.add_argument("--tag", default="run")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    args.out.mkdir(parents=True, exist_ok=True)
    langs = args.langs.split(",")
    pages = public_pages()
    report: dict[str, object] = {}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        cookies = None
        if args.user and args.password:
            context = new_context(browser)
            page = context.new_page()
            login(page, base, args.user, args.password)
            set_id = create_probe_set(page, base, args.probe_items.split(",")) if args.probe_items else None
            pages |= protected_pages(args.session, set_id)
            cookies = context.cookies()
            context.close()

        if args.only in (None, "perf"):
            perf = {}
            for name, template in pages.items():
                if name in PROTECTED_NAMES and not cookies:
                    continue
                perf[name] = measure_perf(browser, base, template.format(l="de"), cookies=cookies if name in PROTECTED_NAMES else None)
                print("perf", name, perf[name]["transfer_kb"], "KB", perf[name]["requests"], "req", perf[name]["dcl_ms"], "ms DCL")
            report["perf"] = perf
            (args.out / f"perf_{args.tag}.json").write_text(json.dumps(perf, indent=2), encoding="utf-8")

        if args.only in (None, "axe"):
            axe: dict[str, object] = {}
            for theme in ("light", "dark"):
                context = new_context(browser, theme=theme)
                if cookies:
                    context.add_cookies(cookies)
                page = context.new_page()
                for lang in langs:
                    for name, template in pages.items():
                        if name in PROTECTED_NAMES and not cookies:
                            continue
                        page.goto(base + template.format(l=lang), wait_until="networkidle")
                        page.wait_for_timeout(300)
                        axe[f"{name}|{lang}|{theme}"] = run_axe(page)
                context.close()
            report["axe"] = axe
            (args.out / f"axe_{args.tag}.json").write_text(json.dumps(axe, indent=2), encoding="utf-8")
            serious = {key: value["serious_or_critical"] for key, value in axe.items() if value["serious_or_critical"]}
            print("axe serious/critical pages:", len(serious), "of", len(axe), "| total serious/critical nodes-types:", sum(serious.values()))

        if args.only in (None, "overflow"):
            overflow: list[dict] = []
            context = new_context(browser)
            if cookies:
                context.add_cookies(cookies)
            page = context.new_page()
            for lang in langs:
                for name, template in pages.items():
                    if name in PROTECTED_NAMES and not cookies:
                        continue
                    for width in (390, 820, 1280):
                        overflow.append({"page": name, "lang": lang, **measure_overflow(page, base, template.format(l=lang), width)})
            context.close()
            report["overflow"] = overflow
            (args.out / f"overflow_{args.tag}.json").write_text(json.dumps(overflow, indent=2), encoding="utf-8")
            bad = [o for o in overflow if o["overflow"]]
            print("overflow cases:", len(bad), "of", len(overflow))
            for o in bad[:12]:
                print("  ", o["page"], o["lang"], o["viewport"], o["scroll_width"], ">", o["client_width"], o["offenders"][:2])
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
