#!/usr/bin/env python3
import json
import os
from datetime import datetime

BASE = os.path.expanduser("~/HERMES")
DATA = f"{BASE}/data/results.json"
LOG = f"{BASE}/logs/auto.log"
REPORT = f"{BASE}/logs/latest_status.txt"

def count_opps():
    if os.path.exists(DATA):
        with open(DATA) as f:
            return len(json.load(f))
    return 0

def estimate_total():
    if not os.path.exists(DATA):
        return 0
    with open(DATA) as f:
        items = json.load(f)
    return sum(i.get("priority", 0)//10 for i in items[:20])

def check_uptime():
    if os.path.exists(LOG):
        with open(LOG) as f:
            lines = f.readlines()
        return len(lines)
    return 0

report = f"""
{'='*50}
GOX.PRO STATUS REPORT
{datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*50}

OPPORTUNITIES FOUND: {count_opps()}
ESTIMATED VALUE: ~${estimate_total()}
SCANS COMPLETED: {check_uptime()}

SYSTEM: {'ACTIVE' if count_opps() > 0 else 'WAITING'}

NEXT ACTIONS:
- Review top opportunities
- Complete pending signups
- Check for new high-value entries

Run 'gox' to refresh manually.
{'='*50}
"""

with open(REPORT, 'w') as f:
    f.write(report)

print(report)
