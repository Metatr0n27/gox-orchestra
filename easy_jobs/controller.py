#!/usr/bin/env python3
import json, os, pathlib, time
from datetime import datetime, timezone

BASE = pathlib.Path('/var/lib/gox/easy_jobs')
INBOX = BASE / 'inbox.jsonl'
READY = BASE / 'ready.jsonl'
HUMAN = BASE / 'human_gates.jsonl'
REJECTED = BASE / 'rejected.jsonl'


def now():
    return datetime.now(timezone.utc).isoformat()


def append(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, sort_keys=True) + '\n')


def effective_hourly(task):
    pay = float(task.get('pay', 0) or 0)
    minutes = max(float(task.get('minutes', 60) or 60), 1)
    return round(pay / minutes * 60, 2)


def route(task):
    task['evaluated_at'] = now()
    task['effective_hourly'] = effective_hourly(task)

    # Easy-job definition: already available, no client-selection wait, legitimate worker eligibility.
    if not task.get('available_now', False):
        task['status'] = 'REJECTED'
        task['reason'] = 'not available now'
        append(REJECTED, task)
        return
    if task.get('requires_client_selection', False):
        task['status'] = 'REJECTED'
        task['reason'] = 'requires client approval/selection first'
        append(REJECTED, task)
        return
    if task.get('prohibited_automation', False):
        task['status'] = 'HUMAN_ONLY'
        task['reason'] = 'platform/task requires registered human performance'
        append(HUMAN, task)
        return
    if task.get('human_required', False):
        task['status'] = 'NEEDS_YOU'
        append(HUMAN, task)
        return

    task['status'] = 'READY'
    task['assigned_chain'] = ['verifier','operator','qa','auditor']
    append(READY, task)


def pop_line(path):
    if not path.exists():
        return None
    lines = path.read_text(encoding='utf-8').splitlines()
    if not lines:
        return None
    path.write_text('\n'.join(lines[1:]) + ('\n' if len(lines) > 1 else ''), encoding='utf-8')
    try:
        return json.loads(lines[0])
    except Exception:
        return None


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    INBOX.touch(exist_ok=True)
    print('GOX easy-jobs controller started', flush=True)
    while True:
        task = pop_line(INBOX)
        if task is None:
            time.sleep(2)
            continue
        route(task)


if __name__ == '__main__':
    main()
