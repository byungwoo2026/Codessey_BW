# 방화벽 실습 완전 초보자 가이드
## (UFW 활성화 + 20022/tcp, 15034/tcp만 허용)

> 이 문서는 방화벽이 *왜* 필요한지, *어떻게* 작동하는지, 명령어 한 줄 한 줄이 *뭘* 하는지 처음 보는 사람도 이해할 수 있게 풀어 쓴 가이드예요.
> SSH 실습([이전 문서](#))에서 만든 Ubuntu 컨테이너에서 이어서 진행한다고 가정하고 썼습니다.

---

## 📚 목차

1. [시작하기 전에 — 방화벽이 뭐야?](#0-시작하기-전에--방화벽이-뭐야)
2. [핵심 용어 미리 알기](#1-핵심-용어-미리-알기)
3. [UFW vs firewalld — 뭘 써야 해?](#2-ufw-vs-firewalld--뭘-써야-해)
4. [전체 그림 (방화벽이 어디서 일하는지)](#3-전체-그림-방화벽이-어디서-일하는지)
5. [⚠️ 시작 전 꼭 알아둘 함정](#4-️-시작-전-꼭-알아둘-함정-자기-자신을-잠그지-않는-법)
6. [UFW 실습 단계 (1 ~ 8)](#5-ufw-실습-단계)
7. [(참고) firewalld로 똑같이 하기](#6-참고-firewalld로-똑같이-하기)
8. [자주 만나는 에러와 해결법](#7-자주-만나는-에러와-해결법)
9. [전체 흐름 한눈에 보기](#8-전체-흐름-한눈에-보기)
10. [다음에 해볼 만한 것들](#9-다음에-해볼-만한-것들)

---

## 0. 시작하기 전에 — 방화벽이 뭐야?

### 🤔 한 문장으로 말하면

**"내 서버에 들어오는/나가는 통신을 미리 정한 규칙대로 허용·차단해주는 검문소"** 입니다.

### 🤔 비유로 이해하기

🏢 **회사 건물 1층 경비실**을 상상해보세요.
- 외부에서 누가 와도 일단 경비실에서 멈춤
- 출입증/방문 사유 확인
- 허락된 사람만 통과, 나머진 막힘

방화벽도 똑같아요.
- 외부에서 어떤 통신이 들어와도 일단 방화벽에서 멈춤
- 어느 포트로 왔는지, 어느 IP에서 왔는지 확인
- 허락된 것만 통과, 나머진 차단

### 🤔 SSH는 이미 설정했는데 방화벽이 또 왜 필요해?

아주 좋은 질문이에요. **각자 역할이 달라요**:

| 구분 | 역할 | 비유 |
|---|---|---|
| **SSH 설정** | SSH 서버 *내부* 동작 규칙 (누가 로그인 가능한지) | 사무실 문 앞에서 신분증 확인 |
| **방화벽** | 서버 *바깥쪽* 통신 자체를 통제 (어떤 포트가 열려 있나) | 1층 경비실에서 출입 자체를 통제 |

둘 다 있어야 진짜 보안이에요. 비유로:
- ❌ SSH만 잘 설정 = 경비실 없이 사무실 문만 잘 잠그는 것
- ❌ 방화벽만 = 경비실은 있는데 사무실은 모든 사람한테 열려있는 것
- ✅ 둘 다 = 경비실에서 1차 차단 + 사무실 문에서 2차 확인

### 🤔 이번 실습 목표

**들어오는 통신은 전부 차단**하되, **20022/tcp(SSH)** 와 **15034/tcp(서비스용)** 만 예외로 허용한다.

이걸 보안 용어로는 **"deny by default, allow by exception"** 원칙이라고 해요. *기본은 막고, 필요한 것만 열어주는* 방식. 보안에서 가장 중요한 사고방식이에요.

---

## 1. 핵심 용어 미리 알기

| 용어 | 비유 | 진짜 의미 |
|---|---|---|
| **방화벽(Firewall)** | 1층 경비실 | 네트워크 트래픽을 규칙대로 허용/차단하는 시스템 |
| **UFW** | 사용하기 쉬운 경비실 매뉴얼 | Uncomplicated Firewall, Ubuntu 표준 방화벽 도구 |
| **firewalld** | 좀 더 복잡한 경비실 매뉴얼 | RHEL/CentOS 표준 방화벽 도구 |
| **iptables / nftables** | 경비실의 *법전 그 자체* | Linux 커널의 진짜 방화벽 엔진. UFW나 firewalld가 이걸 대신 다뤄줌 |
| **포트(Port)** | 건물의 출입문 번호 | 0~65535 사이 통신 출입구 번호 |
| **TCP** | 등기우편 (받았는지 확인) | 신뢰성 있는 통신 프로토콜 (SSH, 웹 등) |
| **UDP** | 일반우편 (속도 우선) | 빠르지만 확인 안 하는 통신 (DNS, 게임 등) |
| **Incoming(인바운드)** | 들어오는 손님 | 외부 → 내 서버로 들어오는 트래픽 |
| **Outgoing(아웃바운드)** | 나가는 사람 | 내 서버 → 외부로 나가는 트래픽 |
| **default policy** | 경비실 기본 방침 | 규칙에 없는 통신은 어떻게 할지 기본값 |
| **rule(룰)** | 경비실 예외 규정 | 특정 포트/IP를 허용·차단하는 개별 규칙 |

### 💡 꼭 기억할 한 가지

방화벽의 진짜 핵심은 **"기본은 막아두고, 예외만 허용한다"** 예요. 반대로 "기본은 다 열고, 위험한 것만 막는다"는 안전하지 않아요. 왜냐하면 *모르는 위험*은 못 막거든요.

---

## 2. UFW vs firewalld — 뭘 써야 해?

### 결론 먼저

**Ubuntu = UFW 쓰세요.** (이번 실습도 이걸로 할 거예요)

### 비교표

| | UFW | firewalld |
|---|---|---|
| 진영 | Ubuntu / Debian | Red Hat / CentOS / Fedora |
| 난이도 | ⭐⭐ (쉬움) | ⭐⭐⭐⭐ (복잡) |
| 개념 모델 | 룰 목록 (단순) | Zone 기반 (구역별 규칙) |
| 명령어 길이 | 짧음 | 김 |
| 표준 환경 | Ubuntu Server | CentOS, RHEL, Rocky Linux |
| 우리 상황 | ✅ 우리가 쓰는 거 | ❌ 안 깔려 있음 |

### 🤔 그럼 firewalld는 언제 배워?

- 회사 서버가 CentOS/RHEL/Rocky 계열이라면 그때 배우면 돼요
- 둘 다 결국 *iptables라는 더 깊은 엔진을 조작*해주는 도구라, 개념은 똑같음
- UFW 익히면 firewalld도 금방 적응 가능

---

## 3. 전체 그림 (방화벽이 어디서 일하는지)

```text
┌─────────────────────────────────────────────────────┐
│  외부 인터넷 (공격자, 봇, 정상 사용자 모두 포함)    │
└───────────────────────┬─────────────────────────────┘
                        │
                        │ TCP/UDP 패킷
                        ▼
              ╔═══════════════════╗
              ║  🛡️  방화벽(UFW)  ║   ← 여기서 1차 검문
              ║                   ║
              ║  규칙 확인:       ║
              ║  ┌─────────────┐  ║
              ║  │ 20022/tcp ✅│  ║
              ║  │ 15034/tcp ✅│  ║
              ║  │ 그 외 ❌    │  ║
              ║  └─────────────┘  ║
              ╚═════════╤═════════╝
                        │ 허용된 것만
                        ▼
        ┌───────────────────────────────┐
        │  Ubuntu 서버 내부              │
        │   ├─ sshd (20022번 듣는 중)    │
        │   └─ 내 서비스 (15034번 듣는 중)│
        └───────────────────────────────┘
```

**핵심 흐름**: 외부 통신 → 방화벽 검문 → 통과한 것만 서버 내부 프로그램에 전달

---

## 4. ⚠️ 시작 전 꼭 알아둘 함정 (자기 자신을 잠그지 않는 법)

### 🚨 진짜 진짜 중요한 함정

방화벽 처음 다루는 사람이 **무조건 한 번씩 당하는 실수**가 있어요:

> **"SSH로 원격 접속 중인 상태에서, SSH 포트 허용 안 하고 방화벽을 켰다."**

결과: **그 즉시 본인이 차단당해서 서버에서 튕겨남 + 다시 못 들어감** 💀

비유: 회사 경비실 첫 출근하면서 "외부인 다 막아!"라고 했는데, *나도 외부인*인 걸 까먹은 상황.

### 🛡️ 안전한 순서

이번 실습에서 **반드시 이 순서대로** 하세요:

```text
1단계: UFW 설치만 (아직 켜지 마!)
2단계: 기본 정책 설정 (deny incoming, allow outgoing)
3단계: SSH 포트(20022) 허용 룰 먼저 추가  ← 🔑 핵심
4단계: 그 외 필요한 포트(15034) 룰 추가
5단계: 룰이 다 들어갔는지 확인
6단계: 그제서야 UFW 활성화 (enable)
```

### 💡 이번 실습은 안전한 환경

다행히 우리는 **Docker 컨테이너 안에서** 작업하고 있어요. 즉:
- 컨테이너 안에서 자기 자신을 차단해도, **Mac에서 `docker exec`로 다시 들어갈 수 있음**
- 그래서 *연습용*으로는 최적의 환경

하지만 진짜 클라우드 서버에서 똑같이 했다간 큰일 나니까, **순서를 몸에 익히는 게 진짜 중요**해요.

### 📌 컨테이너 환경의 한계 (꼭 알아두세요)

| 사실 | 설명 |
|---|---|
| ⚠️ UFW가 컨테이너에서 *진짜로* 동작하려면 추가 권한 필요 | `--cap-add=NET_ADMIN` 옵션으로 컨테이너 생성해야 함 |
| ⚠️ 기본 Ubuntu 컨테이너에선 룰 설정은 되지만, *enable*이 막힐 수 있음 | `iptables` 직접 접근 권한이 없어서 |
| ✅ 그래도 **명령어와 개념 학습**은 100% 가능 | Codyssey 과제 목적엔 충분 |
| ✅ 진짜 적용은 실제 Linux VM이나 클라우드 서버에서 | 같은 명령어가 그대로 동작함 |

만약 컨테이너에서 enable이 안 되면, **에러 메시지 자체를 학습 자료로 보세요**. 어떤 권한이 부족한지 알려주는 좋은 신호예요.

---

## 5. UFW 실습 단계

### Step 1. UFW 설치

#### 🎯 목적
방화벽 도구(UFW)를 Ubuntu에 설치한다.

#### ⌨️ 명령어
```bash
apt update                  # 패키지 목록 최신화 (안 해도 되지만 권장)
apt install ufw -y          # ufw 설치
```

#### 🔍 뜯어보기
- `apt install` → 설치
- `ufw` → 설치할 패키지명
- `-y` → "정말 설치?" 자동 yes

#### ✅ 성공 결과
설치 진행되고 마지막에 `done.` 같은 메시지.

#### 🤔 설치만 하면 자동으로 켜져?
**아니에요!** UFW는 설치해도 *비활성 상태*로 깔려요. 직접 `ufw enable` 해야 켜짐. → 우리가 일부러 안전한 순서대로 켜려고 일단 룰부터 짤 거예요.

---

### Step 2. 현재 상태 확인 (시작점 점검)

#### 🎯 목적
지금 UFW가 켜져 있는지, 어떤 룰이 들어가 있는지 *시작점*을 확인.

#### ⌨️ 명령어
```bash
ufw status
```

#### ✅ 성공 결과 (방금 설치한 상태)
```text
Status: inactive
```
**`inactive`** 가 나오면 정상. "방화벽이 아직 꺼져 있어요" 라는 뜻.

#### 💡 자주 쓰는 변형
```bash
ufw status verbose        # 더 자세한 정보 (기본 정책 포함)
ufw status numbered       # 룰에 번호 매겨서 보여줌 (룰 삭제할 때 유용)
```

---

### Step 3. 기본 정책 설정 (정말 중요)

#### 🎯 목적
"규칙에 없는 통신은 어떻게 할까?" 라는 *기본 방침*을 정한다.

#### ⌨️ 명령어
```bash
ufw default deny incoming      # 들어오는 건 기본적으로 차단
ufw default allow outgoing     # 나가는 건 기본적으로 허용
```

#### 🔍 뜯어보기
- `ufw default` → "기본 정책 설정해"
- `deny` → 차단
- `allow` → 허용
- `incoming` → 외부에서 들어오는 통신
- `outgoing` → 내부에서 나가는 통신

#### 🤔 왜 들어오는 건 막고, 나가는 건 허용?

**들어오는 건** = 외부 누군가가 *나한테* 접근하는 것 → 위험. 그래서 기본 차단.

**나가는 건** = 내가 *밖으로* 나가는 것 (예: `apt update`로 패키지 받기, 웹 요청 등) → 보통 안전. 그래서 기본 허용.

비유:
- 들어오는 거: 처음 보는 사람이 우리 집 초인종 누름 → 일단 의심
- 나가는 거: 내가 마트 가는 것 → 자유롭게

#### 🤔 더 빡센 보안은 없어?

있어요. `ufw default deny outgoing` 까지 하면 **나가는 것도 다 차단**. 그 다음 필요한 외부 통신(80/443 등)만 예외로 허용하는 방식. 진짜 보안 강한 서버는 이렇게 해요. 다만 처음엔 복잡해지니까 이번 실습은 incoming만 빡세게.

#### ✅ 성공 결과
```text
Default incoming policy changed to 'deny'
(be sure to update your rules accordingly)
Default outgoing policy changed to 'allow'
(be sure to update your rules accordingly)
```

뒤의 메시지: **"룰 업데이트하는 거 까먹지 마!"** → 즉, 다음 단계에서 SSH 포트 꼭 열라는 친절한 경고.

---

### Step 4. 🔑 SSH 포트(20022/tcp) 먼저 허용

#### 🎯 목적
**가장 중요한 단계**. 방화벽 켜기 전에 SSH 포트부터 무조건 열어둔다.

#### ⌨️ 명령어
```bash
ufw allow 20022/tcp
```

#### 🔍 뜯어보기
- `ufw allow` → 허용 룰 추가
- `20022` → 포트 번호 (지난번 실습에서 22 → 20022로 바꿨던 그 포트)
- `/tcp` → TCP 프로토콜만 (UDP는 안 열어줌)

#### 🤔 `/tcp` 왜 붙여? 안 붙이면?
`/tcp` 안 붙이면 **TCP + UDP 둘 다** 열어요. 

근데 SSH는 *TCP만* 쓰니까 굳이 UDP까지 열 필요 없어요. **필요 없는 건 안 여는 게 보안**의 기본.

| 프로토콜 | 대표 서비스 | 특징 |
|---|---|---|
| TCP | SSH, HTTP, HTTPS, MySQL | "확인된 통신" - 패킷 도착 확인 |
| UDP | DNS, 게임, 영상 스트리밍 | "빠른 통신" - 도착 확인 안 함 |

#### ✅ 성공 결과
```text
Rules updated
Rules updated (v6)
```
`v6`는 IPv6용. UFW는 알아서 IPv4 + IPv6 둘 다 룰을 만들어줘요.

#### 💡 헷갈리지 마세요
- `ufw allow ssh` ← 이렇게도 가능하긴 한데, **이건 22번 포트를 여는 거예요**. 우리는 20022로 바꿨으니 절대 이렇게 하면 안 됨!
- 항상 *우리가 진짜 쓰는 포트 번호*로 룰 만들기.

---

### Step 5. 서비스 포트(15034/tcp) 허용

#### 🎯 목적
또 다른 필요 서비스용 포트도 열어준다.

#### ⌨️ 명령어
```bash
ufw allow 15034/tcp
```

#### 🔍 뜯어보기
구조는 Step 4와 동일. 포트 번호만 다름.

#### 🤔 15034번 포트는 뭐 하는 거야?
이건 **사용자가 지정한 커스텀 서비스 포트**예요. 예를 들면:
- 웹 애플리케이션 서버용
- 내부 API용
- 모니터링 도구용
- 그 외 우리가 운영할 어떤 서비스용

핵심은 **"기본 포트가 아닌, 우리가 직접 정한 포트"** 라는 점. SSH 포트를 22→20022로 옮긴 것과 같은 이유로, 일반적이지 않은 포트 번호를 쓰면 보안에 살짝 유리해요.

#### ✅ 성공 결과
```text
Rules updated
Rules updated (v6)
```

---

### Step 6. 룰이 잘 들어갔는지 확인

#### 🎯 목적
**UFW 켜기 직전 마지막 점검**. 두 룰이 다 들어갔는지 눈으로 확인.

#### ⌨️ 명령어
```bash
ufw show added
```

#### ✅ 성공 결과
```text
Added user rules (see 'ufw status' for running firewall):
ufw allow 20022/tcp
ufw allow 15034/tcp
```

두 룰이 다 보이면 OK. 

#### 🤔 왜 `ufw status` 안 쓰고 `ufw show added`?
UFW가 아직 켜지지 않은 상태에선 `ufw status`가 `inactive`만 보여줘요. `ufw show added`는 **"아직 활성화 안 된 룰도 보여줘"** 라는 명령어라 미리보기에 좋아요.

---

### Step 7. 🚦 드디어 UFW 활성화

#### 🎯 목적
모든 룰이 준비됐으니, 진짜로 방화벽을 켠다.

#### ⌨️ 명령어
```bash
ufw enable
```

#### ⚠️ 활성화 시 경고 메시지
이런 게 뜰 거예요:
```text
Command may disrupt existing ssh connections. Proceed with operation (y|n)?
```

**해석**: "지금 SSH 연결 중이면 끊길 수도 있는데 진행함?"

여기서 `y` + Enter. **지난 단계에서 20022 포트 열어뒀으니까 안전**.

> ⚠️ 만약 20022 룰을 까먹고 enable 했다면, 이 메시지가 진짜 무서운 경고가 돼요. SSH로 원격 접속 중이었다면 그대로 끊김.

#### ✅ 성공 결과
```text
Firewall is active and enabled on system startup
```

뜻:
- `active` → 지금 켜짐
- `enabled on system startup` → 서버 재부팅해도 자동으로 켜짐

#### 🤔 컨테이너에서 에러 나면?
이런 메시지 가능:
```text
ERROR: problem running ufw-init
```

이건 **컨테이너 환경 한계**예요 (위의 [⚠️ 함정 섹션](#4-️-시작-전-꼭-알아둘-함정-자기-자신을-잠그지-않는-법) 참고). 룰 자체는 다 들어가 있고, 실제 클라우드 서버에선 그대로 작동해요. **개념 학습 목적**으론 여기까지로 충분.

만약 진짜 동작시키고 싶다면 컨테이너를 이렇게 재생성:
```bash
exit                          # 컨테이너 나오기
docker rm ubuntu-ssh          # 기존 컨테이너 삭제
docker run -it --name ubuntu-ssh \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  ubuntu:latest bash
# 그리고 처음부터 다시
```

---

### Step 8. 최종 상태 확인

#### 🎯 목적
방화벽 켜진 후 *현재 상태*를 자세히 본다.

#### ⌨️ 명령어
```bash
ufw status verbose
```

#### ✅ 성공 결과
```text
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
20022/tcp                  ALLOW IN    Anywhere
15034/tcp                  ALLOW IN    Anywhere
20022/tcp (v6)             ALLOW IN    Anywhere (v6)
15034/tcp (v6)             ALLOW IN    Anywhere (v6)
```

#### 🔍 결과 읽는 법

| 부분 | 의미 |
|---|---|
| `Status: active` | ✅ 방화벽 켜짐 |
| `Logging: on (low)` | 로그 기록 중 (낮은 수준) |
| `Default: deny (incoming)` | 기본 정책: 들어오는 건 차단 |
| `Default: allow (outgoing)` | 기본 정책: 나가는 건 허용 |
| `To` 열 | 어디로 향하는 트래픽? (보통 우리 서버의 포트) |
| `Action` 열 | 어떻게 처리? (ALLOW IN = 들어오는 거 허용) |
| `From` 열 | 어디서 오는 거? (`Anywhere` = 어디서든) |
| `(v6)` | IPv6용 룰 (v6는 미래의 IP 주소 체계) |

**핵심**: `20022/tcp`와 `15034/tcp` 두 줄이 `ALLOW IN`으로 보이면 우리가 원한 그림 완성. ✨

---

## 6. (참고) firewalld로 똑같이 하기

UFW가 표준이지만, **CentOS/RHEL 환경**에선 firewalld를 써요. 같은 결과를 firewalld로 하면 이렇게 됩니다.

```bash
# 설치 (CentOS/RHEL 기준)
yum install firewalld -y          # 또는 dnf install
systemctl start firewalld         # 시작
systemctl enable firewalld        # 부팅 시 자동 시작

# 포트 허용 (영구 적용을 위해 --permanent)
firewall-cmd --permanent --add-port=20022/tcp
firewall-cmd --permanent --add-port=15034/tcp

# 변경사항 적용
firewall-cmd --reload

# 확인
firewall-cmd --list-all
```

### 🤔 UFW와 firewalld 명령어 비교표

| 작업 | UFW | firewalld |
|---|---|---|
| 설치 | `apt install ufw` | `yum install firewalld` |
| 시작 | `ufw enable` | `systemctl start firewalld` |
| 포트 허용 | `ufw allow 20022/tcp` | `firewall-cmd --permanent --add-port=20022/tcp` |
| 변경 적용 | (즉시) | `firewall-cmd --reload` 필요 |
| 상태 확인 | `ufw status verbose` | `firewall-cmd --list-all` |
| 룰 삭제 | `ufw delete allow 20022/tcp` | `firewall-cmd --permanent --remove-port=20022/tcp` |

### 💡 알아두면 좋은 차이

- **UFW**: 변경 즉시 적용. 단순함이 강점.
- **firewalld**: `--permanent` 라는 옵션이 핵심. 안 붙이면 *임시*로만 적용되고 재부팅 시 사라짐. `--reload`로 활성화.

처음엔 UFW가 훨씬 직관적이에요. firewalld는 *zone(구역)* 개념이 추가돼서 더 복잡하지만, 그만큼 큰 환경에서 유연해요.

---

## 7. 자주 만나는 에러와 해결법

### ❌ `ufw: command not found`
**원인**: UFW가 안 깔림
**해결**:
```bash
apt update && apt install ufw -y
```

---

### ❌ `ERROR: problem running ufw-init`
**원인**: 컨테이너에 네트워크 권한이 부족함 (Docker 기본 컨테이너의 한계)
**해결**:
1. 학습 목적이면 무시하고 룰 설정만 익혀도 OK
2. 진짜 동작시키려면 `--cap-add=NET_ADMIN --cap-add=NET_RAW` 옵션으로 컨테이너 재생성

---

### ❌ enable 했더니 SSH 끊겼다 (실제 서버에서)
**원인**: SSH 포트 허용 룰 안 넣고 enable함
**해결**:
1. 진짜 데이터센터/클라우드 서버라면 *콘솔 접속* (웹 콘솔, KVM 등)으로 들어가서 `ufw disable` 후 룰 다시 짜기
2. 클라우드(AWS, GCP 등)라면 콘솔에서 보안그룹/방화벽 임시 해제 후 접근

---

### ❌ `Rules updated` 라고 떴는데 안 적용된 것 같음
**원인**: 룰은 들어갔지만 UFW 자체가 *비활성(inactive)* 상태
**확인**:
```bash
ufw status   # inactive면 enable 안 한 거
ufw enable   # 켜기
```

---

### ❌ 포트 열었는데도 외부에서 접속 안 됨
**확인 순서**:
1. 그 포트에서 *실제로 프로그램이 듣고 있나?*
   ```bash
   ss -tlnp | grep 20022
   ```
2. UFW 룰에 정말 들어가 있나?
   ```bash
   ufw status verbose
   ```
3. *외부 방화벽*은? (클라우드라면 보안그룹/네트워크 ACL도 확인)
4. *컨테이너 포트 매핑*은? (Docker라면 `-p 20022:20022` 같은 옵션 필요)

**핵심 개념**: 방화벽 여러 겹이 있을 수 있어요. 우리가 연 건 *Ubuntu 안*. Docker 호스트와 클라우드 보안그룹은 별개로 다 열어야 함.

---

### ❌ 룰 잘못 만들었다, 지우고 싶음
**해결**:
```bash
# 1) 번호로 룰 보기
ufw status numbered

# 결과 예:
# [ 1] 20022/tcp     ALLOW IN    Anywhere
# [ 2] 15034/tcp     ALLOW IN    Anywhere

# 2) 번호로 삭제
ufw delete 2

# 또는 룰을 직접 지정해서 삭제
ufw delete allow 15034/tcp
```

---

### ❌ 모든 룰 다 지우고 처음부터 다시
```bash
ufw reset       # 모든 룰 초기화 + 비활성화
```
**주의**: 진짜 운영 서버에선 함부로 쓰지 마세요. 연습 컨테이너에선 자유롭게.

---

## 8. 전체 흐름 한눈에 보기

```text
[ Ubuntu 컨테이너 안 ]
     │
     │ apt install ufw -y                       ← Step 1: UFW 설치
     │
     │ ufw status                               ← Step 2: 시작점 확인 (inactive)
     │
     │ ufw default deny incoming                ← Step 3: 기본 정책 (들어오는 건 차단)
     │ ufw default allow outgoing               ←        (나가는 건 허용)
     │
     │ ufw allow 20022/tcp     🔑 ⚠️ 가장 중요   ← Step 4: SSH 포트 먼저!
     │
     │ ufw allow 15034/tcp                      ← Step 5: 서비스 포트
     │
     │ ufw show added                           ← Step 6: 룰 미리 확인
     │
     │ ufw enable                               ← Step 7: 활성화 (y 입력)
     │
     │ ufw status verbose                       ← Step 8: 최종 확인
     │
     ▼
[ 방화벽 동작 중! ]
   - 20022/tcp ✅ 허용
   - 15034/tcp ✅ 허용
   - 그 외 들어오는 통신 ❌ 차단
   - 나가는 통신 ✅ 모두 허용
```

---

## 9. 다음에 해볼 만한 것들

### 🔵 초급
- [ ] **특정 IP만 SSH 허용하기**
  ```bash
  ufw allow from 203.0.113.45 to any port 20022 proto tcp
  ```
  → 회사 사무실 IP에서만 SSH 가능하게 만들기
- [ ] **로그 보기**
  ```bash
  ufw status verbose             # 로깅 켜져 있는지 확인
  tail -f /var/log/ufw.log       # 실시간 로그 보기
  ```
  → 누가 차단당했는지, 시도가 얼마나 많은지 보면 흥미로움

### 🟡 중급
- [ ] **outgoing도 빡세게 막아보기**
  ```bash
  ufw default deny outgoing
  ufw allow out 53/udp           # DNS 허용
  ufw allow out 80/tcp           # HTTP 허용 (apt 등)
  ufw allow out 443/tcp          # HTTPS 허용
  ```
  → 보안 등급이 한 단계 더 올라감
- [ ] **속도 제한 룰 (브루트포스 방어)**
  ```bash
  ufw limit 20022/tcp
  ```
  → 한 IP에서 30초 안에 6번 이상 접속 시도하면 차단

### 🔴 실전
- [ ] **fail2ban 같이 쓰기** → SSH 시도 실패 N번이면 자동으로 그 IP 차단
- [ ] **클라우드 보안그룹 + UFW 이중 방화벽** 구성
- [ ] **iptables 직접 다뤄보기** → UFW의 내부 동작 이해

---

## 📌 마무리: 이번에 진짜 배운 것

명령어 외우기가 아니라, **이런 사고방식**이 핵심이에요:

### 1. "기본은 막고, 필요한 것만 연다" (Deny by default)
보안의 가장 기본 원칙. 모르는 건 일단 막는다.

### 2. "순서가 중요하다"
- 룰 먼저 → enable 나중. 반대로 하면 자기가 갇힘.
- 진짜 운영 서버에선 이 순서가 생사를 가름.

### 3. "방화벽은 한 겹이 아니다"
- 컨테이너 안의 UFW
- Docker 호스트의 iptables
- 클라우드 보안그룹
- 사무실 방화벽
- → 다 별개. 어디 한 군데라도 막혀 있으면 통신 안 됨.

### 4. "확인 → 적용 → 재확인"
- 룰 넣기 전 `status`로 확인
- 룰 넣고 `show added`로 미리보기
- 활성화 후 `status verbose`로 재확인
- → 운영 환경에선 *확인 없이 명령 치는 것*이 사고의 시작.

### 5. "에러 메시지는 가장 친절한 선생님"
- `ERROR: problem running ufw-init` → 권한 부족이라는 힌트
- `Command may disrupt existing ssh connections` → 너 잠길 수 있다는 친절한 경고
- → 에러를 안 두려워하고 *읽는 습관*이 진짜 실력.

---

수고하셨어요! 이제 SSH(전 문서) + 방화벽(이 문서)으로 **최소한의 서버 보안 기본기**가 잡혔어요. 🎉
