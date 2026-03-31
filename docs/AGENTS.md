# PROMAT Docs Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` für Arbeiten unter `docs/`.

## Rollen der Doku-Bereiche

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md` ist die bindende Spezifikation.
- `docs/architecture/` erklärt die aktive Architektur und ihre Grenzen.
- `docs/conventions/` hält aktive Arbeits- und Benennungsregeln fest.
- `docs/runbooks/` enthält wiederholbare Betriebs- und Arbeitsabläufe.
- `docs/decisions/` enthält nur dauerhafte Architekturentscheidungen.
- `docs/agent-runs/` enthält substanzielle Run-Protokolle.
- `docs/start/` bleibt die historische Bootstrap- und Umbauchronik.

## Dokumentationsregeln

- Neue aktive Regeln kommen nicht in `docs/start/`, sondern in `docs/conventions/`, `docs/architecture/` oder `docs/runbooks/`.
- Run-Logs beschreiben Änderungen, ersetzen aber keine aktive Referenzdokumentation.
- Wenn ein Dokument veraltet ist, aktualisiere oder markiere es als historisch statt eine konkurrierende Kopie anzulegen.
- Doku muss repo-spezifisch, knapp und operational bleiben.

## Run-Dokumentation

- Für jeden substantiellen Run: Eintrag unter `docs/agent-runs/` nach Template.
- Für Bootstrap-, Setup- oder Governance-Runs zusätzlich ein Eintrag unter `docs/start/`.
- Für dauerhafte Architekturentscheidungen zusätzlich ein ADR unter `docs/decisions/`.

## No-Go

- Keine Schatten-Dokumentation mit widersprüchlichen Regeln.
- Keine stillen Architekturänderungen ohne passende Doku-Aktualisierung.
- Keine neue aktive Governance in historischen Run-Logs verstecken.