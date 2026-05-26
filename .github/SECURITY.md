# Security Policy

PROMAT verarbeitet potenziell geschützte Forschungsdaten und personenbezogene Metadaten. Schwachstellen bitte nicht öffentlich über GitHub Issues oder Pull Requests melden.

## Pre-Publication Status

This repository is not configured as a public vulnerability intake channel yet. Until a concrete public security contact is named, vulnerability reports must use the private maintainer or operator channel already used for deployment coordination.

Do not enable required public security reporting, public issue triage for vulnerabilities, or required CODEOWNERS security review enforcement from this file alone before that contact path is explicitly configured.

## Supported Versions

| Version / branch | Supported |
| --- | --- |
| `main` | Yes |
| older branches | No |

## Reporting a Vulnerability

Please do not open a public GitHub issue for vulnerabilities.

When reporting a security issue, include only the minimum technical detail required to reproduce the problem safely:

- affected surface, route, command, or workflow
- risk type and expected impact
- reproduction steps without sensitive data
- current behavior and expected secure behavior
- whether authentication, role boundaries, data export, or runtime path handling is involved

Do not include:

- real audio files
- runtime artifacts from `data/`, `public/`, or `secure/`
- real names, email addresses, or other personenbezogene Daten
- credentials, tokens, or secrets
- screenshots or logs containing productive data

## Handling Artifacts Safely

- Do not upload productive data to GitHub issues, pull requests, CI logs, screenshots, or other artifacts.
- Use dummy values and minimal synthetic examples when demonstrating a problem.
- If a bug requires a screenshot, redact all personally identifiable or research-sensitive content first.

## Response Expectations

PROMAT will triage reported vulnerabilities, request clarification when needed, and coordinate remediation before any public disclosure.
