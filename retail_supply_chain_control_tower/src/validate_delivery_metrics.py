
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
    "Late_delivery_risk",
    "Shipping Mode",
]

df = df[columns].copy()
df = df.dropna(subset=["Order Id"])

# 1. Check whether shipping information is consistent within each order
check_columns = [
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Delivery Status",
    "Late_delivery_risk",
    "Shipping Mode",
]

consistency = df.groupby("Order Id")[check_columns].nunique(
    dropna=False
)

inconsistent_orders = consistency[
    (consistency > 1).any(axis=1)
]

print("\n===== ORDER CONSISTENCY CHECK =====")
print("Total unique orders:", df["Order Id"].nunique())
print("Orders with inconsistent shipping information:",
      len(inconsistent_orders))

# 2. Create an order-level dataset
orders = df.drop_duplicates(subset=["Order Id"]).copy()

orders = orders.dropna(subset=[
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
])

orders["calculated_late"] = (
    orders["Days for shipping (real)"]
    > orders["Days for shipment (scheduled)"]
)

# 3. Compare our calculation with the supplied Delivery Status
print("\n===== DELIVERY STATUS VALUES =====")
print(orders["Delivery Status"].value_counts(dropna=False).to_string())

print("\n===== CALCULATED LATE VS DELIVERY STATUS =====")
print(pd.crosstab(
    orders["calculated_late"],
    orders["Delivery Status"],
    margins=True
).to_string())

# 4. Compare our calculation with the supplied risk indicator
print("\n===== LATE DELIVERY RISK VALUES =====")
print(orders["Late_delivery_risk"].value_counts(dropna=False).to_string())

print("\n===== CALCULATED LATE VS LATE DELIVERY RISK =====")
print(pd.crosstab(
    orders["calculated_late"],
    orders["Late_delivery_risk"],
    margins=True
).to_string())

# 5. Save the consistency report
output_path = (
    PROJECT_ROOT / "data" / "processed"
    / "delivery_validation.csv"
)

inconsistent_orders.to_csv(output_path)
print(f"\nSaved consistency report to: {output_path}")
