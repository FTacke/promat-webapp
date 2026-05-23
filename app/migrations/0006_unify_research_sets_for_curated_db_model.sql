-- 0006_unify_research_sets_for_curated_db_model.sql
-- PostgreSQL migration: unify private and curated research sets in the DB-backed model

BEGIN;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'research_sets'
      AND column_name = 'state'
  ) AND NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'research_sets'
      AND column_name = 'lifecycle'
  ) THEN
    ALTER TABLE research_sets RENAME COLUMN state TO lifecycle;
  END IF;
END $$;

ALTER TABLE research_sets ALTER COLUMN owner_user_id DROP NOT NULL;

ALTER TABLE research_sets ADD COLUMN IF NOT EXISTS visibility TEXT;
ALTER TABLE research_sets ADD COLUMN IF NOT EXISTS source_curated_set_id TEXT NULL REFERENCES research_sets(set_id) ON DELETE SET NULL;
ALTER TABLE research_sets ADD COLUMN IF NOT EXISTS created_by_user_id TEXT NULL REFERENCES users(user_id) ON DELETE SET NULL;
ALTER TABLE research_sets ADD COLUMN IF NOT EXISTS updated_by_user_id TEXT NULL REFERENCES users(user_id) ON DELETE SET NULL;
ALTER TABLE research_sets ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;
ALTER TABLE research_sets ADD COLUMN IF NOT EXISTS published_at TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE research_sets ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE NULL;

UPDATE research_sets
SET visibility = 'private'
WHERE visibility IS NULL;

UPDATE research_sets
SET created_by_user_id = owner_user_id
WHERE created_by_user_id IS NULL
  AND owner_user_id IS NOT NULL;

UPDATE research_sets
SET updated_by_user_id = owner_user_id
WHERE updated_by_user_id IS NULL
  AND owner_user_id IS NOT NULL;

UPDATE research_sets
SET version = 1
WHERE version IS NULL OR version < 1;

ALTER TABLE research_sets ALTER COLUMN visibility SET NOT NULL;
ALTER TABLE research_sets ALTER COLUMN lifecycle SET NOT NULL;
ALTER TABLE research_sets ALTER COLUMN version SET DEFAULT 1;

ALTER TABLE research_sets DROP CONSTRAINT IF EXISTS ck_research_sets_state;
ALTER TABLE research_sets DROP CONSTRAINT IF EXISTS ck_research_sets_saved_label;

ALTER TABLE research_sets ADD CONSTRAINT ck_research_sets_visibility CHECK (
  visibility IN ('private', 'curated')
);

ALTER TABLE research_sets ADD CONSTRAINT ck_research_sets_lifecycle CHECK (
  lifecycle IN ('draft', 'saved', 'archived')
);

ALTER TABLE research_sets ADD CONSTRAINT ck_research_sets_saved_label CHECK (
  lifecycle = 'draft' OR (label IS NOT NULL AND length(btrim(label)) > 0)
);

ALTER TABLE research_sets ADD CONSTRAINT ck_research_sets_visibility_lifecycle CHECK (
  (visibility = 'private' AND lifecycle IN ('draft', 'saved'))
  OR (visibility = 'curated' AND lifecycle IN ('saved', 'archived'))
);

ALTER TABLE research_sets ADD CONSTRAINT ck_research_sets_owner_scope CHECK (
  (visibility = 'private' AND owner_user_id IS NOT NULL)
  OR (visibility = 'curated' AND owner_user_id IS NULL)
);

ALTER TABLE research_sets ADD CONSTRAINT ck_research_sets_curated_expiry CHECK (
  visibility = 'private' OR expires_at IS NULL
);

ALTER TABLE research_sets ADD CONSTRAINT ck_research_sets_version CHECK (
  version >= 1
);

DROP INDEX IF EXISTS idx_research_sets_owner_state;
CREATE INDEX IF NOT EXISTS idx_research_sets_owner_lifecycle ON research_sets (owner_user_id, lifecycle);
CREATE INDEX IF NOT EXISTS idx_research_sets_language_visibility_lifecycle ON research_sets (corpus_language, visibility, lifecycle);
CREATE INDEX IF NOT EXISTS idx_research_sets_source_curated_set_id ON research_sets (source_curated_set_id);

COMMIT;