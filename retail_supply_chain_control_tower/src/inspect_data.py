
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
csv_path = project_root / "data" / "raw" / "DataCoSupplyChainDataset.csv"

if not csv_path.exists():
    raise FileNotFoundError(
        f"Dataset not found at {csv_path}. "
        "Check the CSV filename and data/raw folder."
    )

df = pd.read_csv(csv_path, encoding="latin1", low_memory=False)

print("\n--- DATASET SIZE ---")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- FIRST FIVE ROWS ---")
print(df.head().to_string())

print("\n--- MISSING VALUES ---")
print(df.isnull().sum().sort_values(ascending=False).head(15))

print("\n--- DATA TYPES ---")
print(df.dtypes)
