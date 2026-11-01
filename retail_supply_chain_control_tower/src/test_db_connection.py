
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

try:
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), version();")
            database, version = cur.fetchone()

            print("Connection successful!")
            print("Database:", database)
            print("PostgreSQL:", version.split(",")[0])

except Exception as error:
    print("Connection failed.")
    print("Error:", error)
