# MD3-Cleanup Final — `app/static/css/md3/` gelöscht

**Datum:** 2026-05-30  
**Branch:** main  
**Commit-Basis:** b73b4ed3e0e7949ecbe817b1e29cb7c3c7772a44  
**Typ:** Implementation, kein Commit (Arbeitsbaum offen für Prüfung)

## Ziel

Vollständige Entfernung von `app/static/css/md3/` — alle aktiven Reste zuerst überführen, dann Ordner per `git rm -r` löschen.

## Ergebnis

**Ziel erreicht:** `app/static/css/md3/` gelöscht (25 Dateien, ~7.900 Zeilen).

## Geänderte Dateien

| Datei | Typ |
|---|---|
| `app/static/css/md3/` (25 Dateien) | Gelöscht |
| `app/static/css/footer.css` | Neu (footer-shell Regeln) |
| `app/static/css/00_tokens.css` | `--z-index-*` Tokens ergänzt |
| `app/static/css/layout.css` | `html { overflow-x: hidden }` ergänzt |
| `app/static/css/30_components.css` | Dialog-z-index, Tabellen, Research-Scroll, pm-button--success |
| `app/static/css/40_cards.css` | `.md3-card` Selektoren und Blöcke entfernt |
| `app/templates/base.html` | Alle MD3-Links entfernt, `footer.css` eingebunden |
| `app/templates/partials/_admonition.html` | `md3-status-live` entfernt |
| `app/static/js/modules/navigation/drawer.js` | Dead Submenu-Methoden entfernt |
| `app/static/js/modules/navigation/turbo-integration.js` | Stale MD3-Selektoren bereinigt |
| `app/static/js/modules/navigation/material-symbols-loader.js` | Staler parent-Selektor entfernt |
| `app/static/js/logout.js` | Staler Fallback-Selektor entfernt |
| `app/static/js/auth/password_reset.js` | Toten textfield-Block entfernt |
| `app/static/js/pages/corpus-guia.js` | `md3-code-block__copy--success` → `pm-button--success` |
| `app/tests/test_auth_phase1.py` | Test auf gelöschte Datei angepasst |
| `docs/audits/promat_md3_removal_plan_2026-05-30.md` | Abschlussdokumentation |

## Testergebnisse

667 passed, 0 failed | Ruff: clean | Governance: all passed

## Verbleibende Reste

- Dead `md3-*` Selektoren in `layout.css`, `20_layout.css`, `10_typography.css` (keine DOM-Matches)
- `--md-sys-*` Token-Bridge in `00_tokens.css` (aktiv benötigt bis Dead-Selector-Cleanup)
- `app/static/js/md3/alert-utils.js` — inhaltlich migriert, Pfad noch nicht bereinigt
