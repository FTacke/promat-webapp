# Run Log: Git History Reset

**Datum:** 2026-03-31  
**Typ:** Repo-Struktur / Git-Verwaltung  
**Laufnummer:** 04

---

## Ziel

Die gesamte Git-Historie des PROMAT-Repos vollständig neu aufsetzen, sodass der aktuelle lokale Arbeitsstand (nach drei vorherigen Cleanup- und Governance-Runs) der neue, saubere Ausgangspunkt auf `main` wird. Kein älterer Commit soll in der Historie verbleiben.

---

## Geänderte Bereiche

- `.git/` — vollständig gelöscht und neu initialisiert
- Remote `origin` — `https://github.com/FTacke/promat-webapp.git` mit Force-Push überschrieben

---

## Vorgehen

1. Lokalen Zustand verifiziert: Branch `main`, Remote `origin → https://github.com/FTacke/promat-webapp.git`, 25+ modifizierte/gelöschte tracked Files, 60+ neue untracked Files.
2. `.gitignore` geprüft: `.venv/`, `logs/`, `tmp/`, `data/db/postgres_dev/`, `__pycache__/` korrekt ausgeschlossen. Explizite Einschlüsse für `data/sessions/spanish/ES-L-DE-B2-24-001/**`, `data/research.db`, `public/.gitkeep`, `secure/.gitkeep` vorhanden.
3. Reset-Sequenz ausgeführt:
   ```powershell
   Remove-Item -Recurse -Force .git
   git init -b main
   git config user.name 'Felix Tacke'
   git config user.email 'felix.tacke@gmail.com'
   git remote add origin https://github.com/FTacke/promat-webapp.git
   git fetch origin main --depth=1
   git add -A
   git commit -m 'Initialize clean PROMAT baseline'
   git push --force-with-lease origin main
   ```
4. Ergebnis verifiziert: `git log --oneline -3` zeigt genau einen Commit, `git status` meldet `nothing to commit, working tree clean`.

---

## Architekturwirkung

Keine inhaltliche Architekturänderung. Die Git-Historie bildet jetzt ausschließlich den sauberen Post-Governance-Zustand ab. Alle vorherigen Intermediate-Commits (Legacy-Cleanup, Pfadmigrationen, Governance-Bootstrapping) sind nicht mehr in der Historie.

---

## Verifikation

| Prüfpunkt | Ergebnis |
|---|---|
| Genau ein Commit in `git log` | ✅ `2624c04 Initialize clean PROMAT baseline` |
| `HEAD -> main, origin/main, origin/HEAD` | ✅ |
| Remote URL korrekt | ✅ `https://github.com/FTacke/promat-webapp.git` |
| Working tree clean | ✅ `nothing to commit` |
| `.venv/` nicht im Commit | ✅ (durch `.gitignore` ausgeschlossen) |
| `data/db/postgres_dev/` nicht im Commit | ✅ (durch `.gitignore` ausgeschlossen) |

Verwendeter Push-Befehl: `--force-with-lease` (funktioniert, weil `git fetch --depth=1` die Tracking-Referenz korrekt gesetzt hat).

---

## Offene Punkte

- Demo-Asset-Dateinamen in `app/templates/pages/sample_page.html` (z. B. `img/cards/forschung_01.png`) tragen noch ältere deutsche Namen. Dies ist kosmetisch und nicht strukturell blockierend; dokumentiert in Run 01.
- `data/sessions/spanish/ES-L-DE-B2-24-001/` ist als Beispiel-Session im Repo enthalten. Zukünftige echte Sessions kommen nicht ins Repo.

---

## Nächste sinnvolle Schritte

- Kontinuierliche Feature-Entwicklung auf der sauberen Basis.
- Bei nächstem inhaltlichen Architektur-Entscheid: `docs/decisions/` befüllen.
- CI/CD-Pipeline einrichten, sobald Deployment-Infrastruktur steht.
