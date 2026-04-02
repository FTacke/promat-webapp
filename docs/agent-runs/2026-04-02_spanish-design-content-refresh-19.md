# Spanisch-Designseite inhaltlich ersetzt

Datum: 2026-04-02

## Ziel

Die öffentliche Forschungsseite `de/research/spanish/design` inhaltlich durch die bereitgestellte Fassung aus `Design.md` ersetzen und dabei das bestehende PROMAT-Standardlayout mit `intro` und gegliederten Inhaltssektionen beibehalten.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `docs/AGENTS.md`
- `app/AGENTS.md`
- `app/src/app/routes/public_content.py`
- `app/templates/pages/promat_page.html`
- `app/templates/partials/_content_header.html`
- `c:\Users\Felix Tacke\Downloads\Design.md`

## Geänderte Bereiche

- `app/src/app/routes/public_content.py`: Inhaltsblock für die öffentliche Spanisch-Seite `research/design` vollständig neu strukturiert und textlich ersetzt
- `docs/agent-runs/2026-04-02_spanish-design-content-refresh-19.md`: Run-Log für diesen Lauf ergänzt

## Wichtige Entscheidungen

- Die bereitgestellte Fassung wurde nicht als Markdown eingebettet, sondern in die bestehende strukturierte Seitendefinition mit `intro`, Abschnittsüberschriften, Fließtext und Literatur-Bullets überführt.
- Titel, Route und Standardlayout der Seite bleiben unverändert; geändert wurde nur der öffentliche Seiteninhalt.

## Abweichungen

- Keine Abweichung von den aktiven Spezifikationen oder Routing-Konventionen.
- Keine Änderung unter `docs/spec/`, weil keine fachliche Regel oder Architekturvorgabe geändert wurde.

## Verifikation

- Bestehende Content-Struktur in `app/src/app/routes/public_content.py` gegen das Renderlayout in `app/templates/pages/promat_page.html` geprüft
- Patch auf Syntaxkonsistenz und Datenstruktur (`intro`, `sections`, `paragraphs`, `bullets`) validiert

## Offene Punkte

- Die Literaturliste wird im aktuellen Standardlayout als einfache Bullet-Liste ohne typografische Auszeichnung oder klickbare Spezialformatierung gerendert.

## Nächste sinnvolle Schritte

- Die Seite im Browser auf Lesefluss und Zeilenumbrüche prüfen.
- Bei Bedarf die Literaturliste später in ein spezielleres Publikationslayout überführen.