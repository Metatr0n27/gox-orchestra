#!/usr/bin/env python3
import os,time
from pathlib import Path
def check():
 dirs=[\"~/HERMES/logs\",\"~/HERMES/done\",\"~/HERMES/queue\",\"~/HERMES/swarm_monetizer/earnings\"]
 for d in dirs:
  p=Path(os.path.expanduser(d))
  if not p.exists():p.mkdir(parents=True);print(f\"Fixed: {d}\")
while 1:check();time.sleep(60)
