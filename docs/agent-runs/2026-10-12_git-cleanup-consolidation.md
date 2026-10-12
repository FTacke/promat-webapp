# 2026-10-12 – Git-Bereinigung und Konsolidierung

Nicht normativ. Arbeitsjournal.

## Ausgangslage

- `main` == `origin/main` (fca5fe6); untracked: Run-Notiz Spanisch-Export und `spanish-curated-sets.zip` (Produktionsdaten-Export).
- 8 lokale Branches, keine Worktrees, keine Stashes.
- Alle lokalen Branches und die `claude/*`- sowie `local/preservation-activation`-Remote-Branches hatten 0 Commits, die nicht in `main` enthalten sind (`git rev-list main..<branch>`, `git cherry`).

## Maßnahmen

- Run-Notiz committet; `docs/agent-runs/*.zip` in `.gitignore` aufgenommen (Export enthält Produktionsdaten, bewusst nicht versioniert).
- Lokale Branches mit `git branch -d` entfernt (Git prüft die Merge-Eigenschaft).
- Vollständig in `main` enthaltene Remote-Branches entfernt; Dependabot-Branches bleiben (offene Update-Vorschläge).
