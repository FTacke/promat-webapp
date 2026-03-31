-- 0002_create_analytics_tables.sql
-- Analytics table for anonymous usage statistics
-- VARIANTE 3a: Nur aggregierte Zähler, KEINE Suchinhalte!
-- IMPORTANT: No foreign keys to users table (privacy by design)

BEGIN;

-- Daily aggregated metrics (nur Zähler, keine Inhalte)
CREATE TABLE IF NOT EXISTS analytics_daily (
  date DATE PRIMARY KEY,
  visitors INTEGER NOT NULL DEFAULT 0,
  mobile INTEGER NOT NULL DEFAULT 0,
  desktop INTEGER NOT NULL DEFAULT 0,
  searches INTEGER NOT NULL DEFAULT 0,
  audio_plays INTEGER NOT NULL DEFAULT 0,
  errors INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Index for time-range queries (last 30 days etc.)
CREATE INDEX IF NOT EXISTS idx_analytics_daily_date ON analytics_daily (date DESC);

-- HINWEIS: Keine analytics_queries Tabelle!
-- Variante 3a speichert keine Suchinhalte/Query-Texte.

COMMIT;
