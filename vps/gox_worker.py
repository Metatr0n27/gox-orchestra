#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import time
from datetime import datetime, timezone

REPO = pathlib.Path(os.environ.get("GOX_REPO", "/opt/gox-orchestra"))
STATE = pathlib.Path(os.environ.get("GOX_STATE_DIR", "/var/lib/gox"))
QUEUE = STATE / "queue.jsonl"
DONE = STATE / "done.jsonl"
FAILED = STATE / "failed.jsonl"
HEARTBEAT = STATE / "heartbeat.json"
AUDIT = STATE / "audit.log"
POLL_SECONDS = int(os.environ.get("GOX_POLL_SECONDS", "5"))
MAX_RETRIES = int(os.environ.get("GOX_MAX_RETRIES", "3"))

ALLOWED_SCRIPTS = {
    "status_report": "status_report.py",
    "show_top": "show_top.py",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def append_json(path, payload):
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def log(message):
    line = f"{now()} {message}"
    print(line, flush=True)
    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def heartbeat(status="ok", detail=None):
    payload = {"time": now(), "status": status, "repo": str(REPO)}
    if detail:
        payload["detail"] = detail
    HEARTBEAT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_checked(argv, timeout=180):
    result = subprocess.run(
        argv,
        cwd=REPO,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout[-8000:],
        "stderr": result.stderr[-8000:],
    }


def execute(task):
    task_type = task.get("type")
    if task_type == "healthcheck":
        return {
            "returncode": 0,
            "stdout": json.dumps({
                "repo_exists": REPO.exists(),
                "python": os.sys.version.split()[0],
                "state_writable": os.access(STATE, os.W_OK),
            }),
            "stderr": "",
        }
    if task_type == "git_sync":
        return run_checked(["git", "pull", "--ff-only"])
    if task_type == "run_script":
        name = task.get("name")
        relative_path = ALLOWED_SCRIPTS.get(name)
        if not relative_path:
            return {"returncode": 126, "stdout": "", "stderr": f"script not allowed: {name!r}"}
        target = REPO / relative_path
        if not target.is_file():
            return {"returncode": 127, "stdout": "", "stderr": f"missing script: {relative_path}"}
        return run_checked(["python3", str(target)])
    return {"returncode": 125, "stdout": "", "stderr": f"unsupported task type: {task_type!r}"}


def pop_task():
    if not QUEUE.exists():
        return None
    lines = QUEUE.read_text(encoding="utf-8").splitlines()
    if not lines:
        return None
    first = lines[0]
    rest = lines[1:]
    QUEUE.write_text("\n".join(rest) + ("\n" if rest else ""), encoding="utf-8")
    try:
        return json.loads(first)
    except json.JSONDecodeError as exc:
        append_json(FAILED, {"time": now(), "task": first, "error": f"invalid json: {exc}"})
        return None


def main():
    STATE.mkdir(parents=True, exist_ok=True)
    QUEUE.touch(exist_ok=True)
    DONE.touch(exist_ok=True)
    FAILED.touch(exist_ok=True)
    AUDIT.touch(exist_ok=True)
    log("GOX worker started")
    heartbeat()
    last_heartbeat = time.time()

    while True:
        current = time.time()
        if current - last_heartbeat >= 60:
            heartbeat()
            last_heartbeat = current

        task = pop_task()
        if task is None:
            time.sleep(POLL_SECONDS)
            continue

        task.setdefault("id", f"task-{int(time.time() * 1000)}")
        task.setdefault("attempt", 1)
        log(f"executing {task['id']} type={task.get('type')}")
        try:
            result = execute(task)
        except Exception as exc:
            result = {"returncode": 1, "stdout": "", "stderr": repr(exc)}

        record = {"time": now(), "task": task, "result": result}
        if result["returncode"] == 0:
            append_json(DONE, record)
            log(f"completed {task['id']}")
        elif task["attempt"] < MAX_RETRIES:
            task["attempt"] += 1
            append_json(QUEUE, task)
            log(f"retry queued {task['id']} attempt={task['attempt']}")
        else:
            append_json(FAILED, record)
            log(f"failed {task['id']} after {task['attempt']} attempts")


if __name__ == "__main__":
    main()
