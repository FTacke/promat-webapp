# PROMAT Editorial Reading System 03

Run-Zeitpunkt: 2026-03-26

## 1. Ziel dieses Runs

Ziel dieses Runs war, PROMAT konsequenter von einer ruhigen App-Oberfläche zu einer editorialen Leseumgebung mit App-Shell umzubauen. Die Shell sollte funktional bleiben, gestalterisch aber deutlich hinter Leseraum, typographische Hierarchie und inhaltliche Orientierung zurücktreten.

## 2. Verwendete Referenzen

Dieser Run wurde gegen folgende lokale Referenzen umgesetzt:

- `docs/start/promat_layout_plan.md`
- `docs/start/00_tokens.css`
- `docs/start/20_book.css`
- `docs/start/40_custom.css`
- `docs/start/admonitions.md`

Leitend waren dabei vor allem diese Prinzipien:

- editoriale Einstiegszonen statt UI-Hero-Panels
- offener Leseraum ohne sichtbare Content-Boxen
- ruhige Navigation im Sinn eines Inhaltsverzeichnisses
- Card-System nach Admonition-Logik: Border vor Shadow, minimale Tinting-Flaechen, semantische Akzente
- keine Uppercase-Navigation als dominantes UI-Signal

## 3. Wichtigste festgestellte Abweichungen

- Textseiten-Heroes wirkten noch zu sehr wie generische Komponenten und nicht wie typographische Kapitelauftakte.
- Der Haupttextbereich war zwar bereits geoeffnet, aber Page-Navigation und einzelne Metadatenregeln trugen noch alte App-Semantik in den Leseraum.
- Drawer und Untermenüs waren ruhiger geworden, aber noch nicht vollständig auf TOC-artige Zurückhaltung und robuste Submenu-Cleanup-Logik gebracht.
- Landing-Cards und Landing-Hero transportierten noch zu viel Panel- bzw. Card-Logik.
- Alte Uppercase-Regeln im MD3-Unterbau kollidierten weiterhin mit der editorialen Zielrichtung.

## 4. Konkret umgesetzte Aenderungen

### System, Typografie und Layout

- Lesebreiten auf buchnaehere Masse umgestellt (`72ch` fuer Text, `78ch` fuer Hero-Kontext).
- Textseiten-Hero von sichtbarer Card-/Icon-Logik geloest und als ruhiger, haarliniengetrennter Einstieg neu gefasst.
- Landing-Hero auf eine schlichte, einspaltige editoriale Einleitung mit integrierter Marke reduziert.
- Metadaten- und Navigationslabels aus Uppercase-Logik geloest.

### Navigation und Shell

- Drawer-Flaechen, Hover- und Active-States weiter in Richtung Inhaltsverzeichnis beruhigt.
- Submenu-Layout mit feiner linker Leitlinie und engerem, textnahem Rhythmus verfeinert.
- Submenu-Cleanup in JavaScript mit robuster Fallback-Logik fuer reduzierte oder ausbleibende Transitions abgesichert.
- Top-App-Bar und Footer auf ruhigere Hairline- und Surface-Logik abgestimmt.

### Cards

- Landing- und semantische Cards vom weichen App-Panel in Richtung Admonition-System verschoben.
- Starke Flaechen- und Gradienteneindruecke entfernt.
- Semantische Varianten ueber subtile Tinting-Flaechen und linke Akzentkanten ausdifferenziert.
- CTA-Zonen als ruhige Fortsetzung des Leseflusses statt als stark abgesetzte Action-Flaechen behandelt.

## 5. Betroffene Dateien

- `app/static/css/00_tokens.css`
- `app/static/css/10_typography.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/static/js/modules/navigation/drawer.js`
- `app/templates/_md3_skeletons/page_text_skeleton.html`
- `app/templates/pages/index.html`

## 6. Wie Header/Hero neu geordnet wurden

Die textseitigen Header wurden von dekorativer Hero-Panel-Logik befreit. Das Icon wurde entfernt, der Auftakt auf Eyebrow, H1 und Intro reduziert und ueber eine ruhige Hairline vom folgenden Fliesstext getrennt. Dadurch funktioniert der Seitenbeginn jetzt als editoriale Einfuehrung statt als App-Komponente.

Auf der Landingpage wurde die frühere technischere Hero-Struktur in einen kompakten, zentrierten Einstieg überführt: Logo im Textfluss, klare Eyebrow, starkes H1 und ein Lead, das die neue Rolle der Navigation explizit unterordnet.

## 7. Wie Drawer/Submenus repariert wurden

Die Drawer-Navigation wurde visuell weiter reduziert: weniger Flächenwirkung, subtilere Hover-Hintergründe, leisere Icons und eine klarere TOC-Anmutung. Untermenüs haben jetzt einen engeren, linearen Rhythmus und eine linke Leitlinie statt Card- oder Pill-Semantik.

Technisch wurde das Schliessen von Submenus in `drawer.js` stabilisiert. Statt ausschliesslich auf `transitionend` zu vertrauen, nutzt der Code jetzt eine zentrale Cleanup-Funktion mit berechneter Dauer und Timeout-Fallback. Das verhindert haengende A11y-Zustaende, wenn Transitionen reduziert oder gar nicht ausgefuehrt werden.

## 8. Wie das Card-System neu gefasst wurde

Das Card-System wurde explizit auf die Logik der Referenz-Admonitions gezogen:

- sehr dezente semantische Flaechen
- klare, aber schmale Border-Struktur
- linke Akzentkante bei inhaltlich markierten Varianten
- keine weichgespuelten Gradient- oder Hover-Schatten als Hauptsignal

Insbesondere die Landing-Cards funktionieren jetzt eher als ruhige editoriale Wegweiser denn als Dashboard-Kacheln.

## 9. Offene Restprobleme

- Inhaltlich tragen mehrere uebernommene Projektseiten weiterhin sichtbare CO.RA.PAN-Texte und importierte Sprachmischung; das ist redaktionell, nicht systemisch.
- Im alten MD3-Unterbau existieren weiterhin Uppercase-Regeln, die aber fuer die relevanten PROMAT-Zonen inzwischen gezielt ueberschrieben werden. Ein spaeterer Aufraeum-Run koennte diese Basis weiter ausduennen.
- Die gerenderte Seitennavigation nutzt noch die bestehende Grundstruktur mit Divider-Markup; visuell ist sie beruhigt, strukturell aber noch Altbestand.

## 10. Naechster sinnvoller Schritt

Der sinnvollste naechste Schritt ist ein redaktioneller Durchgang ueber die sichtbar importierten Projektseiten. Das visuelle System ist jetzt deutlich naeher an der gewuenschten editorialen Leseumgebung; der auffaelligste Bruch liegt deshalb nicht mehr in Shell oder Komponente, sondern im noch uebernommenen Inhalts- und Sprachmaterial.

## Verifikation

Lokal verifiziert wurde gegen `http://127.0.0.1:8000`.

Gepruefte Marker im gerenderten HTML:

- Landing-Hero mit `promat-landing__hero`
- Landing-Grid mit `promat-landing__grid`
- Textseiten-Hero mit `promat-reading-hero`
- offener Textbereich mit `promat-reading-space`
- Seitennavigation mit `md3-page-navigation`
- Top-App-Bar und Drawer-Struktur im gerenderten Shell-Markup