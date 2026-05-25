#!/bin/bash
# Runs every 60 seconds checking component health

INTERVAL=60
LOG_DIR="$HOME/HERMES/spark_infra/logs"
mkdir -p "$LOG_DIR"

while true; do
    STAMP=$(date '+%Y-%m-%d %H:%M:%S')
    REPORT=""
    
    # Check database integrity
    if sqlite3 ~/HERMES/spark_infra/db/spark.db "PRAGMA integrity_check;" 2>/dev/null | grep -q ok; then
        REPORT+="[OK] Database healthy\n"
    else
        REPORT+="[FAIL] Database corrupted!\n"
    fi
    
    # Check API server
    if curl -s localhost:8765/health >/dev/null 2>&1; then
        REPORT+="[OK] API responsive\n"
    else
        REPORT+="[WARN] API unreachable\n"
    fi
    
    # Memory check
    MEM_FREE=$(free -m | awk '/^-/{print $NF}')
    if [ "$MEM_FREE" -lt 100 ]; then
        REPORT+="[WARN] Low memory: ${MEM_FREE}MB free\n"
    fi
    
    # Disk check
    DISK_AVAIL=$(df -h ~ | tail -1 | awk '{print $4}')
    REPORT+="[INFO] Disk avail: ${DISK_AVAIL}\n"
    
    echo -e "[$STAMP]\n$REPORT" >> "$LOG_DIR/heartbeat.log"
    sleep $INTERVAL
done
