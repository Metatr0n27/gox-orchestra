#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/opt/gox-orchestra"
STATE_DIR="/var/lib/gox"
CONTROL_DIR="$STATE_DIR/control"
FAIL=0

check() {
  local label="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    printf 'PASS  %s\n' "$label"
  else
    printf 'FAIL  %s\n' "$label"
    FAIL=1
  fi
}

printf 'GOX VPS PREFLIGHT\n'
printf '=================\n'
printf 'host: %s\n' "$(hostname)"
printf 'time: %s\n' "$(date -Is)"
printf 'user: %s\n' "$(id -un)"
printf '\n'

check "root privileges" test "$(id -u)" -eq 0
check "python3 installed" command -v python3
check "git installed" command -v git
check "curl installed" command -v curl
check "systemd available" command -v systemctl
check "network DNS" getent hosts github.com
check "HTTPS to GitHub" curl -fsSI --max-time 10 https://github.com
check "disk has >=1GB free" bash -c '[ "$(df -Pk / | awk "NR==2 {print \$4}")" -ge 1048576 ]'
check "repo installed" test -d "$INSTALL_DIR/.git"
check "worker file exists" test -f "$INSTALL_DIR/vps/gox_worker.py"
check "controller file exists" test -f "$INSTALL_DIR/control_plane/controller.py"
check "team manifest exists" test -f "$INSTALL_DIR/control_plane/team_manifest.json"
check "state directory writable" bash -c "mkdir -p '$STATE_DIR' '$CONTROL_DIR' && touch '$STATE_DIR/.write_test' && rm -f '$STATE_DIR/.write_test'"

if systemctl list-unit-files gox-worker.service >/dev/null 2>&1; then
  check "gox-worker active" systemctl is-active --quiet gox-worker
else
  printf 'WAIT  gox-worker not installed yet\n'
fi

if systemctl list-unit-files gox-control.service >/dev/null 2>&1; then
  check "gox-control active" systemctl is-active --quiet gox-control
else
  printf 'WAIT  gox-control not installed yet\n'
fi

printf '\nBLOCKER SUMMARY\n'
printf '===============\n'
if [ -s "$CONTROL_DIR/human_gates.jsonl" ]; then
  tail -20 "$CONTROL_DIR/human_gates.jsonl"
else
  printf 'No queued human gates on this VPS.\n'
fi

printf '\nRECENT FAILURES\n'
printf '===============\n'
if [ -s "$STATE_DIR/failed.jsonl" ]; then
  tail -20 "$STATE_DIR/failed.jsonl"
else
  printf 'No worker failures recorded.\n'
fi

if [ "$FAIL" -eq 0 ]; then
  printf '\nPREFLIGHT RESULT: PASS\n'
else
  printf '\nPREFLIGHT RESULT: BLOCKED\n'
fi

exit "$FAIL"
