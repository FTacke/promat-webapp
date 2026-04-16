# Speaker Card Native Standard Variety Badge

Datum: 2026-04-16

## Ziel

Die Native-Speaker-Card so nachziehen, dass die Zeile `Standardvarietät` denselben lokalisierten Badge-Typ wie die übrigen produktiven Research-Oberflächen verwendet, statt `Spanien`/`Spain` als Fließtext zu zeigen.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/research-access.md`
- `app/templates/partials/_research_speaker_card.html`
- `app/src/app/research_views.py`
- `app/src/app/routes/public.py`
- `app/tests/test_research_sessions.py`

## Geaenderte Bereiche

- Speaker-Card-Builder fuer Native-`Standardvarietät` als `native-detail`-Badge
- Sample-Speaker-Card-Daten fuer denselben Badge-Pfad in `de` und `en`
- fokussierte Research-Sessions-Regression fuer Badge-Markup und Payload
- aktive Speaker-Card-Spec in `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Die Native-Speaker-Card nutzt fuer `Standardvarietät` denselben vorhandenen `pm-research-meta-badge--native-detail`-Pfad wie die anderen konsolidierten Native-Referenzdarstellungen.
- Die Meta-Zeile behaelt ihr Label `Standardvarietät`/`Standard variety`, aber der sichtbare Wert wird als Badge und nicht als normaler Metatext ausgegeben.
- Der bestehende kanonische lokalisierte Native-Referenzwert bleibt die Datenquelle, damit `Spanien` und `Spain` ohne Sonderlogik konsistent aus derselben Builder-Regel kommen.

## Abweichungen

- Keine Abweichung von der aktiven Spec; die Speaker-Card-Regel wurde in `docs/spec/research-access.md` konkretisiert.

## Verifikation

- `get_errors` auf den geaenderten Python-, Test- und Spec-Dateien: keine Fehler
- `Run research sessions tests`: `150 passed`
- Live-HTML gegen den laufenden Dev-Server:
  - `http://127.0.0.1:8000/de/sample`: `Standardvarietät` rendert `Spanien` als `pm-research-meta-badge--native-detail`
  - `http://127.0.0.1:8000/en/sample`: `Standard variety` rendert `Spain` als `pm-research-meta-badge--native-detail`

## Offene Punkte

- Kein weiterer in-scope Punkt offen.