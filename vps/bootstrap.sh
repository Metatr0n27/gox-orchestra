#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Metatr0n27/gox-orchestra.git"
INSTALL_DIR="/opt/gox-orchestra"
STATE_DIR="/var/lib/gox"
WORKER_SERVICE="/etc/systemd/system/gox-worker.service"
CONTROL_SERVICE="/etc/systemd/system/gox-control.service"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash vps/bootstrap.sh"
  exit 1
fi

if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 ca-certificates curl
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y git python3 ca-certificates curl
else
  echo "Unsupported package manager. Install git, curl, and python3 manually."
  exit 2
fi

mkdir -p "$STATE_DIR" "$STATE_DIR/control"

if [ -d "$INSTALL_DIR/.git" ]; then
  git -C "$INSTALL_DIR" fetch --all --prune
  git -C "$INSTALL_DIR" reset --hard origin/main
else
  rm -rf "$INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

chmod +x "$INSTALL_DIR/vps/gox_worker.py" "$INSTALL_DIR/control_plane/controller.py"

cat > "$WORKER_SERVICE" <<'EOF'
[Unit]
Description=GOX persistent task worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Environment=GOX_REPO=/opt/gox-orchestra
Environment=GOX_STATE_DIR=/var/lib/gox
ExecStart=/usr/bin/python3 /opt/gox-orchestra/vps/gox_worker.py
Restart=always
RestartSec=5
WorkingDirectory=/opt/gox-orchestra

[Install]
WantedBy=multi-user.target
EOF

cat > "$CONTROL_SERVICE" <<'EOF'
[Unit]
Description=GOX control plane
After=network-online.target gox-worker.service
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /opt/gox-orchestra/control_plane/controller.py
Restart=always
RestartSec=5
WorkingDirectory=/opt/gox-orchestra

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now gox-worker gox-control
sleep 3

printf '%s\n' '{"id":"bootstrap-health","type":"healthcheck"}' >> "$STATE_DIR/queue.jsonl"
printf '%s\n' '{"id":"bootstrap-route","expected_pay":10,"minutes":10,"confidence":1,"start_now":true,"wait_minutes":0,"human_required":false}' >> "$STATE_DIR/control/inbox.jsonl"
sleep 7

WORKER_ACTIVE="$(systemctl is-active gox-worker || true)"
CONTROL_ACTIVE="$(systemctl is-active gox-control || true)"

echo "gox-worker=$WORKER_ACTIVE"
echo "gox-control=$CONTROL_ACTIVE"

test "$WORKER_ACTIVE" = "active"
test "$CONTROL_ACTIVE" = "active"
test -s "$STATE_DIR/heartbeat.json"
grep -q 'bootstrap-health' "$STATE_DIR/done.jsonl"
grep -q 'bootstrap-route' "$STATE_DIR/control/active.jsonl"

echo
echo "GOX VPS bootstrap VERIFIED."
echo "Worker heartbeat: $STATE_DIR/heartbeat.json"
echo "Worker queue:     $STATE_DIR/queue.jsonl"
echo "Worker done:      $STATE_DIR/done.jsonl"
echo "Worker failures:  $STATE_DIR/failed.jsonl"
echo "Worker audit:     $STATE_DIR/audit.log"
echo "Control inbox:    $STATE_DIR/control/inbox.jsonl"
echo "Control active:   $STATE_DIR/control/active.jsonl"
echo "Human gates:      $STATE_DIR/control/human_gates.jsonl"
echo "Control audit:    $STATE_DIR/control/audit.jsonl"
