from flask import Flask,jsonify,request
import json,os,subprocess
from pathlib import Path
app=Flask(__name__);B=Path.home()/\"HERMES\"
@app.route(\"/health\")\ndef h():return{\"ok\":True}
@app.route(\"/earnings\",methods=[\"GET\",\"POST\"])\ndef e():
 if request.method==\"POST\":
  d=request.json;a=d.get(\"amount\",0);s=d.get(\"source\",\"api\")
  subprocess.run([\"python3\",str(B/\"swarm_monetizer\"/\"reportEarning.py\"),str(a),s])
  return{\"added\":a}
 return json.load(open(B/\"swarm_monetizer\"/\"earnings\"/\"log.json\"))if(B/\"swarm_monetizer\"/\"earnings\"/\"log.json\").exists()else{}
@app.route(\"/spark/rec\")\ndef sr():
 r=subprocess.run([\"python3\",str(B/\"spark_navigator\"/\"backend\"/\"orchestrator.py\"),\"rec\"],capture_output=True,text=True)
 return r.stdout
if __name__==\"__main__\":app.run(host=\"0.0.0.0\",port=8765)
