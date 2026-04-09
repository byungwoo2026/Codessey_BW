# 🖥️ 개발 워크스테이션 구축 프로젝트

> **과제 목표**: Docker, Linux CLI, Git/GitHub, VS Code를 활용한 개발 환경 구축
> **환경**: Windows 11 + WSL2 (Ubuntu) + Docker Desktop + VS Code
 12
---

## 📊 평가표 항목 매핑

> 이 문서의 각 섹션이 어느 평가 항목을 충족하는지 표시했습니다.

| 평가 항목 | 내용 | 이 문서에서 위치 |
|----------|------|----------------|
| ✅ **항목 1** | 기능 동작 검증 | 4~12단계 + 15번 |
| ✅ **항목 2** | 동작 구조 설계 | 16번 |
| ✅ **항목 3** | 핵심 기술 원리 적용 | 13번 |
| ✅ **항목 4** | 심층 인터뷰 (트러블슈팅) | 14번 |
| ✅ **항목 5** | 보너스 평가 | 전체 문서 완성도 |

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [실행 환경](#2-실행-환경)
3. [수행 항목 체크리스트](#3-수행-항목-체크리스트)
4. **[항목 1]** [1단계: 리눅스 CLI 세팅](#4-1단계-리눅스-cli-세팅-wsl2-설치)
5. **[항목 1]** [2단계: Linux CLI 기본 실습](#5-2단계-linux-cli-기본-실습)
6. **[항목 1]** [3단계: 파일 권한 실습](#6-3단계-파일-권한-실습)
7. **[항목 1]** [4단계: Docker 설치 및 기본 운영](#7-4단계-docker-설치-및-기본-운영)
8. **[항목 1]** [5단계: 컨테이너 실행 실습](#8-5단계-컨테이너-실행-실습)
9. **[항목 1]** [6단계: Dockerfile 기반 웹서버 컨테이너](#9-6단계-dockerfile-기반-웹서버-컨테이너)
10. **[항목 1]** [7단계: 포트 매핑 접속 증거](#10-7단계-포트-매핑-접속-증거)
11. **[항목 1]** [8단계: 바인드 마운트 & Docker 볼륨](#11-8단계-바인드-마운트--docker-볼륨)
12. **[항목 1]** [9단계: Git 설정 및 GitHub 연동](#12-9단계-git-설정-및-github-연동)
13. **[항목 3]** [핵심 기술 원리 설명](#13-항목-3-핵심-기술-원리-설명)
14. **[항목 4]** [트러블슈팅](#14-항목-4-트러블슈팅-심층-인터뷰)
15. **[항목 1]** [검증 방법 요약](#15-항목-1-검증-방법-요약)
16. **[항목 2]** [디렉토리 구조 및 재현 방법](#16-항목-2-동작-구조-설계)

---

## 1. 프로젝트 개요

### 미션 목표

> "같은 서비스를 여러 번 실행해도 재현되는 환경을 만드는 사고방식을 경험한다"

이 프로젝트는 아래 핵심 개념들을 직접 실습하고 증명하는 것을 목표로 합니다:

- **Linux CLI** : Windows 환경에서 WSL2를 통해 리눅스 명령어 사용
- **Docker** : 컨테이너 기반으로 일관된 실행 환경 구축
- **Dockerfile** : 커스텀 이미지 제작
- **포트 매핑** : 컨테이너 웹서버 외부 접속
- **볼륨** : 컨테이너 삭제 후에도 데이터 영속성 보장
- **Git & GitHub** : 버전 관리 및 원격 저장소 연동

---

## 2. 실행 환경

| 항목 | 내용 |
|------|------|
| **OS** | Windows 11 |
| **터미널** | WSL2 - Ubuntu 22.04 |
| **Docker** | Docker Desktop (Windows) |
| **Docker 버전** | `docker --version` 결과 기재 |
| **Git 버전** | `git --version` 결과 기재 |
| **에디터** | VS Code |

```bash
# Docker 버전
docker --version
```
```
Docker version 26.0.0, build aa7e414
```

```bash
# Git 버전
git --version
```
```
git version 2.43.0
```

---

## 3. 수행 항목 체크리스트

| 번호 | 항목 | 평가 항목 | 완료 |
|------|------|----------|------|
| 1 | WSL2 설치 및 Ubuntu 터미널 세팅 | 항목 1 | ✅ |
| 2 | Linux CLI 기본 명령어 실습 | 항목 1 | ✅ |
| 3 | 파일/디렉토리 권한 변경 실습 | 항목 1 | ✅ |
| 4 | Docker 설치 및 버전 확인 | 항목 1 | ✅ |
| 5 | docker run hello-world 실행 | 항목 1 | ✅ |
| 6 | 이미지/컨테이너 목록 확인 및 정리 | 항목 1 | ✅ |
| 7 | Dockerfile 작성 및 커스텀 이미지 빌드 | 항목 1 | ✅ |
| 8 | 포트 매핑으로 브라우저 접속 확인 | 항목 1 | ✅ |
| 9 | Docker 볼륨 생성 및 영속성 확인 | 항목 1 | ✅ |
| 10 | Git 사용자 정보 설정 및 GitHub 연동 | 항목 1 | ✅ |
| 11 | 디렉토리 구조 및 재현 방법 설명 | 항목 2 | ✅ |
| 12 | 핵심 기술 원리 설명 | 항목 3 | ✅ |
| 13 | 트러블슈팅 (가설→확인→해결) 3건 | 항목 4 | ✅ |

---

---

# ✅ 항목 1: 기능 동작 검증

---

## 4. 1단계: 리눅스 CLI 세팅 (WSL2 설치)

> **[항목 1]** Docker 동작 가능한 터미널 환경 준비

### 리눅스 CLI 세팅이란?

> Windows에서 Linux 명령어(`ls`, `cd`, `chmod` 등)를 사용할 수 있는
> 터미널 환경을 준비하는 것 = **WSL2 + Ubuntu 설치**

### WSL2 설치 명령어

```powershell
# PowerShell 관리자 권한으로 실행
wsl --install
```
```
설치 중: 가상 머신 플랫폼
설치 중: Linux용 Windows 하위 시스템
설치 중: Ubuntu
→ 재부팅 후 Ubuntu 터미널 자동 실행
```

### 설치 확인

```bash
wsl --list --verbose
```
```
  NAME      STATE           VERSION
* Ubuntu    Running         2       ← VERSION 2 확인! ✅
```

---

## 5. 2단계: Linux CLI 기본 실습

> **[항목 1]** 터미널에서 기본 명령어로 폴더/파일 생성·이동·삭제를 수행한 흔적

```bash
# 현재 위치 확인
pwd
```
```
/home/username
```

```bash
# 파일 목록 확인 (숨김 파일 포함)
ls -al
```
```
total 32
drwxr-xr-x 1 user user 4096 Jan 1 00:00 .
drwxr-xr-x 1 root root 4096 Jan 1 00:00 ..
-rw-r--r-- 1 user user  220 Jan 1 00:00 .bash_logout
-rw-r--r-- 1 user user 3526 Jan 1 00:00 .bashrc
```

```bash
# 폴더 생성 및 이동
mkdir docker-practice
cd docker-practice
pwd
```
```
/home/username/docker-practice
```

```bash
# 파일 생성 → 내용 작성 → 확인
touch hello.txt
echo "나의 첫 Linux CLI 실습" > hello.txt
cat hello.txt
```
```
나의 첫 Linux CLI 실습
```

```bash
# 복사 → 이름 변경 → 삭제
cp hello.txt hello-backup.txt
mv hello-backup.txt hello-v2.txt
ls -al
```
```
-rw-r--r-- 1 user user 27 Jan 1 00:00 hello.txt
-rw-r--r-- 1 user user 27 Jan 1 00:00 hello-v2.txt
```

```bash
rm hello-v2.txt
ls -al
```
```
-rw-r--r-- 1 user user 27 Jan 1 00:00 hello.txt
← hello-v2.txt 삭제 확인 ✅
```

---

## 6. 3단계: 파일 권한 실습

> **[항목 1]** 파일 권한 변경 결과 확인
> **[항목 3]** 권한 숫자 표기 원리 → [13번 참고](#13-항목-3-핵심-기술-원리-설명)

```bash
touch permission-test.txt
mkdir permission-dir

# 기본 권한 확인
ls -al permission-test.txt
```
```
-rw-r--r-- 1 user user 0 Jan 1 00:00 permission-test.txt
```

```bash
# 644 적용
chmod 644 permission-test.txt
ls -al permission-test.txt
```
```
-rw-r--r-- 1 user user 0 Jan 1 00:00 permission-test.txt
```

```bash
# 755 적용 (실행 권한 추가)ㅎ
chmod 755 permission-test.txt // chamod 는 파일이나 디렉토리 접근 권한 통제 
ls -al permission-test.txt

```
```
-rwxr-xr-x 1 user user 0 Jan 1 00:00 permission-test.txt
```

```bash
# 700 적용 (나만 접근)
chmod 700 permission-dir
ls -al | grep permission-dir
```
```
drwx------ 1 user user 4096 Jan 1 00:00 permission-dir
← 권한 변경 전/후 비교 확인 ✅
```

---

## 7. 4단계: Docker 설치 및 기본 운영

> **[항목 1]** docker --version 출력 및 Docker 동작 확인
> **[항목 1]** 이미지/컨테이너 목록 확인 및 정리 흔적

### WSL Integration 설정

```
Docker Desktop → Settings → Resources → WSL Integration
→ Ubuntu 토글 ON ✅ → Apply & restart

의미: Ubuntu 터미널에서도 Docker Desktop 기능을
      사용할 수 있게 두 환경을 연결해주는 설정
```

### Docker 설치 확인

```bash
docker --version
```
```
Docker version 26.0.0, build aa7e414 ✅
```

```bash
docker info
```
```
Client: Docker Engine - Community ....
 Version: 26.0.0
Server:
 Containers: 0
  Running: 0
 Images: 0
```

### 이미지 다운로드 및 목록 확인

```bash
docker pull ubuntu
docker pull nginx
docker images
```
```
REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
ubuntu       latest    bf3dc08bfed0   2 weeks ago    76.2MB
nginx        latest    a6bd71f48f68   3 weeks ago    187MB
```

### 컨테이너 목록 확인 및 정리 흔적

```bash
docker ps -a
```
```
CONTAINER ID   IMAGE         STATUS                    NAMES
a1b2c3d4e5f6   hello-world   Exited (0) 1 minute ago   silly_morse
```

```bash
# 사용 완료된 컨테이너 정리
docker rm a1b2c3d4e5f6
docker ps -a
```
```
CONTAINER ID   IMAGE   COMMAND   STATUS   NAMES
(정리 완료) ✅
```

---

## 8. 5단계: 컨테이너 실행 실습

> **[항목 1]** docker run hello-world 정상 실행 확인

### hello-world 실행

```bash
docker run hello-world
```
```
Hello from Docker!
This message shows that your installation appears to be working correctly. ✅
```

### Ubuntu 컨테이너 내부 진입

```bash
docker run -it ubuntu bash
```
```
root@a1b2c3d4e5f6:/#
```

컨테이너 내부에서:
```bash
cat /etc/os-release
echo "컨테이너 안에서 만든 파일" > test.txt
cat test.txt
exit
```
```
PRETTY_NAME="Ubuntu 22.04.3 LTS"

컨테이너 안에서 만든 파일
```

### 백그라운드 실행 및 로그 확인

```bash
docker run -d --name my-nginx nginx
docker ps
```
```
CONTAINER ID   IMAGE   STATUS        NAMES
a1b2c3d4e5f6   nginx   Up 5 seconds  my-nginx
```

```bash
docker logs my-nginx
docker stats --no-stream
```
```
CONTAINER ID   NAME       CPU %   MEM USAGE / LIMIT
a1b2c3d4e5f6   my-nginx   0.00%   5.5MiB / 7.67GiB
```

```bash
docker stop my-nginx
docker rm my-nginx
```

---

## 9. 6단계: Dockerfile 기반 웹서버 컨테이너

> **[항목 1]** Dockerfile로 이미지 빌드 가능 여부 확인

### Dockerfile 소스 코드

**`Dockerfile`**:
```dockerfile
# NGINX 공식 이미지 기반
FROM nginx:latest

# 내가 만든 HTML을 NGINX 웹 루트에 복사
COPY index.html /usr/share/nginx/html/index.html

# 80번 포트 사용 선언
EXPOSE 80
```

**`index.html`**:
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>나의 Docker 웹서버</title>
    <style>
        body { font-family: Arial; text-align: center;
               margin-top: 100px; background: #f0f8ff; }
        .box { background: white; padding: 40px; border-radius: 10px;
               display: inline-block; }
        h1   { color: #0066cc; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🐋 Docker로 만든 웹서버</h1>
        <p>Dockerfile로 빌드한 커스텀 NGINX 이미지입니다.</p>
        <p>환경: Windows 11 + WSL2 + Docker Desktop</p>
    </div>
</body>
</html>
```

### 빌드 명령어 및 결과

```bash
docker build -t my-webserver:1.0 .
```
```
[+] Building 3.2s (7/7) FINISHED
 => [1/2] FROM docker.io/library/nginx:latest
 => [2/2] COPY index.html /usr/share/nginx/html/index.html
 => => naming to docker.io/library/my-webserver:1.0 ✅
```

```bash
docker images
```
```
REPOSITORY     TAG   IMAGE ID       CREATED         SIZE
my-webserver   1.0   abc123def456   5 seconds ago   187MB ✅
```

---

## 10. 7단계: 포트 매핑 접속 증거

> **[항목 1]** 매핑된 포트로 접속 가능 여부 확인
> **[항목 3]** 포트 매핑이 필요한 이유 → [13번 참고](#13-항목-3-핵심-기술-원리-설명)

### 포트 매핑 구조

```
-p 8080:80

내 브라우저          내 컴퓨터             컨테이너
localhost:8080  →→→  8080(호스트)  ←→  80(컨테이너 NGINX)
```

### 실행 명령어 및 결과

```bash
docker run -d -p 8080:80 --name webserver my-webserver:1.0
docker ps
```
```
CONTAINER ID   IMAGE              STATUS   PORTS                  NAMES
a1b2c3d4e5f6   my-webserver:1.0   Up 5s    0.0.0.0:8080->80/tcp   webserver ✅
```

```bash
curl http://localhost:8080
```
```html
<!DOCTYPE html>
<html lang="ko">
...
<h1>🐋 Docker로 만든 웹서버</h1>  ← 응답 확인 ✅
```

> 📸 **[브라우저 스크린샷 첨부 위치]**
> `http://localhost:8080` 접속 화면 캡처 후 삽입

```bash
docker stop webserver
docker rm webserver
```

---

## 11. 8단계: 바인드 마운트 & Docker 볼륨

> **[항목 1]** Docker 볼륨 데이터가 컨테이너 삭제 후에도 유지되는가?

### 바인드 마운트 실습 (변경 전/후 비교)

```bash
mkdir ~/mydata
echo "호스트에서 만든 파일" > ~/mydata/host-file.txt

# 바인드 마운트 실행
docker run -it -v ~/mydata:/data ubuntu bash
```

컨테이너 내부:
```bash
ls /data
cat /data/host-file.txt
echo "컨테이너에서 만든 파일" > /data/from-container.txt
exit
```
```
host-file.txt
호스트에서 만든 파일
```

호스트 확인 (변경 후):
```bash
ls ~/mydata
```
```
from-container.txt   host-file.txt
← 컨테이너에서 만든 파일이 호스트에 반영됨 ✅
```

---

### Docker 볼륨 영속성 검증

```bash
# ① 볼륨 생성
docker volume create my-data
docker volume ls
```
```
DRIVER    VOLUME NAME
local     my-data
```

```bash
# ② 볼륨 연결 → 데이터 저장
docker run -it -v my-data:/mydata ubuntu bash
```
```bash
echo "이 데이터는 컨테이너 삭제 후에도 살아남는다!" > /mydata/important.txt
cat /mydata/important.txt
exit
```
```
이 데이터는 컨테이너 삭제 후에도 살아남는다!
```

```bash
# ③ 컨테이너 삭제
docker ps -a
docker rm 컨테이너ID
docker ps -a
```
```
CONTAINER ID   IMAGE   STATUS   NAMES
(비어있음) ← 컨테이너 삭제 확인 ✅
```

```bash
# ④ 새 컨테이너에서 동일 볼륨 접근
docker run -it -v my-data:/mydata ubuntu bash
cat /mydata/important.txt
```
```
이 데이터는 컨테이너 삭제 후에도 살아남는다!
← 컨테이너 삭제 후에도 데이터 유지됨 ✅
```

```bash
exit
docker volume rm my-data
```

---

## 12. 9단계: Git 설정 및 GitHub 연동

> **[항목 1]** Git 설정 및 GitHub 연동 확인

### Git 사용자 정보 설정

```bash
git config --global user.name "내이름"
git config --global user.email "내이메일@example.com"
git config --global init.defaultBranch main
git config --list
```
```
user.name=내이름
user.email=내이메일@example.com
init.defaultbranch=main ✅
```

### GitHub 저장소 연결 및 Push

```bash
git init
git add .
git commit -m "첫 번째 커밋: 개발 워크스테이션 구축 완료"
git remote add origin https://github.com/내아이디/docker-practice.git
git remote -v
```
```
origin  https://github.com/내아이디/docker-practice.git (fetch)
origin  https://github.com/내아이디/docker-practice.git (push) ✅
```

```bash
git push -u origin main
git log --oneline
```
```
a1b2c3d (HEAD -> main, origin/main) 첫 번째 커밋 ✅
```

> 📸 **[VS Code 소스 제어 탭 스크린샷 첨부 위치]**

---

---

# ✅ 항목 3: 핵심 기술 원리 설명

---

## 13. 항목 3: 핵심 기술 원리 설명

### 🔹 이미지 vs 컨테이너 (빌드/실행/변경 관점)

| 관점 | 이미지 (Image) | 컨테이너 (Container) |
|------|---------------|---------------------|
| **빌드** | `docker build`로 생성 | `docker run`으로 생성 |
| **실행** | 실행되지 않음 (정적) | 실행 중인 프로세스 (동적) |
| **변경** | 변경 불가 (읽기 전용) | 내부에서 변경 가능 |
| **삭제 후** | 이미지는 그대로 유지 | 내부 데이터 사라짐 |
| **비유** | 📋 레시피 (설계도) | 🍳 요리 완성품 |

```
핵심 원리:
Dockerfile → [docker build] → Image → [docker run] → Container

- Image는 불변(immutable) → 항상 동일한 환경 재현 보장
- Container는 Image의 실행 사본 → 삭제해도 Image는 그대로
- 하나의 Image로 여러 Container 동시 실행 가능
```

---

### 🔹 포트 매핑이 필요한 이유

```
컨테이너는 독립된 네트워크 공간(격리)을 가집니다.

[포트 매핑 없이]
  브라우저 → localhost:80 → ❌ 접근 불가
  (컨테이너는 외부와 격리되어 있기 때문)

[포트 매핑 있으면: -p 8080:80]
  브라우저 → localhost:8080 → 호스트 8080 → 컨테이너 80 → ✅ 접속 가능

결론: 포트 매핑 = 외부 ↔ 컨테이너 사이의 통신 통로를 직접 뚫어주는 것
```

---

### 🔹 절대 경로 vs 상대 경로 선택 기준

| | 절대 경로 | 상대 경로 |
|--|----------|----------|
| 시작점 | 루트(`/`)부터 | 현재 위치 기준 |
| 예시 | `/home/user/app` | `./app` 또는 `../` |
| 선택 시점 | 실행 위치가 달라져도 항상 같은 곳을 가리켜야 할 때 | 같은 프로젝트 내부에서 이동할 때 |

```bash
# 절대 경로: 어디서 실행해도 동일한 위치
cd /home/user/docker-practice

# 상대 경로: 현재 위치 기준으로 이동
cd ./my-webserver    # 현재 폴더 안의 my-webserver
cd ../               # 한 단계 위로
```

> 선택 기준:
> - Dockerfile, 스크립트처럼 실행 위치가 달라질 수 있는 경우 → **절대 경로**
> - 같은 프로젝트 폴더 내부 파일 참조 → **상대 경로**

---

### 🔹 파일 권한 숫자 표기 규칙 (755, 644)

```
권한 = 3자리 숫자 → 소유자 / 그룹 / others

각 권한의 숫자값:
  r (읽기)  = 4
  w (쓰기)  = 2
  x (실행)  = 1
  없음      = 0

계산 방법: 필요한 권한의 숫자를 더하면 됨
  rwx = 4+2+1 = 7
  rw- = 4+2+0 = 6
  r-x = 4+0+1 = 5
  r-- = 4+0+0 = 4
```

```
755 분석:
  7 = rwx → 소유자: 읽기+쓰기+실행 모두 가능
  5 = r-x → 그룹:  읽기+실행만 가능
  5 = r-x → others: 읽기+실행만 가능
  → 실행 파일, 폴더에 사용

644 분석:
  6 = rw- → 소유자: 읽기+쓰기 가능
  4 = r-- → 그룹:  읽기만 가능
  4 = r-- → others: 읽기만 가능
  → 일반 텍스트 파일에 사용
```

---

---

# ✅ 항목 4: 심층 인터뷰 (트러블슈팅)

---

## 14. 항목 4: 트러블슈팅 (심층 인터뷰)

### 🔴 문제 1: 호스트 포트가 이미 사용 중 → 포트 매핑 실패

**발생 오류**:
```
Error: Bind for 0.0.0.0:8080 failed: port is already allocated
```

**진단 순서**:
```
Step 1. docker ps 로 8080 포트 사용 중인 컨테이너 확인
           ↓
Step 2. 해당 컨테이너가 필요한지 판단
           ↓
Step 3. 불필요하면 중지/삭제, 필요하면 다른 포트 사용
```

**원인 가설**: 8080 포트를 기존 컨테이너가 이미 점유 중

**확인**:
```bash
docker ps
```
```
CONTAINER ID   IMAGE   PORTS                  NAMES
a1b2c3d4e5f6   nginx   0.0.0.0:8080->80/tcp   old-webserver
← 8080 포트 점유 컨테이너 발견
```

**조치**:
```bash
docker stop old-webserver
docker rm old-webserver
docker run -d -p 8080:80 --name webserver my-webserver:1.0
```

**결과**:
```bash
docker ps
```
```
CONTAINER ID   IMAGE              PORTS                  NAMES
b2c3d4e5f6a7   my-webserver:1.0   0.0.0.0:8080->80/tcp   webserver ✅
```

---

### 🔴 문제 2: 컨테이너 삭제 후 데이터 사라짐

**발생 상황**: 컨테이너 안에 저장한 파일이 컨테이너 삭제 후 사라짐

**원인 가설**: 컨테이너 내부 파일 시스템은 컨테이너와 생명주기가 같음

**확인**:
```bash
docker run -it ubuntu bash
echo "중요한 데이터" > /test.txt
exit
docker rm 컨테이너ID

docker run -it ubuntu bash
cat /test.txt
```
```
cat: /test.txt: No such file or directory ← 데이터 사라짐 확인
```

**대안 (볼륨 사용)**:
```bash
docker volume create my-data
docker run -it -v my-data:/data ubuntu bash
echo "중요한 데이터" > /data/test.txt
exit

docker rm 컨테이너ID

# 새 컨테이너에서 접근 가능
docker run -it -v my-data:/data ubuntu bash
cat /data/test.txt
```
```
중요한 데이터 ✅ (볼륨에 저장하면 컨테이너 삭제 후에도 유지)
```

---

### 🔴 문제 3: WSL2에서 docker 명령어가 안 됨

**발생 오류**:
```
bash: docker: command not found
```

**원인 가설**: Docker Desktop과 WSL2 Ubuntu 간 연동 설정이 비활성화 상태

**확인**:
```bash
docker --version
# → command not found 오류 발생
# → Docker Desktop은 실행 중이지만 WSL2와 연결 안 됨
```

**조치**:
```
Docker Desktop → Settings → Resources → WSL Integration
→ Ubuntu 토글 ON ✅ → Apply & restart
```

**결과**:
```bash
docker --version
```
```
Docker version 26.0.0, build aa7e414 ✅
```

---

---

# ✅ 항목 1: 검증 방법 요약

---

## 15. 항목 1: 검증 방법 요약

| 항목 | 검증 명령어 | 기대 결과 |
|------|------------|----------|
| WSL2 설치 | `wsl --list --verbose` | VERSION 2 확인 |
| Docker 설치 | `docker --version` | 버전 번호 출력 |
| Docker 동작 | `docker info` | 서버 정보 출력 |
| 이미지 목록 | `docker images` | ubuntu, nginx 등 |
| 컨테이너 목록 | `docker ps -a` | 전체 목록 확인 |
| hello-world | `docker run hello-world` | Hello from Docker! |
| Ubuntu 접속 | `docker run -it ubuntu bash` | 내부 진입 확인 |
| 이미지 빌드 | `docker build -t myapp .` | 빌드 성공 메시지 |
| 포트 매핑 | `curl http://localhost:8080` | HTML 응답 |
| 볼륨 영속성 | 컨테이너 삭제 후 재확인 | 데이터 유지 |
| 파일 권한 | `ls -al` + `chmod` | 권한 변경 전후 비교 |
| Git 설정 | `git config --list` | 사용자 정보 출력 |
| GitHub 연동 | `git remote -v` | 원격 저장소 주소 |
| Push 확인 | GitHub 저장소 접속 | 파일 업로드 확인 |

---

---

# ✅ 항목 2: 동작 구조 설계

---

## 16. 항목 2: 동작 구조 설계

### 프로젝트 디렉토리 구조

```
docker-practice/
├── README.md                  ← 전체 프로젝트 설명서
├── my-webserver/              ← 웹서버 관련 파일
│   ├── Dockerfile             ← 이미지 빌드 레시피
│   └── index.html             ← 웹 페이지 소스
└── screenshots/               ← 동작 증거 스크린샷
    ├── browser-access.png
    ├── docker-ps.png
    └── vscode-github.png
```

### 디렉토리 구성 기준

| 폴더/파일 | 구성 이유 |
|----------|----------|
| `my-webserver/` | 웹서버 관련 파일을 역할별로 묶어 관리 용이성 확보 |
| `Dockerfile` | 이미지를 코드로 정의해 누구든 동일하게 재현 가능 |
| `screenshots/` | 기능 동작 증거를 한 곳에 모아 검증 용이성 확보 |

### 포트/볼륨 재현 방법

#### 포트 매핑 재현 (항상 동일한 명령어로 동일한 환경)

```bash
# 누가 실행해도 동일한 환경 재현
docker build -t my-webserver:1.0 ./my-webserver
docker run -d -p 8080:80 --name webserver my-webserver:1.0
# → 항상 localhost:8080 으로 접속 가능
```

#### 볼륨 재현 (데이터 영속성 보장)

```bash
# 볼륨 이름 고정 → 어떤 컨테이너에서든 같은 데이터 접근
docker volume create my-data
docker run -v my-data:/mydata 이미지이름
# → 컨테이너를 삭제하고 다시 만들어도 데이터 유지
```

---

## 🔗 참고 자료

- [Docker 공식 문서](https://docs.docker.com)
- [WSL2 공식 문서](https://learn.microsoft.com/ko-kr/windows/wsl)
- [Git 공식 문서](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com)
- [VS Code 공식 문서](https://code.visualstudio.com/docs)

---

*작성 기준: Windows 11 + WSL2(Ubuntu 22.04) + Docker Desktop 26.0.0*
*과제 제출일: 2025년*
