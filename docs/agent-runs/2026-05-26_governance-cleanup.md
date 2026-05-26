# Governance Cleanup

## Scope

Umgesetzt wurden nur sichere Governance-Befunde aus `docs/agent-runs/2026-05-26_governance-md3-mobile-audit.md`.

Im Scope waren:

- `.github/SECURITY.md`
- `.github/CODEOWNERS`
- `README.md`
- `.github/workflows/ci.yml`

Nicht im Scope waren Produktcode, UI, CSS/MD3, Mobile-Fixes, Teaching-/Content-Änderungen, Design-System-Migrationen, Prod-Pakete und Serverkontakt.

## Geänderte Dateien

| Datei | Änderung |
|---|---|
| `.github/SECURITY.md` | Der alte Security-Kontakt-Platzhalter wurde entfernt. Die Datei markiert den aktuellen Zustand jetzt bewusst als Pre-Publication-Status ohne öffentlichen Vulnerability-Intake-Kanal. Bis ein echter öffentlicher Kontakt feststeht, sollen Reports über den privaten Maintainer-/Operator-Kanal laufen. |
| `.github/CODEOWNERS` | Die Datei ist jetzt klar als documentation-only Scaffold beschrieben. Required CODEOWNERS Review Enforcement darf daraus nicht aktiviert werden, solange keine echten, unkommentierten Handles oder Teams eingetragen sind. |
| `README.md` | Die Binding-Source-Liste wurde um `docs/spec/research-capabilities.md` ergänzt. Zusätzlich verweist README jetzt auf scoped `AGENTS.md` und das relevante Runtime-Wiring für Architektur-, Routing-, Datenpfad- und Governance-Änderungen. |
| `.github/workflows/ci.yml` | Die CI-Pytest-Suite führt zusätzlich `tests/test_runtime_config.py` und einen fokussierten Security/Governance-Filter aus: `security_headers or csp or access_request or runtime_config or governance`. |

## Governance-Entscheidungen

- Es wurde kein falscher Security-Kontakt erfunden.
- `.github/SECURITY.md` ist weiterhin nutzbar als Sicherheitsleitlinie, aber nicht als öffentlicher Meldekanal.
- `.github/CODEOWNERS` bleibt comment-only, bis reale Owner bekannt sind.
- Die README folgt jetzt der Root-`AGENTS.md`-Binding-Liste enger.
- Keine aktiven Specs wurden geändert, weil keine Produkt- oder Architekturregel geändert wurde.

## CI-Änderungen

CI soll nun zusätzlich explizit prüfen:

- Runtime-Konfiguration und Prod-Verbot von `memory://` über `tests/test_runtime_config.py`
- Access-Request-Validierung und Abuse-Basics über den fokussierten `-k`-Lauf
- CSP-/Security-Header-Basics über den fokussierten `-k`-Lauf
- vorhandene Auth-/Admin-/Rate-Limit-Grundtests über `tests/test_auth_phase1.py`
- vorhandene Research-Smokes über `tests/test_research_sessions.py` und `tests/test_research_phenomena.py`

Bewusst nicht als neue harte Gates ergänzt wurden:

- redaktionelle Fließtext-Assertions
- konkrete Personennamen auf Content-Seiten
- visuelle Pixel-Details
- echte externe Mailzustellung
- vollständige Browser-E2E-Suite bei jedem Push

## Tests

Ausgeführt:

```text
.venv\Scripts\python.exe -m compileall app -q
```

Ergebnis: bestanden.

```text
.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q
```

Ergebnis: 66 passed.

```text
.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -q
```

Ergebnis: 201 passed.

```text
.venv\Scripts\python.exe -m pytest app/tests -q -k "security_headers or csp or access_request or runtime_config or governance"
```

Ergebnis: 16 passed, 458 deselected.

Zusätzlich wegen Workflow-Änderung ausgeführt:

```text
.venv\Scripts\python.exe -m pytest app/tests/test_research_phenomena.py -q
```

Ergebnis: 17 passed. Es gab 17 bekannte Testmodus-Warnungen von Flask-Limiter zur In-Memory-Storage-Nutzung im Testlauf; die Produktionskonfiguration wird durch `test_runtime_config.py` weiter gegen `memory://` abgesichert.

Workflow-YAML wurde geparst mit:

```text
python yaml.safe_load für .github/workflows/*.yml
```

Ergebnis: `ok .github\workflows\ci.yml`.

## Repo-Grenzen

`git status --short -- .github\SECURITY.md .github\CODEOWNERS README.md .github\workflows\ci.yml content content\teaching public\teaching` zeigte nur die vier Governance-/CI-Dateien als geändert. `content/`, `content/teaching/` und `public/teaching/` blieben unangetastet.

Der Workspace war bereits vor diesem Cleanup dirty; diese Änderungen beschränken sich auf die genannten Governance-/CI-Dateien und diesen Abschlussbericht.

## Bewusst Nicht Geändert

- keine Produktcode-Änderungen
- keine UI-Änderungen
- keine CSS-/MD3-Arbeit
- keine Mobile-Fixes
- keine Teaching-/Content-Änderungen
- keine Design-System-Migration
- keine echten externen Mailtests
- kein Prod-Paket
- kein Serverkontakt

## Offene Punkte

- Vor öffentlicher Prod-Freigabe muss ein echter Security-Meldekanal in `.github/SECURITY.md` eingetragen werden.
- Vor Required Reviews müssen echte CODEOWNERS-Handles oder Teams unkommentiert eingetragen werden.
- Die lokale CI-Governance-Guard-Datei bleibt unverändert; sie sollte auf sauberem CI-Checkout laufen. Der aktuelle Workspace enthält unabhängig von diesem Run bereits Root-Debug-/Startdateien, die nicht Teil dieses Cleanups waren.
