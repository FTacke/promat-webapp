# Runbook: VM-Speicherwartung (Root-Dateisystem)

## Zugehörige Spezifikation

- Keine eigene Spezifikation: reiner Host-Betrieb der Produktions-VM `vhrz2184`, ohne Wirkung auf Anwendungsdaten, Routing oder Datenpfade (`docs/spec/platform-data-files.md` bleibt unberührt).
- Hintergrund und Messwerte: `docs/agent-runs/2026-10-20_vm-disk-cleanup.md`.

## Zweck

Die VM teilt sich das Root-Dateisystem (50 GB, btrfs) mit mehreren Anwendungen (PROMAT, CO.RA.PAN, games, hedgedoc, marele). Zwei Dinge ließen es unkontrolliert wachsen: alte VS-Code-Server-Installationen und unbegrenzte Docker-Logs. Dieses Runbook beschreibt die dauerhafte Wartung und wie sie auf einer neuen VM wiederhergestellt wird.

## Bestandteile

| Baustein | Quelle im Repo | Ziel auf der VM | Zeitplan |
|---|---|---|---|
| VS-Code-Server-Cleanup | `scripts/vm_storage_vscode_cleanup.py` | `/usr/local/sbin/vscode-server-cleanup` | `vscode-server-cleanup.timer`: sonntags 05:15 (+ bis 15 min) |
| Konservative Docker-Wartung | `scripts/vm_storage_docker_maintenance.sh` | `/usr/local/sbin/docker-safe-maintenance` | `docker-safe-maintenance.timer`: sonntags 05:45 (+ bis 15 min) |
| Speicherüberwachung | `scripts/vm_storage_disk_watch.sh` | `/usr/local/sbin/disk-watch` | `disk-watch.timer`: stündlich |
| Selbsttests | `scripts/vm_storage_*_selftest.*` | `/usr/local/share/vm-storage-maintenance/` | manuell, und bei jedem Installer-Lauf |
| Units | `infra/host-maintenance/*.service`, `*.timer` | `/etc/systemd/system/` | – |
| Docker-Log-Vorlage | `infra/host-maintenance/docker-daemon.json` | `/etc/docker/daemon.json` (manuell, siehe unten) | – |

Nicht im Repo (hostindividuell): `disk-check.sh` im Root-Crontab (stündliche Mail ab 85 %), das nächtliche Backup-Cron `/etc/cron.d/promat-db-backup`.

### Was die Jobs tun und nie tun

- **VS-Code-Cleanup** löscht nur `~/.vscode-server/cli/servers/<Kanal>-<Commit>[.staging]`. Es bleiben: alles, was ein Prozess nutzt (exe, cwd, offene Dateien, Mappings, Kommandozeile, Umgebung; samt Geschwister-Eintrag), alles mit Schreibzugriff in den letzten 60 Minuten, die zwei neuesten *vollständigen* Installationen je Kanal, alles Neuere, Installationen unter 14 und `.staging` unter 7 Tagen. „Vollständig“ heißt: alle Kerndateien und mindestens 70 % der üblichen Dateizahl. Bei unklarer Version, fehlendem vollständigem Eintrag im Kanal oder unvollständigem Prozess-Scan wird nichts gelöscht. Parallelläufe verhindert ein Lock. Extensions, `data/` und Einstellungen werden nie angefasst.
- **Docker-Wartung** entfernt ausschließlich Build-Cache, der älter als 7 Tage ist (`docker builder prune --filter until=168h`). Sie entfernt **nie** Images (auch keine ungetaggten), Container, Netzwerke oder Volumes; der Installer verbietet solche Befehle per Textprüfung im Skript. Sie hält außerdem `/etc/logrotate.d/docker-unbounded-container-logs` aktuell (siehe unten) und berichtet, was sie bewusst liegen lässt.
- **disk-watch** schreibt nur ins Journal und löscht nichts: ab 75 % `warning`, ab 85 % `crit`, dazu Warnung bei mehr als 3 GiB Wachstum in 7 Tagen (mit geschätzten Resttagen) sowie bei fehlgeschlagener oder seit mehr als 9 Tagen nicht ausgelöster Wartungs-Unit.

## Voraussetzungen

- Root-Zugang auf die VM, Checkout dieses Repos (oder entpacktes Archiv) auf der VM, `python3` (3.10), `systemd`, `logrotate`.
- Docker ist optional; ohne Docker wird `docker-safe-maintenance.timer` nicht aktiviert. Ohne `/root/.vscode-server` bleibt `vscode-server-cleanup.timer` deaktiviert.

## Schritte (neue VM oder Neuaufbau)

1. Repo auf die VM bringen, zum Beispiel von der Arbeitsmaschine:
   `tar czf - scripts/vm_storage_* infra/host-maintenance | ssh <vm> 'mkdir -p /tmp/vmstorage && tar xzf - -C /tmp/vmstorage'`
2. Auf der VM als Root: `cd /tmp/vmstorage && bash scripts/vm_storage_install.sh`
   Der Installer führt zuerst alle Selbsttests aus (`--check`), installiert Skripte und Units, lädt systemd neu und aktiviert die Timer. Er ändert keine Crontabs, Container, Images oder Volumes. Wiederholte Läufe sind harmlos.
3. Docker-Log-Limits für **alle künftig erstellten** Container setzen, falls `/etc/docker/daemon.json` noch fehlt: Inhalt aus `infra/host-maintenance/docker-daemon.json` übernehmen. Wirksam wird das erst nach `systemctl restart docker`, was alle Container kurz stoppt: nur in einem geplanten Wartungsfenster. Ohne `live-restore` ist das ein Produktionsausfall.
4. Gefährliche Altlasten prüfen und entfernen: `crontab -l | grep -i prune`. Jeder `docker system prune -a`/`--volumes`-Eintrag gehört entfernt (löscht ungenutzte Volumes und alle Rollback-Images). Die Docker-Wartung aus diesem Runbook ersetzt ihn.
5. Rollback-Images schützen. Ein Image ohne Tag („dangling“) fällt dem `docker image prune -f` fremder Deploy-Skripte zum Opfer (zum Beispiel in der games-App). Ein Tag im Namensraum `rollback/` verhindert das:
   `docker tag <image-id> rollback/<anwendung>:<datum>`
   Freigeben, wenn nicht mehr gebraucht: `docker rmi rollback/<anwendung>:<datum>`.
6. Danach `docker-safe-maintenance` einmal von Hand starten: `systemctl start docker-safe-maintenance.service`. Es legt die logrotate-Überbrückung für Container ohne Log-Limit an.

## Docker-Logrotation ohne doppelte Rotation

`daemon.json` begrenzt Logs nur für **nach** der Änderung erstellte Container (Option `max-size`/`max-file` stehen dann in deren `HostConfig.LogConfig`). Für ältere Container (leere Optionen) listet `docker-safe-maintenance` deren Log-Pfade in `/etc/logrotate.d/docker-unbounded-container-logs` (`size 50M`, `rotate 3`, `copytruncate`). Wird ein Container neu erstellt, ist er nativ begrenzt und fällt beim nächsten Wartungslauf aus der Datei; sobald kein Container mehr betroffen ist, wird die Datei gelöscht. Die Überbrückung braucht keinen Container-Neustart, und es wird nie doppelt rotiert. Container werden dafür nie neu erstellt.

## VS-Code-Agent-Hosts

Der VS-Code-Client startet `code agent host` und führt die Registry unter `~/.config/Code/agent-host/local-endpoint/entries/*.json`. Ein Aufruf von `code agent host` verwendet einen registrierten, kompatiblen Supervisor weiter und startet keinen zweiten (`Agent host supervisor already running`). Frühere Clients (Mai 2026) starteten dagegen drei Hosts innerhalb von sieben Sekunden; alle drei luden bei jedem Update dieselbe Version in dasselbe `.staging`-Verzeichnis und blockierten sich gegenseitig (`error renaming downloaded server: Directory not empty`). Prüfen:

- Registrierte Hosts: `cat ~/.config/Code/agent-host/local-endpoint/entries/*.json` (Token nicht weitergeben), Prozesse: `pgrep -af 'agent host'`.
- Ein Host ohne Registry-Eintrag, ohne Kindprozesse und ohne aufgebaute Verbindungen (`ss -tanp | grep pid=<pid>,`) ist verwaist und kann mit `kill -TERM <pid>` beendet werden. Registrierte Hosts und solche mit Verbindung nie beenden.

Der Cleanup-Timer beseitigt die Folgen weiterhin, falls erneut mehrere Hosts gleichzeitig starten.

## Verifikation

- Selbsttests: `bash scripts/vm_storage_install.sh --check` (VS-Code-Cleanup 34, disk-watch 17, Docker-Wartung 7 Prüfungen).
- Timer: `systemctl list-timers vscode-server-cleanup.timer docker-safe-maintenance.timer disk-watch.timer`
- Probelauf ohne Löschen: `vscode-server-cleanup` (Dry-Run ist der Standard) und `docker-safe-maintenance --dry-run`.
- Journal: `journalctl -u vscode-server-cleanup -u docker-safe-maintenance -u disk-watch --since -8d`. Probleme: `journalctl -t vscode-server-cleanup -t docker-safe-maintenance -t disk-watch -p warning`. Ein Fehlschlag setzt die Unit auf `failed` (`systemctl --failed`) und `disk-watch` meldet das zusätzlich.
- Root-Belegung: `df -h /`; btrfs gibt gelöschte Daten verzögert frei, deshalb nach einigen Sekunden erneut messen.

## Risiken und Rückbau

- Der VS-Code-Cleanup kann nur Server-Installationen entfernen; VS Code installiert eine fehlende Version beim nächsten Verbinden neu (ca. 200 MB Download).
- Rückbau: `systemctl disable --now <name>.timer`, danach die Units in `/etc/systemd/system/` und die Skripte in `/usr/local/sbin/` entfernen, `systemctl daemon-reload`. `/etc/logrotate.d/docker-unbounded-container-logs` darf bleiben oder wird gelöscht.
- Das Deploy-Skript der games-App (`scripts/update.sh`) ruft `docker image prune -f` auf (nur ungetaggte Images). Es gehört zu einem anderen Repo und wurde nicht geändert; Rollback-Images sind durch ihr `rollback/`-Tag davor geschützt.
- `disk-watch` ersetzt die vorhandene Mail-Warnung nicht; beide laufen parallel.
