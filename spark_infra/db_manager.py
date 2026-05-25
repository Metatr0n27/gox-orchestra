#!/usr/bin/env python3
"""SQLite-backed persistence for Spark Navigator data."""
import sqlite3, json, os
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home()/"HERMES/spark_infra/db/spark.db"

SCHEMA = '''
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    items INTEGER,
    destination TEXT,
    tip REAL,
    base_pay REAL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS earnings_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    source TEXT,
    logged_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routes_learned (
    address_hash TEXT PRIMARY KEY,
    unit_number TEXT,
    corrected_lat REAL,
    corrected_lng REAL,
    times_confirmed INTEGER DEFAULT 1,
    last_updated TIMESTAMP
);
'''

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    return conn

def insert_order(order_id, items, dest="", tip=0, base=7):
    with get_conn() as c:
        c.execute('''INSERT OR REPLACE INTO orders 
            (id, items, destination, tip, base_pay, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)''',
            (order_id, items, dest, tip, base, datetime.now().isoformat()))

def complete_order(order_id, actual_tip=None):
    with get_conn() as c:
        tip_val = actual_tip if actual_tip else c.execute(
            'SELECT tip FROM orders WHERE id=?',(order_id,)).fetchone()
        tip_final = tip_val[0] if tip_val else 0
        c.execute('''UPDATE orders SET status='completed', completed_at=?, tip=? 
            WHERE id=?''', (datetime.now().isoformat(), tip_final, order_id))

def log_earning(amount, source="manual"):
    with get_conn() as c:
        c.execute('INSERT INTO earnings_log (amount, source, logged_at) VALUES (?,?,?)',
            (amount, source, datetime.now().isoformat()))
    return get_totals()

def get_totals():
    with get_conn() as c:
        total = c.execute('SELECT COALESCE(SUM(amount),0) FROM earnings_log').fetchone()[0]
        count = c.execute('SELECT COUNT(*) FROM earnings_log').fetchone()[0]
        return {"total": total, "entries": count}

def export_backup():
    backup_dir = Path.home()/"HERMES/spark_infra/backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir/f"spark_backup_{stamp}.sql"
    os.system(f'sqlite3 {DB_PATH} ".dump" > {backup_file}')
    return backup_file

if __name__ == "__main__":
    print("[DB] Initializing SQLite persistence...")
    get_conn()
    print(f"[DB] Database ready: {DB_PATH}")
    totals = get_totals()
    print(f"[DB] Current earnings: ${totals['total']:.2f} ({totals['entries']} entries)")
