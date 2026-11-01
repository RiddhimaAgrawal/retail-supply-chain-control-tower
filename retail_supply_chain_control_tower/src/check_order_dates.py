
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
file_path = project_root / "data" / "raw" / "DataCoSupplyChainDataset.csv"

df = pd.read_csv(file_path, encoding="latin1", low_memory=False)

print("Order date column exists:", "order date (DateOrders)" in df.columns)
print("Order ID column exists:", "Order Id" in df.columns)

if "order date (DateOrders)" in df.columns:
    print("\nSample order dates:")
    print(
        df[["Order Id", "order date (DateOrders)"]]
        .head(10)
        .to_string(index=False)
    )

    dates = pd.to_datetime(
        df["order date (DateOrders)"],
        errors="coerce"
    )

    print("\nEarliest order date:", dates.min())
    print("Latest order date:", dates.max())
    print("Rows with unparseable dates:", dates.isna().sum())
