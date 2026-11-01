
from pathlib import Path
import pandas as pd

# Locate the project and dataset
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"

df = pd.read_csv(DATA_PATH, encoding="latin1", low_memory=False)

# Keep only the columns needed for delivery analysis.
# This also excludes sensitive and irrelevant customer information.
columns = [
    "Order Id",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Delivery Status",
    "Shipping Mode",
]

df = df[columns].copy()

# Check for missing values in the fields we need.
df = df.dropna(subset=[
    "Order Id",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
])

# Each order can have multiple product rows.
# Count each order once for shipment-level KPIs.
orders = df.drop_duplicates(subset=["Order Id"]).copy()

# An order is on time if actual shipping duration
# is less than or equal to the scheduled duration.
orders["is_late"] = (
    orders["Days for shipping (real)"]
    > orders["Days for shipment (scheduled)"]
)

orders["is_on_time"] = ~orders["is_late"]

total_orders = len(orders)
late_orders = int(orders["is_late"].sum())
on_time_orders = int(orders["is_on_time"].sum())

on_time_rate = (
    on_time_orders / total_orders * 100
    if total_orders else 0
)

late_rate = (
    late_orders / total_orders * 100
    if total_orders else 0
)

print("\n===== DELIVERY PERFORMANCE =====")
print(f"Unique orders analyzed: {total_orders:,}")
print(f"Late orders: {late_orders:,}")
print(f"On-time orders: {on_time_orders:,}")
print(f"On-time delivery rate: {on_time_rate:.2f}%")
print(f"Late delivery rate: {late_rate:.2f}%")

print("\n===== SHIPPING DURATION =====")
print(
    "Average actual duration:",
    f"{orders['Days for shipping (real)'].mean():.2f} days"
)
print(
    "Average scheduled duration:",
    f"{orders['Days for shipment (scheduled)'].mean():.2f} days"
)

print("\n===== PERFORMANCE BY SHIPPING MODE =====")
by_mode = orders.groupby("Shipping Mode").agg(
    total_orders=("Order Id", "nunique"),
    average_actual_days=("Days for shipping (real)", "mean"),
    average_scheduled_days=("Days for shipment (scheduled)", "mean"),
    late_orders=("is_late", "sum"),
)

by_mode["late_rate_pct"] = (
    by_mode["late_orders"] / by_mode["total_orders"] * 100
)

print(by_mode.round(2).to_string())

# Save the order-level analysis for later use.
output_path = PROJECT_ROOT / "data" / "processed" / "delivery_analysis.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

orders.to_csv(output_path, index=False)
print(f"\nSaved order-level results to: {output_path}")
