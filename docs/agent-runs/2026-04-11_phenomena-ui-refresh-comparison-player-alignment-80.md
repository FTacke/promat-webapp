# Phenomena UI Refresh Comparison Player Alignment 80

## Ziel

Die Split-Architektur von `phenomena` beibehalten, aber Terminologie, UI-Hierarchie, Aktionslogik, Badge-System, Materiallisten und Selected-Items sichtbar stärker an die bestehende App-Sprache von `comparison` und `player` angleichen.

## Umgesetzte Änderungen

- Terminologie in Overview und Editor von `Liste`/`Phänomenliste` auf `Set` umgestellt:
  - Step: `1 Set wählen`
  - Suche: `Set suchen`
  - Primäraktion: `Neues Set`
  - Intro: `Kuratierte Sets öffnen, bearbeiten oder ein neues Set mit ausgewählten Items aus Wortliste und Text anlegen.`
- Login-CTA und Login-Hinweis innerhalb der Arbeitsflächen entfernt:
  - kein `Anmelden`-Button mehr in der Phenomena-Overview
  - kein `Zum Speichern bitte anmelden` mehr im Editor
  - owner-pflichtige Aktionen lösen Login nur noch bei Ausführung aus, nicht als widersprüchliche Arbeitsflächen-CTA
- Overview visuell neu aufgebaut:
  - oberer Step-Container stärker an `comparison` angelehnt
  - Set-Liste als ruhiger vertikaler Listenblock statt grober Einzelkarten
  - Status-Badge vor Item-Zahl angeordnet
  - Vorschauzeile auf kurze Vorschau mit `…` verdichtet
  - `Öffnen` entfernt; nur noch `Ansehen` plus `Modifizieren` für curated und `Bearbeiten` für custom
- Badge-System an die Comparison-Familie angenähert:
  - Phenomena-Status nutzt dieselbe Badge-Grundlogik wie `pm-comparison-speaker-badge`
  - nur ruhige Farb- und Statusvarianten für `curated`, `custom`, `saved`, `unsaved`
- Editor-Workhead verdichtet:
  - Titel, Status, curated-Hinweis und Hauptaktionen klarer auf gemeinsamen Achsen
  - Notizfeld kompakter und integrierter mit derselben Form-Control-Sprache wie die übrigen Eingabefelder
- Materialspalten dichter und playernäher gebaut:
  - ruhigere Nummernzone links
  - leiseres Muted-State für nicht ausgewählte Items
  - Selected-State primär über Flächenzustand der Zeile statt über harte Kontur
  - rechte Plus-/Check-Zone nur noch als leiser Statusanker
- `Ausgewählte Items` weiter als sortierbare Arbeitsliste verdichtet:
  - ruhigere linke Nummernzone
  - sekundäre Meta-Zeile `WORT · 26` bzw. `SATZ · …`
  - Haupttext klar dominant
  - Drag-Handle und Remove-Zone rechts zusammengefasst

## Technische Nachzüge

- `research-phenomena-overview.js` blendet den Listenblock beim Filtern sauber aus und behandelt `Neues Set` plus `Modifizieren` ohne sichtbare Login-CTA in der Oberfläche.
- Der vorherige Discard-Fix bleibt aktiv: Bestätigtes Verwerfen navigiert ohne `beforeunload`-Blocker zurück zur Overview.
- Render-Tests für die neue Terminologie und das Entfernen des Editor-Login-Hinweises angepasst.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sets.py tests/test_research_phenomena.py`
  - Ergebnis: `26 passed`
- Browser-QA auf einer frischen isolierten Test-Instanz statt auf einem stale lokalen ReLoader-Stand durchgeführt
- Zusätzlich `comparison` screenshot-basiert als Shared-CSS-Regression gegengeprüft

## Screenshots

- `tmp/ui-qa/phenomena-refresh-80/overview-default.png`
- `tmp/ui-qa/phenomena-refresh-80/overview-auth-custom-actions.png`
- `tmp/ui-qa/phenomena-refresh-80/editor-head.png`
- `tmp/ui-qa/phenomena-refresh-80/editor-wordlist-selected-muted.png`
- `tmp/ui-qa/phenomena-refresh-80/editor-textlist.png`
- `tmp/ui-qa/phenomena-refresh-80/editor-selected-items.png`
- `tmp/ui-qa/phenomena-refresh-80/comparison-regression.png`

## Visuelle Bewertung

- Overview wirkt jetzt deutlich mehr wie ein ruhiger Step-Flow der bestehenden Research-App und weniger wie eine Sammlung grober Sonderkarten.
- `curated: Ansehen + Modifizieren` und `custom: Bearbeiten` sind sprachlich und visuell klar getrennt.
- Materiallisten und Selected-Items liegen sichtbar näher an der dichten Player-/Comparison-Logik: ruhigere Nummern, leiseres Muted-State, präzisere Achsen und weniger UI-Lärm.
- `comparison` blieb im Regression-Screenshot unauffällig; es wurde keine neue konkurrierende Komponentenfamilie für Phenomena eingeführt.

## Sample

- Kein Update an `sample`, weil dort keine gespiegelt dargestellte Phenomena-Oberfläche oder dieselbe konkrete Listenkomponente enthalten ist.