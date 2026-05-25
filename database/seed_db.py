"""Database seeder script - loads CSV data into Postgres."""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import execute_script
from config.settings import get_settings

DATA_DIR = Path(__file__).parent / "data"
CHUNK_SIZE = 10000
TABLES_NEEDING_ID = ["sales", "finance"]  # ✅ add this line


def load_csv_to_db(table_name: str, csv_file: str, engine, chunk: bool = False) -> int:
    """Load CSV file into database table."""
    print(f"Loading {table_name}...")
    df = pd.read_csv(DATA_DIR / csv_file)

    # Clean numeric columns for Postgres compatibility
    # Postgres is strict about numeric formatting (e.g., "28.  0" is invalid)
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    # Also explicitly check columns that should be numeric but might be read as objects due to bad formatting
    potential_numeric = [
        "temperature",
        "rainfall",
        "humidity",
        "revenue",
        "amount",
        "unit_price",
        "unit_cost",
    ]
    for col in potential_numeric:
        if col in df.columns and col not in numeric_cols:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r"\s+", "", regex=True), errors="coerce"
            )

    # ✅ Only add id for tables that need it and don't already have it
    if table_name in TABLES_NEEDING_ID and "id" not in df.columns:
        df.insert(0, "id", range(1, len(df) + 1))

    if chunk:
        for i in range(0, len(df), CHUNK_SIZE):
            df.iloc[i : i + CHUNK_SIZE].to_sql(
                table_name, engine, if_exists="append", index=False
            )
    else:
        df.to_sql(table_name, engine, if_exists="append", index=False)

    print(f"✓ Loaded {len(df)} {table_name}")
    return len(df)


def seed_database():
    """Initialize schema and load all CSV data."""
    print("=" * 60)
    print("Starting database seeding (PostgreSQL)...")
    print("=" * 60)

    try:
        # Initialize schema - Running this even if tables exist to ensure correct SERIAL primary keys
        execute_script(Path(__file__).parent / "schema.sql")
        print("✓ Schema initialized")

        # Create SQLAlchemy engine for pandas to_sql
        engine = create_engine(get_settings().postgres_url)

        # Truncate tables to ensure fresh start
        print("Truncating existing tables for fresh seed...")
        with engine.connect() as conn:
            from sqlalchemy import text

            conn.execute(
                text(
                    "TRUNCATE TABLE tickets, sales, finance, inventory, vendors, conversations, forecasts CASCADE"
                )
            )
            conn.commit()

        # Load data (vendors first due to foreign keys)
        counts = {
            "vendors": load_csv_to_db("vendors", "vendors.csv", engine),
            "inventory": load_csv_to_db("inventory", "inventory.csv", engine),
            "finance": load_csv_to_db("finance", "finance.csv", engine, chunk=True),
            "sales": load_csv_to_db("sales", "sales.csv", engine, chunk=True),
        }

        # Summary
        print("\n" + "=" * 60)
        print("✓ Seeding completed successfully!")
        for table, count in counts.items():
            print(f"  {table}: {count} records")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"✗ Seeding failed: {e}")
        print("=" * 60)
        return False


def main():
    """Main entry point for seeding."""
    return seed_database()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
