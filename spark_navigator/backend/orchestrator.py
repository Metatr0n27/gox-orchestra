#!/usr/bin/env python3
import json,os
from pathlib import Path
from datetime import datetime
D=Path.home()/\"HERMES\"/\"spark_navigator\"/\"backend\"/\"runtime_data\"
D.mkdir(parents=True,exist_ok=True)
class Orchestrator:
 def __init__(self):self.o=[];self.e=0
 def add(self,b):
  b[\"rx\"]=datetime.now().isoformat();self.o.append(b);return b
 def recommend(self):
  if not self.o:return{\"action\":\"await\",\"msg\":\"No orders yet\"}
  return{\"next\":self.o[-1]} if self.o else{}
 def deliver(self,i,t=None):
  for x in self.o:
   if x.get(\"id\")==i:x[\"status\"]=\"done\";self.e+=t or 0
 def summary(self):return{\"count\":len(self.o),\"earnings\":self.e}
O=Orchestrator()
if __name__==\"__main__\":
 import sys;c=sys.argv[1]if len(sys.argv)>1 else \"status\"
 if c==\"add\":print(json.dumps(O.add(json.loads(sys.argv[2])),indent=2))
 elif c==\"rec\":print(json.dumps(O.recommend(),indent=2))
 elif c==\"deliver\":O.deliver(sys.argv[2],float(sys.argv[3])if len(sys.argv)>3 else None)
 else:print(f\"Buffer:{len(O.o)} Earned:${O.e:.2f}\")
