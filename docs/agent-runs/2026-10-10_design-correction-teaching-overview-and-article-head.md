# Designkorrektur: Themenseiten-Übersicht und Aufsatzkopf der Forschungsdesign-Seiten

Datum: 2026-10-10

## Ziel

Die Unterrichts-Themenübersicht (`/{ui_lang}/teaching/{language}`) an die ruhige Designsprache der Sprachauswahl angleichen und den Aufsatzkopf der Forschungsdesign-Seiten (Titel, Metadaten, Abstract, Schlagwörter) typografisch beruhigen; Überlagerung der oberen Leiste prüfen.

## Consulted Sources

- `docs/spec/platform-data-files.md` (Aufsatzkopf, Corpus landing page), `docs/spec/research-capabilities.md`
- bestehende Komponenten: `.pm-nav-surface`, `pm-teaching-language-row`, `render_topic_metadata_rows`, `promat_page.html`

## Geänderte Bereiche

**Themenübersicht**
- `40_cards.css`: `.pm-teaching-topic-card` ohne Rahmen und ohne farbigen oberen Rand; Hover nur über die gemeinsame `.pm-nav-surface`-Fläche. Verfügbar: dezente violette Tönung (`--pm-nav-surface-accent`); in Vorbereitung: neutrale graue Fläche (`--pm-nav-surface-quiet`), weiterhin `<article>` ohne Link und ohne Pfeil.
- `30_components.css`: Gruppenüberschriften der Übersicht ohne Unterstreichungsmarke, kleiner (`--pm-type-group-title-*`), Beschreibung kompakter (`--pm-type-group-description-size`, `text-wrap: balance`); die Themenseite behält ihre eigene Überschriftengestaltung. Seitenabstand des Hub verringert.
- `20_layout.css`: Abstände Gruppe/Überschrift/Karten reduziert.
- `00_tokens.css`: nicht mehr benötigte Tokens `--pm-teaching-topic-card-accent`, `-accent-bar`, `-border`, `-hover-border`, `-pending-border` entfernt; `-pending-status` an `--pm-nav-text-pending` gebunden; neue semantische Tokens `--pm-type-group-title-size/-weight/-line`, `--pm-type-group-description-size`.
- Zitierkasten und Autorangaben: unverändert (keine Autor:innenangaben auf der Übersicht).

**Aufsatzkopf (Forschung)**
- Neue Struktur statt Box: `pm-article-masthead` (Seitenkopf + Metadaten, enger Abstand), `partials/_article_meta.html` (Metadaten, linksbündig, `--pm-type-nav-size` = 16 px, Trennzeichen durch Spaltenabstand ersetzt) und `partials/_article_abstract.html` (kleine Überschrift, Abstract im normalen Fließtext-Stil `promat-content-block__text`, Schlagwörter als eine Textfolge). Die frühere Abstract-Box samt Tokens `--pm-article-abstract-*` ist entfernt; es entsteht weder Fläche, Rahmen noch Farbstreifen. Eine Trennlinie zwischen Abstract und Schlagwörtern erschien nicht nötig.
- `20_layout.css`: `.promat-page`/`.pm-content` mit `grid-template-columns: minmax(0, 1fr)`, damit die breite Phänomentabelle nur in ihrem Rahmen scrollt (sonst verbreiterte sie auf Mobil Titel und Metadaten).

**Navigation / Anker**
- Die obere Leiste (`#top-app-bar`) ist `position: sticky`. Beim Laden liegt die Seitenüberschrift der Übersicht in allen geprüften Viewports (320–1920 px, Höhen 500–1080 px, DE/EN) 123–144 px unter der Leiste, auch nach Scrollen und Zurückscrollen; eine Überlagerung ist dort **nicht reproduzierbar** (beim Scrollen läuft Inhalt erwartungsgemäß unter der Leiste durch, ebenso können Ganzseiten-Screenshots die sticky Leiste mitten im Bild zeigen). Messbar war nur ein Randfall bei Sprungmarken: `--pm-shell-top-offset` war fest 64 px, die Leiste ist auf Desktop 78 px hoch (2 px Abstand bei Fußnotensprüngen). Das Token folgt jetzt `--promat-topbar-height` (15 px Abstand auf Desktop und Mobil).

**Tests**
- `test_research_sessions.py`: Kopf-/Abstract-Tests auf die neue Struktur angepasst, Test auf kastenlosen Abstract, neuer CSS-Test für flache Karten, ruhige Gruppenüberschriften und Anker-Offset.

## Wichtige Entscheidungen

- Der Abstract ist reiner Artikeltext; es wird keine neue neutrale Box eingeführt.
- Das Metadaten-Makro der Teaching-Themenseiten bleibt gemeinsam genutzt, nur im Aufsatzkopf linksbündig und größer überschrieben (scoped unter `.pm-article-meta`).
- Der Zitierkasten bleibt unverändert (gemeinsame Komponente, funktional und lesbar).

## Abweichungen

- keine.

## Verifikation

- `app/tests`: 1348 grün, 1 bekannter, bereits vorher roter Windows-Test (`test_legal_pages_render_in_image_layout…`, nicht Teil dieses Runs).
- `ci_browser_smoke.py`: 263 Checks, 0 Fehler; `ci_governance_checks.py` grün.
- Browser (Vorher/Nachher unter `tmp/ui-qa/2026-10-10-design-correction/`): Sprachauswahl, Themenübersicht, Themenseite, Erhebungsdesign; DE/EN, hell/dunkel, 1280/820/390 px; kein Überlauf; Hover, Fokus (2 px Outline) und Navigationsziel der verfügbaren Karte geprüft, nicht verfügbare Karten enthalten keinen Link.
