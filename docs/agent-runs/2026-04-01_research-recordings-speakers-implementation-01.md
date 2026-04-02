# Research Recordings Speakers Implementation 01

Datum: 2026-04-01

## Ziel

Die spanischen Forschungsseiten `recordings` und `speakers` entsprechend des verbindlichen PROMAT-Konzepts als funktionale Workbench-Seiten implementieren, einschließlich Sprecherprofilroute und vorbereiteter Player-Zielroute.

## Consulted Sources

* `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
* `AGENTS.md`
* `app/AGENTS.md`
* `docs/AGENTS.md`
* `scripts/AGENTS.md`
* `.github/instructions/repo.instructions.md`
* `app/src/app/runtime_paths.py`
* `app/src/app/config/__init__.py`
* `docker-compose.dev-postgres.yml`
* `app/infra/docker-compose.prod.yml`
* `docs/research_pages/promat_recordings_speakers.md`
* `docs/agent-runs/2026-03-31_dev-example-spanish-seed-01.md`
* `scripts/session_setup/seed_dev_spanish_example_sessions.py`
* `scripts/session_setup/dev_spanish_example_sessions.json`

## Geänderte Bereiche

* Research-Routing in `app/src/app/routes/public.py`
* dateibasierter Session-Zugriff und View-Modelle unter `app/src/app/`
* neue Templates und Partials unter `app/templates/`
* Workbench-spezifische Styles im bestehenden CSS-System unter `app/static/css/`
* Referenz- und Run-Dokumentation unter `docs/research_pages/` und `docs/agent-runs/`

## Wichtige Entscheidungen

* Die spanischen Forschungsseiten lesen Sessions direkt aus `data/sessions/spanish/{session_id}/metadata.json`, statt eine neue Datenquelle oder Zwischenstruktur einzuführen.
* `recordings` und `speakers` bleiben auf den bestehenden Research-Routen, werden für Spanisch aber auf spezialisierte Templates und View-Modelle umgestellt.
* Die Player-Zielroute wird bereits für alle drei kanonischen Tasks vorbereitet, obwohl die aktuellen Dev-Beispielmetadaten diese Task-Abdeckung noch nicht überall vollständig ausweisen.
* Fehlende strukturierte Exposure-Werte werden in der UI transparent als `Nicht erfasst` dargestellt, statt heuristisch zu `Ja` oder `Nein` umgedeutet zu werden.
* Bei mehrfachen Sessions pro `person_id` verwendet die Profilseite zunächst eine primäre Session, ohne spätere Mehrfach-Session-Logik auszuschließen.

## Abweichungen

* Keine Abweichung von Routing-Schema, Runtime-Grenzen oder Dev/Prod-Parität eingeführt.
* Der aktuelle Dev-Datensatz bleibt inhaltlich begrenzt; die UI bildet deshalb bereits die Zielroute ab, ohne den Player fachlich vorwegzunehmen.

## Verifikation

* Python-Fehlerprüfung für `app/src/app/research_sessions.py`, `app/src/app/research_views.py` und `app/src/app/routes/public.py` ausgeführt, ohne Befunde.
* Bestehende spanische Session-Metadaten und Seed-Skripte gegen die neue Reader-Logik geprüft.
* Routen- und Seiteneinbindung manuell gegen die bestehende Public-Shell und Panel-Navigation abgeglichen.

## Offene Punkte

* Template- und CSS-Validierung im laufenden Dev-Server braucht noch einen expliziten Neustart oder einen Test-Client-Lauf.
* Der Player ist weiterhin nur Stub und enthält noch keine Fachlogik für Audio, Transkript oder Vergleich.
* Strukturierte Exposure-Metadaten fehlen weiterhin im aktuellen spanischen Dev-Datensatz.

## Nächste sinnvolle Schritte

* HTTP-/Template-Validierung der neuen Seiten gegen den laufenden Dev-Stack durchführen.
* Danach den eigentlichen Player fachlich implementieren.
* Anschließend die spanischen Dev-Metadaten um strukturierte Exposure-Felder und konsistente Task-Dokumentation erweitern.