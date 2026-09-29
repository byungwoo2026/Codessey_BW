# Mini Git

Git의 핵심 구조를 학습하기 위한 CLI 기반 Mini Git입니다. 실제 Git 명령을 호출하지 않고, 커밋 그래프, 브랜치, 검색 인덱스, 정렬 알고리즘을 Python으로 직접 구현합니다.

## 과제 목표 설명

이 과제의 목표는 “Git 명령어를 외워서 쓰는 것”이 아니라, Git 내부에서 커밋이 어떤 구조로 저장되고 어떻게 탐색되는지 설명할 수 있게 되는 것입니다.

### 1. 커밋 그래프와 DAG 설명하기

Git의 커밋은 단순한 목록이 아니라 그래프 구조입니다. 커밋 하나는 자신보다 이전에 만들어진 부모 커밋을 가리킵니다.

```text
C000001
   ↓
C000002
   ↓
C000003
```

여기서 `C000003`의 부모는 `C000002`이고, `C000002`의 부모는 `C000001`입니다. 새 커밋은 항상 기존 커밋 위에 쌓이므로 과거 커밋이 미래 커밋을 부모로 가리키는 일은 없습니다.

그래서 커밋 그래프는 DAG입니다.

```text
DAG = Directed Acyclic Graph
    = 방향이 있고, 순환이 없는 그래프
```

쉽게 말하면 커밋은 시간상 앞으로만 쌓이기 때문에 다시 자기 자신으로 돌아오는 순환 구조가 생기지 않습니다.

### 2. 부모가 먼저 출력되는 로그 설명하기

일반적인 최신순 출력은 가장 최근 커밋부터 보여줍니다. 하지만 이 과제의 `LOG`는 부모 커밋이 자식 커밋보다 먼저 나오도록 출력합니다.

```text
부모 먼저 출력:

C000001
C000002
C000003
```

이렇게 출력하면 커밋이 어떤 순서로 쌓였는지 이해하기 쉽습니다. 그래프 관점에서는 부모가 먼저 나오고 자식이 나중에 나오는 순서이므로, 위상 정렬과 비슷한 성격을 가집니다.

쉽게 말하면 `LOG`는 “커밋이 만들어진 기반부터 차례대로 보여주는 기능”입니다.

### 3. 두 커밋 사이의 최단 경로 설명하기

`PATH <commit1> <commit2>`는 두 커밋이 그래프에서 어떻게 이어져 있는지 가장 짧은 길을 찾습니다.

예:

```text
C000001
   ↓
C000002
   ↓
C000003
```

```text
PATH C000001 C000003
```

결과:

```text
C000001->C000002->C000003
```

이 과제에서는 부모-자식 연결을 무방향 간선처럼 봅니다. 그래서 부모 방향으로도 이동할 수 있고, 자식 방향으로도 이동할 수 있다고 생각합니다. 가장 짧은 길을 찾기 위해 BFS를 사용합니다.

```text
BFS = 가까운 커밋부터 차례대로 넓게 탐색하는 방법
```

BFS는 먼저 발견한 가까운 경로가 최단 경로가 되기 때문에, 최단 경로 찾기에 적합합니다.

### 4. 특정 커밋의 조상 탐색 설명하기

`ANCESTORS <commit_hash>`는 특정 커밋에서 부모를 따라 계속 올라가며 모든 조상 커밋을 찾습니다.

예:

```text
C000001
   ↓
C000002
   ↓
C000003
```

`C000003`의 조상은 다음과 같습니다.

```text
C000002
C000001
```

쉽게 말하면 조상 탐색은 “이 커밋이 어떤 커밋들 위에 쌓였는지 거슬러 올라가는 기능”입니다.

### 5. 정렬 알고리즘 직접 구현 설명하기

이 과제에서는 Python의 기본 정렬 기능인 `sorted()`와 `list.sort()`를 사용하지 않습니다. 대신 직접 구현한 merge sort를 사용합니다.

merge sort는 데이터를 반으로 나누고, 각각을 정렬한 뒤 다시 합치는 방식입니다.

```text
[4, 1, 3, 2]
   ↓ 반으로 나누기
[4, 1] [3, 2]
   ↓ 다시 나누기
[4] [1] [3] [2]
   ↓ 정렬하며 합치기
[1, 4] [2, 3]
   ↓ 합치기
[1, 2, 3, 4]
```

시간복잡도는 평균과 최악 모두 `O(N log N)`입니다. 또한 같은 값이 있을 때 기존 순서를 유지할 수 있는 안정 정렬입니다.

이 프로그램에서는 같은 merge sort를 사용하되 비교 기준만 바꿉니다.

```text
LOG --sort-by=date    -> timestamp 기준 비교
LOG --sort-by=author  -> author 이름 기준 비교
```

### 6. 역색인 설명하기

검색을 할 때 모든 커밋을 처음부터 끝까지 검사하면 커밋 수가 많을수록 느려집니다. 그래서 이 과제에서는 역색인을 사용합니다.

역색인은 “검색어에서 커밋을 바로 찾을 수 있게 미리 만들어 둔 색인”입니다.

예를 들어 커밋 메시지가 다음과 같다면:

```text
add login feature
```

커밋 생성 시 아래처럼 미리 저장합니다.

```text
add     -> C000002
login   -> C000002
feature -> C000002
```

그러면 나중에:

```text
SEARCH login
```

을 실행했을 때 모든 커밋 메시지를 검사하지 않고, `login` 인덱스에서 바로 `C000002`를 찾을 수 있습니다.

author 검색도 같은 방식입니다.

```text
alice -> C000001, C000002
```

쉽게 말하면 역색인은 책 맨 뒤의 찾아보기와 비슷합니다. 원하는 단어를 찾으면 그 단어가 나오는 위치를 바로 알 수 있습니다.

## 실행 방법

Task5 폴더에서 실행합니다.

```powershell
cd C:\Codyssey26\본과정\Task5
python main.py
```

실행하면 아래 프롬프트가 나타납니다.

```text
mini-git>
```

종료는 `exit` 또는 `quit`을 입력합니다.

### 실행 후 사용 흐름

이 프로그램은 실제 Git처럼 먼저 저장소를 초기화한 다음 커밋을 만들고, 필요하면 브랜치를 생성하거나 이동하면서 작업합니다.

가장 기본적인 사용 순서는 다음과 같습니다.

```text
1. INIT으로 저장소 시작
2. COMMIT으로 첫 커밋 생성
3. BRANCH로 새 브랜치 생성
4. SWITCH로 브랜치 이동
5. COMMIT으로 새 커밋 추가
6. LOG, SEARCH, PATH, ANCESTORS로 커밋 확인
```

예를 들어 처음 실행 후 바로 `COMMIT`을 하면 안 됩니다. 아직 저장소가 초기화되지 않았기 때문입니다. 먼저 아래처럼 사용자 이름을 넣어 초기화해야 합니다.

```text
mini-git> INIT alice
```

여기서 `alice`는 커밋 작성자 이름입니다. 이후 만들어지는 커밋의 `author`가 됩니다.

## 명령어 예시

```text
mini-git> INIT alice
Initialized repository for alice
Current branch: main

mini-git> COMMIT "initial commit"
Committed C000001: initial commit

mini-git> BRANCH feature
Created branch: feature

mini-git> SWITCH feature
Switched to branch: feature

mini-git> COMMIT "add login feature"
Committed C000002: add login feature

mini-git> LOG
C000001 | alice | 2026-09-02T16:30:00 | parents=- | initial commit
C000002 | alice | 2026-09-02T16:30:01 | parents=C000001 | add login feature
```

## 지원 명령어

### 저장소 및 브랜치 명령

```text
INIT <user_name>
BRANCH <branch_name>
SWITCH <branch_name>
COMMIT <message>
```

### 로그, 탐색, 검색 명령

```text
LOG
LOG --sort-by=date
LOG --sort-by=author
PATH <commit1> <commit2>
ANCESTORS <commit_hash>
SEARCH <keyword>
SEARCH --author=<name>
```

## 명령어별 역할 상세 설명

### `INIT <user_name>`

저장소를 처음 시작하는 명령어입니다. 실제 Git의 `git init`과 비슷한 역할을 합니다. 다만 이 Mini Git에서는 사용자 이름도 함께 설정합니다.

예:

```text
mini-git> INIT alice
Initialized repository for alice
Current branch: main
```

이 명령을 실행하면 내부적으로 다음 일이 일어납니다.

- 저장소 상태가 초기화됩니다.
- 작성자 이름이 `alice`로 설정됩니다.
- `main` 브랜치가 만들어집니다.
- 현재 HEAD가 `main` 브랜치를 가리키게 됩니다.
- 기존에 메모리에 있던 커밋 정보는 새 저장소 기준으로 초기화됩니다.

쉽게 말하면 `INIT`은 “이제부터 Mini Git을 시작하겠다”는 준비 명령입니다.

### `COMMIT <message>`

현재 상태를 하나의 커밋으로 기록하는 명령어입니다. 실제 Git의 `git commit -m "메시지"`와 비슷한 역할입니다.

예:

```text
mini-git> COMMIT "initial commit"
Committed C000001: initial commit
```

이 명령을 실행하면 새 커밋 노드가 만들어집니다. 커밋에는 다음 정보가 저장됩니다.

- 커밋 hash
- 커밋 메시지
- 작성자 author
- 생성 시각 timestamp
- 부모 커밋 parents

첫 커밋은 부모가 없습니다.

```text
C000001
parents = -
```

두 번째 커밋부터는 현재 HEAD가 가리키던 커밋이 부모가 됩니다.

```text
C000001
   ↓
C000002

C000002.parents = [C000001]
```

또한 `COMMIT`을 실행할 때 검색을 위한 역색인도 같이 갱신됩니다. 예를 들어 메시지가 `"add login feature"`라면 아래 키워드들이 검색 인덱스에 들어갑니다.

```text
add
login
feature
```

그래서 나중에 아래 명령으로 찾을 수 있습니다.

```text
mini-git> SEARCH login
```

### `BRANCH <branch_name>`

새 브랜치를 만드는 명령어입니다. 실제 Git의 `git branch <branch_name>`과 비슷합니다.

예:

```text
mini-git> BRANCH feature
Created branch: feature
```

브랜치는 커밋을 복사하지 않습니다. 현재 HEAD가 가리키는 커밋 hash만 저장합니다.

예를 들어 현재 `main`이 `C000001`을 가리키고 있을 때 `BRANCH feature`를 실행하면:

```text
main    -> C000001
feature -> C000001
```

이렇게 됩니다. 두 브랜치가 같은 커밋에서 시작하는 것입니다.

쉽게 말하면 `BRANCH`는 “지금 위치에 새 이름표를 붙이는 명령”입니다.

### `SWITCH <branch_name>`

현재 작업 브랜치를 바꾸는 명령어입니다. 실제 Git의 `git switch <branch_name>`과 비슷합니다.

예:

```text
mini-git> SWITCH feature
Switched to branch: feature
```

이 명령은 커밋을 새로 만들지 않습니다. 단지 현재 HEAD 브랜치 이름만 바꿉니다.

```text
전:
HEAD -> main

후:
HEAD -> feature
```

이후 `COMMIT`을 실행하면 `main`이 아니라 `feature` 브랜치가 새 커밋을 가리키게 됩니다.

```text
main    -> C000001
feature -> C000002
```

쉽게 말하면 `SWITCH`는 “작업할 브랜치를 선택하는 명령”입니다.

### `LOG`

커밋 목록을 출력하는 명령어입니다. 실제 Git의 `git log`와 비슷하지만, 이 과제에서는 최신순이 아니라 부모 커밋이 자식 커밋보다 먼저 나오도록 출력합니다.

예:

```text
mini-git> LOG
C000001 | alice | 2026-09-02T16:30:00 | parents=- | initial commit
C000002 | alice | 2026-09-02T16:30:01 | parents=C000001 | add login feature
```

출력 한 줄의 의미는 다음과 같습니다.

```text
커밋hash | 작성자 | 생성시각 | 부모커밋 | 커밋메시지
```

예를 들어:

```text
C000002 | alice | 2026-09-02T16:30:01 | parents=C000001 | add login feature
```

이 뜻은 `C000002` 커밋은 `alice`가 만들었고, 부모 커밋은 `C000001`이며, 메시지는 `add login feature`라는 뜻입니다.

### `LOG --sort-by=date`

커밋 목록을 날짜 기준으로 정렬해서 출력합니다.

예:

```text
mini-git> LOG --sort-by=date
```

이 프로그램은 Python의 `sorted()`나 `list.sort()`를 쓰지 않고, 직접 구현한 merge sort로 정렬합니다. 날짜 기준 정렬은 커밋의 `timestamp` 값을 비교합니다.

쉽게 말하면 “커밋을 만든 시간 순서로 보여줘”라는 명령입니다.

### `LOG --sort-by=author`

커밋 목록을 작성자 이름 기준으로 정렬해서 출력합니다.

예:

```text
mini-git> LOG --sort-by=author
```

작성자 이름이 같으면 커밋 hash로 한 번 더 비교해 출력 순서를 안정적으로 만듭니다.

쉽게 말하면 “누가 만든 커밋인지 이름 기준으로 묶어서 보여줘”라는 명령입니다.

### `SEARCH <keyword>`

커밋 메시지에서 특정 키워드를 검색하는 명령어입니다.

예:

```text
mini-git> SEARCH login
```

이 명령은 모든 커밋 메시지를 매번 처음부터 검사하지 않습니다. `COMMIT`을 만들 때 미리 keyword 인덱스를 만들어두고, 검색할 때 그 인덱스에서 바로 후보 커밋을 가져옵니다.

예를 들어 커밋 메시지가 다음과 같다면:

```text
add login feature
```

내부적으로 아래처럼 저장됩니다.

```text
login -> C000002
feature -> C000002
add -> C000002
```

그래서 `SEARCH login`을 실행하면 `C000002`를 빠르게 찾을 수 있습니다.

### `SEARCH --author=<name>`

작성자 이름으로 커밋을 검색하는 명령어입니다.

예:

```text
mini-git> SEARCH --author=alice
```

이 명령도 역색인을 사용합니다. 커밋을 만들 때 작성자 이름을 기준으로 인덱스를 만들어두기 때문에, 특정 작성자의 커밋을 빠르게 찾을 수 있습니다.

```text
alice -> C000001, C000002
```

쉽게 말하면 “alice가 만든 커밋만 보여줘”라는 명령입니다.

### `ANCESTORS <commit_hash>`

특정 커밋의 모든 조상 커밋을 출력하는 명령어입니다.

예:

```text
mini-git> ANCESTORS C000003
```

커밋 그래프가 아래와 같다고 하면:

```text
C000001
   ↓
C000002
   ↓
C000003
```

`C000003`의 조상은 `C000002`, `C000001`입니다. 부모를 따라 계속 거슬러 올라가면서 도달 가능한 모든 커밋을 찾습니다.

쉽게 말하면 `ANCESTORS`는 “이 커밋이 어떤 커밋들 위에 쌓였는지 보여줘”라는 명령입니다.

### `PATH <commit1> <commit2>`

두 커밋 사이의 최단 경로를 찾는 명령어입니다.

예:

```text
mini-git> PATH C000001 C000003
```

커밋 그래프가 아래와 같다면:

```text
C000001
   ↓
C000002
   ↓
C000003
```

결과는 다음처럼 나옵니다.

```text
C000001->C000002->C000003
```

이 과제에서는 부모-자식 연결을 무방향 간선처럼 보고 최단 경로를 찾습니다. 즉 부모 방향으로도 이동할 수 있고, 자식 방향으로도 이동할 수 있다고 보고 BFS로 가장 짧은 경로를 찾습니다.

쉽게 말하면 `PATH`는 “두 커밋이 그래프에서 어떻게 연결되어 있는지 가장 짧은 길을 보여줘”라는 명령입니다.

### `exit`, `quit`

프로그램을 종료하는 명령어입니다.

```text
mini-git> exit
```

또는:

```text
mini-git> quit
```

이 프로그램은 데이터를 파일에 저장하지 않고 메모리에만 보관합니다. 따라서 프로그램을 종료하면 지금까지 만든 커밋과 브랜치 정보는 사라집니다.

## 프로젝트 구조

```text
Task5/
├── main.py              실행 진입점
├── README.md            사용 방법과 구조 설명
├── 문제.md              정리된 과제 문서
└── mini_git/
    ├── __init__.py      패키지 표시
    ├── cli.py           REPL, 명령어 파싱, 출력
    ├── hashmap.py       직접 구현한 체이닝 해시맵
    ├── models.py        Commit 데이터 모델
    ├── repository.py    커밋 그래프, 브랜치, 검색, 탐색
    └── sorting.py       직접 구현한 merge sort
```

## 모듈별 역할

### `main.py`

프로그램의 시작점입니다. `mini_git.cli.main()`을 호출해 REPL을 시작합니다. 과제의 실행 예시인 `python main.py`를 만족시키는 파일입니다.

### `cli.py`

사용자 입력을 해석합니다. `shlex.split()`을 사용해 `COMMIT "add login feature"`처럼 공백이 포함된 문자열도 하나의 인자로 처리합니다.

`cli.py`는 명령어 이름과 인자 개수만 확인하고, 실제 작업은 `MiniGit` 객체에 맡깁니다.

### `repository.py`

Mini Git의 핵심 로직입니다. 다음 상태를 관리합니다.

- 현재 저장소 초기화 여부
- 현재 사용자 author
- 현재 HEAD 브랜치
- 커밋 hash로 찾는 커밋 저장소
- 브랜치 이름과 브랜치가 가리키는 커밋 hash
- 커밋 생성 순서
- keyword 역색인
- author 역색인

`COMMIT`을 실행하면 현재 HEAD 커밋을 부모로 연결해 새 커밋 노드를 만들고, 현재 브랜치가 새 커밋을 가리키도록 갱신합니다.

### `models.py`

커밋 노드인 `Commit` 클래스를 정의합니다. 각 커밋은 아래 정보를 가집니다.

- `hash`
- `message`
- `author`
- `timestamp`
- `parents`

부모 커밋을 `parents`에 저장하므로 커밋들이 그래프 형태로 연결됩니다.

### `hashmap.py`

커밋 hash, 브랜치, 역색인을 빠르게 찾기 위해 직접 구현한 해시맵입니다. Python의 `dict` 대신 버킷 배열과 `Entry.next` 체이닝으로 충돌을 처리합니다.

### `sorting.py`

Python의 `sorted()`나 `list.sort()`를 쓰지 않기 위해 직접 구현한 merge sort입니다. 날짜 기준, author 기준처럼 비교 함수를 바꿔 정렬할 수 있습니다.

## 구현 포인트

### 커밋 그래프와 DAG

새 커밋은 현재 HEAD를 부모로 갖습니다. 부모는 이미 존재하는 과거 커밋이므로, 새 커밋에서 과거 커밋 방향으로만 연결됩니다. 따라서 순환이 생기지 않는 DAG 구조가 됩니다.

```text
C000001
   ↓
C000002
   ↓
C000003
```

### 브랜치

브랜치는 커밋을 복사하지 않고, 특정 커밋 hash만 가리킵니다.

```text
main    -> C000001
feature -> C000003
```

`SWITCH`는 현재 HEAD 브랜치 이름만 바꿉니다. 이후 `COMMIT`하면 현재 브랜치가 새 커밋을 가리키게 됩니다.

### 역색인

검색을 빠르게 하기 위해 커밋 생성 시 인덱스를 미리 만듭니다.

```text
keyword "login" -> C000002, C000005
author  "alice" -> C000001, C000002
```

`SEARCH login`을 실행하면 모든 커밋을 순회하지 않고 keyword 인덱스에서 후보 hash 목록을 바로 가져옵니다.

### 직접 구현 정렬

`LOG --sort-by=date`, `LOG --sort-by=author`는 직접 구현한 merge sort를 사용합니다. merge sort는 안정 정렬이며 시간복잡도는 평균/최악 모두 `O(N log N)`입니다.

### 최단 경로

`PATH <commit1> <commit2>`는 커밋과 부모 연결을 무방향 간선처럼 보고 BFS로 최단 경로를 찾습니다. 최단 경로가 여러 개라면 `hash1->hash2->...` 문자열 기준으로 사전순이 가장 작은 경로를 출력합니다.

## 제약

- 데이터는 메모리에만 저장됩니다.
- 프로그램을 종료하면 커밋 기록은 사라집니다.
- 실제 Git 저장소를 만들거나 `.git` 폴더를 사용하지 않습니다.
- 정렬에는 `sorted()`와 `list.sort()`를 사용하지 않습니다.

