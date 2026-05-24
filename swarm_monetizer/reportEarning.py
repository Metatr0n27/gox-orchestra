#!/usr/bin/env python3
"""Log earnings with audio confirmation."""
import os, json, subprocess, sys
from datetime import datetime

LOG = os.path.expanduser("~/HERMES/swarm_monetizer/earnings/log.json")
TARGET = 500.0

def play_chime():
    try:
        import pygame
        pygame.mixer.init()
        freq, dur = 880, 150
        samp = int(44100 * dur / 1000)
        buf = bytes([128 + int(127 * __import__('math').sin(2 * 3.14159 * freq * i / 44100)) for i in range(samp)])
        snd = pygame.mixer.Sound(buffer=buf)
        snd.play()
        pygame.time.wait(dur)
    except:
        subprocess.run('paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || speaker-test -t sine -f 1200 -l 1 2>/dev/null', shell=True, stderr=subprocess.DEVNULL)

def report(amount, source="manual"):
    try:
        data = json.load(open(LOG))
    except:
        data = {"events": [], "total": 0.0}
    
    data["events"].append({"amount": float(amount), "source": source, "time": datetime.now().isoformat()})
    data["total"] += float(amount)
    json.dump(data, open(LOG, "w"), indent=2)
    
    play_chime()
    
    pct = min(100, (data["total"] / TARGET) * 100)
    filled = int(pct / 5)
    bar = "█" * filled + "░" * (20 - filled)
    
    print(f"\n{'='*50}")
    print(f"   💰 +${float(amount):.2f} ← {source}")
    print(f"   📊 TOTAL: ${data['total']:.2f} / ${TARGET:.0f}")
    print(f"   [{bar}] {pct:.1f}%")
    print(f"{'='*50}\n")
    
    if data["total"] >= TARGET:
        print("🎯 TARGET REACHED!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 reportEarning.py AMOUNT [SOURCE]")
        sys.exit(1)
    report(float(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "entry")
