# Run: Selbsteinordnung — Überarbeitung der A1/A2/B1/B2-Darstellung

**Datum:** 2026-06-23
**Scope:** UI-Labels, Hilfetexte, Tooltips, Badge-Styling; keine Datenfelder, Filterlogik oder API-Änderungen.

## Ausgangsproblem

Die bisherigen Labels „Niveau" und „Niveau zum Aufnahmezeitpunkt" suggerierten objektive Kompetenzstufen. Die A1/A2/B1/B2-Werte beruhen auf einer Selbsteinordnung der Teilnehmenden im Referenzrahmen und spiegeln nicht notwendigerweise das individuell erreichte Ausspracheniveau wider.

## Geänderte Dateien

### `app/src/app/i18n.py`

DE-Schlüssel umbenannt:
- `common.labels.level`: „Niveau" → „Selbsteinordnung"
- `common.labels.levels`: „Niveaus" → „Selbsteinordnungen"
- `common.labels.level_at_recording`: „Niveau zum Aufnahmezeitpunkt" → „Selbsteinordnung zum Aufnahmezeitpunkt"
- `research.speakers.table.level`: „Niveau" → „Selbsteinordnung"
- `research.comparison.level_label`: „Niveau" → „Nach Selbsteinordnung" (Chip-Gruppen-Label in Vergleichsansicht)

EN-Schlüssel umbenannt (analog):
- `common.labels.level`: → „Self-placement"
- `common.labels.levels`: → „Self-placements"
- `common.labels.level_at_recording`: → „Self-placement at the time of recording"
- `research.speakers.table.level`: → „Self-placement"
- `research.comparison.level_label`: → „By self-placement"

Neue Tooltip-Schlüssel:
- `common.labels.self_placement_tooltip` (DE + EN) mit Erklärungstext

### `app/src/app/research_views.py`

- **Player-Badge:** Label von reinem Level-Code (z. B. „B2") auf „B2 · Selbsteinordnung" umgestellt (`_player_summary_badges`).
- **Filter-Formular:** `tooltip`-Feld zum Level-Filtereintrag in `_speakers_filter_form` ergänzt.
- **Session-Karte:** `tooltip`-Feld zur Level-Zeile in `_session_card_rows` ergänzt.
- **Comparison-Client-State:** `levelTooltip`-Schlüssel in `client_state.labels` ergänzt.
- **contextLabel** in Katalog und Player-Summary: von `research.comparison.level_label` auf `common.labels.level` umgestellt (Feldlabel, nicht Gruppen-Header).

### `app/templates/partials/_research_filters.html`

- `<label>`-Wrapper durch `<div class="pm-research-filter-field">` mit explizitem `<label for="...">` ersetzt.
- Neue `<div class="pm-research-filter-field__label-row">` mit optionalem `<details class="pm-comparison-inline-help">` Info-Popover.

### `app/templates/pages/research_comparison.html`

- Chip-Zone um sichtbares Gruppen-Label + Info-Popover erweitert: `<div class="pm-comparison-level-header">` mit `<span class="pm-comparison-level-label">` und `<details class="pm-comparison-inline-help">`.

### `app/templates/pages/research_speaker_profile.html`

- Session-Metadaten-Grid: bedingte Darstellung mit `pm-profile-metadata__label-row` + Info-Popover, wenn `row.tooltip` gesetzt.

### `app/static/css/30_components.css`

- **`.pm-research-meta-badge--level` / `.pm-comparison-speaker-badge--level`:** `font-weight: 600` → `400`, `border-color: currentColor` → `var(--pm-border-subtle)`. Badges wirken jetzt als neutrale Kontextmetadaten statt als Kompetenz-Ranking.
- **`.pm-comparison-filter-zone--levels`:** `gap: 0.6rem` ergänzt.
- Neue Klassen: `pm-comparison-level-header`, `pm-comparison-level-label`, `pm-research-filter-field__label-row`, `pm-profile-metadata__label-row`.

### `app/tests/test_research_sessions.py`

- Zwei Testassertionen auf neue Label-Texte angepasst:
  - Sprecher-Karte: „Niveau" → „Selbsteinordnung"
  - Player-Badge: „B1" → „B1 · Selbsteinordnung"

## Testergebnis

206/206 relevante Tests bestanden. Vorher bereits schlagende Fehler (design-page, auth-phase1, teaching-content) bleiben unverändert — kein Regression durch diese Änderung.

## Konsistenzabdeckung

| Bereich | Abgedeckt |
|---|---|
| Filterbereich (Sprecher:innen) | ✓ Label + Info-Icon |
| Personenkarten | ✓ Label |
| Tabellenansicht | ✓ Spaltenheader |
| Profilseiten / Session-Karten | ✓ Label + Info-Icon |
| Sprecher:innen-Auswahl (Vergleich) | ✓ Gruppen-Label + Info-Icon |
| Player-Badges | ✓ „B2 · Selbsteinordnung" |
| Vergleichsansicht (contextLabel) | ✓ |
| DE + EN | ✓ beide Sprachen vollständig |
