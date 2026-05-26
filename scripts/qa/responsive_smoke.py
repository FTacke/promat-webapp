from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright


"""Manual responsive smoke QA for a local PROMAT dev server.

Writes screenshots and JSON summaries to tmp/ui-qa/<run-id>/.
Protected routes require explicit QA credentials via flags or environment.
"""


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
VIEWPORTS = {
    "360": (360, 800),
    "390": (390, 844),
    "768": (768, 1024),
    "1440": (1440, 900),
}
ROUTES = [
    ("project", "/de/project/about", ["360", "390", "768", "1440"], False),
    ("login", "/login?ui_lang=de", ["360", "390", "768", "1440"], False),
    ("access-request", "/access-request?ui_lang=de", ["360", "390"], False),
    ("research-root", "/de/research/spanish", ["360", "390", "768", "1440"], False),
    ("speakers-card", "/de/research/spanish/speakers", ["360", "390", "768"], True),
    ("player-wordlist", "/de/research/spanish/player/ES-L-0001-2026-S01/wordlist", ["390", "768"], True),
    ("player-interview", "/de/research/spanish/player/ES-L-0001-2026-S01/interview", ["390", "768"], True),
    ("teaching-root", "/de/teaching/spanish", ["360", "390", "768", "1440"], False),
    ("teaching-audio-datawrapper", "/de/teaching/spanish/which-pronunciation", ["360", "390", "768"], False),
    ("admin-users", "/admin/users/page?ui_lang=de", ["360", "768"], True),
]


def slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value).strip("-").lower()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PROMAT responsive smoke QA.")
    parser.add_argument("--run-id", required=True, help="Output folder suffix under tmp/ui-qa.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--email", default=os.environ.get("PROMAT_QA_EMAIL", ""))
    parser.add_argument("--password", default=os.environ.get("PROMAT_QA_PASSWORD", ""))
    args = parser.parse_args()
    if not args.email or not args.password:
        parser.error("Protected-route smoke checks require --email and --password or PROMAT_QA_EMAIL/PROMAT_QA_PASSWORD.")
    return args


def collect_metrics(page: Page) -> dict[str, Any]:
    return page.evaluate(
        """
        () => {
          const vw = window.innerWidth;
          const doc = document.documentElement;
          const body = document.body;
          const scrollWidth = Math.max(doc.scrollWidth, body ? body.scrollWidth : 0);
          const rectFor = (selector) => {
            const el = document.querySelector(selector);
            if (!el) return null;
            const rect = el.getBoundingClientRect();
            return {
              left: Math.round(rect.left),
              top: Math.round(rect.top),
              right: Math.round(rect.right),
              bottom: Math.round(rect.bottom),
              width: Math.round(rect.width),
              height: Math.round(rect.height),
              className: String(el.className || ''),
            };
          };
          const offenders = [];
          for (const el of Array.from(document.querySelectorAll('body *'))) {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            if (
              rect.width > 0 &&
              rect.height > 0 &&
              style.display !== 'none' &&
              style.visibility !== 'hidden' &&
              (rect.right > vw + 2 || rect.left < -2)
            ) {
              offenders.push({
                tag: el.tagName.toLowerCase(),
                id: el.id || '',
                className: String(el.className || '').slice(0, 140),
                left: Math.round(rect.left),
                right: Math.round(rect.right),
                width: Math.round(rect.width),
                overflowX: style.overflowX,
              });
            }
          }
          return {
            pageOverflow: scrollWidth - vw,
            scrollWidth,
            wrapper: rectFor('.pm-content-wrapper, .md3-content-wrapper'),
            footerShell: rectFor('#site-footer'),
            footerInner: Boolean(document.querySelector('.promat-footer')),
            topbar: rectFor('.promat-topbar'),
            drawerButton: rectFor('[data-action="open-drawer"]'),
            audioCount: document.querySelectorAll('audio').length,
            datawrapperCount: document.querySelectorAll('iframe[src*="datawrapper"]').length,
            offenders: offenders.slice(0, 8),
          };
        }
        """
    )


def screenshot(page: Page, screenshot_dir: Path, viewport: str, name: str) -> str:
    path = screenshot_dir / f"{viewport}_{slug(name)}.jpg"
    page.screenshot(path=str(path), type="jpeg", quality=72, full_page=False)
    return path.name


def login(page: Page, base_url: str, email: str, password: str) -> dict[str, Any]:
    page.goto(base_url + "/login?ui_lang=de", wait_until="networkidle")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    return {"url_after_login": page.url, "logged_in": "/login" not in page.url}


def visit(page: Page, base_url: str, screenshot_dir: Path, viewport: str, name: str, path: str) -> dict[str, Any]:
    response = page.goto(base_url + path, wait_until="networkidle")
    page.wait_for_timeout(250)
    return {
        "name": name,
        "path": path,
        "url": page.url,
        "status": response.status if response else None,
        "screenshot": screenshot(page, screenshot_dir, viewport, name),
        "metrics": collect_metrics(page),
    }


def drawer_check(page: Page, base_url: str, screenshot_dir: Path, viewport: str) -> dict[str, Any]:
    page.goto(base_url + "/de/research/spanish", wait_until="networkidle")
    page.wait_for_timeout(250)
    button = page.locator('[data-action="open-drawer"]')
    result: dict[str, Any] = {"button_visible": button.is_visible()}
    if not result["button_visible"]:
        return result
    button.click()
    page.wait_for_timeout(250)
    dialog = page.locator("#navigation-drawer-modal")
    result["opened"] = dialog.evaluate("el => el.open")
    result["screenshot"] = screenshot(page, screenshot_dir, viewport, "drawer-open")
    result["body_overflow"] = page.evaluate("() => getComputedStyle(document.body).overflow")
    page.keyboard.press("Escape")
    page.wait_for_timeout(250)
    result["closed_after_escape"] = not dialog.evaluate("el => el.open")
    return result


def validation_check(page: Page, base_url: str, screenshot_dir: Path, viewport: str) -> dict[str, Any]:
    page.goto(base_url + "/access-request?ui_lang=de", wait_until="networkidle")
    page.click("[data-access-request-submit]")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(250)
    return {
        "viewport": viewport,
        "status_visible": page.locator(".pm-auth-message.is-error").is_visible(),
        "field_errors": page.locator(".pm-auth-field__error").count(),
        "screenshot": screenshot(page, screenshot_dir, viewport, "access-request-validation"),
        "metrics": collect_metrics(page),
    }


def run() -> dict[str, Any]:
    args = parse_args()
    out_dir = Path("tmp/ui-qa") / args.run_id
    screenshot_dir = out_dir / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {"routes": [], "drawer": [], "validation": [], "login": [], "console": [], "static_404": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for viewport, size in VIEWPORTS.items():
            context = browser.new_context(viewport={"width": size[0], "height": size[1]}, device_scale_factor=1)
            page = context.new_page()
            page.on("console", lambda msg: results["console"].append({"viewport": viewport, "type": msg.type, "text": msg.text}))
            page.on(
                "response",
                lambda response: results["static_404"].append(response.url)
                if response.status == 404 and "/static/" in response.url
                else None,
            )
            if viewport in {"360", "390"}:
                results["drawer"].append({"viewport": viewport, **drawer_check(page, args.base_url, screenshot_dir, viewport)})
                results["validation"].append(validation_check(page, args.base_url, screenshot_dir, viewport))
            authed = False
            for name, path, viewports, needs_login in ROUTES:
                if viewport not in viewports:
                    continue
                if needs_login and not authed:
                    results["login"].append({"viewport": viewport, **login(page, args.base_url, args.email, args.password)})
                    authed = True
                results["routes"].append({"viewport": viewport, **visit(page, args.base_url, screenshot_dir, viewport, name, path)})
            context.close()
        browser.close()

    overflows = [
        {"viewport": row["viewport"], "name": row["name"], "overflow": row["metrics"]["pageOverflow"], "offenders": row["metrics"]["offenders"]}
        for row in results["routes"]
        if row["metrics"]["pageOverflow"] > 2
    ]
    validation_overflows = [
        {"viewport": row["viewport"], "name": "access-request-validation", "overflow": row["metrics"]["pageOverflow"], "offenders": row["metrics"]["offenders"]}
        for row in results["validation"]
        if row["metrics"]["pageOverflow"] > 2
    ]
    console_errors = [row for row in results["console"] if row["type"] == "error"]
    expected_validation_console = [row for row in console_errors if "400 (BAD REQUEST)" in row["text"]]
    runtime_console_errors = [row for row in console_errors if row not in expected_validation_console]

    summary = {
        "run_id": args.run_id,
        "route_checks": len(results["routes"]),
        "drawer_checks": len(results["drawer"]),
        "validation_checks": len(results["validation"]),
        "overflow_findings": len(overflows) + len(validation_overflows),
        "static_404": results["static_404"],
        "runtime_console_errors": runtime_console_errors,
        "expected_validation_console": expected_validation_console,
    }
    (out_dir / "smoke_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "overflow_results.json").write_text(json.dumps(overflows + validation_overflows, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
