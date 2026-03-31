-- 0001_create_auth_schema_sqlite.sql
-- SQLite-specific migration to create users, refresh_tokens, reset_tokens.

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY, -- store UUID as text
  username TEXT NOT NULL UNIQUE,
  email TEXT UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user',
  is_active INTEGER NOT NULL DEFAULT 1,
  must_reset_password INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  access_expires_at TIMESTAMP NULL,
  valid_from TIMESTAMP NULL,
  last_login_at TIMESTAMP NULL,
  display_name TEXT NULL,
  login_failed_count INTEGER NOT NULL DEFAULT 0,
  locked_until TIMESTAMP NULL,
  deleted_at TIMESTAMP NULL,
  deletion_requested_at TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users (lower(username));
CREATE INDEX IF NOT EXISTS idx_users_email ON users (lower(email));
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users (is_active);
CREATE INDEX IF NOT EXISTS idx_users_access_expires_at ON users (access_expires_at);
CREATE INDEX IF NOT EXISTS idx_users_valid_from ON users (valid_from);
CREATE INDEX IF NOT EXISTS idx_users_locked_until ON users (locked_until);
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users (deleted_at);

CREATE TABLE IF NOT EXISTS refresh_tokens (
  token_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  token_hash TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  last_used_at TIMESTAMP NULL,
  revoked_at TIMESTAMP NULL,
  user_agent TEXT NULL,
  ip_address TEXT NULL,
  replaced_by TEXT NULL,
  FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_refresh_user_id ON refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_token_hash ON refresh_tokens (token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_expires_at ON refresh_tokens (expires_at);
CREATE INDEX IF NOT EXISTS idx_refresh_revoked_at ON refresh_tokens (revoked_at);

CREATE TABLE IF NOT EXISTS reset_tokens (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  token_hash TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  used_at TIMESTAMP NULL,
  FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_reset_user_id ON reset_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_reset_token_hash ON reset_tokens (token_hash);
CREATE INDEX IF NOT EXISTS idx_reset_expires_at ON reset_tokens (expires_at);

COMMIT;
