# monitor.sh 스크립트 완전 초보자 가이드
## (시스템 관제 자동화 스크립트)

> 이 가이드는 **쉘 스크립트가 처음**인 사람도 monitor.sh 한 줄 한 줄을 이해하고, 직접 작성·수정할 수 있게 풀어 썼습니다.

---

## 📚 목차

1. [시작하기 전에 — 쉘 스크립트가 뭐야?](#0-시작하기-전에--쉘-스크립트가-뭐야)
2. [핵심 용어 미리 알기](#1-핵심-용어-미리-알기)
3. [쉘 스크립트 기본 문법 속성 코스](#2-쉘-스크립트-기본-문법-속성-코스)
4. [monitor.sh가 해야 할 일 (요구사항 분해)](#3-monitorsh가-해야-할-일-요구사항-분해)
5. [전체 코드 (완성본)](#4-전체-코드-완성본)
6. [코드 한 블록씩 뜯어보기](#5-코드-한-블록씩-뜯어보기)
7. [실습 단계 (1 ~ 6)](#6-실습-단계)
8. [자주 만나는 에러와 해결법](#7-자주-만나는-에러와-해결법)
9. [전체 흐름 한눈에 보기](#8-전체-흐름-한눈에-보기)

---

## 0. 시작하기 전에 — 쉘 스크립트가 뭐야?

### 🤔 한 문장으로

**"평소에 손으로 치던 명령어들을 *파일에 모아놓고 자동 실행*하게 만드는 것"** 이에요.

### 🤔 비유로

비유: 매일 아침 출근하면 하는 일이 똑같다고 해보세요.
1. 컴퓨터 켜기
2. 메일 확인
3. 일정 보기
4. 슬랙 열기

이걸 매일 손으로 하지 말고 **"출근모드.sh"** 라는 버튼 하나 누르면 1~4가 자동으로 되는 것 — 그게 쉘 스크립트.

### 🤔 왜 자동화가 필요해?

이번 미션의 monitor.sh가 하는 일:
- 프로세스 살아있나 체크
- 포트 듣고 있나 체크
- CPU/MEM/DISK 사용률 측정
- 임계값 초과 시 경고
- 로그 기록

이걸 **매분마다** 손으로 하라고 하면? 진짜 못 함. 그래서 자동화.

> 💡 운영 엔지니어의 격언: **"사람의 손이 닿는 순간 그것은 시한폭탄이다."** 자동화는 사람 실수를 줄이고 일관성을 보장해요.

---

## 1. 핵심 용어 미리 알기

| 용어 | 비유 | 진짜 의미 |
|---|---|---|
| **Shebang** (`#!/bin/bash`) | 사용설명서 첫 줄 | 어떤 인터프리터로 실행할지 명시 |
| **변수** | 메모지 | 값을 저장하는 이름 |
| **`$변수명`** | 메모 내용 꺼내기 | 변수의 값 참조 |
| **`$(명령어)`** | 명령어 결과를 변수에 담기 | Command Substitution |
| **`if [ 조건 ]; then ... fi`** | "만약 ~라면 ~한다" | 조건문 |
| **`exit 0` / `exit 1`** | "정상 퇴근" / "사고 후 퇴근" | 종료 코드 (0=성공, 0이외=실패) |
| **`>>` vs `>`** | 추가 vs 덮어쓰기 | 파일에 출력 방식 |
| **파이프 `\|`** | 컨베이어 벨트 | 앞 명령 결과를 뒤 명령에 전달 |
| **`grep`** | 형광펜 | 패턴 찾기 |
| **`awk`** | 표 가공기 | 열/행 단위 데이터 처리 |
| **`/dev/null`** | 휴지통 | 출력을 버리는 특수 파일 |

---

## 2. 쉘 스크립트 기본 문법 속성 코스

이번 monitor.sh에 쓰일 문법만 빠르게.

### 📝 변수 선언 & 사용

```bash
NAME="agent_app"          # 선언 (= 양옆에 공백 X)
echo $NAME                # 사용 → agent_app
echo "${NAME}.py"         # 안전한 사용 (중괄호) → agent_app.py
```

> ⚠️ `=` 양옆에 공백 넣으면 안 돼요! `NAME = "..."`은 에러.

### 📝 명령어 결과를 변수에 담기

```bash
TODAY=$(date '+%Y-%m-%d')      # 명령어 실행 결과를 변수에
echo "오늘은 $TODAY"
```

### 📝 조건문

```bash
if [ "$NAME" = "agent_app" ]; then
    echo "맞아"
else
    echo "달라"
fi
```

자주 쓰는 조건:

| 표현 | 의미 |
|---|---|
| `[ -z "$VAR" ]` | 변수가 비어있다 |
| `[ -n "$VAR" ]` | 변수에 값이 있다 |
| `[ -f "파일" ]` | 파일이 존재한다 |
| `[ -d "폴더" ]` | 폴더가 존재한다 |
| `[ "$A" = "$B" ]` | 문자열 같다 |
| `[ "$A" -gt "$B" ]` | A > B (숫자 비교) |
| `[ "$A" -lt "$B" ]` | A < B |
| `[ "$A" -ge "$B" ]` | A ≥ B |

### 📝 종료 코드

```bash
exit 0    # 성공
exit 1    # 실패
```

다른 프로그램/스크립트가 이 스크립트의 결과를 *판단*할 수 있게 해줘요. cron도 이 코드로 성공/실패 판단.

### 📝 출력 리다이렉션

```bash
echo "hello" > file.txt       # 파일 덮어쓰기
echo "hello" >> file.txt      # 파일에 추가
echo "hello" 2> error.txt     # 에러만 파일로
echo "hello" 2>&1             # 에러를 표준출력에 합치기
echo "hello" > /dev/null      # 출력 버리기
echo "hello" &> /dev/null     # 표준출력 + 에러 모두 버리기
```

### 📝 파이프와 grep/awk

```bash
ps -ef | grep python                  # 프로세스 중 python 있는 줄만
df / | awk 'NR==2 {print $5}'         # df 결과의 2번째 줄, 5번째 열
free | awk '/Mem:/ {print $3}'        # free 결과 중 Mem: 줄의 3번째 열
```

### 📝 명령어 존재 확인

```bash
if command -v ufw &> /dev/null; then
    echo "ufw 있음"
fi
```

---

## 3. monitor.sh가 해야 할 일 (요구사항 분해)

요구사항을 차근차근 나눠보면:

### 🩺 Health Check (실패 시 즉시 종료)
1. ✅ `agent_app.py` 프로세스 살아있나?
2. ✅ TCP 15034 포트 LISTEN인가?

→ 둘 중 하나라도 실패하면 `exit 1`

### ⚠️ 상태 점검 (경고만)
3. ✅ 방화벽(UFW) 활성 상태인가?

→ 비활성이면 `[WARNING]` 출력 (스크립트는 계속)

### 📊 자원 수집
4. ✅ CPU 사용률 (%)
5. ✅ 메모리 사용률 (%)
6. ✅ 디스크 사용률 (Root partition, %)

### 🚨 임계값 경고
7. ✅ CPU > 20% → `[WARNING]`
8. ✅ MEM > 10% → `[WARNING]`
9. ✅ DISK_USED > 80% → `[WARNING]`

### 📝 로그 기록
10. ✅ `/var/log/agent-app/monitor.log`에 한 줄 추가
11. ✅ 형식: `[YYYY-MM-DD HH:MM:SS] PID:... CPU:..% MEM:..% DISK_USED:..%`

### 🗃️ 로그 용량 관리
12. ✅ 최대 10MB / 10개 파일 유지

---

## 4. 전체 코드 (완성본)

복사해서 바로 쓸 수 있게 만든 완성본이에요. 다음 섹션에서 한 블록씩 뜯어볼게요.

```bash
#!/bin/bash
###############################################################################
# monitor.sh - Agent App Monitoring Script
#
# 작성자: agent-dev
# 실행자: agent-admin (via cron)
# 목적: Agent App 프로세스/포트/리소스를 점검하고 로그 기록
###############################################################################

# ─────────────────────────────────────────────────────────────
# 0. 설정 (Configuration)
# ─────────────────────────────────────────────────────────────
APP_NAME="agent_app.py"
APP_PORT=15034
LOG_DIR="/var/log/agent-app"
LOG_FILE="$LOG_DIR/monitor.log"
MAX_LOG_SIZE=$((10 * 1024 * 1024))    # 10MB in bytes
MAX_LOG_FILES=10

# 임계값
CPU_THRESHOLD=20      # %
MEM_THRESHOLD=10      # %
DISK_THRESHOLD=80     # %

# 타임스탬프
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 로그 디렉토리 보장 (없으면 생성)
mkdir -p "$LOG_DIR" 2>/dev/null

# ─────────────────────────────────────────────────────────────
# 1. Health Check: 프로세스 확인 (실패 시 종료)
# ─────────────────────────────────────────────────────────────
APP_PID=$(pgrep -f "$APP_NAME" | head -n 1)
if [ -z "$APP_PID" ]; then
    echo "[$TIMESTAMP] ERROR: $APP_NAME process not found" >> "$LOG_FILE"
    exit 1
fi

# ─────────────────────────────────────────────────────────────
# 2. Health Check: 포트 LISTEN 확인 (실패 시 종료)
# ─────────────────────────────────────────────────────────────
if ! ss -tlnp 2>/dev/null | grep -q ":$APP_PORT "; then
    echo "[$TIMESTAMP] ERROR: Port $APP_PORT not listening" >> "$LOG_FILE"
    exit 1
fi

# ─────────────────────────────────────────────────────────────
# 3. 방화벽 상태 점검 (경고만)
# ─────────────────────────────────────────────────────────────
if command -v ufw &> /dev/null; then
    if ! ufw status 2>/dev/null | grep -q "Status: active"; then
        echo "[$TIMESTAMP] [WARNING] UFW is not active" >> "$LOG_FILE"
    fi
elif command -v firewall-cmd &> /dev/null; then
    if ! firewall-cmd --state 2>/dev/null | grep -q "running"; then
        echo "[$TIMESTAMP] [WARNING] firewalld is not running" >> "$LOG_FILE"
    fi
fi

# ─────────────────────────────────────────────────────────────
# 4. 자원 수집
# ─────────────────────────────────────────────────────────────
# CPU 사용률 (% as integer)
CPU_USAGE=$(top -bn1 | awk '/Cpu\(s\)/ {print 100 - $8}' | cut -d. -f1)
[ -z "$CPU_USAGE" ] && CPU_USAGE=0

# 메모리 사용률 (% as integer)
MEM_USAGE=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
[ -z "$MEM_USAGE" ] && MEM_USAGE=0

# 디스크 사용률 (Root partition, % as integer)
DISK_USAGE=$(df / | awk 'NR==2 {gsub("%",""); print $5}')
[ -z "$DISK_USAGE" ] && DISK_USAGE=0

# ─────────────────────────────────────────────────────────────
# 5. 임계값 경고 (경고만 출력, 계속 진행)
# ─────────────────────────────────────────────────────────────
if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ]; then
    echo "[$TIMESTAMP] [WARNING] CPU usage high: ${CPU_USAGE}%" >> "$LOG_FILE"
fi

if [ "$MEM_USAGE" -gt "$MEM_THRESHOLD" ]; then
    echo "[$TIMESTAMP] [WARNING] MEM usage high: ${MEM_USAGE}%" >> "$LOG_FILE"
fi

if [ "$DISK_USAGE" -gt "$DISK_THRESHOLD" ]; then
    echo "[$TIMESTAMP] [WARNING] DISK usage high: ${DISK_USAGE}%" >> "$LOG_FILE"
fi

# ─────────────────────────────────────────────────────────────
# 6. 로그 용량 관리 (Rotation: 10MB / 10개 유지)
# ─────────────────────────────────────────────────────────────
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
    if [ "$LOG_SIZE" -gt "$MAX_LOG_SIZE" ]; then
        # 가장 오래된 것부터 밀어내기 (monitor.log.9 → 10, ..., 1 → 2)
        for i in $(seq $((MAX_LOG_FILES - 1)) -1 1); do
            if [ -f "${LOG_FILE}.$i" ]; then
                mv "${LOG_FILE}.$i" "${LOG_FILE}.$((i + 1))"
            fi
        done
        # 현재 로그를 .1로 이동
        mv "$LOG_FILE" "${LOG_FILE}.1"
        # 10번째 초과 파일 삭제
        rm -f "${LOG_FILE}.$((MAX_LOG_FILES + 1))"
    fi
fi

# ─────────────────────────────────────────────────────────────
# 7. 메인 로그 기록
# ─────────────────────────────────────────────────────────────
echo "[$TIMESTAMP] PID:$APP_PID CPU:${CPU_USAGE}% MEM:${MEM_USAGE}% DISK_USED:${DISK_USAGE}%" >> "$LOG_FILE"

exit 0
```

---

## 5. 코드 한 블록씩 뜯어보기

### 🔍 블록 0: 설정

```bash
APP_NAME="agent_app.py"
APP_PORT=15034
LOG_DIR="/var/log/agent-app"
LOG_FILE="$LOG_DIR/monitor.log"
MAX_LOG_SIZE=$((10 * 1024 * 1024))
```

#### 왜 위에 모아두지?
**유지보수 편하라고**. 나중에 포트 바꾸려면 위에 `APP_PORT=` 하나만 수정.

#### `$((...))` 는 뭐야?
**산술 연산** 문법. `10 * 1024 * 1024 = 10,485,760` (10MB를 바이트로).

---

### 🔍 블록 1: 프로세스 체크

```bash
APP_PID=$(pgrep -f "$APP_NAME" | head -n 1)
if [ -z "$APP_PID" ]; then
    echo "[$TIMESTAMP] ERROR: $APP_NAME process not found" >> "$LOG_FILE"
    exit 1
fi
```

#### `pgrep -f "agent_app.py"` 의미
- `pgrep` = process grep (프로세스 검색)
- `-f` = full command line으로 검색 (이걸 안 쓰면 프로세스 이름만 봐서 python으로 실행된 스크립트는 못 찾음)
- 결과: 일치하는 프로세스의 PID들

#### `head -n 1`
여러 PID 중 *첫 번째*만 가져옴.

#### `[ -z "$APP_PID" ]`
- `-z` = zero length (비어있다)
- 즉 "PID가 비어있으면" → 프로세스 없는 것

#### 왜 `exit 1`?
실패 시 종료. cron이 이걸 보고 *실패한 실행*으로 인식. 종료 코드로 상태 전달.

---

### 🔍 블록 2: 포트 체크

```bash
if ! ss -tlnp 2>/dev/null | grep -q ":$APP_PORT "; then
    echo "[$TIMESTAMP] ERROR: Port $APP_PORT not listening" >> "$LOG_FILE"
    exit 1
fi
```

#### `ss -tlnp`
- `-t` TCP만
- `-l` LISTEN 상태만
- `-n` 숫자로
- `-p` 프로세스 정보까지

#### `2>/dev/null`
ss가 권한 부족으로 내는 *에러*는 휴지통에. (PID 정보 못 봐도 LISTEN 정보는 보이니까)

#### `grep -q ":$APP_PORT "`
- `-q` quiet (출력 없이 매칭 여부만)
- `":15034 "` 처럼 *콜론+포트+공백*으로 검색 (`15034`가 들어간 다른 숫자랑 헷갈리지 않게)

#### `if !` 의미
`!`는 부정. "성공 *아니면*", 즉 "포트가 LISTEN *안 하면*".

---

### 🔍 블록 3: 방화벽 체크 (경고만)

```bash
if command -v ufw &> /dev/null; then
    if ! ufw status 2>/dev/null | grep -q "Status: active"; then
        echo "[$TIMESTAMP] [WARNING] UFW is not active" >> "$LOG_FILE"
    fi
elif command -v firewall-cmd &> /dev/null; then
    ...
fi
```

#### `command -v ufw &> /dev/null`
- `command -v`는 명령어가 *존재하는지* 알려줌 (있으면 경로 출력, 없으면 빈 출력)
- `&> /dev/null`로 출력 모두 버림
- "ufw 명령이 있는가?"라는 if 조건

#### 왜 ufw와 firewalld 둘 다 체크?
요구사항: "UFW 또는 firewalld 중 하나 선택". 어느 걸 썼는지 모르니 둘 다 확인.

#### 왜 `exit`이 없어?
요구사항: *방화벽은 경고만, 종료 안 함*. 그래서 echo만 하고 진행.

---

### 🔍 블록 4: 자원 수집 (가장 헷갈리는 부분)

#### CPU 사용률
```bash
CPU_USAGE=$(top -bn1 | awk '/Cpu\(s\)/ {print 100 - $8}' | cut -d. -f1)
```

뜯어보면:

| 부분 | 의미 |
|---|---|
| `top -bn1` | top 한 번 실행 (-b batch 모드, -n1 1회) |
| `awk '/Cpu\(s\)/ {...}'` | "Cpu(s)" 줄 찾아서 처리 |
| `print 100 - $8` | 100 - $8 출력 ($8은 idle %) |
| `cut -d. -f1` | 점(.) 기준 첫 부분만 (소수점 제거) |

**왜 `100 - idle`?**
`top`의 Cpu(s) 줄 형식: `... 95.0 id ...` (95% idle = 5% 사용)
→ `100 - 95 = 5%` 가 진짜 사용률

#### 메모리 사용률
```bash
MEM_USAGE=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
```

| 부분 | 의미 |
|---|---|
| `free` | 메모리 정보 출력 |
| `/Mem:/` | "Mem:" 줄만 |
| `$2` | total memory |
| `$3` | used memory |
| `$3/$2 * 100` | 사용률 % |
| `printf "%.0f"` | 정수로 반올림 |

#### 디스크 사용률
```bash
DISK_USAGE=$(df / | awk 'NR==2 {gsub("%",""); print $5}')
```

| 부분 | 의미 |
|---|---|
| `df /` | 루트 파티션 디스크 사용량 |
| `NR==2` | 2번째 줄 (1번째는 헤더) |
| `gsub("%","")` | `%` 기호 제거 |
| `print $5` | 5번째 열 (Use%) |

#### 안전장치: 빈 값 처리
```bash
[ -z "$CPU_USAGE" ] && CPU_USAGE=0
```

- `[ 조건 ] && 명령` = "조건 참이면 명령 실행"
- 빈 값일 때 0으로 처리해서 다음 숫자 비교가 에러 안 나게.

---

### 🔍 블록 5: 임계값 경고

```bash
if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ]; then
    echo "[$TIMESTAMP] [WARNING] CPU usage high: ${CPU_USAGE}%" >> "$LOG_FILE"
fi
```

#### `-gt` 의미
**g**reater **t**han. 다른 비교 연산자:

| 연산자 | 의미 |
|---|---|
| `-gt` | > |
| `-ge` | ≥ |
| `-lt` | < |
| `-le` | ≤ |
| `-eq` | = |
| `-ne` | ≠ |

> 💡 문자열에선 `=`, `!=` 쓰고, 숫자엔 `-gt`, `-lt` 등 사용.

---

### 🔍 블록 6: 로그 로테이션

```bash
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
    if [ "$LOG_SIZE" -gt "$MAX_LOG_SIZE" ]; then
        for i in $(seq $((MAX_LOG_FILES - 1)) -1 1); do
            ...
        done
        mv "$LOG_FILE" "${LOG_FILE}.1"
        rm -f "${LOG_FILE}.$((MAX_LOG_FILES + 1))"
    fi
fi
```

#### `stat -c%s 파일`
- `stat` = 파일 정보
- `-c%s` = size in bytes

#### 로테이션 원리
```text
monitor.log.9  →  monitor.log.10
monitor.log.8  →  monitor.log.9
...
monitor.log.1  →  monitor.log.2
monitor.log    →  monitor.log.1   (새로 생김)
monitor.log.11 → 삭제
```

#### `seq $((MAX_LOG_FILES - 1)) -1 1`
- `seq 시작 증가 끝` 형식
- `seq 9 -1 1` = 9, 8, 7, ..., 1
- 큰 번호부터 처리하는 게 안전 (덮어쓰기 방지)

#### 💡 더 쉬운 대안: logrotate
시스템 도구 `logrotate`를 쓰면 이 코드 다 안 만들어도 돼요. 보너스 가이드에서 다룸.

---

### 🔍 블록 7: 메인 로그

```bash
echo "[$TIMESTAMP] PID:$APP_PID CPU:${CPU_USAGE}% MEM:${MEM_USAGE}% DISK_USED:${DISK_USAGE}%" >> "$LOG_FILE"
```

요구사항 형식대로 한 줄 추가. `>>` 로 *기존 내용 유지하고 추가*.

---

## 6. 실습 단계

### Step 1. 스크립트 파일 생성

#### ⌨️ 명령어 (root 또는 agent-dev로)
```bash
# agent-dev로 전환
su - agent-dev

# bin 디렉토리는 이미 만들어둠 ($AGENT_HOME/bin)
# 단, agent-dev에서 AGENT_HOME 환경변수가 안 보일 수 있으니 절대 경로 사용
SCRIPT_PATH="/home/agent-admin/agent-app/bin/monitor.sh"

# vim 또는 nano로 열어서 위 전체 코드 붙여넣기
vim $SCRIPT_PATH
```

vim 사용법은 [이전 SSH 가이드의 vim 치트시트](#) 참고.

> 💡 더 빠른 방법: 컨테이너 밖에서 파일 만들어서 `docker cp`로 복사

---

### Step 2. 권한 설정 (가장 중요)

#### 🎯 목적
요구사항대로 정확히 설정.

#### ⌨️ 명령어 (root로)
```bash
# root로 돌아오기
exit

# 소유자: agent-dev, 그룹: agent-core
chown agent-dev:agent-core /home/agent-admin/agent-app/bin/monitor.sh

# 권한: 750 (rwxr-x---)
chmod 750 /home/agent-admin/agent-app/bin/monitor.sh
```

#### 🤔 왜 이렇게 설정?

| 설정 | 이유 |
|---|---|
| **소유자 = agent-dev** | 작성자가 dev (요구사항) |
| **그룹 = agent-core** | cron 실행자(agent-admin)이 agent-core 그룹이라 *읽기+실행* 가능 |
| **권한 = 750** | 소유자 전부, 그룹 R/X, 나머지 차단 |

#### ✅ 확인
```bash
ls -la /home/agent-admin/agent-app/bin/monitor.sh
```
결과 예시:
```text
-rwxr-x--- 1 agent-dev agent-core 1234 May 18 12:00 monitor.sh
```

---

### Step 3. 로그 디렉토리 권한 확인

#### 🎯 목적
스크립트가 `/var/log/agent-app/monitor.log`에 쓸 수 있어야 함.

#### ⌨️ 명령어
```bash
ls -la /var/log/ | grep agent-app
```

`drwxrwx--- agent-admin agent-core` 형태로 나오면 OK. agent-core 그룹 멤버라 쓸 수 있음.

만약 권한이 다르면:
```bash
chown agent-admin:agent-core /var/log/agent-app
chmod 770 /var/log/agent-app
```

---

### Step 4. 수동 실행 테스트

#### 🎯 목적
cron 등록 전, **손으로 한 번 돌려서** 잘 동작하는지 확인.

#### ⌨️ 명령어
```bash
# agent-admin으로 (cron 실행 계정과 동일)
su - agent-admin

# 앱이 안 떠 있으면 먼저 띄우기 (다른 터미널에서)
# python3 $AGENT_HOME/agent_app.py &

# monitor.sh 실행
/home/agent-admin/agent-app/bin/monitor.sh

# 종료 코드 확인
echo "Exit code: $?"
```

#### 🔍 `$?` 의미
- 직전 명령의 **종료 코드**
- 0이면 성공, 그 외는 실패

#### ✅ 성공 결과
- 종료 코드 0
- `/var/log/agent-app/monitor.log`에 한 줄 추가됨

#### ⌨️ 로그 확인
```bash
tail -5 /var/log/agent-app/monitor.log
```

결과 예시:
```text
[2026-05-18 12:30:00] PID:1234 CPU:5% MEM:8% DISK_USED:45%
```

---

### Step 5. 다양한 시나리오 테스트

#### 시나리오 1: 앱이 꺼진 상태
```bash
# 앱 종료
pkill -f agent_app.py

# 스크립트 실행
/home/agent-admin/agent-app/bin/monitor.sh
echo "Exit code: $?"
```

기대 결과:
- 종료 코드 `1`
- 로그에 `ERROR: agent_app.py process not found`

#### 시나리오 2: 정상 상태
앱 켜고 다시 실행 → 종료 코드 `0`, 정상 로그 한 줄.

#### 시나리오 3: CPU 부하 (선택)
```bash
# 다른 터미널에서 CPU 부하 생성 (60초)
yes > /dev/null &
YES_PID=$!
sleep 60
kill $YES_PID

# 그 사이에 monitor.sh 실행 → CPU 경고가 로그에 남는지 확인
```

---

### Step 6. 디버깅 모드로 실행 (문제 있을 때)

```bash
bash -x /home/agent-admin/agent-app/bin/monitor.sh
```

`-x`는 *각 명령 실행 직전*에 그 명령을 화면에 출력. 어디서 막히는지 추적할 때 유용.

---

## 7. 자주 만나는 에러와 해결법

### ❌ `Permission denied`
**원인**: 실행 권한 없음
**해결**:
```bash
chmod 750 /home/agent-admin/agent-app/bin/monitor.sh
```

---

### ❌ `bad interpreter: No such file`
**원인**: Shebang 줄(`#!/bin/bash`)에 줄바꿈이 이상함 (Windows에서 만든 파일)
**해결**:
```bash
# dos2unix 설치 후 변환
apt install -y dos2unix
dos2unix monitor.sh
```

---

### ❌ `[: : integer expression expected`
**원인**: 변수가 비었는데 숫자 비교 시도 (예: CPU_USAGE가 빈 값)
**해결**: 우리 코드의 안전장치(`[ -z ... ] && VAR=0`)가 이미 처리

---

### ❌ 로그 파일에 안 써짐
**원인**: 로그 디렉토리 권한 없음
**해결**:
```bash
ls -la /var/log/ | grep agent-app
# 770이고 그룹이 agent-core여야 함
```

---

### ❌ `ss: command not found`
**원인**: iproute2 미설치
**해결**:
```bash
apt install -y iproute2
```

---

### ❌ cron에선 동작 안 하는데 손으로는 됨
**원인**: cron은 *최소 환경*으로 실행. PATH가 다름.
**해결**: 스크립트 안에서 절대 경로 사용 (`/usr/sbin/sshd` 등). 자세한 건 [06번 가이드].

---

### ❌ awk 결과가 이상함
**원인**: 일부 명령어 출력 형식이 시스템마다 다름 (특히 `top`)
**해결**: 손으로 한 번 출력 형식 확인 후 awk 수정
```bash
top -bn1 | grep "Cpu(s)"   # 출력 형식 확인
```

---

## 8. 전체 흐름 한눈에 보기

```text
[ monitor.sh 실행 ]
       │
       ▼
┌─────────────────┐
│ 1. 프로세스 ✅?  │── ❌ ──► [ERROR 로그 기록] → exit 1
└────────┬────────┘
         │ ✅
         ▼
┌─────────────────┐
│ 2. 포트 LISTEN? │── ❌ ──► [ERROR 로그 기록] → exit 1
└────────┬────────┘
         │ ✅
         ▼
┌─────────────────┐
│ 3. 방화벽 활성?  │── ❌ ──► [WARNING 로그] (계속)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 자원 수집    │  CPU, MEM, DISK
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. 임계값 점검  │  초과 시 [WARNING] 로그
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. 로그 로테이션 │  10MB 초과 시 .1, .2, ... 로 밀어내기
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 7. 메인 로그 기록│  [TIME] PID:.. CPU:..% MEM:..% DISK:..%
└────────┬────────┘
         │
         ▼
    exit 0 ✅
```

---

## 📌 마무리: 이번에 진짜 배운 것

1. **"스크립트는 명령어의 묶음"** — 손으로 치던 걸 파일에 담은 것
2. **"종료 코드로 상태 전달"** — 0=성공, 1+=실패
3. **"Health Check는 fail-fast"** — 진짜 문제는 즉시 exit
4. **"경고는 죽이지 않음"** — 모든 게 치명적인 건 아니다
5. **"변수는 위에 모은다"** — 설정과 로직 분리
6. **"파이프와 awk는 친구"** — Linux 정보 추출의 표준 패턴
7. **"로그 로테이션은 필수"** — 안 그러면 디스크 가득 참

다음은 **`06_crontab_자동실행_가이드.md`**: 매분 자동 실행 설정.
