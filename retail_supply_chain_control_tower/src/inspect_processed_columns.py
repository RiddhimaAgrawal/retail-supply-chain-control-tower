
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
file_path = project_root / "data" / "processed" / "final_delivery_kpis_by_order.csv"

df = pd.read_csv(file_path)

print("Columns available:")
for column in df.columns:
    print("-", column)

print("\nFirst 5 rows:")
print(df.head().to_string(index=False))
