#!/usr/bin/env bash
set -euo pipefail
cd /opt/gox-orchestra
git pull --ff-only
install -d -m 0755 /var/lib/gox/easy_jobs
for f in inbox.jsonl ready.jsonl human_gates.jsonl rejected.jsonl; do touch "/var/lib/gox/easy_jobs/$f"; done
cat >/etc/systemd/system/gox-easy-jobs.service <<'EOF'
[Unit]
Description=GOX Easy Jobs Controller
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/gox-orchestra
ExecStart=/usr/bin/python3 /opt/gox-orchestra/easy_jobs/controller.py
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now gox-easy-jobs
sleep 2
systemctl is-active gox-easy-jobs
printf '\nGOX EASY JOBS READY\n'
printf 'Inbox: /var/lib/gox/easy_jobs/inbox.jsonl\n'
printf 'Ready: /var/lib/gox/easy_jobs/ready.jsonl\n'
printf 'Human gates: /var/lib/gox/easy_jobs/human_gates.jsonl\n'
