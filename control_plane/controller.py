#!/usr/bin/env python3
"""GOX Control Plane: deterministic task routing and blocker escalation."""
import json
import pathlib
import time
from datetime import datetime, timezone

STATE = pathlib.Path("/var/lib/gox/control")
INBOX = STATE / "inbox.jsonl"
ACTIVE = STATE / "active.jsonl"
HUMAN = STATE / "human_gates.jsonl"
AUDIT = STATE / "audit.jsonl"


def now():
    return datetime.now(timezone.utc).isoformat()


def append(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def score(task):
    """Favor immediate, short, paid work over speculative waiting."""
    pay = float(task.get("expected_pay", 0) or 0)
    minutes = max(float(task.get("minutes", 60) or 60), 1)
    wait = float(task.get("wait_minutes", 0) or 0)
    confidence = min(max(float(task.get("confidence", 0.5) or 0.5), 0), 1)
    immediate_bonus = 100 if task.get("start_now") else 0
    return round((pay / minutes * 60 * confidence) + immediate_bonus - (wait / 10), 3)


def route(task):
    task["score"] = score(task)
    task["routed_at"] = now()
    if task.get("human_required"):
        gate = {
            "task_id": task.get("id"),
            "status": "USER ACTION",
            "reason": task.get("human_reason", "mandatory human action"),
            "url": task.get("url"),
            "instruction": task.get("human_instruction"),
            "created_at": now(),
        }
        append(HUMAN, gate)
        append(AUDIT, {"event":"human_gate", **gate})
        return gate
    task["status"] = "READY"
    task["assigned_chain"] = ["verifier", "operator", "qa", "auditor"]
    append(ACTIVE, task)
    append(AUDIT, {"event":"routed", "task_id":task.get("id"), "score":task["score"], "time":now()})
    return task


def pop_line(path):
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return None
    path.write_text("\n".join(lines[1:]) + ("\n" if len(lines) > 1 else ""), encoding="utf-8")
    return json.loads(lines[0])


def main():
    STATE.mkdir(parents=True, exist_ok=True)
    INBOX.touch(exist_ok=True)
    while True:
        task = pop_line(INBOX)
        if task is None:
            time.sleep(3)
            continue
        try:
            route(task)
        except Exception as exc:
            append(AUDIT, {"event":"controller_error", "error":repr(exc), "task":task, "time":now()})


if __name__ == "__main__":
    main()
