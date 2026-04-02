# Forschungs-Shell-Hierarchie räumlich entkoppelt

Hinweis: Dieser Zwischenstand wurde im Folge-Run zur systemweiten Sidebar-Header-Regel aktualisiert; die gemeinsame Innen-Shell behält den Bereichsheader inzwischen auch in Forschung wieder bei.

Datum: 2026-04-02

## Ziel

Die Forschungsseiten räumlich klarer staffeln: globalen Header als eigene Ebene beruhigen, Forschungs-Shell verbreitern und lokale Bereichsnavigation als echte lokale Spalte tiefer ansetzen. Die damals temporär entfernte Bereichswiederholung in der Forschungs-Übersicht wurde später wieder zugunsten eines systemweiten Sidebar-Headers vereinheitlicht.

## Geänderte Bereiche

- `app/static/css/00_tokens.css`: zentrale Alias-Tokens für aktuelle Shell-Breiten und Abstände ergänzt; Forschungs-spezifische Shell-, Sidebar-, Divider- und Header-Abstände als Tokens eingeführt
- `app/static/css/layout.css`: Shell systemisch auf aktuelle Layout-Tokens umgestellt; Forschungsseiten erhalten breitere Shell, größeren Startabstand und eine subtile Sidebar-Trennlinie
- `app/static/css/20_layout.css`: Seiten- und Feature-Breiten auf die aktuellen Shell-Tokens umgestellt
- `app/static/css/30_components.css`: Topbar als dreizonige Desktop-Ebene organisiert; Header-Unterkante läuft ohne zusätzliche Trennlinie; Footer und Panel folgen den aktuellen Shell-Tokens
- `app/templates/partials/_top_app_bar.html`: globale Navigation in die Primärzeile zwischen Marke und Utilities gezogen
- `app/templates/partials/_navigation_drawer.html`: Panel-Kontext mit strukturellen Klassen und Data-Attributen präzisiert
- `app/src/app/routes/public.py`: Forschungs-Übersicht damals temporär ohne Bereichskopf konfiguriert; später systemweit wieder auf Sidebar-Header vereinheitlicht
- `app/tests/test_research_sessions.py`: Render-Regressionen für Forschung-Übersicht und Spanisch-Unterseite ergänzt

## Normative Doku

- Keine Änderung unter `docs/spec/`: es handelt sich um Layout-Hierarchie, Shell-Breiten und Navigationsinszenierung, nicht um eine Änderung aktiver fachlicher Regeln.

## Verifikation

- Route-Render-Prüfung für `/de/research`: damals noch ohne Sidebar-Section-Header; dieser Zwischenstand wurde später wieder vereinheitlicht
- Route-Render-Prüfung für `/de/research/spanish`: Sprachkontext blieb erhalten; der Bereichsheader wurde im späteren Follow-up wieder systemweit ergänzt
- vollständiger bestehender Research-Testlauf bleibt Teil der Verifikation

## Offene Punkte

- Möglicherweise lohnt sich später noch ein letzter visueller Feinschliff an der genauen Desktop-Balance zwischen Sidebar-Breite und Kartenraster auf sehr breiten Screens; funktional und strukturell ist die Hierarchie jetzt jedoch konsistent.