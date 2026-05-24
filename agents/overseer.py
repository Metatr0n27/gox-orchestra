#!/usr/bin/env python3
import os, json, time
from datetime import datetime

BASE = os.path.expanduser("~/HERMES")
DONE = f"{BASE}/done"
FAILED = f"{BASE}/failed"
FIXES = f"{BASE}/fixed"
STATUS = f"{BASE}/status.json"
LOG = f"{BASE}/logs/overseer.log"

def log(m):
    line = f"[BOSS][{datetime.now():%H:%M:%S}] {m}"
    print(line, flush=True)
    open(LOG, "a").write(line+"\n")

def notify_user(subject, msg):
    # Placeholder - wire your notification method here
    # Options: email, telegram, pushbullet, ntfy.sh
    log(f"NOTIFY: {subject} - {msg[:50]}")
    
    # Easy option: ntfy.sh (free, no signup)
    os.system(f'''curl -s -d "{msg}" ntfy.sh/goxalerts >/dev/null 2>&1 &''')

def main():
    log("Overseer activated")
    last_counts = {"done": 0, "fail": 0}
    
    while True:
        done_cnt = len([f for f in os.listdir(DONE) if f.endswith(".json")]) if os.path.exists(DONE) else 0
        fail_cnt = len([f for f in os.listdir(FAILED) if f.endswith(".json")]) if os.path.exists(FAILED) else 0
        stuck_cnt = len([f for f in os.listdir(FIXES) if f.endswith(".json")]) if os.path.exists(FIXES) else 0
        
        if done_cnt != last_counts["done"]:
            diff = done_cnt - last_counts["done"]
            if diff > 0:
                notify_user("Progress", f"{diff} tasks completed. Total: {done_cnt}")
        
        if fail_cnt > last_counts["fail"]:
            notify_user("Warning", f"{fail_cnt} tasks need attention")
        
        if stuck_cnt > 0:
            notify_user("Action Needed", f"{stuck_cnt} tasks require manual decision")
        
        status = {
            "completed": done_cnt,
            "processing": fail_cnt,
            "blocked": stuck_cnt,
            "checked_at": datetime.now().isoformat()
        }
        json.dump(status, open(STATUS, "w"), indent=2)
        
        last_counts = {"done": done_cnt, "fail": fail_cnt}
        time.sleep(30)

if __name__ == "__main__":
    main()
