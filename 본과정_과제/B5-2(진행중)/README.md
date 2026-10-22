# Mini Git

Git의 핵심 구조(커밋 그래프, 브랜치, 검색 인덱스, 정렬)를 Python으로 직접 구현한 **CLI 기반 Mini Git**입니다.
실제 `git` 명령이나 그래프 라이브러리를 쓰지 않고, 모든 알고리즘(위상 정렬, BFS, 역색인, 병합 정렬)을 손으로 만들었습니다.
데이터는 메모리에만 저장되며 프로그램을 끝내면 사라집니다.

## 실행

- Python 3.10 이상 (외부 라이브러리 없음)

```console
python main.py
```

`mini-git>` 프롬프트에 명령을 입력합니다. `exit` 또는 `quit`으로 종료합니다.
테스트는 `python -m unittest -v` 로 실행합니다 (41개).

## 명령어

명령어는 **대소문자를 구분하지 않습니다**(`INIT`, `init` 모두 가능). 공백이 들어간 인자는 **따옴표**로 감쌉니다.

| 명령 | 설명 |
| --- | --- |
| `INIT <user_name>` | 저장소 초기화. `main` 브랜치 생성, HEAD를 `main`으로, 작성자 설정 |
| `BRANCH <branch_name>` | 현재 HEAD가 가리키는 커밋에 새 브랜치 생성 |
| `SWITCH <branch_name>` | HEAD를 해당 브랜치로 이동 |
| `COMMIT <message>` | 현재 브랜치 끝을 부모로 하는 새 커밋 생성 (역색인 갱신) |
| `LOG` | 모든 커밋 출력. **부모가 항상 자식보다 먼저** (위상 정렬) |
| `LOG --sort-by=date` / `--sort-by=author` | 시각순 / 작성자순 정렬 출력 (직접 구현한 병합 정렬) |
| `PATH <commit1> <commit2>` | 두 커밋 사이 최단 경로. 없으면 `No path` |
| `ANCESTORS <commit_hash>` | 해당 커밋의 모든 조상 (가까운 조상부터) |
| `SEARCH <keyword>` | 메시지 키워드 검색 (역색인). `"add login"`처럼 여러 단어면 모두 포함한 커밋 |
| `SEARCH --author=<name>` | 작성자 검색 (역색인) |
| `EXIT`, `QUIT` | 종료 |

**보조 명령 (과제 요구 외, 시연/디버깅용):** `HELP`(도움말), `STATUS`(현재 사용자·브랜치·HEAD), `INDEX`(역색인 내용 보기),
`USER <name>`(저장소를 유지한 채 작성자만 변경 — `INIT`은 저장소를 초기화하기 때문에 여러 작성자의 커밋을 만들려면 필요)

**표준 에러 메시지:** `Invalid args`, `Unknown branch: <name>`, `Unknown commit: <hash>`,
`Branch already exists: <name>`, `Unknown command: <name>`, `Repository not initialized. Run INIT <user_name> first`

## 실행 예시

```text
mini-git> init "Alice"
Initialized repository.
Current branch: main
Current user: Alice
mini-git> commit "Initial commit"
[main c001] Initial commit
mini-git> branch feature
Created branch: feature
mini-git> switch feature
Switched to branch: feature
mini-git> commit "Add login feature"
[feature c002] Add login feature
mini-git> switch main
Switched to branch: main
mini-git> commit "Add payment feature"
[main c003] Add payment feature
mini-git> log
commit c001 (Alice, 2024-01-15 09:00:00)
    parents: -
    Initial commit
commit c002 (Alice, 2024-01-15 09:15:00) [feature]
    parents: c001
    Add login feature
commit c003 (Alice, 2024-01-15 09:30:00) [HEAD -> main]
    parents: c001
    Add payment feature
mini-git> path c002 c003
Path: c002 -> c001 -> c003
mini-git> search "login"
Found 1 commit:
- c002: Add login feature (Alice)
```

(시각은 실행한 시점의 실제 시각으로 찍힙니다.)

커밋 그래프 모양: `c001` 에서 갈라져 `c002`(feature)와 `c003`(main)이 생깁니다.

```text
            c001 Initial commit
            /                \
 c002 Add login feature   c003 Add payment feature
      [feature]                  [HEAD -> main]
```

## 프로젝트 구조

```text
main.py               실행 진입점 (REPL 시작)
mini_git/
  models.py           Commit 데이터, hash 발급기(HashGenerator), 에러(MiniGitError)
  graph.py            CommitGraph: 커밋 저장(해시맵) + 위상 정렬 / 조상 탐색 / 최단 경로
  index.py            InvertedIndex: keyword -> 커밋, author -> 커밋
  sorting.py          merge_sort: 직접 구현한 안정 병합 정렬
  repository.py       Repository: 브랜치/HEAD/커밋 생성, 위 부품을 묶는 지휘자
  cli.py              입력 파싱, 출력 형식, REPL
test_mini_git.py      자동 테스트
```

의존 방향은 한 줄입니다: `cli` → `repository` → (`graph` / `index` / `sorting` / `models`). 알고리즘(탐색·정렬·인덱싱)은 각각 독립된 클래스/함수이며 주요 함수에 docstring이 있습니다.

## 설계와 알고리즘

| 기능 | 알고리즘 | 시간복잡도 (V=커밋 수, E=부모 연결 수) |
| --- | --- | --- |
| `LOG` | 위상 정렬 (Kahn 알고리즘) | O(V + E) |
| `LOG --sort-by=…` | 병합 정렬 (안정) | 평균·최악 모두 O(V log V), 추가 메모리 O(V) |
| `PATH` | 무방향 BFS + 사전순 욕심쟁이 경로 복원 | O(V + E) |
| `ANCESTORS` | 부모 방향 BFS (visited 집합) | O(V + E) |
| `SEARCH` | 역색인 dict 조회 | 평균 O(1) + 결과 개수 (순회 검색은 O(V)) |
| 커밋 조회 | 해시맵(dict) | 평균 O(1) |

- **DAG**: 커밋은 *이미 존재하는* 커밋만 부모로 가질 수 있습니다(`CommitGraph.add`가 검사). 부모는 항상 자식보다 먼저 만들어지므로 순환이 생길 수 없습니다.
- **위상 정렬(LOG)**: "아직 출력되지 않은 부모가 0개"인 커밋부터 꺼내 출력하고, 그 자식들의 대기 부모 수를 1씩 줄입니다. 부모가 둘인 병합 커밋도 두 부모가 모두 나온 뒤에 출력됩니다.
- **최단 경로(PATH)**: 부모-자식 연결을 방향 없는 간선으로 봅니다. 도착점에서 BFS로 모든 커밋의 거리를 구한 뒤, 출발점에서 "거리가 1 작은 이웃 중 hash가 가장 작은 쪽"으로 걸어가면 `h1->h2->…` 문자열이 사전순으로 가장 작은 최단 경로가 됩니다(최단 경로는 모두 같은 개수의 커밋을 지나므로 앞 칸부터 작은 것을 고르면 전체가 최소).
- **역색인**: 커밋할 때 메시지를 `split()` 후 `lower()`한 단어마다 `keyword -> hash 목록`에, 작성자(소문자)는 `author -> hash 목록`에 등록합니다. 검색은 모든 커밋을 훑지 않고 dict에서 후보를 바로 꺼냅니다.
- **정렬**: `sorted()` / `list.sort()`를 쓰지 않고 병합 정렬을 직접 구현했습니다. 합칠 때 키가 같으면 왼쪽을 먼저 꺼내 **안정 정렬**이 되므로, 동률(예: 같은 초에 만든 커밋)은 위상 정렬 순서(부모 먼저)가 유지됩니다.

## 과제 목표 점검

1. **커밋 그래프와 DAG** — 커밋 = 노드, `parents` = 간선. 새 커밋은 기존 커밋만 가리키므로 방향은 있고(자식→부모) 순환은 없습니다.
2. **부모 먼저 출력되는 로그** — 단순 최신순이 아니라 위상 정렬(Kahn)이 필요합니다. 브랜치가 갈라진 그래프에서도 부모→자식 순서가 깨지지 않습니다.
3. **최단 경로 / 조상 탐색** — 둘 다 BFS. PATH는 부모+자식(무방향) 이웃으로, ANCESTORS는 부모 방향으로만 진행하며 visited로 중복을 막습니다.
4. **정렬** — 병합 정렬: 평균/최악 O(n log n), 안정 정렬. `key` 함수만 바꿔 날짜순/작성자순을 모두 처리합니다.
5. **역색인** — "단어 → 커밋 목록"을 미리 만들어 두므로 검색이 평균 O(1)에 후보를 얻습니다. 대신 COMMIT 때 인덱스를 갱신하는 비용을 치릅니다.

## 구현 선택과 한계

- **hash**: 증가 카운터(`c001`, `c002`, …). 카운터는 줄지 않으므로 세션 내 중복이 불가능하고, `INIT`을 다시 해도 발급기는 유지됩니다. (실제 Git은 내용 기반 SHA-1을 씁니다.) 입력할 때 hash의 대소문자는 구분하지 않습니다.
- **키워드 규칙**: 최소 기준 그대로 `split` + `lower`만 적용합니다. 구두점은 떼지 않으므로 메시지 `Fix bug: login`의 키워드는 `bug:`이고 `bug`로는 검색되지 않습니다.
- **작성자 검색**은 대소문자를 구분하지 않습니다 (`--author=alice` 로 `Alice`를 찾음).
- **첫 커밋 전에 만든 브랜치**는 가리키는 커밋이 아직 없고, 거기서 한 첫 커밋은 부모가 없는 뿌리 커밋이 됩니다. 뿌리가 2개면 서로 이어지지 않아 `PATH`가 `No path`를 출력합니다.
- 동률 규칙: `--sort-by` 결과에서 키가 같으면 위상 정렬(LOG) 순서를 유지합니다.
- 파일 내용 추적, 네트워크, 파일 저장(영속성)은 구현하지 않았습니다. 보너스 과제(diff / merge / 정렬 성능 비교)는 포함하지 않았습니다.
