# Back-Link Consistency Run

Datum: 2026-05-20

## Ziel

Gezielter Diagnose- und Konsistenz-Run für page-level Back-Navigation über Teaching, Research, Public/Auth-Header und Sample. Im Scope: gemeinsame Ursache finden, den Shared-Back-Link-Container stabilisieren, alte Wrapper-Sonderfälle entfernen und die dauerhaften Regeln in Spec/Repo-Instructions nachziehen. Nicht im Scope: neue Navigationsebenen, neue Buttonfamilien oder sonstige Header-Neugestaltung.

## Consulted Sources

- Root- und Scoped-Governance in `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`
- Repo-Anweisungen in `.github/instructions/repo.instructions.md` und `.github/copilot-instructions.md`
- aktive Plattform-Spec in `docs/spec/platform-data-files.md`
- Shared-Header- und Back-Link-Pfade in `app/templates/partials/_content_header.html`, `app/src/app/content_navigation.py`, `app/src/app/protected_navigation.py`
- produktive Teaching-/Research-/Sample-Templates in `app/templates/pages/teaching_page.html`, `app/templates/pages/research_speaker_profile.html`, `app/templates/pages/sample_page.html`
- relevante Layout-/Component-Familien in `app/static/css/20_layout.css` und `app/static/css/30_components.css`
- Routing-/Builder-Pfade für produktive Header-Back-Links in `app/src/app/routes/public.py`, `app/src/app/routes/auth.py`, `app/src/app/research_views.py`, `app/src/app/teaching_content.py`

## Diagnose

- Der obere Shared-Back-Link selbst war nicht das Problem. Produktive Top-Back-Links laufen bereits zentral über `_content_header.html`.
- Der sichtbare X-Versatz kam aus Wrapper-Breiten:
  - Teaching-Topic verengte den Header auf `56rem`; dadurch saß der Top-Back-Link deutlich weiter innen als auf Hub-Seiten.
  - Der Topic-Bottom-Link hing zusätzlich in `pm-reading` und bekam damit noch einmal eine schmalere eigene Achse.
  - Das Research-Speaker-Profile umschloss den Bottom-Link mit `pm-container` und erzeugte damit eine unnötige Box-/Panel-Anmutung.
- Der Sample-Dummy spiegelte diese alte Profile-Navigation noch als eigenes Wrapper-Muster statt als denselben Shared-Back-Link.

## Geänderte Bereiche

- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/templates/pages/teaching_page.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/templates/pages/sample_page.html`
- `app/tests/test_research_sessions.py`
- `.github/instructions/repo.instructions.md`
- `.github/copilot-instructions.md`
- `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- Die Shared-Header-Back-Row `pm-content-header__back` füllt jetzt bewusst die Headerbreite. Dadurch bleibt der Pill-Startpunkt auf der aktiven Content-Achse statt auf einer zufällig schmaleren Inner-Column.
- Die Teaching-Topic-Header-Hülle wurde auf die gleiche äußere Inhaltsbreite wie der Hub gehoben; Titel, Intro und Breadcrumb dürfen innerhalb davon weiter auf einer ruhigeren inneren Measure bleiben.
- Die Topic-Metadaten bleiben als eigener ruhiger Innenblock zentriert, damit der Back-Link-Fix nicht stillschweigend das restliche Headerbild nach links kippt.
- Topic-Bottom-Back-Links nutzen keinen `pm-reading`-Wrapper mehr; Speaker-Profile keinen `pm-container`-Wrapper mehr. Beide bleiben derselbe kompakte Back-Link ohne Zusatzbox.
- Der Sample-Profile-Dummy spiegelt jetzt denselben Shared-Back-Link mit target-only Label `Sprecher:innen` statt eines alten `Zurück zu ...`-Wortlauts.
- Die dauerhaften Regeln wurden in Spec und Repo-Instructions explizit nachgezogen: keine `pm-container`-/`pm-reading`-Wrapper um Shared-Back-Links, keine sichtbaren `Zurück`-/`Back to`-Hilfsphrasen, gleiche Content-Achse oben und unten.

## Verifikation

- Fokussierte Regressionstests:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation or sample_page_uses_shared_inner_shell_renderer or research_workbench_routes_render_english_shared_aria_and_actions"` -> `4 passed, 195 deselected`
- Live-DOM-Messung auf `http://127.0.0.1:8000/de/teaching/spanish`:
  - Hub-Top-Back-Link `left: 220`
- Live-DOM-Messung auf `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`:
  - Topic-Top-Back-Link `left: 220`
  - Topic-Bottom-Back-Link `left: 220`
  - Topic-Metadaten nach dem Follow-up wieder als innerer Block zentriert (`left: 316`, `width: 896`)
- Integrierte-Browser-Screenshots geprüft für:
  - `http://127.0.0.1:8000/de/teaching/spanish`
  - `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`
  - `http://127.0.0.1:8000/de/sample`
- DOM-Check auf `http://127.0.0.1:8000/de/sample`:
  - Profile-Dummy-Navigation rendert als `pm-back-link pm-back-link--bottom pm-profile-navigation`
  - sichtbares Label: `Sprecher:innen`

## Offene Punkte

- Der generische i18n-Schlüssel `research.player.back` ist weiterhin ungenutzt vorhanden. Für diesen Run war keine produktive Referenz mehr daran gebunden; ein separater Aufräum-Run kann ihn entfernen, falls der Schlüsselbestand bereinigt werden soll.
- Der Research-Speaker-Profile-Bottom-Link wurde hier über Template-/Testpfad und Sample-Spiegel abgesichert; eine echte Browser-Screenshot-QA auf einer eingeloggten produktiven Profilroute wäre ein sinnvoller ergänzender Kontrollpunkt, falls für diesen Bereich ohnehin eine Auth-QA-Session läuft.

## Nächste sinnvolle Schritte

- Optional: den ungenutzten Legacy-Schlüssel `research.player.back` in einem kleinen i18n-Aufräum-Run entfernen, sofern keine versteckte Altverwendung mehr existiert.
