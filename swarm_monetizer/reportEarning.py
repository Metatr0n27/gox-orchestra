#!/usr/bin/env python3
"""
Report earnings manually - plays sound, updates totals
Usage: python3 reportEarning.py 15.00 "Coinbase Earn"
"""
import os, json, subprocess, sys
from datetime import datetime

BASE = os.path.expanduser("~/HERMES/swarm_monetizer")
LOG = f"{BASE}/earnings/log.json"
MANIFEST = f"{BASE}/manifest.json"
TARGET = 500.0

def play_chaching():
    """Play cash register sound"""
    subprocess.run('''
paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || \
aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null || \
speaker-test -t sine -f 1200 -l 1 2>/dev/null || \
echo -e "\\007"
''', shell=True, stderr=subprocess.DEVNULL)

def report(amount, source):
    # Load/create log
    try:
        data = json.load(open(LOG))
    except:
        data = {"events": [], "total": 0.0}
    
    # Record event
    event = {
        "amount": float(amount),
        "source": source,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    data["events"].append(event)
    data["total"] += float(amount)
    
    # Save
    json.dump(data, open(LOG, "w"), indent=2)
    
    # Play sound
    play_chaching()
    
    # Display progress
    pct = (data["total"] / TARGET) * 100
    bar_len = int(pct / 5)
    bar = "█" * bar_len + "░" * (20 - bar_len)
    
    print(f"\n{'='*50}")
    print(f"   💰 +${float(amount):.2f} from {source}")
    print(f"   📊 TOTAL: ${data['total']:.2f} / ${TARGET:.0f}")
    print(f"   [{bar}] {pct:.1f}%")
    print(f"{'='*50}\n")
    
    if data["total"] >= TARGET:
        print("🎉🎉🎉 TARGET REACHED! 🎉🎉🎉")
        for _ in range(3):
            play_chaching()
            time.sleep(0.3)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 reportEarning.py AMOUNT [SOURCE]")
        print("Example: python3 reportEarning.py 15.00 'Coinbase'")
        sys.exit(1)
    
    amt = float(sys.argv[1])
    src = sys.argv[2] if len(sys.argv) > 2 else "manual_entry"
    report(amt, src)
