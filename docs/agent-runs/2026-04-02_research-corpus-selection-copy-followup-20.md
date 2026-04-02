# Research-Korpusauswahl und spanische Landingpage nachgeschärft

Datum: 2026-04-02

## Ziel

Die öffentliche Forschungsübersicht sprachlich von einer Sprachwahl auf eine Korpuswahl umstellen, die Research-Cards mit datengetriebener Learner-Session-Zählung an die aktive Session-Quelle anbinden und die spanische Research-Landingpage zu einer knappen, cardfreien Einstiegsseite verdichten.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/src/app/routes/public.py`
- `app/src/app/routes/public_content.py`
- `app/src/app/research_sessions.py`
- `app/templates/partials/_navigation_drawer.html`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `app/src/app/routes/public_content.py`: Research-Auswahllabels, Korpus-Card-Titel und -Texte auf Korpuslogik umgestellt; Learner-Session-Zählung direkt an `load_language_sessions(...)` angebunden; spanische Landingpage auf knappen Text-Einstieg ohne Feature-Cards reduziert
- `app/src/app/routes/public.py`: Research-Panel nutzt jetzt Korpuswahl-Label und korpusspezifisches Back-Label; Teaching behält Sprachwahl
- `app/templates/partials/_navigation_drawer.html`: doppelte kleine Sprachzeile unter dem Sprachkopf entfernt; Back-Link-Aria-Label kontextabhängig gemacht
- `docs/spec/research-access.md`: aktive Research-Root-Regel von Sprachwahl auf Korpuswahl präzisiert
- `app/tests/test_research_sessions.py`: Regressionen für Korpus-Titel, datengetriebene Session-Zählung, spanische cardfreie Landingpage und getrennte Research-/Teaching-Auswahllabels ergänzt

## Wichtige Entscheidungen

- Die Learner-Bestandszahl wird nicht aus einer zweiten DB oder Schattenquelle berechnet, sondern aus der aktiven Research-Quelle `data/sessions/{language}/{session_id}/metadata.json` über `load_language_sessions(...)`.
- Die Research-Cards benennen bewusst Korpora (`Spanisch-Korpus` usw.) und koppeln die knappe Beschreibung an die methodische Logik aus `research/spanish/design`: kontrollierte Erhebungsformate über Wortliste, Satzliste und Interview.
- Die spanische Sprach-Landingpage bleibt bewusst schlicht: kurze Orientierung, Inline-Verweise auf Design, Sprecher:innen und Aufnahmen, keine Kartenwand.

## Normative Doku

- `docs/spec/research-access.md` definiert jetzt explizit, dass die Research-Wurzel im deutschen UI als Korpuswahl erscheint.

## Verifikation

- gezielte Render-Regressionen in `app/tests/test_research_sessions.py`
- vollständiger Testlauf: `pytest tests/test_research_sessions.py`

## Offene Punkte

- Für Französisch, Deutsch und Englisch werden aktuell noch keine Learner-Sessions gezählt; die Karten zeigen dort deshalb bewusst den leeren Bestandsstatus statt einer Platzhalterzahl.