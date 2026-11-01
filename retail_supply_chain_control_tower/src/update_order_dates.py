
import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"

load_dotenv(PROJECT_ROOT / ".env")

# Load only the two columns we need.
df = pd.read_csv(
    CSV_PATH,
    encoding="latin1",
    low_memory=False,
    usecols=["Order Id", "order date (DateOrders)"]
)

df = df.drop_duplicates(subset=["Order Id"]).copy()

df["order_date"] = pd.to_datetime(
    df["order date (DateOrders)"],
    errors="coerce"
)

df = df.dropna(subset=["order_date"])

records = [
    (row.order_date.to_pydatetime(), int(row.order_id))
    for row in df.rename(
        columns={"Order Id": "order_id"}
    )[["order_id", "order_date"]].itertuples(index=False)
]

with psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
) as conn:
    with conn.cursor() as cur:
        cur.executemany(
            """
            UPDATE orders
            SET order_date = %s
            WHERE order_id = %s
            """,
            records
        )

        cur.execute("""
            SELECT
                COUNT(*) AS total_orders,
                COUNT(order_date) AS orders_with_dates,
                MIN(order_date) AS earliest_order,
                MAX(order_date) AS latest_order
            FROM orders
        """)

        result = cur.fetchone()

print(f"Unique source orders prepared: {len(records):,}")
print(f"Orders in PostgreSQL: {result[0]:,}")
print(f"Orders with dates: {result[1]:,}")
print(f"Earliest order date: {result[2]}")
print(f"Latest order date: {result[3]}")
