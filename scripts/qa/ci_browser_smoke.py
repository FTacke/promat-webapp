"""Deterministic browser smoke for CI: the real app, a synthetic research runtime, a stubbed audio element.

    python scripts/qa/ci_browser_smoke.py [--out tmp/ui-qa/<date>-ci-smoke] [--keep-runtime]

Needs ``pip install playwright`` and ``playwright install chromium`` (see ``docs/runbooks/test-and-ci.md``). Nothing
touches real data: ``scripts/qa/fixture_runtime.py`` writes a throw-away runtime (Spanish learner pair and native
speaker, one French and one English learner) and an SQLite auth database with one QA account into a temp directory,
the app is served in-process on a free port, and ``HTMLMediaElement.play`` is replaced by a counting stub, so no
codec or timing dependency exists.

Checks (German and English where a language applies):

* public pages load without page errors or console errors (a syntax error in any page script fails here);
* the login return target brings the user back to the protected page;
* the player boots (its transport control works), shows "Alle Items"/"All items" as the selected set and keeps it;
* the comparison keeps the chosen set when speakers are toggled, adds no ``set_id`` to the URL and never calls
  ``/private-copy`` without an item edit;
* the matrix row play control turns into a stop control, stop ends playback, the audio never overlaps;
* dark and light theme both apply; no horizontal overflow at 390 px on the key pages;
* French and English corpora open in the player (fixture sessions of every corpus).

Exit code 1 on any failed check, so the CI job and the mutation guards (stop logic or icon removed, set-id forced
into the URL, "Alle Items" never selected, syntax error in ``research-player.js``) turn red.
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import threading
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
logging.getLogger("werkzeug").setLevel(logging.ERROR)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fixture_runtime import build_runtime  # noqa: E402

QA_EMAIL = "qa.smoke@example.org"
QA_PASSWORD = "Smoke-Password-1!"
SPANISH_SESSION = "ES-L-0001-2026-S01"
ALL_ITEMS = {"de": "Alle Items", "en": "All items"}

AUDIO_STUB = """
(() => {
  const state = { playing: new Set(), maxConcurrent: 0, started: 0, timers: new Map() };
  window.__audioStub = state;
  const proto = HTMLMediaElement.prototype;
  const stop = (element) => {
    clearTimeout(state.timers.get(element));
    state.timers.delete(element);
    state.playing.delete(element);
  };
  proto.play = function () {
    state.started += 1;
    state.playing.add(this);
    state.maxConcurrent = Math.max(state.maxConcurrent, state.playing.size);
    Object.defineProperty(this, "paused", { configurable: true, get: () => !state.playing.has(this) });
    this.dispatchEvent(new Event("play"));
    this.dispatchEvent(new Event("playing"));
    state.timers.set(this, setTimeout(() => {
      stop(this);
      this.dispatchEvent(new Event("ended"));
    }, 900));
    return Promise.resolve();
  };
  proto.pause = function () {
    const wasPlaying = state.playing.has(this);
    stop(this);
    if (wasPlaying) this.dispatchEvent(new Event("pause"));
  };
  proto.load = function () {};
  // Never fetch or decode the placeholder bytes: the source is only remembered.
  Object.defineProperty(proto, "src", {
    configurable: true,
    get() { return this.getAttribute("data-stub-src") || ""; },
    set(value) { this.setAttribute("data-stub-src", value); },
  });
})();
"""


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.checks = 0

    def check(self, condition: bool, label: str) -> bool:
        self.checks += 1
        print(("PASS " if condition else "FAIL ") + label, flush=True)
        if not condition:
            self.failures.append(label)
        return condition


def start_server(root: Path):
    """Serve the real application factory on a free local port with the fixture runtime; returns (server, base_url)."""
    database = root / "auth.sqlite3"
    os.environ.update(
        {
            "FLASK_ENV": "development",
            "APP_ENV": "development",
            "PROMAT_RUNTIME_ROOT": str(root),
            "PROMAT_PUBLIC_ROOT": str(root / "public"),
            "AUTH_DATABASE_URL": f"sqlite:///{database.as_posix()}",
            "FLASK_SECRET_KEY": "ci-smoke-secret-key-ci-smoke-secret-key",
            "JWT_SECRET_KEY": "ci-smoke-jwt-secret-ci-smoke-jwt-secret",
            "PROMAT_PUBLIC_BASE_URL": "http://127.0.0.1",
        }
    )
    for name in ("PROMAT_ENV", "RATE_LIMIT_STORAGE_URI", "RATELIMIT_STORAGE_URI", "VITE_GOATCOUNTER_URL"):
        os.environ.pop(name, None)
    sys.path.insert(0, str(REPO_ROOT / "app" / "src"))

    from sqlalchemy import create_engine
    from werkzeug.serving import make_server

    from app.auth.models import Base, User

    engine = create_engine(os.environ["AUTH_DATABASE_URL"])
    Base.metadata.create_all(engine)
    engine.dispose()

    from app import create_app
    from app.auth import services
    from app.extensions.sqlalchemy_ext import get_session

    app = create_app("development")
    app.config["DEBUG"] = False
    app.debug = False
    now = datetime.now(timezone.utc)
    with app.app_context(), get_session() as session:
        session.add(
            User(
                id="smoke-1",
                username="smokeuser",
                email=QA_EMAIL,
                password_hash=services.hash_password(QA_PASSWORD),
                role="user",
                is_active=True,
                must_reset_password=False,
                created_at=now,
                updated_at=now,
                first_name="Smoke",
                last_name="User",
                display_name="Smoke User",
            )
        )
    server = make_server("127.0.0.1", 0, app, threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"


def login(page, base: str, next_path: str) -> str:
    page.goto(f"{base}/login?next={next_path}", wait_until="networkidle")
    page.fill('input[name="email"]', QA_EMAIL)
    page.fill('input[name="password"]', QA_PASSWORD)
    with page.expect_navigation(wait_until="networkidle"):
        page.click('button[type="submit"]')
    return page.url


def create_set(page, base: str, label: str, item_ids: list[str]) -> str | None:
    """Create a saved private set through the real API (page context: the CSRF-aware fetch of the app)."""
    return page.evaluate(
        """async ([base, label, ids]) => {
            const post = await fetch(base + '/api/research/sets', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({corpus_language: 'spanish', label})});
            if (!post.ok) return null; const id = (await post.json()).set.set_id;
            const put = await fetch(base + '/api/research/sets/' + id + '/items', {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({items: ids.map(i => ({task: 'wordlist', item_id: i}))})});
            if (!put.ok) return null;
            const patch = await fetch(base + '/api/research/sets/' + id, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({label, lifecycle: 'saved'})});
            return patch.ok ? id : null; }""",
        [base, label, item_ids],
    )


def selected_label(page, selector: str) -> str:
    return page.eval_on_selector(selector, "select => select.options[select.selectedIndex] ? select.options[select.selectedIndex].textContent.trim() : ''")


def audio_state(page) -> dict:
    return page.evaluate("() => ({playing: window.__audioStub.playing.size, max: window.__audioStub.maxConcurrent, started: window.__audioStub.started})")


def check_public_pages(browser, base: str, report: Report, out: Path) -> None:
    for lang in ("de", "en"):
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        problems: list[str] = []
        page.on("pageerror", lambda error: problems.append(f"pageerror: {error}"))
        page.on("console", lambda message: problems.append(f"console.{message.type}: {message.text}") if message.type == "error" and "ERR_NO_BUFFER_SPACE" not in message.text else None)
        for path in (f"/{lang}", f"/{lang}/research/spanish", f"/{lang}/teaching/spanish", f"/{lang}/teaching/spanish/which-pronunciation", f"/login?ui_lang={lang}", f"/access-request?ui_lang={lang}"):
            problems.clear()
            response = page.goto(base + path, wait_until="networkidle")
            report.check(response is not None and response.status == 200, f"[{lang}] {path} loads (200)")
            report.check(not problems, f"[{lang}] {path} has no page or console errors {problems[:2]}")
        page.screenshot(path=str(out / f"{lang}_teaching_topic.png"), full_page=True)
        context.close()


def check_login_and_player(browser, base: str, report: Report, out: Path) -> None:
    for lang in ("de", "en"):
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        context.add_init_script(AUDIO_STUB)
        page = context.new_page()
        problems: list[str] = []
        page.on("pageerror", lambda error: problems.append(f"pageerror: {error}"))
        page.on("console", lambda message: problems.append(f"console.{message.type}: {message.text}") if message.type == "error" and "ERR_NO_BUFFER_SPACE" not in message.text else None)

        target = f"/{lang}/research/spanish/player/{SPANISH_SESSION}/wordlist?source=speakers"
        landed = login(page, base, target)
        report.check(landed.endswith(target), f"[{lang}] login returns to the requested protected page ({landed})")
        report.check(not problems, f"[{lang}] player loads without page or console errors {problems[:2]}")

        select = "[data-player-set-select]"
        report.check(page.locator(select).count() == 1, f"[{lang}] player offers the set select")
        report.check(selected_label(page, select) == ALL_ITEMS[lang], f"[{lang}] player shows {ALL_ITEMS[lang]!r} as the selected set")
        marked = page.eval_on_selector(select, "s => [...s.options].filter(o => o.hasAttribute('selected')).map(o => o.textContent.trim())")
        report.check(marked == [ALL_ITEMS[lang]], f"[{lang}] the server marks {ALL_ITEMS[lang]!r} as the current set option {marked}")

        toggle = page.locator("[data-player-toggle]").first
        play_label = toggle.get_attribute("data-play-label")
        pause_label = toggle.get_attribute("data-pause-label")
        toggle.click()
        page.wait_for_timeout(200)
        report.check(audio_state(page)["playing"] == 1, f"[{lang}] player toggle starts one audio element")
        report.check(toggle.get_attribute("aria-label") == pause_label, f"[{lang}] player toggle becomes the pause control")
        toggle.click()
        page.wait_for_timeout(200)
        report.check(audio_state(page)["playing"] == 0, f"[{lang}] player toggle stops the audio")
        report.check(toggle.get_attribute("aria-label") == play_label, f"[{lang}] player toggle returns to the play control")
        report.check(audio_state(page)["max"] <= 1, f"[{lang}] player never plays two audio elements in parallel")
        report.check(selected_label(page, select) == ALL_ITEMS[lang], f"[{lang}] player keeps {ALL_ITEMS[lang]!r} after playback")
        page.screenshot(path=str(out / f"{lang}_player.png"), full_page=True)

        for corpus, session in (("french", "FR-L-0001-2026-S01"), ("english", "EN-L-0001-2026-S01")):
            problems.clear()
            response = page.goto(f"{base}/{lang}/research/{corpus}/player/{session}/wordlist?source=speakers", wait_until="networkidle")
            report.check(response is not None and response.status == 200 and not problems, f"[{lang}] {corpus} fixture session opens in the player {problems[:2]}")
        context.close()


def check_comparison(browser, base: str, report: Report, out: Path) -> None:
    for lang in ("de", "en"):
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        context.add_init_script(AUDIO_STUB)
        page = context.new_page()
        problems: list[str] = []
        requests: list[str] = []
        page.on("pageerror", lambda error: problems.append(f"pageerror: {error}"))
        page.on("console", lambda message: problems.append(f"console.{message.type}: {message.text}") if message.type == "error" and "ERR_NO_BUFFER_SPACE" not in message.text else None)
        page.on("request", lambda request: requests.append(f"{request.method} {request.url}"))

        path = f"/{lang}/research/spanish/comparison"
        report.check(login(page, base, path).endswith(path), f"[{lang}] login returns to the comparison")
        page.wait_for_selector("[data-comparison-session-toggle]")
        report.check(not problems, f"[{lang}] comparison loads without page or console errors {problems[:2]}")

        select = "[data-comparison-material-preset-select]"
        before = selected_label(page, select)
        report.check(before == ALL_ITEMS[lang], f"[{lang}] comparison starts on {ALL_ITEMS[lang]!r} (got {before!r})")

        requests.clear()
        toggles = page.locator("[data-comparison-session-toggle]")
        first_two = [toggles.nth(index).get_attribute("data-comparison-session-toggle") for index in range(2)]
        for session_id in first_two:
            page.locator(f'[data-comparison-session-toggle="{session_id}"]').first.click()
            page.wait_for_timeout(400)
        for _ in range(2):  # deselect and reselect the first speaker
            page.locator(f'[data-comparison-session-toggle="{first_two[0]}"]').first.click()
            page.wait_for_timeout(400)
        report.check(selected_label(page, select) == before, f"[{lang}] toggling speakers keeps the chosen set ({selected_label(page, select)!r})")
        report.check("set_id" not in parse_qs(urlparse(page.url).query), f"[{lang}] toggling speakers adds no set_id to the URL ({page.url})")
        report.check(not any("private-copy" in entry for entry in requests), f"[{lang}] toggling speakers makes no private-copy request")
        report.check(not any(entry.startswith(("POST", "PUT", "PATCH", "DELETE")) and "/api/research/sets" in entry for entry in requests), f"[{lang}] toggling speakers writes no set to the server {[e for e in requests if '/api/research/sets' in e][:3]}")

        # A saved set stays the chosen set while speakers change; only an explicit item edit may fork it.
        set_label = f"Smoke set {lang}"
        set_id = create_set(page, base, set_label, ["wl_059", "wl_087"])
        report.check(bool(set_id), f"[{lang}] a saved set can be created through the API")
        page.goto(base + path, wait_until="networkidle")
        page.wait_for_selector("[data-comparison-session-toggle]")
        value = page.eval_on_selector(select, "(s, label) => { const o = [...s.options].find(o => o.textContent.trim().startsWith(label)); return o ? o.value : null; }", set_label)
        report.check(value is not None, f"[{lang}] the saved set is offered in the set select")
        if value is not None:
            requests.clear()
            page.select_option(select, value=value)
            page.wait_for_timeout(800)
            report.check(parse_qs(urlparse(page.url).query).get("set_id") == [set_id], f"[{lang}] selecting a saved set puts its id in the URL")
            requests.clear()
            toggle_id = page.locator("[data-comparison-session-toggle]").first.get_attribute("data-comparison-session-toggle")
            page.locator(f'[data-comparison-session-toggle="{toggle_id}"]').first.click()
            page.wait_for_timeout(600)
            changed = [entry for entry in requests if "/api/" in entry and not entry.startswith("GET")]
            report.check(selected_label(page, select).startswith(set_label), f"[{lang}] toggling a speaker keeps the saved set chosen ({selected_label(page, select)!r})")
            report.check(parse_qs(urlparse(page.url).query).get("set_id") == [set_id], f"[{lang}] toggling a speaker keeps the set id in the URL")
            report.check(not changed, f"[{lang}] toggling a speaker neither forks nor writes the set {changed[:3]}")
            page.select_option(select, value="__default__")
            page.wait_for_timeout(800)
            report.check(selected_label(page, select) == ALL_ITEMS[lang] and "set_id" not in parse_qs(urlparse(page.url).query), f"[{lang}] choosing {ALL_ITEMS[lang]!r} again drops the set id ({page.url})")

        for session_id in first_two:  # (re)select the two learners for the playback checks
            if page.locator(f'[data-comparison-selected-sessions] [data-comparison-session-toggle="{session_id}"]').count() == 0:
                page.locator(f'[data-comparison-session-toggle="{session_id}"]').first.click()
                page.wait_for_timeout(400)
        rows = page.locator("[data-comparison-play-row]")
        report.check(rows.count() >= 1, f"[{lang}] the matrix offers row play controls")
        row = rows.first
        report.check(row.get_attribute("data-playback-state") == "idle", f"[{lang}] row control starts idle")
        idle_markup = row.inner_html()
        row.click()
        page.wait_for_timeout(300)
        report.check(row.get_attribute("data-playback-state") == "playing" and row.get_attribute("aria-pressed") == "true", f"[{lang}] row control reports playing")
        report.check(row.inner_html() != idle_markup, f"[{lang}] row control swaps its icon while playing (stop icon)")
        report.check(audio_state(page)["playing"] == 1, f"[{lang}] one clip plays")
        row.click()
        page.wait_for_timeout(300)
        report.check(row.get_attribute("data-playback-state") == "idle" and audio_state(page)["playing"] == 0, f"[{lang}] stop ends the sequence and the audio")
        report.check(row.inner_html() == idle_markup, f"[{lang}] row control returns to the play icon")
        started = audio_state(page)["started"]
        row.click()  # let the whole sequence run: one clip per selected speaker, one after another
        page.wait_for_function("(started) => window.__audioStub.started >= started + 2 && window.__audioStub.playing.size === 0", arg=started, timeout=15000)
        report.check(audio_state(page)["max"] <= 1, f"[{lang}] the sequence never overlaps audio")
        # A missing clip is reported in plain, localized words (never the raw "Not Found") and ends the playback.
        page.route("**/items/*.mp3", lambda route: route.fulfill(status=404, body="Not Found"))
        missing_row = rows.nth(1)  # a row whose clips were never fetched (the client caches resolved clips)
        missing_row.click()
        page.wait_for_function("() => { const el = document.querySelector('[data-comparison-feedback]'); return el && !el.hidden && el.textContent.trim().length > 0; }", timeout=5000)
        feedback = page.inner_text("[data-comparison-feedback]")
        report.check("Not Found" not in feedback and missing_row.get_attribute("data-playback-state") == "idle", f"[{lang}] a missing clip shows a localized message and ends playback ({feedback!r})")
        page.unroute("**/items/*.mp3")
        page.screenshot(path=str(out / f"{lang}_comparison.png"), full_page=True)
        report.check(selected_label(page, select) == before, f"[{lang}] the set is still {before!r} after playback")
        context.close()


def check_theme_and_mobile(browser, base: str, report: Report, out: Path) -> None:
    for theme in ("light", "dark"):
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        context.add_init_script(f"try {{ localStorage.setItem('site-theme', '{theme}'); }} catch (e) {{}}")
        page = context.new_page()
        page.goto(f"{base}/de", wait_until="networkidle")
        applied = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        background = page.evaluate("() => getComputedStyle(document.body).backgroundColor")
        report.check(applied == theme, f"theme {theme} is applied to the document (data-theme={applied!r})")
        channels = [int(value) for value in re.findall(r"\d+", background)[:3]]
        luminance = sum(channels) / 3
        report.check((luminance < 90) == (theme == "dark"), f"theme {theme} paints a matching background {background}")
        context.close()

    context = browser.new_context(viewport={"width": 390, "height": 800})
    page = context.new_page()
    login(page, base, "/de/research/spanish/speakers")
    pages = ("/de", "/en", "/de/research/spanish", "/de/teaching/spanish/which-pronunciation", "/de/research/spanish/speakers", "/de/research/spanish/comparison", f"/de/research/spanish/player/{SPANISH_SESSION}/wordlist?source=speakers", "/en/research/spanish/comparison")
    for path in pages:
        page.goto(base + path, wait_until="networkidle")
        page.wait_for_timeout(300)
        widths = page.evaluate("() => [document.documentElement.clientWidth, document.documentElement.scrollWidth]")
        report.check(widths[1] <= widths[0], f"mobile 390: {path} has no horizontal overflow ({widths[1]} <= {widths[0]})")
    page.goto(base + "/de/research/spanish/comparison", wait_until="networkidle")
    page.screenshot(path=str(out / "mobile_de_comparison.png"), full_page=True)
    context.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=Path(tempfile.gettempdir()) / "promat-ci-smoke")
    parser.add_argument("--keep-runtime", action="store_true")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    root = Path(tempfile.mkdtemp(prefix="promat-ci-smoke-"))
    report = Report()
    try:
        build_runtime(root)
        server, base = start_server(root)
        print(f"serving the fixture runtime on {base}", flush=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            check_public_pages(browser, base, report, args.out)
            check_login_and_player(browser, base, report, args.out)
            check_comparison(browser, base, report, args.out)
            check_theme_and_mobile(browser, base, report, args.out)
            browser.close()
        server.shutdown()
    finally:
        if not args.keep_runtime:
            shutil.rmtree(root, ignore_errors=True)
    print(f"\n{report.checks} checks, {len(report.failures)} failed", flush=True)
    for failure in report.failures:
        print(f"  FAILED: {failure}", file=sys.stderr)
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
