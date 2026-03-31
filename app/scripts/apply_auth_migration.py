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
POSTGRES_SQL_FILE = ROOT / "migrations" / "0001_create_auth_schema_postgres.sql"
ANALYTICS_SQL_FILE = ROOT / "migrations" / "0002_create_analytics_tables.sql"


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

    if not POSTGRES_SQL_FILE.exists():
        print(f"ERROR: Migration SQL not found: {POSTGRES_SQL_FILE}", file=sys.stderr)
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

    with open(POSTGRES_SQL_FILE, "r", encoding="utf-8") as f:
        sql = f.read()

    # Remove explicit BEGIN/COMMIT from SQL as psycopg handles transactions
    # This prevents nested transaction issues
    sql = sql.replace("BEGIN;", "").replace("COMMIT;", "")

    conn = None
    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(db_url)
        print("Connected successfully.")

        with conn.cursor() as cur:
            if reset:
                # Drop existing tables (in reverse order of dependencies)
                print("Dropping existing auth tables...")
                cur.execute("DROP TABLE IF EXISTS analytics_daily CASCADE")
                cur.execute("DROP TABLE IF EXISTS reset_tokens CASCADE")
                cur.execute("DROP TABLE IF EXISTS refresh_tokens CASCADE")
                cur.execute("DROP TABLE IF EXISTS users CASCADE")
                cur.execute("DROP TYPE IF EXISTS user_role CASCADE")
                conn.commit()
                print("Existing tables dropped.")

            # Apply migration
            print("Executing auth migration SQL...")
            cur.execute(sql)
            conn.commit()
            print("PostgreSQL auth migration applied successfully.")

            # Apply analytics migration (0002)
            if ANALYTICS_SQL_FILE.exists():
                print("Executing analytics migration SQL...")
                with open(ANALYTICS_SQL_FILE, "r", encoding="utf-8") as f:
                    analytics_sql = f.read()
                analytics_sql = analytics_sql.replace("BEGIN;", "").replace(
                    "COMMIT;", ""
                )
                cur.execute(analytics_sql)
                conn.commit()
                print("PostgreSQL analytics migration applied successfully.")
            else:
                print(f"Warning: Analytics migration not found: {ANALYTICS_SQL_FILE}")

    except OperationalError as e:
        print(f"ERROR: Database connection failed: {e}", file=sys.stderr)
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"ERROR: Migration failed: {e}", file=sys.stderr)
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
