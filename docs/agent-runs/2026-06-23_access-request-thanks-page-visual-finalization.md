# 2026-06-23 Access Request – Bestätigungsseite visuell finalisiert

## Aufgabe

Success-Block auf `/de/access-request/thanks` und `/en/access-request/thanks` klar grün gestalten,
Icon und Text nebeneinander anordnen, Hinweisblock ohne Vollversalien darstellen.

## Ausgangsprobleme

1. **Falsche Farbe:** `pm-auth-success` verwendete `--book-link` (Blau/Marineblau) für Icon und Border — kein grüner Erfolgscharakter.
2. **Falsches Layout:** `flex-direction: column` → Icon über dem Text gestapelt, nicht nebeneinander.
3. **Fehlender Body-Wrapper:** Greeting und Subtitle lagen direkt im Flex-Container des `pm-auth-success`-Blocks, kein eigener `__body`-Container für die Textgruppe.
4. **Eyebrow in Vollversalien:** `.pm-auth-message__eyebrow` bekommt `text-transform: uppercase` über eine Shared-Regel mit `.pm-auth-field__label`. "Hinweis zur Prüfung" wurde als "HINWEIS ZUR PRÜFUNG" dargestellt — unpassend für eine mehrwortige Abschnittsüberschrift.

## Lösung

### 1. Neuer Token `--pm-status-success-border` (`00_tokens.css`)

Ergänzt im Bereich der bereits vorhandenen `pm-status-success-*`-Tokens:

```css
--pm-status-success-border: color-mix(in srgb, var(--book-adm-success) 38%, var(--pm-surface-paper) 62%);
```

Licht- und Dunkel-Modus adaptieren automatisch über `pm-surface-paper`. Keine separaten Dark-Mode-Overrides nötig.

Vorhandene Tokens (bereits vorhanden, jetzt genutzt):
- `--pm-status-success-surface` → leicht grüner Hintergrund (`book-adm-success` 14% in Paper)
- `--pm-status-success-text` → kräftiges Grün (`book-adm-success` 78% in `book-fg`)

Basiswerte: Light `#27a577`, Dark `#3dbf8a`.

### 2. `pm-auth-success` neu strukturiert (`30_components.css`)

- **Layout:** `flex-direction: column` → `flex-direction: row` (Icon links, Text rechts)
- **Icon:** `flex-shrink: 0`, `padding-top: 0.1rem` (optische Ausrichtung mit Textoberrand)
- **Icon-Farbe:** `--book-link` → `--pm-status-success-text` (Grün)
- **Border/BG:** Hardcoded `color-mix(book-link …)` → semantische Tokens `--pm-status-success-border` / `--pm-status-success-surface`
- **Neuer `__body`-Wrapper:** Greeting + Subtitle in `flex-direction: column; gap: 0.3rem; min-width: 0`
- **Greeting:** `font-weight: 600` → `700`, Farbe `--book-fg` → `--pm-status-success-text`
- **Subtitle:** unverändert `--book-muted` — ruhige zweite Zeile unterhalb der kräftigen Grüßzeile

### 3. `pm-auth-message--review` Modifier (`30_components.css`)

Neuer Modifier, der das Uppercase-Styling des geteilten Eyebrow/Label-Patterns für den Hinweisblock aufhebt:

```css
.pm-auth-message--review .pm-auth-message__eyebrow {
  text-transform: none;
  font-size: 0.88rem;
  font-weight: 600;
  letter-spacing: 0;
  color: var(--book-fg);
}
```

Alle anderen `pm-auth-message`-Callouts (Login, Passwort, Error-Callout) nutzen das kurze Label `t('auth.common.notice')` (z. B. "HINWEIS" / "NOTICE") — die behalten ihr Uppercase-Styling. Kein Regressionsrisiko.

### 4. Template (`access_request.html`)

- `__body`-Div um Greeting + Subtitle hinzugefügt
- Notice-Block: `class="pm-auth-message"` → `class="pm-auth-message pm-auth-message--review"`

## Geänderte Dateien

| Datei | Änderung |
|---|---|
| `app/static/css/00_tokens.css` | `--pm-status-success-border` ergänzt |
| `app/static/css/30_components.css` | `pm-auth-success` auf Row-Layout + grüne Tokens umgestellt; `pm-auth-message--review` Modifier hinzugefügt |
| `app/templates/auth/access_request.html` | `__body`-Wrapper; `pm-auth-message--review`-Modifier |

Keine Tests, i18n, Routen oder Submit-Logik geändert.

## Testergebnis

762 passed, 15 failed (alle pre-existing). Keine Regressionen.

## Visuelle Hierarchie nach Abschluss

```
A. Breadcrumb
B. Seitentitel: "Anfrage eingegangen" / "Request received"
C. Grüner Success-Block (pm-auth-success):
   [✓]  Vielen Dank, Felix Tacke.         ← Grün, fett, 1.12rem
        Ihre Anfrage wurde erfolgreich…   ← Muted, 0.92rem
D. Neutraler Hinweisblock (pm-auth-message--review):
   [ℹ]  Hinweis zur Prüfung               ← Normal-Case, 0.88rem, font-weight 600
        72-Stunden-Text + Spam + Vorbehalt
E. Login-Karte (unverändert)
```
