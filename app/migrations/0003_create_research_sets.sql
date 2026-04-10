-- 0003_create_research_sets.sql
-- PostgreSQL migration: create owner-bound research set tables for draft and saved sets

BEGIN;

CREATE TABLE IF NOT EXISTS research_sets (
  set_id TEXT PRIMARY KEY,
  owner_user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  corpus_language TEXT NOT NULL,
  label TEXT NULL,
  state TEXT NOT NULL,
  source_preset_id TEXT NULL,
  preferred_task TEXT NULL,
  comparison_view_task TEXT NOT NULL DEFAULT 'all',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  last_accessed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  expires_at TIMESTAMP WITH TIME ZONE NULL,
  CONSTRAINT ck_research_sets_state CHECK (state IN ('draft', 'saved')),
  CONSTRAINT ck_research_sets_preferred_task CHECK (preferred_task IS NULL OR preferred_task IN ('wordlist', 'text')),
  CONSTRAINT ck_research_sets_comparison_view_task CHECK (comparison_view_task IN ('all', 'wordlist', 'text')),
  CONSTRAINT ck_research_sets_saved_label CHECK (
    state = 'draft' OR (label IS NOT NULL AND length(btrim(label)) > 0)
  )
);

CREATE INDEX IF NOT EXISTS idx_research_sets_owner_user_id ON research_sets (owner_user_id);
CREATE INDEX IF NOT EXISTS idx_research_sets_owner_state ON research_sets (owner_user_id, state);
CREATE INDEX IF NOT EXISTS idx_research_sets_language ON research_sets (corpus_language);
CREATE INDEX IF NOT EXISTS idx_research_sets_expires_at ON research_sets (expires_at);
CREATE INDEX IF NOT EXISTS idx_research_sets_last_accessed_at ON research_sets (last_accessed_at);

CREATE TABLE IF NOT EXISTS research_set_items (
  set_id TEXT NOT NULL REFERENCES research_sets(set_id) ON DELETE CASCADE,
  task TEXT NOT NULL,
  item_id TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  segment_id TEXT NULL,
  note TEXT NULL,
  PRIMARY KEY (set_id, task, item_id),
  CONSTRAINT ck_research_set_items_task CHECK (task IN ('wordlist', 'text')),
  CONSTRAINT ck_research_set_items_sort_order CHECK (sort_order >= 1)
);

CREATE INDEX IF NOT EXISTS idx_research_set_items_set_sort ON research_set_items (set_id, sort_order);

CREATE TABLE IF NOT EXISTS research_set_sessions (
  set_id TEXT NOT NULL REFERENCES research_sets(set_id) ON DELETE CASCADE,
  session_id TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  PRIMARY KEY (set_id, session_id),
  CONSTRAINT ck_research_set_sessions_sort_order CHECK (sort_order >= 1)
);

CREATE INDEX IF NOT EXISTS idx_research_set_sessions_set_sort ON research_set_sessions (set_id, sort_order);

COMMIT;