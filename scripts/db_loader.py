"""
db_loader.py
Loads cleaned CSVs into PostgreSQL database.
Run AFTER clean_data.py.
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "tariff_jobs")

CLEANED_DIR = "data/cleaned"

def get_engine():
    conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(conn_str)


def create_database():
    """Create the database if it doesn't exist."""
    conn = psycopg2.connect(
        user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT, database="postgres"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"✅ Database '{DB_NAME}' created.")
    else:
        print(f"ℹ️  Database '{DB_NAME}' already exists.")
    conn.close()


def load_table(engine, csv_path: str, table_name: str, if_exists: str = "replace"):
    """Load a CSV into a PostgreSQL table."""
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    print(f"   ✅ Loaded {len(df)} rows → table: {table_name}")


if __name__ == "__main__":
    print("\n🚀 Loading data into PostgreSQL...\n")
    create_database()
    engine = get_engine()

    load_table(engine, f"{CLEANED_DIR}/employment_monthly.csv",    "employment_monthly")
    load_table(engine, f"{CLEANED_DIR}/trade_indicators_monthly.csv", "trade_indicators")
    load_table(engine, f"{CLEANED_DIR}/usitc_annual.csv",          "trade_flows_annual")
    load_table(engine, "data/raw/tariff_events.csv",               "tariff_events")
    load_table(engine, f"{CLEANED_DIR}/master_dataset.csv",        "master_dataset")

    print("\n✅ All tables loaded! Run sql/analysis_queries.sql next.\n")
