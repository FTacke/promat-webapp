# Auth Account Types – PROMAT Specification

## Overview

PROMAT supports two orthogonal axes of account classification:

- **Role:** `user` | `admin` (unchanged)
- **Account kind:** `personal` | `group`

These axes are independent. A group account always has `role = user`. An admin account always has `account_kind = personal`.

---

## Personal Accounts

Personal accounts are the default. They map one natural person to one PROMAT user account.

- Created administratively via the admin user management UI (`/admin/users` POST).
- **Login:** email address (lowercase-normalized).
- **Invitation:** a 14-day password-setup link is prepared and optionally sent by email.
- **Self-service:** the user can change their own profile data and password at `/auth/account` and `/auth/account/password`.
- **Password reset:** available via the public forgot-password flow (`/auth/password/forgot`).
- Fields: `first_name`, `last_name`, `email` (all required at creation).
- `account_kind = 'personal'` (DB default for all pre-existing accounts).

---

## Group Accounts

Group accounts represent a shared access credential for a seminar group, course, or similar collective. They do not map to a single natural person.

- Created administratively via the admin UI ("Gruppenaccount anlegen" / "Create group account", `POST /admin/groups`).
- **Login:** `username` field (the "login name"), set explicitly by the admin. Not an email address.
- **No email address** (stored as `NULL`).
- **No first name / last name** (stored as `NULL`).
- **No invitation link / setup email:** password is set directly by the admin at creation. No `must_reset_password`.
- **No self-service:** group accounts cannot access `/auth/account` or `/auth/account/password`. Both routes redirect to the research home page.
- **No public password reset:** the forgot-password flow silently ignores group accounts even if a matching email were present.
- **Password changes** are performed exclusively by admins via `POST /admin/groups/<id>/set-password`.
- **Role:** always `user`. Group accounts do not receive research privileges beyond those of a regular `user` account.
- **Responsible admin:** `responsible_admin_user_id` (nullable FK) identifies the admin responsible for the group account. Shown in the admin list under "Erstellt". If the responsible admin is later deactivated or deleted, the FK is set to `NULL` (ON DELETE SET NULL).
- **Account menu:** group accounts see no "Mein Konto" item in the dropdown. Only "Logout" (and "Admin area" if the account were ever an admin, which is not permitted).
- **Default post-login target:** the research home page (not `/auth/account`).
- `account_kind = 'group'` in the DB.
- `display_name` stores the group name / display name.
- `username` stores the login name (lowercase, validated: `[a-z0-9][a-z0-9\-_]{0,62}[a-z0-9]`, no `@`, max 64 chars).

---

## Login Field

The login form field accepts both:

- an **email address** → resolves to a personal account
- a **login name** (username) → resolves to a group account (or a personal account whose username happens to match)

The server resolves the identifier using `find_user_by_username_or_email`: username is checked first, then email. The form field name remains `email` for backward compatibility; the input type is `text` (not `email`).

Label (DE): `E-Mail oder Login-Name`
Label (EN): `Email or login name`

---

## Database Columns (users table)

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `account_kind` | TEXT | NOT NULL DEFAULT 'personal' CHECK IN ('personal', 'group') | Added in migration 0010 |
| `responsible_admin_user_id` | TEXT | NULL, FK → users.user_id ON DELETE SET NULL | Added in migration 0010 |

All pre-existing accounts automatically received `account_kind = 'personal'` via the DEFAULT.

---

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/admin/groups` | Create a group account |
| PATCH | `/admin/groups/<id>` | Edit display_name, is_active, expiry, responsible_admin |
| POST | `/admin/groups/<id>/set-password` | Set a new password for a group account |
| GET | `/admin/admins` | List active admins for the responsible-admin dropdown |

---

## What Group Accounts Can Do

Group accounts are functionally equivalent to personal `user` accounts for all research workflows:

- access protected research pages
- create, load, and save private research sets
- use comparison and phenomena workbenches
- own private sets (identified by `owner_user_id`)

---

## No Public Username Login for Personal Accounts

The `login_name` / `username` login path is a **narrowly scoped exception** for group accounts. It does not introduce:

- public self-registration
- public username-based login for ordinary personal users
- any new role or capability

Personal accounts continue to be identified and administered primarily by email address.

---

## Logging and Audit

- `created_by_user_id` on `users` records which admin created the account (both personal and group).
- `responsible_admin_user_id` on group accounts records the organisationally responsible admin.
- JWT claims include `account_kind` so templates and route guards can act without DB lookups.
- The admin user list shows `shown_creator_name`, resolved server-side to the responsible admin for group accounts or to the creator for personal accounts.

---

## Rollback / Migration Safety

Migration `0010_add_account_kind.sql` is purely additive:

- `ADD COLUMN IF NOT EXISTS account_kind … DEFAULT 'personal'`
- `ADD COLUMN IF NOT EXISTS responsible_admin_user_id … REFERENCES users(user_id) ON DELETE SET NULL`

No existing rows are modified. Rollback removes the two columns and their indexes.
