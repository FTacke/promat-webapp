# PROMAT .github, Instructions, Skills and Workflow Audit

Datum: 2026-04-27
Scope: `.github/`, CI-Workflow, PR-/Issue-Templates, Copilot-/Instructions-Layer, Repo-Governance-Umsetzung
Artefakttyp: nicht-normativer Auditbericht

## Executive Summary

Der `.github`-Bereich ist fuer Governance und Agentenfuehrung sichtbar ernsthaft gepflegt, aber technisch untererzwingt. Die groesste Schwachstelle ist nicht fehlende Regelabsicht, sondern die Luecke zwischen dokumentierter Disziplin und technischer Durchsetzung.

Konkret:

- die Governance ist sehr praesent in Templates und Instructions
- CI prueft aber nur Ruff und Compile, nicht die vorhandenen Tests und nicht die wichtigsten Governance-Annahmen
- relevante organisatorische Sicherheitsartefakte fehlen
- Teile der `.github`-Anweisungen duplizieren Regeln, die bereits in `AGENTS.md` und `docs/spec/` gebunden sind

Gesamturteil: gute Regelkultur, aber noch keine ausreichend starke Automatisierung und Konsolidierung.

## Positive Befunde

### 1. Governance ist sichtbar und ernst gemeint

Der PR-Template- und Instructions-Layer macht viele repo-spezifische Qualitaetsregeln explizit:

- Spec-First-Disziplin
- Pflicht zu `docs/agent-runs/`
- klare Trennung von `docs/spec/`, `docs/decisions/`, `docs/runbooks/`
- harte Regeln fuer UI-Reuse und browserbasierte UI-Abnahme

Das ist deutlich reifer als ein Repo ohne produktive Governance-Sprache.

### 2. `.github/ISSUE_TEMPLATE/config.yml` deaktiviert leere Blank-Issues

Das reduziert unscharfe, unstrukturierte Issue-Eingaenge und ist fuer ein governance-starkes Repo sinnvoll.

### 3. CI ist restriktiv in Permissions

`contents: read` ist als Baseline gut und vermeidet uebermaessige Workflow-Rechte.

## Kritische Findings

### G1. CI erzwingt die wichtigsten Projektregeln nicht

Prioritaet: P1

`/.github/workflows/ci.yml` fuehrt aktuell nur aus:

- Dependency-Installation
- Ruff Check
- Python Compile Check

Nicht enthalten sind mindestens:

- pytest-Ausfuehrung
- Governance-nahe Checks fuer relevante Spec-Aenderungen
- Sicherungschecks fuer `.github`- oder sensitive Runtime-Dateien

Wirkung:

- das Repo verlangt viel Disziplin, vertraut aber zu stark auf manuelle Sorgfalt
- Architektur- oder Security-Regressionen koennen leichter unbemerkt mergebar bleiben

### G2. Harte Test-Secrets und konkrete DB-Struktur in CI-Datei

Prioritaet: P1

In `/.github/workflows/ci.yml` stehen Test-Secrets und eine konkrete Datenbank-URL hart in der Workflow-Datei.

Das ist kein unmittelbarer Produktionsvorfall, aber ein schwaches Sicherheits- und Operationsmuster fuer ein spaeter sensitiveres System.

### G3. Wichtige Sicherheits- und Verantwortungsartefakte fehlen

Prioritaet: P2

Fehlend im sichtbaren Scope:

- `.github/SECURITY.md`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`

Folgen:

- unklare Schwachstellenmeldewege
- keine formalisierte Review-Verantwortung fuer zentrale Governance-/Security-Dateien
- keine Standardautomatisierung fuer Dependency-Wartung

### G4. Governance-Regeln sind teilweise dupliziert

Prioritaet: P2

Sowohl `.github/copilot-instructions.md` als auch `.github/instructions/repo.instructions.md` transportieren grosse Teile von Regeln, die bereits in Root- bzw. Scoped-`AGENTS.md` und `docs/spec/` verankert sind.

Problem:

- mehrere halbauthoritative Einstiegsebenen
- hoeheres Risiko fuer inkrementelle Drift zwischen denselben Regeln in verschiedenen Dateien

Das widerspricht der eigenen Repo-Richtung, `.github` eher als Zeiger- und Durchsetzungslayer statt als parallele Normquelle zu halten.

### G5. Language-/Audience-Konsistenz ist uneinheitlich

Prioritaet: P3

Es gibt eine Mischlage aus:

- deutschsprachigen PR- und Issue-Templates
- englischsprachigen Instructions
- englischsprachigen CI-Kommentaren

Das ist nicht zwingend falsch, aber fuer externe oder gemischte Mitwirkende unruhig. Fuer ein intern gefuehrtes Projekt kann es funktionieren, solange die Zielgruppe bewusst so gewaehlt ist.

## Skills- und Instructions-Bewertung

### 1. Instructions-Layer ist stark, aber schwergewichtig

Die Instructions sind detailliert und repo-spezifisch nuetzlich. Gleichzeitig tragen sie eine hohe Last an Regeln, die ohne technische Durchsetzung bei laengerer Laufzeit eher zu Ermuedung als zu Verbindlichkeit fuehren koennen.

Empfehlung:

- `.github` knapper als Eintrittspunkt formulieren
- auf kanonische `AGENTS.md`- und `docs/spec/`-Quellen verweisen
- technische Erzwingung fuer zentrale Regeln ausbauen

### 2. Skill-Layer ist fuer diesen Repo-Scope nicht das Hauptproblem

Die verfuegbaren Skills wirken nicht schaedlich und sind im Auditkontext eher randstaendig. Der Hauptbefund betrifft nicht Skill-Qualitaet, sondern Repo-Governance versus CI-Durchsetzung.

## Priorisierte Empfehlungen

### Sofort

1. CI um pytest erweitern.
2. fuer zentrale Aenderungspfade wenigstens minimale Governance-Checks einfuehren.
3. Test-Secrets und konkrete Strukturangaben in Workflows bereinigen.

### Kurzfristig

4. `.github/SECURITY.md`, `.github/CODEOWNERS` und `.github/dependabot.yml` ergaenzen.
5. `.github`-Rulesets auf Verweise plus technische Durchsetzung reduzieren, statt parallele Regeltexte wachsen zu lassen.

### Mittelfristig

6. entscheiden, ob Contributor-Facing Templates bewusst deutsch bleiben oder bilingual werden sollen.
7. PR-Template-Regeln, die wirklich verbindlich sein sollen, in Checks ueberfuehren.

## Audit-Fazit

PROMAT hat fuer ein kleines bis mittleres Spezialrepo ueberdurchschnittlich starke schriftliche Governance. Das Problem ist nicht mangelnde Regelklarheit, sondern die fehlende technische Rueckendeckung. Solange CI weder Tests noch zentrale Governance-Annahmen erzwingt und zugleich sicherheitsrelevante Repo-Artefakte fehlen, bleibt der `.github`-Bereich eher ein gut gemeinter Regelraum als ein belastbarer Schutzrahmen.