#!/bin/bash

# 1. 설정 및 경로 정의
AGENT_HOME="/home/agent-admin/agent-app"
LOG_FILE="/var/log/agent-app/monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 임계치 설정 (요구사항 반영)
CPU_LIMIT=80
MEM_LIMIT=10
DISK_LIMIT=80

# 2. 상태 점검 (프로세스 및 포트)
PROC_DEV=$(pgrep -f "agent-dev" | wc -l)
PROC_CORE=$(pgrep -f "agent-core" | wc -l)
PORT_CHECK=$(netstat -lnpt | grep ":15034" | wc -l)

# 3. 리소스 사용량 계산
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
MEM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
DISK_USAGE=$(df / | grep / | awk '{print $5}' | sed 's/%//')

# 4. 경고 판단
STATUS="OK"
if (( $(echo "$CPU_USAGE > $CPU_LIMIT" | bc -l) )); then STATUS="WARNING(CPU)"; fi
if (( $(echo "$MEM_USAGE > $MEM_LIMIT" | bc -l) )); then STATUS="WARNING(MEM)"; fi
if (( $(echo "$DISK_USAGE > $DISK_LIMIT" | bc -l) )); then STATUS="WARNING(DISK)"; fi

# 5. 결과 출력 및 로그 기록
PRINT_CPU=$(printf "%.1f" $CPU_USAGE)
PRINT_MEM=$(printf "%.1f" $MEM_USAGE)

LOG_MSG="[$TIMESTAMP] [$STATUS] CPU:${PRINT_CPU}% | MEM:${PRINT_MEM}% | DISK:${DISK_USAGE}%"

# 로그 파일에 기록 (누적)
echo "$LOG_MSG" >> "$LOG_FILE"