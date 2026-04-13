-- 0005_split_research_set_workbench_state.sql
-- PostgreSQL migration: split workbench state from the canonical research set core

BEGIN;

CREATE TABLE IF NOT EXISTS research_set_workbench_state (
  set_id TEXT PRIMARY KEY REFERENCES research_sets(set_id) ON DELETE CASCADE,
  preferred_task TEXT NULL,
  comparison_view_task TEXT NOT NULL DEFAULT 'all',
  CONSTRAINT ck_research_set_workbench_state_preferred_task CHECK (
    preferred_task IS NULL OR preferred_task IN ('wordlist', 'text')
  ),
  CONSTRAINT ck_research_set_workbench_state_comparison_view_task CHECK (
    comparison_view_task IN ('all', 'wordlist', 'text')
  )
);

CREATE TABLE IF NOT EXISTS research_set_workbench_sessions (
  set_id TEXT NOT NULL REFERENCES research_set_workbench_state(set_id) ON DELETE CASCADE,
  session_id TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  PRIMARY KEY (set_id, session_id),
  CONSTRAINT ck_research_set_workbench_sessions_sort_order CHECK (sort_order >= 1)
);

CREATE INDEX IF NOT EXISTS idx_research_set_workbench_sessions_set_sort
  ON research_set_workbench_sessions (set_id, sort_order);

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'research_sets'
      AND column_name = 'preferred_task'
  ) THEN
    INSERT INTO research_set_workbench_state (set_id, preferred_task, comparison_view_task)
    SELECT set_id, preferred_task, comparison_view_task
    FROM research_sets
    ON CONFLICT (set_id) DO UPDATE SET
      preferred_task = EXCLUDED.preferred_task,
      comparison_view_task = EXCLUDED.comparison_view_task;
  ELSE
    INSERT INTO research_set_workbench_state (set_id, preferred_task, comparison_view_task)
    SELECT set_id, NULL, 'all'
    FROM research_sets
    ON CONFLICT (set_id) DO NOTHING;
  END IF;
END $$;

DO $$
BEGIN
  IF to_regclass('public.research_set_sessions') IS NOT NULL THEN
    INSERT INTO research_set_workbench_sessions (set_id, session_id, sort_order)
    SELECT set_id, session_id, sort_order
    FROM research_set_sessions
    ON CONFLICT (set_id, session_id) DO NOTHING;
  END IF;
END $$;

ALTER TABLE research_sets DROP CONSTRAINT IF EXISTS ck_research_sets_preferred_task;
ALTER TABLE research_sets DROP CONSTRAINT IF EXISTS ck_research_sets_comparison_view_task;
ALTER TABLE research_sets DROP COLUMN IF EXISTS preferred_task;
ALTER TABLE research_sets DROP COLUMN IF EXISTS comparison_view_task;

DROP INDEX IF EXISTS idx_research_set_sessions_set_sort;
DROP TABLE IF EXISTS research_set_sessions;

COMMIT;
