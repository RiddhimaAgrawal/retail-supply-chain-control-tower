
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"

df = pd.read_csv(DATA_PATH, encoding="latin1", low_memory=False)

columns = [
    "Order Id",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Delivery Status",
    "Shipping Mode",
]

orders = df[columns].drop_duplicates(subset=["Order Id"]).copy()

# Exclude canceled orders from delivery performance calculations
canceled = orders[
    orders["Delivery Status"] == "Shipping canceled"
].copy()

delivered = orders[
    orders["Delivery Status"] != "Shipping canceled"
].copy()

delivered = delivered.dropna(subset=[
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
])

delivered["is_late"] = (
    delivered["Delivery Status"] == "Late delivery"
)

total_delivered = len(delivered)
late_orders = int(delivered["is_late"].sum())
on_time_orders = total_delivered - late_orders

late_rate = (
    late_orders / total_delivered * 100
    if total_delivered else 0
)
on_time_rate = (
    on_time_orders / total_delivered * 100
    if total_delivered else 0
)
cancellation_rate = (
    len(canceled) / len(orders) * 100
    if len(orders) else 0
)

print("\n===== FINAL DELIVERY KPIs =====")
print(f"Total unique orders: {len(orders):,}")
print(f"Canceled orders: {len(canceled):,}")
print(f"Eligible delivery orders: {total_delivered:,}")
print(f"Late orders: {late_orders:,}")
print(f"Non-late orders: {on_time_orders:,}")
print(f"Late delivery rate: {late_rate:.2f}%")
print(f"Non-late delivery rate: {on_time_rate:.2f}%")
print(f"Order cancellation rate: {cancellation_rate:.2f}%")

print("\n===== DELIVERY PERFORMANCE BY SHIPPING MODE =====")

by_mode = delivered.groupby("Shipping Mode").agg(
    eligible_orders=("Order Id", "nunique"),
    late_orders=("is_late", "sum"),
    average_actual_days=("Days for shipping (real)", "mean"),
    average_scheduled_days=("Days for shipment (scheduled)", "mean"),
)

by_mode["late_rate_pct"] = (
    by_mode["late_orders"] / by_mode["eligible_orders"] * 100
)

print(by_mode.round(2).to_string())

output_path = (
    PROJECT_ROOT / "data" / "processed"
    / "final_delivery_kpis_by_order.csv"
)

delivered.to_csv(output_path, index=False)
print(f"\nSaved eligible delivery orders to: {output_path}")
