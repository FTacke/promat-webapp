# Runbook: UI Change Workflow

## Zugehörige Spezifikation

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md` für Research-Seiten und Workbenches
- `docs/spec/research-player.md`, wenn Player- oder playernahe Oberflächen betroffen sind

## Zweck

Diesen Ablauf für visuelle oder interaktive UI-Änderungen in `app/templates/`, `app/static/css/` und `app/static/js/` nutzen, damit neue Arbeit sichtbar aus denselben Komponentenfamilien der Webapp abgeleitet bleibt und nicht wieder eigene Sonderlogiken aufbaut.

## Voraussetzungen

- relevante Datei(en) unter `docs/spec/` sowie root- und scoped-`AGENTS.md` gelesen
- lokaler Dev-Server über `scripts/dev-start.ps1`, wenn Browserprüfung nötig ist
- Möglichkeit, Screenshots unter `tmp/ui-qa/` abzulegen

## Referenzflächen

- `comparison`: Step-Container, Auswahlblöcke, Badge- und Meta-Rhythmus, klare vertikale Arbeitssequenzen, ruhige sekundäre Aktionen
- `player`: dichte Materiallisten, kompakte Work-Heads, Sticky-Anker, Muted-vs-Active-Zustände, kompakte Icon-Aktionen und Controls
- `speakers`, `recordings`, Profil: Speaker-Cards, kompakte Task-Aktionen, Zeilen- und Tabellenaktionen, reduzierte Metadatenhierarchie
- `sample`: nur als Spiegel bereits aktiver Elemente mitziehen, niemals als upstream Designquelle benutzen

## Schritte

1. Oberfläche einordnen: Overview, Editor oder Detailansicht, dichte Workbench, unterstützende Form oder Liste, oder Änderung an einer bereits geteilten Komponentenfamilie.
2. Vor dem Editieren die passenden produktiven Referenzseiten, Shared Partials und bestehenden CSS-Familien prüfen. Dazu gehören insbesondere `app/templates/`, gemeinsame Partials sowie `20_layout.css`, `30_components.css` und `40_cards.css`.
3. Wiederverwendung vor Neuerfindung: bestehende Familien für Buttons, Inputs, Selects, Textareas, Badges, Chips, Karten, Listenzeilen, Step-Container, Dialoge, Empty States, Sticky-Anker, Status- und Auswahlzustände sowie Overflow-Menüs erweitern oder wiederverwenden. Neue page-lokale Muster nur dann einführen, wenn kein bestehendes Muster die Aufgabe sauber löst.
4. Hierarchie ruhig halten: lineare Flows bevorzugen, Mini-Oberlabels und doppelte Statuskästen reduzieren, und keine zweite konkurrierende Arbeitsinsel aufbauen. Overview-Seiten bleiben Overview-Seiten; Bearbeitungslogik gehört auf Detail- oder Editorseiten.
5. Shared CSS als Hochrisikobereich behandeln: wenn `20_layout.css`, `30_components.css`, `40_cards.css` oder ein Shared Partial geändert wird, mindestens eine weitere unbetroffene Seite mit derselben Komponentenfamilie gezielt gegenprüfen.
6. `sample` im selben Run aktualisieren, wenn das geänderte reale UI-Element dort bereits repräsentiert wird.
7. Bei substanziellen UI-Änderungen im Browser validieren: reale Route oder manuellen Klickpfad durchlaufen, Screenshots unter `tmp/ui-qa/` erzeugen und das Ergebnis aktiv gegen die produktiven Referenzflächen prüfen.
8. Wenn praktikabel, Render- oder Regressionstests ergänzen beziehungsweise nachziehen, und den Run unter `docs/agent-runs/` dokumentieren.

## Verifikation

- passende produktive Referenzseiten wurden geprüft
- bestehende UI-Familie wurde wiederverwendet oder bewusst erweitert
- kein vermeidbarer UI-Lärm durch neue Miniüberschriften, doppelte Statusflächen oder parallele Arbeitsinseln entstanden
- globale oder shared CSS-Auswirkungen wurden auf mindestens einer weiteren Seite gegengeprüft, falls betroffen
- Browser-Durchlauf für substanzielle UI-Arbeit durchgeführt
- Screenshots erstellt und gegen Referenzseiten geprüft
- `sample` mitgezogen, falls ein repräsentiertes Element geändert wurde
- relevante Tests oder Render-Regressionen ergänzt oder erneut ausgeführt

## Risiken und Rückbau

- Page-lokale CSS-Forks, neu erfundene Badge- oder Button-Taxonomien und gemischte One-Page-Workbenches sind Regressionssignale und sollten zugunsten gemeinsamer Muster zurückgebaut werden.
- Wenn Browser-Screenshots nicht zum aktuellen Code passen, Dev-Server ohne stale ReLoader-Zustand neu starten und die Prüfung wiederholen, statt auf alte Renderstände zu vertrauen.