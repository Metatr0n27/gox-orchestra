#!/usr/bin/env python3
"""
Continuously scans for common failures and remediates automatically.
Designed for operators who are not programmers.
"""
import os, json, subprocess, time
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "HERMES"
CHECK_INTERVAL_SECONDS = 60

KNOWN_FIXES = {
    "missing_directory": lambda p: Path(p).mkdir(parents=True, exist_ok=True),
    "empty_json_store": lambda p: json.dump({}, open(p, "w")),
    "stale_lockfile": lambda p: Path(p).unlink(missing_ok=True),
}

def diagnose():
    issues = []
    
    # Check critical directories
    critical_dirs = [
        "~/HERMES/logs",
        "~/HERMES/done", 
        "~/HERMES/queue",
        "~/HERMES/swarm_monetizer/earnings",
        "~/HERMES/spark_navigator/backend/runtime_data"
    ]
    for d in critical_dirs:
        expanded = Path(os.path.expanduser(d))
        if not expanded.exists():
            issues.append(("missing_directory", str(expanded)))
    
    # Check essential files
    essential_files = {
        "~/HERMES/queue/tasks.json": "{}",
        "~/HERMES/swarm_monetizer/earnings/log.json": '{"events":[],"total":0.0}'
    }
    for f, default in essential_files.items():
        fp = Path(os.path.expanduser(f))
        if not fp.exists() or fp.stat().st_size == 0:
            issues.append(("empty_json_store", str(fp)))
    
    return issues

def heal(issues):
    healed = []
    for typ, path in issues:
        try:
            KNOWN_FIXES[typ](path)
            healed.append(path)
        except Exception as e:
            print(f"[!] Could not heal {path}: {e}")
    return healed

def loop():
    print("[SELF_HEALER] Starting continuous monitoring...")
    while True:
        problems = diagnose()
        if problems:
            fixes = heal(problems)
            ts = datetime.now().strftime("%H:%M:%S")
            msg = f"[{ts}] Healed {len(fixes)} issues: {fixes}"
            print(msg)
            with open(BASE/"logs"/"healer.log", "a") as lg:
                lg.write(msg + "\n")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    loop()
