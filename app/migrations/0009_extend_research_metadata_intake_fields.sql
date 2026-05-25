-- 0009_extend_research_metadata_intake_fields.sql
-- PostgreSQL migration: add secure intake metadata to research_people and allow decimal exposure durations.

BEGIN;

ALTER TABLE research_people ADD COLUMN IF NOT EXISTS research_consent_signed TEXT NULL;
ALTER TABLE research_people ADD COLUMN IF NOT EXISTS teaching_consent_signed TEXT NULL;
ALTER TABLE research_people ADD COLUMN IF NOT EXISTS consent_date DATE NULL;
ALTER TABLE research_people ADD COLUMN IF NOT EXISTS consent_file TEXT NULL;
ALTER TABLE research_people ADD COLUMN IF NOT EXISTS questionnaire_file TEXT NULL;
ALTER TABLE research_people ADD COLUMN IF NOT EXISTS secure_notes TEXT NULL;

ALTER TABLE research_people DROP CONSTRAINT IF EXISTS ck_research_people_research_consent_signed;
ALTER TABLE research_people ADD CONSTRAINT ck_research_people_research_consent_signed
  CHECK (research_consent_signed IS NULL OR research_consent_signed IN ('yes', 'no', 'unknown'));

ALTER TABLE research_people DROP CONSTRAINT IF EXISTS ck_research_people_teaching_consent_signed;
ALTER TABLE research_people ADD CONSTRAINT ck_research_people_teaching_consent_signed
  CHECK (teaching_consent_signed IS NULL OR teaching_consent_signed IN ('yes', 'no', 'unknown'));

ALTER TABLE research_session_exposures
  ALTER COLUMN duration_months TYPE DOUBLE PRECISION
  USING duration_months::double precision;

COMMIT;