-- 0006_finalize_protected_area.sql
-- Finalize protected-area schema: user names, creator audit, and privacy-safe analytics dimensions.

BEGIN;

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS first_name TEXT NULL;

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS last_name TEXT NULL;

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS created_by_user_id TEXT NULL REFERENCES users(user_id);

UPDATE users
SET role = 'user'
WHERE lower(role) = 'editor';

ALTER TABLE analytics_daily
  ADD COLUMN IF NOT EXISTS page_views INTEGER NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS analytics_language_area_daily (
  date DATE NOT NULL,
  section TEXT NOT NULL,
  corpus_language TEXT NOT NULL,
  unique_visitors INTEGER NOT NULL DEFAULT 0,
  page_views INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  PRIMARY KEY (date, section, corpus_language)
);

CREATE INDEX IF NOT EXISTS idx_analytics_language_area_daily_date
  ON analytics_language_area_daily (date DESC);

CREATE INDEX IF NOT EXISTS idx_analytics_language_area_daily_section_language
  ON analytics_language_area_daily (section, corpus_language);

COMMIT;