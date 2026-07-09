#!/usr/bin/env bash
# =====================================================================
# watchdog.sh  —  과점유 방지 정책 (Resource Over-Occupancy Watchdog)
#
#   - 대상 프로세스의 CPU / 메모리 사용량을 주기적으로 감시한다.
#   - 임계치를 연속으로 초과하면 SIGTERM(graceful)으로 종료를 요청한다.
#   - 유예시간 안에 종료되지 않으면 SIGKILL로 강제 종료(escalation)한다.
#   - 모든 판단과 조치를 타임스탬프 로그로 기록한다.
# =====================================================================
set -euo pipefail

# ---------- 설정값 (환경변수로 덮어쓰기 가능) ----------
TARGET="${1:-agent-app}"                 # 감시 대상 프로세스 이름(comm)
CPU_LIMIT="${CPU_LIMIT:-80.0}"           # CPU 사용률 임계치 (%)
MEM_LIMIT="${MEM_LIMIT:-500}"            # 메모리 사용량 임계치 (MB)
VIOLATION_MAX="${VIOLATION_MAX:-3}"      # 연속 위반 허용 횟수 (이만큼 넘으면 조치)
INTERVAL="${INTERVAL:-2}"                # 점검 주기 (초)
GRACE="${GRACE:-10}"                     # SIGTERM 후 정상 종료를 기다리는 시간 (초)
LOG_FILE="${LOG_FILE:-./watchdog.log}"   # 로그 파일 경로

declare -A violations                    # PID별 연속 위반 횟수 저장

log() {                                  # 공통 로그 함수: 화면 + 파일 동시 기록
  local level="$1"; shift
  printf '%s [%-5s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$level" "$*" | tee -a "$LOG_FILE"
}

log INFO "Watchdog 시작 — target=$TARGET, CPU>${CPU_LIMIT}%, MEM>${MEM_LIMIT}MB, 허용=${VIOLATION_MAX}회, 주기=${INTERVAL}s"

while true; do
  # pid / %cpu / rss(KB) / comm 을 한 줄씩 읽어서 대상만 필터링
  while read -r pid cpu rss cmd; do
    [ -z "${pid:-}" ] && continue
    mem_mb=$(( rss / 1024 ))
    # awk로 실수 비교 (CPU%는 소수점이라 bash 산술로는 비교 불가)
    over_cpu=$(awk -v c="$cpu" -v l="$CPU_LIMIT" 'BEGIN{print (c>l)?1:0}')
    over_mem=$(( mem_mb > MEM_LIMIT ? 1 : 0 ))

    if [ "$over_cpu" -eq 1 ] || [ "$over_mem" -eq 1 ]; then
      violations[$pid]=$(( ${violations[$pid]:-0} + 1 ))
      log WARN "과점유 감지 PID=$pid ($cmd) cpu=${cpu}% mem=${mem_mb}MB — 위반 ${violations[$pid]}/${VIOLATION_MAX}"

      if [ "${violations[$pid]}" -ge "$VIOLATION_MAX" ]; then
        log ERROR "임계치 연속 초과 → PID=$pid 에 SIGTERM 전송 (cpu=${cpu}% mem=${mem_mb}MB)"
        if ! kill -TERM "$pid" 2>/dev/null; then
          log WARN "PID=$pid 이미 종료됨"; unset 'violations[$pid]'; continue
        fi

        # graceful 종료 대기
        waited=0
        while kill -0 "$pid" 2>/dev/null && [ "$waited" -lt "$GRACE" ]; do
          sleep 1; waited=$((waited+1))
        done

        if kill -0 "$pid" 2>/dev/null; then
          log ERROR "PID=$pid 가 ${GRACE}s 동안 SIGTERM 무시 → SIGKILL로 강제 종료"
          kill -KILL "$pid" 2>/dev/null || true
        else
          log INFO "PID=$pid SIGTERM으로 ${waited}s 만에 정상 종료 완료"
        fi
        unset 'violations[$pid]'
      fi
    else
      # 정상 범위로 돌아오면 위반 카운터 리셋 (일시적 스파이크 무시)
      if [ -n "${violations[$pid]:-}" ]; then
        log INFO "PID=$pid 정상화 — 위반 카운터 초기화"
        unset 'violations[$pid]'
      fi
    fi
  done < <(ps -eo pid=,pcpu=,rss=,comm= | awk -v t="$TARGET" '$4==t {print $1, $2, $3, $4}')

  sleep "$INTERVAL"
done
