# Legal Pages From Impressum Datenschutz

Date: 2026-06-03

Summary:
- Parsed `docs/plans/impressum_datenschutz.md` into the four explicit Markdown blocks for German Impressum, German privacy, English legal notice, and English privacy.
- Replaced the previous dummy legal-page content with safe Markdown-rendered Reading pages.
- Added localized `/de/...` and `/en/...` legal routes and pointed footer links to the language-specific `impressum` and `privacy` slugs.

Verification:
- `.\.venv\Scripts\python.exe -m pytest app\tests\test_auth_phase1.py -k "shared_footer_localizes_legal_links or privacy_page_documents_goatcounter_usage or legal_pages_render_source_markdown_without_dummy_content or goatcounter_script_renders_on_public_page_with_production_config"`
- `.\.venv\Scripts\python.exe -m ruff check app\src\app\routes\public.py app\src\app\routes\public_content.py app\tests\test_auth_phase1.py`
- Render-test coverage included `/de/impressum`, `/de/privacy`, `/en/impressum`, `/en/privacy`, plus DE/EN public footer links on `/de` and `/en`.

Residual:
- Full `app\tests\test_auth_phase1.py` ran 113/114 passing; the remaining failure is the existing `/en` landing-copy expectation for `Go to research data`, unrelated to the Legal/Footer route changes.
