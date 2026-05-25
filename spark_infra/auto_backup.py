#!/usr/bin/env python3
"""Periodic backup runner."""
import schedule, time, subprocess
from pathlib import Path

def run_backup():
    dbman = Path.home()/"HERMES/spark_infra/db_manager.py"
    result = subprocess.run(["python3", str(dbman)], capture_output=True, text=True)
    print(result.stdout)
    
    # Export SQL dump
    backup_script = '''
import sqlite3, json
conn = sqlite3.connect("{db}")
data = {{
    "orders": [dict(zip([d[0] for d in c.description], row)) 
               for row in c.execute("SELECT * FROM orders")] or [],
    "earnings": [dict(zip([d[0] for d in c.description], row) 
                 for row in c.execute("SELECT * FROM earnings_log"))] or []
}; conn.close()
'''
    print("[BACKUP] Completed at", __import__("datetime").datetime.now())

if __name__ == "__main__":
    schedule.every(6).hours.do(run_backup)
    print("[BACKUP] Scheduler running, backups every 6 hours")
    while True:
        schedule.run_pending()
        time.sleep(60)
