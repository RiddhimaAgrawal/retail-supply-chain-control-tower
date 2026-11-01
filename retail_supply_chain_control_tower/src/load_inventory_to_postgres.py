
from pathlib import Path
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "processed" / "inventory_snapshots.csv"

load_dotenv(BASE_DIR / ".env")

required_columns = [
    "snapshot_date",
    "product_id",
    "warehouse_id",
    "stock_on_hand",
    "daily_demand_estimate",
    "reorder_point",
    "supplier_id",
    "unit_cost",
    "is_simulated",
]

df = pd.read_csv(CSV_PATH, parse_dates=["snapshot_date"])

if df.empty:
    raise ValueError("Inventory CSV is empty.")

if df[required_columns].isnull().any().any():
    raise ValueError("Inventory data contains missing required values.")

if df.duplicated(
    subset=["snapshot_date", "product_id", "warehouse_id"]
).any():
    raise ValueError("Duplicate product/warehouse/date records found.")

connection_params = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

if not all(connection_params.values()):
    raise ValueError("Check the database settings in your .env file.")

insert_sql = """
    INSERT INTO inventory_snapshots (
        snapshot_date, product_id, warehouse_id,
        stock_on_hand, daily_demand_estimate,
        reorder_point, supplier_id, unit_cost, is_simulated
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (snapshot_date, product_id, warehouse_id)
    DO NOTHING;
"""

records = [
    (
        row.snapshot_date.date(),
        int(row.product_id),
        int(row.warehouse_id),
        int(row.stock_on_hand),
        float(row.daily_demand_estimate),
        int(row.reorder_point),
        int(row.supplier_id),
        float(row.unit_cost),
        bool(row.is_simulated),
    )
    for row in df.itertuples(index=False)
]

with psycopg.connect(**connection_params) as conn:
    with conn.cursor() as cur:
        cur.executemany(insert_sql, records)

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM inventory_snapshots")
        total_rows = cur.fetchone()[0]

print(f"CSV records: {len(df):,}")
print(f"Records in PostgreSQL: {total_rows:,}")
print("Inventory load completed.")
