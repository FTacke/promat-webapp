"""Apply auth database migrations for PostgreSQL.

Usage:
    # PostgreSQL (requires AUTH_DATABASE_URL)
    python scripts/apply_auth_migration.py --engine postgres

    # Reset and recreate
    python scripts/apply_auth_migration.py --engine postgres --reset
"""

from __future__ import annotations

import os
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "migrations"


def _postgres_migration_files() -> tuple[Path, ...]:
    migrations: list[Path] = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if not path.name[:4].isdigit():
            continue
        if path.name.endswith("_sqlite.sql"):
            continue
        migrations.append(path)
    return tuple(migrations)


def _read_sql(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    return sql.replace("BEGIN;", "").replace("COMMIT;", "")


def apply_postgres_migration(reset: bool = False) -> None:
    """Apply PostgreSQL migration using AUTH_DATABASE_URL."""
    import sys

    try:
        import psycopg2
        from psycopg2 import OperationalError
    except ImportError:
        print(
            "ERROR: psycopg2 not installed. Run: pip install psycopg2-binary",
            file=sys.stderr,
        )
        sys.exit(1)

    migration_files = _postgres_migration_files()
    if not migration_files:
        print(f"ERROR: No PostgreSQL migration SQL files found in: {MIGRATIONS_DIR}", file=sys.stderr)
        sys.exit(1)
    if migration_files[0].name != "0001_create_auth_schema_postgres.sql":
        print(
            "ERROR: PostgreSQL migration chain must start with 0001_create_auth_schema_postgres.sql.",
            file=sys.stderr,
        )
        sys.exit(1)

    db_url = os.getenv("AUTH_DATABASE_URL", "")
    if not db_url:
        print(
            "ERROR: AUTH_DATABASE_URL is required for auth/core migrations.",
            file=sys.stderr,
        )
        sys.exit(1)
    if not db_url.startswith("postgresql"):
        print(
            "ERROR: AUTH_DATABASE_URL must point to PostgreSQL for auth/core migrations.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Convert SQLAlchemy URL to psycopg2 format
    # postgresql+psycopg2://... -> postgresql://...
    # postgresql+psycopg://...  -> postgresql://...
    if "+psycopg2" in db_url:
        db_url = db_url.replace("+psycopg2", "")
    if "+psycopg" in db_url:
        db_url = db_url.replace("+psycopg", "")

    # Add connect_timeout if not present
    if "connect_timeout" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}connect_timeout=10"

    conn = None
    current_migration_path: Path | None = None
    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(db_url)
        print("Connected successfully.")

        with conn.cursor() as cur:
            if reset:
                # Drop existing tables (in reverse order of dependencies)
                print("Dropping existing auth tables...")
                cur.execute("DROP TABLE IF EXISTS research_session_exposures CASCADE")
                cur.execute("DROP TABLE IF EXISTS research_sessions CASCADE")
                cur.execute("DROP TABLE IF EXISTS research_people CASCADE")
                cur.execute("DROP TABLE IF EXISTS research_set_workbench_sessions CASCADE")
                cur.execute("DROP TABLE IF EXISTS research_set_workbench_state CASCADE")
                cur.execute("DROP TABLE IF EXISTS research_set_sessions CASCADE")
                cur.execute("DROP TABLE IF EXISTS research_set_items CASCADE")
                cur.execute("DROP TABLE IF EXISTS research_sets CASCADE")
                cur.execute("DROP TABLE IF EXISTS access_requests CASCADE")
                cur.execute("DROP TABLE IF EXISTS analytics_language_area_daily CASCADE")
                cur.execute("DROP TABLE IF EXISTS analytics_daily CASCADE")
                cur.execute("DROP TABLE IF EXISTS reset_tokens CASCADE")
                cur.execute("DROP TABLE IF EXISTS refresh_tokens CASCADE")
                cur.execute("DROP TABLE IF EXISTS users CASCADE")
                cur.execute("DROP TYPE IF EXISTS user_role CASCADE")
                conn.commit()
                print("Existing tables dropped.")

            for migration_path in migration_files:
                current_migration_path = migration_path
                print(f"Executing migration SQL: {migration_path.name}...")
                cur.execute(_read_sql(migration_path))
                conn.commit()
                print(f"PostgreSQL migration applied successfully: {migration_path.name}")
                current_migration_path = None

    except OperationalError as e:
        print(f"ERROR: Database connection failed: {e}", file=sys.stderr)
        sys.exit(1)
    except psycopg2.Error as e:
        migration_label = current_migration_path.name if current_migration_path is not None else "unknown"
        message_parts = [
            "ERROR: PostgreSQL migration failed",
            "engine=postgres",
            f"migration={migration_label}",
        ]
        if getattr(e, "diag", None) is not None and getattr(e.diag, "message_primary", None):
            message_parts.append(f"detail={e.diag.message_primary}")
        elif str(e):
            message_parts.append(f"detail={e}")
        print("; ".join(message_parts), file=sys.stderr)
        if getattr(e, "pgerror", None):
            print(e.pgerror.strip(), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply auth database migrations")
    parser.add_argument(
        "--engine",
        choices=["postgres"],
        default="postgres",
        help="Database engine to use (only postgres is supported for auth/core)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="DROP existing tables before applying migration (dev-only).",
    )
    args = parser.parse_args()

    print(f"Applying PostgreSQL migration (reset={args.reset})...")
    apply_postgres_migration(reset=args.reset)
