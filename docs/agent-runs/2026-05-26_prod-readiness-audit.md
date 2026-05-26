# Prod-Readiness Read-only Audit

## 1. Executive Summary
Keine Dateien wurden geändert. Keine Fixes, keine Formatierung, keine Backups, keine Commits.

Mein Gesamturteil: in dem aktuell geprüften Zustand nicht prod-ready. Die klaren Blocker sind nicht kosmetisch, sondern operativ und sicherheitsrelevant: sensible Reset-/Invite-Inhalte werden geloggt, das Produktions-Image startet die App über den Werkzeug-Server statt über einen produktionsgeeigneten WSGI-Server, das Rate Limiting hängt an einem In-Memory-Backend, und die aktuelle lokale Baseline ist nicht grün.

Wichtig für die Einordnung: Es gibt auch positive Gegenbefunde. Research-Detailrouten und Audio-Assets sind serverseitig gegated, Admin-Flächen sind mit JWT plus Rollenprüfung geschützt, CSRF ist in der Basiskonfiguration eingeschaltet, und die Teaching-Markdown-Pipeline deaktiviert rohes HTML. Die größten Risiken liegen also eher in Betriebs- und Logikschichten als in einer offensichtlichen öffentlichen Datenfreigabe.

## 2. Bewertungsmatrix

| Bereich | Status | Priorität | Einordnung |
|---|---|---:|---|
| Auth-/Token-Handling | Rot | P0 | Sensible Reset-/Invite-Inhalte landen im Log |
| Produktions-Runtime | Rot | P0 | Prod-Container fährt Werkzeug statt Gunicorn/äquivalent |
| Abuse-/Bruteforce-Schutz | Rot | P1 | Limits vorhanden, aber nur mit In-Memory-Speicher |
| Test-Baseline | Rot | P1 | Lokale Fokus-Suiten haben reproduzierbare Fehler |
| Security-Härtung | Gelb | P2 | Gute Basis, aber CSP/CDN/Inline-Style-Härtung offen |
| Design-System/CSS | Gelb | P2 | Zwei UI-Systeme parallel geladen |
| Asset-Performance | Gelb | P2 | Einzelne unnötig schwere Fonts/Bilder |
| Repo-Hygiene | Gelb | P3 | Debug-/QA-Dateien tracked, Ignore-Regeln teils wirkungslos |
| Legacy-/Architekturrest | Gelb | P3 | Teilweise vorbereitete, aber nicht produktiv verdrahtete Pfade |

## 3. P0/P1-Befunde

1. Sicherer Befund, P0: Passwort-Reset- und Invite-Inhalte inklusive Reset-Link werden serverseitig geloggt.
   Beleg: auth.py und admin.py.
   Risiko: Jeder Log-Zugriff wird faktisch zu einem Zugriff auf gültige Reset-/Invite-Journeys. Dazu kommt unnötige PII-Exposition im Log.
   Bewertung: Das ist kein theoretischer Hardening-Wunsch, sondern eine echte Geheimnisweitergabe in Betriebsartefakte.

2. Sicherer Befund, P0: Das Produktions-Image startet die App mit Python plus Werkzeug-Server.
   Beleg: Dockerfile und main.py.
   Risiko: schwächere Produktionshärte bei Concurrency, Restart-Verhalten, Proxy-Betrieb, Timeouts und operativer Robustheit. Besonders auffällig ist, dass Gunicorn in den Dependencies existiert, aber nicht der Container-Entrypoint ist.
   Bewertung: Für einen echten Prod-Run ist das ein Blocker.

3. Sicherer Befund, P1: Das Rate Limiting nutzt nur In-Memory-Speicherung.
   Beleg: __init__.py.
   Risiko: Limits resetten nach Neustarts, skalieren nicht über mehrere Instanzen und sind bei horizontalem Betrieb nicht verlässlich. Die Auth-Routen haben zwar Limits, aber die Speicherstrategie macht den Schutz operativ schwach.
   Gegenbeleg zur Einordnung: Limits auf sensiblen Auth-Pfaden existieren tatsächlich, etwa in auth.py und auth.py.

4. Sicherer Befund, P1: Die lokale Release-Baseline ist nicht grün.
   Beleg für den erwarteten Gate-Charakter der Suiten: ci.yml, test_auth_phase1.py und test_research_sessions.py.
   Ergebnis: Die Auth-Phase-Tests hatten 1 Fehler bei 46 Fällen, die Research-Session-Tests 9 Fehler bei 201 Fällen. Die Fehler sind keine rein technischen Flakes, sondern sichtbare inhaltliche und Zustandsregressionen, unter anderem Label-Abweichungen und ein Client-State-Fehler mit fehlendem items-Feld.
   Bewertung: Kein direkter Sicherheitsfehler, aber ein klarer Shipping-Stopper.

## 4. P2/P3-Befunde

1. Sicherer Befund, P2: Das Basetemplate lädt parallel ein großes MD3-Paket und das neuere PM/PROMAT-CSS.
   Beleg: base.html bis base.html.
   Risiko: höhere Kollisionswahrscheinlichkeit, schwerere Wartung, größere CSS-Nutzlast und unklare Design-System-Grenzen. Das ist eher Architektur- als Sofortausfall-Risiko, aber es bremst jede weitere UI-Arbeit.

2. Sicherer Befund, P2: Die Shell ist von externen Font-/Icon-CDNs abhängig und die CSP lässt Inline-Styles zu.
   Beleg: base.html, base.html, base.html und __init__.py.
   Risiko: größere externe Abhängigkeit, breitere Ausfallfläche und schwächere CSP-Härtung als nötig.
   Bewertung: Kein akuter Exploit-Beweis, aber eine saubere P2-Härtungsbaustelle.

3. Sicherer Befund, P2: Einzelne statische Assets sind unnötig schwer.
   Beleg: MaterialSymbolsRounded.woff2, unterricht_01.png, forschung_01.png, 30_components.css.
   Ergebnis: Das größte Web-Asset ist die Material-Symbol-Font mit rund 4,9 MB, dazu kommen Kartenbilder mit rund 2,1 MB und 1,0 MB.
   Einordnung: Die Content-Audios unter teaching sind vergleichsweise klein; der Web-Overhead sitzt eher in Shell-/Visual-Assets.

4. Wahrscheinlicher Befund, P3: Das Refresh-Token-Subsystem ist vorbereitet, aber im aktiven Login-Flow nicht produktiv verdrahtet.
   Beleg: services.py, services.py, services.py, gegenüber auth.py und auth.py.
   Risiko: unnötige Komplexität, missverständliche Sicherheitsarchitektur und höherer Wartungsaufwand.
   Bewertung: Kein akuter Prod-Blocker, aber ein guter Kandidat für Klarstellung oder Entfernung.

5. Sicherer Befund, P3: Repo-Hygiene weicht von der eigenen Governance ab.
   Beleg: tracked sind start.txt, _es_diag.txt, qa_check.py, simple_qa.py und capture_qa.py. Gleichzeitig versucht .gitignore bis .gitignore, genau solche Artefakte auszuschließen.
   Risiko: schwächere Auditierbarkeit, unklare Repo-Grenzen und wiederkehrende Debug-Reste im Hauptbaum.
   Einordnung: Hygieneproblem, kein Laufzeitblocker.

6. Wahrscheinlicher Befund, P3: Medienrouten verzichten auf ETags.
   Beleg: public.py, public.py, public.py.
   Risiko: schlechtere Cache-Revalidierung und unnötige Bandbreite bei wiederholten Downloads.
   Bewertung: eher Performance- als Sicherheitsproblem.

## 5. Security-Bewertung
Positiv: Research-Detailrouten und Player-Audio sind serverseitig vor dem Rendern bzw. vor der Auslieferung gegated, siehe public.py, public.py und public.py. Admin-Routen sind sauber mit JWT plus Rollenprüfung geschützt, siehe admin.py und admin.py. CSRF ist standardmäßig aktiv, siehe __init__.py, und die JS-Mutationspfade setzen sichtbar den X-CSRF-TOKEN-Header, siehe api.js und api.js.

Negativ: Die stärksten Sicherheitsprobleme sitzen derzeit nicht an fehlender Auth-Grenze, sondern an Log-Leaks, unzureichend prod-tauglicher Runtime und operativ schwachem Rate-Limit-Backend. Dazu kommt eine CSP, die noch Inline-Styles und mehrere Drittquellen zulässt, siehe __init__.py.

Offene Frage: Ich habe keine vollständige negative End-to-End-Prüfung aller Mutationspfade gefahren. Die sichtbare CSRF-Verdrahtung spricht eher gegen einen schnellen CSRF-Befund, aber eine echte Missbrauchsprüfung steht aus.

## 6. Design-System/CSS-Bewertung
Die Webapp trägt derzeit zwei Schichten gleichzeitig: ein breites MD3-Paket und das PM/PROMAT-System in derselben Basisshell, siehe base.html bis base.html. Das ist nicht automatisch falsch, aber es erzeugt klare Systemschuld: schwerere Stylesheets, unklare Zuständigkeiten und höhere Regressionsempfindlichkeit.

Dazu kommt, dass die größte einzelne CSS-Datei 30_components.css bereits rund 233 KB hat. Zusammen mit externen Font-/Icon-Layern und der 4,9-MB-Icon-Font ist das eher ein kontrollierbarer Architekturrest als ein sofortiger Bug, aber für Cold-Load und Wartbarkeit eindeutig ein P2-Thema.

## 7. Legacy-/Cleanup-Kandidaten
Sicherer Befund: Ältere historische Run-Logs referenzieren massiv die frühere sample-Fläche, aber der aktuelle Produktzustand erwartet ausdrücklich, dass diese Route entfernt ist. Der Gegenbeleg ist test_research_sessions.py. Das ist kein aktueller Routing-Fehler, sondern historische Doku.

Falscher Alarm / bewusst akzeptierter Zustand: Die größten Repo-Dateien lagen fast vollständig in lokaler .venv, tmp oder untracked Intake-Caches. Für import ist aktuell nur .gitkeep tracked. Das ist lokaler Zustand, nicht Repo-Bloat im engeren Sinn.

Falscher Alarm / bewusst akzeptierter Zustand: Die vielen safe-Ausgaben im Teaching-Rendering sind für sich genommen kein XSS-Beweis, weil die zentrale Markdown-Pipeline rohes HTML deaktiviert, siehe teaching_content.py. Die Template-Stellen in _teaching_blocks.html und folgenden Zeilen sind deshalb eher eine Prüfspur als ein bestätigter Leak.

Offene Frage: Es gibt viele innerHTML-Senken in JS, etwa in admin_users.js, research-comparison.js und alert-utils.js. In den von mir gelesenen repräsentativen Pfaden wird escaped, aber ich habe keinen vollständigen Taint-Audit aller Hilfsfunktionen durchgeführt.

## 8. Tests und Checks
Ausgeführt wurde ein reiner Read-only-Check.

Die wichtigsten Ergebnisse:
- Auth-Tests: 45 bestanden, 1 fehlgeschlagen.
- Research-Session-Tests: 192 bestanden, 9 fehlgeschlagen.
- Python-Compile-Check für den App-Code lief ohne sichtbaren Syntaxfehler durch.
- Ruff und Mypy konnten in der aktuellen lokalen venv nicht ausgeführt werden, weil die Tools dort nicht installiert waren, obwohl sie in der CI vorgesehen sind, siehe ci.yml.

Zusatz zur Asset-Prüfung:
- größte Web-Gewichte: MaterialSymbolsRounded.woff2, unterricht_01.png, forschung_01.png
- Teaching-Content selbst ist vergleichsweise leichtgewichtig
- größte Repo-Dateien insgesamt sind überwiegend lokale Tool-/Import-Artefakte, nicht Git-Inhalt

## 9. Konkrete Folgeprompts

1. Entferne jede serverseitige Protokollierung von Reset-/Invite-Inhalten und Token-Links aus den Auth- und Admin-Flows. Behalte die bestehende Admin-Preview-UX bei, aber sorge dafür, dass Logs nur Metadaten ohne Geheimnisse oder Mail-Body enthalten. Ergänze fokussierte Tests für Logging-Verhalten und Preview-Responses.

2. Stelle den Produktions-Container auf einen produktionsgeeigneten WSGI-Server um. Nutze die bestehende Gunicorn-Dependency, definiere sinnvolle Worker-/Timeout-/Proxy-Einstellungen und halte Health-Checks sowie Startkommandos zwischen Container, Runtime und Doku konsistent.

3. Ersetze das In-Memory-Rate-Limit-Backend durch einen persistenten, multi-instance-tauglichen Store und validiere die Limits auf Login-, Forgot-Password-, Reset- und Admin-Mutationspfaden mit fokussierten Tests.

4. Behebe die aktuell fehlschlagenden Auth- und Research-Session-Tests zuerst, bevor weitere UI- oder Architekturarbeit startet. Arbeite die inhaltlichen Label-Regressions und den fehlenden items-State im Player deterministisch ab und stelle lokal grüne Fokus-Suiten wieder her.

5. Erstelle eine gezielte Design-System-Inventur: Welche MD3-Komponenten sind noch produktiv, welche PM/PROMAT-Familien sind kanonisch, welche Layer können entfallen. Liefere am Ende eine klare Migrationsgrenze statt weiterer Mischzustände.

6. Führe einen gezielten Performance-Pass für statische Assets durch: reduziere oder subsette die Material-Symbol-Font, komprimiere die großen Kartenbilder und prüfe, welche externen Font-/Icon-Abhängigkeiten lokalisiert oder reduziert werden können.

## 10. Klare No-Go-Liste
- Kein Prod-Deploy, solange Reset-/Invite-Links weiterhin in Logs landen.
- Kein Prod-Deploy auf Basis des aktuellen Werkzeug-Entrypoints im Container.
- Kein Vertrauen in horizontale Skalierung oder harte Abuse-Schutz-Aussagen mit dem aktuellen In-Memory-Limiter.
- Kein Release mit dem aktuellen nicht-grünen lokalen Testzustand.
- Keine große UI-Migration ohne vorherige Festlegung, welches Design-System produktiv führend ist.
- Keine pauschale Bereinigung von tmp-/Import-Artefakten, ohne tracked und untracked Zustand sauber zu trennen.