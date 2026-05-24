#!/usr/bin/env python3
"""
GOX.Visual Dashboard - Real-time orchestra monitor
Run: python3 dashboard.py
"""

import os, json, time, subprocess
from datetime import datetime

BASE = os.path.expanduser("~/HERMES")
REFRESH = 2

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def box(title, content, width=52):
    lines = content.split('\n')
    top = f"╭{'─'*(width-2)}╮"
    mid = '\n'.join([f"│ {line.ljust(width-4)} │" for line in lines])
    bot = f"╰{'─'*(width-2)}╯"
    return f"{top}\n│ 🎻 {title.ljust(width-6)} │\n{mid}\n{bot}"

def get_stats():
    done = len([f for f in os.listdir(f"{BASE}/done") if f.endswith('.json')]) if os.path.exists(f"{BASE}/done") else 0
    fail = len([f for f in os.listdir(f"{BASE}/failed") if f.endswith('.json')]) if os.path.exists(f"{BASE}/failed") else 0
    fix = len([f for f in os.listdir(f"{BASE}/fixed") if f.endswith('.json')]) if os.path.exists(f"{BASE}/fixed") else 0
    
    try:
        q = json.load(open(f"{BASE}/queue/tasks.json"))
        pend = len(q.get('pending', []))
    except:
        pend = 0
    
    return done, fail, fix, pend

def get_recent_logs(n=5):
    logfile = f"{BASE}/logs/activity.log"
    if not os.path.exists(logfile):
        return ["Waiting for activity..."]
    
    result = subprocess.run(['tail', '-n', str(n), logfile], capture_output=True, text=True)
    return result.stdout.strip().split('\n') if result.stdout else ["Idle"]

def render():
    clear()
    
    done, fail, fix, pend = get_stats()
    recent = get_recent_logs(6)
    
    # Header
    print("\n" + "="*54)
    print("         🎻 GOX.ORCHESTRA CONTROL CENTER 🎻")
    print("="*54)
    print(f"          {datetime.now():%Y-%m-%d %H:%M:%S}")
    print()
    
    # Stats boxes
    stats_content = f"""✓ Completed: {done}
⟳ Processing: {pend}
⚠ Issues: {fail}
⊘ Blocked: {fix}"""
    print(box("METRICS", stats_content))
    print()
    
    # Progress bar
    total = done + fail + fix + pend
    if total > 0:
        pct = int((done / total) * 100)
        filled = int(pct / 5)
        bar = "█" * filled + "░" * (20 - filled)
        print(f"  Progress: [{bar}] {pct}%")
    print()
    
    # Recent activity
    log_box = '\n'.join([r[:48] for r in recent])
    print(box("RECENT ACTIVITY", log_box))
    print()
    
    # Agents status
    agents = subprocess.run(['pgrep', '-fa', 'agent_'], capture_output=True, text=True)
    agent_lines = agents.stdout.strip().split('\n') if agents.stdout else ['None running']
    ag_box = '\n'.join([a.split()[1] if len(a.split())>1 else a for a in agent_lines][:3])
    print(box("ACTIVE AGENTS", ag_box))
    print()
    
    print("  Press Ctrl+C to exit | Refresh: {}s".format(REFRESH))
    print()

def main():
    print("Starting dashboard...")
    try:
        while True:
            render()
            time.sleep(REFRESH)
    except KeyboardInterrupt:
        print("\nDashboard closed.")

if __name__ == "__main__":
    main()
