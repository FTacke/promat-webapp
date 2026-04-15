-- 0008_create_access_requests.sql
-- PostgreSQL migration: create access request intake table for the public access-request form.

BEGIN;

CREATE TABLE IF NOT EXISTS access_requests (
  id TEXT PRIMARY KEY,
  status TEXT NOT NULL DEFAULT 'submitted',
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  institution TEXT NOT NULL,
  role_or_function TEXT NOT NULL,
  email TEXT NOT NULL,
  purpose TEXT NOT NULL,
  consent_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
  ui_lang TEXT NULL,
  requested_path TEXT NULL,
  user_agent TEXT NULL,
  ip_address TEXT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  CONSTRAINT ck_access_requests_status CHECK (status IN ('submitted', 'reviewed', 'resolved'))
);

CREATE INDEX IF NOT EXISTS idx_access_requests_email ON access_requests (lower(email));
CREATE INDEX IF NOT EXISTS idx_access_requests_status ON access_requests (status);
CREATE INDEX IF NOT EXISTS idx_access_requests_created_at ON access_requests (created_at);

COMMIT;