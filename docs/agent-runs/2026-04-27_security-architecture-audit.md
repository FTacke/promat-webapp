# PROMAT Security Architecture Audit

Datum: 2026-04-27
Scope: Security-Header, Auth-Architektur, Session-/Token-Handling, Research-Zugriff, CI-/Supply-Chain-nahe Sicherheitsguardrails
Artefakttyp: nicht-normativer Auditbericht

## Executive Summary

Die Anwendung zeigt bereits mehrere richtige Grundentscheidungen fuer einen spaeteren Umgang mit geschuetzten Forschungsdaten:

- serverseitige Gating-Semantik fuer Research-Oberflaechen
- owner-gebundene Set-API unter geschuetztem Pfad
- Zugriffstrennung zwischen `data/`, `public/` und `secure/`
- Login- und Access-Request-Flaechen als getrennte Eintritte
- Passwort-Reset-/Lockout-Mechanismen im Auth-Service

Trotzdem ist die Security-Architektur noch nicht produktionsreif. Die kritischsten Probleme liegen an drei Stellen:

1. inkonsistenter Token-Lifecycle zwischen Frontend und Backend
2. unbereinigte bzw. veraltete Security-Header- und Error-Handling-Pfade
3. schwache `.github`- und CI-Guardrails fuer einen spaeteren produktiven Forschungsbetrieb

Gesamturteil: brauchbare Sicherheitsbasis, aber keine harte produktive Absicherung.

## Positive Sicherheitsmerkmale

### 1. Gute Runtime-Trennung sensibler Datenraeume

Die Doku- und Codebasis verteidigt die Trennung zwischen:

- `data/` fuer geschuetzte Forschungsdaten
- `public/` fuer explizit freigegebene Artefakte
- `secure/` fuer Klardaten und Einwilligungsunterlagen ausserhalb des Webapp-Zugriffs

Bewertung: fachlich und datenschutzrechtlich richtig.

### 2. Research-Zugriff ist grundsaetzlich serverseitig gedacht

Die Research-Architektur folgt dem richtigen Prinzip: Schutz vor dem Rendern, nicht erst durch spaetere Client-Hinweise. Das ist fuer sensible Sprachdaten zentral.

Bewertung: klar positiv.

### 3. Passwort- und Lockout-Basis ist vorhanden

Im Auth-Service sind Passwort-Hashing, Passwortstaerkevalidierung, Reset-Token-Logik und ein Lockout-Mechanismus nach Fehlversuchen sichtbar angelegt.

Bewertung: gute Basis fuer einen spaeteren produktiven Betrieb.

## Kritische Findings

### S1. Token-Lifecycle ist architektonisch inkonsistent

Prioritaet: P1

Befund:

- das Frontend erwartet einen stillen Refresh-Flow ueber `/auth/refresh`
- dieser Endpoint ist im gelesenen Backend-Routing nicht vorhanden
- gleichzeitig werden Access-Token-Cookies gesetzt und Session-Antworten ausgewertet

Sicherheitswirkung:

- unklarer, nicht dokumentierter Session-Lifecycle
- moegliche Fehlannahmen ueber Ablauf, Revocation und Recovery bei 401-Zustaenden
- Gefahr, dass spaeterer Schutz auf einer nicht real vorhandenen Sicherheitsstufe aufsetzt

Warum das sicherheitsrelevant ist:

Ein inkonsistenter Token-Lifecycle ist kein Komfortproblem. Er betrifft direkt die Frage, ob Sessionablauf, Zwangs-Logout, Wiederanmeldung und API-Verhalten unter Last und im Fehlerfall korrekt und nachvollziehbar bleiben.

Empfehlung:

1. Kanonischen Session-/Token-Mechanismus explizit spezifizieren.
2. Refresh entweder vollstaendig produktiv umsetzen oder alle aktiven Refresh-Module entfernen.
3. Danach 401/403-/Session-Ablaufpfade gezielt testen.

### S2. Security-Header-Mix enthaelt veraltete und zu weite Freigaben

Prioritaet: P1

Befund in `app/src/app/__init__.py`:

- `X-XSS-Protection` wird gesetzt
- CSP erlaubt `style-src 'unsafe-inline'`
- CSP erlaubt externe CDN- und Google-Font-Quellen
- `frame-src` erlaubt YouTube-Einbettung

Bewertung:

- `X-XSS-Protection` ist veraltet und bringt auf modernen Browsern keinen echten Mehrwert
- `unsafe-inline` fuer Styles schwacht CSP spuerbar ab
- externe Font- und CDN-Abhaengigkeiten vergroessern die Angriffs- und Verfuegbarkeitsflaeche

Das ist nicht automatisch inakzeptabel, aber fuer eine spaeter produktive Forschungsplattform mit geschuetzten Daten zu permissiv.

Empfehlung:

1. CSP auf Minimalprinzip haerten.
2. externe Assets soweit moeglich lokal ausliefern.
3. Inline-Styles schrittweise abbauen und `unsafe-inline` auslaufen lassen.
4. veraltete Header entfernen und nur moderne Schutzmechanismen pflegen.

### S3. Doppelte Error-/Handler-Pfade sind auch ein Security-Risiko

Prioritaet: P1

Wenn in `app/src/app/__init__.py` konkurrierende Error-Handler und Logging-Pfade existieren, ist nicht nur Wartbarkeit betroffen. Es wird auch unsicherer, welche Sicherheitsreaktion im Fehlerfall tatsaechlich greift.

Risiken:

- HTML- und API-Fehlerpfade koennen unterschiedlich haerten
- Logging und Incident-Nachvollziehbarkeit werden unklar
- Security-Fixes koennen am falschen Handler landen

Empfehlung:

- einen einzigen aktiven Fehler- und Logging-Pfad etablieren

### S4. Access-Request speichert sensible Zusatzdaten ohne sichtbare Lifecycle-Strategie

Prioritaet: P1

Der Access-Request-Flow speichert neben Stammdaten auch:

- Zweck der Nutzung
- angefragten Pfad
- User-Agent
- IP-Adresse

Das kann fachlich vertretbar sein, braucht fuer einen spaeteren produktiven Betrieb aber klare Regeln zu:

- Zweckbindung
- Aufbewahrungsdauer
- Einsichts- und Loeschprozess
- Admin-Sichtbarkeit und Exportfaehigkeit

Aktuell ist die Datenerhebung sichtbar, aber eine klare Daten-Lifecycle-Architektur war im gelesenen Scope nicht gleichwertig sichtbar.

Empfehlung:

1. Retention- und Review-Regeln spezifizieren.
2. PII-Minimierung pruefen.
3. Admin-Zugriff auf diese Datensaetze separat auditieren.

## Weitere relevante Findings

### S5. CI enthaelt fest codierte Test-Secrets und DB-Struktur

Prioritaet: P1

In `.github/workflows/ci.yml` stehen Test-Secrets und eine konkrete DB-URL hart im Repository.

Auch wenn das Testwerte sind, ist das fuer eine spaeter produktive Sicherheitskultur das falsche Muster.

Empfehlung:

- Secrets und sensible CI-Konfiguration auch fuer Testumgebungen nicht als Normalfall hart im Repo etablieren

### S6. Keine Security-Policy, kein CODEOWNERS, kein Dependabot

Prioritaet: P2

Es fehlen mehrere organisatorische Sicherheitsguardrails:

- `.github/SECURITY.md`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`

Sicherheitswirkung:

- unklare Meldewege fuer Schwachstellen
- keine formalisierte Verantwortungszuordnung fuer sensible Dateien
- keine sichtbare Standardautomatisierung fuer Dependency-Updates und Supply-Chain-Pruefung

### S7. CI prueft kein pytest

Prioritaet: P1

Die vorhandene CI fuehrt Ruff und Compile-Checks aus, aber keine Tests.

Sicherheitswirkung:

- Research-Access-, Auth- und Session-Regressionen koennen leichter mergebar bleiben
- Governance-Regeln sind organisatorisch vorhanden, aber technisch untererzwingt

### S8. Refresh-/Session-Module loggen zu viel in die Konsole

Prioritaet: P3

Die aktiven Refresh-Module enthalten zahlreiche `console.log`-/`console.warn`-/`console.error`-Meldungen. Das ist in der Entwicklung tolerabel, sollte aber im spaeteren produktiven Sicherheitsmodus kontrolliert werden.

## Datenschutznaher Befund

Fuer eine App mit pseudonymisierten Sprachdaten und Access Requests fuer Forschungseinrichtungen ist nicht nur technische Security relevant, sondern auch nachweisbare Datenverantwortung. Die aktuelle Architektur zeigt gute Intentionen, aber noch nicht durchgehend dieselbe Reife in folgenden Punkten:

- Retention und Zweckbindung fuer Access-Request-Daten
- klare Session-/Token-Policy
- harte Shared-Template- und i18n-Disziplin bei User-facing Security-Flaechen
- reproduzierbare und verifizierbare Security-Checks in CI

## Priorisierte Empfehlungen

### Sofortblocker vor produktivem sensiblen Betrieb

1. Token- und Session-Architektur entscheiden und implementativ angleichen.
2. Security-Header und externe Asset-Abhaengigkeiten haerten.
3. konkurrierende Error-/Logging-Handler entfernen.
4. CI um Tests und mindestens grundlegende Governance-/Security-Pruefungen erweitern.

### Kurzfristige Haertung

5. Access-Request-Daten-Lifecycle spezifizieren.
6. SECURITY.md, CODEOWNERS und Dependabot einfuehren.
7. Shared Error-Seiten und Footer bilingual und zentralisiert machen.

### Mittelfristige Reife

8. Auditable Security-Testfaelle fuer Auth-/Research-Zugriff etablieren.
9. CSP weiter verengen und Inline-/CDN-Abhaengigkeiten abbauen.

## Audit-Fazit

PROMAT ist nicht sicherheitsnaiv. Die Grundtrennung der Datenraeume und die serverseitig gedachte Research-Zugriffsschicht sind richtige Entscheidungen. Die eigentlichen Risiken entstehen derzeit durch Inkonsistenz und unvollstaendige Haertung an den Systemgrenzen. Das ist reparierbar, muss aber vor einem ernsthaften produktiven Einsatz mit sensiblen Forschungsdaten prioritaer behandelt werden.