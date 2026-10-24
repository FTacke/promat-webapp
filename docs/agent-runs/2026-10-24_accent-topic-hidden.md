# Themenseite „Ein Akzent verändert alles“ vorerst nicht öffentlich

Datum: 2026-10-24

Die Seite ist noch nicht fertig und nicht freigegeben. Sie wurde über den vorgesehenen Mechanismus (`status: draft` in `de.yaml` und `en.yaml`, siehe `docs/spec/platform-data-files.md`, Teaching availability) aus der Öffentlichkeit genommen und zusätzlich aus den beiden Hub-Dateien (`content/teaching/spanish/hubs/{de,en}.yaml`) entfernt: Ein im Hub gelistetes Draft-Thema würde sonst als Platzhalterkarte („pending“) sichtbar bleiben.

Folgen: keine Karte in der Übersicht (Spanisch zeigt „7 Themenseiten“), die Seiten-URLs und die zugehörigen Medien antworten mit 404, die Seite ist kein Sprachwechsel-Äquivalent. Inhalt, Audio-Slots und Medien bleiben unverändert im Repository.

Wieder freigeben: `status: draft` in beiden Editionen entfernen und den Slug wieder in `hubs/{de,en}.yaml` (Gruppe „Aussprachephänomene entdecken“, zuletzt) eintragen; Tests (`UNRELEASED` in `test_teaching_spanish_topics.py`, Zählungen in `test_research_sessions.py`, `TOPICS`/`IMPULSES`, `SPANISH_TOPICS` in `scripts/post_deploy_smoke.py`) wieder um die Seite ergänzen.

Tests: Zählungen 8 → 7, neuer Test `test_unreleased_accent_topic_is_hidden_from_hub_and_not_served`, Deploy-Smoke ohne die Seite; Volltest 1490 passed, 2 skipped; Governance-, Content- und Slot-Checks grün.
