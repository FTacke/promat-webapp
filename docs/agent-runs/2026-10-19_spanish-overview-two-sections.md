# Spanische Teaching-Übersicht: zwei Bereiche, durchgehend zweispaltig (2026-10-19)

## Änderungen

- Hubs `content/teaching/spanish/hubs/{de,en}.yaml`: Kategorien ersetzt durch **Zum Einstieg / Getting started** (*Welche Aussprache unterrichten?*, *Weiches Spanisch, hartes Deutsch*) und **Aussprachephänomene entdecken / Exploring pronunciation features** (*B oder V?*, *Weiche Konsonanten: b, d und g*, *Das spanische r*, *Das r am Wortende*, *Ein Akzent verändert alles*); Bereichsbeschreibungen wie vorgegeben, die des zweiten Bereichs behutsam gekürzt (ohne „authentische Hörbeispiele“, das die allgemeine Einleitung bereits nennt). Titel und Teaser der Karten unverändert; die geplante Vokalseite hat weder Karte noch Platzhalter.
- Layout deklarativ: neues Hub-Feld `card_columns: 2` (nur im spanischen Hub gesetzt) lässt alle Gruppen das vorhandene Zweispalten-Raster (`pm-teaching-topic-grid--compact`, max. 48 rem) verwenden; kein neues CSS. Andere Teaching-Übersichten bleiben unverändert (Test auf fehlendes `card_columns` in ihren Hubs).
- Messung im Browser (DE/EN, 1280/900/390 px, hell/dunkel): beide Bereiche je 2 Spalten (768 px, gleiche Position), mobil eine Spalte, keine Überläufe, Karten je Zeile gleich hoch, Abstand zwischen den Bereichen 68 px (Desktop), alle Karten verlinken auf die bestehenden Seiten.
- Tests: Übersicht (Bereiche, Reihenfolge, Raster, keine Platzhalter, sieben Karten genau einmal) und angepasste ältere Hub-Tests.
- Spezifikation ergänzt (`card_columns`).
