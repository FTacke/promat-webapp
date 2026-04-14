-- 0007_create_research_metadata_tables.sql
-- PostgreSQL migration: create imported research person/session/exposure metadata tables.

BEGIN;

CREATE TABLE IF NOT EXISTS research_people (
  person_id TEXT PRIMARY KEY,
  speaker_type TEXT NOT NULL,
  l1 TEXT NULL,
  l1_additional TEXT NULL,
  mother_l1 TEXT NULL,
  father_l1 TEXT NULL,
  additional_languages TEXT NULL,
  gender TEXT NULL,
  birth_year INTEGER NULL,
  current_region TEXT NULL,
  childhood_region TEXT NULL,
  origin_country TEXT NULL,
  origin_region TEXT NULL,
  needs_review BOOLEAN NOT NULL DEFAULT FALSE,
  person_notes TEXT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  CONSTRAINT ck_research_people_speaker_type CHECK (speaker_type IN ('learner', 'native_speaker'))
);

CREATE TABLE IF NOT EXISTS research_sessions (
  session_id TEXT PRIMARY KEY,
  person_id TEXT NOT NULL REFERENCES research_people(person_id) ON DELETE CASCADE,
  session_ref TEXT NOT NULL,
  corpus_language TEXT NOT NULL,
  target_language TEXT NOT NULL,
  standard_variety TEXT NULL,
  level_self TEXT NULL,
  level_code TEXT NULL,
  recording_year INTEGER NOT NULL,
  recording_date DATE NULL,
  recorded_by TEXT NULL,
  context TEXT NULL,
  stays_in_target_country BOOLEAN NULL,
  needs_review BOOLEAN NOT NULL DEFAULT FALSE,
  session_notes TEXT NULL,
  documented_tasks TEXT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  CONSTRAINT ck_research_sessions_target_language CHECK (target_language IN ('es', 'fr', 'en', 'de')),
  CONSTRAINT ck_research_sessions_context CHECK (context IS NULL OR context IN ('baseline', 'follow_up')),
  CONSTRAINT uq_research_sessions_person_session_ref UNIQUE (person_id, session_ref)
);

CREATE INDEX IF NOT EXISTS idx_research_sessions_person_id ON research_sessions (person_id);
CREATE INDEX IF NOT EXISTS idx_research_sessions_corpus_language ON research_sessions (corpus_language);
CREATE INDEX IF NOT EXISTS idx_research_sessions_target_language ON research_sessions (target_language);

CREATE TABLE IF NOT EXISTS research_session_exposures (
  exposure_id BIGSERIAL PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES research_sessions(session_id) ON DELETE CASCADE ON UPDATE CASCADE,
  sort_order INTEGER NOT NULL,
  country TEXT NULL,
  duration_months INTEGER NULL,
  exposure_type TEXT NULL,
  exposure_notes TEXT NULL,
  needs_review BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  CONSTRAINT ck_research_session_exposures_sort_order CHECK (sort_order >= 1),
  CONSTRAINT uq_research_session_exposures_session_sort UNIQUE (session_id, sort_order)
);

CREATE INDEX IF NOT EXISTS idx_research_session_exposures_session_id ON research_session_exposures (session_id, sort_order);

COMMIT;