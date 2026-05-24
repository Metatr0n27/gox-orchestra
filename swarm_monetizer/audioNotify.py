#!/usr/bin/env python3
"""
Plays satisfying cha-ching sound on earning events
"""
import os, subprocess, json
from datetime import datetime

EARNINGS_LOG = os.path.expanduser("~/HERMES/swarm_monetizer/earnings/log.json")
AUDIO_DIR = os.path.expanduser("~/HERMES/swarm_monetizer/audio")

def ensure_audio():
    """Generate cash register sound effect"""
    snd = f"{AUDIO_DIR}/cash.wav"
    if not os.path.exists(snd):
        # Create beep sequence as WAV (simple synthesis)
        subprocess.run(f'''
sox -n -r 44100 -c 2 {snd} synth 0.3 sine 1200 fade 0.1 0.3 0.1 \
synth 0.2 sine 1600 fade 0.05 0.2 0.05 \
synth 0.4 sine 800 fade 0.1 0.4 0.2 2>/dev/null || \
beep -f 1200 -l 100 -n -f 1600 -l 80 -n -f 800 -l 150 2>/dev/null || \
echo -e '\\a'
''', shell=True)
    return snd

def play_cash_sound(amount=None):
    """Play earning confirmation sound"""
    snd = ensure_audio()
    if os.path.exists(snd):
        subprocess.Popen(['aplay', snd], stderr=subprocess.DEVNULL)
    else:
        subprocess.run('beep -f 1200 -l 100', shell=True, stderr=subprocess.DEVNULL)
    
    if amount:
        log_earning(amount)

def log_earning(amount, source="swarm"):
    """Record earning event"""
    try:
        data = json.load(open(EARNINGS_LOG))
    except:
        data = {"events": [], "total": 0}
    
    event = {
        "amount": float(amount),
        "source": source,
        "timestamp": datetime.now().isoformat()
    }
    data["events"].append(event)
    data["total"] += float(amount)
    json.dump(data, open(EARNINGS_LOG, "w"), indent=2)
    
    print(f"💰 +${float(amount):.2f} | Total: ${data['total']:.2f}")

if __name__ == "__main__":
    import sys
    amt = float(sys.argv[1]) if len(sys.argv) > 1 else 0
    play_cash_sound(amt)
