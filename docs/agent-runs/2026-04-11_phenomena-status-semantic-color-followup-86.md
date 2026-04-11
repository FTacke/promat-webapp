# Phenomena Status Semantic Color Follow-Up 86

Datum: 2026-04-11

## Ziel

Die Status- und Metafarbigkeit im produktiven `phenomena`-UI semantisch sauberer machen: `curated` weg vom braunen Praxis-Ton in Richtung `book-accent`, `ungespeichert` auf eine echte Warning-Semantik umstellen und die Item-Zahl in der Overview lesbarer machen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/runbooks/ui-change-workflow.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/static/css/00_tokens.css`
- `app/static/css/30_components.css`

## Geänderte Bereiche

- semantische Status-Tokens in `app/static/css/00_tokens.css`
- Badge- und Count-Styling in `app/static/css/30_components.css`

## Wichtige Entscheidungen

- `curated` verwendet jetzt eine ruhige `book-accent`-nahe Blaufläche statt des vorherigen warmen Praxis-Tons.
- `ungespeichert` wurde semantisch auf den Warning-Pfad umgestellt; damit bleibt `gespeichert` klar vom nativen Türkis getrennt und `ungespeichert` nutzt keinen fachfremden Praxis-Ton mehr.
- Die Overview-Item-Zahl wurde auf `book-muted` mit normalem Font-Weight reduziert, damit sie lesbarer bleibt und nicht mit dem Settitel konkurriert.

## Abweichungen

- Keine Abweichung von der aktiven Spec.

## Verifikation

- Editor-Problems-Check für die geänderten CSS-Dateien ohne Fehler
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py tests/test_research_phenomena.py`
  - Ergebnis: `15 passed`
- Headless-Edge-Browser-Check gegen `http://127.0.0.1:8000`
  - `curated`-Badge live mit `book-accent`-naher Fläche und Accent-Border bestätigt
  - `ungespeichert`-Badge live mit Warning-Farbe bestätigt
  - Overview-Count live mit dunklerer Farbe und Font-Weight `400` bestätigt
  - `comparison` als Shared-CSS-Regression gegengeprüft, ohne sichtbare Nebenwirkung auf die Badge-Familie

## Offene Punkte

- Kein weiterer offener Defekt aus diesem reinen Farb- und Lesbarkeits-Follow-up.

## Nächste sinnvolle Schritte

- Falls gewünscht, kann als nächster rein visueller Feinschliff noch die sichtbare Badge-Copy `curated`/`custom` auf endgültige deutsche Arbeitsbegriffe umgestellt werden.