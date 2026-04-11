-- 0004_extend_research_sets_for_phenomena_editor.sql
-- PostgreSQL migration: add set-level notes for the split phenomena editor workflow

BEGIN;

ALTER TABLE research_sets
  ADD COLUMN IF NOT EXISTS note TEXT NULL;

COMMIT;