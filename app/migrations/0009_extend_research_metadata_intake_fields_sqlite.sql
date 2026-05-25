-- 0009_extend_research_metadata_intake_fields_sqlite.sql
-- SQLite migration: add secure intake metadata to research_people.
-- SQLite already permits storing REAL values in the existing duration_months column without a table rebuild.

BEGIN;

ALTER TABLE research_people ADD COLUMN research_consent_signed TEXT NULL;
ALTER TABLE research_people ADD COLUMN teaching_consent_signed TEXT NULL;
ALTER TABLE research_people ADD COLUMN consent_date DATE NULL;
ALTER TABLE research_people ADD COLUMN consent_file TEXT NULL;
ALTER TABLE research_people ADD COLUMN questionnaire_file TEXT NULL;
ALTER TABLE research_people ADD COLUMN secure_notes TEXT NULL;

COMMIT;