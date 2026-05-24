#!/usr/bin/env python3
"""
GOX.PRO Autonomous Orchestra Runner
Run once. It handles everything in queue.
Add tasks via ~/HERMES/TASK_QUEUE.txt
"""
import os
import subprocess
import time
import json
from datetime import datetime

BASE = os.path.expanduser("~/HERMES")
QUEUE_FILE = f"{BASE}/TASK_QUEUE.txt"
DONE_FILE = f"{BASE}/TASK_DONE.txt"
LOG_DIR = f"{BASE}/logs"

os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(f"{LOG_DIR}/orchestra.log", "a") as f:
        f.write(f"[{ts}] {msg}\n")

def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
    return lines

def mark_done(task_line):
    with open(DONE_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {task_line}\n")

def extract_code_from_task(task_str):
    """Parse task string and determine what to execute"""
    
    # Built-in task handlers
    TASKS = {
        "revenue_sweep": lambda: subprocess.run(["python3", f"{BASE}/revenue/orchestrator.py", "--sweep"], cwd=BASE),
        "wallet_setup": lambda: setup_wallets(),
        "domain_monitor_start": lambda: subprocess.Popen(["python3", f"{BASE}/scripts/domain_sniper.py"]),
        "job_bot_launch": lambda: subprocess.Popen(["python3", f"{BASE}/scripts/job_auto_apply.py"]),
        "cron_schedule": lambda: setup_cron(),
    }
    
    # Check if it's a known task key
    task_lower = task_str.lower().replace(" ", "_").replace("-", "_")
    for key, handler in TASKS.items():
        if key in task_lower:
            return handler
    
    # Otherwise treat as shell command
    return lambda: subprocess.run(task_str, shell=True, cwd=BASE)

def setup_wallets():
    log("Setting up wallet addresses...")
    wallets = {}
    
    # Monero (most likely available)
    try:
        result = subprocess.run(["monero-wallet-cli", "--generate-new-wallet", 
                                f"{BASE}/security/xmr_wallet", "--password", "gox_secure"],
                               capture_output=True, text=True, timeout=30)
        log("Monero wallet initiated")
    except:
        log("Monero CLI not installed - skip")
    
    # Save placeholder addresses
    wallet_file = f"{BASE}/security/wallet_addresses.txt"
    with open(wallet_file, "w") as f:
        f.write("# GOX.PRO Collection Addresses\n")
        f.write("# Update manually with real addresses\n")
        f.write("BTC_PLACEHOLDER=your_btc_address_here\n")
        f.write("ETH_PLACEHOLDER=your_eth_address_here\n")
        f.write("XMR_PLACEHOLDER=your_xmr_address_here\n")
        f.write("SOL_PLACEHOLDER=your_sol_address_here\n")
    log(f"Wallet template saved to {wallet_file}")

def setup_cron():
    log("Setting up scheduled jobs...")
    cron_jobs = """
# GOX.PRO Scheduled Tasks
0 */4 * * * cd ~/HERMES && python3 revenue/orchestrator.py --quick >> logs/auto_sweep.log 2>&1
0 9 * * * cd ~/HERMES && python3 scripts/opportunity_scanner.py >> logs/scanner.log 2>&1
""" 
    with open("/tmp/gox_crontab", "w") as f:
        subprocess.run(["crontab", "-l"], stdout=f, stderr=subprocess.DEVNULL)
        f.write(cron_jobs)
    subprocess.run(["crontab", "/tmp/gox_crontab"])
    log("Cron jobs scheduled")

def main():
    log("=" * 50)
    log("GOX.ORCHESTRA STARTED")
    log("=" * 50)
    log(f"Watching: {QUEUE_FILE}")
    log("Add tasks by appending lines to TASK_QUEUE.txt")
    log("")
    
    consecutive_empty = 0
    
    while True:
        tasks = load_queue()
        
        if not tasks:
            consecutive_empty += 1
            if consecutive_empty >= 120:  # ~2 min idle
                log("Queue empty. Waiting for tasks...")
            time.sleep(1)
            continue
        
        consecutive_empty = 0
        
        # Pop first task
        task = tasks.pop(0)
        
        # Rewrite queue without this task
        with open(QUEUE_FILE, "w") as f:
            f.write("\n".join(tasks))
        
        log(f">>> EXECUTING: {task[:80]}{'...' if len(task)>80 else ''}")
        
        try:
            handler = extract_code_from_task(task)
            result = handler()
            
            if hasattr(result, 'returncode'):
                if result.returncode == 0:
                    log(f"SUCCESS: {task[:50]}")
                    mark_done(task)
                else:
                    log(f"FAILED (exit {result.returncode}): {task[:50]}")
                    # Put back in queue for retry
                    with open(QUEUE_FILE, "a") as f:
                        f.write(f"\n{task} # RETRY_NEEDED")
            else:
                log(f"STARTED (background): {task[:50]}")
                
        except Exception as e:
            log(f"ERROR: {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
