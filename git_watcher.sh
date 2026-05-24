#!/bin/bash
# Auto-commits changes every 5 minutes
# Run in background: ./git_watcher.sh &

cd ~/HERMES

while true; do
    CHANGES=$(git status --porcelain 2>/dev/null | wc -l)
    
    if [ "$CHANGES" -gt 0 ]; then
        TIMESTAMP=$(date "+%H:%M")
        git add -A
        git commit -m "Auto-sync [$TIMESTAMP]"
        git push origin main 2>/dev/null
        echo "[$TIMESTAMP] Committed $CHANGES changes"
    fi
    
    sleep 300
done
