
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def run_data_quality_checks():
    query = """
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT order_id) AS unique_order_ids,
            COUNT(*) FILTER (
                WHERE order_id IS NULL
            ) AS missing_order_ids,
            COUNT(*) FILTER (
                WHERE actual_shipping_days IS NULL
                   OR scheduled_shipping_days IS NULL
                   OR delivery_status IS NULL
                   OR shipping_mode IS NULL
            ) AS rows_with_missing_required_fields,
            COUNT(*) FILTER (
                WHERE actual_shipping_days < 0
                   OR scheduled_shipping_days < 0
            ) AS rows_with_invalid_durations,
            COUNT(*) FILTER (
                WHERE is_late IS DISTINCT FROM
                      (delivery_status = 'Late delivery')
            ) AS late_flag_mismatches
        FROM orders;
    """

    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()

    checks = {
        "Total rows": result[0] == 62897,
        "Unique order IDs": result[1] == result[0],
        "Missing order IDs": result[2] == 0,
        "Missing required fields": result[3] == 0,
        "Invalid shipping durations": result[4] == 0,
        "Late flag mismatches": result[5] == 0,
    }

    print("\nPOSTGRESQL DATA QUALITY REPORT")
    print("-" * 40)

    labels = [
        "Total rows",
        "Unique order IDs",
        "Missing order IDs",
        "Missing required fields",
        "Invalid shipping durations",
        "Late flag mismatches",
    ]

    for label, value in zip(labels, result):
        print(f"{label}: {value:,}")

    print("\nCHECK RESULTS")
    for check, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {check}")

    if not all(checks.values()):
        raise RuntimeError("Data quality validation failed.")

    print("\nAll data quality checks passed.")


if __name__ == "__main__":
    run_data_quality_checks()
