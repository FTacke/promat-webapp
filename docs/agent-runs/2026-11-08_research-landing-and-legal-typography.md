# Forschungs-Landingpage und Rechtstexte gestalterisch vereinheitlichen

Datum: 2026-11-08

## Ziel

1. `/{ui_lang}/research` wie die Unterrichts-Landingpage: keine Desktop-Sidebar, zentrierter Titel „Lernendenaussprache erforschen“ / „Researching Learner Pronunciation“ mit einem Einleitungssatz, die vier Korpuskarten unverändert in einem zentrierten Zweispaltenraster.
2. Impressum und Datenschutz (DE/EN) in der Lesetypografie der wissenschaftlichen Artikelseite (`/de/research/spanish/design`), Rechtstexte unverändert.

## Consulted Sources

- `docs/spec/platform-data-files.md` (Shell/Sidebar, Forschungsübersicht, Footer/Rechtsseiten)
- `AGENTS.md` (UI Change Discipline, Repo-Hygiene)
- `app/templates/pages/promat_page.html`, `pages/teaching_page.html`, `partials/_content_header.html`
- `app/static/css/00_tokens.css`, `10_typography.css`, `20_layout.css`, `30_components.css`, `layout.css`

## Geänderte Bereiche

- `app/src/app/i18n.py`: `research.overview.title` und `research.overview.cards_aria` neu; der ungenutzte Schlüssel `research.overview.intro` trägt jetzt den neuen Einleitungssatz (DE/EN).
- `app/src/app/routes/public_content.py` (`build_research_select_page`): Titel, `overview_intro`, `layout: "section-overview"`, lokalisiertes ARIA-Label der Kartengruppe.
- `app/src/app/routes/public.py` (`_render_promat_page`): Layout `section-overview` setzt die Body-Klasse `page-section-overview`.
- `app/templates/pages/promat_page.html`: Artikelklasse `pm-section-overview`, Einleitungsabschnitt `pm-section-overview__intro` (Struktur wie `pm-teaching-overview__intro`), hartcodiertes deutsches `aria-label="Sprachbereiche"` durch den lokalisierten Wert ersetzt.
- CSS, nur Erweiterung bestehender Regeln (keine neuen Farben, Schriften oder Pixelwerte):
  - `layout.css`: die Desktop-Regel, die auf Teaching-Seiten die Sidebar ausblendet und die Spalte zentriert, gilt auch für `page-section-overview`.
  - `20_layout.css` / `30_components.css`: Teaching-Overview-Selektoren (zentrierter Header 58rem, Intro-Abschnitt, Intro-Textstil, Artikel-Gap `--pm-space-grid`, mobile Intro-Größe) um die Forschungsübersicht erweitert; Kartenraster der Übersicht auf `--pm-layout-component-width`, einspaltig unter 768 px über die bestehende Regel.
  - `10_typography.css`: `.promat-content-block__body :where(h2)` in die Serif-Familie der Überschriften, `.promat-content-block__body :where(p, ul, ol)` in die Lesetypografie (`--pm-type-reading-*`) aufgenommen.
  - `20_layout.css`: `h2 + h3` erhält den bestehenden Abstand nach h2 (`--pm-reading-heading-gap-after-h2`); Adress-/Kontaktblöcke (`p:has(> br)` im Markdown-Body) nutzen `--pm-literature-line-height`.
- `app/tests/test_research_sessions.py`: Shell-Test an die Body-Klasse angepasst; neuer parametrisierter Test (DE/EN) für exakten Titel, exakten Einleitungstext, Reihenfolge Titel → Einleitung → Karten, kein Zusatz-h2, vier Korpuslinks.
- `docs/spec/platform-data-files.md`: Sidebar-Ausnahme, neue Regel für die Forschungsübersicht (ersetzt „ohne Intro“), neue Regel zur Typografie der Rechtsseiten.

## Wichtige Entscheidungen

- Kein Wechsel auf das Teaching-Template: Research bleibt im generischen `promat_page.html`; die Teaching-Regeln werden per zusätzlichem Selektor geteilt statt kopiert.
- Die Sidebar-Markup bleibt auf der Forschungsübersicht erhalten (wie bei Teaching), weil sie die Grundlage des mobilen Drawers ist; ausgeblendet wird nur die Desktop-Spalte.
- `.promat-content-block__body` wird ausschließlich von den Rechtsseiten verwendet; die Typografie-Erweiterung wirkt daher nur dort. Die Rechtsseiten behalten ihre schmale „Rechtliches“-Sidebar, wie die Artikelseite ihre Korpus-Sidebar.

## Abweichungen

- Keine. Rechtstexte (`content/legal/impressum_datenschutz.md`) und Korpuskarten-Inhalte unverändert.

## Verifikation

- Browserpass auf eigener QA-Instanz (Port 8011, aktueller Code), Screenshots unter `tmp/ui-qa/2026-11-08-research-landing-legal/` (`before/`, `after/`): `/de|en/research`, `/de|en/impressum`, `/de|en/privacy`, `/de|en/teaching`, `/de/research/spanish`, `/en/research/french`, `/de/research/spanish/design`, `/de/project/about`, eine Teaching-Themenseite; 1440/820/390 px, Light und Dark (Theme über `site-theme` gesetzt).
- Teaching-Übersicht und Design-Artikel vorher/nachher pixelidentisch (1440 px, Light).
- DOM-Prüfung: die neuen Geschwister-Regeln (`h2 + h3`, Adressblöcke) treffen nur Impressum und Datenschutz, keine Projekt-, Teaching- oder Artikelseite.
- Korpusseiten und Unterseiten zeigen die linke Navigation unverändert.
- Tests: siehe Abschnitt „Ergebnis der Testsuite“.

## Ergebnis der Testsuite

- `pytest` gesamt: 1606 passed, 2 skipped, 12 deselected (PostgreSQL-Tests lokal ohne Container übersprungen bzw. abgewählt).
- `ruff check app/src app/tests`: ohne Befund. `scripts/ci_governance_checks.py`: alle Checks bestanden.

## Offene Punkte

- Keine bekannten.

## Nächste sinnvolle Schritte

- Optional: die `pm-teaching-overview__*`-Klassen langfristig zu einer neutralen Overview-Familie zusammenführen, wenn eine dritte Übersicht hinzukommt.
