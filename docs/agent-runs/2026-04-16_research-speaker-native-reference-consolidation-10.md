# Research Speaker Native Reference Consolidation

Datum: 2026-04-16

## Ziel

Die verbleibenden Inkonsistenzen zwischen Speaker-Cards, Profilseiten, Player-Metakarten und Comparison-Speaker-Darstellungen beseitigen: ein kanonischer lokalisierter Native-Referenzwert statt Rohslugs oder gemischter Herkunftslabels, keine redundanten Native-Badges in bereits eindeutigem Kontext, und ein einheitlicher Profil-CTA.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/spec/research-access.md`
- `app/src/app/research_views.py`
- `app/src/app/routes/public.py`
- `app/templates/partials/_research_speaker_card.html`
- `app/templates/pages/research_player.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/40_cards.css`
- `app/static/js/pages/research-comparison.js`
- `app/tests/test_research_sessions.py`
- `app/tests/test_research_comparison.py`

## Geaenderte Bereiche

- Builder-Helfer fuer lokalisierte Native-Referenzwerte und deduplizierte Herkunftsmetadaten
- Speakers-Card-Builder, Profil-Builder, Player-Summary-Builder und Comparison-Session-Payload
- Speaker-Card-Footer-Reihenfolge und Profilheader-Badge-Rendering
- Sample-Spiegel fuer Badge-Familie, CTA-Wording und native Referenzwerte
- Aktive Specs und fokussierte Regressionen

## Wichtige Entscheidungen

- Native-Speaker verwenden jetzt systemweit einen kanonischen lokaliserten Referenzwert aus `standard_variety` und `origin_country`; wenn beide fachlich denselben Nutzerwert ergeben, wird dieser nur einmal gezeigt.
- Rohwerte wie `ES_STD` oder gemischte Kombinationen wie `Spanien` plus `Spain` gehoeren nicht mehr zur aktiven UI.
- Im Player entfaellt das redundante `Native Speaker`-Badge in den Metakarten; dort bleibt fuer Native-Sessions genau ein lokalisierter Referenz-Badge erhalten.
- In der Comparison-Oberflaeche entfaellt das redundante `Native`-Badge in den Speaker-Reihen, weil die Spalten- bzw. Listenstruktur die Rolle bereits sichtbar macht.
- Speaker-Cards verwenden fuer das Profil jetzt dieselbe CTA-Semantik wie der Player: lokalisierter Labelpfad `Profil`/`Profile` plus vorhandene Pfeil-Affordanz.
- Die Speaker-Card-Footer-Reihenfolge ist jetzt Profilaktion, danach Aufzeichnungen, dann die Task-Links.
- Profilheader verwenden fuer die sichtbaren Badges die shared research badge family statt der separaten alten `pm-profile-badge`-Sprache.

## Abweichungen

- Keine fachliche Abweichung von der aktiven Spec. `docs/spec/platform-data-files.md`, `docs/spec/research-player.md` und `docs/spec/research-access.md` wurden im selben Run auf die neue Native-Referenz- und CTA-Regel angehoben.

## Verifikation

- `get_errors` auf den geaenderten Python-, Template-, CSS-, JS-, Test- und Spec-Dateien: keine relevanten Fehler
- `Run research sessions tests`: `150 passed`
- `Push-Location c:/dev/promat/app; ../.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py -q; Pop-Location`: `9 passed`
- Render-Smoke fuer `de` und `en` ueber die echten Builder mit temporaerem Runtime-Root:
  - Speakers-Card Native-CTA: `Profil` / `Profile`
  - Speakers-Card Native-Metawerte: `Spanien` / `Spain`
  - Profilheader-Badges: `Native Speaker`, `Spanien` bzw. `Native Speaker`, `Spain`
  - Player-Native-Badges: genau ein Badge `Spanien` / `Spain`
  - Comparison-Native-Referenz: `Spanien` / `Spain`

## Offene Punkte

- In dieser Umgebung stand keine echte Screenshot-Automation fuer einen visuellen Desktop-/Mobile-Browserlauf zur Verfuegung. Die Runde ist deshalb ueber Tests plus rendernahen Builder-Smoke abgesichert, nicht ueber neue Bildartefakte unter `tmp/ui-qa/`.