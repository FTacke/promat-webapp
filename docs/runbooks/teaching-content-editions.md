# Runbook: Teaching-Inhaltsfassung aktivieren (z. B. Spanisch, Französisch)

## Zugehörige Spezifikation

- `docs/spec/platform-data-files.md` (Routing rules, *Teaching content editions*; *URL identity*; *Citations*)
- ADR `docs/decisions/2026-10-26_teaching-content-editions-06.md`

## Zweck

Eine zusätzliche Inhaltssprache einer Unterrichtssprache (Spanisch: `es`, Französisch: `fr`) Seite für Seite veröffentlichen, ohne die globale UI-Sprache (`de`/`en`) zu ändern.

## Voraussetzungen

- Die Unterrichtssprache deklariert den Code in `content/teaching/{teaching_language}/teaching.yaml` unter `content_editions` (Spanisch: `es` ist deklariert; Französisch: `fr` ergänzen).
- Fachlich freigegebener Text der Themenseite in der Zielsprache (kein maschineller Platzhalter).
- Vor der ersten Veröffentlichung einer Sprache einmalig im Code ergänzen und testen: Beschriftungen der Inhaltsblöcke in dieser Sprache (Sprecherrollen, Wortfolge-Chip, Auflösung, Vertiefung) und Zitationskonventionen (`publication._QUOTES`, `_EDITOR_LABELS`). Ohne diese Ergänzung erscheinen Block-Labels in der UI-Sprache und die Zitation in englischer Form.

## Schritte

1. Themendatei anlegen: `content/teaching/{teaching_language}/{topic_slug}/{code}.yaml`, gleicher Slug wie die DE/EN-Seite. `resource_id` und `metadata.creators` exakt wie in `de.yaml` übernehmen; `metadata.created`/`updated` setzen; Blocktypen, Audio- und Bildreferenzen wie in der Ausgangsseite (Medien werden geteilt, keine Kopien).
2. Solange der Text nicht fachlich abgenommen ist, `status: draft` setzen; die Seite ist dann weder erreichbar noch verlinkt.
3. Für die Übersicht `content/teaching/{teaching_language}/hubs/{code}.yaml` anlegen (Titel, Einleitung, Gruppen); dort nur Themen aufführen, die eine `{code}.yaml` haben. Die Übersicht ist erst sichtbar, wenn mindestens ein gelistetes Thema veröffentlicht ist.
4. Interne Links im Text auf die Fassung derselben Sprache setzen (`/de/teaching/spanish/es/{slug}`), sofern diese veröffentlicht ist, sonst auf die deutsche Seite.
5. Prüfen: `python scripts/validate_teaching_content.py`, `python scripts/teaching_audio_slots.py --check`, `cd app && python -m pytest tests/test_teaching_content_editions.py tests/test_teaching_spanish_topics.py`.
6. Freigeben: `status: draft` entfernen. Lokal prüfen (eigene Instanz, siehe `docs/runbooks/local-dev-start.md`): DE- und EN-Seite zeigen oben rechts `En español`; die Fassung zeigt `Auf Deutsch`/`In English` je nach Herkunft; DE/EN-Schalter auf der Fassung behält den Inhalt; Hell/Dunkel, Desktop/Mobil.
7. Commit, Push, Deploy nach `docs/runbooks/deploy-and-rollback.md`; Run-Log unter `docs/agent-runs/`.

## Verifikation

- `/{ui_lang}/teaching/{teaching_language}/{code}/{slug}` antwortet 200 unter `de` und `en`, mit `<article lang="{code}">` und demselben Canonical (Präfix der Standard-UI-Edition).
- `hreflang` der DE-, EN- und der neuen Fassung nennt `de`, `en`, `{code}` gegenseitig; nicht übersetzte Seiten behalten nur `de`/`en`.
- Zitation: Titel der Fassung, unveränderte Autorenschaft, URL der Fassung.

## Risiken und Rückbau

- Ein Slug oder Alias gleich dem Sprachcode kollidiert mit der Übersichtsroute (Validator meldet es).
- Rückbau einer Seite: `status: draft` setzen (404, Links und `hreflang` verschwinden sofort); Rückbau einer Sprache: Code aus `content_editions` entfernen (der Validator verlangt dann das Entfernen der Sprachdateien).
