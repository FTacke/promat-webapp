# Landing-Startseite: Navigationspanels statt Bild-Cards

Datum: 2026-10-09

## Ziel

Die beiden Startseiten-Cards „Aussprache erforschen“ / „Aussprache unterrichten“ durch zwei flache, vollständig klickbare, editorial gestaltete Panels mit den neuen Bildern `card_research.png` / `card_teaching.png` ersetzen.

## Consulted Sources

- `docs/spec/platform-data-files.md` (Shell- und Landing-Regeln, Asset-Lieferung)
- `app/static/css/00_tokens.css`, `10_typography.css`, `20_layout.css`, `30_components.css`, `40_cards.css`
- `app/templates/pages/landing.html`, `app/src/app/routes/public_content.py`, `app/src/app/i18n.py`

## Geänderte Bereiche

- `landing.html`: ein `<a class="landing-panel">` pro Panel (Label + Pfeil, Bildband, Titel, Text); kein „Öffnen“-Link.
- Tokens: neue `--pm-landing-panel-*`-Tokens und `--pm-icon-arrow-up-right`; alte `--pm-landing-card-*` und `--pm-card-max-inline-entry` entfernt.
- CSS: neue Panel-Komponente in `40_cards.css`, Typografie in `10_typography.css`; ungenutzte `pm-card--entry` / `pm-card--with-image` / `is-overlay`-Regeln entfernt (nur Landing nutzte sie).
- Bilder: als WebP (1200 × 675, 22 bzw. 29 KB) unter `app/static/img/cards/landing_*.webp`; alte JPGs entfernt. Die Quell-PNGs lagen nicht im Repo-Root, sondern in `Downloads` und wurden von dort verarbeitet.
- i18n: Label aus vorhandenen `section.research` / `section.teaching`; `landing.*.link` und `landing.*.image_alt` entfernt (Bilder sind dekorativ, `alt=""`).
- Spec `platform-data-files.md` angepasst.

## Wichtige Entscheidungen

- Dark Mode ohne Invertierung: Bild per `mix-blend-mode: multiply` auf einer gedämpften Platte (Token); Light Mode `darken`, dadurch verschwindet das Papierweiß nahtlos in der Panel-Fläche.
- Bildband 13:5, Ausschnitt pro Panel über Token (`object-position`), damit Wellenform und Personen nicht angeschnitten werden.

## Abweichungen

- Keine Abweichung von der Spezifikation.

## Verifikation

- Playwright-Screenshots (Desktop 1280, Mobile 390; DE/EN; Light/Dark), kein horizontaler Overflow; Hover, Tastaturfokus, Reduced Motion und Navigation zu `/de|en/research` und `/de|en/teaching` geprüft; Regressionscheck an `/de/teaching`, `/de/research`, `/de/project`.
- Screenshots: `tmp/ui-qa/2026-10-09-landing-panels/`
