# 2026-10-10 – Export der aktiven kuratierten Spanisch-Sets

Nicht normativ. Arbeitsjournal.

## Auftrag

Aktive kuratierte Spanisch-Sets (Phänomene) inklusive Item-IDs, Wort-/Satzzuordnung und Beschreibungen exportieren.

## Vorgehen

- Die Sets liegen nur in der Produktions-DB (`research_sets`, `visibility='curated'`, `lifecycle='saved'`, `corpus_language='spanish'`); lokal existiert nur das Seed-Testset.
- Lesender Zugriff (ein SELECT, keine Schreiboperation) auf `promat-db-prod`; archivierte Sets sind ausgeschlossen.
- Konten-IDs (`created_by_user_id`, `updated_by_user_id`) sind nicht exportiert.
- Ergebnis: `docs/agent-runs/spanish-curated-sets.zip` mit `spanish-curated-sets.json` und `spanish-curated-sets.md`. Das Zip ist bewusst nicht committet.
- Export-Skripte (git-ignoriert): `tmp/sets-export/export_curated_sets.sql`, `tmp/sets-export/build_zip.py`.

## Ergebnis

9 aktive Sets, 232 Items (Wörter und Sätze), alle mit Beschreibung.
