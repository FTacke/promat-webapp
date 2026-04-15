# 2026-04-15 Dev Server Single Process 04

## Summary
- replaced the `python -m src.app.main` entrypoint's `app.run(...)` call with a direct Werkzeug WSGI server via `make_server(...).serve_forever()`
- targeted a Windows-specific duplicate-process issue where the workspace `.venv` server spawned a second child process under the base Python installation
- kept runtime behavior and port unchanged at `0.0.0.0:8000`, while preserving threaded request handling and optional template reload via `FLASK_DEBUG`

## Why
- live browser checks showed mixed code states because the process actually bound to `127.0.0.1:8000` was not always the workspace interpreter
- process inspection confirmed the `.venv` server launched a child `python.exe` from `C:\Users\Felix Tacke\AppData\Local\Programs\Python\Python312\python.exe`, and that child took over the listener
- the duplicate listener produced stale or inconsistent HTML for the public research sidebar and the access-request route

## Validation
- `get_errors` on `app/src/app/main.py`: no errors
- direct app-factory reproduction with the workspace interpreter and the active fallback DB port `55432`: `/access-request?ui_lang=de` returned `200`
- live runtime should be rechecked after relaunch to confirm that only the workspace `.venv` process owns port `8000`

## Files
- `app/src/app/main.py`
