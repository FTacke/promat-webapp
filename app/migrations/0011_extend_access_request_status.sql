-- 0011_extend_access_request_status.sql
-- PostgreSQL migration: allow the notification states the application writes.
-- 0008 created ck_access_requests_status with ('submitted', 'reviewed', 'resolved'), but the notification service
-- also writes 'notified' and 'notification_failed'. Idempotent: drops and re-creates the constraint.

BEGIN;

ALTER TABLE access_requests DROP CONSTRAINT IF EXISTS ck_access_requests_status;
ALTER TABLE access_requests
  ADD CONSTRAINT ck_access_requests_status
  CHECK (status IN ('submitted', 'notified', 'notification_failed', 'reviewed', 'resolved'));

COMMIT;
