# Runbook: Illustrationen auf Teaching-Themenseiten einbinden und für das Web optimieren

## Zugehörige Spezifikation

- `docs/spec/platform-data-files.md` (Teaching-Medien, Block `image`, Abschnitt zu Bildderivaten)

## Zweck

Standardablauf für jede neue Rasterillustration (PNG/JPEG) einer Teaching-Themenseite: Das Original bleibt als Master in voller Qualität erhalten, ausgeliefert wird eine deutlich kleinere WebP-Variante. Vektorgrafiken (SVG) brauchen kein Derivat.

## Voraussetzungen

- Pillow für den Build (`pip install Pillow`); die Prüfung braucht nur PyYAML
- die Illustration liegt noch nicht im Repository-Root (dort ist keine Arbeitskopie vorgesehen)

## Schritte

1. Master unter `content/teaching/{sprache}/{thema}/media/images/{sprechender-name}.png` ablegen (Kleinbuchstaben, Bindestriche). Eine Datei für alle Sprachfassungen. Der Master wird nie bearbeitet oder neu gespeichert.
2. Im Themen-YAML (`de.yaml`, `en.yaml`) den Block `image` anlegen: `src` (Dateiname des Masters), lokalisierter `alt` (beschreibt das Bild, wiederholt nie den Nachweis), `caption`, `credit` (Bildnachweis).
3. Die Anzeigebreite bestimmen (größte CSS-Breite des Bildes; der Block `image` zeigt höchstens 30 rem = 480 px). Derivatbreite = 2 × diese Breite (hochauflösende Displays), nie über der Masterbreite.
4. Qualität nach dem Ergebnis wählen, nicht pauschal: Varianten mit `python scripts/teaching_images.py --build --width 960 --quality 88|92|95 <name.png>` erzeugen und bei 2-facher Vergrößerung gegen den auf dieselbe Breite herunterskalierten Master vergleichen (feine Linien, sanfte Farbverläufe, Farbstich, Bänderung, Artefakte). Die niedrigste Stufe wählen, die nicht unterscheidbar ist; Richtwert für Zeichnungen: Qualität 92, Größe etwa 3 % des PNG.
5. `python scripts/teaching_images.py --build` schreibt `{name}.webp` neben den Master und die Deklaration `content/teaching/image-derivatives.yaml` (Hashes von Master und Derivat, Breite, Qualität). Beide Dateien committen.
6. Der Block `image` liefert automatisch `<picture>` mit `<source type="image/webp">` und dem Master als `<img>`-Fallback, mit `width`/`height` des Masters (kein Layoutsprung) sowie `loading="lazy"`; ohne Derivat bleibt es beim einfachen `<img>`.
7. Browserprüfung (DE/EN, Desktop und Smartphone, Light und Dark): geladene Variante (`currentSrc` endet auf `.webp`), Seitenverhältnis, kein Überlauf, Bildgrund im Dark Mode.

## Verifikation

- `python scripts/teaching_images.py --check` meldet `image derivatives OK` (Derivat vorhanden und kleiner, Seitenverhältnis gleich, nicht breiter als der Master, Hashes stimmen)
- `python scripts/validate_teaching_content.py` (ein Derivat zählt als referenziert, wenn sein Master referenziert ist) und `pytest app/tests/test_teaching_spanish_topics.py app/tests/test_teaching_content.py`

## Risiken und Rückbau

- Wird ein Master ersetzt, schlägt `--check` fehl, bis `--build` erneut gelaufen ist; die Derivatparameter eines vorhandenen Eintrags werden dabei übernommen, sofern keine neuen angegeben werden.
- Der Master bleibt über die Route `/teaching-media/…` öffentlich abrufbar (er ist der Fallback) und in der Git-Historie des öffentlichen Repositorys enthalten.
- Rückbau: `{name}.webp` und den Manifesteintrag löschen; der Block fällt auf das einfache `<img>` mit dem Master zurück.
