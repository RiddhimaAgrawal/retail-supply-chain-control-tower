
import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

with psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
) as conn:
    df = pd.read_sql_query(
        """
        SELECT
            order_month,
            SUM(total_orders) AS total_orders,
            SUM(late_orders) AS late_orders,
            ROUND(
                100.0 * SUM(late_orders)
                / NULLIF(SUM(total_orders), 0),
                2
            ) AS late_delivery_rate_pct
        FROM vw_monthly_delivery_performance
        GROUP BY order_month
        ORDER BY order_month;
        """,
        conn,
    )

output_dir = PROJECT_ROOT / "reports"
output_dir.mkdir(parents=True, exist_ok=True)

df["order_month"] = pd.to_datetime(df["order_month"])

plt.figure(figsize=(12, 6))
plt.plot(
    df["order_month"],
    df["late_delivery_rate_pct"],
    marker="o",
)
plt.axhline(
    57.31,
    linestyle="--",
    label="Overall late-delivery rate (57.31%)",
)
plt.title("Monthly Late-Delivery Rate")
plt.xlabel("Order Month")
plt.ylabel("Late Deliveries (%)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

chart_path = output_dir / "monthly_delivery_trend.png"
plt.savefig(chart_path, dpi=150)
plt.close()

df.to_csv(
    PROJECT_ROOT / "data" / "processed" / "monthly_delivery_trend.csv",
    index=False,
)

print(f"Months analyzed: {len(df)}")
print(f"Chart saved to: {chart_path}")
print("Monthly trend CSV saved successfully.")
