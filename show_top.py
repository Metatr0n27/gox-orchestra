#!/usr/bin/env python3
import json
import os
from datetime import datetime

data_file = os.path.expanduser("~/HERMES/data/results.json")
if not os.path.exists(data_file):
    print("No data yet. Run hunt first.")
    exit()

with open(data_file) as f:
    items = json.load(f)

print("\n" + "="*60)
print("TOP 5 MONEY OPPORTUNITIES - " + datetime.now().strftime("%H:%M"))
print("="*60)

for i, item in enumerate(items[:5], 1):
    amt = item.get("amount", 0)
    if amt and amt > 100:
        amt_display = f"${amt:.0f}"
    else:
        amt_display = "~$" + str(item.get("priority", 0)//10)
    
    print(f"\n{i}. [{item['source']}] {amt_display}")
    print(f"   {item['title'][:55]}...")
    print(f"   Link: {item['link']}")

print("\n" + "="*60)
