# Run: Research Login Return-Target Korrektur

**Datum:** 2026-06-22  
**Scope:** Login-CTA auf öffentlichen Korpus-Root-Seiten, Return-Target-Logik, Open-Redirect-Schutz

## Ziel

Auf den öffentlichen Korpus-Orientierungsseiten (`/{ui_lang}/research/{corpus}`) soll der Login-CTA nach erfolgreicher Authentifizierung nicht mehr zur Korpus-Root zurückführen, sondern direkt zu `/{ui_lang}/research/{corpus}/speakers`. Direktklicks auf konkrete geschützte Routen bewahren weiterhin ihr exaktes Return-Target.

## Geänderte Dateien

### `app/src/app/routes/public.py`

`_resolve_href_key` um `login_next:` Präfix erweitert (nach dem `access_request`-Block, vor dem allgemeinen `:`-Splitter):

```python
if href_key.startswith("login_next:"):
    target_key = href_key[len("login_next:"):]
    next_url = _resolve_href_key(target_key, ui_lang)
    return _build_login_href(ui_lang, next_url=next_url)
```

Damit kann jede Komponente einen Login-Link mit explizit definiertem `next`-Ziel erzeugen, ohne dass `_request_next_value()` (aktueller Pfad) verwendet wird.

### `app/src/app/routes/public_content.py`

In `build_research_language_root_page`: Login-Aktion von `"href_key": "login"` auf `"href_key": f"login_next:research:{language_slug}:speakers"` umgestellt. Der `href_key` für den Access-Request-CTA bleibt unverändert.

### `app/tests/test_auth_phase1.py`

- `test_login_from_corpus_root_returns_to_same_corpus_root` → umbenannt und umgeschrieben als `test_login_from_corpus_root_redirects_to_speakers`.
- Neuer parametrisierter Test `test_corpus_root_login_href_points_to_speakers` für alle 4 Korpora × 2 UI-Sprachen (8 Fälle).
- `test_protected_research_route_click_preserves_exact_target` — Klick auf `/comparison` als unauthentifizierter Nutzer.
- `test_speakers_route_click_preserves_speakers_target` — Klick auf `/speakers` direkt.
- `test_phenomena_route_click_preserves_exact_target` — Klick auf `/phenomena`.
- `test_design_page_is_publicly_accessible_without_login` — `/design` bleibt öffentlich.
- `test_login_post_rejects_external_next_url_and_falls_back_to_default` — Open-Redirect-Schutz.
- `test_login_post_rejects_protocol_relative_external_next_url` — Protokoll-relative Angriffe.

### `docs/spec/research-access.md`

Zeile 49 aktualisiert: alte Regel „corpus root login returns to same corpus landing page" durch neue Regel mit `/speakers`-Ziel und Ausnahmeformulierung für direkte Routenklicks ersetzt.

## Testergebnisse

15 neue/aktualisierte Tests: alle grün (`15 passed`).  
1 pre-existierender Failure (`test_landing_page_renders_english_copy_and_shared_language_switch`) war vor dieser Session bereits rot — nicht durch diese Änderungen verursacht.

## Architektur-Entscheidung

Die neue `login_next:`-Konvention in `_resolve_href_key` ist die zentrale Erweiterung: Sie erlaubt es Inhaltsebenen (`public_content.py`) ein explizites Login-Ziel zu benennen, ohne URL-Generierung (`url_for`) in den Content-Layer zu ziehen. Die vorhandene recursive `href_key`-Auflösung (z. B. `research:spanish:speakers` → `/de/research/spanish/speakers`) wird wiederverwendet.
