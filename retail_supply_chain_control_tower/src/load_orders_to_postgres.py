
import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "final_delivery_kpis_by_order.csv"
)

if not CSV_PATH.exists():
    raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)

# Keep only the columns required by our PostgreSQL table.
df = df[
    [
        "Order Id",
        "Days for shipping (real)",
        "Days for shipment (scheduled)",
        "Delivery Status",
        "Shipping Mode",
    ]
].copy()

df = df.rename(
    columns={
        "Order Id": "order_id",
        "Days for shipping (real)": "actual_shipping_days",
        "Days for shipment (scheduled)": "scheduled_shipping_days",
        "Delivery Status": "delivery_status",
        "Shipping Mode": "shipping_mode",
    }
)

df["is_late"] = df["delivery_status"].eq("Late delivery")

# Remove any accidental duplicate order IDs before importing.
df = df.drop_duplicates(subset=["order_id"])

records = [
    (
        int(row.order_id),
        int(row.actual_shipping_days),
        int(row.scheduled_shipping_days),
        row.delivery_status,
        row.shipping_mode,
        bool(row.is_late),
    )
    for row in df.itertuples(index=False)
]

try:
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
                INSERT INTO orders (
                    order_id,
                    actual_shipping_days,
                    scheduled_shipping_days,
                    delivery_status,
                    shipping_mode,
                    is_late
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id) DO NOTHING;
                """,
                records,
            )

            cur.execute("SELECT COUNT(*) FROM orders")
            total = cur.fetchone()[0]

    print(f"CSV rows prepared: {len(records):,}")
    print(f"Rows currently in PostgreSQL orders table: {total:,}")
    print("Import completed successfully.")

except Exception as error:
    print("Import failed:", error)
    raise
