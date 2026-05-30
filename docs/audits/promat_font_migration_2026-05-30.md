# ProMat Webapp – Font-Migrationsbericht

**Datum:** 2026-05-30  
**Typ:** Migration – lokales Font-Hosting  
**Grundlage:** `docs/audits/promat_font_inventory_2026-05-30.md`  
**Branch:** `main` (b92cf27 → neuer Commit)

---

## 1. Executive Summary

Die zwei Google-Fonts-Abhängigkeiten (Inter, Source Serif 4) wurden durch lokal gehostete Variable-Font-WOFF2-Dateien ersetzt. Die App lädt keine externen Font-Ressourcen mehr. Die CSP wurde bereinigt. `--book-font-display` wurde auf `var(--book-font-body)` (Source Serif 4) definiert.

**Ruff:** grün  
**Pytest:** 665 passed, 2 pre-existing failures (unverändert)  
**Governance:** grün  
**mypy:** 72 pre-existing errors (unverändert gegenüber HEAD, keine neuen durch diese Migration)  
**Google-Fonts-Referenzen in aktiven Templates/CSS/CSP:** keine  
**Browser-Screenshot-Prüfung:** nicht durchgeführt (lokale UI-Prüfung nicht möglich in diesem Run)

---

## 2. Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `app/templates/base.html` | Google-Fonts-Preconnects und -Stylesheet entfernt; `typefaces.css` eingebunden |
| `app/static/css/00_tokens.css` | `--book-font-display: var(--book-font-body)` hinzugefügt |
| `app/static/css/md3/components/typefaces.css` | **Neu** – alle vier `@font-face`-Regeln |
| `app/src/app/__init__.py` | CSP: `fonts.googleapis.com` und `fonts.gstatic.com` entfernt |
| `app/tests/test_auth_phase1.py` | Zwei Tests auf neue CSP und neue Font-Einbindung aktualisiert |

---

## 3. Hinzugefügte Font-Dateien

| Dateiname | Größe | Herkunft |
|-----------|-------|----------|
| `app/static/fonts/Inter-Variable.woff2` | 344 KB | Inter 4.1, `web/InterVariable.woff2` |
| `app/static/fonts/Inter-Italic-Variable.woff2` | 379 KB | Inter 4.1, `web/InterVariable-Italic.woff2` |
| `app/static/fonts/SourceSerif4-Variable.woff2` | 420 KB | Source Serif 4.005, `VAR/SourceSerif4Variable-Roman.ttf.woff2` |
| `app/static/fonts/SourceSerif4-Italic-Variable.woff2` | 339 KB | Source Serif 4.005, `VAR/SourceSerif4Variable-Italic.ttf.woff2` |

**Gesamt:** ca. 1,48 MB neue Font-Dateien.

---

## 4. Font-Quellen und Lizenzen

### Inter 4.1

- **Quelle:** https://github.com/rsms/inter/releases/tag/v4.1
- **Release-Asset:** `Inter-4.1.zip`
- **Entnommene Dateien:** `web/InterVariable.woff2`, `web/InterVariable-Italic.woff2`
- **Lizenz:** SIL Open Font License 1.1 (OFL-1.1) — freie Nutzung, keine Attribution in der UI erforderlich
- **Autor:** Rasmus Andersson

### Source Serif 4 v4.005

- **Quelle:** https://github.com/adobe-fonts/source-serif/releases/tag/4.005R
- **Release-Asset:** `source-serif-4.005_WOFF2.zip`
- **Entnommene Dateien:** `VAR/SourceSerif4Variable-Roman.ttf.woff2`, `VAR/SourceSerif4Variable-Italic.ttf.woff2`
- **Lizenz:** SIL Open Font License 1.1 (OFL-1.1) — freie Nutzung, keine Attribution in der UI erforderlich
- **Autor:** Adobe

Beide Fonts sind OFL-1.1-lizenziert und dürfen ohne Einschränkungen in kommerziellen und nicht-kommerziellen Webanwendungen eingesetzt werden.

---

## 5. Finale `@font-face`-Regeln

```css
/* Inter – Variable Font (UI-Schrift) */
@font-face {
  font-family: "Inter";
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  src: url("/static/fonts/Inter-Variable.woff2") format(woff2) tech(variations);
}

@font-face {
  font-family: "Inter";
  font-style: italic;
  font-weight: 100 900;
  font-display: swap;
  src: url("/static/fonts/Inter-Italic-Variable.woff2") format(woff2) tech(variations);
}

/* Source Serif 4 – Variable Font (Lesetext) */
@font-face {
  font-family: "Source Serif 4";
  font-style: normal;
  font-weight: 200 900;
  font-display: swap;
  src: url("/static/fonts/SourceSerif4-Variable.woff2") format(woff2) tech(variations);
}

@font-face {
  font-family: "Source Serif 4";
  font-style: italic;
  font-weight: 200 900;
  font-display: swap;
  src: url("/static/fonts/SourceSerif4-Italic-Variable.woff2") format(woff2) tech(variations);
}
```

Format-Syntax: `format(woff2) tech(variations)` konsistent mit bestehendem `material-symbols-fallback.css`.

---

## 6. Entscheidung: Variable Fonts

**Entscheidung:** Variable Fonts werden eingesetzt (nicht statische Schnitte).

**Begründung:**
- Die CSS nutzt `font-weight: 450` und `font-weight: 650`. Mit statischen Schnitten (400/500/600/700) würde der Browser diese synthetisieren. Variable Fonts interpolieren exakt auf die angeforderten Gewichte.
- Eine Datei deckt die gesamte Weight-Achse ab (Inter: 100–900, Source Serif 4: 200–900).
- Gesamtgröße (4 Variable-Font-Dateien) ist vergleichbar mit oder kleiner als 4+4 statische Schnitte.

**Akzeptierte visuelle Abweichung:** `font-weight: 450` und `font-weight: 650` werden nun auf echten Variable-Font-Interpolationspunkten gerendert statt durch Browser-Synthesis. Das ist eine typografische Verbesserung.

---

## 7. Entscheidung: Echte Italics

**Entscheidung:** Echte Italic-Schnitte werden mitgeliefert (kein Synthesis-Only).

**Begründung:**
- Die Zielanforderung der Migration nennt echte Italics als gewünschtes Ziel.
- Beide Fonts haben echte Kursivschnitte mit eigener Strichführung.
- Betroffen: `.pm-player-inline-ref__label`, `.md3-page-navigation__title`, `.md3-text-citation em`, `.md3-blockquote p`.

**Akzeptierte visuelle Abweichung:** Kursiver Text erscheint nun mit echter Kursivform (besonders Source Serif 4 Antiqua-Kursive) statt Browser-Synthesis. Leichte Änderung in Neigungswinkel und Strichcharakter ist erwünscht und akzeptiert.

---

## 8. Entscheidung: `--book-font-display`

**Entscheidung:** `--book-font-display: var(--book-font-body)` → Source Serif 4.

**Begründung:**
- Die Variable war bisher undefiniert; 9 Phenomena-Komponenten erbten dadurch Inter aus dem DOM-Kontext.
- Phenomena-Überschriften und Display-Komponenten sollen die Serifenschrift erhalten (bewusste Designentscheidung laut Aufgabenstellung).
- `var(--book-font-body)` ist die kanonische Definition der Lesetext-Schriftfamilie.

**Risiko:** Die Phenomena-Komponenten werden nun mit Source Serif 4 statt Inter gerendert. Das ist eine sichtbare Designänderung, die eine Browserprüfung erfordert. (Siehe Abschnitt 12.)

---

## 9. Entfernte Google-Fonts-Referenzen

Entfernt aus `app/templates/base.html`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:wght@400;600;700&display=swap">
```

Ersetzt durch:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/md3/components/typefaces.css') }}">
```

Keine weiteren aktiven Google-Fonts-Referenzen im Template-Baum, CSS oder Python-Code.

---

## 10. CSP-Änderung

**Datei:** `app/src/app/__init__.py`

**Vorher:**
```python
"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
"font-src 'self' https://fonts.gstatic.com; "
```

**Nachher:**
```python
"style-src 'self' 'unsafe-inline'; "
"font-src 'self'; "
```

Nur Google-Fonts-spezifische Domains entfernt. GoatCounter, YouTube, Datawrapper, Script-CSP unverändert.

---

## 11. Unicode-/Glyph-Einschätzung

**Entscheidung:** Keine `unicode-range`-Einschränkung.

**Begründung:**
- Alle nachgewiesenen Zeichenbedarfe (DE, EN, ES, FR: Latin-1 Supplement, General Punctuation, Guillemets, Typografische Anführungszeichen) sind in den vollständigen Variable-Font-Dateien abgedeckt.
- IPA-Phonetikzeichen (ɛ ɔ ə ʁ etc.) sind im Repo noch nicht nachgewiesen, aber für das phonetische Lehrprojekt perspektivisch relevant. Beide Fonts decken IPA-Zeichen über die vollständige Datei ab.
- Aggressive Subsetting-/Unicode-Range-Optimierung würde das Risiko eingehen, spätere Zeichen abzuschneiden.

**Risiko:** Die Font-Dateien sind größer (ca. 1,5 MB total) als subsettierte Versionen. Bei langsamen Verbindungen ist `font-display: swap` aktiv (FOUC-Verhalten wie bisher bei Google Fonts).

---

## 12. UI-/Screenshot-Prüfung

**Status: Nicht durchgeführt.** Lokale App-Ausführung und Browser-Prüfung waren in diesem Run nicht möglich.

**Ausstehende Prüfung erforderlich auf:**

| Route | Prüfpunkt |
|-------|-----------|
| `/de` | Inter UI-Font aktiv, keine Layout-Brüche |
| `/de/project/projekt` | Source Serif 4 Fließtext, echte Italics in Blockquotes |
| `/de/research` | Card-Titel mit `font-weight: 650` (Source Serif 4 Variable) |
| `/de/teaching/spanish/r` | Inter-Labels mit `font-weight: 650` |
| `/de/research/spanish/phenomena/overview` | **Kritisch:** `--book-font-display` jetzt Source Serif 4 statt Inter |
| `/admin/users` | Auth-Titel Inter 650 |

**Viewports:** 320px, 390px, 768px, 1280px.

**Besonderer Fokus:** Phenomena-Überschriften – diese werden erstmals Source Serif 4 nutzen statt Inter. Eine visuelle Prüfung ist vor dem Merge in eine Produktionsumgebung zwingend.

---

## 13. Testergebnisse

| Check | Ergebnis |
|-------|----------|
| `ruff check src/` | ✅ Grün |
| `pytest tests/` | ✅ 667 passed, 0 failures |
| `ci_governance_checks.py` | ✅ Grün |
| `mypy src/ --ignore-missing-imports` | ⚠ 72 pre-existing errors (unverändert) |
| Keine Google-Fonts-Refs in aktiven Dateien | ✅ Bestätigt |
| Font-Datei-Pfade korrekt | ✅ Bestätigt |
| Material Symbols Rounded unberührt | ✅ Bestätigt |

---

## 14. Offene Risiken

1. **Browser-Prüfung ausstehend (HOCH):** Phenomena-Überschriften werden jetzt mit Source Serif 4 statt Inter gerendert (`--book-font-display`-Fix). Das kann Layout-Änderungen verursachen, insbesondere bei Zeilenlängen und Überschriftenhöhen. Muss visuell vor Produktions-Deploy geprüft werden.

2. **Echte Italic-Änderung (MITTEL):** Source Serif 4 Italic sieht messbar anders aus als Browser-Synthesis. Blockquotes und Zitat-Komponenten haben nun echte Antiqua-Kursive. Akzeptiert laut Aufgabenstellung, aber visuelle Verifikation steht aus.

3. **Font-Größe (NIEDRIG):** 4 Variable-Font-Dateien = ca. 1,5 MB. Bei `font-display: swap` ist das Ladeverhalten identisch zu Google Fonts (FOUC-Muster gleich). Performance-Auswirkung nicht messbar ohne tatsächlichen Browser-Test.

4. **IPA-Abdeckung (NIEDRIG):** Nicht explizit geprüft. Da keine `unicode-range` gesetzt wird, laden die vollständigen Font-Dateien – IPA-Zeichen sind in Inter und Source Serif 4 enthalten.

5. **Inter opsz-Achse:** `InterVariable.woff2` enthält nur die `wght`-Achse (nicht die zweiachsige `opsz,wght`-Variante). Das ist korrekt für den Web-Einsatz; die Display-Variante (`InterDisplay`) ist bewusst nicht eingebunden.

---

## 15. Rollback-Hinweis

Um zur Google-Fonts-Version zurückzukehren:

1. In `app/templates/base.html` die drei Google-Fonts-Links wiederherstellen (siehe Audit-Dokument Abschnitt 2).
2. In `app/src/app/__init__.py` die CSP-Zeilen mit `fonts.googleapis.com` und `fonts.gstatic.com` wiederherstellen.
3. In `app/static/css/00_tokens.css` die Zeile `--book-font-display: var(--book-font-body);` entfernen.
4. `app/static/css/md3/components/typefaces.css` löschen.
5. Die 4 Font-Dateien aus `app/static/fonts/` entfernen.
6. Tests in `test_auth_phase1.py` zurücksetzen (CSP-Test + CDN-Test).

Der Git-Commit ist atomar und kann mit `git revert` rückgängig gemacht werden.

---

## Follow-up: Pytest-Failure-Klärung

### Ursache der zwei Failures

Beide Failures (`test_account_page_user_menu_stays_compact_for_regular_users` und `test_admin_users_page_uses_sidebar_only_for_admin_area_navigation`) hatten dieselbe Ursache: die Hilfsfunktion `_extract_element_by_id` in `app/tests/test_auth_phase1.py` nutzte einen Regex mit nicht-gierigem `.*?` und `re.DOTALL`:

```python
rf'<{tag}[^>]*id="{re.escape(element_id)}".*?</{tag}>'
```

Bei verschachtelten Elementen desselben Tags stoppt dieser Ausdruck am **ersten** `</div>` — dem schließenden Tag des innersten verschachtelten Elements. Der Inhalt nach diesem Punkt (u.a. der "My account"-Link) wurde nie in das extrahierte HTML aufgenommen.

### Pre-existing oder durch Font-Migration ausgelöst?

**Nicht durch die Font-Migration ausgelöst.** Die Font-Migration ändert keine HTML-Struktur.

Die Failures wurden durch Commit `b92cf27` (`feat(identity): optimize account dropdown layout for clarity and compactness`) eingeführt: Dieser Commit änderte den `promat-user-menu__identity`-Block von einem `<p>`-Element auf ein `<div>` mit einem zusätzlichen verschachtelten `<div class="promat-user-menu__identity-text">`. Damit wurde der erste `</div>`, den der Regex trifft, der schließende Tag des inneren Elements — nicht der äußere Dropdown-Container. Der Test wurde bei diesem Commit nicht mitgepflegt.

### Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `app/tests/test_auth_phase1.py` | `_extract_element_by_id` auf tiefensensitives Nesting umgestellt |

### Fix

`_extract_element_by_id` wurde auf ein tiefenzählendes Verfahren umgestellt: Statt eines einzelnen nicht-gierigen Regex-Ausdrucks werden jetzt alle öffnenden und schließenden Tags des gesuchten Typs iteriert und eine Tiefenzählung durchgeführt. Rückgabe erfolgt erst, wenn die Tiefe wieder auf 0 zurückgeht — d.h. beim echten äußeren schließenden Tag.

Das Verhalten für nicht-verschachtelte Tags (z.B. `<aside>`) bleibt korrekt.

### Finale Testergebnisse

| Check | Ergebnis |
|-------|----------|
| `ruff check src/` | ✅ Grün |
| `pytest tests/` | ✅ 667 passed, 0 failures |
| `ci_governance_checks.py` | ✅ Grün |
| `mypy src/ --ignore-missing-imports` | ⚠ 72 pre-existing errors (unverändert) |

### Verbleibende Risiken

Keine neuen Risiken durch diesen Fix. Die Funktion `_extract_element_by_id` ist jetzt korrekt für verschachtelte Elemente des gleichen Typs. Eine Einschränkung bleibt: Der Regex ignoriert selbst-schließende Varianten (`<div />`), die im HTML5-Kontext für `div` und `aside` jedoch nie vorkommen.
