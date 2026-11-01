
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

# Reproducible synthetic data
START_DATE = "2026-07-01"
END_DATE = "2026-09-28"
NUM_PRODUCTS = 100
NUM_WAREHOUSES = 3
NUM_SUPPLIERS = 12

rng = __import__("numpy").random.default_rng(42)

dates = pd.date_range(START_DATE, END_DATE, freq="D")

# Product-level characteristics
products = pd.DataFrame({
    "product_id": range(1001, 1001 + NUM_PRODUCTS),
    "supplier_id": rng.integers(1, NUM_SUPPLIERS + 1, NUM_PRODUCTS),
    "unit_cost": rng.uniform(5, 250, NUM_PRODUCTS).round(2),
    "base_daily_demand": rng.uniform(2, 35, NUM_PRODUCTS).round(2),
})

records = []

for product in products.itertuples(index=False):
    for warehouse_id in range(1, NUM_WAREHOUSES + 1):
        stock = int(rng.uniform(50, 500))
        reorder_point = int(product.base_daily_demand * rng.uniform(4, 12))

        for date in dates:
            # Daily demand varies around the product's normal demand.
            demand = max(
                0,
                int(rng.normal(product.base_daily_demand, max(1, product.base_daily_demand * 0.25)))
            )

            # Occasional demand spikes.
            if rng.random() < 0.03:
                demand *= 2

            stock = max(0, stock - demand)

            # Simulate replenishment when stock is low.
            if stock <= reorder_point and rng.random() < 0.25:
                stock += int(rng.uniform(100, 350))

            records.append({
                "snapshot_date": date.date(),
                "product_id": product.product_id,
                "warehouse_id": warehouse_id,
                "stock_on_hand": stock,
                "daily_demand_estimate": round(
                    float(product.base_daily_demand), 2
                ),
                "reorder_point": reorder_point,
                "supplier_id": product.supplier_id,
                "unit_cost": product.unit_cost,
                "is_simulated": True,
            })

df = pd.DataFrame(records)

output_path = OUTPUT_DIR / "inventory_snapshots.csv"
df.to_csv(output_path, index=False)

print(f"Generated {len(df):,} inventory snapshots")
print(f"Date range: {df['snapshot_date'].min()} to "
      f"{df['snapshot_date'].max()}")
print(f"Products: {df['product_id'].nunique()}")
print(f"Warehouses: {df['warehouse_id'].nunique()}")
print(f"Zero-stock records: {(df['stock_on_hand'] == 0).sum():,}")
print(f"Saved to: {output_path}")
