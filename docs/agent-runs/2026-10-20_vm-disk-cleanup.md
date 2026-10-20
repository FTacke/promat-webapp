# VM-Speicher bereinigen und dauerhaft absichern

Datum: 2026-10-20

## Ziel

Die Warnung „Disk usage critical: 85 %“ auf `vhrz2184` (Root-Dateisystem, btrfs, 50 GB) untersuchen, den Speicher sicher freigeben und die Ursachen dauerhaft beseitigen: unkontrolliert wachsende VS-Code-Server-Installationen, ein riskanter Docker-Prune-Cronjob und Container-Logs ohne Limit. Es wurde ausschließlich der Host angefasst; im Repo liegen nur die Wartungsskripte, Unit-Vorlagen und die Dokumentation. Kein App-Code, keine PROMAT-Daten.

## Consulted Sources

- `docs/spec/platform-data-files.md` (Host `vhrz2184`), `docs/runbooks/deploy-and-rollback.md` (Rollback = Neu-Deployment eines früheren Commits), `scripts/AGENTS.md`
- Host: `df`/`btrfs`, `docker system df`, `/etc/docker/daemon.json`, Root-Crontab, `/etc/cron.d`, systemd-Timer, `agent-host-stable.log` und die Agent-Host-Registry von VS Code Server

## Geänderte Bereiche

**Im Repo (neu):**

- `scripts/vm_storage_vscode_cleanup.py` + `..._selftest.py`: VS-Code-Server-Cleanup (Dry-Run ist Standard) und Selbsttest (34 Prüfungen)
- `scripts/vm_storage_docker_maintenance.sh` + `..._selftest.sh`: konservative Docker-Wartung (nur alter Build-Cache) und Test mit Docker-Stub (7 Prüfungen)
- `scripts/vm_storage_disk_watch.sh` + `..._selftest.sh`: Speicherüberwachung (17 Prüfungen)
- `scripts/vm_storage_install.sh`: Installer und Wiederherstellung auf einer neuen VM, `--check` führt alle Tests aus
- `infra/host-maintenance/`: sechs systemd-Units und die `docker-daemon.json`-Vorlage
- `docs/runbooks/vm-storage-maintenance.md`: Betrieb, Wiederherstellung, Rückbau
- `.gitattributes`: LF-Zeilenenden für diese Dateien

**Auf dem Host (installiert über `vm_storage_install.sh`):**

- `/usr/local/sbin/{vscode-server-cleanup,docker-safe-maintenance,disk-watch}`, Selbsttests unter `/usr/local/share/vm-storage-maintenance/`
- Timer (alle `enabled`): `vscode-server-cleanup.timer` sonntags 05:15, `docker-safe-maintenance.timer` sonntags 05:45 (je + bis 15 min Versatz, `Persistent=true`), `disk-watch.timer` stündlich
- Root-Crontab: der Eintrag `docker system prune -af --volumes` (täglich 03:00) wurde entfernt, ein Hinweiskommentar ersetzt ihn; das Original liegt gesichert unter `/root/maintenance-backups/`
- Rollback-Images geschützt durch Tags `rollback/promat-prod-web:2026-10-20` (`be2eef45c21d`) und `rollback/corapan-infra-web:2026-10-20` (`62e6d424449f`)
- `/etc/logrotate.d/docker-unbounded-container-logs`: wird jetzt von `docker-safe-maintenance` erzeugt (siehe unten)
- Drei verwaiste VS-Code-Agent-Hosts (PID 2420903, 2421076, 2421273) beendet; Registry und Lock-File vorher gesichert

## Wichtige Entscheidungen

- **Docker-Prune-Cron entfernt statt umgestellt:** Er löschte alle von keinem Container genutzten Volumes und alle ungenutzten Images (Rollback-Images eingeschlossen). Ersatz ist ein Timer, der nur Build-Cache älter als 7 Tage entfernt; Images (auch ungetaggte), Container, Netzwerke und Volumes werden nie automatisch gelöscht. Der Installer prüft per Textsuche, dass das Skript keine solchen Befehle enthält, und der Test lässt jeden Docker-Aufruf aufzeichnen und gegen eine Allow-List prüfen.
- **Ungetaggte Images sind nicht sicher entbehrlich:** Das games-Deploy-Skript (anderes Repo, nicht geändert) ruft `docker image prune -f` auf und würde ungetaggte Rollback-Images hostweit löschen. Darum der Tag-Namespace `rollback/` statt einer Löschregel.
- **Agent-Hosts:** Die aktuelle Registry (`~/.config/Code/agent-host/local-endpoint/entries/`) kennt nur PID 3420750. Die drei Hosts vom 22.05. waren dort nicht registriert, hatten keine Kindprozesse und keine einzige aufgebaute Verbindung und waren die drei gleichzeitigen Downloader. Sie wurden mit SIGTERM beendet, nachdem unmittelbar vorher dieselben Bedingungen erneut geprüft wurden; der registrierte Host und seine Registry blieben unverändert. Ein anschließender `code agent host`-Aufruf meldet `already running (PID 3420750)` und startet keinen zweiten. Eine unterstützte Konfigurationsoption gegen mehrfache Update-Downloads gibt es nicht (`--idle-timeout`/`--replace` wirken nur beim Start durch den Client bzw. würden den laufenden Host beenden).
- **Log-Rotation ohne doppelte Rotation:** `docker-safe-maintenance` listet nur Container mit leerer `LogConfig` in der logrotate-Überbrückung und löscht die Datei, sobald keiner mehr übrig ist. Wird ein Container neu erstellt, gilt die native Rotation aus `daemon.json`. Keine Container wurden dafür neu erstellt.
- **Nachschärfung des Cleanups gegenüber der ersten Fassung:** Fehlschläge beim Löschen zählen als Fehler (Exit 1, `delete-failed`, `summary result=errors`); unter systemd tragen Zeilen Journal-Prioritäten (`journalctl -p err` findet sie); unerwartete Ausnahmen werden als `unexpected-error` geloggt; die `Condition`-Zeile in der Unit entfiel, damit ein fehlendes Verzeichnis nicht stumm als „übersprungen“ erscheint.
- **Fund durch die Tests:** `mawk` kappt `printf "%d"` bei 2³¹; das 3-GiB-Wachstumslimit wäre als ca. 2 GiB gerechnet worden. Ersetzt durch Bash-Arithmetik.

## Abweichungen

Keine Abweichung von Spezifikation oder Konventionen. Die Skripte liegen flach unter `scripts/` (nach `scripts/AGENTS.md`), die Units unter dem bestehenden `infra/`. Hostindividuelles (die vorhandene Mail-Warnung `disk-check.sh` mit Adresse, Container-IDs) ist nicht versioniert.

## Verifikation

- Root-Dateisystem: 85 % (42 G belegt, 7,5 G frei) → 59 % (29 G belegt, 21 G frei). Davon VS Code ca. 12,1 GB (`/root/.vscode-server` 18 G → 5,8 G); Docker: Build-Cache 0,5 GB, ein Image 0,3 GB, Container-Logs von zusammen ca. 0,7 GB auf 36 KB im Live-Log (komprimierte Kopien bleiben).
- Selbsttests: VS-Code-Cleanup 34/34, disk-watch 17/17, Docker-Wartung 7/7; wiederholter Installer-Lauf unverändert; `ci_governance_checks.py` und `ruff` grün.
- Echte Läufe über systemd: alle drei Services `success`; Dry-Run des Cleanups gegen das echte Verzeichnis ohne Kandidaten (5 Einträge, alle begründet behalten).
- Fehlerpfad: Ein absichtlich fehlerhafter Aufruf über `systemd-run --wait` liefert Exit 2 und einen Journal-Eintrag mit Priorität `err`; ein Löschfehler (unveränderliche Datei) im Test ergibt Exit 1 und `result=errors`.
- Produktion unverändert: alle 11 Container laufen und sind (soweit mit Healthcheck) `healthy`; `https://pronunciation-matters.de/ready` antwortet 200. Beide behaltenen Server (1.141.2, 1.141.0) starten (`code-server --version`). Es gibt keinen Prune-Befehl mehr in Crontab, `/etc/cron.d` und `/etc/cron.daily`. Keine fehlgeschlagenen systemd-Units.

## Offene Punkte

- **Mehrfach-Downloads noch nicht am Echtfall bestätigt:** Ob das nächste VS-Code-Release nur noch einen Download auslöst (jetzt durch den einzigen Host `3420750` im `:31`-Takt), zeigt erst das Log nach dem nächsten Release (`grep -c "Downloading server" ~/.vscode-server/cli/agent-host-stable.log`, erwartet 1 je Version statt 3). Startet ein Client wieder mehrere Hosts, fängt der Timer die Folgen auf.
- **Unvollständige Installationen:** `6d62…` (1.142.0, Ziel nur teilweise befüllt, vollständiges `.staging` ist 5,7 Tage alt) und `7baa…` (1.141.1) bleiben bis zur Altersgrenze; VS Code installiert beim nächsten Verbinden nach.
- **Fremdes Deploy-Skript:** `games_hispanistica/app/scripts/update.sh` (Zeile `docker image prune -f`) wurde nicht geändert. Ungetaggte Images anderer Anwendungen ohne `rollback/`-Tag bleiben dadurch gefährdet.
- **Neuerstellung der drei Container:** `hedgedoc_app`, `hedgedoc_db`, `marele-container` erhalten das native Limit erst bei Neuerstellung; die Überbrückung entfällt dann selbsttätig.
- **Nicht angefasst:** `/root/.vscode-server/data/CachedExtensionVSIXs` (ca. 1 G).
- Der Commit wurde nicht gepusht (Push auf `main` löst ein Deployment aus).

## Nächste sinnvolle Schritte

- Nach dem ersten automatischen Lauf (Sonntag, 2026-10-25) `journalctl -u vscode-server-cleanup -u docker-safe-maintenance -u disk-watch --since -2d` prüfen.
- Nach dem nächsten VS-Code-Release die Download-Zahl im Agent-Host-Log prüfen (siehe oben).
- Rollback-Tags freigeben, sobald die Vorgänger-Images nicht mehr gebraucht werden: `docker rmi rollback/<name>:<datum>`.
