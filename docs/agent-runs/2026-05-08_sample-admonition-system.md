# sample-admonition-system

Datum: 2026-05-08

## Ziel

Die Sample-Seite sollte ein systematisches PROMAT-Admonition-System erhalten, das sichtbar aus der bestehenden Card-Familie abgeleitet ist: gemeinsame Geometrie, Token-Hierarchie statt Einzelstile, acht semantische Varianten, zugängliche Toggle-Unterstützung für collapsible Fälle und echte, lokalisierte sichtbare Titel statt technischer Variantennamen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- root `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `docs/runbooks/ui-change-workflow.md`
- Repo memory `/memories/repo/promat-research-ui-notes.md`

## Geänderte Bereiche

- `app/static/css/00_tokens.css`
- `app/static/css/10_typography.css`
- `app/static/css/40_cards.css`
- `app/static/js/modules/core/entry.js`
- `app/static/js/modules/core/admonitions.js`
- `app/templates/partials/_admonition.html`
- `app/templates/pages/sample_page.html`
- `app/src/app/routes/public.py`
- `app/src/app/i18n.py`
- `app/tests/test_research_sessions.py`

## Wichtige Entscheidungen

- Die Token-Hierarchie wurde bewusst gestuft: globale primitive und semantische Farbwerte bleiben in `00_tokens.css`, card-spezifische Geometrie- und Texttokens leben in `40_cards.css`, und die Admonition-Basis leitet ihre lokalen Variablen direkt aus diesen Card-Tokens ab.
- Der Demo-Stack wurde auf eine leseruhige Breite begrenzt (`--pm-admonition-stack-max-width`, `--pm-admonition-stack-gap`), damit die Admonitions auf der Sample-Seite nicht mehr wie durchlaufende Querbänder, sondern wie kuratierte Card-Blöcke erscheinen.
- Die finale Admonition-Shell liest sich als vollständige Card: die gesamte Fläche bleibt semantisch, aber ruhig getönt; der frühere Tabellenkopf-Eindruck wurde entfernt; Border, Radius und Innenabstände kommen aus der Card-Geometrie bzw. engen Admonition-Ableitungen davon.
- Header und Body teilen jetzt dieselbe Shell statt zweier gegeneinander gestellter Flächen. Der Header bleibt eine saubere Flex-/Grid-Zeile für Icon, Titel und optionalen Toggle; der Body hängt darunter über einen festen Textkorridor, der an der Titelkante ausgerichtet ist.
- Varianten (`hoermal`, `regel`, `tip`, `praxis`, `context`, `cite`, `summary`, `weiterlesen`) setzen weiterhin nur semantische Werte wie Hintergrund, Border, Akzent, Icon- und Titelfarbe. Layout, Radius, Padding und typografischer Rhythmus werden nicht mehr je Variante dupliziert.
- Die sichtbare Ausgabe wurde in ein Shared-Macro verschoben, damit die Sample-Seite und spätere Wiederverwendung denselben DOM-Aufbau, dieselben Accessibility-Attribute und dieselbe Toggle-Logik teilen.
- Die beiden collapsiblen Beispiele wurden als echte Button-gesteuerte Bereiche mit `aria-expanded`, `aria-controls` und synchronem `hidden`-State umgesetzt.
- Es war keine Spec-Änderung nötig, weil weder Shell-Hierarchie noch Routing- oder Datenregeln geändert wurden; die Arbeit erweitert eine bestehende Shared-UI-Familie und aktualisiert die Sample-/QA-Spiegelfläche.

## Abweichungen

- `get_errors` meldete nur bestehende CSS-Kompatibilitätswarnungen für bereits genutzte `color-mix(...)`- und `text-wrap`-Features sowie ein Jinja-bedingtes ARIA-False-Positive auf dynamischen Attributwerten im neuen Macro. Die Runtime-Validierung im Browser zeigte dabei korrektes Verhalten.

## Verifikation

- `pytest app/tests/test_research_sessions.py -q -k sample_page` -> `10 passed, 172 deselected`
- denselben fokussierten Test nach jeder visuellen Nachschärfung erneut ausgeführt -> jeweils `10 passed, 172 deselected`
- Browser-QA auf `/de/sample`: Admonitions lesen sich als eigenständige Cards mit ruhiger Shell, großzügigerem Innenraum, sauberem Icon-/Titel-/Toggle-Header und serifenbasiertem Lesetext
- Browser-QA auf `/en/sample`: englische Titel und Texte korrekt, längere Zeilen bleiben layoutstabil und die Materialität bleibt konsistent zur deutschen Fassung
- Browser-QA der Toggle-Interaktion: `Hörbeispiel` initial offen, `Weiterlesen` initial geschlossen, Klick öffnet den Bereich und synchronisiert `aria-expanded` sowie `hidden`
- Fremdregression auf `/en/research`: bestehende Corpus-Cards blieben visuell unverändert und zeigten keine Nebenwirkung der Shared-CSS-Anpassung

## Offene Punkte

- Keine offenen funktionalen Punkte im umgesetzten Slice.

## Nächste sinnvolle Schritte

- Falls Admonitions künftig außerhalb der Sample-Seite produktiv eingesetzt werden, die Macro-Verwendung direkt in der jeweiligen Zieloberfläche übernehmen, statt neue lokale Varianten oder abweichende DOM-Strukturen einzuführen.