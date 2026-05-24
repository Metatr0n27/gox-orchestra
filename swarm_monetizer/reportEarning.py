#!/usr/bin/env python3
import os,json,sys,subprocess
from datetime import datetime
LOG=os.path.expanduser("~/HERMES/swarm_monetizer/earnings/log.json")
def chime():subprocess.run('paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null||speaker-test -t sine -f 1200 -l 1 2>/dev/null',shell=True,stderr=subprocess.DEVNULL)
def report(a,s="manual"):
 d=json.load(open(LOG)) if os.path.exists(LOG) else {"events":[],"total":0}
 d["events"].append({"amount":float(a),"source":s,"time":datetime.now().isoformat()})
 d["total"]+=float(a)
 json.dump(d,open(LOG,"w"),indent=2)
 chime();p=min(100,(d["total"]/500)*100);b="█"*int(p/5)+"░"*(20-int(p/5));print(f"\n💰 +${float(a):.2f} ← {s}\n📊 ${d['total']:.2f}/$500\n[{b}] {p:.0f}%\n")
if __name__=="__main__":report(float(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else "entry")
