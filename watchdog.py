#!/usr/bin/env python3
import time
import subprocess
from datetime import datetime

INTERVAL_SEC = 600

def log(msg):
    ts = datetime.now().strftime("[%H:%M:%S]")
    print(f"{ts} {msg}")

def cycle():
    log("Running hunter scan...")
    result = subprocess.run(
        ["python3", "/home/metatron/HERMES/hunt.py"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        log("Scan complete - opportunities updated")
    else:
        log(f"Scan issue: {result.stderr[:60]}")

def main():
    log("WATCHDOG ACTIVE - scanning every 10 minutes")
    while True:
        cycle()
        log(f"Sleeping {INTERVAL_SEC//60} minutes...")
        time.sleep(INTERVAL_SEC)

if __name__ == "__main__":
    main()
