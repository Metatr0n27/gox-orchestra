#!/usr/bin/env python3
import os, json, subprocess, time
from datetime import datetime

BASE = os.path.expanduser("~/HERMES")
QUEUE = f"{BASE}/queue/tasks.json"
FAILED = f"{BASE}/failed"
DONE = f"{BASE}/done"
LOG = f"{BASE}/logs/activity.log"

for d in [FAILED, DONE]:
    os.makedirs(d, exist_ok=True)

def log(m):
    line = f"[EXEC][{datetime.now():%H:%M:%S}] {m}"
    print(line, flush=True)
    open(LOG, "a").write(line+"\n")

def load_q():
    try:
        return json.load(open(QUEUE)).get("pending", [])
    except:
        return []

def save_q(tasks):
    json.dump({"pending": tasks, "updated": datetime.now().isoformat()}, open(QUEUE, "w"), indent=2)

def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, cwd=BASE, capture_output=True, text=True, timeout=180)
        return r.returncode, r.stdout[-400:], r.stderr[-400:]
    except Exception as e:
        return -1, "", str(e)[:200]

def main():
    log("Executor started")
    while True:
        tasks = load_q()
        if not tasks:
            time.sleep(2)
            continue
        
        t = tasks.pop(0)
        save_q(tasks)
        
        tid = t.get("id", "?")
        cmd = t.get("command", "")
        
        log(f"Running [{tid}]: {cmd[:50]}")
        rc, out, err = run_cmd(cmd)
        
        if rc == 0:
            t["status"] = "done"
            t["finished"] = datetime.now().isoformat()
            json.dump(t, open(f"{DONE}/{tid}.json", "w"), indent=2)
            log(f"DONE [{tid}]")
        else:
            t["status"] = "failed"
            t["error"] = err
            t["attempts"] = t.get("attempts", 0) + 1
            json.dump(t, open(f"{FAILED}/{tid}.json", "w"), indent=2)
            log(f"FAIL [{tid}] - sent to repair")

if __name__ == "__main__":
    main()
