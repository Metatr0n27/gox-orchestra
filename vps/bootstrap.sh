#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Metatr0n27/gox-orchestra.git"
INSTALL_DIR="/opt/gox-orchestra"
STATE_DIR="/var/lib/gox"
SERVICE_FILE="/etc/systemd/system/gox-worker.service"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash vps/bootstrap.sh"
  exit 1
fi

if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 ca-certificates
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y git python3 ca-certificates
else
  echo "Unsupported package manager. Install git and python3 manually."
  exit 2
fi

mkdir -p "$STATE_DIR"

if [ -d "$INSTALL_DIR/.git" ]; then
  git -C "$INSTALL_DIR" pull --ff-only
else
  rm -rf "$INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

chmod +x "$INSTALL_DIR/vps/gox_worker.py"

cat > "$SERVICE_FILE" <<'EOF'
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

systemctl daemon-reload
systemctl enable --now gox-worker
sleep 2
systemctl --no-pager --full status gox-worker || true

echo
echo "GOX worker bootstrap complete."
echo "Heartbeat: $STATE_DIR/heartbeat.json"
echo "Queue:     $STATE_DIR/queue.jsonl"
echo "Done log:  $STATE_DIR/done.jsonl"
echo "Failures:  $STATE_DIR/failed.jsonl"
echo "Audit:     $STATE_DIR/audit.log"
