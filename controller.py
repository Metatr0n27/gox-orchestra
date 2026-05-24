#!/usr/bin/env python3
"""
GOX.PRO Unified Controller
Manages dual-stream revenue operations
"""
import subprocess
import threading
import time
import json
import os
from datetime import datetime

BASE = os.path.expanduser("~/HERMES")
STATE_FILE = f"{BASE}/controller_state.json"

class RevenueController:
    def __init__(self):
        self.streams = {
            "referrals": {"active": False, "interval": 1800},
            "jobs": {"active": False, "interval": 7200}
        }
        self.running = True
        self._load_state()
    
    def _load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                self.state = json.load(f)
        else:
            self.state = {"earnings": 0, "completed_ops": [], "started": datetime.now().isoformat()}
    
    def _save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def referral_cycle(self):
        """Process referral signups"""
        while self.streams["referrals"]["active"]:
            print(f"[REFERRALS] Starting cycle @ {datetime.now().strftime('%H:%M:%S')}")
            
            # Load targets from hunt results
            results_path = f"{BASE}/data/results.json"
            if os.path.exists(results_path):
                with open(results_path) as f:
                    opportunities = json.load(f)[:5]
                
                for opp in opportunities:
                    print(f"  Processing: {opp['title'][:50]}...")
                    # Placeholder for actual signup automation
                    
            self.state["completed_ops"].append({
                "stream": "referrals",
                "time": datetime.now().isoformat(),
                "count": len(opportunities) if os.path.exists(results_path) else 0
            })
            self._save_state()
            
            time.sleep(self.streams["referrals"]["interval"])
    
    def job_application_cycle(self):
        """Submit IT job applications"""
        platforms = ["linkedin", "indeed", "remoteok", "weworkremotely"]
        
        while self.streams["jobs"]["active"]:
            print(f"[JOBS] Application burst @ {datetime.now().strftime('%H:%M:%S')}")
            
            # Generate fresh persona for applications
            result = subprocess.run(
                ["python3", f"{BASE}/modules/persona/generator.py"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print("  Generated applicant identity")
                # Placeholder for job board submissions
            
            self.state["completed_ops"].append({
                "stream": "jobs",
                "time": datetime.now().isoformat(),
                "platforms_checked": len(platforms)
            })
            self._save_state()
            
            time.sleep(self.streams["jobs"]["interval"])
    
    def start_stream(self, stream_name):
        if stream_name in self.streams:
            self.streams[stream_name]["active"] = True
            thread = threading.Thread(target=getattr(self, f"{stream_name}_cycle"))
            thread.daemon = True
            thread.start()
            print(f"[STARTED] {stream_name.upper()} stream")
    
    def stop_stream(self, stream_name):
        if stream_name in self.streams:
            self.streams[stream_name]["active"] = False
            print(f"[STOPPED] {stream_name.upper()} stream")
    
    def status(self):
        uptime = datetime.now() - datetime.fromisoformat(self.state["started"])
        return {
            "uptime_hours": round(uptime.total_seconds() / 3600, 2),
            "total_operations": len(self.state["completed_ops"]),
            "estimated_earnings": self.state["earnings"],
            "streams_active": [k for k,v in self.streams.items() if v["active"]]
        }

if __name__ == "__main__":
    ctrl = RevenueController()
    
    print("=" * 50)
    print("GOX.PRO CONTROLLER INITIALISING")
    print("=" * 50)
    
    # Start both streams
    ctrl.start_stream("referrals")
    time.sleep(2)
    ctrl.start_stream("jobs")
    
    # Monitor loop
    try:
        while True:
            time.sleep(300)
            stats = ctrl.status()
            print(f"\n[STATUS] Uptime: {stats['uptime_hours']}hrs | "
                  f"Ops: {stats['total_operations']} | "
                  f"Earnings: ${stats['estimated_earnings']}")
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping all streams...")
        ctrl.stop_stream("referrals")
        ctrl.stop_stream("jobs")
