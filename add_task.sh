#!/bin/bash
# Add task to GOX Orchestra queue
# Usage: ./add_task.sh "id" "description" "command"

ID="${1:-auto_$(date +%s)}"
DESC="$2"
CMD="$3"

if [ -z "$CMD" ]; then
    CMD="$1"
    DESC="$1"
fi

python3 << PYSCRIPT
import json, os
from datetime import datetime

qpath = os.path.expanduser("~/HERMES/queue/tasks.json")
os.makedirs(os.path.dirname(qpath), exist_ok=True)

try:
    data = json.load(open(qpath))
except:
    data = {"pending": [], "updated": "now"}

task = {
    "id": "${ID}",
    "desc": """${DESC}""",
    "command": """${CMD}""",
    "added": datetime.now().isoformat(),
    "priority": 5,
    "attempts": 0,
    "max_attempts": 3
}

data["pending"].append(task)
json.dump(data, open(qpath, "w"), indent=2)
print(f"+ Added [{task['id']}]: {task['desc'][:50]}")
PYSCRIPT
