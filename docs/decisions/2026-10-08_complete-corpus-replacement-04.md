# ADR: Vollständiger Korpusersatz statt inkrementellem Upsert

Status: accepted

Datum: 2026-10-08

## Kontext

Die Beta-Phase hinterließ für Englisch, Französisch und Spanisch unvollständige Bestände in Produktion (zum Beispiel Runtime-Ordner ohne DB-Zeilen, ein Metadaten-Ordner ohne Audio). Ein normaler Publish ergänzt und aktualisiert nur; er löscht nie. Ein reiner `--apply-db-upsert` lässt abgelöste Datensätze stehen. Ein vollständiger, finaler Batch (Complete-Batch) muss aber alles bisher Veröffentlichte eines Korpus ablösen können, ohne dass alte und neue Stände vermischt werden.

## Entscheidung

Der vollständige Korpusersatz ist der einzige ausdrückliche Löschmechanismus und besteht aus drei aufeinander abgestimmten Teilen (Details in `docs/spec/platform-data-files.md`, „Complete corpus replacement“):

- das Upload-Paket erklärt `replace_corpora` im Manifest (`build_prod_upload_package.py --replace-corpus`), trägt einen Payload, der jede gepackte Session abdeckt, und enthält kein `config/`;
- der Publish verlangt dieselbe Liste per `--replace-corpus` und entfernt den Korpus nur im gestageten Release; `current` bleibt als Rollback;
- die DB-Reconciliation (`apply_prod_db_payload.py --replace-language`) löscht nur Personen, Sessions, Expositionen und Workbench-Verweise der genannten Sprachen, die der Payload nicht enthält, und validiert vor dem Commit in derselben Transaktion.

Kataloge, kuratierte Sets, Nutzerkonten und andere Korpora gehören nicht zum Ersatz. `corpus_inventory.py` belegt per Inhaltshash, dass Produktion genau das geprüfte Release trägt.

## Auswirkungen

- Alte Beta-Daten lassen sich kontrolliert und reversibel (vorheriges Release, temporäre DB-Sicherung) ablösen; ein Fehler in der DB-Prüfung rollt zurück, bevor `current` umgeschaltet wird.
- Stabile Session-IDs bleiben erhalten, damit Workbench-Verweise und Sets gültig bleiben.
- Das reguläre Backup überschreibt nie; ersetzte Archiveinheiten erfordern eine bewusste Operator-Aktion (Einheit samt Quittungen auf dem Backup-Laufwerk entfernen, danach `backup-copy` und `backup-verify`), siehe `docs/runbooks/archive-preservation.md`.
- Der Mechanismus ist bewusst eng; ein Ersatz ohne passendes Manifest, ohne Payload oder ohne `--apply-db-upsert` wird abgelehnt.

## Alternativen

- Reines Upsert plus manuelles SQL: unkontrolliert, nicht testbar.
- Neue Parallelpipeline für Migrationen: unnötig, die bestehenden Werkzeuge reichen.
- Globales Löschen vor dem Publish: würde Produktion bei einem Fehler leer lassen.

## Referenzen

- `docs/agent-runs/2026-10-08_corpora-replace-en-fr-es.md`
- `docs/spec/platform-data-files.md`, `docs/runbooks/research-prod-upload-and-publish.md`
