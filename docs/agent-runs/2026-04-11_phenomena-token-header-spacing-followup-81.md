# Phenomena Token Header Spacing Follow-Up 81

## Ziel

Die bereits überarbeitete split `phenomena`-Oberfläche noch konsequenter systemisch nachschärfen: semantische Zustands-Tokens zentralisieren, den Editor-Header auf echten Set-Kontext umstellen, die Bearbeitbarkeit des Titels ruhiger sichtbar machen und die Set-Zeilen in der Overview mit etwas mehr Luft und klareren Binnenabständen abschließen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/runbooks/ui-change-workflow.md`
- `app/src/app/research_phenomena_views.py`
- `app/templates/pages/research_phenomena_overview.html`
- `app/templates/pages/research_phenomena_editor.html`
- `app/static/css/00_tokens.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/templates/pages/research_comparison.html`

## Umgesetzte Änderungen

- Editor-Header und Breadcrumb präzisiert:
  - Editor-Seiten verwenden jetzt den konkreten Setnamen als Seiten- und Content-Header-Titel
  - der Breadcrumb endet auf `Phänomene > [Setname]`
  - die Sekundärzeile lautet ruhig `Set bearbeiten`
- Bearbeitbarkeit des Titels sichtbar gemacht:
  - der Titel bleibt als ruhiges Inline-Feld im Arbeitskopf
  - eine kleine Edit-Affordanz mit System-Icon markiert die Bearbeitbarkeit ohne Formular- oder Admin-Optik
  - beim Bearbeiten synchronisiert das JS den sichtbaren Content-Header-Titel mit
- Save-Hierarchie nachgeschärft:
  - `Speichern` ist bei gespeicherten, unveränderten Sets visuell deaktiviert
  - Drafts bleiben auch ohne Dirty-State speicherbar
- Semantische Zustands-Tokens in `00_tokens.css` zentralisiert:
  - `muted`
  - `selected`
  - `status-neutral`
  - `status-curated`
  - `status-custom`
  - `status-saved`
  - `status-unsaved`
- Phenomena-Badges und Listenzeilen auf diese Tokens umgestellt statt einzelne Farbwerte lokal zu mischen
- Overview-Zeilen rhythmisch verfeinert:
  - etwas mehr Innenabstand pro Zeile
  - klarere Abstände zwischen Titel, Meta und Vorschau
  - mehr Luft zwischen Inhaltsblock und Aktionszone
  - kompakt geblieben, aber nicht mehr gequetscht
- Selected-Items weiter beruhigt:
  - Meta-Zeile jetzt in normaler Groß-/Kleinschreibung
  - `Wortliste · n` und `Satzliste · n` statt knapper Einzeltypen
  - rechte Aktionszone als zusammenhängige, leisere Gruppe
- Materiallisten noch klarer über Flächenzustände statt harte Borders differenziert:
  - unselected = ruhiger, heller, leiser
  - selected = leichte Tönung und präziseres Check-Signal

## Wiederverwendete oder erweiterte Systemmuster

- `pm-comparison-speaker-badge` als Badge-Basisfamilie
- `pm-research-button` und `pm-research-inline-action` für Aktionshierarchie
- `pm-player-list__number` und `pm-player-panel__title` für Listen- und Panelrhythmus
- bestehende `pm-icon-mask`-Familie, erweitert um ein `edit`-Icon statt featurelokaler Sondergrafik
- zentrale Surface-, Border- und Text-Tokens aus `00_tokens.css`, ergänzt um semantische Status- und Zustandsvarianten

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sets.py tests/test_research_phenomena.py`
  - Ergebnis: `26 passed`
- Frische isolierte Browser-QA auf einer Testinstanz unter `127.0.0.1:8014`
- Zusätzlicher isolierter Screenshot für echten `selected`/`muted`-Mischzustand unter `127.0.0.1:8015`
- Shared-CSS-Regression auf `comparison` per Screenshot gegengeprüft

## Screenshots

- `tmp/ui-qa/phenomena-followup-81/overview-default.png`
- `tmp/ui-qa/phenomena-followup-81/overview-auth-custom-actions.png`
- `tmp/ui-qa/phenomena-followup-81/editor-head.png`
- `tmp/ui-qa/phenomena-followup-81/editor-note.png`
- `tmp/ui-qa/phenomena-followup-81/editor-wordlist-selected-muted.png`
- `tmp/ui-qa/phenomena-followup-81/editor-textlist.png`
- `tmp/ui-qa/phenomena-followup-81/editor-selected-items.png`
- `tmp/ui-qa/phenomena-followup-81/editor-selected-muted-mixed.png`
- `tmp/ui-qa/phenomena-followup-81/comparison-regression.png`

## Visuelle Bewertung

- Die Overview-Zeilen lesen sich jetzt kompakt, aber nicht gedrängt; Titel, Meta und Vorschau sind klar getrennt und die rechte Aktionszone hat genug Abstand.
- Der Editor wirkt stärker wie Teil derselben App-Familie wie `comparison` und `player`: ruhigere Zustände, gleiche Badge-Grammatik, dichtere Materialzeilen und ein klarerer Arbeitskopf.
- Die Bearbeitbarkeit des Setnamens ist sichtbar, ohne dass der Kopf in eine grobe Formmaske kippt.
- Die neuen semantischen Tokens reduzieren den Phenomena-spezifischen Farb-Wildwuchs und machen spätere gleichartige Zustände an einer Stelle wartbarer.

## Sample

- Kein Update an `sample`, weil dort keine entsprechend gespiegelte Phenomena-Overview oder Editor-Komponente vertreten ist.