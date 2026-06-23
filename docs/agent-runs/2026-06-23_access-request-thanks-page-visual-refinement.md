# 2026-06-23 Access Request – Bestätigungsseite visuelle Verfeinerung

## Aufgabe

Visuelle Hierarchie und Inhalt der Bestätigungsseite `/de/access-request/thanks` finalisieren.

## Ausgangslage

Die persönliche Begrüßung stand im `pm-auth-message is-success`-Callout (Hinweis-Kasten) — das war semantisch falsch: eine Erfolgsbestätigung ist kein Hinweis. Außerdem waren Begrüßung, Prüfhinweis und Spam-Hinweis im selben Block vermischt.

## Neue Struktur

Drei klar getrennte visuelle Ebenen:

```
A. Breadcrumb / Seitentitel: "Anfrage eingegangen"
B. pm-auth-success: ✓ Vielen Dank, Felix Tacke. / Ihre Anfrage wurde erfolgreich übermittelt.
C. pm-auth-message: Hinweis zur Prüfung / Prüf- + Spam + Disclaimer-Text (kompakt)
D. Login-Karte (unverändert)
```

## Neue CSS-Komponente: `pm-auth-success`

Flex-Column-Block mit grünem Success-Charakter (Border + Hintergrund in `book-link`-Farbe):
- `__icon`: `check_circle`-Icon, 1.75rem, `color: var(--book-link)`
- `__greeting`: 1.12rem, font-weight 600, `color: var(--book-fg)` — persönlicher Name prominent
- `__subtitle`: 0.95rem, `color: var(--book-muted)` — sachliche Bestätigung

Kein Breakout aus bestehenden CSS-Familien; nahtlose Erweiterung der `pm-auth-*`-Familie.

## Notice-Callout: neutrales `pm-auth-message`

- Kein `is-success`-Modifier mehr (war semantisch falsch)
- Icon: `info` (informationell, nicht success)
- Eyebrow: "Hinweis zur Prüfung" / "Review note"
- Body: konsolidierter Review-Text (Prüfung + Spam + Disclaimer in einem Absatz)

## i18n-Änderungen

| Schlüssel | DE | EN |
|---|---|---|
| `submitted_subtitle` (neu) | "Ihre Anfrage wurde erfolgreich übermittelt." | "Your request has been submitted successfully." |
| `submitted_review_heading` (neu) | "Hinweis zur Prüfung" | "Review note" |
| `submitted_review_text` (neu) | "Wir prüfen Ihre Anfrage und melden uns in der Regel innerhalb von 72 Stunden, sofern der Zugang freigegeben werden kann. Bitte prüfen Sie auch Ihren Spam-Ordner. Ein automatischer Anspruch auf Zugang besteht nicht." | "We will review your request and usually get back to you within 72 hours if access can be granted. Please also check your spam folder. Access is not granted automatically." |

Alte Keys (`submitted_body`, `submitted_spam_hint`, `submitted_disclaimer`) bleiben als toter Code in `i18n.py` — im Template nicht mehr genutzt.

## Geänderte Dateien

| Datei | Änderung |
|---|---|
| `app/static/css/30_components.css` | Neue `.pm-auth-success`-Komponente (Icon + Greeting + Subtitle) |
| `app/src/app/i18n.py` | 3 neue Keys (DE + EN); alte Keys bleiben |
| `app/templates/auth/access_request.html` | Submitted-Block: `pm-auth-success` + neutrales `pm-auth-message` |
| `app/tests/test_auth_phase1.py` | Alle Assertions auf neue Texte/Struktur aktualisiert |

## Testergebnis

762 passed, 15 failed (alle pre-existing). Keine Regressionen.
