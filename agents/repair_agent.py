#!/usr/bin/env python3
import os, json, time, shutil
from datetime import datetime

BASE = os.path.expanduser("~/HERMES")
FAILED = f"{BASE}/failed"
QUEUE = f"{BASE}/queue/tasks.json"
FIXES = f"{BASE}/fixed"
LOG = f"{BASE}/logs/repair.log"

os.makedirs(FIXES, exist_ok=True)

def log(m):
    line = f"[FIX][{datetime.now():%H:%M:%S}] {m}"
    print(line, flush=True)
    open(LOG, "a").write(line+"\n")

def analyze_and_fix(err):
    err_low = err.lower()
    
    if "command not found" in err_low:
        return "sudo apt-get update && sudo apt-get install -y $(basename $CMD 2>/dev/null || echo 'build-essential')"
    elif "permission denied" in err_low:
        return "chmod +x $TARGET 2>/dev/null || sudo chmod +x $TARGET"
    elif "no such file" in err_low:
        return "mkdir -p $(dirname $TARGET 2>/dev/null) && touch $TARGET"
    elif "connection" in err_low or "network" in err_low:
        return "sleep 5 && ping -c 1 google.com && RETRY_ORIGINAL"
    else:
        return None

def main():
    log("Repair agent watching...")
    while True:
        for fname in os.listdir(FAILED):
            if not fname.endswith(".json"):
                continue
            
            fpath = os.path.join(FAILED, fname)
            t = json.load(open(fpath))
            
            attempts = t.get("attempts", 0)
            max_att = t.get("max_attempts", 3)
            
            if attempts >= max_att:
                log(f"Giving up on [{t.get('id')}] - max attempts reached")
                shutil.move(fpath, f"{FIXES}/{fname}")
                continue
            
            fix_cmd = analyze_and_fix(t.get("error", ""))
            
            if fix_cmd:
                t["fix_attempted"] = fix_cmd
                t["attempts"] = attempts + 1
                
                # Return to queue with fix prefix
                t["command"] = f"{fix_cmd} && {t.get('command','')}"
                
                data = json.load(open(QUEUE))
                data["pending"].insert(0, t)
                json.dump(data, open(QUEUE, "w"), indent=2)
                
                os.remove(fpath)
                log(f"Repaired [{t.get('id')}] - attempt {attempts+1}")
            else:
                log(f"No auto-fix for [{t.get('id')}] - manual review needed")
                shutil.move(fpath, f"{FIXES}/{fname}")
        
        time.sleep(5)

if __name__ == "__main__":
    main()
