import sqlite3
from flask import current_app

def init_db():
    db_path = current_app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_date TEXT,
            usage_kwh REAL,
            generation_kwh REAL,
            efficiency REAL
        )
    ''')

    conn.commit()
    conn.close()
