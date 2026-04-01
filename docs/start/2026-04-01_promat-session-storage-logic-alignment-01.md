# PROMAT Session Storage Logic Alignment 01

Datum: 2026-04-01

## Ziel

Die Session-Audio-, Alignment- und Item-Logik auf den jetzt akzeptierten Projektstand ziehen und die bereits erzeugten spanischen Dev-Beispiele daran ausrichten.

## Umgesetzter Stand

- Seed-Logik fuer spanische Dev-Beispiele von `raw/isolated_speech.wav` auf `source/isolated_speech.wav` umgestellt.
- Verbindlich dokumentiert, dass `raw/` nur unveraenderte Master-WAVs enthaelt und bei den aktuellen Dev-Beispielen leer bleiben darf.
- Verbindlich dokumentiert, dass spaetere Alignment-JSONs unter `alignment/` liegen und `items/` nur Split-MP3s enthaelt.
- Verbindlich dokumentiert, dass interne Split-Dateinamen auf stabiler `item_id` beruhen.
- Bestehende spanische Dev-Sessions fachlich auf `source/` statt `raw/` korrigiert.

## Verifikation

- Aktive Spezifikation, Kurzkonventionen, `.github`-Instruktionen und Seed-Skript gegeneinander abgeglichen.
- Vorhandene spanische Dev-Sessions und der bestehende Repo-Platzhalter an die neue Pfadlogik angepasst.