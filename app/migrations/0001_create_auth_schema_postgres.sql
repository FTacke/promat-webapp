-- 0001_create_auth_schema_postgres.sql
-- Postgres migration: create users, refresh_tokens, reset_tokens tables with recommended indexes and constraints

-- NOTE: Run this in a transaction (e.g., via alembic or psql) and verify in staging first.
-- NOTE: Uses TEXT for IDs (UUIDs stored as strings) for SQLAlchemy compatibility.

BEGIN;

CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  must_reset_password BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  access_expires_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
  valid_from TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
  last_login_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
  display_name TEXT NULL DEFAULT NULL,
  login_failed_count INTEGER NOT NULL DEFAULT 0,
  locked_until TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
  deleted_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
  deletion_requested_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_users_username ON users (lower(username));
CREATE INDEX IF NOT EXISTS idx_users_email ON users (lower(email));
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users (is_active);
CREATE INDEX IF NOT EXISTS idx_users_access_expires_at ON users (access_expires_at);
CREATE INDEX IF NOT EXISTS idx_users_valid_from ON users (valid_from);
CREATE INDEX IF NOT EXISTS idx_users_locked_until ON users (locked_until);
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users (deleted_at);

-- Refresh tokens table
CREATE TABLE IF NOT EXISTS refresh_tokens (
  token_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  last_used_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
  revoked_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
  user_agent TEXT NULL DEFAULT NULL,
  ip_address TEXT NULL DEFAULT NULL,
  replaced_by TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_refresh_user_id ON refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_token_hash ON refresh_tokens (token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_expires_at ON refresh_tokens (expires_at);
CREATE INDEX IF NOT EXISTS idx_refresh_revoked_at ON refresh_tokens (revoked_at);

-- Reset tokens
CREATE TABLE IF NOT EXISTS reset_tokens (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  used_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_reset_user_id ON reset_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_reset_token_hash ON reset_tokens (token_hash);
CREATE INDEX IF NOT EXISTS idx_reset_expires_at ON reset_tokens (expires_at);

COMMIT;
