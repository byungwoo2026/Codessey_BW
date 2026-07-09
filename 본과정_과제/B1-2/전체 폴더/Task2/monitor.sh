#!/usr/bin/env bash

APP_NAME="${APP_NAME:-agent-leak-app}"
LOG_FILE="${LOG_FILE:-./logs/monitor.log}"
INTERVAL="${INTERVAL:-2}"

echo "timestamp,pid,cpu_percent,mem_percent,rss_kb,vsz_kb,state,elapsed" > "$LOG_FILE"

while true; do
  PID=$(pgrep -f "$APP_NAME" | head -n 1)

  if [ -z "$PID" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S'),PROCESS_NOT_FOUND,,,,,," >> "$LOG_FILE"
  else
    ps -p "$PID" -o pid=,%cpu=,%mem=,rss=,vsz=,stat=,etime= \
      | awk -v ts="$(date '+%Y-%m-%d %H:%M:%S')" \
      '{print ts "," $1 "," $2 "," $3 "," $4 "," $5 "," $6 "," $7}' >> "$LOG_FILE"
  fi

  sleep "$INTERVAL"
done