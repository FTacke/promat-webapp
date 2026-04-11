# Phenomena Overview Actions And Selected List Follow-Up 79

## Ziel

Die sprachliche Aktionslogik der `phenomena`-Overview schärfen, den defekten Flow `Entwurf verwerfen` im Editor beheben und die Zeilen in `Ausgewählte Items` sichtbar näher an die ruhigen Listenmuster aus `comparison` und `player` bringen.

## Umgesetzte Änderungen

- Overview-Aktionen sprachlich getrennt:
  - curated-Sets: `Ansehen` plus `Modifizieren`
  - custom-Sets: `Bearbeiten`
  - das generische `Öffnen` wurde aus der Set-Liste entfernt
- Selected-Items-Zeilen strukturell neu geordnet:
  - ruhigere linke Nummernzone
  - klarere Meta- und Haupttext-Hierarchie in der Mitte
  - zusammengefasste rechte Aktionszone mit Separator und sauberer Achsenführung
- Editor-Discard-Flow repariert:
  - Root cause war, dass das Confirm-`dialog` im Page-JS innerhalb des Editor-Sections gesucht wurde, obwohl es als Geschwisterelement im Artikel gerendert wird
  - dadurch öffnete der Bestätigungsdialog im echten Browser nicht zuverlässig
  - die Dialogelemente werden jetzt korrekt auf Dokumentebene gebunden
- `beforeunload` blockiert die absichtliche Rücknavigation nach bestätigtem Verwerfen nicht mehr
- Fokus-Tests ergänzt, damit `Ansehen`/`Bearbeiten`/kein `Öffnen` serverseitig abgesichert bleiben

## Referenzen

- `comparison` als Referenz für ruhige horizontale Arbeitslisten, Meta-Hierarchie und Aktionsrhythmus
- `player` als Referenz für dichte Itemzeilen, kleine Identifikationszonen und zurückhaltende Aktionsenden
- Kein Update an `sample`, weil dort kein gespiegelt gezeigtes `phenomena`-Layout-Element betroffen ist

## Verifikation

- Editor-/CSS-/Template-Fehlerprüfung für die geänderten Dateien, zuletzt ohne Fehler
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sets.py tests/test_research_phenomena.py`
  - Ergebnis: `26 passed`
- Headless-Browser-Validierung gegen den laufenden lokalen Dev-Server auf `http://127.0.0.1:8000`:
  - curated Overview mit `Ansehen` plus `Modifizieren`
  - Editor mit Dirty-State
  - Confirm-Dialog für `Entwurf verwerfen`
  - bestätigtes Verwerfen mit Rücknavigation zurück zur Overview
- Zusätzliche isolierte Headless-Browser-Prüfung gegen eine temporäre Test-App auf `http://127.0.0.1:8011` mit owner-gebundenem Custom-Set:
  - visuelle Prüfung von `Bearbeiten` für Custom-Sets zusammen mit `Ansehen` plus `Modifizieren` für curated-Sets

## Screenshots

- `tmp/ui-qa/phenomena-followup-79/overview-curated-actions.png`
- `tmp/ui-qa/phenomena-followup-79/overview-auth-custom-actions.png`
- `tmp/ui-qa/phenomena-followup-79/editor-selected-items-refined.png`
- `tmp/ui-qa/phenomena-followup-79/editor-selected-items-section.png`
- `tmp/ui-qa/phenomena-followup-79/editor-discard-confirm.png`
- `tmp/ui-qa/phenomena-followup-79/overview-after-discard.png`

## Ergebnisbewertung

- Die Set-Liste ist sprachlich klarer: kuratierte Vorlagen werden angesehen oder modifiziert, eigene Sets werden bearbeitet.
- Die Selected-Items-Zeilen lesen sich jetzt als zusammenhängende sortierbare Arbeitsliste statt als lose zusammengesetzte Admin-Zeilen.
- Der vorher defekte Discard-Flow ist im echten Browser reproduzierbar repariert.