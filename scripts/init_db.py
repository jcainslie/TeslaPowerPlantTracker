# scripts/init_db.py

import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DB path from env
db_path = os.getenv("DATABASE_PATH", "instance/tesla_tracker.db")

def init_db():
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            bill_date TEXT,
            usage_kwh REAL,
            usage_cost REAL,
            generation_kwh REAL,
            generation_credit REAL,
            efficiency REAL,
            ghi_kwh_m2 REAL,
            potential_kwh REAL
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {db_path}")

if __name__ == "__main__":
    init_db()
