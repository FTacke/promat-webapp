-- 0010_add_account_kind.sql
-- Additive migration: introduce account_kind (personal | group) and responsible_admin_user_id.
-- All existing rows automatically receive account_kind = 'personal' via DEFAULT.
-- No existing data is modified. No columns are dropped or renamed.
-- Rollback: see comment at end of file.

BEGIN;

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS account_kind TEXT NOT NULL DEFAULT 'personal'
    CHECK (account_kind IN ('personal', 'group'));

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS responsible_admin_user_id TEXT
    REFERENCES users(user_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_users_account_kind
  ON users (account_kind);

CREATE INDEX IF NOT EXISTS idx_users_responsible_admin
  ON users (responsible_admin_user_id)
  WHERE responsible_admin_user_id IS NOT NULL;

COMMIT;

-- Rollback (run manually if needed, never automatically):
-- BEGIN;
-- DROP INDEX IF EXISTS idx_users_responsible_admin;
-- DROP INDEX IF EXISTS idx_users_account_kind;
-- ALTER TABLE users DROP COLUMN IF EXISTS responsible_admin_user_id;
-- ALTER TABLE users DROP COLUMN IF EXISTS account_kind;
-- COMMIT;
