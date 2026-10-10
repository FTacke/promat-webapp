# Unterrichtsübersicht: vertikaler Rhythmus und redundante Statusangaben

Datum: 2026-10-10

## Ziel

Auf `/{ui_lang}/teaching/{language}` mehr Weißraum und klarere Trennung der Themenabschnitte, ohne Karten, Farben, Typografie oder Zitierkasten zu ändern; Statusredundanz in Beschreibungen vorbereiteter Themen entfernen.

## Abstände (Desktop 1280 px; Mobil 390 px in Klammern; Messung im Browser vorher → nachher)

| Abstand | vorher | nachher | Token |
|---|---|---|---|
| Einleitung → erster Abschnitt | 35 (27) | 59 (51) | `--pm-teaching-intro-gap` = `--pm-space-container` (24 px, als Rand auf `.pm-teaching-group-stack`) |
| Abschnittsüberschrift → Beschreibung | 5 | 12 | `--pm-teaching-group-header-gap` = `--pm-space-xs` |
| Beschreibung → Kartenraster | 18 | 32 | `--pm-teaching-group-gap` = `--pm-space-lg` |
| Abschnitt → Abschnitt | 45 (37) | 68 (60) | `--pm-teaching-group-stack-gap` = `xl + text` (ab 721 px), `xl + xs` darunter |
| letztes Raster → Zitierkasten | 67 (59) | 67 (59) | unverändert |

Kartengröße unverändert (377 × 142 px DE, 377 × 167 px EN; 358 px breit mobil). Die Abschnitte sind allein durch Weißraum getrennt, keine Linien, Boxen oder Dekoration. Geänderte Dateien: `00_tokens.css` (Tokens, ein Media-Query-Override), `20_layout.css` (Header-Abstand der Gruppe), `30_components.css` (Rand der Gruppen-Liste, nur unter `.pm-teaching-page--hub`). Forschungsseiten wurden nicht angefasst.

## Statusredundanz

Das Präfix „In Vorbereitung: “ / „In preparation: “ entfällt in `summary` und `metadata.description` aller vorbereiteten Themen (Spanisch: R am Silbenende; Französisch: Gleitlaute, Liaison, Nasalvokale; DE und EN), im Englischen mit großem Anfangsbuchstaben. Die separate Statuszeile der Karte bleibt. Weitere vorbereitete Karten tragen nur „Beschreibung folgt.“ (Platzhalter, keine Redundanz) und blieben unverändert.

## Verifikation

- Tests (`app/tests`): alle grün außer dem bekannten, bereits vorher roten Windows-Test `test_legal_pages_render_in_image_layout…`; angepasst: Beschreibungs-/Statusprüfung, neu: Token-Test für die Übersichtsabstände. `ruff check .`, `compileall`, `ci_governance_checks.py`, `validate_teaching_content.py` grün; `ci_browser_smoke.py` 263 Checks ohne Fehler.
- Browser (`tmp/ui-qa/2026-10-10-design-correction/`, Präfix `spacing-`): DE/EN, hell/dunkel, 1280/820/390 px, kein Überlauf; die Abstände wurden per DOM-Messung bestätigt.
