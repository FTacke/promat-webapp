# 2026-05-30 – Gruppenaccounts implementiert

## Ziel

Einführung von Gruppenaccounts (`account_kind = group`) neben den bisherigen persönlichen Accounts (`account_kind = personal`). Gruppenaccounts sind funktional normale `user`-Accounts, unterscheiden sich aber in Anlage, Login, Account-Self-Service und Anzeige.

## Umfang

### Neue Dateien
- `app/migrations/0010_add_account_kind.sql` – additive PostgreSQL-Migration (zwei neue Spalten, zwei Indexes, vollständig reversibel)
- `app/tests/test_group_accounts.py` – 23 neue Tests für alle Group-Account-Aspekte
- `docs/spec/auth-accounts.md` – neues Spec-Dokument für den Account-Typ-Vertrag

### Geänderte Dateien (Kernlogik)
- `app/src/app/auth/models.py` – neue Felder `account_kind`, `responsible_admin_user_id`, Relationship `responsible_admin`
- `app/src/app/auth/services.py` – `create_group_account()`, `list_active_admins()`, `validate_login_name()`, `normalize_login_name()`, `_responsible_admin_lookup()`, `create_access_token_for_user` (+`account_kind`, +`display_name` im JWT), `serialize_user_for_admin` (+neue Felder), `serialize_users_for_admin` (+responsible lookup)
- `app/src/app/routes/admin.py` – neue Endpoints `GET /admin/admins`, `POST /admin/groups`, `PATCH /admin/groups/<id>`, `POST /admin/groups/<id>/set-password`
- `app/src/app/routes/auth.py` – Login nutzt `find_user_by_username_or_email`, `_default_post_login_target` unterscheidet Gruppenaccounts, `account_page`/`account_update`/`account_password_page`/`account_password_submit`/`change_password` blockieren Gruppenaccounts, `_forgot_password_response` erzeugt keinen Reset-Token für Gruppenaccounts
- `app/src/app/__init__.py` – `g.account_kind` und `g.display_name` im Auth-Context

### Geänderte Dateien (UI/Templates)
- `app/templates/auth/admin_users.html` – `invite_note` entfernt, neue Tabellenspalten (Account/Typ/Login/Status/Gültig bis/Datum/Erstellt/Aktionen), neuer Gruppenaccount-Anlegen-Dialog, neuer Gruppenaccount-Bearbeiten-Dialog
- `app/templates/auth/login.html` – Input-Typ `text` statt `email`, Label-Key auf `auth.login.identifier_label` geändert
- `app/templates/partials/_top_app_bar.html` – Identity-Zeile im Dropdown (Gruppenname/Login-Name für Gruppe, Name/Rolle für persönlich), „Mein Konto" nur für `account_kind != 'group'`
- `app/templates/partials/_navigation_drawer.html` – „Mein Konto" nur für `account_kind != 'group'` im mobilen Drawer
- `app/static/js/auth/admin_users.js` – komplett neu: neue Tabellen-Render-Logik, Gruppenaccount-Dialog-Handling, `/admin/admins` API für Admin-Dropdown

### Geänderte Spec
- `docs/spec/platform-data-files.md` – email-only-Aussage angepasst, Gruppenaccounts erwähnt, Post-Login-Targets aktualisiert

### Angepasste Tests
- `app/tests/test_auth_phase1.py` – 3 Tests auf neue Labels/Verhalten aktualisiert

## Ergebnisse

- **Testsuite:** 667/667 bestanden (inkl. 23 neue Group-Account-Tests)
- **Migration:** erfolgreich gegen lokale Dev-PostgreSQL (Migration 0010)
- **Browser-Smoke:** Login-Label DE/EN korrekt, Admin-Seite zeigt beide Buttons, Gruppenaccount-Anlage per API funktioniert, Gruppenaccount-Login funktioniert, `/auth/account` leitet Gruppenaccounts um, „Mein Konto" fehlt für Gruppenaccounts, Gruppenname (display_name) korrekt in Identity-Zeile

## Produktions-Hinweise

Vor dem Produktions-Deploy:
1. `pg_dump` der Produktionsdatenbank erstellen und verifizieren
2. `python scripts/apply_auth_migration.py --engine postgres` ausführen – nur Migration 0010 wird neu angewendet
3. App neu deployen
4. Smoke-Test: `SELECT account_kind, COUNT(*) FROM users GROUP BY account_kind;` → nur `personal`; Admin-Seite ladbar; Login bestehender Accounts funktioniert
5. Rollback (falls nötig): SQL aus Kommentar am Ende von `0010_add_account_kind.sql` ausführen, dann alten Code deployen
