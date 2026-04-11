# Phenomena Unsaved Danger Color Follow-Up 88

Datum: 2026-04-11

## Ziel

Die sichtbare `ungespeichert`-Badge im produktiven `phenomena`-UI von einem bräunlichen Warning-Ton auf eine klarer warnende, rötliche Semantik umstellen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/static/css/00_tokens.css`
- `app/static/css/30_components.css`

## Geänderte Bereiche

- Status-Tokens in `app/static/css/00_tokens.css`
- Badge-Styling in `app/static/css/30_components.css`

## Wichtige Entscheidungen

- `ungespeichert` verwendet nicht länger die Warning-Familie auf Basis des bräunlichen `book-adm-warning`, sondern die Danger-Familie auf Basis von `book-adm-danger`.
- Die Fläche bleibt bewusst hell getönt, damit die Badge als Warnhinweis lesbar bleibt, ohne wie ein destruktiver Primär-CTA zu wirken.

## Abweichungen

- Keine Abweichung von der aktiven Spec.

## Verifikation

- Editor-Problems-Check für die geänderten CSS-Dateien

## Offene Punkte

- Keine weiteren offenen Punkte aus diesem gezielten Farb-Follow-up.

## Nächste sinnvolle Schritte

- Falls gewünscht, kann als nächster Feinschliff die gesamte Statusfamilie `saved`/`unsaved`/`curated` noch einmal im Browser gegeneinander auf Balance und Kontrast geprüft werden.