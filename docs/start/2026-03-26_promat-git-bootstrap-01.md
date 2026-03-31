# PROMAT Git-Bootstrap 01

Run-Zeitpunkt: 2026-03-26

## Ziel

Initialisierung des PROMAT-Workspace als eigenstaendiges Git-Repository mit sauberem Clean Cut gegenueber der CORAPAN-Herkunft.

## Umgesetzt

- Neues Git-Repository im Workspace-Root vorbereitet
- Root-README fuer die PROMAT Webapp angelegt
- `.gitignore` fuer Laufzeitdaten, lokale Env-Dateien und temporaere Artefakte angelegt
- `data/` und `media/` nur als leere Struktur ueber Platzhalterdateien vorgesehen
- Remote-Ziel fuer GitHub festgelegt: `https://github.com/FTacke/promat-webapp.git`

## Hinweise

- Inhalte unter `data/`, `media/`, `logs/` und `tmp/` sind nicht Teil des initialen Repository-Stands
- Der erste Commit und Push erfolgen auf `main`