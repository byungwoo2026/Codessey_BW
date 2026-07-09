FROM ubuntu:latest


# apt-get uodate     : ubuntu pagacke 최신화
# &&                 : 앞의 명령어가 성공하였을때 후속 작업 진행
# apt-get install -y : 후속에 나오는 package 설치 
#---------------------------------------------------------------------------------------
# procps             : 프로세스 상태를 확인하는 명령어들이 들어 있는 패키지 
#                    : ps -ef    >> 프로세스 목록 확인
#                    : top       >> CPU, 메모리 사용량 실시간 확인
#                    : free -m   >> 시스템 메모리 사용량 확인
#                    : pgrep -f agent-leak-app   >>  실행중인 agent-leak-app 의 PID 찾기
#---------------------------------------------------------------------------------------
# iproute2           : 네트워크 상태를 확인 하는 도구
#                    : ss -ltn   >> 현재 열려 있는 TCP 포트를 확인 (ss -ltn | grep 15034)
#---------------------------------------------------------------------------------------  
# net-tools          : 예전 방식의 네트워크 명령어 모음
#                    : netstat -tuln  >> 열려 있는 포트 확인
#                    : ifconfig
#---------------------------------------------------------------------------------------  
# curl               : HTTP 요청을 보내는 도구 (앱이 설아 있는지, 응답이 느려졌는지,.,.)
#                    : curl http://localhost:15034
#                    : curl http://localhost:15034/health
#---------------------------------------------------------------------------------------
# bash               : Linux 쉘
#                    : #!/usr/bin/env bash    >>  이 파일을 bash 쉘로 실행 해줘줘
#---------------------------------------------------------------------------------------
# rm -rf /var/lib/apt/lists/*  : apt-get update가 받아온 목록 캐시를 삭제 하는 명령
#                              : apt-get update를 하면 /var/lib/apt/lists/ 아래에 패키지 목록 파일들이 저장장
#---------------------------------------------------------------------------------------

RUN apt-get update && apt-get install -y \
    procps \
    iproute2 \
    net-tools \
    curl \
    vim \
    bash \
    && rm -rf /var/lib/apt/lists/*


#---------------------------------------------------------------------------------------
# Docker 이미지 안에 agentuser 라는 일반 사용자 계정을 만드는 명령
# RUN        : DOCKER 이미지를 빌드할때 실행 하라는 뜻
# useradd    : Linux 에서 새사용자를 만드는 명령어
# -m         : 사용자의 홈 디렉토리도 같이 만들라는 옵션
# agentuser  : 만들고자 하는 사용자 이름
#---------------------------------------------------------------------------------------
RUN useradd -m agentuser 

#---------------------------------------------------------------------------------------
# Docker 컨테이너 안에서 agent-leak-app 이 실행될때 필요한 환경변수를 미리 설정 하는 부분
# 환경변수는 프로그램 전달하는 설정값
#---------------------------------------------------------------------------------------
ENV AGENT_HOME=/home/agentuser/agent
# 앱의 기준 폴더를 의미 합니다, agent-leak-app 이 사용할 작업공간 (뒤에 나오는 업로드 폴더, 키폴더,로그폴더도 이 안에 만들어짐)

ENV AGENT_PORT=15034
#앱이 사용할 포토 번호 , 외부에서 접근할때 Docker 실행시 > docker run -p 15034:15034 ...(내 PC의 15034 포트 -> 컨터이너 15034 연결)

ENV AGENT_UPLOAD_DIR=/home/agentuser/agent/upload_files
#앱이 업로드할 파일을 저장할 폴더

ENV AGENT_KEY_PATH=/home/agentuser/agent/api_keys
#앱이 API 카 파일을 찾을 경로 (여기에, secret.key 가 있어야 함)

ENV AGENT_LOG_DIR=/home/agentuser/agent/logs
#앱이 로그 파일을 기록할 폴더

ENV MEMORY_LIMIT=256
#메모리 제한 값, 메모리를 256MB 이상 쓰면 보호정책을 작동

ENV CPU_MAX_OCCUPY=80
#CPU 사용률 제한값, CPU 사용률이 80%를 넘으면 WATCHDOG 보호 정책 작동

ENV MULTI_THREAD_ENABLE=true
#멀티스레드 기능을 켤지 끌지 정하는 값

RUN mkdir -p $AGENT_UPLOAD_DIR $AGENT_KEY_PATH $AGENT_LOG_DIR
#Docker 이미지를 만들 때, 앱이 필요로 하는 폴더들을 미리 생성하는 명령 

RUN echo "agent_api_key_test" > $AGENT_KEY_PATH/secret.key
#Docker 이미지를 만들 때 secret.key 파일을 생성하고, 그 안에 agent_api_key_test라는 내용을 넣는 명령

WORKDIR /home/agentuser/agent
#Docker 이미지 안에서 현재 작업 디렉터리를 설정하는 명령 (일반터미널 cd /home/agentuser/agent 비슷슷)

COPY agent-leak-app-x86 ./agent-leak-app-x86
#내 컴퓨터의 현재 빌드 폴더에 있는 agent-leak-app 파일을 Docker 이미지 안의 /home/agentuser/agent/agent-leak-app으로 복사

COPY monitor.sh ./monitor.sh
#내 컴퓨터의 현재 빌드 폴더에 있는 monitor.sh 파일을 Docker 이미지 안의 /home/agentuser/agent/monitor.sh로 복사
# (COPY의 왼쪽 파일은 docker build를 실행하는 폴더 안에 있어야 합니다)

RUN chmod +x ./agent-leak-app-x86 ./monitor.sh
#  ./agent-leak-app-x86 ./monitor.sh 에 실행 권한을 부여 하는 명령

RUN chown -R agentuser:agentuser /home/agentuser/agent
#chown (파일이나 폴더의 소유자를 변경하는 명령), -R(recursive, 즉 하위 폴더와 파일까지 전부 적용하라는 뜻)
#agentuser:agentuser(앞의 agentuser는 사용자 이름, 뒤의 agentuser는 그룹 이름)
#/home/agentuser/agent (소유자를 바꿀 대상 폴더)

USER agentuser
# 명령과 컨테이너 실행 명령을 agentuser 권한으로 실행하라는 뜻 (USER >> DOCKER 의 전용명령어 , 이 이후 명령을 어떤 사용자 권한으로 실행할지 결정정)

EXPOSE 15034
#이 컨테이너는 15034 포트를 사용하는 앱이라는 것을 Dockerfile에 명시한다. 단, 실제 연결은 docker run -p 15034:15034가 필요하다.

CMD ["./agent-leak-app-x86"]
#CMD는 컨테이너의 기본 실행 명령입니다. /home/agentuser/agent/agent-leak-app (동일)