# crontab 자동실행 완전 초보자 가이드
## (monitor.sh를 매분 자동 실행하기)

> Linux의 자동 스케줄러 **cron**을 처음 보는 사람도 이해할 수 있게 풀어 쓴 가이드입니다.

---

## 📚 목차

1. [시작하기 전에 — cron이 뭐야?](#0-시작하기-전에--cron이-뭐야)
2. [핵심 용어 미리 알기](#1-핵심-용어-미리-알기)
3. [crontab 형식 — 별 5개의 의미](#2-crontab-형식--별-5개의-의미)
4. [실습 단계 (1 ~ 6)](#3-실습-단계)
5. [⚠️ cron의 최대 함정 — 환경변수](#4-️-cron의-최대-함정--환경변수)
6. [자주 만나는 에러와 해결법](#5-자주-만나는-에러와-해결법)
7. [전체 흐름 한눈에 보기](#6-전체-흐름-한눈에-보기)

---

## 0. 시작하기 전에 — cron이 뭐야?

### 🤔 한 문장으로

**"Linux의 *알람시계 + 비서*"** 예요. 정해진 시간이 되면 시키는 명령을 자동 실행해줘요.

### 🤔 비유로

비유: 회사에서 매일 9시에 출근부 확인하고, 매주 월요일 10시에 전체 회의, 매달 1일에 월급 입금... 이런 *정기 업무*를 자동으로 처리해주는 비서.

cron도 똑같아요:
- "매분 monitor.sh 실행해"
- "매일 새벽 3시에 백업 실행해"
- "매주 일요일에 로그 정리해"

### 🤔 cron vs crontab — 헷갈리지 마

| 용어 | 의미 |
|---|---|
| **cron** | *프로그램 자체*. 백그라운드에서 항상 돌면서 스케줄 확인 |
| **crontab** | *예약 목록*. "어떤 작업을 언제 실행할지" 적힌 표 |

비유: cron = 알람시계 본체, crontab = 알람 설정 목록.

### 🤔 이번 미션의 cron 작업

요구사항: **agent-admin 계정에서 monitor.sh를 매분 실행**.

---

## 1. 핵심 용어 미리 알기

| 용어 | 비유 | 진짜 의미 |
|---|---|---|
| **cron** | 알람시계 | 스케줄러 데몬 |
| **crontab** | 알람 설정 목록 | cron 작업 정의 파일 |
| **cron job** | 알람 하나 | crontab의 한 줄 |
| **`crontab -e`** | "내 알람 설정 편집" | crontab 편집 모드 |
| **`crontab -l`** | "내 알람 목록 보기" | crontab 내용 확인 |
| **`crontab -r`** | "내 알람 다 지우기" | 위험! 전체 삭제 |
| **system crontab** | 전사 공지용 알람 | `/etc/crontab` (관리자만) |
| **user crontab** | 개인 알람 | 사용자별 cron 작업 |

---

## 2. crontab 형식 — 별 5개의 의미

cron의 한 줄은 이렇게 생겼어요:

```text
* * * * * 실행할_명령어
│ │ │ │ │
│ │ │ │ └── 요일 (0-7, 0과 7 모두 일요일)
│ │ │ └──── 월 (1-12)
│ │ └────── 일 (1-31)
│ └──────── 시 (0-23)
└────────── 분 (0-59)
```

### 📝 자주 쓰는 패턴

| 표현 | 의미 |
|---|---|
| `* * * * *` | **매분** (이번 미션) |
| `*/5 * * * *` | 5분마다 |
| `0 * * * *` | 매시 정각 |
| `0 9 * * *` | 매일 오전 9시 |
| `0 9 * * 1` | 매주 월요일 9시 |
| `0 0 1 * *` | 매달 1일 자정 |
| `30 3 * * 0` | 매주 일요일 새벽 3시 30분 |
| `*/10 9-18 * * 1-5` | 평일 9~18시 사이 10분마다 |

### 🔍 각 기호 의미

| 기호 | 의미 |
|---|---|
| `*` | 모든 값 |
| `숫자` | 특정 값만 |
| `숫자,숫자` | 여러 값 (예: `1,15`) |
| `숫자-숫자` | 범위 (예: `9-18`) |
| `*/숫자` | 간격 (예: `*/5` = 5마다) |

### 💡 헷갈리는 부분

> **"`* * * * *` 가 정말 매분이야? 매초가 아니고?"**

네, **cron의 최소 단위는 1분**이에요. 매초 실행은 cron으로 못 함. 더 짧은 주기가 필요하면 다른 도구(systemd timer, 무한 루프 스크립트 등) 사용.

---

## 3. 실습 단계

### Step 1. cron 설치 및 실행 확인

#### 🎯 목적
컨테이너 최소 이미지엔 cron이 없을 수 있어요. 깔고 켭니다.

#### ⌨️ 명령어 (root로)
```bash
# 설치
apt update
apt install -y cron

# cron 서비스 시작 (컨테이너에 systemd 없으면 직접 실행)
service cron start
# 또는
cron
```

#### ✅ 확인
```bash
ps -ef | grep cron
```

`cron` 또는 `crond` 프로세스가 보이면 OK.

#### 🤔 systemctl이 안 먹혀요
Docker 컨테이너엔 systemd가 없는 경우가 많아요. 그래서 `systemctl start cron` 대신 `service cron start` 또는 그냥 `cron` 명령어 직접 실행.

---

### Step 2. agent-admin 계정의 crontab 편집

#### 🎯 목적
**agent-admin** 사용자의 crontab에 작업 추가.

#### ⌨️ 명령어
```bash
# 방법 A: agent-admin으로 전환 후 본인 crontab 편집
su - agent-admin
crontab -e
```

또는

```bash
# 방법 B: root에서 agent-admin의 crontab 편집
crontab -u agent-admin -e
```

#### 💡 첫 실행 시
"어떤 편집기 쓸래?" 물어볼 수 있어요. `1` (nano) 또는 `2` (vim) 선택. 처음이면 **nano가 훨씬 쉬워요**.

---

### Step 3. cron 작업 추가

#### 📝 crontab 파일 끝에 다음 한 줄 추가

```text
* * * * * /home/agent-admin/agent-app/bin/monitor.sh
```

#### 💡 더 안정적인 버전 (권장)

위 단순 버전은 환경변수가 안 먹히거나 PATH 문제로 실패할 수 있어요. 안정적인 버전:

```text
# Agent App monitoring - every minute
* * * * * /bin/bash -lc 'export AGENT_HOME=/home/agent-admin/agent-app; export AGENT_PORT=15034; /home/agent-admin/agent-app/bin/monitor.sh' >> /var/log/agent-app/cron.log 2>&1
```

#### 🔍 안정적인 버전 뜯어보기

| 부분 | 의미 |
|---|---|
| `/bin/bash -lc '...'` | bash를 *로그인 셸*로 실행, 명령어 받기 |
| `-l` | **l**ogin shell (`.bashrc` 등 로드) |
| `-c '...'` | 명령어 직접 지정 |
| `export AGENT_HOME=...` | 환경변수 보장 |
| `>> /var/log/agent-app/cron.log 2>&1` | 출력과 에러를 cron.log에 기록 |

#### 🔍 `2>&1` 의미
- `1` = 표준 출력 (stdout)
- `2` = 표준 에러 (stderr)
- `2>&1` = "에러를 표준 출력으로 합쳐줘"
- 결과: stdout과 stderr 모두 같은 파일로

이게 없으면 에러가 *어디로 갔는지* 모르게 사라져요. 디버깅에 필수.

#### ⚠️ 저장 후 vim/nano 종료
- nano: `Ctrl + O` → Enter → `Ctrl + X`
- vim: `ESC` → `:wq` → Enter

#### ✅ 저장 후 메시지
```text
crontab: installing new crontab
```

---

### Step 4. 등록 확인

#### ⌨️ 명령어
```bash
crontab -l
```

#### ✅ 등록한 줄이 보이면 OK

```text
* * * * * /bin/bash -lc 'export AGENT_HOME=...
```

---

### Step 5. 1~2분 기다리고 자동 실행 확인

#### 🎯 목적
진짜 자동으로 돌아가는지 검증.

#### ⌨️ 명령어
```bash
# 등록 직후 로그 라인 수 기록
wc -l /var/log/agent-app/monitor.log

# 2분 기다리기
sleep 120

# 다시 확인 → 라인 수가 2 증가해 있어야 함
wc -l /var/log/agent-app/monitor.log

# 최근 라인 확인
tail -5 /var/log/agent-app/monitor.log
```

#### ✅ 성공 결과

```text
[2026-05-18 12:30:00] PID:1234 CPU:5% MEM:8% DISK_USED:45%
[2026-05-18 12:31:00] PID:1234 CPU:6% MEM:8% DISK_USED:45%
[2026-05-18 12:32:00] PID:1234 CPU:5% MEM:9% DISK_USED:45%
```

1분 단위로 라인이 추가되면 → **완벽한 자동화 작동!** 🎉

---

### Step 6. cron 자체의 로그 확인 (디버깅용)

cron이 *실행 자체에 성공했는지* 보고 싶을 때:

```bash
# 시스템 cron 로그 (배포판마다 위치 다름)
tail -20 /var/log/syslog | grep CRON
# 또는
tail -20 /var/log/cron.log
# 또는
grep CRON /var/log/syslog
```

#### 💡 우리가 만든 cron.log
위에서 cron 작업 뒤에 `>> /var/log/agent-app/cron.log 2>&1` 붙였잖아요? **그 파일에 에러가 다 모여요.**

```bash
tail -20 /var/log/agent-app/cron.log
```

뭔가 잘못되면 여기서 단서가 나와요. 보이는 게 없으면 정상.

---

## 4. ⚠️ cron의 최대 함정 — 환경변수

### 🚨 cron이 진짜 잘 안 되는 이유 1위

**"손으로 돌리면 되는데 cron으로는 안 됨"**

원인 99%: **cron은 *최소 환경*으로 실행돼요.**

### 🔍 cron 환경 vs 일반 셸 환경

| 구분 | 일반 셸 (`ssh` 로그인 등) | cron |
|---|---|---|
| `.bashrc` 로드 | ✅ 함 | ❌ 안 함 |
| `PATH` 변수 | 전체 경로 (`/usr/local/sbin:/usr/sbin:...`) | 짧음 (`/usr/bin:/bin`) |
| 환경변수 | 다 보임 | 거의 없음 |
| 현재 디렉토리 | 홈 디렉토리 | 사용자 홈 |

### 😱 그래서 생기는 문제

#### 문제 1: 명령어를 못 찾음
```bash
# 손으로는 됨
ss -tlnp

# cron으로는 안 됨 (ss가 /usr/sbin에 있는데 PATH에 없어서)
```

**해결**: 절대 경로 사용
```bash
/usr/sbin/ss -tlnp
```

#### 문제 2: 환경변수가 비어있음
```bash
# 스크립트 안에서
echo $AGENT_HOME    # 빈 줄 (cron에서는)
```

**해결 1**: 스크립트 안에서 직접 export
```bash
# monitor.sh 윗부분에
export AGENT_HOME=/home/agent-admin/agent-app
```

**해결 2**: crontab에서 미리 export (위 Step 3의 권장 버전)

**해결 3**: cron이 `.bashrc` 읽도록 `bash -l` 사용
```text
* * * * * /bin/bash -lc '/path/to/script.sh'
```

### 💡 cron 디버깅 황금 패턴

cron 작업 만들 때 처음부터 이 패턴으로:

```text
* * * * * /bin/bash -lc '/full/path/to/script.sh' >> /var/log/myapp/cron.log 2>&1
```

3가지 안전장치:
1. **`/bin/bash -lc`** → 로그인 환경 보장
2. **절대 경로** → PATH 문제 회피
3. **로그 리다이렉트** → 에러 추적 가능

---

## 5. 자주 만나는 에러와 해결법

### ❌ `crontab: command not found`
**원인**: cron 미설치
**해결**:
```bash
apt install -y cron
```

---

### ❌ crontab은 등록됐는데 실행 안 됨
**확인 순서**:
1. cron 데몬 자체가 켜졌나?
   ```bash
   ps -ef | grep cron
   ```
   안 보이면:
   ```bash
   service cron start
   ```

2. crontab 정말 등록됐나?
   ```bash
   crontab -u agent-admin -l
   ```

3. 스크립트 경로가 정확한가? 권한이 맞나?
   ```bash
   ls -la /home/agent-admin/agent-app/bin/monitor.sh
   ```

4. cron 로그에 뭐가 나오나?
   ```bash
   tail -20 /var/log/syslog | grep CRON
   tail -20 /var/log/agent-app/cron.log
   ```

---

### ❌ "loaded: success" 같은 메시지가 syslog에 보이는데 monitor.log엔 추가 안 됨
**원인**: 스크립트가 *실행되긴 했는데 안에서 에러*. 보통 환경변수 문제.
**해결**: 위 [cron 함정](#4-️-cron의-최대-함정--환경변수) 섹션 참고

---

### ❌ `/bin/sh: command not found` 같은 에러
**원인**: cron 기본 셸은 `sh`예요 (`bash`가 아님). bash 전용 문법은 안 먹힘.
**해결**: 명시적으로 `/bin/bash`로 실행
```text
* * * * * /bin/bash /path/to/script.sh
```

---

### ❌ 환경변수 안 먹힘
**해결 패턴들** (위에서 설명한 3가지 중 골라서):

```text
# 패턴 A: bash -lc로 .bashrc 로드
* * * * * /bin/bash -lc '/path/to/script.sh'

# 패턴 B: crontab에서 변수 직접 export
AGENT_HOME=/home/agent-admin/agent-app
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
* * * * * /path/to/script.sh

# 패턴 C: 스크립트 안에서 처리 (가장 견고)
# monitor.sh 안에:
#   export AGENT_HOME=...
#   export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

---

### ❌ `permission denied` (cron 작업)
**원인**: 스크립트 실행 권한 없음 또는 cron 실행자가 멤버 아님
**해결**:
```bash
# 권한 확인
ls -la /home/agent-admin/agent-app/bin/monitor.sh
# 결과: -rwxr-x--- agent-dev agent-core ...

# agent-admin이 agent-core 멤버인지 확인
id agent-admin
# 결과에 agent-core 있어야 함

# 없으면 추가
usermod -aG agent-core agent-admin
```

---

### ❌ `crontab -e` 했는데 어떤 편집기 골라야 할지 몰라
**추천**:
- 초보자: `nano` (간단)
- 익숙해진 후: `vim` (강력)

기본 편집기 영구 변경:
```bash
# .bashrc에 추가
echo 'export EDITOR=nano' >> ~/.bashrc
source ~/.bashrc
```

---

### ❌ `crontab -r` 실수로 눌렀어요!
**원인**: `-r`은 **r**emove. **전체 crontab 삭제**.
**해결**: 백업 없으면 복구 불가. *다시 작성*.

> 💡 예방법: `crontab -l > ~/crontab-backup.txt` 로 가끔 백업 떠두기

---

## 6. 전체 흐름 한눈에 보기

```text
[ root 권한 ]
     │
     │ apt install -y cron                    ← cron 설치
     │ service cron start                     ← cron 데몬 실행
     │
     ▼
[ agent-admin으로 ]
     │
     │ crontab -e                             ← crontab 편집
     │
     │ (편집기에서 한 줄 추가)
     │ * * * * * /bin/bash -lc '...monitor.sh' >> ... 2>&1
     │
     │ (저장 후 종료)
     │
     │ crontab -l                             ← 등록 확인
     │
     │ sleep 120 && tail /var/log/agent-app/monitor.log
     │                                         ← 자동 실행 검증
     ▼
[ 매분 자동 실행 중 ]
   - monitor.log에 한 줄씩 누적
   - 문제 발생 시 cron.log에 에러
```

---

## 📌 마무리: 이번에 진짜 배운 것

1. **"cron은 알람시계"** — 시간 되면 명령 자동 실행
2. **"`* * * * *` = 매분"** — 분/시/일/월/요일 순
3. **"`crontab -e`로 편집, `-l`로 확인, `-r`은 위험"** — 명령 외우기
4. **"cron은 최소 환경"** — 환경변수, PATH 다 챙겨야 됨
5. **"항상 로그 리다이렉트"** — `>> /path/cron.log 2>&1`
6. **"`bash -lc`로 안전하게"** — 환경변수 문제의 90% 해결
7. **"검증 = 시간 지나고 로그 확인"** — `sleep 120 && tail ...`

다음(선택)은 **`07_보너스_과제_가이드.md`**: report.sh와 로그 보존 정책.
