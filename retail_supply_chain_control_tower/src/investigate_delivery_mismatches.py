
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

orders = df[columns].drop_duplicates(subset=["Order Id"]).copy()

orders["calculated_late"] = (
    orders["Days for shipping (real)"]
    > orders["Days for shipment (scheduled)"]
)

print("\n===== DELIVERY STATUS COUNTS =====")
print(orders["Delivery Status"].value_counts().to_string())

print("\n===== MISMATCHED ORDERS =====")
mismatches = orders[
    orders["calculated_late"]
    != (orders["Late_delivery_risk"] == 1)
]

print("Mismatch count:", len(mismatches))
print("\nMismatch breakdown by status:")
print(mismatches["Delivery Status"].value_counts().to_string())

print("\nMismatch breakdown by shipping mode:")
print(mismatches["Shipping Mode"].value_counts().to_string())

print("\nExample mismatched records:")
print(mismatches.head(10).to_string(index=False))

print("\n===== STATUS VS CALCULATED LATE =====")
print(pd.crosstab(
    orders["Delivery Status"],
    orders["calculated_late"],
    margins=True
).to_string())
